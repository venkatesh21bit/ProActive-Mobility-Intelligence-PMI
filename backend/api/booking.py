"""
Booking API for customer appointment scheduling
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import logging

from data.database import get_db_session
from data.models import Appointment, Vehicle, Customer, ServiceCenter
from services.notification_service import NotificationService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/bookings", tags=["Bookings"])


class BookingRequest(BaseModel):
    customer_id: int
    vehicle_id: int
    service_type: str
    scheduled_date: str  # e.g., "Tomorrow" or "12/18/2025"
    scheduled_time: str  # e.g., "9:00 AM"
    notes: Optional[str] = None


class BookingResponse(BaseModel):
    appointment_id: int
    customer_name: str
    vehicle_info: str
    service_type: str
    scheduled_time: datetime
    service_center: str
    status: str
    confirmation_message: str


@router.post("/create", response_model=BookingResponse)
async def create_booking(request: BookingRequest, db: AsyncSession = Depends(get_db_session)):
    """
    Create a new service appointment
    """
    try:
        # Verify customer exists
        customer_query = select(Customer).where(Customer.customer_id == request.customer_id)
        customer_result = await db.execute(customer_query)
        customer = customer_result.scalar_one_or_none()
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        # Verify vehicle exists and belongs to customer
        vehicle_query = select(Vehicle).where(
            Vehicle.vehicle_id == request.vehicle_id,
            Vehicle.customer_id == request.customer_id
        )
        vehicle_result = await db.execute(vehicle_query)
        vehicle = vehicle_result.scalar_one_or_none()
        
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found or doesn't belong to customer"
            )
        
        # Get default service center (or create one if none exists)
        center_query = select(ServiceCenter).limit(1)
        center_result = await db.execute(center_query)
        service_center = center_result.scalar_one_or_none()
        
        if not service_center:
            # Create a default service center
            service_center = ServiceCenter(
                name="Hero MotoCorp Service Center",
                address="123 Main Road, Downtown",
                city="Mumbai",
                state="Maharashtra",
                zip_code="400001",
                phone="+91-22-12345678",
                email="service@heromotocorp.com",
                capacity=20,
                latitude=19.0760,
                longitude=72.8777
            )
            db.add(service_center)
            await db.flush()
        
        # Parse date and time
        scheduled_datetime = parse_appointment_datetime(
            request.scheduled_date, 
            request.scheduled_time
        )
        
        # Map service type to appointment type
        appointment_type_map = {
            "General Service": "general_service",
            "Oil Change": "oil_change",
            "Brake Service": "brake_service",
            "Full Inspection": "inspection",
            "Repair Work": "repair"
        }
        
        appointment_type = appointment_type_map.get(request.service_type, "general_service")
        
        # Estimate duration based on service type
        duration_map = {
            "oil_change": 30,
            "brake_service": 60,
            "inspection": 45,
            "general_service": 90,
            "repair": 120
        }
        estimated_duration = duration_map.get(appointment_type, 60)
        
        # Create appointment
        appointment = Appointment(
            vehicle_id=request.vehicle_id,
            customer_id=request.customer_id,
            center_id=service_center.center_id,
            scheduled_time=scheduled_datetime,
            appointment_type=appointment_type,
            status='scheduled',
            predicted_issue=request.notes or f"{request.service_type} scheduled",
            estimated_duration_minutes=estimated_duration,
            customer_consent=True,
            consent_timestamp=datetime.now()
        )
        
        db.add(appointment)
        await db.commit()
        await db.refresh(appointment)
        
        # Send SMS confirmation
        print(f"🔔 Starting SMS notification for appointment {appointment.appointment_id}")
        logger.info(f"🔔 Starting SMS notification for appointment {appointment.appointment_id}")
        try:
            notification_service = NotificationService()
            print(f"📱 NotificationService initialized - Client exists: {notification_service.client is not None}")
            print(f"📱 Customer phone: {customer.phone}")
            logger.info(f"📱 NotificationService initialized - Client exists: {notification_service.client is not None}")
            logger.info(f"📱 Customer phone: {customer.phone}")
            
            if notification_service.client and customer.phone:
                sms_message = (
                    f"✅ Appointment Confirmed!\n\n"
                    f"Service: {request.service_type}\n"
                    f"Date: {scheduled_datetime.strftime('%b %d, %Y at %I:%M %p')}\n"
                    f"Location: {service_center.name}\n"
                    f"Vehicle: {vehicle.make} {vehicle.model}\n"
                    f"Duration: ~{estimated_duration} mins\n\n"
                    f"We'll see you soon!\n"
                    f"- Hero MotoCorp Service Center"
                )
                
                print(f"📤 Sending SMS to {customer.phone} from {notification_service.phone_number}")
                logger.info(f"📤 Sending SMS to {customer.phone} from {notification_service.phone_number}")
                message = notification_service.client.messages.create(
                    body=sms_message,
                    from_=notification_service.phone_number,
                    to=customer.phone
                )
                print(f"✅ SMS confirmation sent to {customer.phone}, SID: {message.sid}")
                logger.info(f"✅ SMS confirmation sent to {customer.phone}, SID: {message.sid}")
            else:
                print(f"⚠️ SMS not sent - Client: {notification_service.client is not None}, Phone: {customer.phone}")
                logger.warning(f"⚠️ SMS not sent - Client: {notification_service.client is not None}, Phone: {customer.phone}")
        except Exception as sms_error:
            print(f"❌ Failed to send SMS: {sms_error}")
            logger.error(f"❌ Failed to send SMS: {sms_error}", exc_info=True)
            # Don't fail the booking if SMS fails
        
        # Format response
        customer_name = f"{customer.first_name} {customer.last_name}"
        vehicle_info = f"{vehicle.make} {vehicle.model} ({vehicle.vin})"
        
        confirmation_message = (
            f"✅ Appointment confirmed!\n\n"
            f"Service: {request.service_type}\n"
            f"Date: {scheduled_datetime.strftime('%B %d, %Y')}\n"
            f"Time: {scheduled_datetime.strftime('%I:%M %p')}\n"
            f"Location: {service_center.name}\n"
            f"Estimated Duration: {estimated_duration} minutes\n\n"
            f"We'll send you a reminder 24 hours before your appointment."
        )
        
        return BookingResponse(
            appointment_id=appointment.appointment_id,
            customer_name=customer_name,
            vehicle_info=vehicle_info,
            service_type=request.service_type,
            scheduled_time=scheduled_datetime,
            service_center=service_center.name,
            status=appointment.status,
            confirmation_message=confirmation_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create booking: {str(e)}"
        )


@router.get("/customer/{customer_id}")
async def get_customer_appointments(customer_id: int, db: AsyncSession = Depends(get_db_session)):
    """Get all appointments for a customer"""
    try:
        query = select(Appointment).where(
            Appointment.customer_id == customer_id
        ).order_by(Appointment.scheduled_time.desc())
        
        result = await db.execute(query)
        appointments = result.scalars().all()
        
        appointment_list = []
        for apt in appointments:
            # Get vehicle info
            vehicle_query = select(Vehicle).where(Vehicle.vehicle_id == apt.vehicle_id)
            vehicle_result = await db.execute(vehicle_query)
            vehicle = vehicle_result.scalar_one_or_none()
            
            # Get service center info
            center_query = select(ServiceCenter).where(ServiceCenter.center_id == apt.center_id)
            center_result = await db.execute(center_query)
            center = center_result.scalar_one_or_none()
            
            appointment_list.append({
                "appointment_id": apt.appointment_id,
                "vehicle": f"{vehicle.make} {vehicle.model}" if vehicle else "Unknown",
                "service_type": apt.appointment_type,
                "scheduled_time": apt.scheduled_time.isoformat(),
                "status": apt.status,
                "service_center": center.name if center else "Unknown",
                "estimated_duration": apt.estimated_duration_minutes
            })
        
        return {
            "customer_id": customer_id,
            "total_appointments": len(appointment_list),
            "appointments": appointment_list
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get appointments: {str(e)}"
        )


def parse_appointment_datetime(date_str: str, time_str: str) -> datetime:
    """Parse appointment date and time strings into datetime object"""
    try:
        # Handle special dates
        now = datetime.now()
        
        if date_str.lower() == "tomorrow":
            base_date = now + timedelta(days=1)
        else:
            # Try to parse as date string
            try:
                base_date = datetime.strptime(date_str, "%m/%d/%Y")
            except:
                # If parsing fails, default to tomorrow
                base_date = now + timedelta(days=1)
        
        # Parse time
        time_str = time_str.strip()
        try:
            time_obj = datetime.strptime(time_str, "%I:%M %p")
        except:
            # Default to 9:00 AM if parsing fails
            time_obj = datetime.strptime("9:00 AM", "%I:%M %p")
        
        # Combine date and time
        scheduled_datetime = base_date.replace(
            hour=time_obj.hour,
            minute=time_obj.minute,
            second=0,
            microsecond=0
        )
        
        return scheduled_datetime
        
    except Exception as e:
        # Fallback to tomorrow at 9 AM
        return datetime.now() + timedelta(days=1, hours=9)
