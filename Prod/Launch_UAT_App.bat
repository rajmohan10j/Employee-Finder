@echo off
title Employee Finder - UAT Testing Environment
cd /d "%~dp0candidate_app"

echo ========================================================
echo   STARTING EMPLOYEE FINDER - UAT TESTING ENVIRONMENT
echo   (Independent from Production)
echo ========================================================
echo.

:: Check if server is already running on port 5000
netstat -ano | findstr :5000 | findstr LISTENING >nul
if %errorlevel% equ 0 (
    echo [INFO] A server is already running on port 5000!
    echo [INFO] Starting UAT Server on alternate port 5001...
    set PORT=5001
    start /min "Employee Finder - UAT (Port 5001)" python -c "import os; os.environ['PORT']='5001'; from app import app; app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)"
    timeout /t 2 /nobreak >nul
    echo [INFO] Opening Google Chrome to UAT http://127.0.0.1:5001 ...
    start "" "http://127.0.0.1:5001"
) else (
    echo [INFO] Launching UAT Python Flask server on port 5000...
    start /min "Employee Finder - UAT" python app.py
    timeout /t 2 /nobreak >nul
    echo [INFO] Opening Google Chrome to UAT http://127.0.0.1:5000 ...
    start "" "http://127.0.0.1:5000"
)

exit
