@echo off
title Employee Finder - Production Version (V1)
cd /d "%~dp0candidate_app"

echo ========================================================
echo   STARTING EMPLOYEE FINDER - PRODUCTION VERSION (V1)
echo ========================================================
echo.

:: Check if server is already running on port 5000
netstat -ano | findstr :5000 | findstr LISTENING >nul
if %errorlevel% equ 0 (
    echo [INFO] Server is already running on port 5000!
) else (
    echo [INFO] Launching Production Python Flask server on port 5000...
    start /min "Employee Finder - Production" python app.py
    timeout /t 2 /nobreak >nul
)

echo [INFO] Opening Google Chrome to http://127.0.0.1:5000 ...
start "" "http://127.0.0.1:5000"

exit
