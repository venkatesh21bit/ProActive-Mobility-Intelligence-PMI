"""
Fix for vehicle health score, SMS notifications, and appointment status
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from data.database import get_db_session
from data.models import Vehicle, FailurePrediction, Appointment, Customer
from services.notification_service import NotificationService
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/fixes", tags=["fixes"])


@router.get("/vehicles-with-health/{customer_id}")
async def get_vehicles_with_health(customer_id: int, db: AsyncSession = Depends(get_db_session)):
    """Get customer vehicles with accurate health scores"""
    try:
        # Get all vehicles for customer
        vehicles_query = select(Vehicle).where(Vehicle.customer_id == customer_id)
        vehicles_result = await db.execute(vehicles_query)
        vehicles = vehicles_result.scalars().all()
        
        result = []
        for vehicle in vehicles:
            # Get recent predictions for this vehicle
            predictions_query = select(FailurePrediction).where(
                FailurePrediction.vehicle_id == vehicle.vehicle_id
            ).order_by(FailurePrediction.prediction_time.desc()).limit(10)
            
            predictions_result = await db.execute(predictions_query)
            predictions = predictions_result.scalars().all()
            
            # Calculate health score (0-10 scale)
            if predictions:
                # Average failure probability from predictions
                avg_failure_prob = sum(p.failure_probability for p in predictions) / len(predictions)
                health_score = round((1 - avg_failure_prob) * 10, 1)
                
                # Determine status
                if avg_failure_prob >= 0.7:
                    health_status = "critical"
                elif avg_failure_prob >= 0.4:
                    health_status = "warning"
                else:
                    health_status = "good"
            else:
                health_score = 9.5  # Default excellent health
                health_status = "excellent"
            
            # Get latest appointment
            latest_apt_query = select(Appointment).where(
                Appointment.vehicle_id == vehicle.vehicle_id
            ).order_by(Appointment.scheduled_time.desc()).limit(1)
            
            latest_apt_result = await db.execute(latest_apt_query)
            latest_appointment = latest_apt_result.scalar_one_or_none()
            
            result.append({
                "vehicle_id": vehicle.vehicle_id,
                "vin": vehicle.vin,
                "make": vehicle.make,
                "model": vehicle.model,
                "year": vehicle.year,
                "mileage": vehicle.mileage,
                "health_score": health_score,
                "health_status": health_status,
                "health_score_display": f"{health_score}/10",
                "latest_appointment": {
                    "appointment_id": latest_appointment.appointment_id,
                    "scheduled_time": latest_appointment.scheduled_time.isoformat(),
                    "status": latest_appointment.status,
                    "type": latest_appointment.appointment_type
                } if latest_appointment else None
            })
        
        return {
            "customer_id": customer_id,
            "total_vehicles": len(result),
            "vehicles": result
        }
        
    except Exception as e:
        logger.error(f"Error getting vehicles with health: {e}")
        return {"error": str(e)}


@router.post("/send-appointment-sms/{appointment_id}")
async def send_appointment_sms(appointment_id: int, db: AsyncSession = Depends(get_db_session)):
    """Send SMS confirmation for an appointment"""
    try:
        # Get appointment details
        apt_query = select(Appointment).where(Appointment.appointment_id == appointment_id)
        apt_result = await db.execute(apt_query)
        appointment = apt_result.scalar_one_or_none()
        
        if not appointment:
            return {"status": "error", "message": "Appointment not found"}
        
        # Get customer
        customer_query = select(Customer).where(Customer.customer_id == appointment.customer_id)
        customer_result = await db.execute(customer_query)
        customer = customer_result.scalar_one_or_none()
        
        if not customer or not customer.phone:
            return {"status": "error", "message": "Customer phone not found"}
        
        # Get vehicle
        vehicle_query = select(Vehicle).where(Vehicle.vehicle_id == appointment.vehicle_id)
        vehicle_result = await db.execute(vehicle_query)
        vehicle = vehicle_result.scalar_one_or_none()
        
        # Send SMS
        notification_service = NotificationService()
        if notification_service.client:
            sms_message = (
                f"✅ Appointment {appointment.status.upper()}!\\n"
                f"Type: {appointment.appointment_type.replace('_', ' ').title()}\\n"
                f"Date: {appointment.scheduled_time.strftime('%b %d, %Y at %I:%M %p')}\\n"
                f"Vehicle: {vehicle.make} {vehicle.model}\\n"
                f"Duration: ~{appointment.estimated_duration_minutes} min\\n\\n"
                f"Hero MotoCorp Service"
            )
            
            # Use notification service SMS method
            try:
                sms_result = notification_service.client.messages.create(
                    body=sms_message,
                    from_=notification_service.phone_number,
                    to=customer.phone
                )
                
                return {
                    "status": "success",
                    "message": "SMS sent successfully",
                    "sms_sid": sms_result.sid,
                    "to": customer.phone
                }
            except Exception as sms_error:
                logger.error(f"Twilio SMS error: {sms_error}")
                return {
                    "status": "error",
                    "message": f"Failed to send SMS: {str(sms_error)}"
                }
        else:
            return {
                "status": "error",
                "message": "Twilio not configured"
            }
        
    except Exception as e:
        logger.error(f"Error sending appointment SMS: {e}")
        return {"status": "error", "message": str(e)}


@router.get("/appointment-status-info")
async def get_appointment_status_info():
    """Get information about different appointment statuses"""
    return {
        "statuses": {
            "scheduled": {
                "label": "Scheduled",
                "description": "Appointment has been booked and is waiting for the scheduled date/time",
                "color": "blue",
                "icon": "🕐",
                "next_step": "Wait for appointment date or reschedule if needed"
            },
            "confirmed": {
                "label": "Confirmed",
                "description": "Service center has confirmed the appointment and reserved the slot",
                "color": "green",
                "icon": "✅",
                "next_step": "Arrive at service center on scheduled time"
            },
            "in_progress": {
                "label": "In Progress",
                "description": "Vehicle is currently being serviced",
                "color": "orange",
                "icon": "🔧",
                "next_step": "Service ongoing, you'll be notified when complete"
            },
            "completed": {
                "label": "Completed",
                "description": "Service has been completed successfully",
                "color": "green",
                "icon": "✅",
                "next_step": "Pick up your vehicle and provide feedback"
            },
            "cancelled": {
                "label": "Cancelled",
                "description": "Appointment was cancelled",
                "color": "red",
                "icon": "❌",
                "next_step": "Book a new appointment if needed"
            }
        },
        "explanation": {
            "scheduled_vs_confirmed": (
                "SCHEDULED: When you first book - appointment is in the system\\n"
                "CONFIRMED: Service center reviews and confirms they can accommodate - slot is reserved\\n\\n"
                "Think of it like a restaurant reservation:\\n"
                "- Scheduled = You called and requested a table\\n"
                "- Confirmed = Restaurant called back and confirmed your table is ready"
            )
        }
    }
