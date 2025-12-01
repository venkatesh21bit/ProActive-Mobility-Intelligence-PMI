"""
Data Analysis Agent
ML-powered agent for real-time failure prediction and anomaly detection
"""

import sys
from pathlib import Path
import logging
from typing import Dict, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add parent directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from ml.feature_engineering import TelemetryFeatureExtractor
from ml.anomaly_detection import AnomalyDetectionEnsemble, FailurePredictor
from config.settings import settings
from data.redis_client import redis_stream_client
from sqlalchemy import text
from data.database import AsyncSessionLocal

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataAnalysisAgent:
    """
    Agent responsible for analyzing telemetry data and predicting failures
    """
    
    def __init__(self, model_path: Optional[Path] = None):
        """
        Initialize the data analysis agent
        
        Args:
            model_path: Path to saved model (if None, will look in default location)
        """
        self.feature_extractor = TelemetryFeatureExtractor(window_size=20)
        self.model: Optional[AnomalyDetectionEnsemble] = None
        self.predictor: Optional[FailurePredictor] = None
        
        # Load model
        if model_path is None:
            model_path = Path(backend_dir) / "ml" / "models" / "anomaly_detection"
        
        self.model_path = model_path
        self._load_model()
    
    def _load_model(self):
        """Load the trained model"""
        try:
            if self.model_path.exists():
                logger.info(f"Loading model from {self.model_path}")
                self.model = AnomalyDetectionEnsemble()
                self.model.load(self.model_path)
                self.predictor = FailurePredictor(self.model)
                logger.info("Model loaded successfully")
            else:
                logger.warning(f"Model not found at {self.model_path}. Please train model first.")
                logger.info("Run: python ml/train_model.py")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model = None
            self.predictor = None
    
    async def get_vehicle_telemetry(self, vehicle_id: str, hours: int = 24) -> pd.DataFrame:
        """
        Fetch recent telemetry data for a vehicle from TimescaleDB
        
        Args:
            vehicle_id: Vehicle identifier
            hours: Number of hours of historical data to fetch
            
        Returns:
            DataFrame with telemetry data
        """
        async with AsyncSessionLocal() as db:
            query = text("""
                SELECT 
                    time, vehicle_id, vin, engine_temperature, coolant_temperature,
                    oil_pressure, vibration_level, rpm, speed, fuel_level,
                    battery_voltage, odometer, latitude, longitude
                FROM vehicle_telemetry
                WHERE vehicle_id = :vehicle_id
                    AND time >= NOW() - INTERVAL ':hours hours'
                ORDER BY time ASC
            """)
            
            result = await db.execute(query, {"vehicle_id": vehicle_id, "hours": hours})
            rows = result.fetchall()
            
            if not rows:
                logger.warning(f"No telemetry data found for vehicle {vehicle_id}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            columns = ['time', 'vehicle_id', 'vin', 'engine_temperature', 'coolant_temperature',
                      'oil_pressure', 'vibration_level', 'rpm', 'speed', 'fuel_level',
                      'battery_voltage', 'odometer', 'latitude', 'longitude']
            
            df = pd.DataFrame(rows, columns=columns)
            return df
    
    def analyze_vehicle(self, telemetry_df: pd.DataFrame) -> Dict:
        """
        Analyze vehicle telemetry and predict failures
        
        Args:
            telemetry_df: DataFrame with vehicle telemetry
            
        Returns:
            Prediction dictionary
        """
        if self.predictor is None or self.model is None:
            logger.error("Model not loaded. Cannot make predictions.")
            return {
                'error': 'Model not available',
                'severity': 'unknown',
                'failure_probability': 0.0
            }
        
        if telemetry_df.empty:
            logger.warning("Empty telemetry data provided")
            return {
                'error': 'No data available',
                'severity': 'unknown',
                'failure_probability': 0.0
            }
        
        # Extract features
        features = self.feature_extractor.extract_all_features(telemetry_df)
        
        # Make prediction
        prediction = self.predictor.predict_with_explanation(features)
        
        # Add vehicle info
        prediction['vehicle_id'] = telemetry_df['vehicle_id'].iloc[0]
        prediction['vin'] = telemetry_df['vin'].iloc[0]
        prediction['timestamp'] = datetime.utcnow().isoformat()
        prediction['data_points_analyzed'] = len(telemetry_df)
        
        return prediction
    
    async def publish_alert(self, prediction: Dict):
        """
        Publish prediction alert to Redis Stream
        
        Args:
            prediction: Prediction dictionary
        """
        # Only publish if severity is medium or higher
        if prediction.get('severity') in ['medium', 'high', 'critical']:
            alert_data = {
                'vehicle_id': prediction['vehicle_id'],
                'vin': prediction['vin'],
                'timestamp': prediction['timestamp'],
                'severity': prediction['severity'],
                'failure_probability': prediction['failure_probability'],
                'ensemble_score': prediction['ensemble_score'],
                'explanation': prediction['explanation'],
                'confidence': prediction['confidence']
            }
            
            try:
                await redis_stream_client.add_to_stream(
                    alert_data,
                    stream_name=settings.alerts_stream_name
                )
                logger.info(f"Alert published for vehicle {prediction['vehicle_id']} - Severity: {prediction['severity']}")
            except Exception as e:
                logger.error(f"Failed to publish alert: {e}")
    
    async def analyze_and_alert(self, vehicle_id: str, hours: int = 24) -> Dict:
        """
        Complete analysis pipeline: fetch data, analyze, and publish alert
        
        Args:
            vehicle_id: Vehicle identifier
            hours: Hours of historical data to analyze
            
        Returns:
            Prediction dictionary
        """
        logger.info(f"Analyzing vehicle {vehicle_id}")
        
        # Fetch telemetry
        telemetry_df = await self.get_vehicle_telemetry(vehicle_id, hours=hours)
        
        # Analyze
        prediction = self.analyze_vehicle(telemetry_df)
        
        # Publish alert if needed
        if 'error' not in prediction:
            await self.publish_alert(prediction)
        
        return prediction
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model"""
        if self.model is None:
            return {
                'status': 'not_loaded',
                'message': 'Model not available. Train the model first.'
            }
        
        feature_importance = self.model.get_feature_importance(top_n=10)
        
        return {
            'status': 'loaded',
            'model_path': str(self.model_path),
            'num_features': len(self.model.feature_names),
            'feature_names': self.model.feature_names[:20],  # First 20
            'top_features': list(feature_importance.keys()),
            'is_fitted': self.model.is_fitted
        }


# Singleton instance
_agent_instance: Optional[DataAnalysisAgent] = None


def get_data_analysis_agent() -> DataAnalysisAgent:
    """Get or create the data analysis agent singleton"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = DataAnalysisAgent()
    return _agent_instance
