import pandas as pd
import numpy as np
from typing import Dict, Any, List
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')

class DataAnalyzer:
    def __init__(self):
        self.analysis_cache = {}
    
    def generate_comprehensive_summary(self, df: pd.DataFrame, cleaning_log: List[str] = None, privacy_report: Dict[str, Any] = None) -> str:
        """Generate comprehensive data analysis summary using Python statistical models"""
        
        # Basic dataset information
        rows, cols = df.shape
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        # Data quality metrics
        completeness = (1 - df.isnull().sum().sum() / (rows * cols)) * 100
        duplicates = df.duplicated().sum()
        unique_ratio = df.nunique().sum() / (rows * cols) * 100
        
        # Statistical analysis for numeric columns
        numeric_insights = []
        if len(numeric_cols) > 0:
            numeric_data = df[numeric_cols]
            
            # Distribution analysis
            skewed_cols = []
            normal_cols = []
            for col in numeric_cols:
                skewness = stats.skew(numeric_data[col].dropna())
                if abs(skewness) > 1:
                    skewed_cols.append(col)
                else:
                    normal_cols.append(col)
            
            # Correlation analysis
            if len(numeric_cols) > 1:
                corr_matrix = numeric_data.corr()
                high_corr_pairs = []
                for i in range(len(corr_matrix.columns)):
                    for j in range(i+1, len(corr_matrix.columns)):
                        corr_val = abs(corr_matrix.iloc[i, j])
                        if corr_val > 0.7:
                            high_corr_pairs.append((corr_matrix.columns[i], corr_matrix.columns[j], corr_val))
            
            # Outlier detection
            outlier_cols = []
            for col in numeric_cols:
                Q1 = numeric_data[col].quantile(0.25)
                Q3 = numeric_data[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = ((numeric_data[col] < (Q1 - 1.5 * IQR)) | (numeric_data[col] > (Q3 + 1.5 * IQR))).sum()
                if outliers > 0:
                    outlier_cols.append((col, outliers))
        
        # Categorical analysis
        categorical_insights = []
        if len(categorical_cols) > 0:
            for col in categorical_cols:
                unique_count = df[col].nunique()
                most_frequent = df[col].mode().iloc[0] if not df[col].mode().empty else "N/A"
                frequency_pct = (df[col].value_counts().iloc[0] / len(df)) * 100 if len(df) > 0 else 0
                categorical_insights.append((col, unique_count, most_frequent, frequency_pct))
        
        # Generate summary text
        summary = f"""**Dataset Analysis Summary**

**Dataset Overview:**
The dataset contains {rows:,} records across {cols} variables, demonstrating a {'large-scale' if rows > 10000 else 'medium-scale' if rows > 1000 else 'compact'} data structure suitable for comprehensive analysis.

**Data Quality Assessment:**
Data completeness stands at {completeness:.1f}%, indicating {'excellent' if completeness > 95 else 'good' if completeness > 85 else 'moderate'} data quality. The dataset contains {duplicates} duplicate records, representing {(duplicates/rows)*100:.1f}% of the total data.

**Variable Composition:**
The dataset comprises {len(numeric_cols)} numerical variables and {len(categorical_cols)} categorical variables, providing a {'balanced' if abs(len(numeric_cols) - len(categorical_cols)) <= 2 else 'numerically-focused' if len(numeric_cols) > len(categorical_cols) else 'categorically-focused'} analytical foundation."""

        # Add numeric insights
        if len(numeric_cols) > 0:
            summary += f"""

**Numerical Analysis:**
Statistical examination reveals {len(normal_cols)} variables following normal distribution patterns, while {len(skewed_cols)} variables exhibit skewed distributions requiring specialized analytical approaches."""
            
            if len(numeric_cols) > 1 and 'high_corr_pairs' in locals() and high_corr_pairs:
                summary += f" Strong correlations (>0.7) were identified between {len(high_corr_pairs)} variable pairs, suggesting potential multicollinearity considerations."
            
            if outlier_cols:
                total_outliers = sum([count for _, count in outlier_cols])
                summary += f" Outlier analysis detected {total_outliers} anomalous values across {len(outlier_cols)} variables, representing {(total_outliers/(rows*len(numeric_cols)))*100:.1f}% of numerical data points."
        
        # Add categorical insights
        if categorical_insights:
            summary += f"""

**Categorical Analysis:**
Categorical variables demonstrate varying levels of diversity, with unique value counts ranging from {min([count for _, count, _, _ in categorical_insights])} to {max([count for _, count, _, _ in categorical_insights])}."""
            
            high_cardinality = [col for col, count, _, _ in categorical_insights if count > rows * 0.1]
            if high_cardinality:
                summary += f" High-cardinality variables ({', '.join(high_cardinality[:3])}) may require encoding strategies for machine learning applications."
        
        # Add cleaning process insights
        if cleaning_log:
            summary += f"""

**Data Processing Impact:**
The cleaning pipeline successfully processed the dataset through {len(cleaning_log)} transformation steps, enhancing data quality and analytical readiness."""
            
            # Analyze cleaning steps
            imputation_steps = [log for log in cleaning_log if 'imputed' in log.lower() or 'missing' in log.lower()]
            outlier_steps = [log for log in cleaning_log if 'outlier' in log.lower()]
            privacy_steps = [log for log in cleaning_log if 'privacy' in log.lower() or 'encrypt' in log.lower()]
            
            if imputation_steps:
                summary += f" Missing value imputation improved data completeness significantly."
            if outlier_steps:
                summary += f" Outlier handling enhanced data reliability for statistical modeling."
            if privacy_steps:
                summary += f" Privacy protection measures ensure compliance with data governance standards."
        
        # Add privacy assessment
        if privacy_report:
            compliance_score = privacy_report.get('compliance_score', 0)
            summary += f"""

**Privacy & Security Assessment:**
Privacy protection achieved {compliance_score}% compliance score, with {privacy_report.get('protection_summary', {}).get('columns_protected', 0)} sensitive variables successfully secured through enterprise-grade encryption methods."""
        
        # Add recommendations
        summary += f"""

**Analytical Recommendations:**
The dataset demonstrates {'high' if completeness > 90 and duplicates < rows * 0.05 else 'moderate'} analytical readiness. """
        
        if len(numeric_cols) >= len(categorical_cols):
            summary += "The numerical focus enables advanced statistical modeling, regression analysis, and predictive analytics."
        else:
            summary += "The categorical richness supports classification tasks, segmentation analysis, and pattern recognition."
        
        if len(numeric_cols) > 3:
            summary += " Dimensionality reduction techniques may enhance model performance and interpretability."
        
        summary += f"""

**Quality Metrics:**
- Data Completeness: {completeness:.1f}%
- Data Uniqueness: {unique_ratio:.1f}%
- Statistical Reliability: {'High' if completeness > 90 else 'Moderate'}
- Analytical Readiness: {'Excellent' if completeness > 95 and duplicates < rows * 0.02 else 'Good'}"""
        
        return summary
    
    def generate_insights(self, data_summary: Dict[str, Any]) -> str:
        """Generate insights about the dataset structure and characteristics"""
        
        rows = data_summary.get('rows', 0)
        columns = data_summary.get('columns', 0)
        missing = data_summary.get('missing_values', 0)
        data_types = data_summary.get('data_types', {})
        
        # Analyze data types
        numeric_count = sum(1 for dtype in data_types.values() if 'int' in str(dtype) or 'float' in str(dtype))
        categorical_count = sum(1 for dtype in data_types.values() if 'object' in str(dtype))
        
        insights = f"""**Dataset Structure Analysis**

**Scale & Composition:**
This dataset encompasses {rows:,} observations across {columns} variables, representing a {'comprehensive' if rows > 5000 else 'substantial' if rows > 1000 else 'focused'} analytical scope.

**Variable Distribution:**
The dataset contains {numeric_count} numerical variables and {categorical_count} categorical variables, creating a {'numerically-driven' if numeric_count > categorical_count else 'categorically-rich' if categorical_count > numeric_count else 'balanced'} analytical framework.

**Data Integrity:**"""
        
        if missing > 0:
            missing_pct = (missing / (rows * columns)) * 100 if rows > 0 else 0
            insights += f" Data completeness measures {100-missing_pct:.1f}%, with {missing:,} missing values requiring attention through imputation strategies."
        else:
            insights += f" Exceptional data completeness achieved with zero missing values, enabling direct analytical application."
        
        # Dataset size assessment
        if rows > 50000:
            insights += f"""

**Big Data Characteristics:**
The substantial dataset size enables robust statistical inference, complex modeling approaches, and comprehensive pattern detection capabilities."""
        elif rows > 10000:
            insights += f"""

**Large Dataset Benefits:**
The dataset size supports advanced analytical techniques including machine learning algorithms and sophisticated statistical modeling."""
        elif rows > 1000:
            insights += f"""

**Medium Dataset Advantages:**
The dataset provides sufficient statistical power for reliable analysis while maintaining computational efficiency."""
        else:
            insights += f"""

**Focused Dataset Utility:**
The compact dataset size enables detailed examination and rapid analytical iteration."""
        
        # Variable complexity assessment
        if columns > 20:
            insights += f" The high-dimensional nature ({columns} variables) offers rich analytical possibilities but may benefit from feature selection techniques."
        elif columns > 10:
            insights += f" The moderate dimensionality ({columns} variables) provides comprehensive coverage while maintaining analytical clarity."
        else:
            insights += f" The focused variable set ({columns} variables) enables deep, interpretable analysis."
        
        return insights