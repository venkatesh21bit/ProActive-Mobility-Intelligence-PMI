"""
Analytics API - Fleet insights, trends, and reporting
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, case
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from data.database import get_db_session
from data.models import (
    Vehicle, FailurePrediction, Appointment, MaintenanceRecord,
    VehicleTelemetry, Customer
)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


class FleetHealthTrend(BaseModel):
    date: str
    healthy: int
    warning: int
    critical: int
    total: int


class ComponentFailureStats(BaseModel):
    component: str
    prediction_count: int
    avg_probability: float
    critical_count: int


class MaintenanceCostAnalysis(BaseModel):
    period: str
    parts_cost: float
    labor_cost: float
    total_cost: float
    appointment_count: int


class PredictionAccuracy(BaseModel):
    total_predictions: int
    verified_predictions: int
    true_positives: int
    false_positives: int
    accuracy_rate: float


class VehicleRiskScore(BaseModel):
    vehicle_id: int
    vin: str
    make: str
    model: str
    year: int
    risk_score: float
    recent_failures: int
    last_maintenance: Optional[str]


@router.get("/fleet-health-trend")
async def get_fleet_health_trend(
    days: int = Query(30, le=365),
    db: AsyncSession = Depends(get_db_session)
):
    """Get fleet health trend over time"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    trends = []
    
    for i in range(days):
        date = start_date + timedelta(days=i)
        next_date = date + timedelta(days=1)
        
        # Get predictions for this day
        predictions_query = select(FailurePrediction).where(
            and_(
                FailurePrediction.prediction_time >= date,
                FailurePrediction.prediction_time < next_date
            )
        )
        result = await db.execute(predictions_query)
        predictions = result.scalars().all()
        
        # Count by severity
        critical = sum(1 for p in predictions if p.failure_probability >= 0.7)
        warning = sum(1 for p in predictions if 0.5 <= p.failure_probability < 0.7)
        healthy = sum(1 for p in predictions if p.failure_probability < 0.5)
        
        trends.append(FleetHealthTrend(
            date=date.strftime('%Y-%m-%d'),
            critical=critical,
            warning=warning,
            healthy=healthy,
            total=len(predictions)
        ))
    
    return trends


@router.get("/component-failures")
async def get_component_failure_stats(
    days: int = Query(90, le=365),
    db: AsyncSession = Depends(get_db_session)
):
    """Analyze failure predictions by component"""
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    # Get predictions grouped by component
    query = select(
        FailurePrediction.predicted_component,
        func.count(FailurePrediction.prediction_id).label('count'),
        func.avg(FailurePrediction.failure_probability).label('avg_prob'),
        func.sum(
            case((FailurePrediction.failure_probability >= 0.7, 1), else_=0)
        ).label('critical_count')
    ).where(
        FailurePrediction.prediction_time >= cutoff
    ).group_by(
        FailurePrediction.predicted_component
    ).order_by(desc('count'))
    
    result = await db.execute(query)
    stats = result.all()
    
    return [
        ComponentFailureStats(
            component=component,
            prediction_count=count,
            avg_probability=round(avg_prob, 3),
            critical_count=critical_count or 0
        )
        for component, count, avg_prob, critical_count in stats
    ]


@router.get("/maintenance-costs")
async def get_maintenance_cost_analysis(
    months: int = Query(12, le=24),
    db: AsyncSession = Depends(get_db_session)
):
    """Analyze maintenance costs over time"""
    
    costs = []
    
    for i in range(months):
        start_date = datetime.utcnow().replace(day=1) - timedelta(days=30*i)
        if i < months - 1:
            end_date = datetime.utcnow().replace(day=1) - timedelta(days=30*(i-1))
        else:
            end_date = datetime.utcnow()
        
        # Get maintenance records for this period
        query = select(
            func.sum(MaintenanceRecord.parts_cost).label('parts'),
            func.sum(MaintenanceRecord.labor_cost).label('labor'),
            func.sum(MaintenanceRecord.total_cost).label('total'),
            func.count(MaintenanceRecord.maintenance_id).label('count')
        ).where(
            and_(
                MaintenanceRecord.service_date >= start_date,
                MaintenanceRecord.service_date < end_date
            )
        )
        
        result = await db.execute(query)
        data = result.first()
        
        costs.append(MaintenanceCostAnalysis(
            period=start_date.strftime('%Y-%m'),
            parts_cost=float(data.parts or 0),
            labor_cost=float(data.labor or 0),
            total_cost=float(data.total or 0),
            appointment_count=data.count or 0
        ))
    
    return list(reversed(costs))


@router.get("/prediction-accuracy")
async def get_prediction_accuracy(
    days: int = Query(90, le=365),
    db: AsyncSession = Depends(get_db_session)
):
    """Calculate ML prediction accuracy"""
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    # Total predictions
    total_query = select(func.count(FailurePrediction.prediction_id)).where(
        FailurePrediction.prediction_time >= cutoff
    )
    total = await db.scalar(total_query) or 0
    
    # Verified predictions (where actual_failure is not null)
    verified_query = select(func.count(FailurePrediction.prediction_id)).where(
        and_(
            FailurePrediction.prediction_time >= cutoff,
            FailurePrediction.actual_failure.isnot(None)
        )
    )
    verified = await db.scalar(verified_query) or 0
    
    # True positives (predicted failure and actually failed)
    tp_query = select(func.count(FailurePrediction.prediction_id)).where(
        and_(
            FailurePrediction.prediction_time >= cutoff,
            FailurePrediction.failure_probability >= 0.5,
            FailurePrediction.actual_failure == True
        )
    )
    true_positives = await db.scalar(tp_query) or 0
    
    # False positives (predicted failure but didn't fail)
    fp_query = select(func.count(FailurePrediction.prediction_id)).where(
        and_(
            FailurePrediction.prediction_time >= cutoff,
            FailurePrediction.failure_probability >= 0.5,
            FailurePrediction.actual_failure == False
        )
    )
    false_positives = await db.scalar(fp_query) or 0
    
    accuracy = (true_positives / verified * 100) if verified > 0 else 0
    
    return PredictionAccuracy(
        total_predictions=total,
        verified_predictions=verified,
        true_positives=true_positives,
        false_positives=false_positives,
        accuracy_rate=round(accuracy, 2)
    )


@router.get("/vehicle-risk-scores")
async def get_vehicle_risk_scores(
    limit: int = Query(50, le=200),
    min_risk: float = Query(0.5, ge=0, le=1),
    db: AsyncSession = Depends(get_db_session)
):
    """Calculate risk scores for vehicles"""
    
    # Get vehicles with their latest predictions
    vehicles_query = select(Vehicle)
    vehicles_result = await db.execute(vehicles_query)
    vehicles = vehicles_result.scalars().all()
    
    risk_scores = []
    
    for vehicle in vehicles:
        # Get recent predictions (last 30 days)
        cutoff = datetime.utcnow() - timedelta(days=30)
        predictions_query = select(FailurePrediction).where(
            and_(
                FailurePrediction.vehicle_id == vehicle.vehicle_id,
                FailurePrediction.prediction_time >= cutoff
            )
        ).order_by(desc(FailurePrediction.prediction_time))
        
        predictions_result = await db.execute(predictions_query)
        predictions = predictions_result.scalars().all()
        
        if not predictions:
            continue
        
        # Calculate risk score (average of recent predictions)
        risk_score = sum(p.failure_probability for p in predictions) / len(predictions)
        
        if risk_score < min_risk:
            continue
        
        # Count recent failures
        recent_failures = sum(1 for p in predictions if p.failure_probability >= 0.7)
        
        # Get last maintenance
        maintenance_query = select(MaintenanceRecord).where(
            MaintenanceRecord.vehicle_id == vehicle.vehicle_id
        ).order_by(desc(MaintenanceRecord.service_date)).limit(1)
        
        maintenance_result = await db.execute(maintenance_query)
        last_maintenance = maintenance_result.scalar_one_or_none()
        
        risk_scores.append(VehicleRiskScore(
            vehicle_id=vehicle.vehicle_id,
            vin=vehicle.vin,
            make=vehicle.make,
            model=vehicle.model,
            year=vehicle.year,
            risk_score=round(risk_score, 3),
            recent_failures=recent_failures,
            last_maintenance=last_maintenance.service_date.isoformat() if last_maintenance else None
        ))
    
    # Sort by risk score descending
    risk_scores.sort(key=lambda x: x.risk_score, reverse=True)
    
    return risk_scores[:limit]


@router.get("/fleet-summary")
async def get_fleet_summary(db: AsyncSession = Depends(get_db_session)):
    """Get comprehensive fleet summary"""
    
    # Total vehicles
    total_vehicles = await db.scalar(select(func.count(Vehicle.vehicle_id))) or 0
    
    # Active appointments
    active_appointments = await db.scalar(
        select(func.count(Appointment.appointment_id)).where(
            Appointment.status.in_(['scheduled', 'confirmed'])
        )
    ) or 0
    
    # Recent predictions (last 7 days)
    cutoff = datetime.utcnow() - timedelta(days=7)
    recent_predictions = await db.scalar(
        select(func.count(FailurePrediction.prediction_id)).where(
            FailurePrediction.prediction_time >= cutoff
        )
    ) or 0
    
    # Total active alerts (all predictions with probability >= 0.5)
    total_alerts = await db.scalar(
        select(func.count(FailurePrediction.prediction_id)).where(
            FailurePrediction.failure_probability >= 0.5
        )
    ) or 0
    
    # Average fleet health (last prediction per vehicle)
    vehicles_result = await db.execute(select(Vehicle.vehicle_id))
    vehicle_ids = [v[0] for v in vehicles_result.all()]
    
    health_scores = []
    for vid in vehicle_ids:
        pred_query = select(FailurePrediction).where(
            FailurePrediction.vehicle_id == vid
        ).order_by(desc(FailurePrediction.prediction_time)).limit(1)
        
        pred_result = await db.execute(pred_query)
        pred = pred_result.scalar_one_or_none()
        
        if pred:
            health_scores.append((1 - pred.failure_probability) * 100)
    
    avg_health = sum(health_scores) / len(health_scores) if health_scores else 0
    
    return {
        "total_vehicles": total_vehicles,
        "active_appointments": active_appointments,
        "recent_predictions": recent_predictions,
        "total_alerts": total_alerts,
        "avg_health_score": round(avg_health, 1),
        "timestamp": datetime.utcnow().isoformat()
    }
