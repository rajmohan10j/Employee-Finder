@echo off
title Employee-Finder - 1-Click Public Mobile Access Tunnel
cls
echo =====================================================================
echo  Candidate Tracker - 1-Click Public Mobile Access Tunnel
echo =====================================================================
echo [INFO] Preparing 1-Click Public HTTPS Tunnel for 4G/5G Remote Access...
echo.

cd /d "%~dp0"

:: Step 1: Ensure Local App is running
echo [1/3] Checking if Candidate Tracker server is running...
curl -s http://127.0.0.1:5000/api/version >nul 2>&1
if %ERRORLEVEL% EQU 0 goto app_running

echo [INFO] Starting Candidate Tracker server in background...
start /min "" python candidate_app\app.py
timeout /t 3 /nobreak >nul

:app_running
echo [INFO] Candidate Tracker is active on port 5000.

:: Step 2: Ensure cloudflared.exe is available
if exist "cloudflared.exe" goto start_tunnel

echo [2/3] Downloading free portable Cloudflare Tunnel client (first time only)...
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile 'cloudflared.exe'"

if not exist "cloudflared.exe" (
    echo [ERROR] Could not download cloudflared.exe automatically.
    pause
    exit /b 1
)

:start_tunnel
:: Step 3: Start Cloudflare Tunnel
echo.
echo =====================================================================
echo  [3/3] LAUNCHING SECURE HTTPS PUBLIC TUNNEL
echo =====================================================================
echo  Look for the link ending in ".trycloudflare.com" below.
echo  Share that HTTPS link with your team members on ANY phone or 4G/5G!
echo =====================================================================
echo.
cloudflared.exe tunnel --url http://127.0.0.1:5000
pause
