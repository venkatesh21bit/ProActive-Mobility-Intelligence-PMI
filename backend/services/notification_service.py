"""
Notification Service - SMS and Voice Alerts via Twilio
"""
import os
from typing import Optional, List
from datetime import datetime
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from data.models import NotificationLog, Customer, Vehicle, FailurePrediction
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Handle SMS and Voice notifications via Twilio"""
    
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.phone_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        if not all([self.account_sid, self.auth_token, self.phone_number]):
            logger.warning("Twilio credentials not configured")
            self.client = None
        else:
            self.client = Client(self.account_sid, self.auth_token)
    
    async def send_failure_alert_sms(
        self,
        db: AsyncSession,
        customer_id: int,
        vehicle_id: int,
        prediction: FailurePrediction,
        customer_phone: str
    ) -> Optional[dict]:
        """Send SMS alert for predicted failure"""
        
        if not self.client:
            logger.error("Twilio client not initialized")
            return None
        
        try:
            # Get vehicle details
            vehicle_result = await db.execute(
                select(Vehicle).where(Vehicle.vehicle_id == vehicle_id)
            )
            vehicle = vehicle_result.scalar_one_or_none()
            
            if not vehicle:
                return None
            
            # Create message
            severity_emoji = "🚨" if prediction.failure_probability >= 0.7 else "⚠️"
            message = f"""{severity_emoji} PMI Alert: {vehicle.make} {vehicle.model} (VIN: {vehicle.vin})

Predicted Issue: {prediction.predicted_component.replace('_', ' ').title()}
Failure Risk: {prediction.failure_probability*100:.1f}%
Severity: {prediction.severity.upper()}

Action Required: Schedule maintenance immediately to prevent breakdown.

Reply SCHEDULE to book appointment.
"""
            
            # Send SMS
            sms = self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=customer_phone
            )
            
            # Log notification
            notification = NotificationLog(
                customer_id=customer_id,
                vehicle_id=vehicle_id,
                notification_type='failure_alert',
                channel='sms',
                sent_at=datetime.utcnow(),
                delivered=sms.status in ['sent', 'delivered'],
                message_content=message,
                meta_data={'twilio_sid': sms.sid, 'status': sms.status}
            )
            db.add(notification)
            await db.commit()
            
            return {
                'sid': sms.sid,
                'status': sms.status,
                'to': customer_phone,
                'notification_id': notification.notification_id
            }
            
        except TwilioRestException as e:
            logger.error(f"Twilio error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return None
    
    async def send_maintenance_reminder_sms(
        self,
        db: AsyncSession,
        customer_id: int,
        vehicle_id: int,
        appointment_time: datetime,
        customer_phone: str,
        service_type: str
    ) -> Optional[dict]:
        """Send SMS reminder for scheduled maintenance"""
        
        if not self.client:
            return None
        
        try:
            vehicle_result = await db.execute(
                select(Vehicle).where(Vehicle.vehicle_id == vehicle_id)
            )
            vehicle = vehicle_result.scalar_one_or_none()
            
            message = f"""📅 Appointment Reminder

Vehicle: {vehicle.make} {vehicle.model}
Service: {service_type}
Date: {appointment_time.strftime('%B %d, %Y at %I:%M %p')}

Reply CONFIRM to confirm or RESCHEDULE to change.
"""
            
            sms = self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=customer_phone
            )
            
            notification = NotificationLog(
                customer_id=customer_id,
                vehicle_id=vehicle_id,
                notification_type='appointment_reminder',
                channel='sms',
                sent_at=datetime.utcnow(),
                delivered=sms.status in ['sent', 'delivered'],
                message_content=message,
                meta_data={'twilio_sid': sms.sid, 'appointment_time': appointment_time.isoformat()}
            )
            db.add(notification)
            await db.commit()
            
            return {'sid': sms.sid, 'status': sms.status, 'notification_id': notification.notification_id}
            
        except Exception as e:
            logger.error(f"Error sending reminder: {e}")
            return None
    
    async def make_emergency_call(
        self,
        db: AsyncSession,
        customer_id: int,
        vehicle_id: int,
        customer_phone: str,
        issue_description: str
    ) -> Optional[dict]:
        """Make voice call for critical alerts"""
        
        if not self.client:
            return None
        
        try:
            # TwiML response for voice message
            twiml = f"""<Response>
                <Say voice="alice">
                    This is an urgent alert from ProActive Mobility Intelligence.
                    Your vehicle requires immediate attention.
                    {issue_description}
                    Please contact your service center as soon as possible.
                    Press 1 to schedule an appointment now.
                </Say>
                <Gather numDigits="1" action="/api/notifications/call-response">
                    <Say>Press 1 to schedule, or hang up to call later.</Say>
                </Gather>
            </Response>"""
            
            call = self.client.calls.create(
                twiml=twiml,
                from_=self.phone_number,
                to=customer_phone
            )
            
            notification = NotificationLog(
                customer_id=customer_id,
                vehicle_id=vehicle_id,
                notification_type='emergency_call',
                channel='voice',
                sent_at=datetime.utcnow(),
                delivered=call.status != 'failed',
                message_content=issue_description,
                meta_data={'twilio_sid': call.sid, 'status': call.status}
            )
            db.add(notification)
            await db.commit()
            
            return {'sid': call.sid, 'status': call.status, 'notification_id': notification.notification_id}
            
        except Exception as e:
            logger.error(f"Error making call: {e}")
            return None
    
    async def get_notification_history(
        self,
        db: AsyncSession,
        customer_id: Optional[int] = None,
        vehicle_id: Optional[int] = None,
        limit: int = 50
    ) -> List[dict]:
        """Get notification history"""
        
        query = select(NotificationLog, Customer, Vehicle).join(
            Customer, NotificationLog.customer_id == Customer.customer_id
        ).join(
            Vehicle, NotificationLog.vehicle_id == Vehicle.vehicle_id
        ).order_by(desc(NotificationLog.sent_at))
        
        if customer_id:
            query = query.where(NotificationLog.customer_id == customer_id)
        if vehicle_id:
            query = query.where(NotificationLog.vehicle_id == vehicle_id)
        
        query = query.limit(limit)
        
        result = await db.execute(query)
        notifications = result.all()
        
        history = []
        for notif, customer, vehicle in notifications:
            history.append({
                'notification_id': notif.notification_id,
                'type': notif.notification_type,
                'channel': notif.channel,
                'sent_at': notif.sent_at.isoformat(),
                'delivered': notif.delivered,
                'read': notif.read,
                'message': notif.message_content,
                'customer': f"{customer.first_name} {customer.last_name}",
                'vehicle': f"{vehicle.make} {vehicle.model} ({vehicle.vin})",
                'meta_data': notif.meta_data
            })
        
        return history
    
    async def mark_as_read(self, db: AsyncSession, notification_id: int) -> bool:
        """Mark notification as read"""
        try:
            result = await db.execute(
                select(NotificationLog).where(NotificationLog.notification_id == notification_id)
            )
            notification = result.scalar_one_or_none()
            
            if notification:
                notification.read = True
                await db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            return False


# Singleton instance
notification_service = NotificationService()
