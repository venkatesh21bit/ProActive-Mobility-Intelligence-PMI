"""
ML Prediction Service
FastAPI service for serving ML predictions
"""

import sys
from pathlib import Path

# Add parent directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import logging
import uvicorn

from agents.data_analysis_agent import get_data_analysis_agent, DataAnalysisAgent
from config.settings import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Pydantic models
class TelemetryData(BaseModel):
    """Telemetry data for prediction"""
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
    timestamp: Optional[str] = None


class TelemetryBatch(BaseModel):
    """Batch of telemetry data"""
    data_points: List[TelemetryData]


class PredictionRequest(BaseModel):
    """Request for vehicle failure prediction"""
    vehicle_id: str
    hours_of_data: int = Field(default=24, ge=1, le=168)  # 1 hour to 7 days


class PredictionResponse(BaseModel):
    """Response with failure prediction"""
    vehicle_id: str
    vin: str
    timestamp: str
    severity: str
    failure_probability: float
    anomaly_score: float
    ensemble_score: float
    confidence: float
    explanation: str
    feature_importance: Dict[str, float]
    data_points_analyzed: int


class ModelInfo(BaseModel):
    """Model information response"""
    status: str
    model_path: Optional[str] = None
    num_features: Optional[int] = None
    top_features: Optional[List[str]] = None
    is_fitted: Optional[bool] = None
    message: Optional[str] = None


# FastAPI app
app = FastAPI(
    title="ML Prediction Service",
    description="Serves ML-based vehicle failure predictions",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting ML Prediction Service...")
    
    # Initialize the agent (loads model)
    agent = get_data_analysis_agent()
    logger.info(f"Data Analysis Agent initialized: {agent.get_model_info()['status']}")


@app.get("/")
async def root():
    """Root endpoint"""
    agent = get_data_analysis_agent()
    model_info = agent.get_model_info()
    
    return {
        "service": "ML Prediction Service",
        "version": "1.0.0",
        "model_status": model_info['status'],
        "endpoints": {
            "predict": "/predict (POST)",
            "model_info": "/model/info (GET)",
            "health": "/health (GET)"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    agent = get_data_analysis_agent()
    model_info = agent.get_model_info()
    
    is_healthy = model_info['status'] == 'loaded'
    
    return {
        "status": "healthy" if is_healthy else "degraded",
        "model_loaded": is_healthy,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/model/info", response_model=ModelInfo)
async def get_model_information():
    """Get information about the loaded model"""
    agent = get_data_analysis_agent()
    info = agent.get_model_info()
    return ModelInfo(**info)


@app.post("/predict", response_model=PredictionResponse)
async def predict_failure(
    request: PredictionRequest,
    background_tasks: BackgroundTasks
):
    """
    Predict vehicle failure based on historical telemetry data
    
    Fetches recent telemetry from database, extracts features, and runs ML prediction.
    Publishes alerts to Redis stream if failure risk is detected.
    """
    logger.info(f"Prediction request for vehicle {request.vehicle_id}")
    
    agent = get_data_analysis_agent()
    
    # Check if model is loaded
    if agent.model is None:
        raise HTTPException(
            status_code=503,
            detail="ML model not available. Please train the model first."
        )
    
    try:
        # Perform analysis
        prediction = await agent.analyze_and_alert(
            vehicle_id=request.vehicle_id,
            hours=request.hours_of_data
        )
        
        # Check for errors
        if 'error' in prediction:
            raise HTTPException(status_code=404, detail=prediction['error'])
        
        return PredictionResponse(**prediction)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/batch")
async def predict_batch(batch: TelemetryBatch):
    """
    Predict failure from provided telemetry batch (without fetching from DB)
    """
    logger.info(f"Batch prediction request with {len(batch.data_points)} data points")
    
    agent = get_data_analysis_agent()
    
    if agent.model is None:
        raise HTTPException(
            status_code=503,
            detail="ML model not available. Please train the model first."
        )
    
    try:
        # Convert to DataFrame
        import pandas as pd
        
        data = [point.dict() for point in batch.data_points]
        df = pd.DataFrame(data)
        
        # Ensure time column
        if 'timestamp' in df.columns:
            df['time'] = pd.to_datetime(df['timestamp'])
        else:
            df['time'] = datetime.utcnow()
        
        # Analyze
        prediction = agent.analyze_vehicle(df)
        
        if 'error' in prediction:
            raise HTTPException(status_code=400, detail=prediction['error'])
        
        return PredictionResponse(**prediction)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch prediction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")


@app.post("/train")
async def trigger_training(background_tasks: BackgroundTasks):
    """
    Trigger model training in background
    (In production, this should be a separate scheduled job)
    """
    def train_model_task():
        """Background task for training"""
        try:
            from ml.train_model import train_model
            logger.info("Starting background model training...")
            model, feature_names = train_model()
            logger.info("Model training completed successfully")
            
            # Reload model in agent
            agent = get_data_analysis_agent()
            agent._load_model()
            
        except Exception as e:
            logger.error(f"Model training failed: {e}", exc_info=True)
    
    background_tasks.add_task(train_model_task)
    
    return {
        "status": "training_started",
        "message": "Model training started in background. Check logs for progress.",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/predictions/recent")
async def get_recent_predictions(limit: int = 10):
    """
    Get recent predictions from database
    (Placeholder - implement based on your storage strategy)
    """
    # TODO: Implement fetching from failure_predictions table
    return {
        "message": "Feature not yet implemented",
        "limit": limit
    }


if __name__ == "__main__":
    uvicorn.run(
        "ml_service:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
