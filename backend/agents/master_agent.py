"""
Master Agent
Ray-based orchestrator that coordinates all worker agents
Listens to prediction alerts and manages the complete service flow
"""

import sys
from pathlib import Path
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json

# Add parent directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import ray
from ray import serve

from data.redis_client import RedisClient
from agents.diagnosis_agent import DiagnosisAgent
from agents.customer_engagement_agent import CustomerEngagementAgent
from agents.scheduling_agent import SchedulingAgent
from agents.feedback_agent import FeedbackAgent
from sqlalchemy import select
from data.database import get_db
from data.models import Customer, Vehicle, AgentAuditLog

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WorkflowState(str, Enum):
    """Service workflow states"""
    INITIATED = "initiated"
    DIAGNOSED = "diagnosed"
    CONTACTING_CUSTOMER = "contacting_customer"
    SCHEDULING = "scheduling"
    SCHEDULED = "scheduled"
    CUSTOMER_DECLINED = "customer_declined"
    AWAITING_SERVICE = "awaiting_service"
    SERVICE_COMPLETED = "service_completed"
    FEEDBACK_COLLECTED = "feedback_collected"
    ESCALATED = "escalated"
    FAILED = "failed"


class WorkflowContext:
    """Maintains state for a complete service workflow"""
    
    def __init__(self, alert: Dict):
        self.workflow_id = f"wf_{alert['vehicle_id']}_{datetime.utcnow().timestamp()}"
        self.alert = alert
        self.state = WorkflowState.INITIATED
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Workflow data
        self.customer_info = None
        self.vehicle_info = None
        self.diagnosis = None
        self.conversation_id = None
        self.proposed_slots = []
        self.appointment_id = None
        self.feedback = None
        
        # SLA tracking
        self.sla_deadline = None
        self.sla_met = None
        
        # Error handling
        self.errors = []
        self.retry_count = 0
        
    def to_dict(self) -> Dict:
        return {
            'workflow_id': self.workflow_id,
            'state': self.state.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'vehicle_id': self.alert['vehicle_id'],
            'diagnosis_summary': self.diagnosis.get('issue_category') if self.diagnosis else None,
            'appointment_id': self.appointment_id,
            'sla_deadline': self.sla_deadline.isoformat() if self.sla_deadline else None,
            'sla_met': self.sla_met,
            'retry_count': self.retry_count
        }


@ray.remote
class MasterAgent:
    """
    Master orchestrator agent using Ray
    Coordinates all worker agents and maintains workflow state
    """
    
    def __init__(self):
        self.redis_client = None
        self.diagnosis_agent = DiagnosisAgent()
        self.customer_agent = CustomerEngagementAgent()
        self.scheduling_agent = SchedulingAgent()
        self.feedback_agent = FeedbackAgent()
        
        self.active_workflows: Dict[str, WorkflowContext] = {}
        
        # SLA constraints (in hours)
        self.sla_constraints = {
            'immediate': 2,   # 2 hours
            'urgent': 24,     # 24 hours
            'soon': 72,       # 3 days
            'routine': 168    # 1 week
        }
        
        logger.info("Master Agent initialized")
    
    async def initialize(self):
        """Initialize Redis connection"""
        self.redis_client = RedisClient()
        await self.redis_client.connect()
        logger.info("Master Agent Redis connection established")
    
    async def start_listening(self):
        """Start listening to alerts.predicted stream"""
        logger.info("Master Agent starting to listen for alerts...")
        
        if not self.redis_client:
            await self.initialize()
        
        consumer_group = "master_agent_group"
        consumer_name = "master_agent_1"
        stream_name = "alerts:predicted"
        
        # Create consumer group if it doesn't exist
        try:
            await self.redis_client.create_consumer_group(stream_name, consumer_group)
        except Exception as e:
            logger.info(f"Consumer group might already exist: {e}")
        
        # Listen for alerts
        while True:
            try:
                messages = await self.redis_client.read_stream(
                    stream_name,
                    consumer_group,
                    consumer_name,
                    count=10,
                    block=5000
                )
                
                for message in messages:
                    alert_data = message['data']
                    message_id = message['id']
                    
                    # Process alert
                    await self.process_alert(alert_data)
                    
                    # Acknowledge message
                    await self.redis_client.acknowledge_message(
                        stream_name,
                        consumer_group,
                        message_id
                    )
                
            except Exception as e:
                logger.error(f"Error in master agent loop: {e}")
                await asyncio.sleep(5)
    
    async def process_alert(self, alert: Dict):
        """
        Process incoming alert and orchestrate workflow
        
        Args:
            alert: Alert data from prediction service
        """
        vehicle_id = alert.get('vehicle_id')
        severity = alert.get('severity')
        
        logger.info(f"Processing alert for vehicle {vehicle_id}, severity: {severity}")
        
        # Create workflow context
        context = WorkflowContext(alert)
        self.active_workflows[context.workflow_id] = context
        
        try:
            # Set SLA deadline based on urgency
            urgency = alert.get('urgency', 'routine')
            context.sla_deadline = datetime.utcnow() + timedelta(
                hours=self.sla_constraints.get(urgency, 168)
            )
            
            # Execute workflow steps
            await self._execute_workflow(context)
            
        except Exception as e:
            logger.error(f"Error processing alert: {e}")
            context.state = WorkflowState.FAILED
            context.errors.append(str(e))
            await self._log_audit(context, 'workflow_failed', {'error': str(e)})
    
    async def _execute_workflow(self, context: WorkflowContext):
        """Execute complete service workflow"""
        
        # Step 1: Get customer and vehicle info
        customer_info, vehicle_info = await self._get_customer_vehicle_info(context)
        if not customer_info or not vehicle_info:
            raise Exception("Failed to retrieve customer/vehicle information")
        
        context.customer_info = customer_info
        context.vehicle_info = vehicle_info
        
        # Step 2: Generate diagnosis
        diagnosis = await self._generate_diagnosis(context)
        context.diagnosis = diagnosis
        context.state = WorkflowState.DIAGNOSED
        await self._log_audit(context, 'diagnosis_completed', diagnosis)
        
        # Step 3: Find available appointment slots
        available_slots = await self._find_appointment_slots(context)
        context.proposed_slots = available_slots
        
        # Step 4: Contact customer
        contact_result = await self._contact_customer(context)
        context.conversation_id = contact_result.get('conversation_id')
        context.state = WorkflowState.CONTACTING_CUSTOMER
        await self._log_audit(context, 'customer_contacted', contact_result)
        
        # Note: Further steps (scheduling, feedback) would be triggered by
        # customer responses or service completion events
        logger.info(f"Workflow {context.workflow_id} awaiting customer response")
    
    async def _get_customer_vehicle_info(self, context: WorkflowContext) -> tuple:
        """Retrieve customer and vehicle information"""
        
        vehicle_id = context.alert['vehicle_id']
        
        async for db in get_db():
            try:
                # Get vehicle info
                vehicle_stmt = select(Vehicle).where(Vehicle.vehicle_id == vehicle_id)
                vehicle_result = await db.execute(vehicle_stmt)
                vehicle = vehicle_result.scalar_one_or_none()
                
                if not vehicle:
                    return None, None
                
                # Get customer info
                customer_stmt = select(Customer).where(Customer.customer_id == vehicle.customer_id)
                customer_result = await db.execute(customer_stmt)
                customer = customer_result.scalar_one_or_none()
                
                if not customer:
                    return None, None
                
                customer_info = {
                    'customer_id': customer.customer_id,
                    'name': customer.name,
                    'email': customer.email,
                    'phone': customer.phone
                }
                
                vehicle_info = {
                    'vehicle_id': vehicle.vehicle_id,
                    'vin': vehicle.vin,
                    'make': vehicle.make,
                    'model': vehicle.model,
                    'year': vehicle.year
                }
                
                return customer_info, vehicle_info
                
            except Exception as e:
                logger.error(f"Error retrieving customer/vehicle info: {e}")
                return None, None
    
    async def _generate_diagnosis(self, context: WorkflowContext) -> Dict:
        """Generate diagnosis using diagnosis agent"""
        
        prediction = context.alert
        diagnosis = self.diagnosis_agent.diagnose(prediction)
        
        return diagnosis
    
    async def _find_appointment_slots(self, context: WorkflowContext) -> List[Dict]:
        """Find available appointment slots using scheduling agent"""
        
        slots = await self.scheduling_agent.find_available_slots(
            customer_id=context.customer_info['customer_id'],
            vehicle_id=context.vehicle_info['vehicle_id'],
            diagnosis=context.diagnosis,
            max_slots=5
        )
        
        return slots
    
    async def _contact_customer(self, context: WorkflowContext) -> Dict:
        """Contact customer using customer engagement agent"""
        
        contact_result = self.customer_agent.initiate_contact(
            customer_info=context.customer_info,
            vehicle_info=context.vehicle_info,
            diagnosis=context.diagnosis,
            proposed_slots=context.proposed_slots
        )
        
        return contact_result
    
    async def handle_customer_response(
        self,
        workflow_id: str,
        response: Dict
    ) -> Dict:
        """
        Handle customer response to appointment proposal
        
        Args:
            workflow_id: Active workflow ID
            response: Customer response data
            
        Returns:
            Handling result
        """
        if workflow_id not in self.active_workflows:
            return {'error': 'Workflow not found'}
        
        context = self.active_workflows[workflow_id]
        
        # Process response through customer agent
        result = self.customer_agent.process_response(
            context.conversation_id,
            response.get('user_input', '')
        )
        
        # Handle different actions
        action = result.get('action')
        
        if action == 'confirm_appointment':
            # Create appointment
            appointment = await self.scheduling_agent.create_appointment(
                customer_id=context.customer_info['customer_id'],
                vehicle_id=context.vehicle_info['vehicle_id'],
                slot=result['selected_slot'],
                diagnosis=context.diagnosis
            )
            
            context.appointment_id = appointment['appointment_id']
            context.state = WorkflowState.SCHEDULED
            
            # Check SLA
            context.sla_met = datetime.utcnow() <= context.sla_deadline
            
            await self._log_audit(context, 'appointment_scheduled', appointment)
            
            return {
                'status': 'scheduled',
                'appointment': appointment,
                'sla_met': context.sla_met
            }
        
        elif action == 'acknowledge_decline':
            context.state = WorkflowState.CUSTOMER_DECLINED
            await self._log_audit(context, 'customer_declined', result)
            
            return {
                'status': 'declined',
                'message': result.get('message')
            }
        
        elif action == 'escalate_to_human':
            context.state = WorkflowState.ESCALATED
            await self._log_audit(context, 'escalated_to_human', result)
            
            return {
                'status': 'escalated',
                'message': result.get('message')
            }
        
        else:
            return result
    
    async def handle_service_completion(
        self,
        workflow_id: str,
        completion_data: Dict
    ) -> Dict:
        """
        Handle service completion and trigger feedback collection
        
        Args:
            workflow_id: Workflow ID
            completion_data: Service completion details
            
        Returns:
            Handling result
        """
        if workflow_id not in self.active_workflows:
            return {'error': 'Workflow not found'}
        
        context = self.active_workflows[workflow_id]
        context.state = WorkflowState.SERVICE_COMPLETED
        
        # Schedule follow-up
        follow_up = await self.feedback_agent.schedule_follow_up(context.appointment_id)
        
        await self._log_audit(context, 'service_completed', completion_data)
        
        return {
            'status': 'completed',
            'follow_up_scheduled': follow_up
        }
    
    async def handle_feedback_submission(
        self,
        workflow_id: str,
        feedback_data: Dict
    ) -> Dict:
        """
        Handle feedback submission and update training labels
        
        Args:
            workflow_id: Workflow ID
            feedback_data: Customer feedback
            
        Returns:
            Handling result
        """
        if workflow_id not in self.active_workflows:
            return {'error': 'Workflow not found'}
        
        context = self.active_workflows[workflow_id]
        
        # Collect feedback
        from agents.feedback_agent import ServiceOutcome
        
        feedback_result = await self.feedback_agent.collect_feedback(
            appointment_id=context.appointment_id,
            survey_responses=feedback_data.get('survey_responses', {}),
            service_outcome=ServiceOutcome(feedback_data.get('service_outcome', 'completed_as_predicted')),
            actual_repairs=feedback_data.get('actual_repairs', []),
            actual_cost=feedback_data.get('actual_cost', 0),
            actual_duration_hours=feedback_data.get('actual_duration_hours', 0)
        )
        
        context.feedback = feedback_result
        context.state = WorkflowState.FEEDBACK_COLLECTED
        
        await self._log_audit(context, 'feedback_collected', feedback_result)
        
        # Workflow complete - archive
        del self.active_workflows[workflow_id]
        
        return {
            'status': 'complete',
            'feedback_result': feedback_result
        }
    
    async def _log_audit(self, context: WorkflowContext, event_type: str, event_data: Dict):
        """Log workflow event to audit trail"""
        
        async for db in get_db():
            try:
                audit_log = AgentAuditLog(
                    agent_name='master_agent',
                    action=event_type,
                    vehicle_id=context.vehicle_info['vehicle_id'] if context.vehicle_info else None,
                    customer_id=context.customer_info['customer_id'] if context.customer_info else None,
                    meta_data={
                        'workflow_id': context.workflow_id,
                        'state': context.state.value,
                        'event_data': event_data
                    },
                    timestamp=datetime.utcnow()
                )
                
                db.add(audit_log)
                await db.commit()
                
            except Exception as e:
                logger.error(f"Error logging audit: {e}")
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict]:
        """Get status of active workflow"""
        
        if workflow_id not in self.active_workflows:
            return None
        
        return self.active_workflows[workflow_id].to_dict()
    
    def get_active_workflows(self) -> List[Dict]:
        """Get all active workflows"""
        
        return [ctx.to_dict() for ctx in self.active_workflows.values()]


# Deployment entry point for Ray Serve
@serve.deployment
class MasterAgentService:
    """Ray Serve deployment wrapper for Master Agent"""
    
    def __init__(self):
        self.master_agent = None
    
    async def __aenter__(self):
        # Initialize Ray actor
        self.master_agent = MasterAgent.remote()
        await self.master_agent.initialize.remote()
        
        # Start listening in background
        asyncio.create_task(self.master_agent.start_listening.remote())
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def __call__(self, request):
        """Handle HTTP requests for workflow management"""
        pass
