"""
Custom Airflow Operator for Data Quality Operations
Handles data cleaning, outlier detection, typo correction, and imputation with accuracy tracking
"""

import logging
from typing import Dict, Any, Optional
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime
import json

# Add backend directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from airflow_config import AirflowConfig
from data_analyzer import DataAnalyzer
from data_augmenter import DataAugmenter
from enhanced_typo_correction import EnhancedTypoCorrection

class DataQualityOperator(BaseOperator):
    """
    Custom operator for data quality operations with accuracy monitoring
    """
    
    @apply_defaults
    def __init__(
        self,
        task_type: str,
        batch_size: int = 1000,
        timeout: int = 1800,
        accuracy_threshold: float = 0.90,
        enable_validation: bool = True,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.task_type = task_type
        self.batch_size = batch_size
        self.timeout = timeout
        self.accuracy_threshold = accuracy_threshold
        self.enable_validation = enable_validation
        
        # Initialize components
        self.data_analyzer = DataAnalyzer()
        self.data_augmenter = DataAugmenter()
        self.typo_corrector = EnhancedTypoCorrection()
        
        # Results storage
        self.results = {}
        self.accuracy_metrics = {}
        self.processing_time = 0
        
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the data quality operation
        """
        start_time = datetime.now()
        self.log.info(f"Starting {self.task_type} operation with batch size {self.batch_size}")
        
        try:
            # Load data from previous task or from source
            data = self._load_data(context)
            
            if data is None or data.empty:
                self.log.warning("No data to process")
                return self._create_result_dict(accuracy=0.0, status="no_data")
            
            # Process data based on task type
            if self.task_type == 'data_cleaning':
                processed_data = self._clean_data(data)
            elif self.task_type == 'outlier_detection':
                processed_data = self._detect_outliers(data)
            elif self.task_type == 'typo_correction':
                processed_data = self._correct_typos(data)
            elif self.task_type == 'data_imputation':
                processed_data = self._impute_data(data)
            elif self.task_type == 'quality_check':
                processed_data = self._quality_check(data)
            elif self.task_type == 'report_generation':
                processed_data = self._generate_report(data)
            else:
                raise ValueError(f"Unknown task type: {self.task_type}")
            
            # Calculate accuracy metrics
            accuracy = self._calculate_accuracy(data, processed_data)
            
            # Validate results if enabled
            if self.enable_validation:
                validation_result = self._validate_results(processed_data, accuracy)
                if not validation_result['valid']:
                    self.log.warning(f"Validation failed: {validation_result['reason']}")
                    accuracy *= 0.8  # Reduce accuracy for validation failures
            
            # Store results
            self.results = {
                'processed_data': processed_data,
                'accuracy': accuracy,
                'task_type': self.task_type,
                'batch_size': self.batch_size,
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'validation_passed': validation_result.get('valid', True) if self.enable_validation else True
            }
            
            # Log results
            self.log.info(f"{self.task_type} completed with accuracy: {accuracy:.4f}")
            
            # Push results to XCom for downstream tasks
            context['task_instance'].xcom_push(
                key=f'{self.task_type}_results',
                value=self.results
            )
            
            # Push accuracy to XCom for monitoring
            context['task_instance'].xcom_push(
                key='accuracy',
                value=accuracy
            )
            
            return self.results
            
        except Exception as e:
            self.log.error(f"Error in {self.task_type}: {str(e)}")
            raise
    
    def _load_data(self, context: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """
        Load data from previous task or from source
        """
        try:
            # Try to get data from previous task
            ti = context['task_instance']
            upstream_results = ti.xcom_pull(task_ids=None, key='processed_data')
            
            if upstream_results is not None:
                return upstream_results
            
            # If no upstream data, try to load from file or database
            # This would be implemented based on your data source
            self.log.info("No upstream data found, loading from source")
            return self._load_from_source()
            
        except Exception as e:
            self.log.warning(f"Could not load upstream data: {e}")
            return self._load_from_source()
    
    def _load_from_source(self) -> Optional[pd.DataFrame]:
        """
        Load data from source (file, database, etc.)
        """
        # This would be implemented based on your data source
        # For now, return a sample dataset
        self.log.info("Loading sample data for demonstration")
        return pd.DataFrame({
            'text': ['sample text', 'another sample', 'test data'],
            'category': ['A', 'B', 'A'],
            'value': [1, 2, 3]
        })
    
    def _clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Clean data using DataAnalyzer
        """
        self.log.info("Starting data cleaning process")
        
        # Remove duplicates
        cleaned_data = data.drop_duplicates()
        
        # Remove rows with all NaN values
        cleaned_data = cleaned_data.dropna(how='all')
        
        # Basic data type conversion
        for col in cleaned_data.columns:
            if cleaned_data[col].dtype == 'object':
                # Try to convert to numeric if possible
                try:
                    cleaned_data[col] = pd.to_numeric(cleaned_data[col], errors='ignore')
                except:
                    pass
        
        self.log.info(f"Data cleaning completed. Original: {len(data)}, Cleaned: {len(cleaned_data)}")
        return cleaned_data
    
    def _detect_outliers(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Detect outliers using DataAnalyzer
        """
        self.log.info("Starting outlier detection")
        
        # Create a copy to avoid modifying original data
        outlier_data = data.copy()
        
        # Add outlier flags for numeric columns
        numeric_columns = outlier_data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            Q1 = outlier_data[col].quantile(0.25)
            Q3 = outlier_data[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outlier_data[f'{col}_is_outlier'] = (
                (outlier_data[col] < lower_bound) | 
                (outlier_data[col] > upper_bound)
            )
        
        self.log.info(f"Outlier detection completed for {len(numeric_columns)} numeric columns")
        return outlier_data
    
    def _correct_typos(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Correct typos using EnhancedTypoCorrection
        """
        self.log.info("Starting typo correction")
        
        # Create a copy to avoid modifying original data
        corrected_data = data.copy()
        
        # Apply typo correction to text columns
        text_columns = corrected_data.select_dtypes(include=['object']).columns
        
        for col in text_columns:
            if col in corrected_data.columns:
                try:
                    # Apply typo correction (this would use your actual typo correction logic)
                    corrected_data[col] = corrected_data[col].astype(str).apply(
                        lambda x: self.typo_corrector.correct_text(x) if pd.notna(x) else x
                    )
                except Exception as e:
                    self.log.warning(f"Typo correction failed for column {col}: {e}")
        
        self.log.info(f"Typo correction completed for {len(text_columns)} text columns")
        return corrected_data
    
    def _impute_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Impute missing values using DataAugmenter
        """
        self.log.info("Starting data imputation")
        
        # Create a copy to avoid modifying original data
        imputed_data = data.copy()
        
        # Impute numeric columns with median
        numeric_columns = imputed_data.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if imputed_data[col].isnull().sum() > 0:
                median_value = imputed_data[col].median()
                imputed_data[col].fillna(median_value, inplace=True)
        
        # Impute categorical columns with mode
        categorical_columns = imputed_data.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            if imputed_data[col].isnull().sum() > 0:
                mode_value = imputed_data[col].mode().iloc[0] if not imputed_data[col].mode().empty else 'Unknown'
                imputed_data[col].fillna(mode_value, inplace=True)
        
        self.log.info(f"Data imputation completed for {len(numeric_columns)} numeric and {len(categorical_columns)} categorical columns")
        return imputed_data
    
    def _quality_check(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Perform comprehensive quality check
        """
        self.log.info("Starting quality check")
        
        # Create a copy to avoid modifying original data
        quality_data = data.copy()
        
        # Add quality metrics
        quality_data['quality_score'] = 1.0
        
        # Check for missing values
        missing_ratio = quality_data.isnull().sum().sum() / (len(quality_data) * len(quality_data.columns))
        quality_data['quality_score'] *= (1 - missing_ratio)
        
        # Check for duplicates
        duplicate_ratio = quality_data.duplicated().sum() / len(quality_data)
        quality_data['quality_score'] *= (1 - duplicate_ratio)
        
        self.log.info(f"Quality check completed. Overall quality score: {quality_data['quality_score'].mean():.4f}")
        return quality_data
    
    def _generate_report(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate analysis report
        """
        self.log.info("Starting report generation")
        
        # Create a copy to avoid modifying original data
        report_data = data.copy()
        
        # Add report metadata
        report_data['report_timestamp'] = datetime.now()
        report_data['report_version'] = '1.0'
        
        # Generate summary statistics
        if len(report_data) > 0:
            report_data['total_records'] = len(report_data)
            report_data['total_columns'] = len(report_data.columns)
            report_data['missing_values'] = report_data.isnull().sum().sum()
        
        self.log.info("Report generation completed")
        return report_data
    
    def _calculate_accuracy(self, original_data: pd.DataFrame, processed_data: pd.DataFrame) -> float:
        """
        Calculate accuracy of the processing operation
        """
        try:
            # Basic accuracy calculation based on data integrity
            if original_data.empty or processed_data.empty:
                return 0.0
            
            # Check if data structure is maintained
            structure_accuracy = 1.0 if len(original_data.columns) <= len(processed_data.columns) else 0.5
            
            # Check if no data was lost (assuming processing should not reduce data significantly)
            data_loss_penalty = 0.0
            if len(processed_data) < len(original_data) * 0.9:  # Allow 10% data loss
                data_loss_penalty = 0.2
            
            # Check for data type consistency
            type_consistency = 1.0
            for col in original_data.columns:
                if col in processed_data.columns:
                    if original_data[col].dtype != processed_data[col].dtype:
                        type_consistency *= 0.9
            
            # Calculate final accuracy
            accuracy = (structure_accuracy + type_consistency) / 2 - data_loss_penalty
            
            # Ensure accuracy is between 0 and 1
            accuracy = max(0.0, min(1.0, accuracy))
            
            return accuracy
            
        except Exception as e:
            self.log.warning(f"Error calculating accuracy: {e}")
            return 0.5  # Default accuracy
    
    def _validate_results(self, processed_data: pd.DataFrame, accuracy: float) -> Dict[str, Any]:
        """
        Validate the processing results
        """
        validation_result = {
            'valid': True,
            'reason': None,
            'warnings': []
        }
        
        # Check if accuracy meets threshold
        if accuracy < self.accuracy_threshold:
            validation_result['valid'] = False
            validation_result['reason'] = f"Accuracy {accuracy:.4f} below threshold {self.accuracy_threshold}"
        
        # Check for data corruption
        if processed_data.isnull().sum().sum() > len(processed_data) * len(processed_data.columns) * 0.5:
            validation_result['warnings'].append("High percentage of missing values detected")
        
        # Check for extreme values in numeric columns
        numeric_columns = processed_data.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if processed_data[col].std() > processed_data[col].mean() * 10:
                validation_result['warnings'].append(f"High variance detected in column {col}")
        
        return validation_result
    
    def _create_result_dict(self, accuracy: float, status: str) -> Dict[str, Any]:
        """
        Create a standardized result dictionary
        """
        return {
            'accuracy': accuracy,
            'status': status,
            'task_type': self.task_type,
            'batch_size': self.batch_size,
            'processing_time': 0,
            'validation_passed': True
        }
