@echo off
REM Double-click launcher for setup-venvs.ps1: (re)builds the per-version dev
REM venvs. Runs PowerShell with the execution policy bypassed for this one
REM process, and pauses so you can read the result.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup-venvs.ps1"
echo.
pause
