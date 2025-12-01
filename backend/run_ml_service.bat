@echo off
echo ========================================
echo Starting ML Prediction Service
echo Port: 8002
echo ========================================
cd api
python ml_service.py
pause
