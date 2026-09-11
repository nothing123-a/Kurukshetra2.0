"""
Drug Testing Helper Functions
Provides utility functions for clinical trial analysis and drug development pipeline
"""

import os
import json
import requests
import numpy as np
import pandas as pd
from datetime import datetime
import base64
from io import BytesIO

def calculate_overall_success_probability(riskscan_data, microtrial_data, megatrial_data):
    """Calculate overall success probability from all phases"""
    try:
        # Extract scores from each phase
        riskscan_score = extract_score(riskscan_data)
        microtrial_score = extract_score(microtrial_data)
        megatrial_score = extract_score(megatrial_data)
        
        # Weighted average (RiskScan: 30%, MicroTrial: 30%, MegaTrial: 40%)
        overall_probability = (
            riskscan_score * 0.3 +
            microtrial_score * 0.3 +
            megatrial_score * 0.4
        )
        
        return min(100, max(0, overall_probability))
    except:
        return 50  # Default score if calculation fails

def extract_score(phase_data):
    """Extract numerical score from phase data"""
    if not phase_data or isinstance(phase_data, dict) and 'error' in phase_data:
        return 50  # Default score for missing/error data
    
    try:
        # Try to find score in various possible locations
        if isinstance(phase_data, dict):
            # Look for common score fields
            score_fields = ['overall_score', 'suitability_score', 'quality_score', 'best_f1_score', 'success_probability']
            for field in score_fields:
                if field in phase_data:
                    score = phase_data[field]
                    if isinstance(score, (int, float)):
                        return float(score) if score <= 1 else float(score)
            
            # Look in nested structures
            if 'suitability_metrics' in phase_data:
                metrics = phase_data['suitability_metrics']
                if isinstance(metrics, dict):
                    avg_score = sum(metrics.values()) / len(metrics) if metrics else 50
                    return avg_score
            
            if 'model_performance' in phase_data:
                performance = phase_data['model_performance']
                if isinstance(performance, dict):
                    # Get best F1 score from models
                    best_f1 = 0
                    for model_name, model_metrics in performance.items():
                        if isinstance(model_metrics, dict) and 'f1_score' in model_metrics:
                            best_f1 = max(best_f1, model_metrics['f1_score'])
                    return best_f1 * 100 if best_f1 <= 1 else best_f1
        
        return 50  # Default if no score found
    except:
        return 50

def get_investment_recommendation(success_probability):
    """Get investment recommendation based on success probability"""
    if success_probability >= 80:
        return "STRONG BUY - High probability of success, excellent investment opportunity"
    elif success_probability >= 65:
        return "BUY - Good probability of success, recommended investment"
    elif success_probability >= 50:
        return "HOLD - Moderate probability, proceed with caution"
    elif success_probability >= 35:
        return "WEAK HOLD - Below average probability, high risk investment"
    else:
        return "SELL/AVOID - Low probability of success, not recommended"

def extract_risk_factors(riskscan_data, microtrial_data, megatrial_data):
    """Extract key risk factors from all phases"""
    risk_factors = []
    
    try:
        # RiskScan risks
        if isinstance(riskscan_data, dict) and 'risk_analysis' in riskscan_data:
            risk_analysis = riskscan_data['risk_analysis']
            if 'risk_flags' in risk_analysis:
                risk_factors.extend(risk_analysis['risk_flags'])
        
        # MicroTrial risks
        if isinstance(microtrial_data, dict):
            if 'high_correlation_pairs' in microtrial_data and microtrial_data['high_correlation_pairs']:
                risk_factors.append(f"High feature correlation detected: {len(microtrial_data['high_correlation_pairs'])} pairs")
        
        # MegaTrial risks
        if isinstance(megatrial_data, dict) and 'model_performance' in megatrial_data:
            performance = megatrial_data['model_performance']
            low_performing_models = []
            for model_name, metrics in performance.items():
                if isinstance(metrics, dict) and 'f1_score' in metrics:
                    if metrics['f1_score'] < 0.7:
                        low_performing_models.append(model_name)
            
            if low_performing_models:
                risk_factors.append(f"Low model performance: {', '.join(low_performing_models)}")
    except:
        pass
    
    if not risk_factors:
        risk_factors = ["No significant risk factors identified"]
    
    return risk_factors

def extract_success_drivers(riskscan_data, microtrial_data, megatrial_data):
    """Extract key success drivers from all phases"""
    success_drivers = []
    
    try:
        # RiskScan success factors
        if isinstance(riskscan_data, dict):
            if 'cleaned_rows' in riskscan_data and riskscan_data['cleaned_rows'] > 1000:
                success_drivers.append(f"Large dataset: {riskscan_data['cleaned_rows']} samples")
            
            if 'suitability_metrics' in riskscan_data:
                metrics = riskscan_data['suitability_metrics']
                high_scores = [k for k, v in metrics.items() if v > 80]
                if high_scores:
                    success_drivers.append(f"High quality metrics: {', '.join(high_scores)}")
        
        # MicroTrial success factors
        if isinstance(microtrial_data, dict):
            if 'total_features' in microtrial_data and microtrial_data['total_features'] > 10:
                success_drivers.append(f"Rich feature set: {microtrial_data['total_features']} features")
        
        # MegaTrial success factors
        if isinstance(megatrial_data, dict):
            if 'best_f1_score' in megatrial_data and megatrial_data['best_f1_score'] > 0.8:
                success_drivers.append(f"High model performance: {megatrial_data['best_f1_score']:.3f} F1-score")
            
            if 'training_samples' in megatrial_data and megatrial_data['training_samples'] > 500:
                success_drivers.append(f"Adequate training data: {megatrial_data['training_samples']} samples")
    except:
        pass
    
    if not success_drivers:
        success_drivers = ["Standard development pipeline completed successfully"]
    
    return success_drivers

def generate_phase_progression_chart(riskscan_data, microtrial_data, megatrial_data):
    """Generate base64 encoded chart showing phase progression"""
    try:
        import matplotlib.pyplot as plt
        
        phases = ['RiskScan', 'MicroTrial', 'MegaTrial']
        scores = [
            extract_score(riskscan_data),
            extract_score(microtrial_data),
            extract_score(megatrial_data)
        ]
        
        plt.figure(figsize=(10, 6))
        plt.plot(phases, scores, marker='o', linewidth=3, markersize=8, color='#2E86AB')
        plt.fill_between(phases, scores, alpha=0.3, color='#A23B72')
        plt.title('Drug Development Phase Progression', fontsize=16, fontweight='bold')
        plt.ylabel('Success Score (%)', fontsize=12)
        plt.xlabel('Development Phase', fontsize=12)
        plt.ylim(0, 100)
        plt.grid(True, alpha=0.3)
        
        # Add score labels
        for i, score in enumerate(scores):
            plt.annotate(f'{score:.1f}%', (i, score), textcoords="offset points", 
                        xytext=(0,10), ha='center', fontweight='bold')
        
        plt.tight_layout()
        
        # Convert to base64
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        chart_b64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return chart_b64
    except:
        return ""

def generate_gemini_comparison_insights(uploaded_data, project_data, step):
    """Generate Gemini AI insights for data comparison"""
    try:
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not gemini_api_key:
            return "Gemini API key not available for advanced insights"
        
        prompt = f"""
        Analyze the comparison between uploaded data and project reference data for clinical trial step {step}:
        
        Uploaded Data Summary: {uploaded_data}
        Project Data Summary: {project_data}
        
        Provide insights on:
        1. Data compatibility and alignment
        2. Quality assessment and recommendations
        3. Suitability for clinical trial analysis
        4. Potential issues and solutions
        5. Next steps for data preparation
        
        Keep response concise and actionable.
        """
        
        return call_gemini_api(prompt)
    except:
        return "Advanced AI insights unavailable"

def call_gemini_api(prompt):
    """Call Gemini API for AI analysis"""
    try:
        gemini_api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyDrYXOmHqiChayrg_yC0i-aGi-OqeJw1v4')
        
        if not gemini_api_key:
            return "Gemini API key not configured"
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 1000
            }
        }
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                return result['candidates'][0]['content']['parts'][0]['text']
        
        return "AI analysis temporarily unavailable"
        
    except Exception as e:
        return f"AI analysis error: {str(e)}"

def validate_clinical_data(df):
    """Validate clinical trial data for common issues"""
    issues = []
    recommendations = []
    
    # Check for required columns
    required_cols = ['patient_id', 'age', 'treatment_group']
    missing_required = [col for col in required_cols if col not in df.columns]
    if missing_required:
        issues.append(f"Missing required columns: {', '.join(missing_required)}")
        recommendations.append("Add missing required columns for clinical trial analysis")
    
    # Check age validity
    if 'age' in df.columns:
        invalid_ages = ((df['age'] < 0) | (df['age'] > 120)).sum()
        if invalid_ages > 0:
            issues.append(f"Invalid age values: {invalid_ages} patients")
            recommendations.append("Review and correct invalid age values")
    
    # Check for duplicate patients
    if 'patient_id' in df.columns:
        duplicates = df['patient_id'].duplicated().sum()
        if duplicates > 0:
            issues.append(f"Duplicate patient IDs: {duplicates}")
            recommendations.append("Remove or resolve duplicate patient records")
    
    # Check sample size adequacy
    if len(df) < 30:
        issues.append("Small sample size may affect statistical power")
        recommendations.append("Consider collecting more data for robust analysis")
    
    return {
        'issues': issues,
        'recommendations': recommendations,
        'validation_score': max(0, 100 - len(issues) * 20)
    }

def generate_clinical_report_summary(all_phase_data):
    """Generate executive summary for clinical trial report"""
    try:
        total_samples = 0
        total_features = 0
        overall_quality = 0
        phase_count = 0
        
        for phase_name, phase_data in all_phase_data.items():
            if isinstance(phase_data, dict) and 'error' not in phase_data:
                phase_count += 1
                
                # Extract sample counts
                if 'cleaned_rows' in phase_data:
                    total_samples = max(total_samples, phase_data['cleaned_rows'])
                elif 'training_samples' in phase_data:
                    total_samples = max(total_samples, phase_data['training_samples'])
                
                # Extract feature counts
                if 'total_features' in phase_data:
                    total_features = max(total_features, phase_data['total_features'])
                elif 'features_used' in phase_data:
                    total_features = max(total_features, phase_data['features_used'])
                
                # Extract quality scores
                phase_score = extract_score(phase_data)
                overall_quality += phase_score
        
        if phase_count > 0:
            overall_quality /= phase_count
        
        return {
            'total_samples_processed': total_samples,
            'total_features_engineered': total_features,
            'phases_completed': phase_count,
            'overall_quality_score': round(overall_quality, 1),
            'analysis_timestamp': datetime.now().isoformat()
        }
    except:
        return {
            'total_samples_processed': 0,
            'total_features_engineered': 0,
            'phases_completed': 0,
            'overall_quality_score': 0,
            'analysis_timestamp': datetime.now().isoformat()
        }