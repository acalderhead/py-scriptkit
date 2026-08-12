@echo off
REM Double-click launcher for new-test.ps1: prompts for a name, then scaffolds a
REM new pytest file. Runs PowerShell with the execution policy bypassed for this
REM one process, and pauses so you can read the result.
setlocal
set /p "name=Name for the module under test: "
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0new-test.ps1" -Name "%name%"
echo.
pause
