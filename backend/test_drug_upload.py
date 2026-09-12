#!/usr/bin/env python3
"""
Test script for drug testing upload endpoint
"""
import requests
import json

def test_upload():
    url = "http://localhost:8000/api/drug-testing/upload"
    
    # Test with sample CSV data
    csv_content = """Compound No.,SMILES,pIC50,Activity
1,CCO,5.2,Active
2,CCC,4.8,Moderate
3,CCCC,3.1,Inactive
"""
    
    # Create a test file
    files = {'files': ('test_compounds.csv', csv_content, 'text/csv')}
    data = {'step': 'step1'}
    
    try:
        response = requests.post(url, files=files, data=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload successful!")
            print(f"Files uploaded: {result.get('files', [])}")
            if result.get('risk_analysis'):
                print("Risk analysis completed:")
                for analysis in result['risk_analysis']:
                    print(f"  - {analysis['filename']}: {analysis['risk_analysis']}")
        else:
            print(f"❌ Upload failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_upload()