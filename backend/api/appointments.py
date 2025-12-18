"""
Appointments API - Schedule and manage service appointments
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, or_
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel

from data.database import get_db_session
from data.models import Appointment, Vehicle, Customer, ServiceCenter, MaintenanceRecord

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


class CreateAppointmentRequest(BaseModel):
    vehicle_id: int
    customer_id: int
    center_id: int
    scheduled_time: datetime
    appointment_type: str
    predicted_issue: Optional[str] = None
    estimated_duration_minutes: Optional[int] = 60


class UpdateAppointmentRequest(BaseModel):
    scheduled_time: Optional[datetime] = None
    status: Optional[str] = None
    actual_issue: Optional[str] = None
    customer_consent: Optional[bool] = None


class AppointmentDetail(BaseModel):
    appointment_id: int
    vehicle_id: int
    vehicle_vin: str
    vehicle_model: str
    customer_name: str
    customer_phone: Optional[str]
    service_center_name: str
    service_center_id: int
    scheduled_time: datetime
    appointment_type: str
    status: str
    predicted_issue: Optional[str]
    actual_issue: Optional[str]
    estimated_duration_minutes: Optional[int]
    customer_consent: bool
    created_at: datetime


class ServiceCenterInfo(BaseModel):
    center_id: int
    name: str
    address: str
    city: Optional[str]
    state: Optional[str]
    phone: Optional[str]
    capacity: int
    available_slots: int


@router.post("/create")
async def create_appointment(
    request: CreateAppointmentRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Create new service appointment"""
    
    # Validate vehicle exists
    vehicle_result = await db.execute(
        select(Vehicle).where(Vehicle.vehicle_id == request.vehicle_id)
    )
    if not vehicle_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # Check service center capacity
    appointments_count_query = select(func.count(Appointment.appointment_id)).where(
        and_(
            Appointment.center_id == request.center_id,
            Appointment.scheduled_time >= request.scheduled_time - timedelta(hours=1),
            Appointment.scheduled_time <= request.scheduled_time + timedelta(hours=1),
            Appointment.status.in_(['scheduled', 'confirmed'])
        )
    )
    appointments_count = await db.scalar(appointments_count_query) or 0
    
    center_result = await db.execute(
        select(ServiceCenter).where(ServiceCenter.center_id == request.center_id)
    )
    center = center_result.scalar_one_or_none()
    
    if not center:
        raise HTTPException(status_code=404, detail="Service center not found")
    
    if appointments_count >= center.capacity:
        raise HTTPException(status_code=400, detail="Service center fully booked for this time slot")
    
    # Create appointment
    appointment = Appointment(
        vehicle_id=request.vehicle_id,
        customer_id=request.customer_id,
        center_id=request.center_id,
        scheduled_time=request.scheduled_time,
        appointment_type=request.appointment_type,
        predicted_issue=request.predicted_issue,
        estimated_duration_minutes=request.estimated_duration_minutes,
        status='scheduled'
    )
    
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)
    
    return {
        "success": True,
        "appointment_id": appointment.appointment_id,
        "message": "Appointment created successfully"
    }


@router.get("/list", response_model=List[AppointmentDetail])
async def list_appointments(
    status: Optional[str] = Query(None),
    customer_id: Optional[int] = Query(None),
    vehicle_id: Optional[int] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db_session)
):
    """List appointments with filters"""
    
    query = select(Appointment, Vehicle, Customer, ServiceCenter).join(
        Vehicle, Appointment.vehicle_id == Vehicle.vehicle_id
    ).join(
        Customer, Appointment.customer_id == Customer.customer_id
    ).join(
        ServiceCenter, Appointment.center_id == ServiceCenter.center_id
    ).order_by(desc(Appointment.scheduled_time))
    
    # Apply filters
    if status:
        query = query.where(Appointment.status == status)
    if customer_id:
        query = query.where(Appointment.customer_id == customer_id)
    if vehicle_id:
        query = query.where(Appointment.vehicle_id == vehicle_id)
    if from_date:
        query = query.where(Appointment.scheduled_time >= from_date)
    if to_date:
        query = query.where(Appointment.scheduled_time <= to_date)
    
    query = query.limit(limit)
    
    result = await db.execute(query)
    appointments = result.all()
    
    return [
        AppointmentDetail(
            appointment_id=appt.appointment_id,
            vehicle_id=vehicle.vehicle_id,
            vehicle_vin=vehicle.vin,
            vehicle_model=f"{vehicle.make} {vehicle.model}",
            customer_name=f"{customer.first_name} {customer.last_name}",
            customer_phone=customer.phone,
            service_center_name=center.name,
            service_center_id=center.center_id,
            scheduled_time=appt.scheduled_time,
            appointment_type=appt.appointment_type,
            status=appt.status,
            predicted_issue=appt.predicted_issue,
            actual_issue=appt.actual_issue,
            estimated_duration_minutes=appt.estimated_duration_minutes,
            customer_consent=appt.customer_consent or False,
            created_at=appt.created_at
        )
        for appt, vehicle, customer, center in appointments
    ]


@router.get("/{appointment_id}", response_model=AppointmentDetail)
async def get_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Get appointment details"""
    
    query = select(Appointment, Vehicle, Customer, ServiceCenter).join(
        Vehicle, Appointment.vehicle_id == Vehicle.vehicle_id
    ).join(
        Customer, Appointment.customer_id == Customer.customer_id
    ).join(
        ServiceCenter, Appointment.center_id == ServiceCenter.center_id
    ).where(Appointment.appointment_id == appointment_id)
    
    result = await db.execute(query)
    data = result.first()
    
    if not data:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    appt, vehicle, customer, center = data
    
    return AppointmentDetail(
        appointment_id=appt.appointment_id,
        vehicle_id=vehicle.vehicle_id,
        vehicle_vin=vehicle.vin,
        vehicle_model=f"{vehicle.make} {vehicle.model}",
        customer_name=f"{customer.first_name} {customer.last_name}",
        customer_phone=customer.phone,
        service_center_name=center.name,
        service_center_id=center.center_id,
        scheduled_time=appt.scheduled_time,
        appointment_type=appt.appointment_type,
        status=appt.status,
        predicted_issue=appt.predicted_issue,
        actual_issue=appt.actual_issue,
        estimated_duration_minutes=appt.estimated_duration_minutes,
        customer_consent=appt.customer_consent or False,
        created_at=appt.created_at
    )


@router.put("/{appointment_id}")
async def update_appointment(
    appointment_id: int,
    request: UpdateAppointmentRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Update appointment details"""
    
    result = await db.execute(
        select(Appointment).where(Appointment.appointment_id == appointment_id)
    )
    appointment = result.scalar_one_or_none()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if request.scheduled_time:
        appointment.scheduled_time = request.scheduled_time
    if request.status:
        appointment.status = request.status
        if request.status == 'completed':
            appointment.completed_at = datetime.utcnow()
    if request.actual_issue:
        appointment.actual_issue = request.actual_issue
    if request.customer_consent is not None:
        appointment.customer_consent = request.customer_consent
        if request.customer_consent:
            appointment.consent_timestamp = datetime.utcnow()
    
    await db.commit()
    
    return {"success": True, "message": "Appointment updated successfully"}


@router.delete("/{appointment_id}")
async def cancel_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Cancel appointment"""
    
    result = await db.execute(
        select(Appointment).where(Appointment.appointment_id == appointment_id)
    )
    appointment = result.scalar_one_or_none()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    appointment.status = 'cancelled'
    await db.commit()
    
    return {"success": True, "message": "Appointment cancelled"}


@router.get("/service-centers/available", response_model=List[ServiceCenterInfo])
async def get_available_service_centers(
    scheduled_time: datetime = Query(...),
    db: AsyncSession = Depends(get_db_session)
):
    """Get service centers with available capacity for given time"""
    
    # Get all service centers
    centers_result = await db.execute(select(ServiceCenter))
    centers = centers_result.scalars().all()
    
    available_centers = []
    
    for center in centers:
        # Count appointments in 2-hour window
        appointments_query = select(func.count(Appointment.appointment_id)).where(
            and_(
                Appointment.center_id == center.center_id,
                Appointment.scheduled_time >= scheduled_time - timedelta(hours=1),
                Appointment.scheduled_time <= scheduled_time + timedelta(hours=1),
                Appointment.status.in_(['scheduled', 'confirmed'])
            )
        )
        appointments_count = await db.scalar(appointments_query) or 0
        
        available_slots = center.capacity - appointments_count
        
        available_centers.append(ServiceCenterInfo(
            center_id=center.center_id,
            name=center.name,
            address=center.address,
            city=center.city,
            state=center.state,
            phone=center.phone,
            capacity=center.capacity,
            available_slots=max(0, available_slots)
        ))
    
    return available_centers
