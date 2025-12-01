@echo off
echo ========================================
echo Training ML Model (Fast Mode)
echo This will generate synthetic data and
echo train the anomaly detection ensemble
echo WITHOUT MLflow tracking (faster)
echo ========================================
cd ml
python train_model.py --no-mlflow
pause
