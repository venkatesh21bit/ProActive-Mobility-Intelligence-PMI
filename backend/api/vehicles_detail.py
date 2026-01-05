"""
Vehicle Details API with component health visualization data
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from data.database import get_db_session
from data.models import Vehicle, VehicleTelemetry, FailurePrediction
from typing import Dict, Any
from datetime import datetime

router = APIRouter(prefix="/api/vehicles", tags=["Vehicles"])

@router.get("/{vehicle_id}/details")
async def get_vehicle_details(
    vehicle_id: int,
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """Get comprehensive vehicle details including component health for 2D visualization"""
    
    try:
        # Get vehicle
        vehicle_result = await db.execute(
            select(Vehicle).where(Vehicle.vehicle_id == vehicle_id)
        )
        vehicle = vehicle_result.scalar_one_or_none()
        
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        
        # Get latest telemetry using VIN
        try:
            telemetry_result = await db.execute(
                select(VehicleTelemetry)
                .where(VehicleTelemetry.vehicle_id == vehicle.vin)
                .order_by(VehicleTelemetry.time.desc())
                .limit(1)
            )
            telemetry = telemetry_result.scalar_one_or_none()
        except Exception as e:
            print(f"Error fetching telemetry: {e}")
            telemetry = None
        
        # Get failure predictions
        try:
            predictions_result = await db.execute(
                select(FailurePrediction)
                .where(FailurePrediction.vehicle_id == vehicle_id)
                .order_by(FailurePrediction.prediction_time.desc())
            )
            predictions = predictions_result.scalars().all()
        except Exception as e:
            print(f"Error fetching predictions: {e}")
            predictions = []
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_vehicle_details: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # Calculate vehicle's health score same way as dashboard
    vehicle_health_score = 8.5  # Default
    vehicle_status = "healthy"
    
    if predictions:
        try:
            # Get highest failure probability
            max_failure_prob = max(getattr(p, 'failure_probability', 0.1) for p in predictions)
            vehicle_health_score = round((1 - max_failure_prob) * 10, 1)
            
            # Determine status based on health score
            if vehicle_health_score < 5:
                vehicle_status = "critical"
            elif vehicle_health_score < 8:
                vehicle_status = "warning"
        except Exception as e:
            print(f"Error calculating health score: {e}")
            # Keep defaults
    
    # Build component health map with base healthy state
    components = {
        "engine": {"status": "healthy", "health": 85, "issues": []},
        "transmission": {"status": "healthy", "health": 85, "issues": []},
        "brakes": {"status": "healthy", "health": 85, "issues": []},
        "battery": {"status": "healthy", "health": 85, "issues": []},
        "cooling_system": {"status": "healthy", "health": 85, "issues": []},
        "oil_system": {"status": "healthy", "health": 85, "issues": []},
        "suspension": {"status": "healthy", "health": 85, "issues": []},
        "tires": {"status": "healthy", "health": 85, "issues": []},
        "exhaust": {"status": "healthy", "health": 85, "issues": []},
        "fuel_system": {"status": "healthy", "health": 85, "issues": []}
    }
    
    # Update components based on vehicle's overall status
    if vehicle_status == 'critical':
        # Mark some components as critical for critical vehicles
        critical_comps = ['engine', 'transmission']
        for comp in critical_comps:
            components[comp]["status"] = "critical"
            components[comp]["health"] = max(10, int(vehicle_health_score * 10))
            components[comp]["issues"].append({
                "severity": "critical",
                "message": "Component requires immediate attention",
                "action": "Schedule service immediately"
            })
    elif vehicle_status == 'warning':
        # Mark some components as warning for warning vehicles
        warning_comps = ['engine', 'brakes']
        for comp in warning_comps:
            components[comp]["status"] = "warning"
            components[comp]["health"] = max(50, int(vehicle_health_score * 10))
            components[comp]["issues"].append({
                "severity": "warning",
                "message": "Component needs attention soon",
                "action": "Schedule maintenance"
            })
    
    # Update component health based on predictions
    for prediction in predictions:
        try:
            component_name = getattr(prediction, 'predicted_component', '').lower().replace(' ', '_')
            if component_name in components:
                failure_prob = getattr(prediction, 'failure_probability', 0.0)
                
                if failure_prob >= 0.7:
                    components[component_name]["status"] = "critical"
                    components[component_name]["health"] = int((1 - failure_prob) * 100)
                    components[component_name]["issues"].append({
                        "severity": "critical",
                        "probability": f"{failure_prob * 100:.1f}%",
                        "estimated_days": getattr(prediction, 'estimated_days_to_failure', 0),
                        "prediction_time": getattr(prediction, 'prediction_time', datetime.utcnow()).isoformat()
                    })
                elif failure_prob >= 0.5:
                    components[component_name]["status"] = "warning"
                    components[component_name]["health"] = int((1 - failure_prob) * 100)
                    components[component_name]["issues"].append({
                        "severity": "warning",
                        "probability": f"{failure_prob * 100:.1f}%",
                        "estimated_days": getattr(prediction, 'estimated_days_to_failure', 0),
                        "prediction_time": getattr(prediction, 'prediction_time', datetime.utcnow()).isoformat()
                    })
        except Exception as e:
            print(f"Error processing prediction: {e}")
            continue
    
    # Update based on telemetry
    if telemetry:
        # Engine health from temperature
        if telemetry.engine_temperature and telemetry.engine_temperature > 105:
            if components["engine"]["status"] == "healthy":
                components["engine"]["status"] = "warning"
                components["engine"]["health"] = min(components["engine"]["health"], 70)
                components["engine"]["issues"].append({
                    "severity": "warning",
                    "message": f"High temperature: {telemetry.engine_temperature:.1f}°C",
                    "action": "Check coolant levels"
                })
        
        # Oil system from pressure
        if telemetry.oil_pressure and telemetry.oil_pressure < 30:
            if components["oil_system"]["status"] == "healthy":
                components["oil_system"]["status"] = "critical"
                components["oil_system"]["health"] = 40
                components["oil_system"]["issues"].append({
                    "severity": "critical",
                    "message": f"Low oil pressure: {telemetry.oil_pressure:.1f} PSI",
                    "action": "Immediate inspection required"
                })
        
        # Battery from voltage
        if telemetry.battery_voltage and telemetry.battery_voltage < 12.2:
            if components["battery"]["status"] == "healthy":
                components["battery"]["status"] = "warning"
                components["battery"]["health"] = 60
                components["battery"]["issues"].append({
                    "severity": "warning",
                    "message": f"Low voltage: {telemetry.battery_voltage:.1f}V",
                    "action": "Check battery condition"
                })
        
        # Vibration level for suspension
        if telemetry.vibration_level and telemetry.vibration_level > 1.0:
            if components["suspension"]["status"] == "healthy":
                components["suspension"]["status"] = "warning"
                components["suspension"]["health"] = 65
                components["suspension"]["issues"].append({
                    "severity": "warning",
                    "message": f"High vibration: {telemetry.vibration_level:.2f}",
                    "action": "Inspect suspension components"
                })
    
    # Use vehicle's actual health score from database
    overall_health = vehicle_health_score * 10  # Convert to 0-100 scale
    overall_status = vehicle.status if vehicle.status else "healthy"
    
    # Count component statuses for summary
    critical_count = sum(1 for comp in components.values() if comp["status"] == "critical")
    warning_count = sum(1 for comp in components.values() if comp["status"] == "warning")
    
    return {
        "vehicle": {
            "vehicle_id": vehicle.vehicle_id,
            "vin": vehicle.vin,
            "make": vehicle.make,
            "model": vehicle.model,
            "year": vehicle.year,
            "mileage": vehicle.mileage,
            "purchase_date": vehicle.purchase_date.isoformat() if vehicle.purchase_date else None,
            "warranty_expiry": vehicle.warranty_expiry.isoformat() if vehicle.warranty_expiry else None
        },
        "health": {
            "overall_score": round(overall_health, 1),
            "overall_status": overall_status,
            "critical_components": critical_count,
            "warning_components": warning_count,
            "healthy_components": len(components) - critical_count - warning_count
        },
        "components": components,
        "telemetry": {
            "timestamp": telemetry.time.isoformat() if telemetry else None,
            "engine_temperature": telemetry.engine_temperature if telemetry else None,
            "coolant_temperature": telemetry.coolant_temperature if telemetry else None,
            "oil_pressure": telemetry.oil_pressure if telemetry else None,
            "battery_voltage": telemetry.battery_voltage if telemetry else None,
            "vibration_level": telemetry.vibration_level if telemetry else None,
            "rpm": telemetry.rpm if telemetry else None,
            "speed": telemetry.speed if telemetry else None,
            "odometer": telemetry.odometer if telemetry else None,
            "fuel_level": telemetry.fuel_level if telemetry else None
        } if telemetry else None,
        "last_updated": datetime.utcnow().isoformat()
    }
