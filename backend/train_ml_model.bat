@echo off
echo ========================================
echo Training ML Model
echo This will generate synthetic data and
echo train the anomaly detection ensemble
echo ========================================
cd ml
python train_model.py
pause
