"""
Dashboard API endpoints for frontend
Provides aggregated data for the ProActive Mobility Intelligence dashboard
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pydantic import BaseModel
import random

from data.database import get_db_session
from data.models import (
    Vehicle, VehicleTelemetry, FailurePrediction, 
    Appointment, MaintenanceRecord, Customer, ServiceCenter
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


class DashboardStats(BaseModel):
    total_vehicles: int
    critical_alerts: int
    scheduled_services: int
    healthy_vehicles: int


class AlertItem(BaseModel):
    id: int
    vehicle_id: int
    vin: str
    severity: str
    message: str
    timestamp: datetime
    status: str
    predicted_component: str | None = None
    failure_probability: float | None = None
    predicted_failure_date: datetime | None = None


class VehicleStatus(BaseModel):
    vehicle_id: int
    vin: str
    make: str | None = None
    model: str | None = None
    year: int | None = None
    status: str
    health_score: float
    last_reading: datetime
    mileage: float | None = None


class RecentPrediction(BaseModel):
    id: int
    vehicle_id: int
    vin: str
    failure_probability: float
    predicted_component: str
    prediction_time: datetime
    severity: str


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db_session)):
    """Get overview statistics for dashboard"""
    
    # Total vehicles
    total_vehicles_query = select(func.count(Vehicle.vehicle_id))
    total_vehicles = await db.scalar(total_vehicles_query) or 0
    
    # Critical alerts (predictions with >70% failure probability in last 24h)
    critical_cutoff = datetime.utcnow() - timedelta(days=1)
    critical_query = select(func.count(FailurePrediction.prediction_id)).where(
        and_(
            FailurePrediction.failure_probability >= 0.7,
            FailurePrediction.prediction_time >= critical_cutoff
        )
    )
    critical_alerts = await db.scalar(critical_query) or 0
    
    # Scheduled services (pending appointments)
    scheduled_query = select(func.count(Appointment.appointment_id)).where(
        Appointment.status.in_(['scheduled', 'confirmed'])
    )
    scheduled_services = await db.scalar(scheduled_query) or 0
    
    # Healthy vehicles (no critical predictions in last 7 days)
    healthy_cutoff = datetime.utcnow() - timedelta(days=7)
    
    # Get vehicles with critical predictions
    critical_vehicles_query = select(FailurePrediction.vehicle_id).where(
        and_(
            FailurePrediction.failure_probability >= 0.7,
            FailurePrediction.prediction_time >= healthy_cutoff
        )
    ).distinct()
    
    critical_vehicle_ids = await db.scalars(critical_vehicles_query)
    critical_vehicle_ids_list = list(critical_vehicle_ids)
    
    # Count healthy vehicles
    if critical_vehicle_ids_list:
        healthy_query = select(func.count(Vehicle.vehicle_id)).where(
            Vehicle.vehicle_id.notin_(critical_vehicle_ids_list)
        )
    else:
        healthy_query = select(func.count(Vehicle.vehicle_id))
    
    healthy_vehicles = await db.scalar(healthy_query) or 0
    
    return DashboardStats(
        total_vehicles=total_vehicles,
        critical_alerts=critical_alerts,
        scheduled_services=scheduled_services,
        healthy_vehicles=healthy_vehicles
    )


@router.get("/alerts", response_model=List[AlertItem])
async def get_recent_alerts(
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session)
):
    """Get recent critical alerts"""
    
    # Get recent high-risk predictions
    query = (
        select(FailurePrediction, Vehicle)
        .join(Vehicle, FailurePrediction.vehicle_id == Vehicle.vehicle_id)
        .where(FailurePrediction.failure_probability >= 0.5)
        .order_by(desc(FailurePrediction.prediction_time))
        .limit(limit)
    )
    
    result = await db.execute(query)
    predictions = result.all()
    
    alerts = []
    for pred, vehicle in predictions:
        # Determine severity based on probability
        if pred.failure_probability >= 0.8:
            severity = "critical"
        elif pred.failure_probability >= 0.7:
            severity = "high"
        elif pred.failure_probability >= 0.6:
            severity = "medium"
        else:
            severity = "low"
        
        # Determine status based on appointment
        status_query = select(Appointment).where(
            and_(
                Appointment.vehicle_id == vehicle.vehicle_id,
                Appointment.status.in_(['scheduled', 'confirmed'])
            )
        ).order_by(desc(Appointment.created_at)).limit(1)
        
        appointment_result = await db.execute(status_query)
        appointment = appointment_result.scalar_one_or_none()
        
        status = "scheduled" if appointment else "pending"
        
        # Create alert message
        component = pred.predicted_component or "component"
        message = f"{component.replace('_', ' ').title()} failure predicted"
        
        # Calculate predicted failure date from estimated days
        predicted_failure_date = None
        if pred.estimated_days_to_failure:
            predicted_failure_date = pred.prediction_time + timedelta(days=pred.estimated_days_to_failure)
        
        alerts.append(AlertItem(
            id=pred.prediction_id,
            vehicle_id=vehicle.vehicle_id,
            vin=vehicle.vin,
            severity=severity,
            message=message,
            timestamp=pred.prediction_time,
            status=status,
            predicted_component=pred.predicted_component,
            failure_probability=pred.failure_probability,
            predicted_failure_date=predicted_failure_date
        ))
    
    return alerts


@router.get("/vehicles", response_model=List[VehicleStatus])
async def get_vehicle_status(
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session)
):
    """Get vehicle health status"""
    
    # Get vehicles with their latest telemetry
    vehicles_query = select(Vehicle).limit(limit)
    vehicles_result = await db.execute(vehicles_query)
    vehicles = vehicles_result.scalars().all()
    
    vehicle_statuses = []
    
    for vehicle in vehicles:
        # Get latest telemetry
        telemetry_query = (
            select(VehicleTelemetry)
            .where(VehicleTelemetry.vehicle_id == vehicle.vin)
            .order_by(desc(VehicleTelemetry.time))
            .limit(1)
        )
        telemetry_result = await db.execute(telemetry_query)
        latest_telemetry = telemetry_result.scalar_one_or_none()
        
        # Get latest prediction
        prediction_query = (
            select(FailurePrediction)
            .where(FailurePrediction.vehicle_id == vehicle.vehicle_id)
            .order_by(desc(FailurePrediction.prediction_time))
            .limit(1)
        )
        prediction_result = await db.execute(prediction_query)
        latest_prediction = prediction_result.scalar_one_or_none()
        
        # Determine status and health score (0-10 scale for frontend)
        if latest_prediction:
            failure_prob = latest_prediction.failure_probability
            health_score = round((1 - failure_prob) * 10, 1)
            
            if failure_prob >= 0.7:
                status = "critical"
            elif failure_prob >= 0.5:
                status = "warning"
            else:
                status = "healthy"
        else:
            health_score = 8.5  # Default for vehicles without predictions (0-10 scale)
            status = "healthy"
        
        last_reading = latest_telemetry.time if latest_telemetry else vehicle.created_at
        
        vehicle_statuses.append(VehicleStatus(
            vehicle_id=vehicle.vehicle_id,
            vin=vehicle.vin,
            make=vehicle.make,
            model=vehicle.model,
            year=vehicle.year,
            status=status,
            health_score=health_score,
            last_reading=last_reading,
            mileage=latest_telemetry.odometer if latest_telemetry else vehicle.mileage
        ))
    
    return vehicle_statuses


@router.get("/predictions/recent", response_model=List[RecentPrediction])
async def get_recent_predictions(
    limit: int = 50,
    db: AsyncSession = Depends(get_db_session)
):
    """Get recent failure predictions"""
    
    query = (
        select(FailurePrediction, Vehicle)
        .join(Vehicle, FailurePrediction.vehicle_id == Vehicle.vehicle_id)
        .order_by(desc(FailurePrediction.prediction_time))
        .limit(limit)
    )
    
    result = await db.execute(query)
    predictions = result.all()
    
    recent_predictions = []
    for pred, vehicle in predictions:
        # Determine severity
        if pred.failure_probability >= 0.8:
            severity = "critical"
        elif pred.failure_probability >= 0.6:
            severity = "high"
        elif pred.failure_probability >= 0.4:
            severity = "medium"
        else:
            severity = "low"
        
        recent_predictions.append(RecentPrediction(
            id=pred.prediction_id,
            vehicle_id=vehicle.vehicle_id,
            vin=vehicle.vin,
            failure_probability=round(pred.failure_probability, 3),
            predicted_component=pred.predicted_component or "Unknown",
            prediction_time=pred.prediction_time,
            severity=severity
        ))
    
    return recent_predictions


@router.post("/seed", tags=["admin"])
async def seed_database(db: AsyncSession = Depends(get_db_session)):
    """
    Seed database with sample data (admin endpoint - remove in production)
    """
    try:
        # Check if data already exists
        result = await db.execute(select(func.count(Vehicle.vehicle_id)))
        count = result.scalar()
        if count > 0:
            return {"message": f"Database already has {count} vehicles. Skipping seed."}
        
        # Create a customer
        customer = Customer(
            first_name="Fleet",
            last_name="Manager",
            email="fleet@example.com",
            phone="+1234567890"
        )
        db.add(customer)
        await db.flush()  # Get customer_id
        
        # Create a service center
        service_center = ServiceCenter(
            name="Main Service Center",
            address="123 Main St",
            city="San Francisco",
            state="CA",
            zip_code="94105",
            phone="+1234567891"
        )
        db.add(service_center)
        await db.flush()  # Get center_id
        
        # Create 50 vehicles
        statuses = ['critical', 'warning', 'healthy']
        probabilities = [0.1, 0.3, 0.6]
        
        for i in range(1, 51):
            status = random.choices(statuses, probabilities)[0]
            
            vehicle = Vehicle(
                vin=f"1HGBH41JXMN{109186+i:06d}",  # 17 characters total
                customer_id=customer.customer_id,
                make="Toyota" if i % 3 == 0 else "Honda" if i % 3 == 1 else "Ford",
                model="Camry" if i % 3 == 0 else "Accord" if i % 3 == 1 else "F-150",
                year=2020 + (i % 5)
            )
            db.add(vehicle)
            await db.flush()  # Get vehicle_id
            
            # Create telemetry
            telemetry_time = datetime.utcnow() - timedelta(minutes=random.randint(1, 60))
            telemetry = VehicleTelemetry(
                time=telemetry_time,
                vehicle_id=str(vehicle.vehicle_id),
                vin=vehicle.vin,
                engine_temperature=90 + random.uniform(-10, 20) if status != 'critical' else 110 + random.uniform(0, 15),
                coolant_temperature=85 + random.uniform(-5, 10),
                oil_pressure=45 + random.uniform(-5, 5) if status != 'critical' else 25 + random.uniform(-5, 5),
                vibration_level=0.5 + random.uniform(0, 0.3) if status != 'critical' else 1.2 + random.uniform(0, 0.5),
                rpm=int(2000 + random.uniform(-500, 1000)),
                speed=60 + random.uniform(-20, 20),
                fuel_level=50 + random.uniform(-30, 40),
                battery_voltage=12.6 + random.uniform(-0.3, 0.3),
                odometer=50000 + random.randint(0, 100000)
            )
            db.add(telemetry)
            
            # Create predictions
            if status == 'critical':
                failure_prob = 0.75 + random.uniform(0, 0.20)
                component = random.choice(['engine', 'transmission', 'brakes', 'oil_system'])
            elif status == 'warning':
                failure_prob = 0.55 + random.uniform(0, 0.15)
                component = random.choice(['battery', 'cooling_system', 'suspension'])
            else:
                failure_prob = 0.15 + random.uniform(0, 0.25)
                component = random.choice(['tires', 'filters', 'fluids'])
            
            prediction = FailurePrediction(
                vehicle_id=vehicle.vehicle_id,
                vin=vehicle.vin,
                prediction_time=datetime.utcnow() - timedelta(hours=random.randint(1, 24)),
                failure_probability=min(failure_prob, 0.99),
                predicted_component=component,
                severity="critical" if failure_prob >= 0.7 else "warning" if failure_prob >= 0.5 else "low",
                confidence_score=0.85 + random.uniform(0, 0.10)
            )
            db.add(prediction)
            
            # Create appointments for critical and some warning vehicles
            if status == 'critical' or (status == 'warning' and random.random() < 0.5):
                appointment = Appointment(
                    vehicle_id=vehicle.vehicle_id,
                    customer_id=customer.customer_id,
                    center_id=service_center.center_id,
                    scheduled_time=datetime.utcnow() + timedelta(days=random.randint(1, 14)),
                    appointment_type="Preventive Maintenance" if status == 'warning' else "Emergency Repair",
                    estimated_duration_minutes=120 if status == 'warning' else 240,
                    status="scheduled" if random.random() < 0.7 else "confirmed"
                )
                db.add(appointment)
        
        await db.commit()
        return {
            "message": "Database seeded successfully",
            "vehicles": 50,
            "telemetry_records": 50,
            "predictions": 50,
            "appointments": "~25"
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error seeding database: {str(e)}")

