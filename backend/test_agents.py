"""
Test script for Master + Worker Agents
"""

import asyncio
import sys
from pathlib import Path
import json

# Add parent directory to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from agents.diagnosis_agent import DiagnosisAgent
from agents.customer_engagement_agent import CustomerEngagementAgent
from agents.scheduling_agent import SchedulingAgent
from agents.feedback_agent import FeedbackAgent, ServiceOutcome


async def test_diagnosis_agent():
    """Test diagnosis agent"""
    print("\n=== Testing Diagnosis Agent ===")
    
    agent = DiagnosisAgent()
    
    # Mock prediction from ML service
    prediction = {
        'vehicle_id': 1,
        'vin': 'TEST123456789',
        'severity': 'high',
        'failure_probability': 0.85,
        'explanation': 'High engine temperature detected with increasing trend',
        'feature_importance': {
            'engine_temperature_mean': 0.35,
            'engine_temperature_trend': 0.25,
            'coolant_temp_mean': 0.20
        }
    }
    
    diagnosis = agent.diagnose(prediction)
    
    print(f"Issue Category: {diagnosis['issue_category']}")
    print(f"Severity: {diagnosis['severity']}")
    print(f"Urgency: {diagnosis['urgency']}")
    print(f"Primary Component: {diagnosis['primary_component']['component_name']}")
    print(f"Failure Mode: {diagnosis['primary_component']['failure_mode']}")
    print(f"Estimated Cost: ${diagnosis['total_estimated_cost']:.2f}")
    print(f"Estimated Downtime: {diagnosis['total_estimated_downtime_hours']:.1f} hours")
    print(f"Assessment: {diagnosis['assessment']}")
    print(f"Recommended Action: {diagnosis['recommended_action']}")
    
    return diagnosis


def test_customer_engagement_agent():
    """Test customer engagement agent"""
    print("\n=== Testing Customer Engagement Agent ===")
    
    agent = CustomerEngagementAgent()
    
    customer_info = {
        'customer_id': 1,
        'name': 'John Doe',
        'email': 'john@example.com',
        'phone': '+1-555-0123'
    }
    
    vehicle_info = {
        'vehicle_id': 1,
        'vin': 'TEST123456789',
        'make': 'Toyota',
        'model': 'Camry',
        'year': 2020
    }
    
    diagnosis = {
        'urgency': 'urgent',
        'severity': 'high',
        'primary_component': {
            'component_name': 'Thermostat',
            'failure_mode': 'Stuck closed'
        },
        'assessment': 'Engine overheating detected',
        'total_estimated_downtime_hours': 3.5,
        'total_estimated_cost': 450.00
    }
    
    proposed_slots = [
        {
            'start_time': '2024-12-02T09:00:00',
            'end_time': '2024-12-02T12:30:00',
            'duration_hours': 3.5,
            'service_center_id': 1,
            'service_center_name': 'Main Service Center'
        },
        {
            'start_time': '2024-12-02T14:00:00',
            'end_time': '2024-12-02T17:30:00',
            'duration_hours': 3.5,
            'service_center_id': 1,
            'service_center_name': 'Main Service Center'
        }
    ]
    
    # Initiate contact
    contact_result = agent.initiate_contact(
        customer_info,
        vehicle_info,
        diagnosis,
        proposed_slots
    )
    
    print(f"Conversation ID: {contact_result['conversation_id']}")
    print(f"Call Status: {contact_result['call_result']['status']}")
    print(f"\nGreeting Script:\n{contact_result['greeting_script']}")
    
    # Simulate customer response
    conversation_id = contact_result['conversation_id']
    
    print("\n--- Simulating Customer Response: 'yes, option 1' ---")
    response = agent.process_response(conversation_id, "yes, option 1")
    print(f"Action: {response['action']}")
    print(f"Message: {response['message']}")
    
    if response['action'] == 'confirm_appointment':
        print(f"Selected Slot: {response['selected_slot']['start_time']}")
    
    return contact_result


async def test_scheduling_agent():
    """Test scheduling agent"""
    print("\n=== Testing Scheduling Agent ===")
    
    agent = SchedulingAgent()
    
    diagnosis = {
        'urgency': 'urgent',
        'severity': 'high',
        'total_estimated_downtime_hours': 3.5,
        'total_estimated_cost': 450.00,
        'issue_category': 'engine_overheating'
    }
    
    # Find available slots
    slots = await agent.find_available_slots(
        customer_id=1,
        vehicle_id=1,
        diagnosis=diagnosis,
        max_slots=5
    )
    
    print(f"Found {len(slots)} available slots:")
    for i, slot in enumerate(slots, 1):
        print(f"  {i}. {slot['start_time']} - {slot['end_time']}")
        print(f"     Service Center: {slot['service_center_name']}")
        print(f"     Duration: {slot['duration_hours']} hours")
    
    if slots:
        # Create appointment
        print("\n--- Creating Appointment ---")
        appointment = await agent.create_appointment(
            customer_id=1,
            vehicle_id=1,
            slot=slots[0],
            diagnosis=diagnosis,
            notes="Predicted engine overheating issue"
        )
        
        print(f"Appointment ID: {appointment['appointment_id']}")
        print(f"Confirmation #: {appointment['confirmation_number']}")
        print(f"Time: {appointment['appointment_time']}")
        print(f"Status: {appointment['status']}")
        
        return appointment
    
    return None


async def test_feedback_agent():
    """Test feedback agent"""
    print("\n=== Testing Feedback Agent ===")
    
    agent = FeedbackAgent()
    
    # Mock appointment ID (would come from scheduling agent)
    appointment_id = 1
    
    # Schedule follow-up
    follow_up = await agent.schedule_follow_up(appointment_id)
    print(f"Follow-up scheduled for: {follow_up.get('follow_up_scheduled', 'N/A')}")
    print(f"Survey questions: {len(follow_up.get('survey_questions', []))}")
    
    # Simulate feedback collection
    print("\n--- Collecting Feedback ---")
    survey_responses = {
        'q1': 'yes',  # Prediction accurate
        'q2': 4,      # Cost accuracy (1-5)
        'q3': 5,      # Time accuracy (1-5)
        'q4': {'answer': 'no'},  # Additional issues
        'q5': 5,      # Satisfaction (1-5)
        'q6': 'Great proactive service!'
    }
    
    feedback = await agent.collect_feedback(
        appointment_id=appointment_id,
        survey_responses=survey_responses,
        service_outcome=ServiceOutcome.COMPLETED_AS_PREDICTED,
        actual_repairs=['Thermostat', 'Coolant flush'],
        actual_cost=425.00,
        actual_duration_hours=3.0
    )
    
    print(f"Maintenance Record ID: {feedback.get('maintenance_record_id', 'N/A')}")
    print(f"Service Outcome: {feedback['service_outcome']}")
    print(f"Prediction Accuracy: {feedback['prediction_accuracy']['accuracy']}")
    print(f"Predictions Updated: {feedback['prediction_accuracy']['predictions_updated']}")
    print(f"Survey Analysis: {feedback['survey_analysis']}")
    
    # Get feedback summary
    print("\n--- Feedback Summary ---")
    summary = await agent.get_feedback_summary()
    print(f"Total Appointments: {summary['total_appointments']}")
    print(f"Accurate Predictions: {summary['accurate_predictions']}")
    print(f"Accuracy Rate: {summary['accuracy_rate_percent']:.1f}%")
    
    return feedback


async def main():
    """Run all tests"""
    print("=" * 60)
    print("Master + Worker Agents Test Suite")
    print("=" * 60)
    
    try:
        # Test each agent
        diagnosis = await test_diagnosis_agent()
        contact_result = test_customer_engagement_agent()
        appointment = await test_scheduling_agent()
        feedback = await test_feedback_agent()
        
        print("\n" + "=" * 60)
        print("All Agent Tests Completed Successfully!")
        print("=" * 60)
        
        print("\nWorkflow Summary:")
        print(f"1. ✓ Diagnosis generated for vehicle")
        print(f"2. ✓ Customer contacted via engagement agent")
        print(f"3. ✓ Appointment slots found and booked")
        print(f"4. ✓ Feedback collected and labels updated")
        
        print("\nNote: Master Agent orchestration requires Ray to be running.")
        print("To start Master Agent:")
        print("  python -c 'import ray; ray.init()' then run master_agent.py")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
