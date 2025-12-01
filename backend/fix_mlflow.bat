@echo off
echo ============================================
echo Upgrading MLflow to Fix Compatibility Issue
echo ============================================
echo.
echo This will upgrade MLflow from 2.9.2 to 2.15.1
echo to fix the 'EntryPoints' error
echo.
echo ============================================
echo.
pip install --upgrade mlflow==2.15.1
echo.
echo ============================================
echo MLflow Upgrade Complete!
echo ============================================
echo.
echo You can now run: start_mlflow.bat
echo.
pause
