"""
Quick test of ML prediction pipeline
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add parent directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from ml.feature_engineering import TelemetryFeatureExtractor
from ml.anomaly_detection import AnomalyDetectionEnsemble, FailurePredictor

print("="*60)
print("ML Pipeline Test")
print("="*60)

# Step 1: Create sample telemetry data
print("\n1. Creating sample telemetry data...")
data = []
for i in range(50):
    # Simulate a failing vehicle (increasing temperature, decreasing oil pressure)
    deterioration = i / 50
    data.append({
        'time': datetime.now() - timedelta(minutes=(50-i)*5),
        'vehicle_id': 'TEST_001',
        'vin': 'TEST_VIN_001',
        'engine_temperature': 90 + deterioration * 30,  # 90 -> 120°C
        'coolant_temperature': 85 + deterioration * 15,  # 85 -> 100°C
        'oil_pressure': 45 - deterioration * 25,  # 45 -> 20 PSI
        'vibration_level': 0.5 + deterioration * 3,  # 0.5 -> 3.5g
        'rpm': np.random.randint(1000, 3000),
        'speed': np.random.uniform(20, 80),
        'fuel_level': 80 - i * 0.5,
        'battery_voltage': 12.6 - deterioration * 0.5,
        'odometer': 50000 + i * 10
    })

df = pd.DataFrame(data)
print(f"   ✓ Created {len(df)} data points")

# Step 2: Extract features
print("\n2. Extracting features...")
extractor = TelemetryFeatureExtractor(window_size=20)
features = extractor.extract_all_features(df)
print(f"   ✓ Extracted {len(features)} features")
print(f"   Top features:")
for key in list(features.keys())[:5]:
    print(f"     - {key}: {features[key]:.2f}")

# Step 3: Check if model exists
print("\n3. Checking for trained model...")
model_path = Path(backend_dir) / "ml" / "models" / "anomaly_detection"

if model_path.exists() and (model_path / "xgboost.pkl").exists():
    print(f"   ✓ Model found at {model_path}")
    
    # Load and test model
    print("\n4. Loading model...")
    model = AnomalyDetectionEnsemble()
    model.load(model_path)
    print(f"   ✓ Model loaded with {len(model.feature_names)} features")
    
    # Make prediction
    print("\n5. Making prediction...")
    predictor = FailurePredictor(model)
    prediction = predictor.predict_with_explanation(features)
    
    print(f"\n   Prediction Results:")
    print(f"   ==================")
    print(f"   Vehicle ID: {df['vehicle_id'].iloc[0]}")
    print(f"   Severity: {prediction['severity'].upper()}")
    print(f"   Failure Probability: {prediction['failure_probability']:.2%}")
    print(f"   Anomaly Score: {prediction['anomaly_score']:.2%}")
    print(f"   Confidence: {prediction['confidence']:.2%}")
    print(f"   Explanation: {prediction['explanation']}")
    
    if prediction['feature_importance']:
        print(f"\n   Top Contributing Features:")
        for feat, imp in list(prediction['feature_importance'].items())[:5]:
            print(f"     - {feat}: {imp:.4f}")
    
    print("\n" + "="*60)
    print("✓ ML Pipeline Test Completed Successfully!")
    print("="*60)
    
else:
    print(f"   ✗ Model not found at {model_path}")
    print(f"\n   To train the model, run:")
    print(f"     cd ml")
    print(f"     python train_model.py")
    print("\n" + "="*60)
    print("Test incomplete - model needs to be trained first")
    print("="*60)
