@echo off
title Employee Finder - Server Launcher
cd /d "%~dp0candidate_app"

echo ========================================================
echo   STARTING EMPLOYEE FINDER & OPENING IN CHROME
echo ========================================================
echo.

:: Check if server is already running on port 5000
netstat -ano | findstr :5000 | findstr LISTENING >nul
if %errorlevel% equ 0 (
    echo [INFO] Server is already running on port 5000!
) else (
    echo [INFO] Launching Python Flask server...
    start /min "Candidate Tracker Server" python app.py
    timeout /t 2 /nobreak >nul
)

echo [INFO] Opening Google Chrome to http://127.0.0.1:5000 ...
start "" "http://127.0.0.1:5000"

exit
