import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neighbors import NearestNeighbors
import logging

class SyntheticDataGenerator:
    """Generate synthetic data for rare classes and data augmentation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.generation_log = []
        
    def smote_oversampling(self, X: pd.DataFrame, y: pd.Series, 
                          target_class: Any = None, k_neighbors: int = 5,
                          sampling_ratio: float = 1.0) -> Tuple[pd.DataFrame, pd.Series]:
        """SMOTE implementation with Upgini-style minority class handling"""
        
        if target_class is None:
            # Find minority class using Upgini logic
            class_counts = y.value_counts()
            target_class = class_counts.idxmin()
        
        # Get minority class samples
        minority_mask = y == target_class
        minority_X = X[minority_mask]
        minority_y = y[minority_mask]
        
        # Check minimum sample requirements (Upgini-style)
        MIN_TARGET_CLASS_ROWS = 100
        if len(minority_y) < MIN_TARGET_CLASS_ROWS:
            self.generation_log.append(f"Minority class {target_class} has {len(minority_y)} samples, less than minimum {MIN_TARGET_CLASS_ROWS}")
            # Still proceed but with adjusted parameters
        
        if len(minority_X) < k_neighbors:
            k_neighbors = max(1, len(minority_X) - 1)
            if k_neighbors <= 0:
                self.generation_log.append(f"Not enough samples for SMOTE in class {target_class}")
                return X, y
        
        # Calculate number of synthetic samples using Upgini rebalancing logic
        majority_count = len(y) - len(minority_y)
        
        # Use Upgini-style bootstrap loops for rebalancing
        BINARY_BOOTSTRAP_LOOPS = 5
        target_count = min(
            majority_count,
            BINARY_BOOTSTRAP_LOOPS * (len(minority_y) + max(5000 - 2 * len(minority_y), 0))
        )
        
        n_synthetic = max(0, int(target_count * sampling_ratio) - len(minority_y))
        
        if n_synthetic == 0:
            return X, y
        
        # Prepare numeric data for SMOTE
        numeric_cols = X.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            self.generation_log.append("No numeric columns found for SMOTE")
            return X, y
        
        X_numeric = minority_X[numeric_cols].fillna(minority_X[numeric_cols].median())
        
        # Fit k-NN model
        nn_model = NearestNeighbors(n_neighbors=k_neighbors, metric='euclidean')
        nn_model.fit(X_numeric)
        
        # Generate synthetic samples
        synthetic_samples = []
        
        for _ in range(n_synthetic):
            # Randomly select a minority sample
            idx = np.random.randint(0, len(X_numeric))
            sample = X_numeric.iloc[idx].values
            
            # Find k nearest neighbors
            _, neighbors_idx = nn_model.kneighbors([sample])
            
            # Randomly select one neighbor
            neighbor_idx = np.random.choice(neighbors_idx[0])
            neighbor = X_numeric.iloc[neighbor_idx].values
            
            # Generate synthetic sample
            diff = neighbor - sample
            gap = np.random.random()
            synthetic = sample + gap * diff
            
            synthetic_samples.append(synthetic)
        
        # Create synthetic DataFrame
        synthetic_df = pd.DataFrame(synthetic_samples, columns=numeric_cols)
        
        # Handle non-numeric columns by copying from random minority samples
        for col in X.columns:
            if col not in numeric_cols:
                if len(minority_X[col].dropna()) > 0:
                    random_values = np.random.choice(minority_X[col].dropna().values, 
                                                   size=n_synthetic, replace=True)
                    synthetic_df[col] = random_values
                else:
                    synthetic_df[col] = 'Unknown'
        
        # Combine original and synthetic data
        X_augmented = pd.concat([X, synthetic_df], ignore_index=True)
        y_augmented = pd.concat([y, pd.Series([target_class] * n_synthetic)], ignore_index=True)
        
        self.generation_log.append(f"Generated {n_synthetic} synthetic samples for minority class {target_class} using Upgini-style SMOTE")
        
        return X_augmented, y_augmented
    
    def gaussian_noise_augmentation(self, X: pd.DataFrame, 
                                   noise_factor: float = 0.1,
                                   n_samples: int = None) -> pd.DataFrame:
        """Add Gaussian noise to numeric columns for data augmentation"""
        
        if n_samples is None:
            n_samples = len(X)
        
        numeric_cols = X.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            return X
        
        # Sample rows to augment
        sample_indices = np.random.choice(len(X), size=n_samples, replace=True)
        X_augmented = X.iloc[sample_indices].copy()
        
        # Add Gaussian noise to numeric columns
        for col in numeric_cols:
            col_std = X[col].std()
            if pd.notna(col_std) and col_std > 0:
                noise = np.random.normal(0, col_std * noise_factor, size=n_samples)
                X_augmented[col] = X_augmented[col] + noise
        
        self.generation_log.append(f"Generated {n_samples} samples with Gaussian noise augmentation")
        
        return X_augmented
    
    def bootstrap_sampling(self, X: pd.DataFrame, y: pd.Series = None,
                          n_samples: int = None, 
                          stratify: bool = True) -> Tuple[pd.DataFrame, Optional[pd.Series]]:
        """Bootstrap sampling for data augmentation"""
        
        if n_samples is None:
            n_samples = len(X)
        
        if y is not None and stratify:
            # Stratified bootstrap sampling
            augmented_indices = []
            
            for class_val in y.unique():
                class_mask = y == class_val
                class_indices = X[class_mask].index.tolist()
                class_size = len(class_indices)
                
                # Calculate samples for this class
                class_proportion = class_size / len(X)
                class_n_samples = int(n_samples * class_proportion)
                
                # Bootstrap sample
                sampled_indices = np.random.choice(class_indices, 
                                                 size=class_n_samples, 
                                                 replace=True)
                augmented_indices.extend(sampled_indices)
            
            X_augmented = X.loc[augmented_indices].reset_index(drop=True)
            y_augmented = y.loc[augmented_indices].reset_index(drop=True) if y is not None else None
        else:
            # Simple bootstrap sampling
            sample_indices = np.random.choice(len(X), size=n_samples, replace=True)
            X_augmented = X.iloc[sample_indices].reset_index(drop=True)
            y_augmented = y.iloc[sample_indices].reset_index(drop=True) if y is not None else None
        
        self.generation_log.append(f"Generated {n_samples} samples using bootstrap sampling")
        
        return X_augmented, y_augmented
    
    def feature_permutation_augmentation(self, X: pd.DataFrame, 
                                       permute_ratio: float = 0.1,
                                       n_samples: int = None) -> pd.DataFrame:
        """Augment data by permuting feature values"""
        
        if n_samples is None:
            n_samples = len(X)
        
        # Sample rows to augment
        sample_indices = np.random.choice(len(X), size=n_samples, replace=True)
        X_augmented = X.iloc[sample_indices].copy().reset_index(drop=True)
        
        # Permute features
        n_features_to_permute = max(1, int(len(X.columns) * permute_ratio))
        features_to_permute = np.random.choice(X.columns, 
                                             size=n_features_to_permute, 
                                             replace=False)
        
        for feature in features_to_permute:
            # Randomly shuffle values in this feature
            X_augmented[feature] = np.random.permutation(X_augmented[feature].values)
        
        self.generation_log.append(f"Generated {n_samples} samples with feature permutation")
        
        return X_augmented
    
    def mixup_augmentation(self, X: pd.DataFrame, y: pd.Series = None,
                          alpha: float = 0.2, n_samples: int = None) -> Tuple[pd.DataFrame, Optional[pd.Series]]:
        """Mixup augmentation for numeric data"""
        
        if n_samples is None:
            n_samples = len(X)
        
        numeric_cols = X.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            return X, y
        
        # Generate pairs of samples to mix
        indices1 = np.random.choice(len(X), size=n_samples, replace=True)
        indices2 = np.random.choice(len(X), size=n_samples, replace=True)
        
        # Generate mixing coefficients
        lam = np.random.beta(alpha, alpha, size=n_samples)
        
        # Create mixed samples
        X_mixed = X.iloc[indices1].copy().reset_index(drop=True)
        
        for i, col in enumerate(numeric_cols):
            X_mixed[col] = (lam * X.iloc[indices1][col].values + 
                           (1 - lam) * X.iloc[indices2][col].values)
        
        # Handle categorical columns by random selection
        categorical_cols = X.select_dtypes(exclude=[np.number]).columns
        for col in categorical_cols:
            # Randomly choose from either sample
            choice_mask = np.random.random(n_samples) < 0.5
            X_mixed[col] = np.where(choice_mask, 
                                   X.iloc[indices1][col].values,
                                   X.iloc[indices2][col].values)
        
        y_mixed = None
        if y is not None:
            # For classification, use the label from the dominant sample
            y_mixed = pd.Series(np.where(lam > 0.5, 
                                       y.iloc[indices1].values,
                                       y.iloc[indices2].values))
        
        self.generation_log.append(f"Generated {n_samples} samples using Mixup augmentation")
        
        return X_mixed, y_mixed
    
    def comprehensive_augmentation(self, X: pd.DataFrame, y: pd.Series = None,
                                 target_size: int = None,
                                 methods: List[str] = None) -> Tuple[pd.DataFrame, Optional[pd.Series]]:
        """Comprehensive data augmentation using Upgini-inspired sampling techniques"""
        
        if methods is None:
            methods = ['smote', 'gaussian_noise', 'bootstrap']
        
        if target_size is None:
            target_size = len(X) * 2  # Double the dataset size
        
        self.generation_log = []
        self.generation_log.append(f"Starting comprehensive augmentation: {X.shape}")
        
        X_augmented = X.copy()
        y_augmented = y.copy() if y is not None else None
        
        # Apply Upgini-style sampling logic
        if y is not None:
            # Check if target is imbalanced using Upgini logic
            target_counts = y.value_counts()
            min_class_count = target_counts.min()
            max_class_count = target_counts.max()
            
            # Apply rebalancing if needed
            if max_class_count > min_class_count * 2:  # Imbalanced threshold
                self.generation_log.append(f"Detected imbalanced target: min={min_class_count}, max={max_class_count}")
                
                # Use SMOTE for minority class oversampling
                if 'smote' in methods:
                    minority_class = target_counts.idxmin()
                    X_smote, y_smote = self.smote_oversampling(
                        X_augmented, y_augmented,
                        target_class=minority_class,
                        sampling_ratio=0.8
                    )
                    X_augmented = X_smote
                    y_augmented = y_smote
        
        # Apply additional augmentation methods
        remaining_samples = max(0, target_size - len(X_augmented))
        
        for method in methods:
            if remaining_samples <= 0:
                break
            
            method_samples = min(remaining_samples // len(methods), remaining_samples)
            
            if method == 'gaussian_noise' and method_samples > 0:
                X_noise = self.gaussian_noise_augmentation(
                    X, n_samples=method_samples
                )
                X_augmented = pd.concat([X_augmented, X_noise], ignore_index=True)
                
                if y_augmented is not None:
                    # Sample corresponding labels using stratified approach
                    noise_indices = np.random.choice(len(y), size=len(X_noise), replace=True)
                    y_noise = y.iloc[noise_indices].reset_index(drop=True)
                    y_augmented = pd.concat([y_augmented, y_noise], ignore_index=True)
                
                remaining_samples -= len(X_noise)
            
            elif method == 'bootstrap' and method_samples > 0:
                X_boot, y_boot = self.bootstrap_sampling(
                    X, y, n_samples=method_samples, stratify=True
                )
                X_augmented = pd.concat([X_augmented, X_boot], ignore_index=True)
                
                if y_augmented is not None and y_boot is not None:
                    y_augmented = pd.concat([y_augmented, y_boot], ignore_index=True)
                
                remaining_samples -= len(X_boot)
        
        final_shape = X_augmented.shape
        self.generation_log.append(f"Comprehensive augmentation completed: {X.shape} → {final_shape}")
        
        return X_augmented, y_augmented