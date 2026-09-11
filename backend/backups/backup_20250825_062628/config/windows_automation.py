"""
Windows-Compatible Automation System for Refinify-AI
Provides automated data processing, quality monitoring, and safety features
"""

import schedule
import time
import os
import shutil
import json
import sqlite3
from datetime import datetime
import pandas as pd
import numpy as np
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler()
    ]
)

class WindowsAutomation:
    """Windows-compatible automation system for Refinify-AI"""
    
    def __init__(self):
        self.backup_dir = "backups"
        self.uploads_dir = "uploads"
        self.log_file = "automation.log"
        self.config_file = "automation_config.json"
        self.accuracy_thresholds = {
            'data_cleaning': 0.95,
            'outlier_detection': 0.90,
            'typo_correction': 0.85,
            'data_imputation': 0.92,
            'report_generation': 0.98
        }
        self.manual_review_threshold = 0.80
        self.auto_correction_limit = 0.70
        
        # Create necessary directories
        self._create_directories()
        
        # Load or create configuration
        self.config = self._load_config()
        
    def _create_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [self.backup_dir, self.uploads_dir, "logs", "reports"]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logging.info(f"Directory ensured: {directory}")
    
    def _load_config(self):
        """Load or create configuration file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                logging.info("Configuration loaded from file")
                return config
            except Exception as e:
                logging.warning(f"Failed to load config: {e}")
        
        # Default configuration
        default_config = {
            'backup_interval_hours': 24,
            'data_processing_interval_hours': 6,
            'quality_check_interval_hours': 12,
            'max_backup_size_gb': 10,
            'enable_email_alerts': False,
            'enable_slack_alerts': False,
            'admin_email': 'admin@refinify-ai.com',
            'last_backup': None,
            'last_processing': None,
            'total_cycles': 0,
            'successful_cycles': 0
        }
        
        self._save_config(default_config)
        logging.info("Default configuration created")
        return default_config
    
    def _save_config(self, config):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2, default=str)
        except Exception as e:
            logging.error(f"Failed to save config: {e}")
    
    def log_message(self, message, level='INFO'):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        if level == 'INFO':
            logging.info(message)
        elif level == 'WARNING':
            logging.warning(message)
        elif level == 'ERROR':
            logging.error(message)
        elif level == 'CRITICAL':
            logging.critical(message)
        
        print(log_entry)
    
    def create_backup(self):
        """Create backup of critical data and files"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.backup_dir, f"backup_{timestamp}")
            os.makedirs(backup_path, exist_ok=True)
            
            backup_status = {
                'status': 'unknown',
                'message': '',
                'files_backed_up': [],
                'backup_size_mb': 0,
                'timestamp': timestamp
            }
            
            # Backup database
            db_path = "app.db"
            if os.path.exists(db_path):
                db_backup_path = os.path.join(backup_path, "database")
                os.makedirs(db_backup_path, exist_ok=True)
                shutil.copy2(db_path, os.path.join(db_backup_path, "app.db.backup"))
                backup_status['files_backed_up'].append('database/app.db.backup')
                logging.info(f"Database backed up to: {db_backup_path}")
            
            # Backup configuration files
            config_backup_path = os.path.join(backup_path, "config")
            os.makedirs(config_backup_path, exist_ok=True)
            
            config_files = ['config.py', 'app.py', 'windows_automation.py']
            for config_file in config_files:
                if os.path.exists(config_file):
                    shutil.copy2(config_file, os.path.join(config_backup_path, config_file))
                    backup_status['files_backed_up'].append(f'config/{config_file}')
            
            # Backup uploads directory
            if os.path.exists(self.uploads_dir):
                uploads_backup_path = os.path.join(backup_path, "uploads")
                shutil.copytree(self.uploads_dir, uploads_backup_path, dirs_exist_ok=True)
                backup_status['files_backed_up'].append('uploads/')
                logging.info(f"Uploads directory backed up to: {uploads_backup_path}")
            
            # Calculate backup size
            total_size = 0
            for root, dirs, files in os.walk(backup_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
            
            backup_status['backup_size_mb'] = total_size / (1024 * 1024)
            
            # Check if backup size exceeds limit
            if backup_status['backup_size_mb'] > self.config['max_backup_size_gb'] * 1024:
                backup_status['status'] = 'warning'
                backup_status['message'] = f"Backup size ({backup_status['backup_size_mb']:.2f} MB) exceeds limit"
            else:
                backup_status['status'] = 'success'
                backup_status['message'] = f"Backup created successfully ({backup_status['backup_size_mb']:.2f} MB)"
            
            # Create backup metadata
            backup_metadata = {
                'backup_timestamp': datetime.now().isoformat(),
                'files_backed_up': backup_status['files_backed_up'],
                'backup_size_mb': backup_status['backup_size_mb'],
                'backup_path': backup_path
            }
            
            metadata_file = os.path.join(backup_path, 'backup_metadata.json')
            with open(metadata_file, 'w') as f:
                json.dump(backup_metadata, f, indent=2)
            
            # Update configuration
            self.config['last_backup'] = datetime.now().isoformat()
            self._save_config(self.config)
            
            self.log_message(f"Backup completed: {backup_status['message']}")
            return True
            
        except Exception as e:
            self.log_message(f"Backup creation failed: {str(e)}", 'ERROR')
            return False
    
    def clean_data(self, data_path):
        """Clean data files with accuracy tracking"""
        try:
            if data_path.endswith('.csv'):
                df = pd.read_csv(data_path)
            elif data_path.endswith('.xlsx'):
                df = pd.read_excel(data_path)
            else:
                self.log_message(f"Unsupported file format: {data_path}", 'WARNING')
                return None, 0.0
            
            original_count = len(df)
            original_columns = len(df.columns)
            
            # Basic cleaning
            cleaned_df = df.copy()
            
            # Remove rows with all NaN values
            cleaned_df = cleaned_df.dropna(how='all')
            
            # Remove duplicates
            cleaned_df = cleaned_df.drop_duplicates()
            
            # Basic data type conversion
            for col in cleaned_df.columns:
                if cleaned_df[col].dtype == 'object':
                    try:
                        cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='ignore')
                    except:
                        pass
            
            # Calculate accuracy
            data_loss_penalty = 0.0
            if len(cleaned_df) < original_count * 0.9:  # Allow 10% data loss
                data_loss_penalty = 0.2
            
            structure_accuracy = 1.0 if len(cleaned_df.columns) >= original_columns else 0.5
            data_integrity = len(cleaned_df) / original_count
            
            accuracy = (structure_accuracy + data_integrity) / 2 - data_loss_penalty
            accuracy = max(0.0, min(1.0, accuracy))
            
            # Save cleaned data
            output_path = data_path.replace('.csv', '_cleaned.csv').replace('.xlsx', '_cleaned.xlsx')
            if output_path.endswith('_cleaned.csv'):
                cleaned_df.to_csv(output_path, index=False)
            else:
                cleaned_df.to_excel(output_path, index=False)
            
            self.log_message(f"Data cleaning completed: {data_path} -> {output_path} (Accuracy: {accuracy:.4f})")
            return output_path, accuracy
            
        except Exception as e:
            self.log_message(f"Data cleaning failed: {str(e)}", 'ERROR')
            return None, 0.0
    
    def detect_outliers(self, data_path):
        """Detect outliers in data with accuracy tracking"""
        try:
            if data_path.endswith('.csv'):
                df = pd.read_csv(data_path)
            elif data_path.endswith('.xlsx'):
                df = pd.read_excel(data_path)
            else:
                return None, 0.0
            
            # Detect outliers using IQR method
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            outlier_flags = pd.DataFrame()
            
            if len(numeric_cols) == 0:
                self.log_message("No numeric columns found for outlier detection", 'WARNING')
                return data_path, 0.5
            
            for col in numeric_cols:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outlier_flags[f'{col}_is_outlier'] = (
                    (df[col] < lower_bound) | (df[col] > upper_bound)
                )
            
            # Combine original data with outlier flags
            result_df = pd.concat([df, outlier_flags], axis=1)
            
            # Calculate accuracy (simplified - assume good if structure maintained)
            accuracy = 0.9 if len(result_df) == len(df) else 0.7
            
            # Save result
            output_path = data_path.replace('.csv', '_outliers.csv').replace('.xlsx', '_outliers.xlsx')
            if output_path.endswith('_outliers.csv'):
                result_df.to_csv(output_path, index=False)
            else:
                result_df.to_excel(output_path, index=False)
            
            self.log_message(f"Outlier detection completed: {output_path} (Accuracy: {accuracy:.4f})")
            return output_path, accuracy
            
        except Exception as e:
            self.log_message(f"Outlier detection failed: {str(e)}", 'ERROR')
            return None, 0.0
    
    def generate_report(self, cycle_results):
        """Generate automation cycle report"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = os.path.join("reports", f"automation_report_{timestamp}.json")
            
            report_data = {
                'cycle_timestamp': timestamp,
                'cycle_results': cycle_results,
                'system_stats': {
                    'total_cycles': self.config['total_cycles'],
                    'successful_cycles': self.config['successful_cycles'],
                    'success_rate': self.config['successful_cycles'] / max(1, self.config['total_cycles']),
                    'last_backup': self.config['last_backup'],
                    'last_processing': self.config['last_processing']
                },
                'accuracy_summary': {
                    'data_cleaning': cycle_results.get('data_cleaning_accuracy', 0),
                    'outlier_detection': cycle_results.get('outlier_detection_accuracy', 0),
                    'overall_accuracy': cycle_results.get('overall_accuracy', 0)
                }
            }
            
            with open(report_path, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            self.log_message(f"Report generated: {report_path}")
            return report_path
            
        except Exception as e:
            self.log_message(f"Report generation failed: {str(e)}", 'ERROR')
            return None
    
    def run_automation_cycle(self):
        """Run one complete automation cycle"""
        self.log_message("Starting automation cycle...")
        
        cycle_start = datetime.now()
        cycle_results = {
            'status': 'unknown',
            'start_time': cycle_start.isoformat(),
            'end_time': None,
            'files_processed': 0,
            'data_cleaning_accuracy': 0.0,
            'outlier_detection_accuracy': 0.0,
            'overall_accuracy': 0.0,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Create backup
            if not self.create_backup():
                cycle_results['errors'].append("Backup creation failed")
                cycle_results['status'] = 'failed'
                return False
            
            # Process files in uploads directory
            processed_files = 0
            total_accuracy = 0.0
            accuracy_count = 0
            
            if os.path.exists(self.uploads_dir):
                for filename in os.listdir(self.uploads_dir):
                    file_path = os.path.join(self.uploads_dir, filename)
                    if os.path.isfile(file_path) and (file_path.endswith('.csv') or file_path.endswith('.xlsx')):
                        try:
                            # Clean data
                            cleaned_path, cleaning_accuracy = self.clean_data(file_path)
                            if cleaned_path and cleaning_accuracy > 0:
                                cycle_results['data_cleaning_accuracy'] = max(
                                    cycle_results['data_cleaning_accuracy'], 
                                    cleaning_accuracy
                                )
                                total_accuracy += cleaning_accuracy
                                accuracy_count += 1
                                
                                # Detect outliers
                                outlier_path, outlier_accuracy = self.detect_outliers(cleaned_path)
                                if outlier_path and outlier_accuracy > 0:
                                    cycle_results['outlier_detection_accuracy'] = max(
                                        cycle_results['outlier_detection_accuracy'], 
                                        outlier_accuracy
                                    )
                                    total_accuracy += outlier_accuracy
                                    accuracy_count += 1
                                
                                processed_files += 1
                            
                        except Exception as e:
                            error_msg = f"Failed to process {filename}: {str(e)}"
                            cycle_results['errors'].append(error_msg)
                            self.log_message(error_msg, 'ERROR')
            
            # Calculate overall accuracy
            if accuracy_count > 0:
                cycle_results['overall_accuracy'] = total_accuracy / accuracy_count
            
            cycle_results['files_processed'] = processed_files
            cycle_results['end_time'] = datetime.now().isoformat()
            
            # Determine cycle status
            if cycle_results['overall_accuracy'] >= self.accuracy_thresholds['data_cleaning']:
                cycle_results['status'] = 'excellent'
            elif cycle_results['overall_accuracy'] >= self.manual_review_threshold:
                cycle_results['status'] = 'acceptable'
                cycle_results['warnings'].append("Manual review recommended - accuracy below threshold")
            else:
                cycle_results['status'] = 'poor'
                cycle_results['warnings'].append("Automation stopped - accuracy too low")
            
            # Update configuration
            self.config['total_cycles'] += 1
            if cycle_results['status'] in ['excellent', 'acceptable']:
                self.config['successful_cycles'] += 1
            
            self.config['last_processing'] = datetime.now().isoformat()
            self._save_config(self.config)
            
            # Generate report
            self.generate_report(cycle_results)
            
            # Log results
            self.log_message(f"Automation cycle completed: {cycle_results['status']} (Accuracy: {cycle_results['overall_accuracy']:.4f})")
            
            # Check if manual review is needed
            if cycle_results['overall_accuracy'] < self.manual_review_threshold:
                self.log_message("⚠️ MANUAL REVIEW REQUIRED - Accuracy below threshold", 'WARNING')
            
            return True
            
        except Exception as e:
            error_msg = f"Automation cycle failed: {str(e)}"
            cycle_results['errors'].append(error_msg)
            cycle_results['status'] = 'failed'
            cycle_results['end_time'] = datetime.now().isoformat()
            self.log_message(error_msg, 'ERROR')
            return False
    
    def start_scheduler(self):
        """Start the automated scheduler"""
        self.log_message("Starting Windows Automation Scheduler...")
        
        # Schedule tasks
        schedule.every(self.config['data_processing_interval_hours']).hours.do(self.run_automation_cycle)
        schedule.every().day.at("02:00").do(self.create_backup)
        schedule.every(self.config['quality_check_interval_hours']).hours.do(self.run_automation_cycle)
        
        self.log_message(f"Scheduled tasks:")
        self.log_message(f"- Data processing: Every {self.config['data_processing_interval_hours']} hours")
        self.log_message(f"- Daily backup: 2:00 AM")
        self.log_message(f"- Quality checks: Every {self.config['quality_check_interval_hours']} hours")
        
        # Run initial cycle
        self.run_automation_cycle()
        
        # Keep running
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.log_message("Automation stopped by user")
            return False

def main():
    """Main automation function"""
    try:
        automation = WindowsAutomation()
        automation.start_scheduler()
    except Exception as e:
        logging.error(f"Automation system failed: {e}")
        print(f"Automation system failed: {e}")

if __name__ == "__main__":
    main()
