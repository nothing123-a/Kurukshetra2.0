#!/usr/bin/env python3
import requests
import time

def test_endpoint():
    print("🧪 Quick Risk Analysis Test")
    
    # Test with the existing test file
    csv_path = '/Users/darshanpatil/Documents/Project bhishma's 2.0/Project-Bhishma's-2.0/backend/test_compounds.csv'
    
    try:
        with open(csv_path, 'rb') as f:
            files = {'file': ('test_compounds.csv', f, 'text/csv')}
            
            print("📤 Uploading file...")
            start_time = time.time()
            
            response = requests.post(
                'http://localhost:8000/api/risk-analysis/upload',
                files=files,
                timeout=10
            )
            
            end_time = time.time()
            print(f"⏱️ Response time: {end_time - start_time:.2f} seconds")
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ SUCCESS!")
                print(f"📁 File: {result['filename']}")
                print(f"📈 Data: {result['data_stats']['rows']} rows, {result['data_stats']['columns']} cols")
                
                # Parse analysis
                import json
                analysis = json.loads(result['biobert_analysis'])
                print(f"🎯 Risk Level: {analysis['risk_level']}")
                print(f"📊 Success Probability: {analysis['success_probability']}%")
                print(f"⚠️ Risk Factors: {len(analysis['risk_factors'])}")
                print(f"💡 Recommendations: {len(analysis['recommendations'])}")
                
                return True
            else:
                print(f"❌ Failed: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    success = test_endpoint()
    print(f"\n{'🎉 Test PASSED' if success else '💥 Test FAILED'}")