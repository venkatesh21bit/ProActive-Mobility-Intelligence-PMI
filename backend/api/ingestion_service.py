"""
Telemetry Ingestion Service
FastAPI service that receives telemetry data and writes to Redis Streams and TimescaleDB
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import logging
import uvicorn
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from config.settings import settings
from data.database import get_db_session, init_db, close_db, AsyncSessionLocal
from data.redis_client import redis_stream_client
from data.models import VehicleTelemetry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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
    
    # Connect to Redis
    await redis_stream_client.connect()
    
    # Create consumer groups
    try:
        await redis_stream_client.create_consumer_group(
            "telemetry-processors",
            settings.redis_stream_name,
            start_id="0"
        )
    except Exception as e:
        logger.warning(f"Could not create consumer group: {e}")
    
    logger.info("Ingestion service ready")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Telemetry Ingestion Service...")
    await redis_stream_client.disconnect()
    await close_db()
    logger.info("Shutdown complete")


# FastAPI app
app = FastAPI(
    title="Telemetry Ingestion Service",
    description="Receives vehicle telemetry and writes to Redis Streams and TimescaleDB",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    """Health check endpoint"""
    try:
        # Check Redis connection
        redis_status = "connected" if redis_stream_client.redis_client else "disconnected"
        
        # Check database connection
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
            db_status = "connected"
        
        return {
            "status": "healthy",
            "redis": redis_status,
            "database": db_status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


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
