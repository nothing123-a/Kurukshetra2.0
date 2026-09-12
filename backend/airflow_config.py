"""
Apache Airflow Configuration for Refinify-AI
Balancing automation with accuracy through configurable parameters
"""

import os
from datetime import timedelta

class AirflowConfig:
    """Airflow-specific configuration for Refinify-AI automation"""
    
    # Core Airflow Settings
    AIRFLOW_HOME = os.environ.get('AIRFLOW_HOME', './airflow')
    AIRFLOW_DB_CONN_ID = 'refinify_postgres'
    AIRFLOW_EMAIL_CONN_ID = 'refinify_email'
    AIRFLOW_SLACK_CONN_ID = 'refinify_slack'
    
    # Database Configuration
    POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = os.environ.get('POSTGRES_PORT', '5432')
    POSTGRES_USER = os.environ.get('POSTGRES_USER', 'airflow')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'airflow')
    POSTGRES_DB = os.environ.get('POSTGRES_DB', 'airflow')
    
    # Redis Configuration (for Celery)
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = os.environ.get('REDIS_PORT', '6379')
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', '')
    
    # Automation Accuracy Settings
    ACCURACY_THRESHOLDS = {
        'data_cleaning': 0.95,      # 95% accuracy required for data cleaning
        'outlier_detection': 0.90,  # 90% accuracy for outlier detection
        'typo_correction': 0.85,    # 85% accuracy for typo correction
        'data_imputation': 0.92,    # 92% accuracy for missing value imputation
        'report_generation': 0.98   # 98% accuracy for report generation
    }
    
    # Quality Control Parameters
    QUALITY_CONTROL = {
        'max_retries': 3,           # Maximum retries for failed tasks
        'retry_delay': timedelta(minutes=5),  # Delay between retries
        'validation_timeout': 300,   # Timeout for validation tasks (seconds)
        'manual_review_threshold': 0.80,  # Below this accuracy, require manual review
        'auto_correction_limit': 0.70,     # Below this accuracy, disable auto-correction
    }
    
    # Scheduling Configuration
    SCHEDULING = {
        'data_cleaning_interval': '0 */6 * * *',      # Every 6 hours
        'outlier_detection_interval': '0 */4 * * *',  # Every 4 hours
        'typo_correction_interval': '0 */2 * * *',    # Every 2 hours
        'report_generation_interval': '0 9 * * 1',    # Every Monday at 9 AM
        'quality_check_interval': '0 */12 * * *',     # Every 12 hours
        'backup_interval': '0 2 * * *',               # Daily at 2 AM
    }
    
    # Monitoring and Alerting
    MONITORING = {
        'enable_slack_alerts': True,
        'enable_email_alerts': True,
        'enable_webhook_alerts': False,
        'alert_on_accuracy_below': 0.85,
        'alert_on_task_failure': True,
        'alert_on_long_running_tasks': True,
        'long_running_threshold': timedelta(hours=2),
    }
    
    # Task-Specific Settings
    TASK_SETTINGS = {
        'data_cleaning': {
            'batch_size': 1000,
            'parallel_tasks': 4,
            'timeout': 1800,  # 30 minutes
            'memory_limit': '2GB',
        },
        'outlier_detection': {
            'batch_size': 500,
            'parallel_tasks': 2,
            'timeout': 1200,  # 20 minutes
            'memory_limit': '4GB',
        },
        'typo_correction': {
            'batch_size': 200,
            'parallel_tasks': 1,  # Single task for accuracy
            'timeout': 900,   # 15 minutes
            'memory_limit': '6GB',
        },
        'data_imputation': {
            'batch_size': 800,
            'parallel_tasks': 3,
            'timeout': 1500,  # 25 minutes
            'memory_limit': '3GB',
        },
    }
    
    # Fallback and Safety Mechanisms
    SAFETY_MECHANISMS = {
        'enable_rollback': True,           # Enable automatic rollback on failure
        'backup_before_processing': True,  # Create backup before major operations
        'dry_run_mode': False,             # Enable dry run for testing
        'max_processing_time': 7200,       # Maximum total processing time (2 hours)
        'enable_circuit_breaker': True,    # Stop processing if too many failures
        'circuit_breaker_threshold': 5,    # Number of failures before circuit breaker
    }
    
    # Performance Optimization
    PERFORMANCE = {
        'enable_caching': True,
        'cache_ttl': 3600,                # Cache TTL in seconds
        'enable_parallel_processing': True,
        'max_workers': 8,
        'enable_resource_monitoring': True,
        'resource_check_interval': 60,    # Check resources every minute
    }
    
    @staticmethod
    def get_database_url():
        """Get PostgreSQL connection string for Airflow"""
        return f"postgresql://{AirflowConfig.POSTGRES_USER}:{AirflowConfig.POSTGRES_PASSWORD}@{AirflowConfig.POSTGRES_HOST}:{AirflowConfig.POSTGRES_PORT}/{AirflowConfig.POSTGRES_DB}"
    
    @staticmethod
    def get_redis_url():
        """Get Redis connection string for Celery"""
        if AirflowConfig.REDIS_PASSWORD:
            return f"redis://:{AirflowConfig.REDIS_PASSWORD}@{AirflowConfig.REDIS_HOST}:{AirflowConfig.REDIS_PORT}/0"
        return f"redis://{AirflowConfig.REDIS_HOST}:{AirflowConfig.REDIS_PORT}/0"
    
    @staticmethod
    def get_accuracy_threshold(task_type):
        """Get accuracy threshold for a specific task type"""
        return AirflowConfig.ACCURACY_THRESHOLDS.get(task_type, 0.90)
    
    @staticmethod
    def should_require_manual_review(accuracy, task_type):
        """Determine if manual review is required based on accuracy"""
        threshold = AirflowConfig.ACCURACY_THRESHOLDS.get(task_type, 0.90)
        manual_review_threshold = AirflowConfig.QUALITY_CONTROL['manual_review_threshold']
        return accuracy < max(threshold, manual_review_threshold)
    
    @staticmethod
    def get_task_config(task_type):
        """Get configuration for a specific task type"""
        return AirflowConfig.TASK_SETTINGS.get(task_type, {})
    
    @staticmethod
    def is_safety_enabled(safety_feature):
        """Check if a specific safety feature is enabled"""
        return AirflowConfig.SAFETY_MECHANISMS.get(safety_feature, False)
