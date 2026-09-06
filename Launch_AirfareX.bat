@echo off
title AirfareX India Launcher (All Devices)
echo ===================================================
echo   AirfareX India — Multi-Device & Network Server
echo ===================================================

:: Check if server is running on port 8000
netstat -ano | findstr :8000 >nul 2>&1
if %errorlevel% neq 0 (
    echo Starting backend server on 0.0.0.0 in background...
    start "" /B python run_server.py
    timeout /t 2 /nobreak >nul
)

echo.
echo >> Localhost:       http://127.0.0.1:8000/
echo >> Local Network:   http://10.221.83.242:8000/
echo.
echo Opening Web Browser...
start "" "http://127.0.0.1:8000/"

