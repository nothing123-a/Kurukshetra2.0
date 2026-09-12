#!/usr/bin/env python3
"""
Quick BioBERT Risk Analysis Test
"""

import requests
import json

def test_biobert_system():
    """Test BioBERT endpoints"""
    print("🧬 Testing BioBERT Risk Analysis System")
    print("=" * 50)
    
    # Test status
    try:
        response = requests.get('http://localhost:8000/api/risk-analysis/status')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('message')}")
            print(f"✅ Engine: {data.get('analysis_engine')}")
        else:
            print(f"❌ Status failed: {response.status_code}")
            return False
    except:
        print("❌ Server not running")
        return False
    
    # Test with sample data
    sample_csv = """compound_id,toxicity,efficacy,pIC50,SMILES
COMP001,2.1,7.8,6.5,CCO
COMP002,3.2,6.5,5.8,CCC
COMP003,1.8,8.2,7.2,CCCO"""
    
    try:
        files = {'file': ('test.csv', sample_csv, 'text/csv')}
        response = requests.post('http://localhost:8000/api/risk-analysis/upload', files=files)
        
        if response.status_code == 200:
            data = response.json()
            analysis = json.loads(data['biobert_analysis'])
            print(f"✅ Risk Level: {analysis['risk_level']}")
            print(f"✅ Success Rate: {analysis['success_probability']}%")
            print(f"✅ BioBERT Working!")
            return True
        else:
            print(f"❌ Upload failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    if test_biobert_system():
        print("\n🎉 BioBERT Risk Analysis System is WORKING!")
    else:
        print("\n❌ BioBERT System needs attention")