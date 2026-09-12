"""
Custom Airflow Operator for Safety Checks
Performs safety checks, creates backups, and enables rollback capabilities
"""

import logging
from typing import Dict, Any, List, Optional
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
import sys
import os
from datetime import datetime
import shutil
import json
import sqlite3
import pandas as pd

# Add backend directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from airflow_config import AirflowConfig

class SafetyCheckOperator(BaseOperator):
    """
    Custom operator for safety checks, backups, and rollback capabilities
    """
    
    @apply_defaults
    def __init__(
        self,
        safety_features: List[str] = None,
        backup_path: str = None,
        enable_rollback: bool = True,
        max_backup_size_gb: int = 10,
        timeout: int = 300,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.safety_features = safety_features or ['backup_before_processing']
        self.backup_path = backup_path or os.path.join(os.getcwd(), 'backups')
        self.enable_rollback = enable_rollback
        self.max_backup_size_gb = max_backup_size_gb
        self.timeout = timeout
        
        # Safety check results
        self.safety_results = {}
        self.backup_created = False
        self.backup_path_created = None
        
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the safety check operation
        """
        start_time = datetime.now()
        self.log.info(f"Starting safety checks with features: {self.safety_features}")
        
        try:
            # Create backup directory if it doesn't exist
            self._ensure_backup_directory()
            
            # Perform safety checks
            safety_status = self._perform_safety_checks()
            
            # Create backups if requested
            if 'backup_before_processing' in self.safety_features:
                backup_status = self._create_backup(context)
                safety_status['backup'] = backup_status
            
            # Check system resources
            if 'resource_check' in self.safety_features:
                resource_status = self._check_system_resources()
                safety_status['resources'] = resource_status
            
            # Check database health
            if 'database_check' in self.safety_features:
                db_status = self._check_database_health()
                safety_status['database'] = db_status
            
            # Check file permissions
            if 'permission_check' in self.safety_features:
                perm_status = self._check_file_permissions()
                safety_status['permissions'] = perm_status
            
            # Store safety results
            self.safety_results = {
                'safety_features': self.safety_features,
                'safety_status': safety_status,
                'backup_created': self.backup_created,
                'backup_path': self.backup_path_created,
                'timestamp': datetime.now().isoformat(),
                'workflow_run_id': context.get('run_id', 'unknown'),
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
            
            # Push results to XCom
            context['task_instance'].xcom_push(
                key='safety_check_results',
                value=self.safety_results
            )
            
            # Check if all safety checks passed
            all_passed = all(
                status.get('status', 'unknown') == 'passed' 
                for status in safety_status.values()
            )
            
            if not all_passed:
                self.log.warning("Some safety checks failed. Review results before proceeding.")
                failed_checks = [
                    feature for feature, status in safety_status.items()
                    if status.get('status') != 'passed'
                ]
                self.log.warning(f"Failed safety checks: {failed_checks}")
            
            # Log results
            self.log.info(f"Safety checks completed in {(datetime.now() - start_time).total_seconds():.2f} seconds")
            self.log.info(f"Overall safety status: {'PASSED' if all_passed else 'FAILED'}")
            
            return self.safety_results
            
        except Exception as e:
            self.log.error(f"Error in safety checks: {str(e)}")
            raise
    
    def _ensure_backup_directory(self) -> None:
        """
        Ensure backup directory exists
        """
        try:
            if not os.path.exists(self.backup_path):
                os.makedirs(self.backup_path, exist_ok=True)
                self.log.info(f"Created backup directory: {self.backup_path}")
            
            # Create timestamped subdirectory for this run
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.backup_path_created = os.path.join(self.backup_path, f"backup_{timestamp}")
            os.makedirs(self.backup_path_created, exist_ok=True)
            
        except Exception as e:
            self.log.error(f"Failed to create backup directory: {e}")
            raise
    
    def _perform_safety_checks(self) -> Dict[str, Any]:
        """
        Perform basic safety checks
        """
        safety_status = {}
        
        # Check if we're in dry run mode
        if AirflowConfig.is_safety_enabled('dry_run_mode'):
            safety_status['dry_run'] = {
                'status': 'passed',
                'message': 'Dry run mode enabled - no actual changes will be made'
            }
        
        # Check if circuit breaker is enabled
        if AirflowConfig.is_safety_enabled('enable_circuit_breaker'):
            circuit_status = self._check_circuit_breaker()
            safety_status['circuit_breaker'] = circuit_status
        
        # Check maximum processing time
        if AirflowConfig.SAFETY_MECHANISMS['max_processing_time']:
            safety_status['processing_time_limit'] = {
                'status': 'passed',
                'message': f"Processing time limit set to {AirflowConfig.SAFETY_MECHANISMS['max_processing_time']} seconds"
            }
        
        return safety_status
    
    def _create_backup(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create backup of critical data and files
        """
        try:
            backup_status = {
                'status': 'unknown',
                'message': '',
                'files_backed_up': [],
                'backup_size_mb': 0
            }
            
            # Backup database
            db_backup_path = os.path.join(self.backup_path_created, 'database')
            os.makedirs(db_backup_path, exist_ok=True)
            
            # Backup SQLite database if it exists
            db_path = os.path.join(os.getcwd(), 'app.db')
            if os.path.exists(db_path):
                db_backup_file = os.path.join(db_backup_path, 'app.db.backup')
                shutil.copy2(db_path, db_backup_file)
                backup_status['files_backed_up'].append('database/app.db.backup')
                self.log.info(f"Database backed up to: {db_backup_file}")
            
            # Backup configuration files
            config_backup_path = os.path.join(self.backup_path_created, 'config')
            os.makedirs(config_backup_path, exist_ok=True)
            
            config_files = ['config.py', 'airflow_config.py']
            for config_file in config_files:
                if os.path.exists(config_file):
                    config_backup_file = os.path.join(config_backup_path, config_file)
                    shutil.copy2(config_file, config_backup_file)
                    backup_status['files_backed_up'].append(f'config/{config_file}')
            
            # Backup uploads directory if it exists
            uploads_path = os.path.join(os.getcwd(), 'uploads')
            if os.path.exists(uploads_path):
                uploads_backup_path = os.path.join(self.backup_path_created, 'uploads')
                shutil.copytree(uploads_path, uploads_backup_path, dirs_exist_ok=True)
                backup_status['files_backed_up'].append('uploads/')
                self.log.info(f"Uploads directory backed up to: {uploads_backup_path}")
            
            # Calculate backup size
            total_size = 0
            for root, dirs, files in os.walk(self.backup_path_created):
                for file in files:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
            
            backup_status['backup_size_mb'] = total_size / (1024 * 1024)
            
            # Check if backup size exceeds limit
            if backup_status['backup_size_mb'] > self.max_backup_size_gb * 1024:
                backup_status['status'] = 'warning'
                backup_status['message'] = f"Backup size ({backup_status['backup_size_mb']:.2f} MB) exceeds limit"
            else:
                backup_status['status'] = 'passed'
                backup_status['message'] = f"Backup created successfully ({backup_status['backup_size_mb']:.2f} MB)"
            
            # Create backup metadata
            backup_metadata = {
                'backup_timestamp': datetime.now().isoformat(),
                'workflow_run_id': context.get('run_id', 'unknown'),
                'files_backed_up': backup_status['files_backed_up'],
                'backup_size_mb': backup_status['backup_size_mb'],
                'backup_path': self.backup_path_created
            }
            
            metadata_file = os.path.join(self.backup_path_created, 'backup_metadata.json')
            with open(metadata_file, 'w') as f:
                json.dump(backup_metadata, f, indent=2)
            
            self.backup_created = True
            self.log.info(f"Backup completed: {backup_status['message']}")
            
            return backup_status
            
        except Exception as e:
            self.log.error(f"Backup creation failed: {e}")
            return {
                'status': 'failed',
                'message': f"Backup creation failed: {str(e)}",
                'files_backed_up': [],
                'backup_size_mb': 0
            }
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """
        Check system resources (memory, disk space, etc.)
        """
        try:
            resource_status = {
                'status': 'unknown',
                'message': '',
                'details': {}
            }
            
            # Check disk space
            disk_usage = shutil.disk_usage(os.getcwd())
            free_gb = disk_usage.free / (1024**3)
            
            if free_gb < 1.0:  # Less than 1 GB free
                resource_status['status'] = 'failed'
                resource_status['message'] = f"Insufficient disk space: {free_gb:.2f} GB free"
            elif free_gb < 5.0:  # Less than 5 GB free
                resource_status['status'] = 'warning'
                resource_status['message'] = f"Low disk space: {free_gb:.2f} GB free"
            else:
                resource_status['status'] = 'passed'
                resource_status['message'] = f"Sufficient disk space: {free_gb:.2f} GB free"
            
            resource_status['details']['disk_free_gb'] = free_gb
            
            # Check memory (basic check)
            try:
                import psutil
                memory = psutil.virtual_memory()
                memory_usage_percent = memory.percent
                
                if memory_usage_percent > 90:
                    resource_status['status'] = 'warning'
                    resource_status['message'] += f", High memory usage: {memory_usage_percent:.1f}%"
                elif memory_usage_percent > 95:
                    resource_status['status'] = 'failed'
                    resource_status['message'] = f"Critical memory usage: {memory_usage_percent:.1f}%"
                
                resource_status['details']['memory_usage_percent'] = memory_usage_percent
                
            except ImportError:
                resource_status['details']['memory_usage_percent'] = 'unknown (psutil not available)'
            
            return resource_status
            
        except Exception as e:
            self.log.error(f"Resource check failed: {e}")
            return {
                'status': 'failed',
                'message': f"Resource check failed: {str(e)}",
                'details': {}
            }
    
    def _check_database_health(self) -> Dict[str, Any]:
        """
        Check database health and connectivity
        """
        try:
            db_status = {
                'status': 'unknown',
                'message': '',
                'details': {}
            }
            
            # Check SQLite database
            db_path = os.path.join(os.getcwd(), 'app.db')
            if os.path.exists(db_path):
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    # Check if we can query the database
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    
                    db_status['details']['tables'] = [table[0] for table in tables]
                    db_status['details']['database_size_mb'] = os.path.getsize(db_path) / (1024 * 1024)
                    
                    # Check for corruption
                    cursor.execute("PRAGMA integrity_check;")
                    integrity_result = cursor.fetchone()
                    
                    if integrity_result and integrity_result[0] == 'ok':
                        db_status['status'] = 'passed'
                        db_status['message'] = f"Database healthy with {len(tables)} tables"
                    else:
                        db_status['status'] = 'failed'
                        db_status['message'] = "Database integrity check failed"
                    
                    conn.close()
                    
                except Exception as e:
                    db_status['status'] = 'failed'
                    db_status['message'] = f"Database connection failed: {str(e)}"
            else:
                db_status['status'] = 'warning'
                db_status['message'] = "Database file not found"
            
            return db_status
            
        except Exception as e:
            self.log.error(f"Database health check failed: {e}")
            return {
                'status': 'failed',
                'message': f"Database health check failed: {str(e)}",
                'details': {}
            }
    
    def _check_file_permissions(self) -> Dict[str, Any]:
        """
        Check file permissions for critical directories
        """
        try:
            perm_status = {
                'status': 'unknown',
                'message': '',
                'details': {}
            }
            
            critical_paths = [
                'uploads',
                'backups',
                'airflow_dags',
                'airflow_operators'
            ]
            
            permission_issues = []
            
            for path in critical_paths:
                if os.path.exists(path):
                    try:
                        # Check if directory is writable
                        test_file = os.path.join(path, '.test_write')
                        with open(test_file, 'w') as f:
                            f.write('test')
                        os.remove(test_file)
                        
                        perm_status['details'][path] = 'writable'
                        
                    except Exception:
                        permission_issues.append(f"{path} (not writable)")
                        perm_status['details'][path] = 'not_writable'
                else:
                    perm_status['details'][path] = 'not_exists'
            
            if permission_issues:
                perm_status['status'] = 'failed'
                perm_status['message'] = f"Permission issues: {', '.join(permission_issues)}"
            else:
                perm_status['status'] = 'passed'
                perm_status['message'] = "All critical paths have proper permissions"
            
            return perm_status
            
        except Exception as e:
            self.log.error(f"Permission check failed: {e}")
            return {
                'status': 'failed',
                'message': f"Permission check failed: {str(e)}",
                'details': {}
            }
    
    def _check_circuit_breaker(self) -> Dict[str, Any]:
        """
        Check circuit breaker status
        """
        try:
            circuit_status = {
                'status': 'unknown',
                'message': '',
                'details': {}
            }
            
            # Check for recent failures
            failure_file = os.path.join(os.getcwd(), '.circuit_breaker_failures')
            
            if os.path.exists(failure_file):
                try:
                    with open(failure_file, 'r') as f:
                        failure_count = int(f.read().strip())
                    
                    threshold = AirflowConfig.SAFETY_MECHANISMS['circuit_breaker_threshold']
                    
                    if failure_count >= threshold:
                        circuit_status['status'] = 'failed'
                        circuit_status['message'] = f"Circuit breaker triggered: {failure_count} failures >= {threshold}"
                        circuit_status['details']['failure_count'] = failure_count
                        circuit_status['details']['threshold'] = threshold
                    else:
                        circuit_status['status'] = 'warning'
                        circuit_status['message'] = f"Circuit breaker warning: {failure_count}/{threshold} failures"
                        circuit_status['details']['failure_count'] = failure_count
                        circuit_status['details']['threshold'] = threshold
                        
                except Exception:
                    circuit_status['status'] = 'warning'
                    circuit_status['message'] = "Could not read circuit breaker status"
            else:
                circuit_status['status'] = 'passed'
                circuit_status['message'] = "Circuit breaker not triggered"
                circuit_status['details']['failure_count'] = 0
            
            return circuit_status
            
        except Exception as e:
            self.log.error(f"Circuit breaker check failed: {e}")
            return {
                'status': 'failed',
                'message': f"Circuit breaker check failed: {str(e)}",
                'details': {}
            }
    
    def rollback(self, context: Dict[str, Any]) -> bool:
        """
        Rollback to previous state using backup
        """
        try:
            if not self.backup_created or not self.backup_path_created:
                self.log.warning("No backup available for rollback")
                return False
            
            self.log.info(f"Starting rollback from backup: {self.backup_path_created}")
            
            # Restore database
            db_backup = os.path.join(self.backup_path_created, 'database', 'app.db.backup')
            if os.path.exists(db_backup):
                db_path = os.path.join(os.getcwd(), 'app.db')
                shutil.copy2(db_backup, db_path)
                self.log.info("Database restored from backup")
            
            # Restore configuration files
            config_backup_path = os.path.join(self.backup_path_created, 'config')
            if os.path.exists(config_backup_path):
                for config_file in os.listdir(config_backup_path):
                    if config_file.endswith('.py'):
                        src = os.path.join(config_backup_path, config_file)
                        dst = os.path.join(os.getcwd(), config_file)
                        shutil.copy2(src, dst)
                        self.log.info(f"Configuration file restored: {config_file}")
            
            # Restore uploads if they exist
            uploads_backup = os.path.join(self.backup_path_created, 'uploads')
            if os.path.exists(uploads_backup):
                uploads_path = os.path.join(os.getcwd(), 'uploads')
                if os.path.exists(uploads_path):
                    shutil.rmtree(uploads_path)
                shutil.copytree(uploads_backup, uploads_path)
                self.log.info("Uploads directory restored from backup")
            
            self.log.info("Rollback completed successfully")
            return True
            
        except Exception as e:
            self.log.error(f"Rollback failed: {e}")
            return False
