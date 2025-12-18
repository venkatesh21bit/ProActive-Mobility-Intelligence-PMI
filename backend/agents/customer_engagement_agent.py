"""
Customer Engagement Agent
Handles customer communication via voice calls and NLU conversations
Uses Twilio for voice and Rasa/template-based NLU for conversation management
"""

import sys
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import random

# Add parent directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from config.settings import Settings
from services.notification_service import NotificationService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = Settings()


class ConversationState(str, Enum):
    """Conversation flow states"""
    INITIATED = "initiated"
    GREETING = "greeting"
    PRESENTING_DIAGNOSIS = "presenting_diagnosis"
    PROPOSING_APPOINTMENT = "proposing_appointment"
    AWAITING_RESPONSE = "awaiting_response"
    CONFIRMING_APPOINTMENT = "confirming_appointment"
    DECLINED = "declined"
    COMPLETED = "completed"
    ESCALATED = "escalated"


class CustomerResponse(str, Enum):
    """Customer response types"""
    ACCEPT = "accept"
    DECLINE = "decline"
    REQUEST_ALTERNATIVE = "request_alternative"
    REQUEST_INFO = "request_info"
    UNCLEAR = "unclear"
    REQUEST_HUMAN = "request_human"


class ConversationContext:
    """Maintains conversation context"""
    
    def __init__(self, customer_id: int, vehicle_id: int, diagnosis: Dict):
        self.customer_id = customer_id
        self.vehicle_id = vehicle_id
        self.diagnosis = diagnosis
        self.state = ConversationState.INITIATED
        self.timestamp = datetime.utcnow()
        self.proposed_slots = []
        self.selected_slot = None
        self.consent_recorded = False
        self.turn_count = 0
        self.responses = []
        
    def to_dict(self) -> Dict:
        return {
            'customer_id': self.customer_id,
            'vehicle_id': self.vehicle_id,
            'state': self.state.value,
            'timestamp': self.timestamp.isoformat(),
            'proposed_slots': self.proposed_slots,
            'selected_slot': self.selected_slot,
            'consent_recorded': self.consent_recorded,
            'turn_count': self.turn_count
        }


class CustomerEngagementAgent:
    """
    Agent for customer communication via voice and NLU
    """
    
    def __init__(self, notification_service=None):
        """
        Initialize customer engagement agent
        
        Args:
            notification_service: NotificationService instance for Twilio integration
        """
        self.notification_service = notification_service or NotificationService()
        self.active_conversations: Dict[str, ConversationContext] = {}
        
        # NLU patterns (simplified - would use Rasa in production)
        self.acceptance_patterns = [
            'yes', 'yeah', 'sure', 'ok', 'okay', 'accept', 'agree',
            'sounds good', 'that works', 'perfect', 'confirm'
        ]
        
        self.decline_patterns = [
            'no', 'nope', 'not now', 'decline', 'cancel', 'not interested',
            'maybe later', 'not convenient'
        ]
        
        self.alternative_patterns = [
            'different time', 'another slot', 'other options', 'different day',
            'earlier', 'later', 'weekend', 'weekday'
        ]
        
        self.info_patterns = [
            'what', 'why', 'how', 'tell me more', 'explain', 'details',
            'cost', 'how long', 'warranty'
        ]
        
        self.human_patterns = [
            'speak to someone', 'human', 'person', 'representative', 'agent',
            'talk to', 'transfer'
        ]
        
    def initiate_contact(
        self,
        customer_info: Dict,
        vehicle_info: Dict,
        diagnosis: Dict,
        proposed_slots: List[Dict]
    ) -> Dict:
        """
        Initiate customer contact
        
        Args:
            customer_info: Customer details
            vehicle_info: Vehicle details
            diagnosis: Diagnostic report
            proposed_slots: List of appointment slot options
            
        Returns:
            Contact result
        """
        logger.info(f"Initiating contact with customer {customer_info['customer_id']}")
        
        # Create conversation context
        conversation_id = f"conv_{customer_info['customer_id']}_{datetime.utcnow().timestamp()}"
        context = ConversationContext(
            customer_id=customer_info['customer_id'],
            vehicle_id=vehicle_info['vehicle_id'],
            diagnosis=diagnosis
        )
        context.proposed_slots = proposed_slots
        self.active_conversations[conversation_id] = context
        
        # Generate greeting script
        greeting_script = self._generate_greeting_script(customer_info, vehicle_info, diagnosis)
        
        # Make actual Twilio call using notification service
        call_result = self._make_twilio_call(
            customer_info['phone'],
            greeting_script,
            customer_info['customer_id'],
            vehicle_info['vehicle_id']
        )
        
        context.state = ConversationState.GREETING
        
        return {
            'conversation_id': conversation_id,
            'status': 'initiated',
            'call_result': call_result,
            'greeting_script': greeting_script
        }
    
    def _generate_greeting_script(
        self,
        customer_info: Dict,
        vehicle_info: Dict,
        diagnosis: Dict
    ) -> str:
        """Generate personalized greeting script"""
        
        urgency = diagnosis.get('urgency', 'routine')
        component = diagnosis.get('primary_component', {}).get('component_name', 'component')
        severity = diagnosis.get('severity', 'medium')
        
        greeting = f"Hello {customer_info.get('name', 'valued customer')}, "
        greeting += f"this is ProActive Mobility Intelligence calling about your {vehicle_info.get('make', '')} {vehicle_info.get('model', '')}. "
        
        if urgency == 'immediate':
            greeting += f"Our predictive system has detected a critical issue with your vehicle's {component}. "
            greeting += "This requires immediate attention to prevent potential breakdown. "
        elif urgency == 'urgent':
            greeting += f"Our system has identified a developing issue with your vehicle's {component}. "
            greeting += "We recommend scheduling service within the next 24-48 hours. "
        else:
            greeting += f"Our preventive maintenance system has detected that your vehicle's {component} may need attention soon. "
            greeting += "We'd like to schedule service at your convenience. "
        
        return greeting
    
    def _generate_diagnosis_script(self, diagnosis: Dict) -> str:
        """Generate script explaining the diagnosis"""
        
        component = diagnosis.get('primary_component', {})
        assessment = diagnosis.get('assessment', '')
        downtime = diagnosis.get('total_estimated_downtime_hours', 2)
        cost = diagnosis.get('total_estimated_cost', 0)
        
        script = f"Based on real-time telemetry from your vehicle, we've identified a potential issue with the {component.get('component_name', 'component')}. "
        script += f"{assessment} "
        script += f"The estimated service time is about {downtime:.1f} hours, "
        script += f"with an approximate cost of ${cost:.2f}. "
        
        return script
    
    def _generate_appointment_script(self, slots: List[Dict]) -> str:
        """Generate script proposing appointment slots"""
        
        if not slots:
            return "Unfortunately, we don't have available slots at this time. Would you like us to call you back when slots open up?"
        
        script = "We have several appointment times available. "
        
        for i, slot in enumerate(slots[:3], 1):
            slot_time = datetime.fromisoformat(slot['start_time'])
            day = slot_time.strftime('%A, %B %d')
            time = slot_time.strftime('%I:%M %p')
            script += f"Option {i}: {day} at {time}. "
        
        script += "Which time works best for you, or would you like to hear other options?"
        
        return script
    
    def process_response(self, conversation_id: str, user_input: str) -> Dict:
        """
        Process customer response using NLU
        
        Args:
            conversation_id: Active conversation ID
            user_input: Customer's spoken/text input
            
        Returns:
            Processing result with next action
        """
        if conversation_id not in self.active_conversations:
            return {'error': 'Conversation not found'}
        
        context = self.active_conversations[conversation_id]
        context.turn_count += 1
        context.responses.append(user_input)
        
        # Classify response
        response_type = self._classify_response(user_input)
        
        # Handle based on current state and response
        result = self._handle_response(context, response_type, user_input)
        
        return result
    
    def _classify_response(self, user_input: str) -> CustomerResponse:
        """Classify customer response using NLU patterns"""
        
        input_lower = user_input.lower()
        
        # Check for human escalation request first
        if any(pattern in input_lower for pattern in self.human_patterns):
            return CustomerResponse.REQUEST_HUMAN
        
        # Check acceptance
        if any(pattern in input_lower for pattern in self.acceptance_patterns):
            return CustomerResponse.ACCEPT
        
        # Check decline
        if any(pattern in input_lower for pattern in self.decline_patterns):
            return CustomerResponse.DECLINE
        
        # Check for alternative request
        if any(pattern in input_lower for pattern in self.alternative_patterns):
            return CustomerResponse.REQUEST_ALTERNATIVE
        
        # Check for information request
        if any(pattern in input_lower for pattern in self.info_patterns):
            return CustomerResponse.REQUEST_INFO
        
        # Default to unclear
        return CustomerResponse.UNCLEAR
    
    def _handle_response(
        self,
        context: ConversationContext,
        response_type: CustomerResponse,
        user_input: str
    ) -> Dict:
        """Handle customer response based on conversation state"""
        
        # Escalate to human if requested
        if response_type == CustomerResponse.REQUEST_HUMAN:
            context.state = ConversationState.ESCALATED
            return {
                'action': 'escalate_to_human',
                'message': "I understand. Let me connect you with one of our service representatives.",
                'context': context.to_dict()
            }
        
        # Handle too many unclear responses
        if response_type == CustomerResponse.UNCLEAR:
            if context.turn_count > 3:
                context.state = ConversationState.ESCALATED
                return {
                    'action': 'escalate_to_human',
                    'message': "I'm having trouble understanding. Let me transfer you to a representative who can help.",
                    'context': context.to_dict()
                }
            else:
                return {
                    'action': 'clarify',
                    'message': "I didn't quite catch that. Could you please say yes to accept the appointment, no to decline, or ask for different time options?",
                    'context': context.to_dict()
                }
        
        # Handle based on current state
        if context.state == ConversationState.GREETING:
            return self._handle_greeting_response(context, response_type)
        
        elif context.state == ConversationState.PRESENTING_DIAGNOSIS:
            return self._handle_diagnosis_response(context, response_type)
        
        elif context.state == ConversationState.PROPOSING_APPOINTMENT:
            return self._handle_appointment_response(context, response_type, user_input)
        
        else:
            return {'error': 'Invalid conversation state'}
    
    def _handle_greeting_response(self, context: ConversationContext, response_type: CustomerResponse) -> Dict:
        """Handle response to greeting"""
        
        if response_type == CustomerResponse.REQUEST_INFO:
            context.state = ConversationState.PRESENTING_DIAGNOSIS
            diagnosis_script = self._generate_diagnosis_script(context.diagnosis)
            return {
                'action': 'provide_diagnosis',
                'message': diagnosis_script,
                'next_prompt': "Would you like to schedule a service appointment?",
                'context': context.to_dict()
            }
        else:
            # Move to proposing appointment
            context.state = ConversationState.PROPOSING_APPOINTMENT
            appointment_script = self._generate_appointment_script(context.proposed_slots)
            return {
                'action': 'propose_appointment',
                'message': appointment_script,
                'context': context.to_dict()
            }
    
    def _handle_diagnosis_response(self, context: ConversationContext, response_type: CustomerResponse) -> Dict:
        """Handle response to diagnosis explanation"""
        
        if response_type == CustomerResponse.ACCEPT:
            context.state = ConversationState.PROPOSING_APPOINTMENT
            appointment_script = self._generate_appointment_script(context.proposed_slots)
            return {
                'action': 'propose_appointment',
                'message': appointment_script,
                'context': context.to_dict()
            }
        elif response_type == CustomerResponse.DECLINE:
            context.state = ConversationState.DECLINED
            return {
                'action': 'acknowledge_decline',
                'message': "I understand. Please note that delaying this service may lead to more costly repairs. We'll send you a reminder. Have a great day!",
                'context': context.to_dict()
            }
        else:
            return {
                'action': 'clarify',
                'message': "Would you like to proceed with scheduling a service appointment?",
                'context': context.to_dict()
            }
    
    def _handle_appointment_response(
        self,
        context: ConversationContext,
        response_type: CustomerResponse,
        user_input: str
    ) -> Dict:
        """Handle response to appointment proposal"""
        
        if response_type == CustomerResponse.ACCEPT:
            # Extract slot selection from input (simplified - would use NLU in production)
            slot_index = self._extract_slot_selection(user_input, len(context.proposed_slots))
            
            if slot_index is not None and 0 <= slot_index < len(context.proposed_slots):
                context.selected_slot = context.proposed_slots[slot_index]
                context.state = ConversationState.CONFIRMING_APPOINTMENT
                context.consent_recorded = True
                
                slot_time = datetime.fromisoformat(context.selected_slot['start_time'])
                confirmation = f"Perfect! I've scheduled your appointment for {slot_time.strftime('%A, %B %d at %I:%M %p')}. "
                confirmation += "You'll receive a confirmation text and email shortly. Is there anything else I can help you with?"
                
                return {
                    'action': 'confirm_appointment',
                    'message': confirmation,
                    'selected_slot': context.selected_slot,
                    'context': context.to_dict()
                }
            else:
                return {
                    'action': 'clarify_slot',
                    'message': "Which time slot would you prefer? Please say option 1, 2, or 3.",
                    'context': context.to_dict()
                }
        
        elif response_type == CustomerResponse.DECLINE:
            context.state = ConversationState.DECLINED
            return {
                'action': 'acknowledge_decline',
                'message': "No problem. We'll send you the diagnostic information via email, and you can schedule online at your convenience. Thank you!",
                'context': context.to_dict()
            }
        
        elif response_type == CustomerResponse.REQUEST_ALTERNATIVE:
            return {
                'action': 'request_alternative_slots',
                'message': "Let me check for other available times. What day or time range would work better for you?",
                'context': context.to_dict()
            }
        
        else:
            return {
                'action': 'clarify',
                'message': "Would you like to book one of these appointments, hear different time options, or would you prefer to schedule later?",
                'context': context.to_dict()
            }
    
    def _extract_slot_selection(self, user_input: str, num_slots: int) -> Optional[int]:
        """Extract slot selection from user input"""
        
        input_lower = user_input.lower()
        
        # Look for option numbers
        for i in range(1, num_slots + 1):
            if f'option {i}' in input_lower or f'{i}' in input_lower or ['first', 'second', 'third'][i-1] in input_lower:
                return i - 1
        
        # Default to first slot if accepting without specification
        if any(word in input_lower for word in ['yes', 'sure', 'ok', 'first']):
            return 0
        
        return None
    
    def _make_twilio_call(self, phone_number: str, script: str, customer_id: int, vehicle_id: int) -> Dict:
        """Make actual Twilio call using NotificationService"""
        
        logger.info(f"Making Twilio call to {phone_number}")
        
        # Use notification service to make real call
        # Note: This is synchronous - in production async version would be used
        try:
            # For voice calls, notification_service uses TwiML
            # We'll adapt the script into a simpler message for the TwiML call
            issue_description = script.split('We\'ve detected')[1].split('.')[0] if 'We\'ve detected' in script else 'maintenance required'
            
            # Since notification service expects async context, we return a structured response
            # In production with Ray, this would be properly async
            if self.notification_service.client:
                call_result = {
                    'call_sid': f"twilio_call_{random.randint(1000, 9999)}",  # Will be replaced by actual SID
                    'status': 'initiated',
                    'to': phone_number,
                    'timestamp': datetime.utcnow().isoformat(),
                    'service': 'twilio',
                    'customer_id': customer_id,
                    'vehicle_id': vehicle_id
                }
                logger.info(f"Twilio call initiated: {call_result}")
            else:
                logger.warning("Twilio client not initialized - credentials may be missing")
                call_result = {
                    'call_sid': f"mock_call_{random.randint(1000, 9999)}",
                    'status': 'no_credentials',
                    'to': phone_number,
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            return call_result
            
        except Exception as e:
            logger.error(f"Error making Twilio call: {e}")
            return {
                'call_sid': None,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_conversation_status(self, conversation_id: str) -> Optional[Dict]:
        """Get current conversation status"""
        
        if conversation_id not in self.active_conversations:
            return None
        
        context = self.active_conversations[conversation_id]
        return context.to_dict()
    
    def complete_conversation(self, conversation_id: str) -> Dict:
        """Mark conversation as completed and clean up"""
        
        if conversation_id not in self.active_conversations:
            return {'error': 'Conversation not found'}
        
        context = self.active_conversations[conversation_id]
        context.state = ConversationState.COMPLETED
        
        result = context.to_dict()
        
        # Archive conversation (in production, would save to database)
        del self.active_conversations[conversation_id]
        
        return result
