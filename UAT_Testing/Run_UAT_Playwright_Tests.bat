@echo off
title Employee Finder - UAT Test Suite Runner
cd /d "%~dp0candidate_app"

echo ========================================================
echo   RUNNING UAT PLAYWRIGHT AUTOMATED TEST SUITES
echo ========================================================
echo.

echo [1/2] Running Playwright E2E Test Suite...
python playwright_e2e_test.py
if %errorlevel% neq 0 (
    echo [ERROR] Playwright E2E tests failed!
    pause
    exit /b 1
)

echo.
echo [2/2] Running Playwright Mobile Viewport Test Suite...
python playwright_android_mobile_test.py
if %errorlevel% neq 0 (
    echo [ERROR] Playwright Mobile tests failed!
    pause
    exit /b 1
)

echo.
echo ========================================================
echo   ALL UAT AUTOMATED TESTS PASSED SUCCESSFULLY (100%%)
echo ========================================================
pause
