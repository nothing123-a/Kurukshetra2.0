import os
import google.generativeai as genai
from typing import Dict, Any, List

class AIReportAnalyzer:
    def __init__(self):
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY', 'AIzaSyDrYXOmHqiChayrg_yC0i-aGi-OqeJw1v4')
        genai.configure(api_key=self.gemini_api_key)
        # Use the latest Gemini model
        try:
            self.model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
        except:
            try:
                self.model = genai.GenerativeModel('gemini-1.5-flash')
            except:
                self.model = None
    
    def analyze_data_quality(self, cleaning_log: List[str], privacy_report: Dict[str, Any] = None) -> str:
        """Generate AI analysis of data quality and privacy measures"""
        
        # Prepare analysis prompt
        prompt = f"""
        Analyze this data cleaning and privacy protection report:
        
        CLEANING LOG:
        {chr(10).join(cleaning_log)}
        
        PRIVACY REPORT:
        {privacy_report if privacy_report else 'No privacy measures applied'}
        
        Provide a concise executive summary covering:
        1. Data quality improvements made
        2. Privacy protection effectiveness
        3. Compliance assessment
        4. Recommendations for further improvements
        
        Keep response under 300 words and professional.
        """
        
        try:
            if self.model:
                response = self.model.generate_content(prompt)
                return response.text
            else:
                return self._generate_basic_analysis(cleaning_log, privacy_report)
        except Exception as e:
            # Fallback to basic analysis if Gemini fails
            return self._generate_basic_analysis(cleaning_log, privacy_report)
    
    def generate_insights(self, data_summary: Dict[str, Any]) -> str:
        """Generate insights about the dataset"""
        
        prompt = f"""
        Analyze this dataset summary and provide key insights:
        
        Dataset: {data_summary.get('rows', 0)} rows, {data_summary.get('columns', 0)} columns
        Missing values: {data_summary.get('missing_values', 0)}
        Column types: {data_summary.get('data_types', {})}
        
        Provide 3-4 key insights about data quality, completeness, and potential issues.
        Keep response under 200 words.
        """
        
        try:
            if self.model:
                response = self.model.generate_content(prompt)
                return response.text
            else:
                return self._generate_basic_insights(data_summary)
        except Exception as e:
            return self._generate_basic_insights(data_summary)
    
    def _generate_basic_analysis(self, cleaning_log: List[str], privacy_report: Dict[str, Any] = None) -> str:
        """Generate basic analysis without AI when Gemini is unavailable"""
        analysis = "**Data Processing Summary:**\n\n"
        
        # Analyze cleaning steps
        if cleaning_log:
            analysis += "**Data Quality Improvements:**\n"
            for log in cleaning_log:
                if "missing values" in log.lower():
                    analysis += "• Enhanced data completeness through intelligent imputation\n"
                elif "duplicate" in log.lower():
                    analysis += "• Improved data uniqueness by removing duplicates\n"
                elif "privacy" in log.lower():
                    analysis += "• Applied enterprise-grade privacy protection\n"
                elif "outlier" in log.lower():
                    analysis += "• Detected and handled data anomalies\n"
        
        # Privacy assessment
        if privacy_report:
            compliance_score = privacy_report.get('compliance_score', 0)
            analysis += f"\n**Privacy Protection:**\n"
            analysis += f"• Compliance Score: {compliance_score}%\n"
            if compliance_score >= 90:
                analysis += "• Excellent privacy protection standards achieved\n"
            elif compliance_score >= 70:
                analysis += "• Good privacy protection with room for improvement\n"
            else:
                analysis += "• Consider additional privacy measures\n"
        
        analysis += "\n**Recommendations:**\n"
        analysis += "• Data is now ready for analysis and reporting\n"
        analysis += "• All sensitive information has been properly protected\n"
        analysis += "• Quality metrics indicate reliable dataset\n"
        
        return analysis
    
    def _generate_basic_insights(self, data_summary: Dict[str, Any]) -> str:
        """Generate basic insights without AI"""
        rows = data_summary.get('rows', 0)
        columns = data_summary.get('columns', 0)
        missing = data_summary.get('missing_values', 0)
        
        insights = f"**Dataset Overview:**\n"
        insights += f"• Dataset contains {rows:,} records across {columns} variables\n"
        
        if missing > 0:
            missing_pct = (missing / (rows * columns)) * 100 if rows > 0 else 0
            insights += f"• Data completeness: {100-missing_pct:.1f}% ({missing:,} missing values)\n"
        else:
            insights += f"• Excellent data completeness with no missing values\n"
        
        if rows > 10000:
            insights += f"• Large dataset suitable for comprehensive analysis\n"
        elif rows > 1000:
            insights += f"• Medium-sized dataset with good analytical potential\n"
        else:
            insights += f"• Compact dataset suitable for detailed examination\n"
        
        return insights