#!/usr/bin/env python3
import pandas as pd
import json
import requests
import os

def test_simple_analysis():
    """Test simple CSV analysis without Gemini"""
    
    # Load CSV file
    csv_path = "../step 1/DDH Data.csv"
    df = pd.read_csv(csv_path)
    
    print(f"✅ Loaded {len(df)} rows from CSV")
    print(f"✅ Columns: {list(df.columns)}")
    
    # Simple analysis without Gemini
    score = 75
    if 'pIC50' in df.columns or 'IC50' in df.columns:
        score += 10
        print("✅ Found IC50/pIC50 data - score +10")
    if 'SMILES' in df.columns:
        score += 5
        print("✅ Found SMILES data - score +5")
    
    result = {
        'overall_score': score,
        'risk_level': 'MEDIUM' if score < 80 else 'LOW',
        'analysis': f'Analyzed {len(df)} compounds with columns: {list(df.columns)}',
        'graph_data': {
            'labels': ['Data Quality', 'Structure', 'Completeness'],
            'scores': [score, score-5, score+5]
        },
        'next_step_available': score > 80
    }
    
    print(f"✅ Analysis complete - Score: {score}")
    print(f"✅ Next step available: {score > 80}")
    return result

def test_gemini_simple():
    """Test simple Gemini call"""
    try:
        api_key = "AIzaSyCUD3MXSMK6Z9Klkt-D1volQBh6MLhzEEM"
        
        prompt = "Analyze drug safety: Score 0-100. Respond with just a number."
        
        response = requests.post(
            f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}',
            json={'contents': [{'parts': [{'text': prompt}]}]},
            timeout=10
        )
        
        print(f"Gemini status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result:
                analysis = result['candidates'][0]['content']['parts'][0]['text']
                print(f"✅ Gemini response: {analysis[:100]}")
                return True
        else:
            print(f"❌ Gemini error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Gemini exception: {e}")
        return False

def test_upload_endpoint():
    """Test upload endpoint"""
    try:
        response = requests.post(
            'http://localhost:8000/api/data-cleaning/upload',
            files={'files': open('../step 1/DDH Data.csv', 'rb')},
            timeout=5
        )
        print(f"Upload status: {response.status_code}")
        print(f"Upload response: {response.text[:200]}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Upload test failed: {e}")
        return False

if __name__ == "__main__":
    print("=== TESTING ANALYSIS ===")
    test_simple_analysis()
    
    print("\n=== TESTING GEMINI ===")
    test_gemini_simple()
    
    print("\n=== TESTING UPLOAD ===")
    test_upload_endpoint()