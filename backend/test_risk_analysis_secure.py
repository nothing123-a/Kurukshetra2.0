#!/usr/bin/env python3
"""
Secure Risk Analysis Test Script
Tests the BioBERT risk analysis endpoints
"""

import requests
import json
import os

API_BASE = 'http://localhost:8000'

def test_risk_analysis_status():
    """Test risk analysis status endpoint"""
    try:
        response = requests.get(f'{API_BASE}/api/risk-analysis/status')
        print(f"Status Check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('status')}")
            print(f"✅ Message: {data.get('message')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

def test_risk_analysis_upload():
    """Test risk analysis upload with sample data"""
    # Create sample CSV data
    sample_csv = """compound_id,toxicity,efficacy,molecular_weight,bioavailability,quality
COMP001,2.1,7.8,450.2,0.85,95.2
COMP002,3.2,6.5,380.1,0.72,88.7
COMP003,1.8,8.2,520.3,0.91,97.1
COMP004,4.1,5.9,290.8,0.68,82.3
COMP005,2.7,7.1,410.5,0.79,91.8"""
    
    # Save to temporary file
    temp_file = 'temp_compounds.csv'
    with open(temp_file, 'w') as f:
        f.write(sample_csv)
    
    try:
        with open(temp_file, 'rb') as f:
            files = {'file': ('compounds.csv', f, 'text/csv')}
            response = requests.post(f'{API_BASE}/api/risk-analysis/upload', files=files)
        
        print(f"Upload Test: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('success')}")
            print(f"✅ Filename: {data.get('filename')}")
            
            # Parse BioBERT analysis
            if 'biobert_analysis' in data:
                try:
                    analysis = json.loads(data['biobert_analysis'])
                    print(f"✅ Risk Level: {analysis.get('risk_level')}")
                    print(f"✅ Success Probability: {analysis.get('success_probability')}%")
                    print(f"✅ Risk Factors: {len(analysis.get('risk_factors', []))}")
                except:
                    print("✅ Analysis completed (raw format)")
        else:
            print(f"❌ Error: {response.text}")
    
    except Exception as e:
        print(f"❌ Upload Error: {e}")
    
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == "__main__":
    print("🧬 Testing Bhishma's Risk Analysis Endpoints")
    print("=" * 50)
    
    print("\n1. Testing Status Endpoint...")
    test_risk_analysis_status()
    
    print("\n2. Testing Upload & Analysis...")
    test_risk_analysis_upload()
    
    print("\n✅ Risk Analysis Tests Complete!")