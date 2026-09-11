#!/usr/bin/env python3
"""
Test Gemini API with dummy drug data
"""
import os
import pandas as pd
import json
import requests

def test_gemini_with_dummy_data():
    # Create dummy drug data
    dummy_data = [
        {"Compound_ID": "COMP001", "SMILES": "CCO", "pIC50": 5.2, "Activity": "Active", "MW": 46.07},
        {"Compound_ID": "COMP002", "SMILES": "CCC", "pIC50": 4.8, "Activity": "Moderate", "MW": 44.10},
        {"Compound_ID": "COMP003", "SMILES": "CCCC", "pIC50": 3.1, "Activity": "Inactive", "MW": 58.12}
    ]
    
    # Create CSV
    df = pd.DataFrame(dummy_data)
    csv_path = 'test_compounds.csv'
    df.to_csv(csv_path, index=False)
    print(f"✅ Created test CSV: {csv_path}")
    print(f"Data shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"Sample data:\n{df}")
    
    # Test Gemini API
    api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyCUD3MXSMK6Z9Klkt-D1volQBh6MLhzEEM')
    models = ['gemini-2.0-flash-exp', 'gemini-1.5-flash', 'gemini-1.5-pro']
    
    prompt = f"""Analyze this drug compound dataset for clinical trial risk assessment:

Dataset: {len(df)} compounds, {len(df.columns)} features
Columns: {list(df.columns)}
Sample data: {json.dumps(dummy_data, indent=2)}
Data completeness: 100%

Provide:
1. Risk level (LOW/MEDIUM/HIGH)
2. Key safety concerns
3. Recommendations for clinical trials
4. Success probability estimate

Keep response under 200 words."""

    print(f"\n🤖 Testing Gemini API...")
    print(f"Prompt length: {len(prompt)} characters")
    
    for model in models:
        try:
            print(f"\n📡 Trying model: {model}")
            response = requests.post(
                f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}',
                json={'contents': [{'parts': [{'text': prompt}]}]},
                timeout=15
            )
            
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    analysis = result['candidates'][0]['content']['parts'][0]['text']
                    print(f"✅ SUCCESS with {model}")
                    print(f"Analysis length: {len(analysis)} characters")
                    print(f"Analysis preview: {analysis[:200]}...")
                    
                    # Clean up
                    os.remove(csv_path)
                    return True
                else:
                    print(f"❌ No candidates in response: {result}")
            else:
                print(f"❌ API error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception with {model}: {str(e)}")
            continue
    
    print(f"\n❌ All models failed")
    # Clean up
    try:
        os.remove(csv_path)
    except:
        pass
    return False

if __name__ == "__main__":
    print("🧪 Testing Gemini API with dummy drug data...")
    success = test_gemini_with_dummy_data()
    print(f"\n{'✅ GEMINI API WORKING' if success else '❌ GEMINI API FAILED'}")