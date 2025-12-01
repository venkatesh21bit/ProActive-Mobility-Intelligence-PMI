@echo off
echo Testing Master + Worker Agents...
cd /d "%~dp0"
cd ..
python test_agents.py
pause
