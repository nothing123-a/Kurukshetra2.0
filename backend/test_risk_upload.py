#!/usr/bin/env python3
"""
Test risk analysis upload endpoint
"""
import requests
import io

def test_risk_analysis_upload():
    url = "http://localhost:8000/api/risk-analysis/upload"
    
    # Create test CSV content
    csv_content = """Compound_ID,SMILES,pIC50,Activity,MW
COMP001,CCO,5.2,Active,46.07
COMP002,CCC,4.8,Moderate,44.10
COMP003,CCCC,3.1,Inactive,58.12
COMP004,CCCCC,2.9,Inactive,72.15
COMP005,CCCCCC,6.1,Active,86.18"""
    
    # Create file-like object
    files = {'file': ('test_compounds.csv', csv_content, 'text/csv')}
    
    try:
        print("🧪 Testing risk analysis upload...")
        print(f"📡 Sending request to: {url}")
        
        response = requests.post(url, files=files, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload successful!")
            print(f"📋 Response keys: {list(result.keys())}")
            
            if result.get('success'):
                print(f"📁 Filename: {result.get('filename')}")
                print(f"📈 Data stats: {result.get('data_stats')}")
                
                gemini_analysis = result.get('gemini_analysis', '')
                if gemini_analysis:
                    print(f"🤖 Gemini analysis preview: {gemini_analysis[:200]}...")
                    print("✅ Gemini API working!")
                else:
                    print("❌ No Gemini analysis returned")
            else:
                print(f"❌ Upload failed: {result}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection refused - Backend server not running")
        print("💡 Start backend with: ./start_fixed.sh")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_risk_analysis_upload()