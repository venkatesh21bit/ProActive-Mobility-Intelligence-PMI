@echo off
echo ========================================
echo PMI System Startup Checklist
echo ========================================
echo.
echo Step 1: Starting Docker Services...
echo ========================================
docker-compose up -d
echo.
echo Waiting for services to be ready...
timeout /t 10 /nobreak > nul
echo.
echo Step 2: Checking Docker Services Status
echo ========================================
docker-compose ps
echo.
echo ========================================
echo Docker services started!
echo.
echo Now you can start the Python services:
echo   1. run_simulator.bat  (Port 8001)
echo   2. run_ingestion.bat  (Port 8000)
echo   3. run_consumer.bat   (Background)
echo.
echo Access points:
echo   - TimescaleDB: localhost:5432
echo   - Redis: localhost:6379
echo   - MinIO: http://localhost:9000
echo   - MLflow: http://localhost:5000
echo   - Prometheus: http://localhost:9090
echo   - Grafana: http://localhost:3000
echo ========================================
pause
