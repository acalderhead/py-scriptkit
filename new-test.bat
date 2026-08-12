@echo off
REM Double-click launcher for new-test.ps1: runs it interactively (pick an
REM existing file to test, or name a new one), bypassing the execution policy
REM for this one process, and pauses so you can read the result.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0new-test.ps1"
echo.
pause
