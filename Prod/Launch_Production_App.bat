@echo off
title Employee-Finder Production Web & Mobile Server
cd /d "%~dp0candidate_app"

echo ============================================================
echo  Starting Candidate Tracker Production Server (Port 5000)
echo ============================================================
echo.
echo Local Access:        http://127.0.0.1:5000
echo Mobile / LAN Access: http://192.168.29.55:5000
echo.
echo [INFO] In-App GFS Backup Scheduler Daemon active (1PM, 6PM, Sat 6PM, 1st 9AM).
echo.

start "" http://127.0.0.1:5000
python app.py

pause
