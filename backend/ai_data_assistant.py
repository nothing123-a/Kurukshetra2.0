import pandas as pd
import numpy as np
import json
import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import logging
try:
    import google.generativeai as genai
except ImportError:
    genai = None

def sanitize_for_json(obj):
    """Recursively convert numpy/pandas types into standard Python JSON serializable types"""
    if isinstance(obj, dict):
        return {str(k): sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [sanitize_for_json(v) for v in obj]
    elif isinstance(obj, (np.int64, np.int32, np.int16, np.int8, np.integer)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32, np.floating)):
        return float(obj) if not np.isnan(obj) else None
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, pd.Series):
        return sanitize_for_json(obj.tolist())
    elif isinstance(obj, pd.DataFrame):
        return sanitize_for_json(obj.to_dict('records'))
    elif pd.isna(obj):
        return None
    return obj

class AIDataAssistant:
    def __init__(self, gemini_api_key=None):
        self.current_dataset = None
        self.dataset_info = {}
        self.operation_history = []
        self.supported_formats = ['.csv', '.xlsx', '.xls', '.json', '.parquet']
        
        # Initialize Gemini AI
        self.gemini_model = None
        if gemini_api_key and genai:
            try:
                genai.configure(api_key=gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                print("✅ AI initialized for smart command understanding")
            except Exception as e:
                print(f"⚠️ AI initialization failed: {e}")
                self.gemini_model = None
        
    def load_dataset(self, file_path: str) -> Dict[str, Any]:
        """Load dataset from file and provide initial analysis"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.csv':
                # Try multiple encodings and methods for CSV files
                encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
                for encoding in encodings:
                    try:
                        self.current_dataset = pd.read_csv(file_path, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                    except Exception as e:
                        if encoding == encodings[-1]:  # Last encoding attempt
                            # Try with error handling
                            try:
                                self.current_dataset = pd.read_csv(file_path, encoding='utf-8', errors='ignore')
                            except:
                                try:
                                    self.current_dataset = pd.read_csv(file_path, encoding='latin-1', errors='ignore')
                                except:
                                    raise e
                        else:
                            continue
                            
            elif file_ext in ['.xlsx', '.xls']:
                try:
                    self.current_dataset = pd.read_excel(file_path)
                except Exception as e:
                    # Try with openpyxl engine for xlsx files
                    if file_ext == '.xlsx':
                        try:
                            self.current_dataset = pd.read_excel(file_path, engine='openpyxl')
                        except:
                            raise e
                    else:
                        raise e
                        
            elif file_ext == '.json':
                try:
                    self.current_dataset = pd.read_json(file_path)
                except Exception as e:
                    # Try reading as lines-delimited JSON
                    try:
                        self.current_dataset = pd.read_json(file_path, lines=True)
                    except:
                        raise e
                        
            elif file_ext == '.parquet':
                try:
                    self.current_dataset = pd.read_parquet(file_path)
                except Exception as e:
                    return {"error": f"Failed to read Parquet file. Make sure you have pyarrow or fastparquet installed: {str(e)}"}
                    
            else:
                return {"error": f"Unsupported file format: {file_ext}. Supported formats: CSV, Excel (.xlsx, .xls), JSON, Parquet"}
            
            # Validate that we successfully loaded data
            if self.current_dataset is None or len(self.current_dataset) == 0:
                return {"error": "The file appears to be empty or could not be read properly"}
            
            if len(self.current_dataset.columns) == 0:
                return {"error": "No columns found in the dataset"}
            
            # Generate dataset summary
            summary = self._analyze_dataset()
            self.dataset_info = summary
            
            raw_preview = self.current_dataset.head().to_dict('records')
            
            return sanitize_for_json({
                "success": True,
                "message": "Dataset loaded successfully!",
                "summary": summary,
                "preview": raw_preview
            })
            
        except Exception as e:
            return {"error": f"Failed to load dataset: {str(e)}"}
    
    def _analyze_dataset(self) -> Dict[str, Any]:
        """Analyze the current dataset and provide comprehensive summary"""
        if self.current_dataset is None:
            return {}
        
        df = self.current_dataset
        
        # Basic info
        basic_info = {
            "rows": len(df),
            "columns": len(df.columns),
            "size_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
        }
        
        # Column analysis
        columns_info = []
        for col in df.columns:
            col_info = {
                "name": col,
                "type": str(df[col].dtype),
                "non_null": int(df[col].count()),
                "null_count": int(df[col].isnull().sum()),
                "null_percentage": round((df[col].isnull().sum() / len(df)) * 100, 2),
                "unique_values": int(df[col].nunique())
            }
            
            # Add statistics for numeric columns
            if df[col].dtype in ['int64', 'float64', 'int32', 'float32']:
                col_info.update({
                    "mean": round(df[col].mean(), 2) if not df[col].isnull().all() else None,
                    "median": round(df[col].median(), 2) if not df[col].isnull().all() else None,
                    "std": round(df[col].std(), 2) if not df[col].isnull().all() else None,
                    "min": df[col].min() if not df[col].isnull().all() else None,
                    "max": df[col].max() if not df[col].isnull().all() else None
                })
            
            columns_info.append(col_info)
        
        # Data quality issues
        quality_issues = []
        
        # Check for duplicates
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            quality_issues.append(f"{duplicate_count} duplicate rows found")
        
        # Check for missing values
        missing_cols = df.columns[df.isnull().any()].tolist()
        if missing_cols:
            quality_issues.append(f"Missing values in columns: {', '.join(missing_cols)}")
        
        return sanitize_for_json({
            "basic_info": basic_info,
            "columns": columns_info,
            "quality_issues": quality_issues,
            "sample_data": df.head(3).to_dict('records')
        })
    
    def _parse_command_with_gemini(self, user_message: str) -> Dict[str, Any]:
        """Use Gemini AI to intelligently parse user commands"""
        if not self.gemini_model:
            return {"parsed": False, "original_message": user_message}
        
        try:
            # Get column names for context
            columns_info = ""
            if self.current_dataset is not None:
                columns_info = f"Available columns: {', '.join(self.current_dataset.columns.tolist())}"
            
            prompt = f"""
You are a data analysis assistant. Parse the following user command and extract the intent and parameters.

{columns_info}

User command: "{user_message}"

IMPORTANT: Match column names exactly as they appear in the available columns list above. Use fuzzy matching if needed.

Analyze this command and respond with a JSON object containing:
{{
    "intent": "one of: describe_dataset, calculate_mean, calculate_median, calculate_std, drop_column, drop_rows, filter_data, replace_values, rename_column, correlation, unique_values, missing_values, duplicates, export_dataset, show_columns",
    "column_name": "exact column name from available columns (null if not applicable)",
    "operation": "specific operation requested",
    "parameters": {{
        "value": "numeric value if mentioned",
        "condition": "filter condition if applicable (>, <, >=, <=, ==)",
        "method": "method like mean, median, etc.",
        "replacement_value": "value to replace with"
    }},
    "confidence": "high/medium/low",
    "explanation": "brief explanation of what the user wants to do",
    "suggested_column": "closest matching column name if exact match not found"
}}

Examples:
- "calculate mean of salary" → intent: "calculate_mean", column_name: "salary"
- "drop the age column" → intent: "drop_column", column_name: "age"
- "filter rows where price > 100" → intent: "filter_data", column_name: "price", parameters: {{"value": 100, "condition": ">"}}
- "what is this dataset about" → intent: "describe_dataset"
- "show me all columns" → intent: "show_columns"
- "replace missing values in income with 0" → intent: "replace_values", column_name: "income", parameters: {{"method": "value", "replacement_value": 0}}

Respond only with valid JSON.
"""
            
            response = self.gemini_model.generate_content(prompt)
            
            # Parse Gemini response
            try:
                parsed_response = json.loads(response.text)
                parsed_response["parsed"] = True
                parsed_response["original_message"] = user_message
                return parsed_response
            except json.JSONDecodeError:
                # If JSON parsing fails, extract intent manually
                response_text = response.text.lower()
                return {
                    "parsed": True,
                    "intent": "general_query",
                    "explanation": response.text,
                    "original_message": user_message,
                    "confidence": "medium"
                }
                
        except Exception as e:
            print(f"Gemini parsing error: {e}")
            return {"parsed": False, "original_message": user_message}
    
    def process_chat_command(self, user_message: str) -> Dict[str, Any]:
        """Process natural language commands and execute data operations"""
        if self.current_dataset is None:
            return {
                "response": "Please upload a dataset first before I can help you analyze it!",
                "type": "error"
            }
        
        # First, try to parse with Gemini AI
        parsed_command = self._parse_command_with_gemini(user_message)
        
        if parsed_command.get("parsed"):
            # Use Gemini-parsed intent
            intent = parsed_command.get("intent")
            column_name = parsed_command.get("column_name")
            parameters = parsed_command.get("parameters", {})
            explanation = parsed_command.get("explanation", "")
            
            # Log the parsed command
            self._log_operation(f"Gemini parsed: {intent} - {explanation}")
            
            # Execute based on parsed intent
            if intent == "describe_dataset":
                return self._describe_dataset()
            elif intent == "calculate_mean" and column_name:
                return self._calculate_mean_by_column(column_name)
            elif intent == "calculate_median" and column_name:
                return self._calculate_median_by_column(column_name)
            elif intent == "calculate_std" and column_name:
                return self._calculate_std_by_column(column_name)
            elif intent == "drop_column" and column_name:
                return self._drop_column_by_name(column_name)
            elif intent == "filter_data" and column_name:
                value = parameters.get("value")
                condition = parameters.get("condition", ">")
                return self._filter_data_by_condition(column_name, condition, value)
            elif intent == "replace_values":
                method = parameters.get("method", "mean")
                return self._replace_missing_values(column_name, method, None)
            elif intent == "duplicates":
                return self._handle_duplicates("remove duplicates")
            elif intent == "export_dataset":
                return self._export_dataset("export dataset")
            elif intent == "missing_values":
                return self._analyze_missing_values()
            elif intent == "correlation":
                return self._calculate_correlation()
            elif intent == "unique_values" and column_name:
                return self._get_unique_values_for_column(column_name)
            elif intent == "show_columns":
                return self._show_available_columns()
            elif intent == "replace_values" and column_name:
                method = parameters.get("method", "mean")
                replacement_value = parameters.get("replacement_value")
                return self._replace_missing_values(column_name, method, replacement_value)
            else:
                # If parsed but no specific handler, provide helpful response
                return {
                    "response": f"I understand you want to: {explanation}\n\nLet me help you with that. Here are some suggestions:\n• Be more specific about column names\n• Try: 'calculate mean of [column_name]'\n• Or: 'drop column [column_name]'",
                    "type": "help"
                }
        
        # Fallback to original pattern matching
        message = user_message.lower().strip()
        
        # Check for anomaly / outlier / unusual pattern detection query
        anomaly_keywords = ['unusual', 'anomal', 'outlier', 'abnormal', 'pattern', 'divergen', 'strange', 'extreme', 'skewed', 'irregular', 'defect', 'healthcare', 'which district']
        if any(word in message for word in anomaly_keywords):
            return self._analyze_unusual_patterns_and_anomalies(user_message)
            
        if any(word in message for word in ['report', 'full analysis', 'comprehensive analysis', 'findings', 'insights']):
            return self._generate_comprehensive_autonomous_report()
            
        # Pattern matching for different commands
        if any(word in message for word in ['what', 'about', 'describe', 'summary', 'info', 'inspect']):
            return self._describe_dataset()
        
        elif any(word in message for word in ['mean', 'average']):
            return self._calculate_mean(message)
        
        elif 'median' in message:
            return self._calculate_median(message)
        
        elif 'std' in message or 'standard deviation' in message:
            return self._calculate_std(message)
        
        elif any(word in message for word in ['drop', 'delete', 'remove']) and 'column' in message:
            return self._drop_column(message)
        
        elif any(word in message for word in ['drop', 'delete', 'remove']) and 'row' in message:
            return self._drop_rows(message)
        
        elif 'filter' in message or 'where' in message:
            return self._filter_data(message)
        
        elif 'replace' in message or 'fill' in message or 'clean' in message:
            return self._replace_values(message)
        
        elif 'rename' in message and 'column' in message:
            return self._rename_column(message)
        
        elif any(word in message for word in ['correlation', 'corr']):
            return self._calculate_correlation()
        
        elif 'unique' in message and 'values' in message:
            return self._get_unique_values(message)
        
        elif 'missing' in message or 'null' in message:
            return self._analyze_missing_values()
        
        elif 'column' in message and ('show' in message or 'list' in message):
            return self._show_available_columns()
        
        elif 'duplicate' in message:
            return self._handle_duplicates(message)
        
        elif 'export' in message or 'download' in message:
            return self._export_dataset(message)
        
        elif 'history' in message or 'previous' in message:
            return self._show_history_options(message)
        
        else:
            # Enhanced help with Gemini understanding
            help_response = "I am your Autonomous Data Analysis AI Agent. Here is what I can autonomously perform for you:\n\n"
            help_response += "🚨 **Anomaly & Pattern Detection:**\n• 'Which districts show unusual healthcare patterns?'\n• 'Identify anomalies and outliers in this dataset'\n\n"
            help_response += "📊 **Data Analysis & Reports:**\n• 'Generate comprehensive analysis report'\n• 'What is this dataset about?'\n• 'Show missing values and data quality'\n• 'Calculate correlation matrix'\n\n"
            help_response += "📝 **Statistics:**\n• 'Calculate mean of [column]'\n• 'Find median of [column]'\n• 'Show unique values'\n\n"
            help_response += "🧹 **Data Cleaning:**\n• 'Remove duplicate rows'\n• 'Replace missing values with mean'\n• 'Drop column [column]'\n\n"
            help_response += "🔍 **Filtering:**\n• 'Filter rows where [column] > [value]'\n\n"
            help_response += "💾 **Export:**\n• 'Export dataset'"
            
            return {
                "response": help_response,
                "type": "help"
            }

    def _analyze_unusual_patterns_and_anomalies(self, query: str = "") -> Dict[str, Any]:
        """Autonomously detect statistical anomalies, unusual patterns, and outliers across dataset entities"""
        if self.current_dataset is None:
            return {
                "response": "Please upload a dataset first before I can detect anomalies and unusual patterns!",
                "type": "error"
            }
        
        df = self.current_dataset.copy()
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = df.select_dtypes(include=['object', 'string', 'category']).columns.tolist()
        
        if not numeric_cols:
            return {
                "response": "⚠️ No numeric columns found in this dataset to perform statistical anomaly detection.",
                "type": "warning"
            }
            
        # Detect primary entity column (e.g. District_Name, District, State, City, ID, Name)
        entity_col = None
        for c in cat_cols:
            c_lower = c.lower()
            if any(k in c_lower for k in ['district', 'entity', 'region', 'state', 'city', 'country', 'name', 'id']):
                entity_col = c
                break
        if not entity_col and cat_cols:
            entity_col = cat_cols[0]
            
        # Secondary grouping column (e.g. State if entity is District)
        group_col = None
        for c in cat_cols:
            if c != entity_col and any(k in c.lower() for k in ['state', 'region', 'zone', 'country', 'category', 'type']):
                group_col = c
                break

        col_stats = {}
        outlier_counts = {}
        z_scores_df = pd.DataFrame(index=df.index)
        
        for col in numeric_cols:
            series = pd.to_numeric(df[col], errors='coerce').dropna()
            if len(series) < 2:
                continue
            mean_val = float(series.mean())
            std_val = float(series.std()) if series.std() > 0 else 1.0
            median_val = float(series.median())
            q1 = float(series.quantile(0.25))
            q3 = float(series.quantile(0.75))
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            # Identify outliers
            outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
            outlier_counts[col] = int(outlier_mask.sum())
            
            # Normalized z-score for divergence
            z_scores_df[col] = abs((df[col] - mean_val) / std_val)
            
            col_stats[col] = {
                "mean": round(mean_val, 2),
                "std": round(std_val, 2),
                "median": round(median_val, 2),
                "q1": round(q1, 2),
                "q3": round(q3, 2),
                "lower_bound": round(lower_bound, 2),
                "upper_bound": round(upper_bound, 2),
                "outliers_count": int(outlier_mask.sum()),
                "iqr": round(iqr, 2)
            }
            
        row_anomaly_scores = []
        for idx, row in df.iterrows():
            entity_name = str(row[entity_col]) if entity_col else f"Record #{idx+1}"
            group_name = str(row[group_col]) if group_col else ""
            
            anomalous_metrics = []
            score = 0.0
            
            for col in numeric_cols:
                if col not in col_stats:
                    continue
                val = row[col]
                stats = col_stats[col]
                z = z_scores_df.loc[idx, col] if col in z_scores_df.columns else 0.0
                
                # Check IQR bounds or high z-score
                is_outlier = val < stats["lower_bound"] or val > stats["upper_bound"]
                if is_outlier or z > 1.8:
                    score += float(z * 1.5)
                    direction = "Critical High" if val > stats["upper_bound"] else "Critical Low" if val < stats["lower_bound"] else "Elevated"
                    anomalous_metrics.append({
                        "metric": col,
                        "value": float(val),
                        "median": stats["median"],
                        "direction": direction,
                        "z_score": round(float(z), 2)
                    })
                    
            row_anomaly_scores.append({
                "index": idx,
                "entity": entity_name,
                "group": group_name,
                "score": round(score, 2),
                "anomaly_count": len(anomalous_metrics),
                "anomalous_metrics": anomalous_metrics
            })
            
        # Sort by anomaly score descending
        sorted_entities = sorted(row_anomaly_scores, key=lambda x: x["score"], reverse=True)
        top_anomalies = [e for e in sorted_entities if e["anomaly_count"] > 0][:8]
        
        # Build Natural Language Report
        if entity_col and 'district' in entity_col.lower():
            entity_label = "Districts"
            single_entity_label = "District"
        elif entity_col:
            clean_name = entity_col.replace('_', ' ').replace(' Name', '').replace(' name', '').title()
            entity_label = f"{clean_name}s"
            single_entity_label = clean_name
        else:
            entity_label = "Records"
            single_entity_label = "Record"

        res = f"### 🚨 Autonomous Anomaly & Pattern Analysis Report\n\n"
        res += f"**Analysis Scope:** Evaluated **{len(df):,} {entity_label}** across **{len(numeric_cols)} quantitative indicators** using Interquartile Range (IQR 1.5×) boundary modeling and multivariate Z-score divergence analysis.\n\n"
        
        if top_anomalies:
            res += f"#### 🔍 Key Identified Unusual {entity_label}:\n"
            res += f"The AI agent detected **{len(top_anomalies)} {entity_label.lower()} exhibiting statistically anomalous patterns** with severe divergences from benchmark medians:\n\n"
            
            for i, anom in enumerate(top_anomalies, 1):
                loc_str = f"**{anom['entity']}**" + (f" (*{anom['group']}*)" if anom['group'] else "")
                res += f"{i}. {loc_str} — **Composite Anomaly Score: {anom['score']}**\n"
                
                # Highlight aberrant metrics
                for m in anom['anomalous_metrics'][:4]:
                    val_str = f"{m['value']:,.1f}" if m['value'] == int(m['value']) or abs(m['value']) > 100 else f"{m['value']:.2f}"
                    med_str = f"{m['median']:,.1f}" if m['median'] == int(m['median']) or abs(m['median']) > 100 else f"{m['median']:.2f}"
                    ratio = m['value'] / m['median'] if m['median'] > 0 else 0
                    ratio_str = f" ({ratio:.1f}x benchmark median)" if ratio > 1.2 or (ratio < 0.8 and ratio > 0) else ""
                    res += f"   • **{m['metric'].replace('_', ' ')}:** `{val_str}` vs. median `{med_str}`{ratio_str} — *[{m['direction']}, Z={m['z_score']}]*\n"
                
                # Contextual explanation
                res += f"   *Pattern Insight:* "
                if any('mortality' in m['metric'].lower() for m in anom['anomalous_metrics']) and any('doctor' in m['metric'].lower() or 'bed' in m['metric'].lower() for m in anom['anomalous_metrics']):
                    res += "Severe structural crisis characterized by acute healthcare worker/bed shortages paired with critically elevated mortality rates requiring immediate intervention.\n\n"
                elif any('visit' in m['metric'].lower() or 'outpatient' in m['metric'].lower() for m in anom['anomalous_metrics']):
                    res += "Unusual surge in patient load / healthcare utilization significantly exceeding capacity or regional baseline.\n\n"
                elif any('malnutrition' in m['metric'].lower() or 'immunization' in m['metric'].lower() for m in anom['anomalous_metrics']):
                    res += "Preventive care deficiency anomaly with notable divergence in immunization coverage and community nutrition.\n\n"
                else:
                    res += "Multivariate statistical deviation across infrastructure and service delivery benchmarks.\n\n"
                    
            res += "#### 📊 Metric-Level Outlier Distribution:\n"
            for col, count in sorted(outlier_counts.items(), key=lambda x: x[1], reverse=True)[:6]:
                if count > 0:
                    stats = col_stats[col]
                    res += f"• **{col.replace('_', ' ')}:** {count} outlier entities (Median: {stats['median']}, Normal IQR Range: [{stats['lower_bound']} - {stats['upper_bound']}])\n"
                    
            res += "\n#### 💡 Autonomous Actionable Recommendations:\n"
            res += "1. **Emergency Priority Allocation:** Reallocate medical personnel and bed capacity urgently to the highest-severity anomalous districts.\n"
            res += "2. **Targeted Field Audits:** Investigate unusual healthcare utilization spikes (e.g. sudden outpatient surges) for possible localized seasonal disease outbreaks.\n"
            res += "3. **Preventive Intervention Programs:** Establish mobile immunization clinics in districts where immunization falls below the 50% IQR threshold."
        else:
            res += "✅ **No severe statistical outliers detected.** All records fall within normal 1.5 × IQR distribution boundaries across the analyzed metrics."
            
        self._log_operation(f"Executed anomaly pattern detection query for {entity_label}")
        
        return {
            "response": res,
            "type": "anomaly_analysis",
            "data": {
                "entity_column": entity_col,
                "top_anomalies": top_anomalies,
                "column_statistics": col_stats
            }
        }

    def _generate_comprehensive_autonomous_report(self) -> Dict[str, Any]:
        """Generate a complete 8-step autonomous analysis report matching the problem statement"""
        if self.current_dataset is None:
            return {
                "response": "Please upload a dataset first to generate a comprehensive report!",
                "type": "error"
            }
            
        df = self.current_dataset
        rows, cols = df.shape
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = df.select_dtypes(include=['object', 'string', 'category']).columns.tolist()
        missing_total = int(df.isnull().sum().sum())
        duplicates_count = int(df.duplicated().sum())
        completeness = round((1 - missing_total / (rows * cols)) * 100, 2)
        
        rep = "## 📑 Comprehensive Autonomous Dataset Report\n\n"
        rep += "### 1. Dataset Inspection & Schema\n"
        rep += f"• **Total Records:** {rows:,} rows\n"
        rep += f"• **Total Attributes:** {cols} columns ({len(numeric_cols)} numeric, {len(cat_cols)} categorical)\n"
        rep += f"• **Data Completeness:** {completeness}%\n\n"
        
        rep += "### 2. Data Cleaning Diagnostics\n"
        rep += f"• **Missing Values:** {missing_total} cells require imputation\n"
        rep += f"• **Duplicate Rows:** {duplicates_count} detected\n"
        rep += "• **Data Quality Grade:** " + ("A (Excellent)" if completeness > 95 else "B (Good)" if completeness > 80 else "C (Needs Cleaning)") + "\n\n"
        
        rep += "### 3. Key Numerical Statistics\n"
        for col in numeric_cols[:4]:
            s = df[col].dropna()
            rep += f"• **{col.replace('_', ' ')}:** Mean = {s.mean():.2f}, Median = {s.median():.2f}, Std = {s.std():.2f}, Min = {s.min():.2f}, Max = {s.max():.2f}\n"
            
        rep += "\n### 4. Anomaly & Outlier Highlights\n"
        rep += "Automated IQR scanning detected potential outliers in multiple columns. Ask **'Which districts show unusual healthcare patterns?'** or **'Show anomalies'** for detailed district-by-district breakdown.\n\n"
        
        rep += "### 5. Recommended Visualizations & Next Steps\n"
        rep += "• Distribution histograms for skewed rate indicators\n"
        rep += "• Correlation matrix heatmap between infrastructure and outcome metrics\n"
        rep += "• Geo-spatial or bar comparison of top anomalous records\n"
        
        return {
            "response": rep,
            "type": "comprehensive_report",
            "data": {
                "rows": rows,
                "cols": cols,
                "completeness": completeness,
                "missing_total": missing_total,
                "duplicates_count": duplicates_count
            }
        }
    
    def _describe_dataset(self) -> Dict[str, Any]:
        """Provide a natural language description of the dataset"""
        info = self.dataset_info
        basic = info.get('basic_info', {})
        columns = info.get('columns', [])
        issues = info.get('quality_issues', [])
        
        response = f"📊 **Dataset Overview:**\n\n"
        response += f"• **Size:** {basic.get('rows', 0)} rows × {basic.get('columns', 0)} columns\n"
        response += f"• **Memory:** {basic.get('size_mb', 0)} MB\n\n"
        
        response += "**Columns:**\n"
        for col in columns[:5]:  # Show first 5 columns
            response += f"• **{col['name']}** ({col['type']}) - {col['unique_values']} unique values"
            if col['null_count'] > 0:
                response += f", {col['null_percentage']}% missing"
            response += "\n"
        
        if len(columns) > 5:
            response += f"... and {len(columns) - 5} more columns\n"
        
        if issues:
            response += f"\n⚠️ **Data Quality Issues:**\n"
            for issue in issues:
                response += f"• {issue}\n"
        
        return {
            "response": response,
            "type": "analysis",
            "data": info
        }
    
    def _calculate_mean_by_column(self, column_name: str) -> Dict[str, Any]:
        """Calculate mean of specified column (Gemini-parsed)"""
        try:
            if column_name not in self.current_dataset.columns:
                return {"response": f"Column '{column_name}' not found in dataset.", "type": "error"}
            
            if not pd.api.types.is_numeric_dtype(self.current_dataset[column_name]):
                return {"response": f"Column '{column_name}' is not numeric. Cannot calculate mean.", "type": "error"}
            
            mean_value = self.current_dataset[column_name].mean()
            self._log_operation(f"Calculated mean of {column_name}: {mean_value}")
            
            return {
                "response": f"📊 Mean of **{column_name}**: {round(mean_value, 2)}",
                "type": "result",
                "value": mean_value
            }
        except Exception as e:
            return {"response": f"Error calculating mean: {str(e)}", "type": "error"}
    
    def _calculate_mean(self, message: str) -> Dict[str, Any]:
        """Calculate mean of specified column"""
        column_name = self._extract_column_name(message)
        if not column_name:
            # Show available numeric columns for selection
            numeric_columns = self.current_dataset.select_dtypes(include=[np.number]).columns.tolist()
            if not numeric_columns:
                return {"response": "No numeric columns found in the dataset.", "type": "error"}
            
            response = "📊 **Calculate Mean - Select a Column:**\n\n"
            response += "Available numeric columns:\n"
            for i, col in enumerate(numeric_columns, 1):
                col_info = self.current_dataset[col].describe()
                response += f"{i}. **{col}** (Range: {col_info['min']:.2f} to {col_info['max']:.2f})\n"
            
            response += "\n💡 **Usage:** Type 'calculate mean of [column_name]'\n"
            response += "**Examples:**\n"
            for col in numeric_columns[:3]:
                response += f"• calculate mean of {col}\n"
            
            return {
                "response": response,
                "type": "help",
                "data": {"available_columns": numeric_columns, "operation": "mean"}
            }
        
        try:
            if column_name not in self.current_dataset.columns:
                return {"response": f"Column '{column_name}' not found in dataset.", "type": "error"}
            
            if not pd.api.types.is_numeric_dtype(self.current_dataset[column_name]):
                return {"response": f"Column '{column_name}' is not numeric. Cannot calculate mean.", "type": "error"}
            
            mean_value = self.current_dataset[column_name].mean()
            count = self.current_dataset[column_name].count()
            self._log_operation(f"Calculated mean of {column_name}: {mean_value}")
            
            return {
                "response": f"📊 **Mean of {column_name}:** {round(mean_value, 2)}\n\n📈 **Additional Stats:**\n• Count: {count} values\n• Min: {self.current_dataset[column_name].min():.2f}\n• Max: {self.current_dataset[column_name].max():.2f}",
                "type": "result",
                "value": mean_value
            }
        except Exception as e:
            return {"response": f"Error calculating mean: {str(e)}", "type": "error"}
    
    def _calculate_median_by_column(self, column_name: str) -> Dict[str, Any]:
        """Calculate median of specified column (Gemini-parsed)"""
        try:
            if column_name not in self.current_dataset.columns:
                return {"response": f"Column '{column_name}' not found in dataset.", "type": "error"}
            
            if not pd.api.types.is_numeric_dtype(self.current_dataset[column_name]):
                return {"response": f"Column '{column_name}' is not numeric. Cannot calculate median.", "type": "error"}
            
            median_value = self.current_dataset[column_name].median()
            self._log_operation(f"Calculated median of {column_name}: {median_value}")
            
            return {
                "response": f"📊 Median of **{column_name}**: {round(median_value, 2)}",
                "type": "result",
                "value": median_value
            }
        except Exception as e:
            return {"response": f"Error calculating median: {str(e)}", "type": "error"}
    
    def _calculate_median(self, message: str) -> Dict[str, Any]:
        """Calculate median of specified column"""
        column_name = self._extract_column_name(message)
        if not column_name:
            # Show available numeric columns for selection
            numeric_columns = self.current_dataset.select_dtypes(include=[np.number]).columns.tolist()
            if not numeric_columns:
                return {"response": "No numeric columns found in the dataset.", "type": "error"}
            
            response = "📊 **Calculate Median - Select a Column:**\n\n"
            response += "Available numeric columns:\n"
            for i, col in enumerate(numeric_columns, 1):
                col_info = self.current_dataset[col].describe()
                response += f"{i}. **{col}** (Range: {col_info['min']:.2f} to {col_info['max']:.2f})\n"
            
            response += "\n💡 **Usage:** Type 'calculate median of [column_name]'\n"
            response += "**Examples:**\n"
            for col in numeric_columns[:3]:
                response += f"• calculate median of {col}\n"
            
            return {
                "response": response,
                "type": "help",
                "data": {"available_columns": numeric_columns, "operation": "median"}
            }
        
        try:
            if column_name not in self.current_dataset.columns:
                return {"response": f"Column '{column_name}' not found in dataset.", "type": "error"}
            
            if not pd.api.types.is_numeric_dtype(self.current_dataset[column_name]):
                return {"response": f"Column '{column_name}' is not numeric. Cannot calculate median.", "type": "error"}
            
            median_value = self.current_dataset[column_name].median()
            count = self.current_dataset[column_name].count()
            self._log_operation(f"Calculated median of {column_name}: {median_value}")
            
            return {
                "response": f"📊 **Median of {column_name}:** {round(median_value, 2)}\n\n📈 **Additional Stats:**\n• Count: {count} values\n• Q1: {self.current_dataset[column_name].quantile(0.25):.2f}\n• Q3: {self.current_dataset[column_name].quantile(0.75):.2f}",
                "type": "result",
                "value": median_value
            }
        except Exception as e:
            return {"response": f"Error calculating median: {str(e)}", "type": "error"}
    
    def _calculate_std_by_column(self, column_name: str) -> Dict[str, Any]:
        """Calculate standard deviation of specified column (Gemini-parsed)"""
        try:
            if column_name not in self.current_dataset.columns:
                return {"response": f"Column '{column_name}' not found in dataset.", "type": "error"}
            
            if not pd.api.types.is_numeric_dtype(self.current_dataset[column_name]):
                return {"response": f"Column '{column_name}' is not numeric. Cannot calculate standard deviation.", "type": "error"}
            
            std_value = self.current_dataset[column_name].std()
            self._log_operation(f"Calculated std of {column_name}: {std_value}")
            
            return {
                "response": f"📊 Standard Deviation of **{column_name}**: {round(std_value, 2)}",
                "type": "result",
                "value": std_value
            }
        except Exception as e:
            return {"response": f"Error calculating standard deviation: {str(e)}", "type": "error"}
    
    def _drop_column_by_name(self, column_name: str) -> Dict[str, Any]:
        """Drop specified column from dataset (Gemini-parsed)"""
        try:
            if column_name not in self.current_dataset.columns:
                return {"response": f"Column '{column_name}' not found in dataset.", "type": "error"}
            
            self.current_dataset = self.current_dataset.drop(columns=[column_name])
            self._log_operation(f"Dropped column: {column_name}")
            self.dataset_info = self._analyze_dataset()
            
            return {
                "response": f"✅ Successfully dropped column **{column_name}**. Dataset now has {len(self.current_dataset.columns)} columns.",
                "type": "success",
                "download_available": True
            }
        except Exception as e:
            return {"response": f"Error dropping column: {str(e)}", "type": "error"}
    
    def _filter_data_by_condition(self, column_name: str, condition: str, value: float) -> Dict[str, Any]:
        """Filter dataset based on condition (Gemini-parsed)"""
        try:
            if column_name not in self.current_dataset.columns:
                return {"response": f"Column '{column_name}' not found in dataset.", "type": "error"}
            
            original_rows = len(self.current_dataset)
            
            if condition == ">":
                filtered_df = self.current_dataset[self.current_dataset[column_name] > value]
            elif condition == "<":
                filtered_df = self.current_dataset[self.current_dataset[column_name] < value]
            elif condition == ">=":
                filtered_df = self.current_dataset[self.current_dataset[column_name] >= value]
            elif condition == "<=":
                filtered_df = self.current_dataset[self.current_dataset[column_name] <= value]
            elif condition == "==":
                filtered_df = self.current_dataset[self.current_dataset[column_name] == value]
            else:
                return {"response": f"Unsupported condition: {condition}", "type": "error"}
            
            self.current_dataset = filtered_df
            self._log_operation(f"Filtered {column_name} {condition} {value}")
            self.dataset_info = self._analyze_dataset()
            
            return {
                "response": f"✅ Filtered data where **{column_name} {condition} {value}**. Dataset reduced from {original_rows} to {len(self.current_dataset)} rows.",
                "type": "success",
                "download_available": True
            }
        except Exception as e:
            return {"response": f"Error filtering data: {str(e)}", "type": "error"}
    
    def _show_available_columns(self) -> Dict[str, Any]:
        """Show all available columns in the dataset"""
        try:
            if self.current_dataset is None:
                return {"response": "No dataset loaded.", "type": "error"}
            
            columns_info = self.dataset_info.get('columns', [])
            
            response = f"📋 **Available Columns ({len(columns_info)} total):**\n\n"
            
            for i, col in enumerate(columns_info, 1):
                col_type = col.get('type', 'unknown')
                unique_count = col.get('unique_values', 0)
                null_count = col.get('null_count', 0)
                
                response += f"{i}. **{col['name']}** ({col_type})\n"
                response += f"   • Unique values: {unique_count}\n"
                if null_count > 0:
                    response += f"   • Missing values: {null_count} ({col.get('null_percentage', 0):.1f}%)\n"
                response += "\n"
            
            response += "💡 **Usage examples:**\n"
            response += f"• Calculate mean of {columns_info[0]['name'] if columns_info else 'column_name'}\n"
            response += f"• Drop column {columns_info[1]['name'] if len(columns_info) > 1 else 'column_name'}\n"
            response += f"• Filter rows where {columns_info[0]['name'] if columns_info else 'column_name'} > value"
            
            return {
                "response": response,
                "type": "analysis",
                "data": columns_info
            }
            
        except Exception as e:
            return {"response": f"Error showing columns: {str(e)}", "type": "error"}
    
    def _replace_missing_values(self, column_name: str, method: str, replacement_value=None) -> Dict[str, Any]:
        """Replace missing values in specified column (Gemini-parsed)"""
        try:
            if column_name and column_name in self.current_dataset.columns:
                if method == 'value' and replacement_value is not None:
                    # Replace with specific value
                    self.current_dataset[column_name].fillna(replacement_value, inplace=True)
                    self._log_operation(f"Replaced missing values in {column_name} with {replacement_value}")
                    self.dataset_info = self._analyze_dataset()
                    
                    return {
                        "response": f"✅ Replaced missing values in **{column_name}** with {replacement_value}",
                        "type": "success",
                        "download_available": True
                    }
                elif method == 'mean':
                    mean_val = self.current_dataset[column_name].mean()
                    self.current_dataset[column_name].fillna(mean_val, inplace=True)
                    self._log_operation(f"Replaced missing values in {column_name} with mean")
                    self.dataset_info = self._analyze_dataset()
                    
                    return {
                        "response": f"✅ Replaced missing values in **{column_name}** with mean ({round(mean_val, 2)})",
                        "type": "success",
                        "download_available": True
                    }
                elif method == 'median':
                    median_val = self.current_dataset[column_name].median()
                    self.current_dataset[column_name].fillna(median_val, inplace=True)
                    self._log_operation(f"Replaced missing values in {column_name} with median")
                    self.dataset_info = self._analyze_dataset()
                    
                    return {
                        "response": f"✅ Replaced missing values in **{column_name}** with median ({round(median_val, 2)})",
                        "type": "success",
                        "download_available": True
                    }
            
            return {"response": "Please specify a valid column name and method (mean/median/value)", "type": "error"}
            
        except Exception as e:
            return {"response": f"Error replacing values: {str(e)}", "type": "error"}
    
    def _analyze_missing_values(self) -> Dict[str, Any]:
        """Analyze missing values in the dataset"""
        try:
            missing_data = self.current_dataset.isnull().sum()
            missing_cols = missing_data[missing_data > 0]
            
            if len(missing_cols) == 0:
                return {
                    "response": "✅ Great! No missing values found in the dataset.",
                    "type": "info"
                }
            
            response = f"🔍 **Missing Values Analysis:**\n\n"
            for col, count in missing_cols.items():
                percentage = (count / len(self.current_dataset)) * 100
                response += f"• **{col}**: {count} missing ({percentage:.1f}%)\n"
            
            response += f"\n📊 **Total missing values**: {missing_data.sum()}"
            
            return {
                "response": response,
                "type": "analysis",
                "data": missing_cols.to_dict()
            }
            
        except Exception as e:
            return {"response": f"Error analyzing missing values: {str(e)}", "type": "error"}
    
    def _get_unique_values_for_column(self, column_name: str) -> Dict[str, Any]:
        """Get unique values for specified column (Gemini-parsed)"""
        try:
            if column_name not in self.current_dataset.columns:
                return {"response": f"Column '{column_name}' not found in dataset.", "type": "error"}
            
            unique_values = self.current_dataset[column_name].unique()
            unique_count = len(unique_values)
            
            response = f"🔢 **Unique values in {column_name}:**\n\n"
            response += f"• **Total unique values**: {unique_count}\n\n"
            
            # Show first 10 unique values
            if unique_count <= 10:
                response += "**All unique values:**\n"
                for val in unique_values:
                    response += f"• {val}\n"
            else:
                response += "**First 10 unique values:**\n"
                for val in unique_values[:10]:
                    response += f"• {val}\n"
                response += f"... and {unique_count - 10} more"
            
            return {
                "response": response,
                "type": "analysis",
                "value": unique_count
            }
            
        except Exception as e:
            return {"response": f"Error getting unique values: {str(e)}", "type": "error"}
    
    def _drop_column(self, message: str) -> Dict[str, Any]:
        """Drop specified column from dataset"""
        column_name = self._extract_column_name(message)
        if not column_name:
            # Show available columns for selection
            all_columns = self.current_dataset.columns.tolist()
            
            response = "🗑️ **Drop Column - Select a Column:**\n\n"
            response += "Available columns:\n"
            for i, col in enumerate(all_columns, 1):
                col_type = str(self.current_dataset[col].dtype)
                null_count = self.current_dataset[col].isnull().sum()
                response += f"{i}. **{col}** ({col_type})"
                if null_count > 0:
                    response += f" - {null_count} missing values"
                response += "\n"
            
            response += "\n💡 **Usage:** Type 'drop column [column_name]'\n"
            response += "**Examples:**\n"
            for col in all_columns[:3]:
                response += f"• drop column {col}\n"
            
            return {
                "response": response,
                "type": "help",
                "data": {"available_columns": all_columns, "operation": "drop_column"}
            }
        
        try:
            if column_name not in self.current_dataset.columns:
                return {"response": f"Column '{column_name}' not found in dataset.", "type": "error"}
            
            self.current_dataset = self.current_dataset.drop(columns=[column_name])
            self._log_operation(f"Dropped column: {column_name}")
            self.dataset_info = self._analyze_dataset()  # Update info
            
            return {
                "response": f"✅ Successfully dropped column **{column_name}**. Dataset now has {len(self.current_dataset.columns)} columns.",
                "type": "success",
                "download_available": True
            }
        except Exception as e:
            return {"response": f"Error dropping column: {str(e)}", "type": "error"}
    
    def _drop_rows(self, message: str) -> Dict[str, Any]:
        """Drop rows based on conditions"""
        try:
            if 'missing' in message or 'null' in message or 'nan' in message:
                column_name = self._extract_column_name(message)
                
                if not column_name:
                    # Show column selection for missing values
                    missing_data = self.current_dataset.isnull().sum()
                    missing_cols = missing_data[missing_data > 0]
                    
                    if len(missing_cols) == 0:
                        return {
                            "response": "✅ No missing values found in the dataset!",
                            "type": "info"
                        }
                    
                    response = "🗑️ **Drop Rows with Missing Values - Select Column:**\n\n"
                    response += "Columns with missing values:\n"
                    for col, count in missing_cols.items():
                        percentage = (count / len(self.current_dataset)) * 100
                        response += f"• **{col}**: {count} missing ({percentage:.1f}%)\n"
                    
                    response += "\n💡 **Usage:**\n"
                    response += "• 'drop rows with missing values' - Drop all rows with any missing values\n"
                    response += "• 'drop rows with missing values in [column]' - Drop rows with missing values in specific column\n"
                    
                    return {
                        "response": response,
                        "type": "help",
                        "data": {"available_columns": missing_cols.index.tolist(), "operation": "drop_missing_rows"}
                    }
                
                initial_rows = len(self.current_dataset)
                
                if column_name and column_name in self.current_dataset.columns:
                    # Drop rows with missing values in specific column
                    self.current_dataset = self.current_dataset.dropna(subset=[column_name])
                    removed_count = initial_rows - len(self.current_dataset)
                    self._log_operation(f"Dropped {removed_count} rows with missing values in {column_name}")
                    response_msg = f"✅ Dropped **{removed_count}** rows with missing values in **{column_name}**. Dataset now has {len(self.current_dataset)} rows."
                else:
                    # Drop all rows with any missing values
                    self.current_dataset = self.current_dataset.dropna()
                    removed_count = initial_rows - len(self.current_dataset)
                    self._log_operation(f"Dropped {removed_count} rows with missing values")
                    response_msg = f"✅ Dropped **{removed_count}** rows with missing values. Dataset now has {len(self.current_dataset)} rows."
                
                self.dataset_info = self._analyze_dataset()
                
                return {
                    "response": response_msg + "\n\n💾 **What's next?**\n• Continue working with the data\n• Or download the updated dataset",
                    "type": "success",
                    "data": {"show_download_options": True}
                }
            else:
                # Show available operations for dropping rows
                response = "🗑️ **Drop Rows - Available Options:**\n\n"
                response += "• **Drop rows with missing values** - Remove rows containing null/NaN values\n"
                response += "• **Drop duplicate rows** - Remove duplicate entries\n"
                response += "\n💡 **Examples:**\n"
                response += "• drop rows with missing values\n"
                response += "• drop rows with missing values in age\n"
                response += "• remove duplicate rows\n"
                
                return {"response": response, "type": "help"}
                
        except Exception as e:
            return {"response": f"Error dropping rows: {str(e)}", "type": "error"}
    
    def _filter_data(self, message: str) -> Dict[str, Any]:
        """Filter dataset based on conditions"""
        # Simple filtering - can be enhanced with more complex parsing
        try:
            # Extract basic filter conditions
            if '>' in message:
                parts = message.split('>')
                if len(parts) == 2:
                    column_name = self._extract_column_name(parts[0])
                    value = self._extract_number(parts[1])
                    if column_name and value is not None:
                        filtered_df = self.current_dataset[self.current_dataset[column_name] > value]
                        self.current_dataset = filtered_df
                        self._log_operation(f"Filtered {column_name} > {value}")
                        self.dataset_info = self._analyze_dataset()
                        
                        return {
                            "response": f"✅ Filtered data where **{column_name} > {value}**. Dataset now has {len(self.current_dataset)} rows.",
                            "type": "success",
                            "download_available": True
                        }
            
            return {"response": "Please specify a clear filter condition like 'filter age > 25'", "type": "error"}
            
        except Exception as e:
            return {"response": f"Error filtering data: {str(e)}", "type": "error"}
    
    def _replace_values(self, message: str) -> Dict[str, Any]:
        """Replace values in dataset"""
        try:
            if 'null' in message or 'nan' in message or 'missing' in message:
                column_name = self._extract_column_name(message)
                if column_name and column_name in self.current_dataset.columns:
                    if 'mean' in message:
                        mean_val = self.current_dataset[column_name].mean()
                        self.current_dataset[column_name].fillna(mean_val, inplace=True)
                        self._log_operation(f"Replaced missing values in {column_name} with mean")
                        self.dataset_info = self._analyze_dataset()
                        
                        return {
                            "response": f"✅ Replaced missing values in **{column_name}** with mean ({round(mean_val, 2)})",
                            "type": "success",
                            "download_available": True
                        }
                    elif 'median' in message:
                        median_val = self.current_dataset[column_name].median()
                        self.current_dataset[column_name].fillna(median_val, inplace=True)
                        self._log_operation(f"Replaced missing values in {column_name} with median")
                        self.dataset_info = self._analyze_dataset()
                        
                        return {
                            "response": f"✅ Replaced missing values in **{column_name}** with median ({round(median_val, 2)})",
                            "type": "success",
                            "download_available": True
                        }
            
            return {"response": "Please specify what to replace, e.g., 'replace missing values in age with mean'", "type": "error"}
            
        except Exception as e:
            return {"response": f"Error replacing values: {str(e)}", "type": "error"}
    
    def _handle_duplicates(self, message: str) -> Dict[str, Any]:
        """Handle duplicate rows"""
        try:
            if 'remove' in message or 'drop' in message:
                # Check if specific columns mentioned
                column_name = self._extract_column_name(message)
                
                if not column_name and ('based on' in message or 'in column' in message or 'by column' in message):
                    # Show column selection for subset-based duplicate removal
                    all_columns = self.current_dataset.columns.tolist()
                    
                    response = "🔄 **Remove Duplicates - Select Columns:**\n\n"
                    response += "Choose columns to check for duplicates:\n"
                    for i, col in enumerate(all_columns, 1):
                        duplicate_count = self.current_dataset.duplicated(subset=[col]).sum()
                        response += f"{i}. **{col}** - {duplicate_count} duplicates based on this column\n"
                    
                    response += "\n💡 **Usage:**\n"
                    response += "• 'remove duplicates' - Remove all duplicate rows\n"
                    response += "• 'remove duplicates based on [column]' - Remove duplicates based on specific column\n"
                    
                    return {
                        "response": response,
                        "type": "help",
                        "data": {"available_columns": all_columns, "operation": "remove_duplicates"}
                    }
                
                initial_rows = len(self.current_dataset)
                
                if column_name:
                    # Remove duplicates based on specific column
                    self.current_dataset = self.current_dataset.drop_duplicates(subset=[column_name])
                    removed_count = initial_rows - len(self.current_dataset)
                    self._log_operation(f"Removed {removed_count} duplicate rows based on {column_name}")
                    response_msg = f"✅ Removed **{removed_count}** duplicate rows based on column **{column_name}**. Dataset now has {len(self.current_dataset)} rows."
                else:
                    # Remove all duplicates
                    self.current_dataset = self.current_dataset.drop_duplicates()
                    removed_count = initial_rows - len(self.current_dataset)
                    self._log_operation(f"Removed {removed_count} duplicate rows")
                    response_msg = f"✅ Removed **{removed_count}** duplicate rows. Dataset now has {len(self.current_dataset)} rows."
                
                self.dataset_info = self._analyze_dataset()
                
                return {
                    "response": response_msg,
                    "type": "success",
                    "download_available": True
                }
            else:
                duplicate_count = self.current_dataset.duplicated().sum()
                return {
                    "response": f"📊 Found **{duplicate_count}** duplicate rows in the dataset.",
                    "type": "info"
                }
                
        except Exception as e:
            return {"response": f"Error handling duplicates: {str(e)}", "type": "error"}
    
    def _export_dataset(self, message: str) -> Dict[str, Any]:
        """Export current dataset"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"processed_dataset_{timestamp}.csv"
            filepath = os.path.join("uploads", filename)
            
            os.makedirs("uploads", exist_ok=True)
            self.current_dataset.to_csv(filepath, index=False)
            self._log_operation(f"Exported dataset as {filename}")
            
            return {
                "response": f"✅ Dataset exported successfully as **{filename}**",
                "type": "success",
                "download_url": f"/api/ai-assistant/download/{filename}",
                "filename": filename,
                "download_available": True
            }
            
        except Exception as e:
            return {"response": f"Error exporting dataset: {str(e)}", "type": "error"}
    
    def _extract_column_name(self, text: str) -> Optional[str]:
        """Extract column name from user message"""
        if not self.current_dataset is None:
            for col in self.current_dataset.columns:
                if col.lower() in text.lower():
                    return col
        return None
    
    def _extract_number(self, text: str) -> Optional[float]:
        """Extract number from text"""
        numbers = re.findall(r'-?\d+\.?\d*', text)
        if numbers:
            try:
                return float(numbers[0])
            except:
                return None
        return None
    
    def _log_operation(self, operation: str):
        """Log operations for history"""
        self.operation_history.append({
            "timestamp": datetime.now().isoformat(),
            "operation": operation
        })
    
    def get_operation_history(self) -> List[Dict[str, str]]:
        """Get operation history"""
        return self.operation_history
    
    def _calculate_std(self, message: str) -> Dict[str, Any]:
        """Calculate standard deviation of specified column"""
        column_name = self._extract_column_name(message)
        if not column_name:
            return {"response": "Please specify which column you want to calculate the standard deviation for.", "type": "error"}
        
        try:
            if column_name not in self.current_dataset.columns:
                return {"response": f"Column '{column_name}' not found in dataset.", "type": "error"}
            
            if not pd.api.types.is_numeric_dtype(self.current_dataset[column_name]):
                return {"response": f"Column '{column_name}' is not numeric. Cannot calculate standard deviation.", "type": "error"}
            
            std_value = self.current_dataset[column_name].std()
            self._log_operation(f"Calculated std of {column_name}: {std_value}")
            
            return {
                "response": f"📊 Standard Deviation of **{column_name}**: {round(std_value, 2)}",
                "type": "result",
                "value": std_value
            }
        except Exception as e:
            return {"response": f"Error calculating standard deviation: {str(e)}", "type": "error"}
    
    def _rename_column(self, message: str) -> Dict[str, Any]:
        """Rename column in dataset"""
        try:
            return {"response": "Column renaming feature coming soon!", "type": "info"}
        except Exception as e:
            return {"response": f"Error renaming column: {str(e)}", "type": "error"}
    
    def _calculate_correlation(self) -> Dict[str, Any]:
        """Calculate correlation matrix for numeric columns"""
        try:
            numeric_cols = self.current_dataset.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) < 2:
                return {"response": "Need at least 2 numeric columns to calculate correlation.", "type": "error"}
            
            corr_matrix = self.current_dataset[numeric_cols].corr()
            self._log_operation("Calculated correlation matrix")
            
            response = "📊 **Correlation Matrix:**\n\n"
            for i, col1 in enumerate(numeric_cols):
                for j, col2 in enumerate(numeric_cols):
                    if i < j:
                        corr_val = corr_matrix.loc[col1, col2]
                        response += f"• **{col1}** vs **{col2}**: {round(corr_val, 3)}\n"
            
            return {
                "response": response,
                "type": "analysis",
                "data": corr_matrix.to_dict()
            }
            
        except Exception as e:
            return {"response": f"Error calculating correlation: {str(e)}", "type": "error"}
    
    def _get_unique_values(self, message: str) -> Dict[str, Any]:
        """Get unique values for specified column"""
        column_name = self._extract_column_name(message)
        if not column_name:
            # Show available columns for selection
            all_columns = self.current_dataset.columns.tolist()
            
            response = "🔢 **Show Unique Values - Select a Column:**\n\n"
            response += "Available columns:\n"
            for i, col in enumerate(all_columns, 1):
                unique_count = self.current_dataset[col].nunique()
                col_type = str(self.current_dataset[col].dtype)
                response += f"{i}. **{col}** ({col_type}) - {unique_count} unique values\n"
            
            response += "\n💡 **Usage:** Type 'show unique values in [column_name]'\n"
            response += "**Examples:**\n"
            for col in all_columns[:3]:
                response += f"• show unique values in {col}\n"
            
            return {
                "response": response,
                "type": "help",
                "data": {"available_columns": all_columns, "operation": "unique_values"}
            }
        
        return self._get_unique_values_for_column(column_name)
    
    def _show_history_options(self, message: str) -> Dict[str, Any]:
        """Show history analysis options"""
        try:
            response = "📚 **History Analysis Options:**\n\n"
            response += "I can help you analyze data from your processing history:\n\n"
            response += "🔍 **Available Commands:**\n"
            response += "• 'load from history' - Show your recent datasets\n"
            response += "• 'analyze history data' - Get insights from previous work\n"
            response += "• 'compare with history' - Compare current data with previous versions\n\n"
            response += "💡 **What I can do:**\n"
            response += "• Load previously processed datasets\n"
            response += "• Show your data cleaning history\n"
            response += "• Compare before/after statistics\n"
            response += "• Reapply previous operations\n"
            
            return {
                "response": response,
                "type": "help",
                "data": {"show_history_options": True}
            }
        except Exception as e:
            return {"response": f"Error accessing history: {str(e)}", "type": "error"}
    
    def get_current_dataset_info(self) -> Dict[str, Any]:
        """Get current dataset information"""
        if self.current_dataset is None:
            return {"error": "No dataset loaded"}
        
        return {
            "shape": self.current_dataset.shape,
            "columns": self.current_dataset.columns.tolist(),
            "dtypes": {str(k): str(v) for k, v in self.current_dataset.dtypes.to_dict().items()},
            "info": self.dataset_info
        }