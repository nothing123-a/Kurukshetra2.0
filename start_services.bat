@echo off
echo ========================================
echo Starting Refinify - AI Data Pipeline
echo ========================================

echo.
echo [1/5] Checking if backend is already running...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo Backend is already running on port 8000
) else (
    echo Starting backend server...
    cd backend
    start /B python start_simple.py
    cd ..
    echo Waiting for backend to start...
    timeout /t 10 /nobreak >nul
)

echo.
echo [2/5] Checking backend health...
curl -s http://localhost:8000/health
if %errorlevel% equ 0 (
    echo Backend is healthy!
) else (
    echo Warning: Backend may not be fully ready
)

echo.
echo [3/5] Starting Apache Airflow services...
cd backend
echo Starting Airflow webserver...
start /B python -c "import os; os.environ['AIRFLOW_HOME']='./airflow'; os.system('airflow webserver --port 8080')"
echo Starting Airflow scheduler...
start /B python -c "import os; os.environ['AIRFLOW_HOME']='./airflow'; os.system('airflow scheduler')"
echo Starting Airflow worker (if using Celery)...
start /B python -c "import os; os.environ['AIRFLOW_HOME']='./airflow'; os.system('airflow celery worker')"
cd ..
echo Waiting for Airflow to start...
timeout /t 15 /nobreak >nul

echo.
echo [4/5] Starting frontend server...
cd frontend
start /B npm run dev
cd ..

echo.
echo [5/5] Starting Windows Automation System...
cd backend
start /B python windows_automation.py
cd ..

echo.
echo [6/6] All services started!
echo.
echo ========================================
echo   REFINIFY IS NOW RUNNING!
echo ========================================
echo.
echo Frontend:        http://localhost:3000
echo Backend:         http://localhost:8000
echo Backend Health:  http://localhost:8000/health
echo Airflow Web UI:  http://localhost:8080
echo Airflow Login:   admin / admin
echo.
echo Default Login:
echo Username: admin
echo Password: admin123
echo.
echo Services Running:
echo - Flask Backend (Port 8000)
echo - React Frontend (Port 3000)
echo - Apache Airflow (Port 8080)
echo - Windows Automation System
echo.
echo Press any key to open the application...
pause >nul
start http://localhost:3000
start http://localhost:8080