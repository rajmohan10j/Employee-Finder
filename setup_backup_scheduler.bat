@echo off
REM =========================================================================
REM Employee-Finder: Automated GFS Windows Task Scheduler Registration
REM Schedulers configured:
REM   1. Daily Afternoon Slot: 01:00 PM (13:00)
REM   2. Daily Evening Slot:   06:00 PM (18:00)
REM   3. Weekly Saturday Slot: Saturday 06:00 PM (18:00)
REM   4. Monthly Slot:         1st of every month at 09:00 AM
REM =========================================================================

echo ============================================================
echo  Setting up Automated GFS Backup Tasks in Windows Task Scheduler
echo ============================================================

set PYTHON_EXE=python
set SCRIPT_PATH=C:\Users\Raj\Projects\Employee-Finder\candidate_app\backup_manager.py

REM 1. Daily Afternoon Backup (1:00 PM)
schtasks /create /tn "EmployeeFinder_Daily_1300" /tr "%PYTHON_EXE% \"%SCRIPT_PATH%\" --trigger daily" /sc daily /st 13:00 /f
if %ERRORLEVEL% EQU 0 (
    echo [OK] Registered Task: EmployeeFinder_Daily_1300 (Everyday at 01:00 PM)
) else (
    echo [WARNING] Could not register EmployeeFinder_Daily_1300
)

REM 2. Daily Evening Backup (6:00 PM)
schtasks /create /tn "EmployeeFinder_Daily_1800" /tr "%PYTHON_EXE% \"%SCRIPT_PATH%\" --trigger daily" /sc daily /st 18:00 /f
if %ERRORLEVEL% EQU 0 (
    echo [OK] Registered Task: EmployeeFinder_Daily_1800 (Everyday at 06:00 PM)
) else (
    echo [WARNING] Could not register EmployeeFinder_Daily_1800
)

REM 3. Weekly Saturday Evening Backup (6:00 PM)
schtasks /create /tn "EmployeeFinder_Weekly_Sat_1800" /tr "%PYTHON_EXE% \"%SCRIPT_PATH%\" --trigger weekly" /sc weekly /d SAT /st 18:00 /f
if %ERRORLEVEL% EQU 0 (
    echo [OK] Registered Task: EmployeeFinder_Weekly_Sat_1800 (Every Saturday at 06:00 PM)
) else (
    echo [WARNING] Could not register EmployeeFinder_Weekly_Sat_1800
)

REM 4. Monthly Backup (1st of month at 09:00 AM)
schtasks /create /tn "EmployeeFinder_Monthly_01_0900" /tr "%PYTHON_EXE% \"%SCRIPT_PATH%\" --trigger monthly" /sc monthly /d 1 /st 09:00 /f
if %ERRORLEVEL% EQU 0 (
    echo [OK] Registered Task: EmployeeFinder_Monthly_01_0900 (1st of Month at 09:00 AM)
) else (
    echo [WARNING] Could not register EmployeeFinder_Monthly_01_0900
)

echo.
echo ============================================================
echo  GFS Backup Task Registration Complete!
echo ============================================================
pause
