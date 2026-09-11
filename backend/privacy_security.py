import pandas as pd
import numpy as np
import hashlib
import base64
import re
from typing import Dict, Any, List
import warnings
warnings.filterwarnings('ignore')

class PrivacySecurityManager:
    def __init__(self):
        self.sensitive_patterns = {
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'phone': r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            'ssn': r'\d{3}-?\d{2}-?\d{4}',
            'credit_card': r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}',
            'pan': r'[A-Z]{5}\d{4}[A-Z]{1}',
            'aadhaar': r'\d{4}[-\s]?\d{4}[-\s]?\d{4}'
        }
    
    def detect_sensitive_columns(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Auto-detect sensitive columns that need privacy protection"""
        sensitive_cols = {
            'pii': [],
            'financial': [],
            'contact': [],
            'identification': []
        }
        
        for col in df.columns:
            col_lower = col.lower()
            sample_values = df[col].dropna().astype(str).head(100)
            
            # Check column names for sensitive keywords
            if any(keyword in col_lower for keyword in ['email', 'mail']):
                sensitive_cols['contact'].append(col)
            elif any(keyword in col_lower for keyword in ['phone', 'mobile', 'tel']):
                sensitive_cols['contact'].append(col)
            elif any(keyword in col_lower for keyword in ['ssn', 'social', 'security']):
                sensitive_cols['identification'].append(col)
            elif any(keyword in col_lower for keyword in ['pan', 'passport', 'license', 'aadhaar']):
                sensitive_cols['identification'].append(col)
            elif any(keyword in col_lower for keyword in ['card', 'account', 'bank']):
                sensitive_cols['financial'].append(col)
            elif any(keyword in col_lower for keyword in ['name', 'address']):
                sensitive_cols['pii'].append(col)
            
            # Check data patterns
            else:
                for pattern_name, pattern in self.sensitive_patterns.items():
                    matches = sample_values.str.match(pattern, na=False).sum()
                    if matches > len(sample_values) * 0.5:  # More than 50% match
                        if pattern_name in ['email']:
                            sensitive_cols['contact'].append(col)
                        elif pattern_name in ['phone']:
                            sensitive_cols['contact'].append(col)
                        elif pattern_name in ['ssn', 'pan', 'aadhaar']:
                            sensitive_cols['identification'].append(col)
                        elif pattern_name in ['credit_card']:
                            sensitive_cols['financial'].append(col)
                        break
        
        return sensitive_cols
    
    def advanced_hash(self, value):
        """Advanced hashing with salt for privacy protection - Refi compatible format"""
        if pd.isna(value):
            return value
        # Use PBKDF2 with salt for stronger encryption (same as Refi backend)
        salt = b'enterprise_salt_2024'
        key = hashlib.pbkdf2_hmac('sha256', str(value).encode(), salt, 100000)
        return "ENC_" + base64.b64encode(key).decode()[:16]
    
    def mask_data(self, value, mask_type='partial'):
        """Mask sensitive data with different strategies"""
        if pd.isna(value):
            return value
        
        value_str = str(value)
        
        if mask_type == 'partial':
            if len(value_str) <= 4:
                return 'MASK_' + 'X' * len(value_str)
            else:
                return 'MASK_' + value_str[:2] + 'X' * (len(value_str) - 4) + value_str[-2:]
        elif mask_type == 'full':
            return 'MASK_' + 'X' * min(8, len(value_str))
        elif mask_type == 'hash':
            return self.advanced_hash(value)
        else:
            return value_str
    
    def apply_privacy_protection(self, df: pd.DataFrame, privacy_config: Dict[str, Any]) -> pd.DataFrame:
        """Apply privacy protection ONLY to user-selected columns"""
        df_protected = df.copy()
        
        # Get user-selected columns for privacy protection
        privacy_columns = privacy_config.get('columns', [])
        protection_method = privacy_config.get('method', 'hash')  # hash, mask, remove
        
        if not privacy_columns:
            print("⚠️ No columns selected for privacy protection")
            return df_protected
        
        print(f"🔒 Applying {protection_method} protection to {len(privacy_columns)} selected columns: {privacy_columns}")
        
        protected_count = 0
        for col in privacy_columns:
            if col in df_protected.columns:
                print(f"🔐 Processing column: {col}")
                original_sample = df_protected[col].head(3).tolist()
                
                # Apply protection based on method
                if protection_method == 'hash':
                    df_protected[col] = df_protected[col].apply(self.advanced_hash)
                elif protection_method == 'mask':
                    df_protected[col] = df_protected[col].apply(lambda x: self.mask_data(x, 'partial'))
                elif protection_method == 'remove':
                    df_protected = df_protected.drop(columns=[col])
                    protected_count += 1
                    print(f"✅ {col}: Column removed for privacy")
                    continue
                
                protected_sample = df_protected[col].head(3).tolist()
                print(f"✅ {col}: {original_sample} → {protected_sample}")
                
                # Verify encryption was applied - if not, force it
                if protection_method in ['hash', 'mask']:
                    encrypted_values = [str(val) for val in protected_sample if 'ENC_' in str(val) or 'MASK_' in str(val)]
                    if encrypted_values:
                        protected_count += 1
                        print(f"✓ {col}: Successfully encrypted/masked {len(encrypted_values)} sample values")
                        print(f"   Sample encrypted values: {encrypted_values[:2]}")
                    else:
                        print(f"❌ {col}: No encrypted values detected - FORCING encryption...")
                        # Force encryption if it didn't work
                        if protection_method == 'hash':
                            df_protected[col] = df_protected[col].apply(lambda x: f"ENC_{hash(str(x))%1000000:06d}" if not pd.isna(x) else x)
                        else:
                            df_protected[col] = df_protected[col].apply(lambda x: f"MASK_{str(x)[:2]}XXX{str(x)[-2:]}" if not pd.isna(x) and len(str(x)) > 4 else f"MASK_XXX" if not pd.isna(x) else x)
                        protected_count += 1
                        print(f"✅ {col}: FORCED encryption applied")
            else:
                print(f"⚠️ Column '{col}' not found in dataset")
        
        print(f"✅ Privacy protection completed: {protected_count}/{len(privacy_columns)} columns processed")
        return df_protected
    
    def data_anonymization(self, df: pd.DataFrame, k_anonymity: int = 5) -> pd.DataFrame:
        """Apply k-anonymity for data anonymization"""
        df_anon = df.copy()
        
        # Identify quasi-identifiers (columns that could be used for re-identification)
        quasi_identifiers = []
        for col in df_anon.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['age', 'zip', 'postal', 'city', 'state', 'country', 'gender']):
                quasi_identifiers.append(col)
        
        # Apply generalization to achieve k-anonymity
        for col in quasi_identifiers:
            if col in df_anon.columns:
                if df_anon[col].dtype in ['int64', 'float64']:
                    # Generalize numeric values into ranges
                    if 'age' in col.lower():
                        df_anon[col] = pd.cut(df_anon[col], bins=[0, 18, 30, 50, 70, 100], labels=['<18', '18-30', '30-50', '50-70', '70+'])
                    elif 'zip' in col.lower() or 'postal' in col.lower():
                        # Generalize zip codes to first 3 digits
                        df_anon[col] = df_anon[col].astype(str).str[:3] + 'XX'
                else:
                    # For categorical data, group less frequent categories
                    value_counts = df_anon[col].value_counts()
                    rare_categories = value_counts[value_counts < k_anonymity].index
                    df_anon[col] = df_anon[col].replace(rare_categories, 'Other')
        
        return df_anon
    
    def differential_privacy_noise(self, df: pd.DataFrame, epsilon: float = 1.0) -> pd.DataFrame:
        """Add differential privacy noise to numeric columns"""
        df_private = df.copy()
        numeric_cols = df_private.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            # Add Laplace noise for differential privacy
            sensitivity = df_private[col].max() - df_private[col].min()
            scale = sensitivity / epsilon
            noise = np.random.laplace(0, scale, size=len(df_private))
            df_private[col] = df_private[col] + noise
            
            # Ensure values remain within reasonable bounds
            df_private[col] = df_private[col].clip(lower=0)
        
        return df_private
    
    def secure_data_export(self, df: pd.DataFrame, export_config: Dict[str, Any]) -> pd.DataFrame:
        """Prepare data for secure export with privacy controls"""
        df_export = df.copy()
        
        # Apply privacy protection
        if 'privacy' in export_config:
            df_export = self.apply_privacy_protection(df_export, export_config['privacy'])
        
        # Apply anonymization if requested
        if export_config.get('anonymize', False):
            k_value = export_config.get('k_anonymity', 5)
            df_export = self.data_anonymization(df_export, k_value)
        
        # Add differential privacy noise if requested
        if export_config.get('differential_privacy', False):
            epsilon = export_config.get('epsilon', 1.0)
            df_export = self.differential_privacy_noise(df_export, epsilon)
        
        return df_export
    
    def privacy_audit_report(self, df_original: pd.DataFrame, df_protected: pd.DataFrame) -> Dict[str, Any]:
        """Generate privacy protection audit report"""
        report = {
            'privacy_actions': [],
            'sensitive_data_detected': {},
            'protection_summary': {},
            'compliance_score': 0
        }
        
        # Detect sensitive columns in original data
        sensitive_cols = self.detect_sensitive_columns(df_original)
        report['sensitive_data_detected'] = sensitive_cols
        
        # Analyze protection applied
        for col in df_original.columns:
            if col in df_protected.columns:
                original_sample = df_original[col].dropna().astype(str).head(10).tolist()
                protected_sample = df_protected[col].dropna().astype(str).head(10).tolist()
                
                if original_sample != protected_sample:
                    # Check type of protection applied
                    if any('****' in str(val) for val in protected_sample):
                        report['privacy_actions'].append(f"Hashed sensitive data in column: {col}")
                    elif any('*' in str(val) for val in protected_sample):
                        report['privacy_actions'].append(f"Masked sensitive data in column: {col}")
            else:
                report['privacy_actions'].append(f"Removed sensitive column: {col}")
        
        # Calculate compliance score
        total_sensitive = sum(len(cols) for cols in sensitive_cols.values())
        protected_count = len(report['privacy_actions'])
        
        if total_sensitive > 0:
            compliance_score = min(100, (protected_count / total_sensitive) * 100)
        else:
            compliance_score = 100
        
        report['compliance_score'] = round(compliance_score, 1)
        report['protection_summary'] = {
            'total_sensitive_columns': total_sensitive,
            'columns_protected': protected_count,
            'protection_coverage': f"{compliance_score:.1f}%"
        }
        
        return report