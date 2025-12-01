# ML Training Guide

## Quick Start (Recommended - No MLflow)

Train the model without MLflow for fastest results:

```bash
cd backend/ml
python train_model.py --no-mlflow
```

**Or use the batch file:**
```bash
cd backend
train_ml_model.bat
```

This will:
- ✅ Generate 100 vehicles of synthetic data (70% normal, 30% failing)
- ✅ Extract 50+ features per vehicle  
- ✅ Train Isolation Forest + XGBoost ensemble
- ✅ Save model to `ml/models/anomaly_detection/`
- ✅ Save feature importance locally
- ✅ Print metrics: AUC, Precision, Recall, F1
- ✅ **No waiting for MLflow connection retries!**

Expected time: **~30-60 seconds**

## Training With MLflow (For Experiment Tracking)

If you want to track experiments, visualize metrics, and version models:

### Step 1: Upgrade MLflow (If Needed)

If you see `AttributeError: 'EntryPoints' object has no attribute 'get'`:

```bash
pip install --upgrade mlflow==2.15.1
```

### Step 2: Start MLflow Server

**Option A - Using Batch File:**
```bash
cd backend
start_mlflow.bat
```

**Option B - Manual Command:**
```bash
cd backend
mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./ml/mlruns
```

MLflow UI will be at: http://localhost:5000

### Step 3: Train Model

In a **new terminal**:
```bash
cd backend/ml
python train_model.py
# Note: without --no-mlflow flag, it will use MLflow if available
```

**Or use the batch file:**
```bash
cd backend
train_ml_model_with_mlflow.bat
```

Now you'll see:
- ✅ Experiment tracking in MLflow UI
- ✅ Metrics logged (AUC, precision, recall, F1)
- ✅ Model artifacts saved
- ✅ Feature importance logged
- ✅ Run comparison and visualization

## Training Output Example

### Without MLflow (Fast)
```
INFO:__main__:Starting model training...
INFO:__main__:MLflow tracking disabled (use_mlflow=False)
INFO:__main__:Generating synthetic training data...
INFO:__main__:Total samples: 10000
INFO:__main__:Normal samples: 7000
INFO:__main__:Failing samples: 3000
INFO:__main__:Extracting features...
INFO:__main__:Extracted 53 features from 100 vehicles
INFO:__main__:Training anomaly detection ensemble...
INFO:__main__:Evaluating model...
INFO:__main__:AUC: 0.9456, Precision: 0.8923, Recall: 0.9167, F1: 0.9043
INFO:__main__:Model saved to ml/models/anomaly_detection
INFO:__main__:Feature importance saved to ml/models/anomaly_detection/feature_importance.txt
============================================================
✓ Training completed successfully!
============================================================
Feature count: 53
Top 5 features: ['engine_temperature_mean', 'oil_pressure_trend', ...]
Model saved to: ml/models/anomaly_detection/
============================================================
```

### With MLflow
```
INFO:__main__:Starting model training...
✓ MLflow tracking enabled at http://localhost:5000
INFO:__main__:Generating synthetic training data...
INFO:__main__:Total samples: 10000
INFO:__main__:Normal samples: 7000
INFO:__main__:Failing samples: 3000
INFO:__main__:Extracting features...
INFO:__main__:Extracted 53 features from 100 vehicles
INFO:__main__:Training anomaly detection ensemble...
INFO:__main__:Evaluating model...
INFO:__main__:AUC: 0.9456, Precision: 0.8923, Recall: 0.9167, F1: 0.9043
INFO:__main__:Model saved to ml/models/anomaly_detection
INFO:__main__:Feature importance saved to ml/models/anomaly_detection/feature_importance.txt
INFO:__main__:MLflow run ID: abc123def456...
INFO:__main__:Training completed successfully!
```

## Synthetic Data Details

The training generates realistic failure scenarios:

### Normal Vehicles (70%)
- Engine temp: 90°C ± 5°C
- Oil pressure: 45 PSI ± 5 PSI
- Vibration: 0.5g ± 0.2g
- Battery: 12.6V ± 0.2V

### Failing Vehicles (30%)

**Engine Overheating (25% of failures)**
- Progressive temp increase: 90°C → 120°C
- Coolant temp increase: 85°C → 105°C
- Oil pressure drop: 45 PSI → 25 PSI

**Low Oil Pressure (25% of failures)**
- Oil pressure drop: 45 PSI → 15 PSI
- Increased vibration: 0.5g → 2.5g

**High Vibration (25% of failures)**
- Vibration increase: 0.5g → 4.5g
- Stable other metrics

**Battery Degradation (25% of failures)**
- Battery voltage drop: 12.6V → 11.6V
- Gradual deterioration over time

## Model Files Created

After training, you'll find:

```
ml/models/anomaly_detection/
├── isolation_forest.pkl       # Unsupervised anomaly detector
├── xgboost.pkl               # Supervised classifier
├── scaler.pkl                # Feature scaler
├── feature_names.json        # Feature list
├── model_metadata.json       # Training info
└── feature_importance.txt    # Top 20 features
```

## Troubleshooting

### MLflow Connection Retries (SOLVED!)
**Old Behavior**: Script would retry 5 times, taking 30+ seconds
**New Behavior**: Fast connection check (1 second timeout), immediate fallback
**Solution**: Use `--no-mlflow` flag or `train_ml_model.bat` for instant training

### MLflow Connection Refused
**Cause**: MLflow server not running
**Solutions**:
1. **Recommended**: Train without MLflow using `--no-mlflow` flag
2. OR start MLflow server first with `start_mlflow.bat`

### Command Line Options

```bash
# Train without MLflow (fast)
python train_model.py --no-mlflow

# Train with MLflow (if server is running)
python train_model.py
```

### AttributeError: 'EntryPoints' object has no attribute 'get'
**Cause**: Incompatible MLflow version (2.9.2) with newer Python packages
**Solution**: 
```bash
pip install --upgrade mlflow==2.15.1
```

### ImportError: No module named 'mlflow'
**Cause**: MLflow not installed in venv
**Solution**: 
```bash
pip install mlflow==2.15.1
```
OR just train without MLflow using `--no-mlflow` flag

### Model Files Not Created
**Cause**: Permission issues or path error
**Solution**: Check that `ml/models/` directory exists and is writable

### Low Model Performance
**Cause**: This is synthetic data - real data will perform differently
**Solution**: Retrain with actual telemetry data after deployment

## Next Steps After Training

1. ✅ **Verify Model Files**: Check `ml/models/anomaly_detection/` directory
2. ✅ **Test ML Service**: Run `python api/ml_service.py`
3. ✅ **Make Predictions**: `curl -X POST http://localhost:8002/predict -d '{"vehicle_id": 1}'`
4. ✅ **Start Master Agent**: Begin autonomous workflow orchestration

## Retraining the Model

To retrain with new data (e.g., after collecting feedback):

```bash
# Export labeled data from feedback
python -c "
from agents.feedback_agent import FeedbackAgent
import asyncio
agent = FeedbackAgent()
asyncio.run(agent.export_training_data(Path('ml/data/labeled_data.json')))
"

# Retrain with real data (implement custom loader)
python train_model.py
```

## MLflow UI Features

When running with MLflow:

- **Experiments**: Group related training runs
- **Runs**: Individual training sessions with metrics
- **Metrics**: AUC, Precision, Recall, F1 over time
- **Parameters**: Hyperparameters logged
- **Artifacts**: Saved models and files
- **Comparison**: Side-by-side run comparison

Access at: http://localhost:5000
