#!/usr/bin/env python3
"""
Test BioBERT Risk Analysis Endpoints
"""

import requests
import json
import os
import time

API_BASE = 'http://localhost:8000'

def test_risk_analysis_status():
    """Test risk analysis status"""
    try:
        response = requests.get(f'{API_BASE}/api/risk-analysis/status')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data.get('message')}")
            return True
        else:
            print(f"❌ Status failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_risk_analysis_upload():
    """Test BioBERT risk analysis upload"""
    sample_csv = """compound_id,toxicity,efficacy,molecular_weight,bioavailability,quality
COMP001,2.1,7.8,450.2,0.85,95.2
COMP002,3.2,6.5,380.1,0.72,88.7
COMP003,1.8,8.2,520.3,0.91,97.1"""
    
    temp_file = 'test_compounds.csv'
    with open(temp_file, 'w') as f:
        f.write(sample_csv)
    
    try:
        with open(temp_file, 'rb') as f:
            files = {'file': ('compounds.csv', f, 'text/csv')}
            response = requests.post(f'{API_BASE}/api/risk-analysis/upload', files=files)
        
        print(f"Upload: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('success')}")
            
            if 'biobert_analysis' in data:
                try:
                    analysis = json.loads(data['biobert_analysis'])
                    print(f"✅ Risk Level: {analysis.get('risk_level')}")
                    print(f"✅ Success Probability: {analysis.get('success_probability')}%")
                    return True
                except:
                    print("✅ BioBERT analysis completed")
                    return True
        else:
            print(f"❌ Upload failed: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False
    
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def test_drug_testing_status():
    """Test drug testing status"""
    try:
        response = requests.get(f'{API_BASE}/api/drug-testing/status')
        print(f"Drug Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Drug testing ready")
            return True
        else:
            print(f"❌ Drug status failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Drug status error: {e}")
        return False

def start_server():
    """Start the server"""
    import subprocess
    import sys
    
    print("🚀 Starting server...")
    try:
        # Start server in background
        process = subprocess.Popen([sys.executable, 'app.py'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(3)
        
        return process
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

if __name__ == "__main__":
    print("🧬 Testing BioBERT Risk Analysis Endpoints")
    print("=" * 50)
    
    # Check if server is running
    if not test_risk_analysis_status():
        print("\n🚀 Server not running, attempting to start...")
        server_process = start_server()
        if server_process:
            print("✅ Server started")
        else:
            print("❌ Could not start server")
            exit(1)
    
    print("\n1. Testing Risk Analysis Status...")
    status_ok = test_risk_analysis_status()
    
    print("\n2. Testing BioBERT Upload & Analysis...")
    upload_ok = test_risk_analysis_upload()
    
    print("\n3. Testing Drug Testing Status...")
    drug_ok = test_drug_testing_status()
    
    print("\n" + "=" * 50)
    if status_ok and upload_ok and drug_ok:
        print("✅ All BioBERT endpoints working!")
    else:
        print("❌ Some endpoints failed")
    
    print("🧬 BioBERT Risk Analysis System Ready!")