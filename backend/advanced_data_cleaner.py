import pandas as pd
import numpy as np
import hashlib
import logging
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import re
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.ensemble import IsolationForest
from pandas.api.types import is_bool_dtype, is_datetime64_any_dtype, is_numeric_dtype, is_object_dtype, is_string_dtype

class AdvancedDataCleaner:
    """Advanced data cleaning with AI-powered deduplication and normalization from Upgini"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cleaning_log = []
        self.MAX_STRING_FEATURE_LENGTH = 24573
        
    def clean_full_duplicates(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Optional[str]]:
        """Remove full duplicates with intelligent handling from Upgini logic"""
        nrows = len(df)
        if nrows == 0:
            return df, None
            
        # Remove full duplicates (exclude system columns)
        unique_columns = df.columns.tolist()
        system_cols = ['system_record_id', 'entity_system_record_id', 'sort_id', 'eval_set_index']
        for col in system_cols:
            if col in unique_columns:
                unique_columns.remove(col)
        
        self.logger.info(f"Dataset shape before clean duplicates: {df.shape}")
        df_clean = df.drop_duplicates(subset=unique_columns, keep="first")
        self.logger.info(f"Dataset shape after clean duplicates: {df_clean.shape}")
        
        nrows_after = len(df_clean)
        share_removed = 100 * (1 - nrows_after / nrows)
        
        msg = None
        if share_removed > 0:
            msg = f"Removed {share_removed:.1f}% duplicate rows ({nrows - nrows_after} rows)"
            self.cleaning_log.append(msg)
            
        return df_clean, msg
    
    def detect_and_fix_inconsistent_labels(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect and normalize inconsistent categorical labels using Upgini normalization logic"""
        df_clean = df.copy()
        
        # Cut too long string values first
        df_clean = self._cut_too_long_string_values(df_clean)
        
        # Convert bools to string
        df_clean = self._convert_bools(df_clean)
        
        # Normalize string columns
        for col in df_clean.select_dtypes(include=['object']).columns:
            if is_string_dtype(df_clean[col]) or is_object_dtype(df_clean[col]):
                # Find similar labels using fuzzy matching
                unique_values = df_clean[col].dropna().unique()
                
                if len(unique_values) <= 1:
                    continue
                    
                # Group similar values
                value_groups = self._group_similar_values(unique_values)
                
                # Create mapping for normalization
                mapping = {}
                for group in value_groups:
                    if len(group) > 1:
                        # Use the most frequent value as canonical
                        canonical = max(group, key=lambda x: (df_clean[col] == x).sum())
                        for value in group:
                            if value != canonical:
                                mapping[value] = canonical
                
                if mapping:
                    df_clean[col] = df_clean[col].replace(mapping)
                    self.cleaning_log.append(f"Normalized {len(mapping)} inconsistent labels in column '{col}'")
        
        return df_clean
    
    def _cut_too_long_string_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Check that string values less than maximum characters for LLM"""
        for col in df.columns:
            if is_string_dtype(df[col]) or is_object_dtype(df[col]):
                max_length = df[col].astype("str").str.len().max()
                if max_length > self.MAX_STRING_FEATURE_LENGTH:
                    df[col] = df[col].astype("str").str.slice(stop=self.MAX_STRING_FEATURE_LENGTH)
                    self.cleaning_log.append(f"Truncated long strings in column '{col}' to {self.MAX_STRING_FEATURE_LENGTH} chars")
        return df
    
    def _convert_bools(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert bool columns to string"""
        for col in df.columns:
            if is_bool_dtype(df[col]):
                df[col] = df[col].astype("str")
                self.cleaning_log.append(f"Converted boolean column '{col}' to string")
        return df
    
    def _group_similar_values(self, values: np.ndarray, threshold: float = 0.8) -> List[List[str]]:
        """Group similar string values using Levenshtein distance"""
        groups = []
        used = set()
        
        for i, val1 in enumerate(values):
            if val1 in used:
                continue
                
            group = [val1]
            used.add(val1)
            
            for j, val2 in enumerate(values[i+1:], i+1):
                if val2 in used:
                    continue
                    
                similarity = self._string_similarity(str(val1).lower(), str(val2).lower())
                if similarity >= threshold:
                    group.append(val2)
                    used.add(val2)
            
            groups.append(group)
        
        return groups
    
    def _string_similarity(self, s1: str, s2: str) -> float:
        """Calculate string similarity using Levenshtein distance"""
        if s1 == s2:
            return 1.0
        
        len1, len2 = len(s1), len(s2)
        if len1 == 0 or len2 == 0:
            return 0.0
        
        # Create distance matrix
        matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        
        for i in range(len1 + 1):
            matrix[i][0] = i
        for j in range(len2 + 1):
            matrix[0][j] = j
        
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                cost = 0 if s1[i-1] == s2[j-1] else 1
                matrix[i][j] = min(
                    matrix[i-1][j] + 1,      # deletion
                    matrix[i][j-1] + 1,      # insertion
                    matrix[i-1][j-1] + cost  # substitution
                )
        
        distance = matrix[len1][len2]
        return 1 - (distance / max(len1, len2))
    
    def intelligent_missing_value_imputation(self, df: pd.DataFrame) -> pd.DataFrame:
        """Advanced missing value imputation using Upgini-inspired strategies"""
        df_clean = df.copy()
        
        # Remove datetime columns from features first
        df_clean = self._remove_dates_from_features(df_clean)
        
        for col in df_clean.columns:
            missing_count = df_clean[col].isnull().sum()
            if missing_count == 0:
                continue
                
            missing_ratio = missing_count / len(df_clean)
            
            if is_numeric_dtype(df_clean[col]):
                # Numeric columns - use statistical methods
                if missing_ratio < 0.1:
                    # Low missing ratio: use median
                    df_clean[col].fillna(df_clean[col].median(), inplace=True)
                elif missing_ratio < 0.3:
                    # Medium missing ratio: use regression imputation
                    df_clean = self._regression_imputation(df_clean, col)
                else:
                    # High missing ratio: use clustering-based imputation
                    df_clean = self._cluster_imputation(df_clean, col)
            else:
                # Non-numeric columns - convert to string and handle
                df_clean[col] = df_clean[col].astype("string")
                if missing_ratio < 0.05:
                    # Use mode for low missing ratio
                    mode_val = df_clean[col].mode()
                    if not mode_val.empty:
                        df_clean[col].fillna(mode_val[0], inplace=True)
                else:
                    # Create "Unknown" category for high missing ratio
                    df_clean[col].fillna('Unknown', inplace=True)
            
            self.cleaning_log.append(f"Imputed {missing_count} missing values in column '{col}' (ratio: {missing_ratio:.2%})")
        
        return df_clean
    
    def _remove_dates_from_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove datetime columns from features as per Upgini logic"""
        features_to_remove = []
        for col in df.columns:
            if is_datetime64_any_dtype(df[col]) or isinstance(df[col].dtype, pd.PeriodDtype):
                features_to_remove.append(col)
        
        if features_to_remove:
            df = df.drop(columns=features_to_remove)
            self.cleaning_log.append(f"Removed datetime columns: {features_to_remove}")
        
        return df
    
    def _regression_imputation(self, df: pd.DataFrame, target_col: str) -> pd.DataFrame:
        """Impute missing values using regression on other numeric columns"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if target_col in numeric_cols:
            numeric_cols.remove(target_col)
        
        if not numeric_cols:
            # Fallback to median
            df[target_col].fillna(df[target_col].median(), inplace=True)
            return df
        
        # Use complete cases for training
        complete_mask = df[numeric_cols + [target_col]].notna().all(axis=1)
        missing_mask = df[target_col].isna()
        
        if complete_mask.sum() < 10:  # Not enough data
            df[target_col].fillna(df[target_col].median(), inplace=True)
            return df
        
        try:
            from sklearn.linear_model import LinearRegression
            
            X_train = df.loc[complete_mask, numeric_cols]
            y_train = df.loc[complete_mask, target_col]
            X_missing = df.loc[missing_mask, numeric_cols]
            
            # Handle missing values in features
            X_train = X_train.fillna(X_train.median())
            X_missing = X_missing.fillna(X_train.median())
            
            model = LinearRegression()
            model.fit(X_train, y_train)
            predictions = model.predict(X_missing)
            
            df.loc[missing_mask, target_col] = predictions
        except:
            # Fallback to median
            df[target_col].fillna(df[target_col].median(), inplace=True)
        
        return df
    
    def _cluster_imputation(self, df: pd.DataFrame, target_col: str) -> pd.DataFrame:
        """Impute missing values using clustering"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if target_col in numeric_cols:
            numeric_cols.remove(target_col)
        
        if not numeric_cols:
            df[target_col].fillna(df[target_col].median(), inplace=True)
            return df
        
        try:
            # Prepare data for clustering
            cluster_data = df[numeric_cols].fillna(df[numeric_cols].median())
            
            # Standardize features
            scaler = StandardScaler()
            cluster_data_scaled = scaler.fit_transform(cluster_data)
            
            # Perform clustering
            clusterer = DBSCAN(eps=0.5, min_samples=5)
            clusters = clusterer.fit_predict(cluster_data_scaled)
            
            # Impute based on cluster medians
            missing_mask = df[target_col].isna()
            for cluster_id in np.unique(clusters):
                if cluster_id == -1:  # Noise points
                    continue
                    
                cluster_mask = clusters == cluster_id
                cluster_median = df.loc[cluster_mask & ~missing_mask, target_col].median()
                
                if not pd.isna(cluster_median):
                    df.loc[missing_mask & cluster_mask, target_col] = cluster_median
            
            # Fill remaining missing values with global median
            df[target_col].fillna(df[target_col].median(), inplace=True)
            
        except:
            # Fallback to median
            df[target_col].fillna(df[target_col].median(), inplace=True)
        
        return df
    
    def detect_and_handle_outliers(self, df: pd.DataFrame, method: str = 'isolation_forest') -> pd.DataFrame:
        """Advanced outlier detection and handling"""
        df_clean = df.copy()
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return df_clean
        
        outlier_indices = set()
        
        if method == 'isolation_forest':
            try:
                # Use Isolation Forest for multivariate outlier detection
                iso_forest = IsolationForest(contamination=0.1, random_state=42)
                X = df_clean[numeric_cols].fillna(df_clean[numeric_cols].median())
                outliers = iso_forest.fit_predict(X)
                outlier_indices.update(np.where(outliers == -1)[0])
            except:
                method = 'iqr'  # Fallback
        
        if method == 'iqr':
            # Use IQR method for each column
            for col in numeric_cols:
                Q1 = df_clean[col].quantile(0.25)
                Q3 = df_clean[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                col_outliers = df_clean[(df_clean[col] < lower_bound) | 
                                       (df_clean[col] > upper_bound)].index
                outlier_indices.update(col_outliers)
        
        if outlier_indices:
            # Cap outliers instead of removing them
            for idx in outlier_indices:
                for col in numeric_cols:
                    value = df_clean.loc[idx, col]
                    if pd.notna(value):
                        Q1 = df_clean[col].quantile(0.25)
                        Q3 = df_clean[col].quantile(0.75)
                        IQR = Q3 - Q1
                        lower_bound = Q1 - 1.5 * IQR
                        upper_bound = Q3 + 1.5 * IQR
                        
                        if value < lower_bound:
                            df_clean.loc[idx, col] = lower_bound
                        elif value > upper_bound:
                            df_clean.loc[idx, col] = upper_bound
            
            self.cleaning_log.append(f"Handled {len(outlier_indices)} outlier records using capping")
        
        return df_clean
    
    def normalize_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize and optimize data types using Upgini logic"""
        df_clean = df.copy()
        
        # Convert float16 to float64
        df_clean = self._convert_float16(df_clean)
        
        # Convert features to supported data types
        system_columns = ['entity_system_record_id', 'eval_set_index', 'system_record_id', 'target']
        features = [col for col in df_clean.columns if col not in system_columns]
        
        for col in features:
            if not is_numeric_dtype(df_clean[col]):
                df_clean[col] = df_clean[col].astype("string")
            else:
                # Optimize numeric types
                if df_clean[col].dtype == 'int64':
                    min_val = df_clean[col].min()
                    max_val = df_clean[col].max()
                    
                    if pd.notna(min_val) and pd.notna(max_val):
                        if min_val >= -128 and max_val <= 127:
                            df_clean[col] = df_clean[col].astype('int8')
                        elif min_val >= -32768 and max_val <= 32767:
                            df_clean[col] = df_clean[col].astype('int16')
                        elif min_val >= -2147483648 and max_val <= 2147483647:
                            df_clean[col] = df_clean[col].astype('int32')
        
        self.cleaning_log.append("Normalized data types using Upgini standards")
        return df_clean
    
    def _convert_float16(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert float16 to float64 as per Upgini logic"""
        for col in df.columns:
            if df[col].dtype == 'float16':
                df[col] = df[col].astype('float64')
                self.cleaning_log.append(f"Converted float16 to float64 for column '{col}'")
        return df
    
    def comprehensive_clean(self, df: pd.DataFrame, 
                          remove_duplicates: bool = True,
                          fix_labels: bool = True,
                          impute_missing: bool = True,
                          handle_outliers: bool = True,
                          normalize_types: bool = True) -> Tuple[pd.DataFrame, List[str]]:
        """Comprehensive data cleaning pipeline"""
        self.cleaning_log = []
        df_clean = df.copy()
        
        original_shape = df_clean.shape
        self.cleaning_log.append(f"Starting comprehensive cleaning on dataset: {original_shape}")
        
        if remove_duplicates:
            df_clean, dup_msg = self.clean_full_duplicates(df_clean)
        
        if fix_labels:
            df_clean = self.detect_and_fix_inconsistent_labels(df_clean)
        
        if impute_missing:
            df_clean = self.intelligent_missing_value_imputation(df_clean)
        
        if handle_outliers:
            df_clean = self.detect_and_handle_outliers(df_clean)
        
        if normalize_types:
            df_clean = self.normalize_data_types(df_clean)
        
        final_shape = df_clean.shape
        self.cleaning_log.append(f"Comprehensive cleaning completed: {original_shape} → {final_shape}")
        
        # Final type conversion for features
        df_clean = self._convert_features_types(df_clean)
        
        return df_clean, self.cleaning_log
    
    def _convert_features_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert features to supported data types as per Upgini logic"""
        system_columns = ['entity_system_record_id', 'eval_set_index', 'system_record_id', 'target']
        features = [col for col in df.columns if col not in system_columns]
        
        for col in features:
            if not is_numeric_dtype(df[col]):
                df[col] = df[col].astype("string")
        
        return df