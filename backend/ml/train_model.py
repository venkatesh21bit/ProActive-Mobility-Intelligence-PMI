"""
Model Training and Synthetic Data Generation
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path
import logging

# Add parent directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

# Setup logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from ml.feature_engineering import TelemetryFeatureExtractor
from ml.anomaly_detection import AnomalyDetectionEnsemble

# Try to import MLflow, but continue without it if not available
try:
    import mlflow
    import mlflow.sklearn
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    logger.warning("MLflow not available - training will continue without experiment tracking")

try:
    from config.settings import settings
except Exception as e:
    # Fallback if settings can't be loaded
    class FallbackSettings:
        mlflow_tracking_uri = "http://localhost:5000"
    settings = FallbackSettings()


class SyntheticDataGenerator:
    """Generate synthetic vehicle telemetry data for training"""
    
    def __init__(self, num_vehicles: int = 100, days: int = 30):
        self.num_vehicles = num_vehicles
        self.days = days
        
    def generate_normal_telemetry(self, vehicle_id: str, num_points: int = 100) -> pd.DataFrame:
        """Generate normal operating telemetry"""
        data = []
        base_time = datetime.now() - timedelta(days=self.days)
        
        for i in range(num_points):
            timestamp = base_time + timedelta(minutes=i * 5)
            
            data.append({
                'time': timestamp,
                'vehicle_id': vehicle_id,
                'vin': f'VIN{vehicle_id}',
                'engine_temperature': np.random.normal(90, 5),
                'coolant_temperature': np.random.normal(85, 3),
                'oil_pressure': np.random.normal(45, 5),
                'vibration_level': np.random.normal(0.5, 0.2),
                'rpm': np.random.randint(800, 2500),
                'speed': np.random.uniform(0, 100),
                'fuel_level': max(5, 95 - i * 0.5),
                'battery_voltage': np.random.normal(12.6, 0.2),
                'odometer': 50000 + i * 10
            })
        
        return pd.DataFrame(data)
    
    def generate_failing_telemetry(self, vehicle_id: str, num_points: int = 100, failure_type: str = 'engine') -> pd.DataFrame:
        """Generate telemetry showing gradual failure"""
        data = []
        base_time = datetime.now() - timedelta(days=self.days)
        
        for i in range(num_points):
            timestamp = base_time + timedelta(minutes=i * 5)
            
            # Progressive deterioration
            deterioration = i / num_points
            
            if failure_type == 'engine':
                engine_temp = np.random.normal(90 + deterioration * 30, 5)
                coolant_temp = np.random.normal(85 + deterioration * 20, 3)
                oil_pressure = np.random.normal(45 - deterioration * 20, 5)
                vibration = np.random.normal(0.5 + deterioration * 3, 0.3)
            elif failure_type == 'oil':
                engine_temp = np.random.normal(90, 5)
                coolant_temp = np.random.normal(85, 3)
                oil_pressure = np.random.normal(45 - deterioration * 30, 5)
                vibration = np.random.normal(0.5 + deterioration * 2, 0.3)
            elif failure_type == 'vibration':
                engine_temp = np.random.normal(90, 5)
                coolant_temp = np.random.normal(85, 3)
                oil_pressure = np.random.normal(45, 5)
                vibration = np.random.normal(0.5 + deterioration * 4, 0.5)
            else:  # battery
                engine_temp = np.random.normal(90, 5)
                coolant_temp = np.random.normal(85, 3)
                oil_pressure = np.random.normal(45, 5)
                vibration = np.random.normal(0.5, 0.2)
            
            data.append({
                'time': timestamp,
                'vehicle_id': vehicle_id,
                'vin': f'VIN{vehicle_id}',
                'engine_temperature': engine_temp,
                'coolant_temperature': coolant_temp,
                'oil_pressure': max(10, oil_pressure),
                'vibration_level': vibration,
                'rpm': np.random.randint(800, 3500),
                'speed': np.random.uniform(0, 100),
                'fuel_level': max(5, 95 - i * 0.5),
                'battery_voltage': np.random.normal(12.6 - deterioration * 1.0, 0.2) if failure_type == 'battery' else np.random.normal(12.6, 0.2),
                'odometer': 50000 + i * 10
            })
        
        return pd.DataFrame(data)
    
    def generate_dataset(self) -> tuple[pd.DataFrame, np.ndarray]:
        """
        Generate complete dataset with normal and failing vehicles
        
        Returns:
            Tuple of (telemetry_df, labels)
        """
        all_data = []
        labels = []
        
        # 70% normal vehicles
        num_normal = int(self.num_vehicles * 0.7)
        for i in range(num_normal):
            df = self.generate_normal_telemetry(f'NORMAL_{i:03d}', num_points=100)
            all_data.append(df)
            labels.append(0)  # Normal
        
        # 30% failing vehicles
        failure_types = ['engine', 'oil', 'vibration', 'battery']
        num_failing = self.num_vehicles - num_normal
        
        for i in range(num_failing):
            failure_type = failure_types[i % len(failure_types)]
            df = self.generate_failing_telemetry(f'FAILING_{i:03d}', num_points=100, failure_type=failure_type)
            all_data.append(df)
            labels.append(1)  # Failing
        
        return pd.concat(all_data, ignore_index=True), np.array(labels)


def train_model(experiment_name: str = "vehicle_failure_prediction", use_mlflow: bool = True):
    """Train the anomaly detection model with optional MLflow tracking"""
    
    logger.info("Starting model training...")
    
    # Set MLflow tracking URI if available
    mlflow_enabled = False
    if MLFLOW_AVAILABLE and use_mlflow:
        try:
            # Test connection first with a quick timeout
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)  # 1 second timeout
            result = sock.connect_ex(('localhost', 5000))
            sock.close()
            
            if result == 0:
                # MLflow server is running
                mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
                mlflow.set_experiment(experiment_name)
                mlflow.start_run()
                mlflow_enabled = True
                logger.info(f"✓ MLflow tracking enabled at {settings.mlflow_tracking_uri}")
            else:
                logger.warning("⚠ MLflow server not running on localhost:5000")
                logger.info("→ Continuing training without MLflow tracking...")
                logger.info("→ To enable MLflow: run 'start_mlflow.bat' in a separate terminal")
        except Exception as e:
            logger.warning(f"⚠ MLflow connection failed: {e}")
            logger.info("→ Continuing training without MLflow tracking...")
            mlflow_enabled = False
    elif not use_mlflow:
        logger.info("MLflow tracking disabled (use_mlflow=False)")
    else:
        logger.info("MLflow package not installed - training without experiment tracking")
    
    try:
        # Log parameters
        if mlflow_enabled:
            mlflow.log_param("num_vehicles", 100)
            mlflow.log_param("training_days", 30)
            mlflow.log_param("contamination", 0.1)
        
        # Generate synthetic data
        logger.info("Generating synthetic training data...")
        generator = SyntheticDataGenerator(num_vehicles=100, days=30)
        telemetry_df, labels = generator.generate_dataset()
        
        logger.info(f"Total samples: {len(telemetry_df)}")
        logger.info(f"Normal samples: {np.sum(labels == 0)}")
        logger.info(f"Failing samples: {np.sum(labels == 1)}")
        
        if mlflow_enabled:
            mlflow.log_metric("total_samples", len(telemetry_df))
            mlflow.log_metric("normal_samples", np.sum(labels == 0))
            mlflow.log_metric("failing_samples", np.sum(labels == 1))
        
        # Extract features for each vehicle
        logger.info("Extracting features...")
        extractor = TelemetryFeatureExtractor(window_size=20)
        
        features_list = []
        vehicle_labels = []
        
        for vehicle_id, label in zip(telemetry_df['vehicle_id'].unique(), labels):
            vehicle_data = telemetry_df[telemetry_df['vehicle_id'] == vehicle_id].copy()
            vehicle_data = vehicle_data.sort_values('time')
            
            features = extractor.extract_all_features(vehicle_data)
            features_list.append(features)
            vehicle_labels.append(label)
        
        # Convert to DataFrame for easier handling
        features_df = pd.DataFrame(features_list)
        feature_names = list(features_df.columns)
        X = features_df.values
        y = np.array(vehicle_labels)
        
        logger.info(f"Extracted {X.shape[1]} features from {X.shape[0]} vehicles")
        
        if mlflow_enabled:
            mlflow.log_param("num_features", X.shape[1])
        
        # Train model
        logger.info("Training anomaly detection ensemble...")
        model = AnomalyDetectionEnsemble(
            isolation_forest_contamination=0.1,
            xgb_params={'n_estimators': 100, 'max_depth': 6}
        )
        
        model.fit(X, y, feature_names=feature_names)
        
        # Evaluate model
        logger.info("Evaluating model...")
        ensemble_scores, anomaly_scores, failure_probs = model.predict(X)
        
        # Calculate metrics
        from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score
        
        predictions = (ensemble_scores > 0.5).astype(int)
        
        auc = roc_auc_score(y, ensemble_scores)
        precision = precision_score(y, predictions)
        recall = recall_score(y, predictions)
        f1 = f1_score(y, predictions)
        
        logger.info(f"AUC: {auc:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")
        
        # Log metrics
        if mlflow_enabled:
            mlflow.log_metric("auc", auc)
            mlflow.log_metric("precision", precision)
            mlflow.log_metric("recall", recall)
            mlflow.log_metric("f1_score", f1)
        
        # Save model
        model_dir = Path(backend_dir) / "ml" / "models" / "anomaly_detection"
        model.save(model_dir)
        logger.info(f"Model saved to {model_dir}")
        
        # Log model to MLflow
        if mlflow_enabled:
            try:
                mlflow.sklearn.log_model(model.xgboost, "xgboost_model")
                mlflow.sklearn.log_model(model.isolation_forest, "isolation_forest_model")
                logger.info("Models logged to MLflow")
            except Exception as e:
                logger.warning(f"Could not log models to MLflow: {e}")
        
        # Log feature importance
        feature_importance = model.get_feature_importance(top_n=20)
        importance_df = pd.DataFrame([
            {'feature': k, 'importance': v} 
            for k, v in feature_importance.items()
        ])
        
        if mlflow_enabled:
            try:
                mlflow.log_text(importance_df.to_string(), "feature_importance.txt")
            except Exception as e:
                logger.warning(f"Could not log feature importance to MLflow: {e}")
        
        # Save feature importance locally
        importance_file = model_dir / "feature_importance.txt"
        with open(importance_file, 'w') as f:
            f.write(importance_df.to_string())
        logger.info(f"Feature importance saved to {importance_file}")
        
        if mlflow_enabled:
            logger.info(f"MLflow run ID: {mlflow.active_run().info.run_id}")
        
        return model, feature_names
    
    finally:
        # End MLflow run if it was started
        if mlflow_enabled and MLFLOW_AVAILABLE:
            try:
                mlflow.end_run()
            except Exception:
                pass


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Train vehicle failure prediction model')
    parser.add_argument('--no-mlflow', action='store_true', help='Disable MLflow tracking')
    args = parser.parse_args()
    
    # Train the model
    model, feature_names = train_model(use_mlflow=not args.no_mlflow)
    
    logger.info("=" * 60)
    logger.info("✓ Training completed successfully!")
    logger.info("=" * 60)
    logger.info(f"Feature count: {len(feature_names)}")
    logger.info(f"Top 5 features: {list(model.get_feature_importance(top_n=5).keys())}")
    logger.info(f"Model saved to: ml/models/anomaly_detection/")
    logger.info("=" * 60)
    logger.info("\nNext steps:")
    logger.info("  1. Test the model: python test_ml_pipeline.py")
    logger.info("  2. Start ML service: python api/ml_service.py")
    logger.info("  3. Start agents: python -m agents")
    logger.info("=" * 60)
