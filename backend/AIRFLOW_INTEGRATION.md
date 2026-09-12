# Apache Airflow Integration for Refinify-AI

## Overview

This integration brings powerful automation capabilities to Refinify-AI using Apache Airflow, while maintaining a careful balance between automation and accuracy. The system includes:

- **Automated Data Processing Workflows** - Scheduled data cleaning, outlier detection, and typo correction
- **Accuracy Monitoring** - Real-time accuracy tracking with configurable thresholds
- **Safety Mechanisms** - Automatic backups, rollback capabilities, and circuit breakers
- **Quality Control** - Multi-level validation and manual review triggers
- **Monitoring & Alerting** - Email, Slack, and webhook notifications

## 🎯 Key Features

### 1. **Accuracy-First Automation**
- Configurable accuracy thresholds for each task type
- Automatic fallback to manual review when accuracy drops
- Real-time accuracy monitoring and validation
- Disable auto-correction when accuracy is too low

### 2. **Safety & Reliability**
- Automatic backups before major operations
- Rollback capabilities for failed workflows
- Circuit breaker pattern to prevent cascading failures
- Resource monitoring and health checks

gaurav

### 3. **Intelligent Scheduling**
- Configurable intervals for different task types
- Adaptive scheduling based on data volume and complexity
- Resource-aware task distribution
- Performance optimization with caching

## 🚀 Quick Start

### Prerequisites
```bash
# Install Apache Airflow with required providers
pip install apache-airflow[postgres,redis,slack,email]

# Install additional dependencies
pip install psutil schedule croniter
```

### 1. **Setup Airflow**
```bash
cd backend
python airflow_setup.py
```

### 2. **Start Airflow Services**
```bash
# Windows
start_airflow.bat

# Unix/Linux/Mac
./start_airflow.sh

# Manual start
airflow webserver -p 8080 &
airflow scheduler &
```

### 3. **Access Web UI**
- Open: http://localhost:8080
- Username: `admin`
- Password: `admin`

## 📊 Workflow Architecture

### Main Workflow DAG: `refinify_main_workflow`

```
Start → Safety Check → Data Quality Assessment → Accuracy Monitoring
  ↓
Branch Decision (based on accuracy)
  ↓
├─ High Accuracy (≥95%): Continue Processing
├─ Medium Accuracy (80-95%): Manual Review Required
└─ Low Accuracy (<80%): Stop Workflow
```

### Task Types & Accuracy Thresholds

| Task Type | Accuracy Threshold | Action on Low Accuracy |
|-----------|-------------------|------------------------|
| Data Cleaning | 95% | Manual review |
| Outlier Detection | 90% | Manual review |
| Typo Correction | 85% | Disable auto-correction |
| Data Imputation | 92% | Manual review |
| Report Generation | 98% | Manual verification |

## ⚙️ Configuration

### Airflow Configuration (`airflow_config.py`)

```python
# Accuracy thresholds
ACCURACY_THRESHOLDS = {
    'data_cleaning': 0.95,      # 95% accuracy required
    'outlier_detection': 0.90,  # 90% accuracy required
    'typo_correction': 0.85,    # 85% accuracy required
    'data_imputation': 0.92,    # 92% accuracy required
    'report_generation': 0.98   # 98% accuracy required
}

# Quality control parameters
QUALITY_CONTROL = {
    'max_retries': 3,                    # Maximum retries
    'retry_delay': timedelta(minutes=5), # Delay between retries
    'manual_review_threshold': 0.80,     # Below this: manual review
    'auto_correction_limit': 0.70,       # Below this: disable auto-correction
}

# Safety mechanisms
SAFETY_MECHANISMS = {
    'enable_rollback': True,           # Enable automatic rollback
    'backup_before_processing': True,  # Create backup before operations
    'dry_run_mode': False,             # Enable dry run for testing
    'enable_circuit_breaker': True,    # Stop processing if too many failures
}
```

### Environment Variables

```bash
# Database configuration
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_USER=airflow
export POSTGRES_PASSWORD=airflow
export POSTGRES_DB=airflow

# Redis configuration
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_PASSWORD=

# Airflow home
export AIRFLOW_HOME=./airflow
```

## 🔧 Custom Operators

### 1. **DataQualityOperator**
Handles data processing tasks with accuracy monitoring:
- Data cleaning
- Outlier detection
- Typo correction
- Data imputation
- Quality checks
- Report generation

### 2. **AccuracyMonitorOperator**
Monitors task accuracy and triggers alerts:
- Real-time accuracy tracking
- Threshold-based decision making
- Multi-channel alerting (email, Slack, webhooks)
- Action recommendations

### 3. **SafetyCheckOperator**
Ensures system safety and reliability:
- Automatic backups
- System resource monitoring
- Database health checks
- File permission validation
- Circuit breaker management

## 📈 Monitoring & Alerting

### Accuracy Alerts
- **Green (≥95%)**: Continue processing
- **Yellow (80-95%)**: Manual review required
- **Orange (70-80%)**: Stop and review
- **Red (<70%)**: Critical - disable automation

### Alert Channels
1. **Email Alerts**: Detailed reports with recommendations
2. **Slack Notifications**: Real-time updates with severity indicators
3. **Webhook Alerts**: Integration with external monitoring systems

### Alert Content
- Task type and accuracy score
- Threshold comparison
- Required actions
- Recommendations
- Timestamp and workflow ID

## 🛡️ Safety Features

### Automatic Backups
- Database snapshots before processing
- Configuration file backups
- Upload directory preservation
- Metadata tracking

### Rollback Capabilities
- One-click rollback to previous state
- Selective restoration options
- Validation of restored data
- Audit trail maintenance

### Circuit Breaker Pattern
- Automatic failure detection
- Configurable failure thresholds
- Graceful degradation
- Recovery mechanisms

## 📋 Usage Examples

### 1. **Run Workflow Manually**
```bash
# Trigger DAG manually
airflow dags trigger refinify_main_workflow

# Run specific task
airflow tasks test refinify_main_workflow assess_data_quality 2024-01-01
```

### 2. **Monitor Workflow Status**
```bash
# Check DAG status
airflow dags list

# View task instances
airflow tasks list refinify_main_workflow

# Check logs
airflow tasks logs refinify_main_workflow assess_data_quality 2024-01-01
```

### 3. **Customize Accuracy Thresholds**
```python
# Modify thresholds in airflow_config.py
ACCURACY_THRESHOLDS = {
    'data_cleaning': 0.98,      # Increase to 98%
    'typo_correction': 0.90,    # Increase to 90%
}

# Or set via environment variables
export DATA_CLEANING_ACCURACY_THRESHOLD=0.98
export TYPO_CORRECTION_ACCURACY_THRESHOLD=0.90
```

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure Python path includes backend directory
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

2. **Database Connection Issues**
   ```bash
   # Check database status
   airflow db check
   
   # Reset database (WARNING: loses data)
   airflow db reset
   ```

3. **Permission Issues**
   ```bash
   # Check file permissions
   ls -la airflow_dags/
   ls -la airflow_operators/
   
   # Fix permissions
   chmod 755 airflow_dags/ airflow_operators/
   ```

4. **Accuracy Thresholds Not Working**
   ```bash
   # Check configuration
   airflow config get-value core accuracy_thresholds
   
   # Verify operator configuration
   python -c "from airflow_config import AirflowConfig; print(AirflowConfig.ACCURACY_THRESHOLDS)"
   ```

### Debug Mode
```bash
# Enable debug logging
export AIRFLOW__LOGGING__LOGGING_LEVEL=DEBUG

# Run with verbose output
airflow dags test refinify_main_workflow 2024-01-01 --verbose
```

## 📚 Advanced Configuration

### Custom DAGs
Create additional DAGs for specific use cases:

```python
from airflow import DAG
from airflow_operators.data_quality_operator import DataQualityOperator

dag = DAG(
    'custom_workflow',
    schedule_interval='@daily',
    default_args={'owner': 'refinify-ai'}
)

custom_task = DataQualityOperator(
    task_id='custom_processing',
    task_type='data_cleaning',
    batch_size=500,
    accuracy_threshold=0.95,
    dag=dag
)
```

### Custom Operators
Extend existing operators or create new ones:

```python
from airflow_operators.data_quality_operator import DataQualityOperator

class CustomDataOperator(DataQualityOperator):
    def _custom_processing(self, data):
        # Custom processing logic
        return processed_data
    
    def execute(self, context):
        # Custom execution logic
        return super().execute(context)
```

### Performance Tuning
```python
# Optimize for high-volume data
TASK_SETTINGS = {
    'data_cleaning': {
        'batch_size': 5000,        # Larger batches
        'parallel_tasks': 8,       # More parallel tasks
        'timeout': 3600,           # Longer timeout
        'memory_limit': '8GB',     # More memory
    }
}

# Enable caching
PERFORMANCE = {
    'enable_caching': True,
    'cache_ttl': 7200,            # 2 hours cache
    'max_workers': 16,            # More workers
}
```

## 🔐 Security Considerations

### Authentication
- Use strong passwords for admin accounts
- Implement LDAP/AD integration for enterprise use
- Enable SSL/TLS for web interface

### Data Protection
- Encrypt sensitive data in transit and at rest
- Implement role-based access control
- Regular security audits and updates

### Network Security
- Restrict access to Airflow web interface
- Use VPN for remote access
- Implement firewall rules

## 📊 Performance Monitoring

### Metrics to Track
- Task execution time
- Accuracy scores over time
- Resource utilization
- Error rates and types
- Backup sizes and frequency

### Monitoring Tools
- Airflow built-in metrics
- Prometheus integration
- Grafana dashboards
- Custom logging and alerting

## 🚀 Deployment Options

### Local Development
```bash
# Simple local setup
python airflow_setup.py
./start_airflow.sh
```

### Production Deployment
```bash
# Use Docker Compose
docker-compose -f docker-compose.airflow.yml up -d

# Or deploy to cloud platforms
# - AWS ECS/Fargate
# - Google Cloud Run
# - Azure Container Instances
# - Kubernetes clusters
```

### Scaling Considerations
- Use Celery executor for distributed processing
- Implement Redis for task queuing
- Use PostgreSQL for metadata storage
- Consider horizontal scaling for high-volume workloads

## 📞 Support & Community

### Getting Help
1. Check the troubleshooting section above
2. Review Airflow logs for error details
3. Consult Apache Airflow documentation
4. Join the Refinify-AI community

### Contributing
- Report bugs and issues
- Suggest new features
- Contribute code improvements
- Share use cases and examples

## 📄 License

This integration is part of the Refinify-AI project and follows the same licensing terms.

---

**Note**: This integration is designed to balance automation with accuracy. Always review results and adjust thresholds based on your specific use case and data quality requirements.
