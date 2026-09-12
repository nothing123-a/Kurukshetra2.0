from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import pandas as pd
import os

# Default arguments for the DAG
default_args = {
    'owner': 'refinify',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

# Create the DAG
dag = DAG(
    'refinify_data_processing',
    default_args=default_args,
    description='Refinify AI Data Processing Pipeline',
    schedule_interval=timedelta(hours=1),  # Run every hour
    catchup=False,
    tags=['refinify', 'data-processing', 'ai']
)

def check_data_uploads():
    """Check for new data uploads"""
    upload_dir = '/Users/darshanpatil/Documents/Mern Stack/Refinify/backend/uploads'
    if not os.path.exists(upload_dir):
        print("Upload directory not found")
        return False
    
    files = [f for f in os.listdir(upload_dir) if f.endswith(('.csv', '.xlsx', '.xls'))]
    print(f"Found {len(files)} data files to process")
    return len(files) > 0

def process_data_files():
    """Process uploaded data files with AI"""
    upload_dir = '/Users/darshanpatil/Documents/Mern Stack/Refinify/backend/uploads'
    processed_count = 0
    
    for filename in os.listdir(upload_dir):
        if filename.endswith(('.csv', '.xlsx', '.xls')):
            filepath = os.path.join(upload_dir, filename)
            try:
                # Load and process data
                if filename.endswith('.csv'):
                    df = pd.read_csv(filepath)
                else:
                    df = pd.read_excel(filepath)
                
                # Basic data processing
                original_rows = len(df)
                df_cleaned = df.dropna()  # Remove null values
                df_cleaned = df_cleaned.drop_duplicates()  # Remove duplicates
                
                # Save processed file
                processed_filename = f"processed_{filename}"
                processed_filepath = os.path.join(upload_dir, processed_filename)
                df_cleaned.to_csv(processed_filepath, index=False)
                
                processed_count += 1
                print(f"Processed {filename}: {original_rows} -> {len(df_cleaned)} rows")
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    
    print(f"Successfully processed {processed_count} files")
    return processed_count

def generate_ai_insights():
    """Generate AI insights from processed data"""
    upload_dir = '/Users/darshanpatil/Documents/Mern Stack/Refinify/backend/uploads'
    insights = []
    
    for filename in os.listdir(upload_dir):
        if filename.startswith('processed_') and filename.endswith('.csv'):
            filepath = os.path.join(upload_dir, filename)
            try:
                df = pd.read_csv(filepath)
                
                # Generate basic insights
                insight = {
                    'filename': filename,
                    'rows': len(df),
                    'columns': len(df.columns),
                    'numeric_columns': len(df.select_dtypes(include=['number']).columns),
                    'missing_values': df.isnull().sum().sum(),
                    'timestamp': datetime.now().isoformat()
                }
                insights.append(insight)
                
            except Exception as e:
                print(f"Error analyzing {filename}: {e}")
    
    # Save insights
    insights_file = os.path.join(upload_dir, 'ai_insights.json')
    import json
    with open(insights_file, 'w') as f:
        json.dump(insights, f, indent=2)
    
    print(f"Generated insights for {len(insights)} files")
    return insights

def cleanup_old_files():
    """Clean up old processed files"""
    upload_dir = '/Users/darshanpatil/Documents/Mern Stack/Refinify/backend/uploads'
    cutoff_time = datetime.now() - timedelta(days=7)  # Keep files for 7 days
    cleaned_count = 0
    
    for filename in os.listdir(upload_dir):
        filepath = os.path.join(upload_dir, filename)
        if os.path.isfile(filepath):
            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            if file_time < cutoff_time and filename.startswith('processed_'):
                try:
                    os.remove(filepath)
                    cleaned_count += 1
                    print(f"Removed old file: {filename}")
                except Exception as e:
                    print(f"Error removing {filename}: {e}")
    
    print(f"Cleaned up {cleaned_count} old files")
    return cleaned_count

# Define tasks
check_uploads_task = PythonOperator(
    task_id='check_data_uploads',
    python_callable=check_data_uploads,
    dag=dag
)

process_data_task = PythonOperator(
    task_id='process_data_files',
    python_callable=process_data_files,
    dag=dag
)

generate_insights_task = PythonOperator(
    task_id='generate_ai_insights',
    python_callable=generate_ai_insights,
    dag=dag
)

cleanup_task = PythonOperator(
    task_id='cleanup_old_files',
    python_callable=cleanup_old_files,
    dag=dag
)

# Health check task
health_check_task = BashOperator(
    task_id='health_check',
    bash_command='curl -f http://localhost:8000/health || exit 1',
    dag=dag
)

# Set task dependencies
check_uploads_task >> process_data_task >> generate_insights_task >> cleanup_task
health_check_task >> check_uploads_task