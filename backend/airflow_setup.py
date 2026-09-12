"""
Apache Airflow Setup Script for Refinify-AI
Initializes Airflow with custom configuration and connections
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def setup_airflow():
    """
    Setup Apache Airflow for Refinify-AI
    """
    print("🚀 Setting up Apache Airflow for Refinify-AI...")
    
    # Get current directory
    current_dir = Path(__file__).parent
    airflow_home = current_dir / "airflow"
    
    # Set environment variables
    os.environ['AIRFLOW_HOME'] = str(airflow_home)
    os.environ['AIRFLOW__CORE__DAGS_FOLDER'] = str(current_dir / "airflow_dags")
    os.environ['AIRFLOW__CORE__PLUGINS_FOLDER'] = str(current_dir / "airflow_plugins")
    
    # Create necessary directories
    directories = [
        airflow_home,
        airflow_home / "dags",
        airflow_home / "logs",
        airflow_home / "plugins",
        airflow_home / "config",
        current_dir / "backups"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Copy DAGs to Airflow dags folder
    dags_source = current_dir / "airflow_dags"
    dags_dest = airflow_home / "dags"
    
    if dags_source.exists():
        for dag_file in dags_source.glob("*.py"):
            if dag_file.name != "__init__.py":
                shutil.copy2(dag_file, dags_dest / dag_file.name)
                print(f"✅ Copied DAG: {dag_file.name}")
    
    # Copy operators to Airflow plugins folder
    operators_source = current_dir / "airflow_operators"
    operators_dest = airflow_home / "plugins"
    
    if operators_source.exists():
        for operator_file in operators_source.glob("*.py"):
            if operator_file.name != "__init__.py":
                shutil.copy2(operator_file, operators_dest / operator_file.name)
                print(f"✅ Copied operator: {operator_file.name}")
    
    # Create Airflow configuration file
    create_airflow_config(airflow_home)
    
    # Initialize Airflow database
    initialize_airflow_db()
    
    # Create admin user
    create_admin_user()
    
    # Setup connections
    setup_connections()
    
    print("\n🎉 Apache Airflow setup completed successfully!")
    print(f"📁 Airflow home: {airflow_home}")
    print(f"🔗 Web UI will be available at: http://localhost:8080")
    print(f"👤 Default admin credentials: admin/admin")
    print("\n📋 Next steps:")
    print("1. Start Airflow webserver: airflow webserver -p 8080")
    print("2. Start Airflow scheduler: airflow scheduler")
    print("3. Open http://localhost:8080 in your browser")

def create_airflow_config(airflow_home):
    """
    Create Airflow configuration file
    """
    config_content = f"""
[core]
dags_folder = {airflow_home}/dags
plugins_folder = {airflow_home}/plugins
executor = LocalExecutor
sql_alchemy_conn = sqlite:///{airflow_home}/airflow.db
load_examples = False
fernet_key = your-fernet-key-here

[webserver]
web_server_host = 0.0.0.0
web_server_port = 8080
secret_key = your-secret-key-here

[scheduler]
job_heartbeat_sec = 5
scheduler_heartbeat_sec = 5
max_tis_per_query = 512
parsing_processes = 2

[email]
email_backend = airflow.utils.email.send_email_smtp
smtp_host = localhost
smtp_starttls = True
smtp_ssl = False
smtp_user = airflow
smtp_password = airflow
smtp_port = 587
smtp_mail_from = airflow@example.com

[celery]
celery_app_name = airflow.executors.celery_executor
worker_concurrency = 16
worker_prefetch_multiplier = 1
worker_log_server_port = 8793
broker_url = redis://localhost:6379/0
result_backend = db+postgresql://airflow:airflow@localhost/airflow

[logging]
base_log_folder = {airflow_home}/logs
dag_processor_manager_log_location = {airflow_home}/logs/dag_processor_manager/dag_processor_manager.log
task_log_reader = task

[metrics]
statsd_on = False
statsd_host = localhost
statsd_port = 8125
statsd_prefix = airflow

[secrets]
backend = airflow.secrets.environment_variables.EnvironmentVariablesBackend
"""
    
    config_file = airflow_home / "airflow.cfg"
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    print(f"✅ Created Airflow config: {config_file}")

def initialize_airflow_db():
    """
    Initialize Airflow database
    """
    print("🗄️  Initializing Airflow database...")
    
    try:
        # Initialize the database
        result = subprocess.run(
            ["airflow", "db", "init"],
            capture_output=True,
            text=True,
            env=os.environ
        )
        
        if result.returncode == 0:
            print("✅ Airflow database initialized successfully")
        else:
            print(f"⚠️  Database initialization output: {result.stdout}")
            print(f"⚠️  Database initialization errors: {result.stderr}")
            
    except FileNotFoundError:
        print("❌ Airflow command not found. Please install Apache Airflow first.")
        print("   Run: pip install apache-airflow")
        return False
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False
    
    return True

def create_admin_user():
    """
    Create Airflow admin user
    """
    print("👤 Creating admin user...")
    
    try:
        # Create admin user
        result = subprocess.run([
            "airflow", "users", "create",
            "--username", "admin",
            "--firstname", "Admin",
            "--lastname", "User",
            "--role", "Admin",
            "--email", "admin@refinify-ai.com",
            "--password", "admin"
        ], capture_output=True, text=True, env=os.environ)
        
        if result.returncode == 0:
            print("✅ Admin user created successfully")
        else:
            print(f"⚠️  User creation output: {result.stdout}")
            print(f"⚠️  User creation errors: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")

def setup_connections():
    """
    Setup Airflow connections
    """
    print("🔗 Setting up Airflow connections...")
    
    try:
        # Setup PostgreSQL connection
        subprocess.run([
            "airflow", "connections", "add",
            "--conn-id", "refinify_postgres",
            "--conn-type", "postgres",
            "--conn-host", "localhost",
            "--conn-login", "airflow",
            "--conn-password", "airflow",
            "--conn-port", "5432",
            "--conn-schema", "airflow"
        ], capture_output=True, env=os.environ)
        
        # Setup Redis connection
        subprocess.run([
            "airflow", "connections", "add",
            "--conn-id", "refinify_redis",
            "--conn-type", "redis",
            "--conn-host", "localhost",
            "--conn-port", "6379",
            "--conn-password", ""
        ], capture_output=True, env=os.environ)
        
        # Setup Slack connection (placeholder)
        subprocess.run([
            "airflow", "connections", "add",
            "--conn-id", "refinify_slack",
            "--conn-type", "http",
            "--conn-host", "https://hooks.slack.com",
            "--conn-password", "your-slack-webhook-url"
        ], capture_output=True, env=os.environ)
        
        # Setup email connection
        subprocess.run([
            "airflow", "connections", "add",
            "--conn-id", "refinify_email",
            "--conn-type", "email",
            "--conn-host", "smtp.gmail.com",
            "--conn-login", "your-email@gmail.com",
            "--conn-password", "your-app-password",
            "--conn-port", "587"
        ], capture_output=True, env=os.environ)
        
        print("✅ Airflow connections configured")
        
    except Exception as e:
        print(f"❌ Error setting up connections: {e}")

def create_startup_scripts():
    """
    Create startup scripts for Airflow
    """
    print("📜 Creating startup scripts...")
    
    # Create Windows batch file
    batch_content = """@echo off
echo Starting Apache Airflow for Refinify-AI...
echo.

REM Set environment variables
set AIRFLOW_HOME=%~dp0airflow
set AIRFLOW__CORE__DAGS_FOLDER=%~dp0airflow_dags
set AIRFLOW__CORE__PLUGINS_FOLDER=%~dp0airflow_plugins

echo Environment variables set:
echo AIRFLOW_HOME=%AIRFLOW_HOME%
echo.

echo Starting Airflow webserver...
start "Airflow Webserver" cmd /k "airflow webserver -p 8080"

echo Starting Airflow scheduler...
start "Airflow Scheduler" cmd /k "airflow scheduler"

echo.
echo Airflow services started!
echo Web UI: http://localhost:8080
echo Username: admin
echo Password: admin
echo.
pause
"""
    
    batch_file = Path(__file__).parent / "start_airflow.bat"
    with open(batch_file, 'w') as f:
        f.write(batch_content)
    
    print(f"✅ Created startup script: {batch_file}")
    
    # Create shell script for Unix systems
    shell_content = """#!/bin/bash
echo "Starting Apache Airflow for Refinify-AI..."
echo

# Set environment variables
export AIRFLOW_HOME="$(dirname "$0")/airflow"
export AIRFLOW__CORE__DAGS_FOLDER="$(dirname "$0")/airflow_dags"
export AIRFLOW__CORE__PLUGINS_FOLDER="$(dirname "$0")/airflow_plugins"

echo "Environment variables set:"
echo "AIRFLOW_HOME=$AIRFLOW_HOME"
echo

echo "Starting Airflow webserver..."
airflow webserver -p 8080 &
WEBSERVER_PID=$!

echo "Starting Airflow scheduler..."
airflow scheduler &
SCHEDULER_PID=$!

echo
echo "Airflow services started!"
echo "Web UI: http://localhost:8080"
echo "Username: admin"
echo "Password: admin"
echo
echo "Press Ctrl+C to stop all services"

# Wait for interrupt signal
trap "echo 'Stopping Airflow services...'; kill $WEBSERVER_PID $SCHEDULER_PID; exit" INT
wait
"""
    
    shell_file = Path(__file__).parent / "start_airflow.sh"
    with open(shell_file, 'w') as f:
        f.write(shell_content)
    
    # Make shell script executable
    shell_file.chmod(0o755)
    
    print(f"✅ Created startup script: {shell_file}")

def main():
    """
    Main setup function
    """
    print("=" * 60)
    print("🔧 Apache Airflow Setup for Refinify-AI")
    print("=" * 60)
    
    # Check if Airflow is installed
    try:
        import airflow
        print(f"✅ Apache Airflow {airflow.__version__} detected")
    except ImportError:
        print("❌ Apache Airflow not found!")
        print("Please install it first:")
        print("pip install apache-airflow[postgres,redis,slack,email]")
        return
    
    # Run setup
    setup_airflow()
    
    # Create startup scripts
    create_startup_scripts()
    
    print("\n" + "=" * 60)
    print("🎯 Setup Complete! Your Refinify-AI automation is ready.")
    print("=" * 60)

if __name__ == "__main__":
    main()
