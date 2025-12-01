@echo off
echo ========================================
echo Training ML Model WITH MLflow Tracking
echo ========================================
echo.
echo IMPORTANT: Make sure MLflow server is running!
echo   Start it with: start_mlflow.bat
echo.
echo MLflow UI: http://localhost:5000
echo ========================================
echo.
cd ml
python train_model.py
pause
