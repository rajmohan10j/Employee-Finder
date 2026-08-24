@echo off
:: Register custom URI protocol "empfinder://" in Windows Current User Registry
echo Setting up empfinder:// custom protocol for Chrome...

reg add "HKCU\Software\Classes\empfinder" /ve /d "URL:Employee Finder Protocol" /f >nul
reg add "HKCU\Software\Classes\empfinder" /v "URL Protocol" /d "" /f >nul
reg add "HKCU\Software\Classes\empfinder\shell\open\command" /ve /d "\"%~dp0Launch_Employee_Finder.bat\"" /f >nul

echo Protocol registered successfully!
