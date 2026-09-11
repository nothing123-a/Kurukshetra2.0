#!/usr/bin/env python3
"""
Manual test script for risk analysis functionality
"""
import requests
import json
import os
import pandas as pd
from io import StringIO

# Create test CSV data
test_data = {
    'compound_id': ['COMP001', 'COMP002', 'COMP003', 'COMP004', 'COMP005'],
    'molecular_weight': [250.5, 180.2, 320.8, 195.4, 275.6],
    'toxicity_score': [2.1, 1.8, 3.2, 1.5, 2.7],
    'efficacy_score': [7.8, 8.2, 6.5, 8.9, 7.1],
    'bioavailability': [0.65, 0.72, 0.58, 0.81, 0.69],
    'side_effects': ['mild', 'none', 'moderate', 'mild', 'mild']
}

def create_test_csv():
    """Create a test CSV file"""
    df = pd.DataFrame(test_data)
    csv_path = '/Users/darshanpatil/Documents/Project bhishma's 2.0/Project-Bhishma's-2.0/backend/test_compounds.csv'
    df.to_csv(csv_path, index=False)
    print(f"✅ Created test CSV: {csv_path}")
    return csv_path

def test_risk_analysis_upload():
    """Test the risk analysis upload endpoint"""
    print("🧪 Testing Risk Analysis Upload...")
    
    # Create test CSV
    csv_path = create_test_csv()
    
    # Test the endpoint
    url = 'http://localhost:8000/api/risk-analysis/upload'
    
    try:
        with open(csv_path, 'rb') as f:
            files = {'file': ('test_compounds.csv', f, 'text/csv')}
            response = requests.post(url, files=files, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Filename: {result.get('filename')}")
            print(f"Data Stats: {result.get('data_stats')}")
            analysis = result.get('biobert_analysis', 'No analysis available')
            print(f"BioBERT Analysis: {analysis[:200]}...")
            return True
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Is the server running on localhost:8000?")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_risk_analysis_status():
    """Test the risk analysis status endpoint"""
    print("🔍 Testing Risk Analysis Status...")
    
    url = 'http://localhost:8000/api/risk-analysis/status'
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Status endpoint working!")
            print(f"Status: {result.get('status')}")
            print(f"Message: {result.get('message')}")
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Is the server running on localhost:8000?")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_gemini_api_directly():
    """Test Gemini API directly"""
    print("🤖 Testing Gemini API directly...")
    
    api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyCUD3MXSMK6Z9Klkt-D1volQBh6MLhzEEM')
    
    if not api_key:
        print("❌ No Gemini API key found")
        return False
    
    prompt = """Analyze this sample drug data for risk assessment:
    
compound_id,molecular_weight,toxicity_score,efficacy_score
COMP001,250.5,2.1,7.8
COMP002,180.2,1.8,8.2

Provide risk level (LOW/MEDIUM/HIGH) and key factors."""
    
    try:
        response = requests.post(
            f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}',
            json={'contents': [{'parts': [{'text': prompt}]}]},
            timeout=20
        )
        
        print(f"Gemini API Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result:
                analysis = result['candidates'][0]['content']['parts'][0]['text']
                print("✅ Gemini API working!")
                print(f"Analysis: {analysis[:200]}...")
                return True
        
        print(f"❌ Gemini API failed: {response.text}")
        return False
        
    except Exception as e:
        print(f"❌ Gemini API error: {str(e)}")
        return False

if __name__ == '__main__':
    print("🧬 Bhishma's Risk Analysis Manual Test")
    print("=" * 50)
    
    # Test 1: Status endpoint
    status_ok = test_risk_analysis_status()
    print()
    
    # Test 2: Gemini API
    gemini_ok = test_gemini_api_directly()
    print()
    
    # Test 3: Upload endpoint
    upload_ok = test_risk_analysis_upload()
    print()
    
    # Summary
    print("📊 Test Summary:")
    print(f"Status Endpoint: {'✅' if status_ok else '❌'}")
    print(f"Gemini API: {'✅' if gemini_ok else '❌'}")
    print(f"Upload Endpoint: {'✅' if upload_ok else '❌'}")
    
    if all([status_ok, gemini_ok, upload_ok]):
        print("\n🎉 All tests passed! Risk analysis is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the server and API configuration.")