"""
Main Refinify-AI Workflow DAG
Orchestrates the complete data processing pipeline with accuracy monitoring
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.branch import BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.email import EmailOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.models import Variable
import sys
import os

# Add backend directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from airflow_config import AirflowConfig
from airflow_operators.data_quality_operator import DataQualityOperator
from airflow_operators.accuracy_monitor_operator import AccuracyMonitorOperator
from airflow_operators.safety_check_operator import SafetyCheckOperator

# Default arguments for the DAG
default_args = {
    'owner': 'refinify-ai',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': AirflowConfig.MONITORING['enable_email_alerts'],
    'email_on_retry': False,
    'retries': AirflowConfig.QUALITY_CONTROL['max_retries'],
    'retry_delay': AirflowConfig.QUALITY_CONTROL['retry_delay'],
    'catchup': False,
}

# Create the main DAG
dag = DAG(
    'refinify_main_workflow',
    default_args=default_args,
    description='Main Refinify-AI data processing workflow with accuracy monitoring',
    schedule_interval=AirflowConfig.SCHEDULING['data_cleaning_interval'],
    max_active_runs=1,
    tags=['refinify-ai', 'data-processing', 'ai-automation'],
    catchup=False,
)

# Task 1: Start workflow
start_workflow = DummyOperator(
    task_id='start_workflow',
    dag=dag,
)

# Task 2: Safety check and backup
safety_check = SafetyCheckOperator(
    task_id='safety_check',
    dag=dag,
    safety_features=['backup_before_processing', 'enable_rollback'],
    timeout=300,
)

# Task 3: Data quality assessment
assess_data_quality = DataQualityOperator(
    task_id='assess_data_quality',
    dag=dag,
    task_type='data_cleaning',
    batch_size=AirflowConfig.get_task_config('data_cleaning')['batch_size'],
    timeout=AirflowConfig.get_task_config('data_cleaning')['timeout'],
)

# Task 4: Accuracy monitoring for data cleaning
monitor_data_cleaning_accuracy = AccuracyMonitorOperator(
    task_id='monitor_data_cleaning_accuracy',
    dag=dag,
    task_type='data_cleaning',
    accuracy_threshold=AirflowConfig.get_accuracy_threshold('data_cleaning'),
    manual_review_threshold=AirflowConfig.QUALITY_CONTROL['manual_review_threshold'],
)

# Task 5: Branch based on accuracy
def determine_next_step(**context):
    """Determine next step based on accuracy results"""
    ti = context['ti']
    accuracy = ti.xcom_pull(task_ids='monitor_data_cleaning_accuracy', key='accuracy')
    
    if accuracy >= AirflowConfig.get_accuracy_threshold('data_cleaning'):
        return 'proceed_with_processing'
    elif accuracy >= AirflowConfig.QUALITY_CONTROL['manual_review_threshold']:
        return 'manual_review_required'
    else:
        return 'stop_workflow_low_accuracy'

branch_task = BranchPythonOperator(
    task_id='determine_next_step',
    python_callable=determine_next_step,
    dag=dag,
)

# Task 6: Manual review required
manual_review_required = DummyOperator(
    task_id='manual_review_required',
    dag=dag,
)

# Task 7: Stop workflow due to low accuracy
stop_workflow_low_accuracy = DummyOperator(
    task_id='stop_workflow_low_accuracy',
    dag=dag,
)

# Task 8: Proceed with processing
proceed_with_processing = DummyOperator(
    task_id='proceed_with_processing',
    dag=dag,
)

# Task 9: Outlier detection
outlier_detection = DataQualityOperator(
    task_id='outlier_detection',
    dag=dag,
    task_type='outlier_detection',
    batch_size=AirflowConfig.get_task_config('outlier_detection')['batch_size'],
    timeout=AirflowConfig.get_task_config('outlier_detection')['timeout'],
)

# Task 10: Monitor outlier detection accuracy
monitor_outlier_accuracy = AccuracyMonitorOperator(
    task_id='monitor_outlier_accuracy',
    dag=dag,
    task_type='outlier_detection',
    accuracy_threshold=AirflowConfig.get_accuracy_threshold('outlier_detection'),
    manual_review_threshold=AirflowConfig.QUALITY_CONTROL['manual_review_threshold'],
)

# Task 11: Typo correction
typo_correction = DataQualityOperator(
    task_id='typo_correction',
    dag=dag,
    task_type='typo_correction',
    batch_size=AirflowConfig.get_task_config('typo_correction')['batch_size'],
    timeout=AirflowConfig.get_task_config('typo_correction')['timeout'],
)

# Task 12: Monitor typo correction accuracy
monitor_typo_accuracy = AccuracyMonitorOperator(
    task_id='monitor_typo_accuracy',
    dag=dag,
    task_type='typo_correction',
    accuracy_threshold=AirflowConfig.get_accuracy_threshold('typo_correction'),
    manual_review_threshold=AirflowConfig.QUALITY_CONTROL['manual_review_threshold'],
)

# Task 13: Data imputation
data_imputation = DataQualityOperator(
    task_id='data_imputation',
    dag=dag,
    task_type='data_imputation',
    batch_size=AirflowConfig.get_task_config('data_imputation')['batch_size'],
    timeout=AirflowConfig.get_task_config('data_imputation')['timeout'],
)

# Task 14: Monitor imputation accuracy
monitor_imputation_accuracy = AccuracyMonitorOperator(
    task_id='monitor_imputation_accuracy',
    dag=dag,
    task_type='data_imputation',
    accuracy_threshold=AirflowConfig.get_accuracy_threshold('data_imputation'),
    manual_review_threshold=AirflowConfig.QUALITY_CONTROL['manual_review_threshold'],
)

# Task 15: Final quality check
final_quality_check = DataQualityOperator(
    task_id='final_quality_check',
    dag=dag,
    task_type='quality_check',
    batch_size=100,  # Smaller batch for final check
    timeout=600,     # 10 minutes
)

# Task 16: Generate report
generate_report = DataQualityOperator(
    task_id='generate_report',
    dag=dag,
    task_type='report_generation',
    batch_size=50,   # Small batch for report generation
    timeout=900,     # 15 minutes
)

# Task 17: Monitor report accuracy
monitor_report_accuracy = AccuracyMonitorOperator(
    task_id='monitor_report_accuracy',
    dag=dag,
    task_type='report_generation',
    accuracy_threshold=AirflowConfig.get_accuracy_threshold('report_generation'),
    manual_review_threshold=AirflowConfig.QUALITY_CONTROL['manual_review_threshold'],
)

# Task 18: Success notification
success_notification = DummyOperator(
    task_id='success_notification',
    trigger_rule=TriggerRule.ALL_DONE,
    dag=dag,
)

# Task 19: Send success email
send_success_email = EmailOperator(
    task_id='send_success_email',
    to=Variable.get('admin_email', 'admin@refinify-ai.com'),
    subject='Refinify-AI Workflow Completed Successfully',
    html_content="""
    <h2>Refinify-AI Workflow Completed Successfully</h2>
    <p>The automated data processing workflow has completed with high accuracy.</p>
    <p>All quality checks passed and reports have been generated.</p>
    """,
    dag=dag,
    trigger_rule=TriggerRule.ALL_DONE,
)

# Task 20: Send success Slack notification
send_success_slack = SlackWebhookOperator(
    task_id='send_success_slack',
    webhook_conn_id=AirflowConfig.AIRFLOW_SLACK_CONN_ID,
    message="""
    :white_check_mark: *Refinify-AI Workflow Completed Successfully*
    
    The automated data processing workflow has completed with high accuracy.
    All quality checks passed and reports have been generated.
    """,
    dag=dag,
    trigger_rule=TriggerRule.ALL_DONE,
)

# Task 21: End workflow
end_workflow = DummyOperator(
    task_id='end_workflow',
    trigger_rule=TriggerRule.ALL_DONE,
    dag=dag,
)

# Define task dependencies
start_workflow >> safety_check
safety_check >> assess_data_quality
assess_data_quality >> monitor_data_cleaning_accuracy
monitor_data_cleaning_accuracy >> branch_task

# Branch paths
branch_task >> [manual_review_required, stop_workflow_low_accuracy, proceed_with_processing]

# Main processing path
proceed_with_processing >> outlier_detection
outlier_detection >> monitor_outlier_accuracy
monitor_outlier_accuracy >> typo_correction
typo_correction >> monitor_typo_accuracy
monitor_typo_accuracy >> data_imputation
data_imputation >> monitor_imputation_accuracy
monitor_imputation_accuracy >> final_quality_check
final_quality_check >> generate_report
generate_report >> monitor_report_accuracy
monitor_report_accuracy >> success_notification

# Success path
success_notification >> [send_success_email, send_success_slack]
[send_success_email, send_success_slack] >> end_workflow

# Manual review path (can be extended with manual review tasks)
manual_review_required >> end_workflow

# Stop workflow path
stop_workflow_low_accuracy >> end_workflow
