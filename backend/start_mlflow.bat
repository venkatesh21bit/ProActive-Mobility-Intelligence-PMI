@echo off
echo ============================================
echo Starting MLflow Tracking Server
echo ============================================
echo.
echo MLflow UI will be available at:
echo   http://localhost:5000
echo.
echo This server tracks ML experiments and models
echo Press Ctrl+C to stop
echo ============================================
echo.
cd /d "%~dp0"
cd ..
mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./ml/mlruns
pause
