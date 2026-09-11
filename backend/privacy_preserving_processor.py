import pandas as pd
import numpy as np
import hashlib
import re
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, timedelta

class PrivacyPreservingProcessor:
    """Privacy-preserving data processing with differential privacy and anonymization"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.privacy_log = []
        
    def detect_pii_columns(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Detect potential PII columns using enhanced pattern matching with Upgini-style validation"""
        pii_patterns = {
            'email': [r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'],
            'phone': [r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', r'\b\(\d{3}\)\s?\d{3}[-.]?\d{4}\b'],
            'ssn': [r'\b\d{3}-\d{2}-\d{4}\b', r'\b\d{9}\b'],
            'credit_card': [r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'],
            'ip_address': [r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'],
            'name': [],  # Will be detected by column names
            'address': []  # Will be detected by column names
        }
        
        name_keywords = ['name', 'first', 'last', 'fname', 'lname', 'full_name']
        address_keywords = ['address', 'street', 'city', 'state', 'zip', 'postal']
        
        detected_pii = {pii_type: [] for pii_type in pii_patterns.keys()}
        
        for col in df.columns:
            col_lower = col.lower()
            
            # Check for name columns
            if any(keyword in col_lower for keyword in name_keywords):
                detected_pii['name'].append(col)
                continue
            
            # Check for address columns
            if any(keyword in col_lower for keyword in address_keywords):
                detected_pii['address'].append(col)
                continue
            
            # Check string columns for patterns
            if df[col].dtype == 'object':
                sample_values = df[col].dropna().astype(str).head(100)
                
                for pii_type, patterns in pii_patterns.items():
                    if pii_type in ['name', 'address']:
                        continue
                    
                    for pattern in patterns:
                        if sample_values.str.match(pattern).any():
                            detected_pii[pii_type].append(col)
                            break
        
        # Apply additional Upgini-style validation
        validated_pii = {}
        for pii_type, columns in detected_pii.items():
            if columns:
                # Validate that columns actually contain PII data
                valid_columns = []
                for col in columns:
                    if col in df.columns:
                        # Check if column has sufficient non-null values
                        non_null_ratio = df[col].notna().sum() / len(df)
                        if non_null_ratio > 0.1:  # At least 10% non-null values
                            valid_columns.append(col)
                
                if valid_columns:
                    validated_pii[pii_type] = valid_columns
        
        if validated_pii:
            self.privacy_log.append(f"Detected and validated PII columns: {validated_pii}")
        else:
            self.privacy_log.append("No PII columns detected with sufficient data quality")
        
        return validated_pii
    
    def anonymize_data(self, df: pd.DataFrame, 
                      pii_columns: Dict[str, List[str]] = None,
                      anonymization_method: str = 'hash') -> pd.DataFrame:
        """Anonymize PII data using various methods"""
        
        if pii_columns is None:
            pii_columns = self.detect_pii_columns(df)
        
        df_anon = df.copy()
        
        for pii_type, columns in pii_columns.items():
            for col in columns:
                if col not in df_anon.columns:
                    continue
                
                if anonymization_method == 'hash':
                    df_anon[col] = self._hash_anonymize(df_anon[col])
                elif anonymization_method == 'mask':
                    df_anon[col] = self._mask_anonymize(df_anon[col], pii_type)
                elif anonymization_method == 'generalize':
                    df_anon[col] = self._generalize_anonymize(df_anon[col], pii_type)
                elif anonymization_method == 'suppress':
                    df_anon[col] = self._suppress_anonymize(df_anon[col])
                
                self.privacy_log.append(f"Anonymized {pii_type} column '{col}' using {anonymization_method}")
        
        return df_anon
    
    def _hash_anonymize(self, series: pd.Series) -> pd.Series:
        """Hash-based anonymization"""
        def hash_value(x):
            if pd.isna(x):
                return x
            return hashlib.sha256(str(x).encode()).hexdigest()[:16]
        
        return series.apply(hash_value)
    
    def _mask_anonymize(self, series: pd.Series, pii_type: str) -> pd.Series:
        """Mask-based anonymization"""
        def mask_value(x):
            if pd.isna(x):
                return x
            
            x_str = str(x)
            
            if pii_type == 'email':
                # Mask email: keep first char and domain
                if '@' in x_str:
                    local, domain = x_str.split('@', 1)
                    return f"{local[0]}***@{domain}"
                return '***'
            
            elif pii_type == 'phone':
                # Mask phone: keep area code
                digits = re.sub(r'\D', '', x_str)
                if len(digits) >= 10:
                    return f"({digits[:3]}) ***-****"
                return '***-***-****'
            
            elif pii_type == 'ssn':
                # Mask SSN: keep last 4 digits
                digits = re.sub(r'\D', '', x_str)
                if len(digits) >= 4:
                    return f"***-**-{digits[-4:]}"
                return '***-**-****'
            
            elif pii_type == 'credit_card':
                # Mask credit card: keep last 4 digits
                digits = re.sub(r'\D', '', x_str)
                if len(digits) >= 4:
                    return f"****-****-****-{digits[-4:]}"
                return '****-****-****-****'
            
            elif pii_type in ['name', 'address']:
                # Mask names and addresses
                if len(x_str) > 2:
                    return x_str[0] + '*' * (len(x_str) - 2) + x_str[-1]
                return '***'
            
            else:
                return '***'
        
        return series.apply(mask_value)
    
    def _generalize_anonymize(self, series: pd.Series, pii_type: str) -> pd.Series:
        """Generalization-based anonymization"""
        def generalize_value(x):
            if pd.isna(x):
                return x
            
            if pii_type == 'email':
                # Generalize to domain only
                if '@' in str(x):
                    return str(x).split('@')[1]
                return 'unknown_domain'
            
            elif pii_type == 'phone':
                # Generalize to area code
                digits = re.sub(r'\D', '', str(x))
                if len(digits) >= 3:
                    return f"({digits[:3]}) XXX-XXXX"
                return '(XXX) XXX-XXXX'
            
            elif pii_type == 'address':
                # Generalize to city/state level
                return 'City, State'
            
            else:
                return 'GENERALIZED'
        
        return series.apply(generalize_value)
    
    def _suppress_anonymize(self, series: pd.Series) -> pd.Series:
        """Suppression-based anonymization"""
        return pd.Series(['SUPPRESSED'] * len(series), index=series.index)
    
    def add_differential_privacy_noise(self, df: pd.DataFrame, 
                                     epsilon: float = 1.0,
                                     sensitivity: float = 1.0) -> pd.DataFrame:
        """Add differential privacy noise to numeric columns"""
        df_private = df.copy()
        numeric_cols = df_private.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return df_private
        
        # Calculate noise scale (Laplace mechanism)
        scale = sensitivity / epsilon
        
        for col in numeric_cols:
            # Add Laplace noise
            noise = np.random.laplace(0, scale, size=len(df_private))
            df_private[col] = df_private[col] + noise
        
        self.privacy_log.append(f"Added differential privacy noise (ε={epsilon}) to {len(numeric_cols)} columns")
        
        return df_private
    
    def k_anonymize(self, df: pd.DataFrame, 
                   quasi_identifiers: List[str],
                   k: int = 5) -> pd.DataFrame:
        """Apply k-anonymity to quasi-identifier columns"""
        
        if not quasi_identifiers:
            return df
        
        df_k_anon = df.copy()
        
        # Group by quasi-identifiers
        groups = df_k_anon.groupby(quasi_identifiers)
        
        # Find groups with less than k members
        small_groups = []
        for name, group in groups:
            if len(group) < k:
                small_groups.append(group.index.tolist())
        
        if not small_groups:
            self.privacy_log.append(f"Dataset already satisfies {k}-anonymity")
            return df_k_anon
        
        # Generalize small groups
        for indices in small_groups:
            for col in quasi_identifiers:
                if df_k_anon[col].dtype in ['object', 'category']:
                    # For categorical data, use most common value in larger dataset
                    mode_val = df_k_anon[col].mode()
                    if not mode_val.empty:
                        df_k_anon.loc[indices, col] = mode_val[0]
                else:
                    # For numeric data, use median
                    median_val = df_k_anon[col].median()
                    df_k_anon.loc[indices, col] = median_val
        
        self.privacy_log.append(f"Applied {k}-anonymity to {len(quasi_identifiers)} quasi-identifiers")
        
        return df_k_anon
    
    def l_diversify(self, df: pd.DataFrame,
                   quasi_identifiers: List[str],
                   sensitive_attribute: str,
                   l: int = 2) -> pd.DataFrame:
        """Apply l-diversity to sensitive attributes"""
        
        if sensitive_attribute not in df.columns:
            return df
        
        df_l_div = df.copy()
        
        # Group by quasi-identifiers
        groups = df_l_div.groupby(quasi_identifiers)
        
        # Check l-diversity for each group
        for name, group in groups:
            sensitive_values = group[sensitive_attribute].value_counts()
            
            if len(sensitive_values) < l:
                # Need to diversify this group
                # Simple approach: sample from other groups
                other_groups = df_l_div[~df_l_div.index.isin(group.index)]
                
                if len(other_groups) > 0:
                    # Sample diverse values
                    diverse_values = other_groups[sensitive_attribute].value_counts().head(l).index
                    
                    # Assign diverse values to group members
                    for i, idx in enumerate(group.index):
                        df_l_div.loc[idx, sensitive_attribute] = diverse_values[i % len(diverse_values)]
        
        self.privacy_log.append(f"Applied {l}-diversity to sensitive attribute '{sensitive_attribute}'")
        
        return df_l_div
    
    def comprehensive_privacy_protection(self, df: pd.DataFrame,
                                       protection_level: str = 'medium',
                                       custom_pii: Dict[str, List[str]] = None) -> pd.DataFrame:
        """Comprehensive privacy protection using Upgini-inspired normalization and anonymization"""
        
        self.privacy_log = []
        self.privacy_log.append(f"Starting privacy protection (level: {protection_level}): {df.shape}")
        
        df_protected = df.copy()
        
        # Apply Upgini-style data normalization first
        df_protected = self._normalize_for_privacy(df_protected)
        
        # Detect PII using enhanced patterns
        pii_columns = custom_pii or self.detect_pii_columns(df_protected)
        
        if protection_level == 'low':
            # Basic masking with Upgini-style string truncation
            df_protected = self._truncate_long_strings(df_protected)
            df_protected = self.anonymize_data(df_protected, pii_columns, 'mask')
        
        elif protection_level == 'medium':
            # Anonymization + light differential privacy + normalization
            df_protected = self._truncate_long_strings(df_protected)
            df_protected = self.anonymize_data(df_protected, pii_columns, 'hash')
            df_protected = self.add_differential_privacy_noise(df_protected, epsilon=2.0)
        
        elif protection_level == 'high':
            # Full anonymization + strong differential privacy + k-anonymity + Upgini normalization
            df_protected = self._truncate_long_strings(df_protected)
            df_protected = self.anonymize_data(df_protected, pii_columns, 'suppress')
            df_protected = self.add_differential_privacy_noise(df_protected, epsilon=0.5)
            
            # Apply k-anonymity to remaining quasi-identifiers
            quasi_identifiers = []
            for col in df_protected.columns:
                if (df_protected[col].dtype in ['object', 'category'] and 
                    col not in [item for sublist in pii_columns.values() for item in sublist]):
                    quasi_identifiers.append(col)
            
            if quasi_identifiers:
                df_protected = self.k_anonymize(df_protected, quasi_identifiers[:3], k=5)
        
        # Final normalization step
        df_protected = self._final_type_conversion(df_protected)
        
        self.privacy_log.append(f"Privacy protection completed: {df.shape} → {df_protected.shape}")
        
        return df_protected
    
    def _normalize_for_privacy(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply Upgini-style normalization for privacy protection"""
        df_norm = df.copy()
        
        # Convert boolean columns to string (Upgini logic)
        for col in df_norm.columns:
            if df_norm[col].dtype == 'bool':
                df_norm[col] = df_norm[col].astype('str')
                self.privacy_log.append(f"Converted boolean column '{col}' to string for privacy")
        
        # Handle float16 conversion
        for col in df_norm.columns:
            if df_norm[col].dtype == 'float16':
                df_norm[col] = df_norm[col].astype('float64')
                self.privacy_log.append(f"Converted float16 to float64 for column '{col}'")
        
        return df_norm
    
    def _truncate_long_strings(self, df: pd.DataFrame) -> pd.DataFrame:
        """Truncate long string values using Upgini's MAX_STRING_FEATURE_LENGTH"""
        MAX_STRING_LENGTH = 24573
        
        for col in df.columns:
            if df[col].dtype == 'object' or df[col].dtype == 'string':
                max_length = df[col].astype('str').str.len().max()
                if pd.notna(max_length) and max_length > MAX_STRING_LENGTH:
                    df[col] = df[col].astype('str').str.slice(stop=MAX_STRING_LENGTH)
                    self.privacy_log.append(f"Truncated long strings in column '{col}' to {MAX_STRING_LENGTH} characters")
        
        return df
    
    def _final_type_conversion(self, df: pd.DataFrame) -> pd.DataFrame:
        """Final type conversion following Upgini standards"""
        # Convert non-numeric features to string
        system_columns = ['system_record_id', 'entity_system_record_id', 'eval_set_index', 'target']
        
        for col in df.columns:
            if col not in system_columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].astype('string')
        
        self.privacy_log.append("Applied final type conversion for privacy-protected data")
        return df