@echo off
title Refinify-AI Windows Automation System
color 0A

echo.
echo ========================================
echo   Refinify-AI Windows Automation
echo ========================================
echo.
echo This automation system will:
echo - Process data every 6 hours
echo - Create daily backups at 2:00 AM
echo - Clean data and detect outliers
echo - Monitor accuracy and quality
echo - Generate detailed reports
echo.
echo Press Ctrl+C to stop the automation
echo.
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking required packages...
python -c "import pandas, numpy, schedule" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install pandas numpy schedule
    if errorlevel 1 (
        echo ERROR: Failed to install required packages
        pause
        exit /b 1
    )
)

echo Starting automation system...
echo.

REM Start the automation
python windows_automation.py

echo.
echo Automation stopped.
pause
