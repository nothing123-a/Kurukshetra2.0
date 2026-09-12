from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'bhishma's',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'bhishma's_clinical_trial_pipeline',
    default_args=default_args,
    description='Bhishma's Clinical Trial Data Processing Pipeline',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['bhishma's', 'clinical-trials', 'data-processing'],
)

def process_drug_data():
    """Process drug testing data"""
    print("Processing drug testing data...")
    return "Drug data processed successfully"

def run_trial_simulation():
    """Run clinical trial simulation"""
    print("Running clinical trial simulation...")
    return "Trial simulation completed"

def generate_reports():
    """Generate analysis reports"""
    print("Generating analysis reports...")
    return "Reports generated successfully"

# Define tasks
drug_processing = PythonOperator(
    task_id='process_drug_data',
    python_callable=process_drug_data,
    dag=dag,
)

trial_simulation = PythonOperator(
    task_id='run_trial_simulation',
    python_callable=run_trial_simulation,
    dag=dag,
)

report_generation = PythonOperator(
    task_id='generate_reports',
    python_callable=generate_reports,
    dag=dag,
)

# Set task dependencies
drug_processing >> trial_simulation >> report_generation