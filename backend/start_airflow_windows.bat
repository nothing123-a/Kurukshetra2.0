@echo off
title Apache Airflow for Refinify-AI
color 0B

echo.
echo ========================================
echo   Starting Apache Airflow on Windows
echo ========================================
echo.

REM Set Airflow environment variables
set AIRFLOW_HOME=%~dp0airflow
set AIRFLOW__CORE__DAGS_FOLDER=%~dp0airflow_dags
set AIRFLOW__CORE__PLUGINS_FOLDER=%~dp0airflow_operators

echo Airflow Home: %AIRFLOW_HOME%
echo DAGs Folder: %AIRFLOW__CORE__DAGS_FOLDER%
echo.

REM Check if Airflow is installed
python -c "import airflow" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Apache Airflow is not installed!
    echo Please run: pip install apache-airflow[postgres,redis,slack,email]
    echo.
    pause
    exit /b 1
)

REM Check if Airflow is initialized
if not exist "%AIRFLOW_HOME%\airflow.cfg" (
    echo Initializing Airflow for first time...
    python airflow_setup.py
    if errorlevel 1 (
        echo ERROR: Failed to initialize Airflow!
        pause
        exit /b 1
    )
)

echo Starting Airflow services...
echo.

REM Start Airflow webserver
echo [1/3] Starting Airflow Webserver on port 8080...
start "Airflow Webserver" /B python -c "import os; os.environ['AIRFLOW_HOME']='%AIRFLOW_HOME%'; os.system('airflow webserver --port 8080')"

REM Wait a bit for webserver to start
timeout /t 5 /nobreak >nul

REM Start Airflow scheduler
echo [2/3] Starting Airflow Scheduler...
start "Airflow Scheduler" /B python -c "import os; os.environ['AIRFLOW_HOME']='%AIRFLOW_HOME%'; os.system('airflow scheduler')"

REM Wait for scheduler to start
timeout /t 5 /nobreak >nul

REM Start Airflow worker (if using Celery)
echo [3/3] Starting Airflow Worker...
start "Airflow Worker" /B python -c "import os; os.environ['AIRFLOW_HOME']='%AIRFLOW_HOME%'; os.system('airflow celery worker')"

echo.
echo ========================================
echo   Apache Airflow Started Successfully!
echo ========================================
echo.
echo Web UI: http://localhost:8080
echo Login: admin / admin
echo.
echo Services Running:
echo - Webserver (Port 8080)
echo - Scheduler
echo - Worker
echo.
echo Press any key to open Airflow Web UI...
pause >nul
start http://localhost:8080
