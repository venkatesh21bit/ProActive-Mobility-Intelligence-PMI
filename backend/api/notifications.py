"""
Notifications API - Manage alerts, SMS, and voice calls
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel

from data.database import get_db_session
from data.models import (
    NotificationLog, Customer, Vehicle, FailurePrediction, Appointment
)
from services.notification_service import notification_service

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


class SendAlertRequest(BaseModel):
    customer_id: int
    vehicle_id: int
    prediction_id: int
    channel: str  # 'sms' or 'voice'
    
    class Config:
        # Allow extra fields to be ignored
        extra = "ignore"


class ScheduleReminderRequest(BaseModel):
    appointment_id: int


class NotificationResponse(BaseModel):
    notification_id: int
    type: str
    channel: str
    sent_at: str
    delivered: bool
    read: bool
    message: str
    customer: str
    vehicle: str


class NotificationStats(BaseModel):
    total_sent: int
    sms_sent: int
    voice_calls: int
    delivered: int
    pending: int
    failed: int


@router.post("/send-alert")
async def send_failure_alert(
    request: SendAlertRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Send SMS or voice alert for predicted failure"""
    
    # Get customer phone
    customer_result = await db.execute(
        select(Customer).where(Customer.customer_id == request.customer_id)
    )
    customer = customer_result.scalar_one_or_none()
    
    if not customer or not customer.phone:
        raise HTTPException(status_code=404, detail="Customer phone not found")
    
    # Get prediction
    prediction_result = await db.execute(
        select(FailurePrediction).where(FailurePrediction.prediction_id == request.prediction_id)
    )
    prediction = prediction_result.scalar_one_or_none()
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    # Send notification based on channel
    if request.channel == 'sms':
        result = await notification_service.send_failure_alert_sms(
            db, request.customer_id, request.vehicle_id, prediction, customer.phone
        )
    elif request.channel == 'voice':
        issue = f"{prediction.predicted_component.replace('_', ' ').title()} failure predicted with {prediction.failure_probability*100:.0f}% probability"
        result = await notification_service.make_emergency_call(
            db, request.customer_id, request.vehicle_id, customer.phone, issue
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid channel")
    
    if not result:
        raise HTTPException(status_code=500, detail="Failed to send notification")
    
    return {
        "success": True,
        "notification_id": result.get('notification_id'),
        "status": result.get('status'),
        "message": f"{request.channel.upper()} sent successfully"
    }


@router.post("/send-reminder/{appointment_id}")
async def send_appointment_reminder(
    appointment_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Send SMS reminder for appointment"""
    
    # Get appointment details
    appointment_result = await db.execute(
        select(Appointment, Customer).join(
            Customer, Appointment.customer_id == Customer.customer_id
        ).where(Appointment.appointment_id == appointment_id)
    )
    
    appt_data = appointment_result.first()
    if not appt_data:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    appointment, customer = appt_data
    
    if not customer.phone:
        raise HTTPException(status_code=404, detail="Customer phone not found")
    
    result = await notification_service.send_maintenance_reminder_sms(
        db,
        appointment.customer_id,
        appointment.vehicle_id,
        appointment.scheduled_time,
        customer.phone,
        appointment.appointment_type
    )
    
    if not result:
        raise HTTPException(status_code=500, detail="Failed to send reminder")
    
    return {
        "success": True,
        "notification_id": result.get('notification_id'),
        "message": "Reminder sent successfully"
    }


@router.get("/history", response_model=List[NotificationResponse])
async def get_notification_history(
    customer_id: Optional[int] = Query(None),
    vehicle_id: Optional[int] = Query(None),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db_session)
):
    """Get notification history with filters"""
    
    history = await notification_service.get_notification_history(
        db, customer_id=customer_id, vehicle_id=vehicle_id, limit=limit
    )
    
    return [NotificationResponse(**notif) for notif in history]


@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Mark notification as read"""
    
    success = await notification_service.mark_as_read(db, notification_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"success": True, "message": "Notification marked as read"}


@router.get("/stats", response_model=NotificationStats)
async def get_notification_stats(
    days: int = Query(30, le=365),
    db: AsyncSession = Depends(get_db_session)
):
    """Get notification statistics"""
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    # Total sent
    total_query = select(func.count(NotificationLog.notification_id)).where(
        NotificationLog.sent_at >= cutoff
    )
    total_sent = await db.scalar(total_query) or 0
    
    # SMS count
    sms_query = select(func.count(NotificationLog.notification_id)).where(
        and_(
            NotificationLog.channel == 'sms',
            NotificationLog.sent_at >= cutoff
        )
    )
    sms_sent = await db.scalar(sms_query) or 0
    
    # Voice count
    voice_query = select(func.count(NotificationLog.notification_id)).where(
        and_(
            NotificationLog.channel == 'voice',
            NotificationLog.sent_at >= cutoff
        )
    )
    voice_calls = await db.scalar(voice_query) or 0
    
    # Delivered
    delivered_query = select(func.count(NotificationLog.notification_id)).where(
        and_(
            NotificationLog.delivered == True,
            NotificationLog.sent_at >= cutoff
        )
    )
    delivered = await db.scalar(delivered_query) or 0
    
    return NotificationStats(
        total_sent=total_sent,
        sms_sent=sms_sent,
        voice_calls=voice_calls,
        delivered=delivered,
        pending=total_sent - delivered,
        failed=total_sent - delivered
    )


@router.post("/auto-alert-critical")
async def auto_send_critical_alerts(
    db: AsyncSession = Depends(get_db_session)
):
    """Automatically send alerts for all critical predictions without notifications"""
    
    # Get critical predictions from last 24 hours without notifications
    cutoff = datetime.utcnow() - timedelta(hours=24)
    
    query = select(FailurePrediction, Vehicle, Customer).join(
        Vehicle, FailurePrediction.vehicle_id == Vehicle.vehicle_id
    ).join(
        Customer, Vehicle.customer_id == Customer.customer_id
    ).where(
        and_(
            FailurePrediction.failure_probability >= 0.7,
            FailurePrediction.prediction_time >= cutoff
        )
    )
    
    result = await db.execute(query)
    predictions = result.all()
    
    sent_count = 0
    failed_count = 0
    
    for pred, vehicle, customer in predictions:
        if not customer.phone:
            continue
        
        # Check if alert already sent
        existing_query = select(func.count(NotificationLog.notification_id)).where(
            and_(
                NotificationLog.vehicle_id == vehicle.vehicle_id,
                NotificationLog.notification_type == 'failure_alert',
                NotificationLog.sent_at >= pred.prediction_time
            )
        )
        existing = await db.scalar(existing_query)
        
        if existing > 0:
            continue
        
        # Send alert
        result = await notification_service.send_failure_alert_sms(
            db, customer.customer_id, vehicle.vehicle_id, pred, customer.phone
        )
        
        if result:
            sent_count += 1
        else:
            failed_count += 1
    
    return {
        "success": True,
        "sent": sent_count,
        "failed": failed_count,
        "message": f"Sent {sent_count} critical alerts"
    }
