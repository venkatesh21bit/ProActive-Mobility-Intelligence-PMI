@echo off
echo ============================================
echo Starting Master Agent with Ray
echo ============================================
echo.
echo This will initialize Ray and start the
echo Master Agent orchestration system.
echo.
echo The agent will listen for alerts on:
echo   Redis Stream: alerts:predicted
echo.
echo Press Ctrl+C to stop
echo ============================================
echo.
cd /d "%~dp0"
cd ..
python -m agents
pause
