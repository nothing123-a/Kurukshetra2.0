import pandas as pd
import numpy as np
from faker import Faker
from sklearn.preprocessing import LabelEncoder, StandardScaler
from typing import Dict, Any, List
import warnings
warnings.filterwarnings('ignore')

try:
    from imblearn.over_sampling import SMOTE, ADASYN, BorderlineSMOTE
    from sklearn.neighbors import NearestNeighbors
    from sklearn.ensemble import IsolationForest
    from sklearn.cluster import KMeans
    ADVANCED_LIBS_AVAILABLE = True
except ImportError:
    ADVANCED_LIBS_AVAILABLE = False

class AdvancedDataAugmenter:
    def __init__(self):
        self.fake = Faker()
        
    def auto_detect_target_column(self, df: pd.DataFrame) -> str:
        """Automatically detect the best target column for augmentation"""
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        best_col = None
        best_score = 0
        
        for col in categorical_cols:
            # Calculate imbalance score
            value_counts = df[col].value_counts()
            if len(value_counts) < 2 or len(value_counts) > 20:  # Skip if too few or too many classes
                continue
                
            # Calculate class imbalance ratio
            min_class_size = value_counts.min()
            max_class_size = value_counts.max()
            imbalance_ratio = min_class_size / max_class_size
            
            # Prefer columns with moderate imbalance (not too balanced, not too imbalanced)
            if 0.1 < imbalance_ratio < 0.8:
                score = (1 - imbalance_ratio) * len(value_counts)  # Higher score for more imbalanced with more classes
                if score > best_score:
                    best_score = score
                    best_col = col
        
        return best_col or (categorical_cols[0] if len(categorical_cols) > 0 else None)
    
    def detect_rare_classes(self, df: pd.DataFrame, target_column: str, threshold: float = 0.05) -> List[str]:
        """Detect minority classes automatically"""
        if target_column not in df.columns:
            return []
        
        value_counts = df[target_column].value_counts()
        total_samples = len(df)
        
        rare_classes = []
        for class_name, count in value_counts.items():
            if count / total_samples < threshold:
                rare_classes.append(class_name)
        
        return rare_classes
    
    def basic_augmentation(self, df: pd.DataFrame, target_column: str) -> pd.DataFrame:
        """Basic augmentation without advanced libraries"""
        augmented_df = df.copy()
        rare_classes = self.detect_rare_classes(df, target_column)
        
        for rare_class in rare_classes:
            class_data = df[df[target_column] == rare_class]
            
            # Simple duplication with noise for numeric columns
            for _ in range(min(50, len(class_data))):
                new_row = class_data.sample(1).iloc[0].copy()
                
                # Add small noise to numeric columns
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                for col in numeric_cols:
                    if col in new_row.index:
                        noise = np.random.normal(0, df[col].std() * 0.1)
                        new_row[col] = max(0, new_row[col] + noise)
                
                augmented_df = pd.concat([augmented_df, new_row.to_frame().T], ignore_index=True)
        
        return augmented_df
    
    def advanced_smote_augmentation(self, df: pd.DataFrame, target_column: str) -> pd.DataFrame:
        """Advanced SMOTE with multiple techniques"""
        if not ADVANCED_LIBS_AVAILABLE:
            return self.basic_augmentation(df, target_column)
            
        try:
            X = df.drop(columns=[target_column])
            y = df[target_column]
            
            # Encode categorical variables
            categorical_columns = X.select_dtypes(include=['object']).columns
            label_encoders = {}
            
            X_encoded = X.copy()
            for col in categorical_columns:
                le = LabelEncoder()
                X_encoded[col] = le.fit_transform(X_encoded[col].astype(str))
                label_encoders[col] = le
            
            # Encode target variable
            target_encoder = LabelEncoder()
            y_encoded = target_encoder.fit_transform(y.astype(str))
            
            # Choose best SMOTE variant based on data characteristics
            n_samples = len(X_encoded)
            
            if n_samples < 100:
                sampler = SMOTE(random_state=42, k_neighbors=min(5, n_samples-1))
            else:
                sampler = BorderlineSMOTE(random_state=42, k_neighbors=min(5, n_samples-1))
            
            X_resampled, y_resampled = sampler.fit_resample(X_encoded, y_encoded)
            
            # Decode categorical variables
            X_resampled_df = pd.DataFrame(X_resampled, columns=X.columns)
            for col in categorical_columns:
                X_resampled_df[col] = label_encoders[col].inverse_transform(
                    X_resampled_df[col].astype(int)
                )
            
            # Decode target variable
            y_resampled_df = pd.Series(
                target_encoder.inverse_transform(y_resampled),
                name=target_column
            )
            
            # Combine features and target
            result_df = pd.concat([X_resampled_df, y_resampled_df], axis=1)
            return result_df
            
        except Exception as e:
            print(f"Advanced SMOTE failed: {e}")
            return self.basic_augmentation(df, target_column)
    
    def augment_data(self, df: pd.DataFrame, options: Dict[str, Any]) -> pd.DataFrame:
        """Main augmentation function with auto-detection"""
        # Auto-detect target column
        target_column = self.auto_detect_target_column(df)
        
        if not target_column:
            print("⚠️ No suitable target column found for augmentation")
            return df
        
        print(f"🎯 Auto-detected target column: {target_column}")
        
        # Use appropriate augmentation method
        if ADVANCED_LIBS_AVAILABLE:
            augmented_df = self.advanced_smote_augmentation(df, target_column)
        else:
            augmented_df = self.basic_augmentation(df, target_column)
        
        print(f"✅ Augmentation complete: {len(df)} → {len(augmented_df)} rows")
        return augmented_df

# Backward compatibility
DataAugmenter = AdvancedDataAugmenter