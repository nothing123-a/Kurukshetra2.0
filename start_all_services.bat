@echo off
title Refinify-AI Complete Service Manager
color 0E

:menu
cls
echo.
echo ========================================
echo     REFINIFY-AI SERVICE MANAGER
echo ========================================
echo.
echo Choose what to start:
echo.
echo [1] Start Everything (Backend + Frontend + Airflow + Windows Automation)
echo [2] Start Backend Only
echo [3] Start Frontend Only
echo [4] Start Apache Airflow Only
echo [5] Start Windows Automation Only
echo [6] Start Backend + Frontend (No Airflow)
echo [7] Start Backend + Airflow (No Frontend)
echo [8] Check Service Status
echo [9] Stop All Services
echo [0] Exit
echo.
echo ========================================
set /p choice="Enter your choice (0-9): "

if "%choice%"=="1" goto start_all
if "%choice%"=="2" goto start_backend
if "%choice%"=="3" goto start_frontend
if "%choice%"=="4" goto start_airflow
if "%choice%"=="5" goto start_windows_automation
if "%choice%"=="6" goto start_backend_frontend
if "%choice%"=="7" goto start_backend_airflow
if "%choice%"=="8" goto check_status
if "%choice%"=="9" goto stop_all
if "%choice%"=="0" goto exit
goto menu

:start_all
echo.
echo Starting ALL services...
echo.
call start_services.bat
goto menu

:start_backend
echo.
echo Starting Backend only...
cd backend
start /B python start_simple.py
cd ..
echo Backend started on port 8000
echo Health check: http://localhost:8000/health
timeout /t 3 /nobreak >nul
goto menu

:start_frontend
echo.
echo Starting Frontend only...
cd frontend
start /B npm run dev
cd ..
echo Frontend started on port 3000
echo URL: http://localhost:3000
timeout /t 3 /nobreak >nul
goto menu

:start_airflow
echo.
echo Starting Apache Airflow...
call backend\start_airflow_windows.bat
goto menu

:start_windows_automation
echo.
echo Starting Windows Automation System...
cd backend
start /B python windows_automation.py
cd ..
echo Windows Automation started
timeout /t 3 /nobreak >nul
goto menu

:start_backend_frontend
echo.
echo Starting Backend + Frontend...
echo.
echo [1/2] Starting Backend...
cd backend
start /B python start_simple.py
cd ..
timeout /t 5 /nobreak >nul
echo [2/2] Starting Frontend...
cd frontend
start /B npm run dev
cd ..
echo.
echo Services started:
echo - Backend: http://localhost:8000
echo - Frontend: http://localhost:3000
timeout /t 3 /nobreak >nul
goto menu

:start_backend_airflow
echo.
echo Starting Backend + Airflow...
echo.
echo [1/3] Starting Backend...
cd backend
start /B python start_simple.py
cd ..
timeout /t 5 /nobreak >nul
echo [2/3] Starting Airflow...
call backend\start_airflow_windows.bat
echo.
echo Services started:
echo - Backend: http://localhost:8000
echo - Airflow: http://localhost:8080
timeout /t 3 /nobreak >nul
goto menu

:check_status
echo.
echo Checking service status...
echo.
echo Backend (Port 8000):
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo - Status: RUNNING
) else (
    echo - Status: STOPPED
)

echo.
echo Frontend (Port 3000):
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo - Status: RUNNING
) else (
    echo - Status: STOPPED
)

echo.
echo Airflow (Port 8080):
curl -s http://localhost:8080 >nul 2>&1
if %errorlevel% equ 0 (
    echo - Status: RUNNING
) else (
    echo - Status: STOPPED
)

echo.
echo Press any key to continue...
pause >nul
goto menu

:stop_all
echo.
echo Stopping all services...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
echo All services stopped
timeout /t 3 /nobreak >nul
goto menu

:exit
echo.
echo Goodbye!
timeout /t 2 /nobreak >nul
exit
