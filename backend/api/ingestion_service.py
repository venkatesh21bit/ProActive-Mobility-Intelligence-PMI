"""
Telemetry Ingestion Service
FastAPI service that receives telemetry data and writes to Redis Streams and TimescaleDB
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
import logging
import uvicorn
from contextlib import asynccontextmanager
import os
import time

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from config.settings import settings
from data.database import get_db_session, init_db, close_db, AsyncSessionLocal
from data.redis_client import redis_stream_client
from data.models import VehicleTelemetry
from api.dashboard import router as dashboard_router
from api.notifications import router as notifications_router
from api.appointments import router as appointments_router
from api.analytics import router as analytics_router
from api.agent_workflow import router as agent_workflow_router
from api.vehicles_detail import router as vehicles_detail_router
from api.auth import router as auth_router
from api.booking import router as booking_router
from api.migration import router as migration_router
from api.demo_user import router as demo_user_router
from api.fixes import router as fixes_router
from middleware import (
    RateLimitMiddleware,
    RequestIDMiddleware,
    ErrorHandlerMiddleware,
    http_exception_handler
)

# Determine environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT == "production"

# Configure logging
log_level = logging.INFO if IS_PRODUCTION else logging.DEBUG
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s' if not IS_PRODUCTION else '{"timestamp": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
)
logger = logging.getLogger(__name__)


# Pydantic models for API
class TelemetryInput(BaseModel):
    """Input model for telemetry data"""
    vehicle_id: str
    vin: str
    engine_temperature: float
    coolant_temperature: float
    oil_pressure: float
    vibration_level: float
    rpm: int
    speed: float
    fuel_level: float
    battery_voltage: float
    odometer: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    metadata: Optional[dict] = None


class TelemetryBatchInput(BaseModel):
    """Batch input for multiple telemetry records"""
    telemetry: List[TelemetryInput]


class IngestionResponse(BaseModel):
    """Response model for ingestion"""
    status: str
    message: str
    count: int
    redis_message_ids: List[str] = []
    timestamp: datetime


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for FastAPI app"""
    # Startup
    logger.info("Starting Telemetry Ingestion Service...")
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(f"Database initialization failed (non-critical): {e}")
    
    # Connect to Redis (optional)
    try:
        await redis_stream_client.connect()
        logger.info("Redis connected successfully")
        
        # Create consumer groups
        try:
            await redis_stream_client.create_consumer_group(
                "telemetry-processors",
                settings.redis_stream_name,
                start_id="0"
            )
        except Exception as e:
            logger.warning(f"Consumer group may already exist: {e}")
    except Exception as e:
        logger.warning(f"Redis connection failed (will retry on demand): {e}")
    
    logger.info("Ingestion service ready")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Telemetry Ingestion Service...")
    try:
        await redis_stream_client.disconnect()
    except:
        pass
    await close_db()
    logger.info("Shutdown complete")


# FastAPI app
app = FastAPI(
    title="ProActive Mobility Intelligence - API",
    description="Production-grade automotive predictive maintenance platform",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs" if not IS_PRODUCTION else None,
    redoc_url="/redoc" if not IS_PRODUCTION else None,
    openapi_url="/openapi.json" if not IS_PRODUCTION else None,
)

# Add custom exception handler
app.add_exception_handler(Exception, http_exception_handler)

# Add middleware (order matters - first added is last executed)
# 1. Error Handler (outermost layer)
app.add_middleware(ErrorHandlerMiddleware)

# 2. Request ID (for tracing)
app.add_middleware(RequestIDMiddleware)

# 3. Rate Limiting (configurable per environment)
rate_limit = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))
app.add_middleware(RateLimitMiddleware, requests_per_minute=rate_limit, burst_size=rate_limit * 2)

# 4. GZip Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 5. Security Middleware - Trusted Host
if IS_PRODUCTION:
    allowed_hosts = os.getenv("ALLOWED_HOSTS", "*").split(",")
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=allowed_hosts
    )

# CORS Configuration
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "https://pmi-1234.web.app",
    "https://pmi-1234.firebaseapp.com",
]

# Allow additional origins from environment variable in production
if IS_PRODUCTION:
    production_origins = os.getenv("CORS_ORIGINS", "")
    if production_origins:
        additional_origins = [origin.strip() for origin in production_origins.split(",") if origin.strip()]
        allowed_origins.extend(additional_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    max_age=3600,
)

# GZip compression for responses
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error" if IS_PRODUCTION else str(exc)}
    )


# Include routers
app.include_router(auth_router)
app.include_router(booking_router)
app.include_router(dashboard_router)
app.include_router(notifications_router)
app.include_router(appointments_router)
app.include_router(analytics_router)
app.include_router(agent_workflow_router)
app.include_router(vehicles_detail_router)
app.include_router(migration_router)
app.include_router(demo_user_router)
app.include_router(fixes_router)


async def write_to_timescaledb(telemetry_data: TelemetryInput, db: AsyncSession):
    """Write telemetry data to TimescaleDB"""
    try:
        query = text("""
            INSERT INTO vehicle_telemetry (
                time, vehicle_id, vin, engine_temperature, coolant_temperature,
                oil_pressure, vibration_level, rpm, speed, fuel_level,
                battery_voltage, odometer, latitude, longitude, metadata
            ) VALUES (
                NOW(), :vehicle_id, :vin, :engine_temperature, :coolant_temperature,
                :oil_pressure, :vibration_level, :rpm, :speed, :fuel_level,
                :battery_voltage, :odometer, :latitude, :longitude, :metadata
            )
        """)
        
        await db.execute(query, {
            "vehicle_id": telemetry_data.vehicle_id,
            "vin": telemetry_data.vin,
            "engine_temperature": telemetry_data.engine_temperature,
            "coolant_temperature": telemetry_data.coolant_temperature,
            "oil_pressure": telemetry_data.oil_pressure,
            "vibration_level": telemetry_data.vibration_level,
            "rpm": telemetry_data.rpm,
            "speed": telemetry_data.speed,
            "fuel_level": telemetry_data.fuel_level,
            "battery_voltage": telemetry_data.battery_voltage,
            "odometer": telemetry_data.odometer,
            "latitude": telemetry_data.latitude,
            "longitude": telemetry_data.longitude,
            "metadata": telemetry_data.metadata
        })
        await db.commit()
        
    except Exception as e:
        logger.error(f"Error writing to TimescaleDB: {e}")
        await db.rollback()
        raise


async def write_to_redis_stream(telemetry_data: TelemetryInput) -> str:
    """Write telemetry data to Redis Stream"""
    try:
        data = {
            "vehicle_id": telemetry_data.vehicle_id,
            "vin": telemetry_data.vin,
            "engine_temperature": telemetry_data.engine_temperature,
            "coolant_temperature": telemetry_data.coolant_temperature,
            "oil_pressure": telemetry_data.oil_pressure,
            "vibration_level": telemetry_data.vibration_level,
            "rpm": telemetry_data.rpm,
            "speed": telemetry_data.speed,
            "fuel_level": telemetry_data.fuel_level,
            "battery_voltage": telemetry_data.battery_voltage,
            "odometer": telemetry_data.odometer,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if telemetry_data.latitude:
            data["latitude"] = telemetry_data.latitude
        if telemetry_data.longitude:
            data["longitude"] = telemetry_data.longitude
        if telemetry_data.metadata:
            data["metadata"] = telemetry_data.metadata
        
        message_id = await redis_stream_client.add_to_stream(data)
        return message_id
        
    except Exception as e:
        logger.error(f"Error writing to Redis Stream: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Telemetry Ingestion Service",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "ingest_single": "/ingest (POST)",
            "ingest_batch": "/ingest/batch (POST)",
            "stream_info": "/stream/info",
        }
    }


@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint for production monitoring"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": ENVIRONMENT,
            "version": "1.0.0",
            "checks": {}
        }
        
        # Check Redis connection
        try:
            if redis_stream_client.redis_client:
                await redis_stream_client.redis_client.ping()
                health_status["checks"]["redis"] = "healthy"
            else:
                health_status["checks"]["redis"] = "disconnected"
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
            health_status["status"] = "degraded"
        
        # Check database connection
        try:
            async with AsyncSessionLocal() as db:
                await db.execute(text("SELECT 1"))
                health_status["checks"]["database"] = "healthy"
        except Exception as e:
            health_status["checks"]["database"] = f"unhealthy: {str(e)}"
            health_status["status"] = "unhealthy"
        
        # Return appropriate status code
        if health_status["status"] == "unhealthy":
            return JSONResponse(status_code=503, content=health_status)
        elif health_status["status"] == "degraded":
            return JSONResponse(status_code=200, content=health_status)
        
        return health_status
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e) if not IS_PRODUCTION else "Health check failed",
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@app.get("/readiness")
async def readiness_check():
    """Kubernetes readiness probe - checks if service can handle traffic"""
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        
        if not redis_stream_client.redis_client:
            raise Exception("Redis not connected")
            
        return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "not ready", "error": str(e) if not IS_PRODUCTION else "Not ready"}
        )


@app.get("/liveness")
async def liveness_check():
    """Kubernetes liveness probe - checks if service is alive"""
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}


@app.post("/ingest", response_model=IngestionResponse)
async def ingest_telemetry(
    telemetry: TelemetryInput,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Ingest single telemetry record
    Writes to both Redis Streams (for real-time processing) and TimescaleDB (for storage)
    """
    try:
        # Write to Redis Stream (fast, non-blocking)
        message_id = await write_to_redis_stream(telemetry)
        
        # Write to TimescaleDB in background
        background_tasks.add_task(write_to_timescaledb, telemetry, db)
        
        return IngestionResponse(
            status="success",
            message="Telemetry ingested successfully",
            count=1,
            redis_message_ids=[message_id],
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error ingesting telemetry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest/batch", response_model=IngestionResponse)
async def ingest_telemetry_batch(
    batch: TelemetryBatchInput,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Ingest batch of telemetry records
    Optimized for bulk ingestion from simulator
    """
    try:
        message_ids = []
        
        # Write all to Redis Stream
        for telemetry in batch.telemetry:
            message_id = await write_to_redis_stream(telemetry)
            message_ids.append(message_id)
            
            # Queue database write
            background_tasks.add_task(write_to_timescaledb, telemetry, db)
        
        return IngestionResponse(
            status="success",
            message=f"Batch of {len(batch.telemetry)} records ingested",
            count=len(batch.telemetry),
            redis_message_ids=message_ids,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error ingesting batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stream/info")
async def get_stream_info():
    """Get information about the telemetry stream"""
    try:
        info = await redis_stream_client.get_stream_info()
        return {
            "stream_name": settings.redis_stream_name,
            "info": info,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting stream info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_ingestion_stats(db: AsyncSession = Depends(get_db_session)):
    """Get ingestion statistics"""
    try:
        # Get count from TimescaleDB
        result = await db.execute(text("""
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT vehicle_id) as unique_vehicles,
                MAX(time) as latest_timestamp
            FROM vehicle_telemetry
        """))
        row = result.fetchone()
        
        return {
            "total_records": row[0] if row else 0,
            "unique_vehicles": row[1] if row else 0,
            "latest_timestamp": row[2].isoformat() if row and row[2] else None,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/seed")
async def seed_database():
    """Seed database with Hero MotoCorp sample data with varied scenarios"""
    from data.models import Vehicle, VehicleTelemetry, FailurePrediction, Customer, ServiceCenter, Appointment, MaintenanceRecord
    from sqlalchemy import select
    import random
    
    try:
        async with AsyncSessionLocal() as db:
            # Check if already seeded
            result = await db.execute(select(Vehicle).limit(1))
            if result.scalar_one_or_none():
                return {"message": "Database already seeded", "vehicles": 0}
            
            # Create multiple customers
            customers = [
                Customer(first_name="Rajesh", last_name="Kumar", email="rajesh@heromotocorp.com", phone="+919876543210", address="Mumbai, Maharashtra"),
                Customer(first_name="Priya", last_name="Sharma", email="priya@heromotocorp.com", phone="+919876543211", address="Delhi, NCR"),
                Customer(first_name="Amit", last_name="Patel", email="amit@heromotocorp.com", phone="+919876543212", address="Bangalore, Karnataka"),
                Customer(first_name="Sneha", last_name="Reddy", email="sneha@heromotocorp.com", phone="+919876543213", address="Hyderabad, Telangana"),
                Customer(first_name="Vijay", last_name="Singh", email="vijay@heromotocorp.com", phone="+919876543214", address="Pune, Maharashtra"),
            ]
            for customer in customers:
                db.add(customer)
            
            # Create multiple service centers
            service_centers = [
                ServiceCenter(name="Hero Service Center - South Delhi", address="Greater Kailash", city="Delhi", state="Delhi", zip_code="110048", phone="+911123456789", capacity=15),
                ServiceCenter(name="Hero Service Center - Bangalore", address="Koramangala", city="Bangalore", state="Karnataka", zip_code="560034", phone="+918012345678", capacity=20),
                ServiceCenter(name="Hero Service Center - Mumbai", address="Bandra West", city="Mumbai", state="Maharashtra", zip_code="400050", phone="+912223456789", capacity=18),
            ]
            for sc in service_centers:
                db.add(sc)
            
            await db.commit()
            for customer in customers:
                await db.refresh(customer)
            for sc in service_centers:
                await db.refresh(sc)
            
            # Hero MotoCorp models with realistic distribution
            hero_models = [
                ('Splendor Plus', 0.25), ('HF Deluxe', 0.20), ('Passion Pro', 0.15),
                ('Glamour', 0.10), ('Super Splendor', 0.08), ('Xtreme 160R', 0.08),
                ('Xpulse 200', 0.05), ('Maestro Edge', 0.04), ('Pleasure Plus', 0.03), ('Destini 125', 0.02)
            ]
            
            vehicles = []
            
            for i in range(50):
                # Weighted random model selection
                model = random.choices([m[0] for m in hero_models], weights=[m[1] for m in hero_models])[0]
                year = random.choices([2020, 2021, 2022, 2023, 2024], weights=[0.1, 0.15, 0.25, 0.3, 0.2])[0]
                mileage = random.randint(2000, 80000) if year < 2024 else random.randint(500, 15000)
                customer = random.choice(customers)
                
                vehicle = Vehicle(
                    vin=f"HERO{year}{chr(65+i%26)}{str(i).zfill(7)}",
                    make="Hero MotoCorp",
                    model=model,
                    year=year,
                    mileage=mileage,
                    purchase_date=datetime.utcnow() - timedelta(days=random.randint(30, 1825)),
                    warranty_expiry=datetime.utcnow() + timedelta(days=random.randint(-180, 730)),
                    customer_id=customer.customer_id
                )
                vehicles.append(vehicle)
                db.add(vehicle)
            
            await db.commit()
            
            # Add diverse telemetry data
            for vehicle in vehicles:
                telemetry_days = min(30, int(vehicle.mileage / 1000))  # More history for higher mileage
                for days_ago in range(telemetry_days):
                    # Simulate realistic sensor readings based on vehicle age/mileage
                    age_factor = (datetime.utcnow().year - vehicle.year) / 5
                    mileage_factor = vehicle.mileage / 100000
                    wear = min(age_factor + mileage_factor, 0.5)
                    
                    telemetry = VehicleTelemetry(
                        vehicle_id=vehicle.vin,
                        vin=vehicle.vin,
                        time=datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0, 23)),
                        engine_temperature=random.uniform(75 + wear*20, 105 + wear*15),
                        coolant_temperature=random.uniform(65 + wear*15, 95 + wear*10),
                        oil_pressure=random.uniform(25 - wear*10, 55 - wear*5),
                        vibration_level=random.uniform(1 + wear*5, 8 + wear*4),
                        rpm=random.randint(900, 7500),
                        speed=random.uniform(0, 110),
                        fuel_level=random.uniform(15, 95),
                        battery_voltage=random.uniform(12.0 - wear*0.5, 13.2 - wear*0.3),
                        odometer=vehicle.mileage + random.randint(0, 200),
                        latitude=random.uniform(12.0, 28.0) if random.random() > 0.3 else None,
                        longitude=random.uniform(72.0, 88.0) if random.random() > 0.3 else None
                    )
                    db.add(telemetry)
            
            await db.commit()
            
            # Add varied failure predictions with different severities
            components = ['Engine', 'Brakes', 'Transmission', 'Battery', 'Cooling System', 'Oil System', 'Suspension', 'Tires', 'Exhaust', 'Fuel System']
            
            for vehicle in vehicles:
                num_predictions = random.choices([0, 1, 2, 3], weights=[0.3, 0.4, 0.2, 0.1])[0]
                
                for _ in range(num_predictions):
                    age_factor = (datetime.utcnow().year - vehicle.year) / 5
                    mileage_factor = vehicle.mileage / 100000
                    base_prob = min(0.15 + age_factor * 0.3 + mileage_factor * 0.3, 0.85)
                    
                    failure_prob = random.uniform(base_prob - 0.1, base_prob + 0.15)
                    failure_prob = max(0.1, min(0.95, failure_prob))
                    
                    if failure_prob >= 0.7:
                        severity = 'Critical'
                        days_until = random.randint(5, 20)
                    elif failure_prob >= 0.5:
                        severity = 'High'
                        days_until = random.randint(20, 45)
                    elif failure_prob >= 0.3:
                        severity = 'Medium'
                        days_until = random.randint(45, 90)
                    else:
                        severity = 'Low'
                        days_until = random.randint(90, 180)
                    
                    prediction = FailurePrediction(
                        vehicle_id=vehicle.vehicle_id,
                        vin=vehicle.vin,
                        prediction_time=datetime.utcnow() - timedelta(days=random.randint(0, 7)),
                        predicted_component=random.choice(components),
                        failure_probability=failure_prob,
                        severity=severity,
                        estimated_days_to_failure=days_until,
                        confidence_score=random.uniform(0.75, 0.95),
                        model_version="v2.1.0"
                    )
                    db.add(prediction)
            
            await db.commit()
            
            # Add appointments for some vehicles
            appointment_types = ['Routine Maintenance', 'Repair', 'Inspection', 'Warranty Service', 'Emergency Repair']
            appointment_statuses = ['scheduled', 'confirmed', 'in_progress', 'completed']
            
            for i in range(25):  # Create 25 appointments
                vehicle = random.choice(vehicles)
                service_center = random.choice(service_centers)
                apt_type = random.choice(appointment_types)
                status = random.choices(appointment_statuses, weights=[0.3, 0.3, 0.2, 0.2])[0]
                
                scheduled_time = datetime.utcnow() + timedelta(days=random.randint(-7, 30), hours=random.randint(8, 17))
                
                appointment = Appointment(
                    vehicle_id=vehicle.vehicle_id,
                    customer_id=vehicle.customer_id,
                    center_id=service_center.center_id,
                    scheduled_time=scheduled_time,
                    appointment_type=apt_type,
                    status=status,
                    estimated_duration_minutes=random.choice([60, 90, 120, 180]),
                    customer_consent=status in ['confirmed', 'in_progress', 'completed']
                )
                db.add(appointment)
            
            await db.commit()
            
            # Add maintenance records for completed appointments
            maintenance_services = ['Oil Change', 'Brake Service', 'Tire Rotation', 'Battery Replacement', 'Engine Tune-up', 'Transmission Service']
            
            for i in range(15):  # Create 15 maintenance records
                vehicle = random.choice(vehicles)
                
                maintenance = MaintenanceRecord(
                    vehicle_id=vehicle.vehicle_id,
                    service_date=datetime.utcnow() - timedelta(days=random.randint(1, 180)),
                    service_type=random.choice(maintenance_services),
                    labor_hours=random.uniform(1.0, 4.5),
                    parts_cost=random.uniform(500, 5000),
                    labor_cost=random.uniform(300, 2000),
                    total_cost=random.uniform(800, 7000),
                    technician_notes=f"Service completed successfully. {random.choice(['Minor', 'Moderate', 'Significant'])} wear detected.",
                    feedback_rating=random.randint(3, 5)
                )
                db.add(maintenance)
            
            await db.commit()
            
            return {
                "message": "Database seeded successfully with varied scenarios",
                "vehicles": 50,
                "customers": 5,
                "service_centers": 3,
                "appointments": 25,
                "maintenance_records": 15
            }
            
    except Exception as e:
        logger.error(f"Seed error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/seed-predictions")
async def seed_predictions():
    """Add failure predictions for existing vehicles"""
    from data.models import Vehicle, FailurePrediction
    from sqlalchemy import select
    import random
    
    try:
        async with AsyncSessionLocal() as db:
            # Get all vehicles
            result = await db.execute(select(Vehicle))
            vehicles = result.scalars().all()
            
            if not vehicles:
                return {"message": "No vehicles found", "predictions": 0}
            
            # Delete existing predictions
            await db.execute(text("DELETE FROM failure_predictions"))
            
            # Add varied failure predictions with more critical ones
            components = ['Engine', 'Brakes', 'Transmission', 'Battery', 'Cooling System', 'Oil System', 'Suspension', 'Tires', 'Exhaust', 'Fuel System']
            predictions_added = 0
            critical_predictions = 0
            
            for vehicle in vehicles:
                # More vehicles get predictions, some get critical ones
                num_predictions = random.choices([0, 1, 2, 3], weights=[0.2, 0.4, 0.25, 0.15])[0]
                
                for _ in range(num_predictions):
                    age_factor = (datetime.utcnow().year - vehicle.year) / 5
                    mileage_factor = vehicle.mileage / 100000
                    base_prob = min(0.15 + age_factor * 0.3 + mileage_factor * 0.3, 0.85)
                    
                    # 20% chance of critical failure for demo purposes
                    if random.random() < 0.2:
                        failure_prob = random.uniform(0.70, 0.92)
                        severity = 'Critical'
                        days_until = random.randint(3, 15)
                        critical_predictions += 1
                    else:
                        failure_prob = random.uniform(base_prob - 0.1, base_prob + 0.15)
                        failure_prob = max(0.1, min(0.68, failure_prob))
                        
                        if failure_prob >= 0.5:
                            severity = 'High'
                            days_until = random.randint(20, 45)
                        elif failure_prob >= 0.3:
                            severity = 'Medium'
                            days_until = random.randint(45, 90)
                        else:
                            severity = 'Low'
                            days_until = random.randint(90, 180)
                    
                    prediction = FailurePrediction(
                        vehicle_id=vehicle.vehicle_id,
                        vin=vehicle.vin,
                        prediction_time=datetime.utcnow() - timedelta(hours=random.randint(0, 23)),
                        predicted_component=random.choice(components),
                        failure_probability=failure_prob,
                        severity=severity,
                        estimated_days_to_failure=days_until,
                        confidence_score=random.uniform(0.75, 0.95),
                        model_version="v2.1.0"
                    )
                    db.add(prediction)
                    predictions_added += 1
            
            await db.commit()
            
            return {
                "message": "Predictions seeded successfully",
                "predictions": predictions_added,
                "critical_predictions": critical_predictions,
                "vehicles": len(vehicles)
            }
            
    except Exception as e:
        logger.error(f"Seed predictions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/seed-notifications")
async def seed_notification_history():
    """Seed notification history for demo purposes"""
    from data.models import NotificationLog, Customer, FailurePrediction
    from sqlalchemy import select
    import random
    
    try:
        async with AsyncSessionLocal() as db:
            # Get customers and predictions
            customers_result = await db.execute(select(Customer))
            customers = customers_result.scalars().all()
            
            predictions_result = await db.execute(select(FailurePrediction))
            predictions = predictions_result.scalars().all()
            
            if not customers or not predictions:
                return {"message": "No customers or predictions found"}
            
            # Delete existing notifications
            await db.execute(text("DELETE FROM notification_logs"))
            
            # Create notification history
            notification_types = ['failure_alert', 'service_reminder', 'appointment_confirmation', 'maintenance_complete']
            channels = ['sms', 'voice', 'email']
            statuses = ['delivered', 'pending', 'failed']
            
            notifications_added = 0
            
            for _ in range(75):  # Create 75 notifications
                customer = random.choice(customers)
                prediction = random.choice(predictions)
                
                notification = NotificationLog(
                    customer_id=customer.customer_id,
                    vehicle_id=prediction.vehicle_id,
                    notification_type=random.choice(notification_types),
                    channel=random.choice(channels),
                    recipient=customer.phone or customer.email,
                    message=f"Alert: {prediction.predicted_component} maintenance required",
                    status=random.choices(statuses, weights=[0.7, 0.2, 0.1])[0],
                    sent_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                    delivered_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)) if random.random() > 0.3 else None,
                    read_at=datetime.utcnow() - timedelta(days=random.randint(0, 25)) if random.random() > 0.5 else None
                )
                db.add(notification)
                notifications_added += 1
            
            await db.commit()
            
            return {
                "message": "Notifications seeded successfully",
                "notifications": notifications_added
            }
            
    except Exception as e:
        logger.error(f"Seed notifications error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "ingestion_service:app",
        host="0.0.0.0",
        port=settings.api_port,
        reload=True,
        log_level="info"
    )
