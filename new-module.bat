@echo off
REM Double-click launcher for new-module.ps1: prompts for a name, then scaffolds
REM a new module. Runs PowerShell with the execution policy bypassed for this
REM one process, and pauses so you can read the result.
setlocal
set /p "name=Name for the new module: "
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0new-module.ps1" -Name "%name%"
echo.
pause
