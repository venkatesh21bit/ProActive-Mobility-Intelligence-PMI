@echo off
echo ========================================
echo Starting Ingestion Service
echo Port: 8000
echo ========================================
cd api
python ingestion_service.py
pause
