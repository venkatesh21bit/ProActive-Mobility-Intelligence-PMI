"""
Scheduling Agent
Manages service appointment scheduling with service centers
Queries available slots, proposes options, and finalizes bookings
"""

import sys
from pathlib import Path
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random

# Add parent directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select
from data.database import get_db
from data.models import ServiceCenter, Appointment, Vehicle, Customer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SchedulingAgent:
    """
    Agent for managing service appointment scheduling
    """
    
    def __init__(self):
        self.slot_duration_hours = 2  # Default appointment duration
        self.business_hours = {
            'start': 8,  # 8 AM
            'end': 18    # 6 PM
        }
        self.working_days = [0, 1, 2, 3, 4]  # Monday to Friday
        
    async def find_available_slots(
        self,
        customer_id: int,
        vehicle_id: int,
        diagnosis: Dict,
        preferred_date: Optional[datetime] = None,
        max_slots: int = 5
    ) -> List[Dict]:
        """
        Find available appointment slots
        
        Args:
            customer_id: Customer ID
            vehicle_id: Vehicle ID
            diagnosis: Diagnostic report
            preferred_date: Preferred date (defaults to tomorrow)
            max_slots: Maximum number of slots to return
            
        Returns:
            List of available slots
        """
        logger.info(f"Finding slots for customer {customer_id}, vehicle {vehicle_id}")
        
        # Determine urgency-based scheduling window
        urgency = diagnosis.get('urgency', 'routine')
        search_window = self._get_search_window(urgency, preferred_date)
        
        # Get nearest service center
        service_center = await self._get_nearest_service_center(customer_id)
        
        if not service_center:
            logger.warning("No service center found")
            return []
        
        # Get existing appointments
        existing_appointments = await self._get_existing_appointments(service_center['service_center_id'])
        
        # Generate available slots
        available_slots = self._generate_available_slots(
            service_center,
            existing_appointments,
            search_window,
            diagnosis,
            max_slots
        )
        
        return available_slots
    
    def _get_search_window(self, urgency: str, preferred_date: Optional[datetime]) -> Dict:
        """Determine search window based on urgency"""
        
        start_date = preferred_date or datetime.now()
        
        if urgency == 'immediate':
            # Same day or next day
            return {
                'start': start_date,
                'end': start_date + timedelta(days=1),
                'priority': 'critical'
            }
        elif urgency == 'urgent':
            # Within 2-3 days
            return {
                'start': start_date,
                'end': start_date + timedelta(days=3),
                'priority': 'high'
            }
        elif urgency == 'soon':
            # Within a week
            return {
                'start': start_date,
                'end': start_date + timedelta(days=7),
                'priority': 'medium'
            }
        else:
            # Within 2 weeks
            return {
                'start': start_date,
                'end': start_date + timedelta(days=14),
                'priority': 'low'
            }
    
    async def _get_nearest_service_center(self, customer_id: int) -> Optional[Dict]:
        """Get nearest service center for customer"""
        
        # In production, would use geolocation
        # For now, return mock service center or query database
        async for db in get_db():
            try:
                stmt = select(ServiceCenter).limit(1)
                result = await db.execute(stmt)
                center = result.scalar_one_or_none()
                
                if center:
                    return {
                        'service_center_id': center.service_center_id,
                        'name': center.name,
                        'location': center.location,
                        'phone': center.phone,
                        'capacity': center.capacity
                    }
                else:
                    # Return mock center if none exists
                    return {
                        'service_center_id': 1,
                        'name': 'Main Service Center',
                        'location': 'Downtown',
                        'phone': '+1-555-0100',
                        'capacity': 10
                    }
            except Exception as e:
                logger.error(f"Error fetching service center: {e}")
                return {
                    'service_center_id': 1,
                    'name': 'Main Service Center',
                    'location': 'Downtown',
                    'phone': '+1-555-0100',
                    'capacity': 10
                }
    
    async def _get_existing_appointments(self, service_center_id: int) -> List[Dict]:
        """Get existing appointments for service center"""
        
        async for db in get_db():
            try:
                # Get appointments for the next 30 days
                start_date = datetime.now()
                end_date = start_date + timedelta(days=30)
                
                stmt = select(Appointment).where(
                    Appointment.service_center_id == service_center_id,
                    Appointment.appointment_time >= start_date,
                    Appointment.appointment_time <= end_date,
                    Appointment.status.in_(['scheduled', 'confirmed'])
                )
                
                result = await db.execute(stmt)
                appointments = result.scalars().all()
                
                return [
                    {
                        'appointment_time': appt.appointment_time,
                        'estimated_duration_hours': appt.estimated_duration_hours or 2
                    }
                    for appt in appointments
                ]
            except Exception as e:
                logger.error(f"Error fetching appointments: {e}")
                return []
    
    def _generate_available_slots(
        self,
        service_center: Dict,
        existing_appointments: List[Dict],
        search_window: Dict,
        diagnosis: Dict,
        max_slots: int
    ) -> List[Dict]:
        """Generate available appointment slots"""
        
        slots = []
        current_date = search_window['start'].replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = search_window['end']
        
        estimated_duration = diagnosis.get('total_estimated_downtime_hours', 2)
        
        while current_date <= end_date and len(slots) < max_slots:
            # Skip weekends unless urgent
            if current_date.weekday() not in self.working_days:
                if search_window['priority'] != 'critical':
                    current_date += timedelta(days=1)
                    continue
            
            # Generate slots for this day
            day_slots = self._generate_day_slots(
                current_date,
                existing_appointments,
                service_center,
                estimated_duration
            )
            
            slots.extend(day_slots)
            
            if len(slots) >= max_slots:
                slots = slots[:max_slots]
                break
            
            current_date += timedelta(days=1)
        
        return slots
    
    def _generate_day_slots(
        self,
        date: datetime,
        existing_appointments: List[Dict],
        service_center: Dict,
        estimated_duration: float
    ) -> List[Dict]:
        """Generate available slots for a specific day"""
        
        slots = []
        capacity = service_center.get('capacity', 10)
        
        # Generate hourly slots during business hours
        current_hour = self.business_hours['start']
        
        while current_hour < self.business_hours['end']:
            slot_start = date.replace(hour=current_hour, minute=0)
            slot_end = slot_start + timedelta(hours=estimated_duration)
            
            # Check if slot conflicts with existing appointments
            if not self._has_conflict(slot_start, slot_end, existing_appointments, capacity):
                slots.append({
                    'start_time': slot_start.isoformat(),
                    'end_time': slot_end.isoformat(),
                    'duration_hours': estimated_duration,
                    'service_center_id': service_center['service_center_id'],
                    'service_center_name': service_center['name'],
                    'available_capacity': capacity - self._count_overlapping_appointments(
                        slot_start,
                        slot_end,
                        existing_appointments
                    )
                })
            
            current_hour += 1
        
        return slots
    
    def _has_conflict(
        self,
        slot_start: datetime,
        slot_end: datetime,
        existing_appointments: List[Dict],
        capacity: int
    ) -> bool:
        """Check if slot has conflicts"""
        
        overlapping = self._count_overlapping_appointments(slot_start, slot_end, existing_appointments)
        return overlapping >= capacity
    
    def _count_overlapping_appointments(
        self,
        slot_start: datetime,
        slot_end: datetime,
        existing_appointments: List[Dict]
    ) -> int:
        """Count appointments overlapping with slot"""
        
        count = 0
        
        for appt in existing_appointments:
            appt_start = appt['appointment_time']
            appt_end = appt_start + timedelta(hours=appt['estimated_duration_hours'])
            
            # Check for overlap
            if slot_start < appt_end and slot_end > appt_start:
                count += 1
        
        return count
    
    async def create_appointment(
        self,
        customer_id: int,
        vehicle_id: int,
        slot: Dict,
        diagnosis: Dict,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Create and finalize appointment booking
        
        Args:
            customer_id: Customer ID
            vehicle_id: Vehicle ID
            slot: Selected time slot
            diagnosis: Diagnostic report
            notes: Optional appointment notes
            
        Returns:
            Created appointment details
        """
        logger.info(f"Creating appointment for customer {customer_id}, vehicle {vehicle_id}")
        
        async for db in get_db():
            try:
                # Create appointment record
                appointment = Appointment(
                    customer_id=customer_id,
                    vehicle_id=vehicle_id,
                    service_center_id=slot['service_center_id'],
                    appointment_time=datetime.fromisoformat(slot['start_time']),
                    status='scheduled',
                    service_type='predictive_maintenance',
                    estimated_duration_hours=slot['duration_hours'],
                    estimated_cost=diagnosis.get('total_estimated_cost'),
                    notes=notes or f"Predicted issue: {diagnosis.get('issue_category')}",
                    created_at=datetime.utcnow()
                )
                
                db.add(appointment)
                await db.commit()
                await db.refresh(appointment)
                
                logger.info(f"Appointment created: {appointment.appointment_id}")
                
                return {
                    'appointment_id': appointment.appointment_id,
                    'customer_id': customer_id,
                    'vehicle_id': vehicle_id,
                    'appointment_time': appointment.appointment_time.isoformat(),
                    'service_center_id': slot['service_center_id'],
                    'service_center_name': slot['service_center_name'],
                    'status': appointment.status,
                    'estimated_duration_hours': appointment.estimated_duration_hours,
                    'estimated_cost': appointment.estimated_cost,
                    'confirmation_number': f"APT-{appointment.appointment_id:06d}"
                }
                
            except Exception as e:
                logger.error(f"Error creating appointment: {e}")
                await db.rollback()
                raise
    
    async def update_appointment_status(
        self,
        appointment_id: int,
        status: str,
        notes: Optional[str] = None
    ) -> Dict:
        """Update appointment status"""
        
        async for db in get_db():
            try:
                stmt = select(Appointment).where(Appointment.appointment_id == appointment_id)
                result = await db.execute(stmt)
                appointment = result.scalar_one_or_none()
                
                if not appointment:
                    return {'error': 'Appointment not found'}
                
                appointment.status = status
                if notes:
                    appointment.notes = f"{appointment.notes}\n{notes}"
                
                await db.commit()
                
                return {
                    'appointment_id': appointment_id,
                    'status': status,
                    'updated_at': datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error updating appointment: {e}")
                await db.rollback()
                raise
    
    async def cancel_appointment(self, appointment_id: int, reason: str) -> Dict:
        """Cancel appointment"""
        
        return await self.update_appointment_status(
            appointment_id,
            'cancelled',
            f"Cancellation reason: {reason}"
        )
    
    async def reschedule_appointment(
        self,
        appointment_id: int,
        new_slot: Dict
    ) -> Dict:
        """Reschedule existing appointment"""
        
        async for db in get_db():
            try:
                stmt = select(Appointment).where(Appointment.appointment_id == appointment_id)
                result = await db.execute(stmt)
                appointment = result.scalar_one_or_none()
                
                if not appointment:
                    return {'error': 'Appointment not found'}
                
                old_time = appointment.appointment_time
                appointment.appointment_time = datetime.fromisoformat(new_slot['start_time'])
                appointment.estimated_duration_hours = new_slot['duration_hours']
                
                await db.commit()
                
                return {
                    'appointment_id': appointment_id,
                    'old_time': old_time.isoformat(),
                    'new_time': appointment.appointment_time.isoformat(),
                    'updated_at': datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error rescheduling appointment: {e}")
                await db.rollback()
                raise
