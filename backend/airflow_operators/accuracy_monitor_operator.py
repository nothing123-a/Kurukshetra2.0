"""
Custom Airflow Operator for Accuracy Monitoring
Monitors task accuracy and triggers alerts when thresholds are not met
"""

import logging
from typing import Dict, Any, Optional
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from airflow.operators.email import EmailOperator
from airflow.models import Variable
import sys
import os
from datetime import datetime
import json

# Add backend directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from airflow_config import AirflowConfig

class AccuracyMonitorOperator(BaseOperator):
    """
    Custom operator for monitoring task accuracy and triggering alerts
    """
    
    @apply_defaults
    def __init__(
        self,
        task_type: str,
        accuracy_threshold: float = 0.90,
        manual_review_threshold: float = 0.80,
        enable_alerts: bool = True,
        alert_channels: list = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.task_type = task_type
        self.accuracy_threshold = accuracy_threshold
        self.manual_review_threshold = manual_review_threshold
        self.enable_alerts = enable_alerts
        self.alert_channels = alert_channels or ['email', 'slack']
        
        # Results storage
        self.monitoring_results = {}
        self.alert_triggered = False
        
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the accuracy monitoring operation
        """
        self.log.info(f"Starting accuracy monitoring for {self.task_type}")
        
        try:
            # Get accuracy from upstream task
            accuracy = self._get_upstream_accuracy(context)
            
            if accuracy is None:
                self.log.warning("No accuracy data found from upstream task")
                accuracy = 0.0
            
            # Analyze accuracy and determine action
            analysis_result = self._analyze_accuracy(accuracy)
            
            # Store monitoring results
            self.monitoring_results = {
                'task_type': self.task_type,
                'accuracy': accuracy,
                'accuracy_threshold': self.accuracy_threshold,
                'manual_review_threshold': self.manual_review_threshold,
                'status': analysis_result['status'],
                'action_required': analysis_result['action_required'],
                'timestamp': datetime.now().isoformat(),
                'workflow_run_id': context.get('run_id', 'unknown')
            }
            
            # Push results to XCom
            context['task_instance'].xcom_push(
                key='accuracy',
                value=accuracy
            )
            
            context['task_instance'].xcom_push(
                key='monitoring_results',
                value=self.monitoring_results
            )
            
            # Trigger alerts if enabled and needed
            if self.enable_alerts and analysis_result['alert_needed']:
                self._trigger_alerts(analysis_result, context)
            
            # Log results
            self.log.info(f"Accuracy monitoring completed for {self.task_type}: {accuracy:.4f}")
            self.log.info(f"Status: {analysis_result['status']}, Action: {analysis_result['action_required']}")
            
            return self.monitoring_results
            
        except Exception as e:
            self.log.error(f"Error in accuracy monitoring for {self.task_type}: {str(e)}")
            raise
    
    def _get_upstream_accuracy(self, context: Dict[str, Any]) -> Optional[float]:
        """
        Get accuracy from upstream task
        """
        try:
            ti = context['task_instance']
            
            # Try to get accuracy from immediate upstream task
            upstream_accuracy = ti.xcom_pull(task_ids=None, key='accuracy')
            
            if upstream_accuracy is not None:
                return float(upstream_accuracy)
            
            # Try to get from specific task results
            upstream_results = ti.xcom_pull(task_ids=None, key=f'{self.task_type}_results')
            
            if upstream_results and 'accuracy' in upstream_results:
                return float(upstream_results['accuracy'])
            
            # Try to get from any task with accuracy
            all_results = ti.xcom_pull(task_ids=None)
            for task_id, result in all_results.items():
                if isinstance(result, dict) and 'accuracy' in result:
                    return float(result['accuracy'])
            
            return None
            
        except Exception as e:
            self.log.warning(f"Could not retrieve upstream accuracy: {e}")
            return None
    
    def _analyze_accuracy(self, accuracy: float) -> Dict[str, Any]:
        """
        Analyze accuracy and determine required actions
        """
        analysis = {
            'status': 'unknown',
            'action_required': 'none',
            'alert_needed': False,
            'severity': 'low'
        }
        
        # Determine status based on accuracy thresholds
        if accuracy >= self.accuracy_threshold:
            analysis['status'] = 'excellent'
            analysis['action_required'] = 'continue'
            analysis['alert_needed'] = False
            analysis['severity'] = 'low'
            
        elif accuracy >= self.manual_review_threshold:
            analysis['status'] = 'acceptable'
            analysis['action_required'] = 'manual_review'
            analysis['alert_needed'] = True
            analysis['severity'] = 'medium'
            
        else:
            analysis['status'] = 'poor'
            analysis['action_required'] = 'stop_and_review'
            analysis['alert_needed'] = True
            analysis['severity'] = 'high'
        
        # Additional analysis for specific task types
        if self.task_type == 'typo_correction' and accuracy < 0.85:
            analysis['action_required'] = 'disable_auto_correction'
            analysis['alert_needed'] = True
            analysis['severity'] = 'critical'
            
        elif self.task_type == 'report_generation' and accuracy < 0.95:
            analysis['action_required'] = 'manual_verification'
            analysis['alert_needed'] = True
            analysis['severity'] = 'high'
        
        return analysis
    
    def _trigger_alerts(self, analysis_result: Dict[str, Any], context: Dict[str, Any]) -> None:
        """
        Trigger alerts based on analysis results
        """
        try:
            self.log.info(f"Triggering alerts for {self.task_type} with severity {analysis_result['severity']}")
            
            # Prepare alert message
            alert_message = self._prepare_alert_message(analysis_result)
            
            # Send email alerts
            if 'email' in self.alert_channels and AirflowConfig.MONITORING['enable_email_alerts']:
                self._send_email_alert(alert_message, analysis_result, context)
            
            # Send Slack alerts
            if 'slack' in self.alert_channels and AirflowConfig.MONITORING['enable_slack_alerts']:
                self._send_slack_alert(alert_message, analysis_result, context)
            
            # Send webhook alerts
            if 'webhook' in self.alert_channels and AirflowConfig.MONITORING['enable_webhook_alerts']:
                self._send_webhook_alert(alert_message, analysis_result, context)
            
            self.alert_triggered = True
            
        except Exception as e:
            self.log.error(f"Failed to trigger alerts: {e}")
    
    def _prepare_alert_message(self, analysis_result: Dict[str, Any]) -> str:
        """
        Prepare alert message based on analysis results
        """
        severity_emoji = {
            'low': '🟢',
            'medium': '🟡',
            'high': '🟠',
            'critical': '🔴'
        }
        
        emoji = severity_emoji.get(analysis_result['severity'], '⚪')
        
        message = f"""
{emoji} *Refinify-AI Accuracy Alert*

*Task Type:* {self.task_type}
*Accuracy:* {self.monitoring_results['accuracy']:.4f}
*Threshold:* {self.accuracy_threshold:.4f}
*Status:* {analysis_result['status'].title()}
*Action Required:* {analysis_result['action_required'].replace('_', ' ').title()}
*Severity:* {analysis_result['severity'].title()}
*Timestamp:* {self.monitoring_results['timestamp']}

*Recommendations:*
"""
        
        if analysis_result['action_required'] == 'manual_review':
            message += "• Review the processed data manually\n• Check for data quality issues\n• Consider adjusting processing parameters"
        elif analysis_result['action_required'] == 'stop_and_review':
            message += "• Stop the workflow immediately\n• Investigate the root cause\n• Review data source quality\n• Consider manual intervention"
        elif analysis_result['action_required'] == 'disable_auto_correction':
            message += "• Disable automatic typo correction\n• Switch to manual review mode\n• Investigate model performance"
        elif analysis_result['action_required'] == 'manual_verification':
            message += "• Manually verify generated reports\n• Check for formatting issues\n• Validate data accuracy"
        
        return message
    
    def _send_email_alert(self, message: str, analysis_result: Dict[str, Any], context: Dict[str, Any]) -> None:
        """
        Send email alert
        """
        try:
            admin_email = Variable.get('admin_email', 'admin@refinify-ai.com')
            
            email_operator = EmailOperator(
                task_id=f'accuracy_alert_email_{self.task_type}',
                to=admin_email,
                subject=f"Refinify-AI Accuracy Alert: {self.task_type} - {analysis_result['severity'].title()}",
                html_content=message.replace('\n', '<br>'),
                dag=context['dag']
            )
            
            # Execute email operator
            email_operator.execute(context)
            self.log.info(f"Email alert sent to {admin_email}")
            
        except Exception as e:
            self.log.error(f"Failed to send email alert: {e}")
    
    def _send_slack_alert(self, message: str, analysis_result: Dict[str, Any], context: Dict[str, Any]) -> None:
        """
        Send Slack alert
        """
        try:
            slack_operator = SlackWebhookOperator(
                task_id=f'accuracy_alert_slack_{self.task_type}',
                webhook_conn_id=AirflowConfig.AIRFLOW_SLACK_CONN_ID,
                message=message,
                dag=context['dag']
            )
            
            # Execute Slack operator
            slack_operator.execute(context)
            self.log.info("Slack alert sent")
            
        except Exception as e:
            self.log.error(f"Failed to send Slack alert: {e}")
    
    def _send_webhook_alert(self, message: str, analysis_result: Dict[str, Any], context: Dict[str, Any]) -> None:
        """
        Send webhook alert
        """
        try:
            # This would be implemented based on your webhook configuration
            self.log.info("Webhook alert would be sent here")
            
        except Exception as e:
            self.log.error(f"Failed to send webhook alert: {e}")
    
    def _should_require_manual_review(self, accuracy: float) -> bool:
        """
        Determine if manual review is required
        """
        return AirflowConfig.should_require_manual_review(accuracy, self.task_type)
    
    def _get_accuracy_threshold(self) -> float:
        """
        Get accuracy threshold for the task type
        """
        return AirflowConfig.get_accuracy_threshold(self.task_type)
