@echo off
title Virtual AI Mouse ^& Keyboard
echo ============================================================
echo         VIRTUAL AI MOUSE ^& KEYBOARD LAUNCHER
echo ============================================================
echo Starting application...
cd /d "%~dp0"
python -m src.main
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with error code %ERRORLEVEL%.
    pause
)
