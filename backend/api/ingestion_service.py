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
from datetime import datetime
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
    await init_db()
    
    # Connect to Redis (optional for startup)
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
    await redis_stream_client.disconnect()
    await close_db()
    logger.info("Shutdown complete")


# FastAPI app
app = FastAPI(
    title="ProActive Mobility Intelligence - Telemetry Ingestion",
    description="High-throughput telemetry ingestion service",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if not IS_PRODUCTION else None,
    redoc_url="/redoc" if not IS_PRODUCTION else None,
    openapi_url="/openapi.json" if not IS_PRODUCTION else None,
)

# Security Middleware - Trusted Host
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
]

if IS_PRODUCTION:
    production_origins = os.getenv("CORS_ORIGINS", "").split(",")
    allowed_origins = [origin.strip() for origin in production_origins if origin.strip()]

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
app.include_router(dashboard_router)


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


if __name__ == "__main__":
    uvicorn.run(
        "ingestion_service:app",
        host="0.0.0.0",
        port=settings.api_port,
        reload=True,
        log_level="info"
    )
