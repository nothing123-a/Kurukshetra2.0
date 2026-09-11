#!/usr/bin/env python3
import pandas as pd
import json
import requests
import os

def test_gemini_with_csv():
    """Test extracting CSV data and sending to Gemini"""
    
    # Load CSV file
    csv_path = "../step 1/DDH Data.csv"
    df = pd.read_csv(csv_path)
    
    # Extract sample data (first 10 rows to avoid timeout)
    sample_data = df.head(10).to_dict('records')
    
    print(f"Loaded {len(df)} rows from CSV, using first 10 for analysis")
    print(f"Columns: {list(df.columns)}")
    
    # Create prompt with sample data
    prompt = f"""DRUG COMPOUND ANALYSIS

Dataset: {len(df)} compounds (analyzing first 10)
Columns: {list(df.columns)}

SAMPLE DATA:
{json.dumps(sample_data, indent=2)}

Analyze this drug data and provide:
1. Overall safety score (0-100)
2. Risk ingredients found
3. Better alternatives if needed
4. Test results for graphs
5. Next step recommendation if score > 80

Respond in JSON format:
{{
  "overall_score": 85,
  "risk_level": "LOW",
  "analysis": "detailed analysis",
  "graph_data": {{"labels": ["Safety", "Efficacy"], "scores": [85, 90]}},
  "next_step_available": true
}}"""
    
    # Call Gemini API
    api_key = "AIzaSyCUD3MXSMK6Z9Klkt-D1volQBh6MLhzEEM"
    
    response = requests.post(
        f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}',
        json={'contents': [{'parts': [{'text': prompt}]}]},
        timeout=30
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    
    if response.status_code == 200:
        result = response.json()
        if 'candidates' in result:
            analysis = result['candidates'][0]['content']['parts'][0]['text']
            print("GEMINI RESPONSE:")
            print(analysis)
            return analysis
    
    return None

if __name__ == "__main__":
    test_gemini_with_csv()