"""
Feedback Agent
Handles post-service follow-up surveys and updates training labels
Confirms repairs completed and updates maintenance records
"""

import sys
from pathlib import Path
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum

# Add parent directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select, update
from data.database import get_db
from data.models import Appointment, MaintenanceRecord, FailurePrediction, Vehicle

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ServiceOutcome(str, Enum):
    """Service completion outcomes"""
    COMPLETED_AS_PREDICTED = "completed_as_predicted"
    COMPLETED_DIFFERENT_ISSUE = "completed_different_issue"
    NO_ISSUE_FOUND = "no_issue_found"
    PARTIALLY_COMPLETED = "partially_completed"
    CANCELLED = "cancelled"


class FeedbackAgent:
    """
    Agent for post-service feedback collection and model improvement
    """
    
    def __init__(self):
        self.survey_questions = self._initialize_survey_questions()
        
    def _initialize_survey_questions(self) -> List[Dict]:
        """Initialize standard survey questions"""
        return [
            {
                'question_id': 'q1',
                'question': 'Was the predicted issue accurately identified?',
                'type': 'yes_no',
                'required': True
            },
            {
                'question_id': 'q2',
                'question': 'How would you rate the accuracy of the cost estimate?',
                'type': 'scale_1_5',
                'required': True
            },
            {
                'question_id': 'q3',
                'question': 'How would you rate the accuracy of the time estimate?',
                'type': 'scale_1_5',
                'required': True
            },
            {
                'question_id': 'q4',
                'question': 'Were there any additional issues discovered during service?',
                'type': 'yes_no_text',
                'required': False
            },
            {
                'question_id': 'q5',
                'question': 'How satisfied are you with the proactive service notification?',
                'type': 'scale_1_5',
                'required': True
            },
            {
                'question_id': 'q6',
                'question': 'Additional comments or feedback',
                'type': 'text',
                'required': False
            }
        ]
    
    async def schedule_follow_up(self, appointment_id: int) -> Dict:
        """
        Schedule follow-up survey after service completion
        
        Args:
            appointment_id: Completed appointment ID
            
        Returns:
            Follow-up scheduling result
        """
        logger.info(f"Scheduling follow-up for appointment {appointment_id}")
        
        async for db in get_db():
            try:
                # Get appointment details
                stmt = select(Appointment).where(Appointment.appointment_id == appointment_id)
                result = await db.execute(stmt)
                appointment = result.scalar_one_or_none()
                
                if not appointment:
                    return {'error': 'Appointment not found'}
                
                # Schedule follow-up 1-2 days after service
                follow_up_date = datetime.utcnow() + timedelta(days=1)
                
                return {
                    'appointment_id': appointment_id,
                    'customer_id': appointment.customer_id,
                    'vehicle_id': appointment.vehicle_id,
                    'follow_up_scheduled': follow_up_date.isoformat(),
                    'survey_questions': self.survey_questions
                }
                
            except Exception as e:
                logger.error(f"Error scheduling follow-up: {e}")
                raise
    
    async def collect_feedback(
        self,
        appointment_id: int,
        survey_responses: Dict,
        service_outcome: ServiceOutcome,
        actual_repairs: List[str],
        actual_cost: float,
        actual_duration_hours: float
    ) -> Dict:
        """
        Collect and process post-service feedback
        
        Args:
            appointment_id: Appointment ID
            survey_responses: Customer survey responses
            service_outcome: Service outcome classification
            actual_repairs: List of actual repairs performed
            actual_cost: Actual service cost
            actual_duration_hours: Actual service duration
            
        Returns:
            Feedback processing result
        """
        logger.info(f"Collecting feedback for appointment {appointment_id}")
        
        async for db in get_db():
            try:
                # Get appointment and related prediction
                stmt = select(Appointment).where(Appointment.appointment_id == appointment_id)
                result = await db.execute(stmt)
                appointment = result.scalar_one_or_none()
                
                if not appointment:
                    return {'error': 'Appointment not found'}
                
                # Create maintenance record
                maintenance_record = await self._create_maintenance_record(
                    db,
                    appointment,
                    service_outcome,
                    actual_repairs,
                    actual_cost,
                    actual_duration_hours
                )
                
                # Update prediction labels for model improvement
                prediction_accuracy = await self._update_prediction_labels(
                    db,
                    appointment.vehicle_id,
                    appointment.appointment_time,
                    service_outcome,
                    actual_repairs
                )
                
                # Process survey responses
                survey_analysis = self._analyze_survey_responses(survey_responses)
                
                # Update appointment status
                appointment.status = 'completed'
                await db.commit()
                
                logger.info(f"Feedback processed for appointment {appointment_id}")
                
                return {
                    'appointment_id': appointment_id,
                    'maintenance_record_id': maintenance_record.maintenance_record_id,
                    'service_outcome': service_outcome.value,
                    'prediction_accuracy': prediction_accuracy,
                    'survey_analysis': survey_analysis,
                    'model_training_label_updated': True
                }
                
            except Exception as e:
                logger.error(f"Error collecting feedback: {e}")
                await db.rollback()
                raise
    
    async def _create_maintenance_record(
        self,
        db,
        appointment: Appointment,
        service_outcome: ServiceOutcome,
        actual_repairs: List[str],
        actual_cost: float,
        actual_duration_hours: float
    ) -> MaintenanceRecord:
        """Create maintenance record from service completion"""
        
        maintenance_record = MaintenanceRecord(
            vehicle_id=appointment.vehicle_id,
            service_center_id=appointment.service_center_id,
            appointment_id=appointment.appointment_id,
            service_date=datetime.utcnow(),
            service_type=appointment.service_type,
            description=f"Predicted: {appointment.notes}\nActual: {', '.join(actual_repairs)}",
            parts_replaced=', '.join(actual_repairs),
            labor_hours=actual_duration_hours,
            total_cost=actual_cost,
            technician_notes=f"Service outcome: {service_outcome.value}",
            created_at=datetime.utcnow()
        )
        
        db.add(maintenance_record)
        await db.flush()
        
        return maintenance_record
    
    async def _update_prediction_labels(
        self,
        db,
        vehicle_id: int,
        appointment_time: datetime,
        service_outcome: ServiceOutcome,
        actual_repairs: List[str]
    ) -> Dict:
        """Update prediction labels based on actual service outcome"""
        
        # Find predictions made before the appointment
        prediction_window_start = appointment_time - timedelta(days=7)
        
        stmt = select(FailurePrediction).where(
            FailurePrediction.vehicle_id == vehicle_id,
            FailurePrediction.prediction_timestamp >= prediction_window_start,
            FailurePrediction.prediction_timestamp <= appointment_time
        ).order_by(FailurePrediction.prediction_timestamp.desc())
        
        result = await db.execute(stmt)
        predictions = result.scalars().all()
        
        if not predictions:
            logger.warning(f"No predictions found for vehicle {vehicle_id}")
            return {'accuracy': 'unknown', 'predictions_updated': 0}
        
        # Determine if prediction was accurate
        prediction_accurate = service_outcome == ServiceOutcome.COMPLETED_AS_PREDICTED
        
        # Update predictions with actual outcome
        predictions_updated = 0
        for prediction in predictions:
            # Update metadata with actual outcome
            if prediction.meta_data is None:
                prediction.meta_data = {}
            
            prediction.meta_data['actual_outcome'] = {
                'service_outcome': service_outcome.value,
                'actual_repairs': actual_repairs,
                'prediction_accurate': prediction_accurate,
                'feedback_timestamp': datetime.utcnow().isoformat()
            }
            
            predictions_updated += 1
        
        await db.flush()
        
        # Calculate accuracy metrics
        accuracy = 'accurate' if prediction_accurate else 'inaccurate'
        
        return {
            'accuracy': accuracy,
            'predictions_updated': predictions_updated,
            'most_recent_prediction_id': predictions[0].prediction_id if predictions else None
        }
    
    def _analyze_survey_responses(self, survey_responses: Dict) -> Dict:
        """Analyze survey responses and extract insights"""
        
        analysis = {
            'prediction_accuracy_rating': None,
            'cost_accuracy_rating': None,
            'time_accuracy_rating': None,
            'customer_satisfaction': None,
            'additional_issues_found': False,
            'comments': None
        }
        
        # Process responses based on question IDs
        if 'q1' in survey_responses:
            analysis['prediction_accuracy_rating'] = 5 if survey_responses['q1'] == 'yes' else 1
        
        if 'q2' in survey_responses:
            analysis['cost_accuracy_rating'] = survey_responses['q2']
        
        if 'q3' in survey_responses:
            analysis['time_accuracy_rating'] = survey_responses['q3']
        
        if 'q4' in survey_responses:
            if isinstance(survey_responses['q4'], dict):
                analysis['additional_issues_found'] = survey_responses['q4'].get('answer') == 'yes'
            else:
                analysis['additional_issues_found'] = survey_responses['q4'] == 'yes'
        
        if 'q5' in survey_responses:
            analysis['customer_satisfaction'] = survey_responses['q5']
        
        if 'q6' in survey_responses:
            analysis['comments'] = survey_responses['q6']
        
        # Calculate overall score
        ratings = [
            analysis.get('prediction_accuracy_rating'),
            analysis.get('cost_accuracy_rating'),
            analysis.get('time_accuracy_rating'),
            analysis.get('customer_satisfaction')
        ]
        
        valid_ratings = [r for r in ratings if r is not None]
        analysis['overall_score'] = sum(valid_ratings) / len(valid_ratings) if valid_ratings else None
        
        return analysis
    
    async def get_feedback_summary(
        self,
        vehicle_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Get feedback summary for analysis
        
        Args:
            vehicle_id: Filter by vehicle (optional)
            start_date: Start date for summary (optional)
            end_date: End date for summary (optional)
            
        Returns:
            Feedback summary statistics
        """
        async for db in get_db():
            try:
                # Build query for completed appointments
                stmt = select(Appointment).where(Appointment.status == 'completed')
                
                if vehicle_id:
                    stmt = stmt.where(Appointment.vehicle_id == vehicle_id)
                
                if start_date:
                    stmt = stmt.where(Appointment.appointment_time >= start_date)
                
                if end_date:
                    stmt = stmt.where(Appointment.appointment_time <= end_date)
                
                result = await db.execute(stmt)
                appointments = result.scalars().all()
                
                # Get corresponding predictions
                total_appointments = len(appointments)
                accurate_predictions = 0
                
                for appointment in appointments:
                    stmt = select(FailurePrediction).where(
                        FailurePrediction.vehicle_id == appointment.vehicle_id,
                        FailurePrediction.prediction_timestamp <= appointment.appointment_time
                    ).order_by(FailurePrediction.prediction_timestamp.desc()).limit(1)
                    
                    result = await db.execute(stmt)
                    prediction = result.scalar_one_or_none()
                    
                    if prediction and prediction.meta_data:
                        actual_outcome = prediction.meta_data.get('actual_outcome', {})
                        if actual_outcome.get('prediction_accurate'):
                            accurate_predictions += 1
                
                accuracy_rate = (accurate_predictions / total_appointments * 100) if total_appointments > 0 else 0
                
                return {
                    'total_appointments': total_appointments,
                    'accurate_predictions': accurate_predictions,
                    'accuracy_rate_percent': accuracy_rate,
                    'period': {
                        'start': start_date.isoformat() if start_date else None,
                        'end': end_date.isoformat() if end_date else None
                    }
                }
                
            except Exception as e:
                logger.error(f"Error generating feedback summary: {e}")
                raise
    
    async def export_training_data(self, output_path: Optional[Path] = None) -> Dict:
        """
        Export labeled data for model retraining
        
        Args:
            output_path: Path to save training data
            
        Returns:
            Export summary
        """
        logger.info("Exporting training data with actual outcomes")
        
        async for db in get_db():
            try:
                # Get predictions with actual outcomes
                stmt = select(FailurePrediction).where(
                    FailurePrediction.meta_data.isnot(None)
                )
                
                result = await db.execute(stmt)
                predictions = result.scalars().all()
                
                training_samples = []
                
                for prediction in predictions:
                    if prediction.meta_data and 'actual_outcome' in prediction.meta_data:
                        training_samples.append({
                            'prediction_id': prediction.prediction_id,
                            'vehicle_id': prediction.vehicle_id,
                            'prediction_timestamp': prediction.prediction_timestamp.isoformat(),
                            'predicted_failure_type': prediction.predicted_failure_type,
                            'failure_probability': prediction.failure_probability,
                            'actual_outcome': prediction.meta_data['actual_outcome'],
                            'label': 1 if prediction.meta_data['actual_outcome']['prediction_accurate'] else 0
                        })
                
                if output_path:
                    import json
                    with open(output_path, 'w') as f:
                        json.dump(training_samples, f, indent=2)
                
                return {
                    'total_samples': len(training_samples),
                    'positive_samples': sum(1 for s in training_samples if s['label'] == 1),
                    'negative_samples': sum(1 for s in training_samples if s['label'] == 0),
                    'export_path': str(output_path) if output_path else None
                }
                
            except Exception as e:
                logger.error(f"Error exporting training data: {e}")
                raise
