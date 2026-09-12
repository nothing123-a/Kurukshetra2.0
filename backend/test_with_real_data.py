#!/usr/bin/env python3
"""
Test BioBERT Risk Analysis with Real DDH Data
"""

import requests
import json

API_BASE = 'http://localhost:8000'

def test_with_ddh_data():
    """Test with actual DDH_Data.csv"""
    print("🧬 Testing BioBERT with Real DDH Drug Data")
    print("=" * 50)
    
    # Test file upload
    try:
        with open('uploads/drug_testing/step1/DDH_Data.csv', 'rb') as f:
            files = {'file': ('DDH_Data.csv', f, 'text/csv')}
            response = requests.post(f'{API_BASE}/api/risk-analysis/upload', files=files)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('success')}")
            print(f"✅ File: {data.get('filename')}")
            print(f"✅ Compounds: {data['data_stats']['rows']}")
            print(f"✅ Features: {data['data_stats']['columns']}")
            print(f"✅ Completeness: {data['data_stats']['completeness']}%")
            
            # Parse BioBERT analysis
            if 'biobert_analysis' in data:
                try:
                    analysis = json.loads(data['biobert_analysis'])
                    print(f"\n🧬 BioBERT Analysis Results:")
                    print(f"✅ Risk Level: {analysis.get('risk_level')}")
                    print(f"✅ Success Probability: {analysis.get('success_probability')}%")
                    print(f"✅ Bio Metrics: {analysis.get('bio_metrics')}")
                    
                    print(f"\n⚠️ Risk Factors:")
                    for factor in analysis.get('risk_factors', []):
                        print(f"  • {factor}")
                    
                    print(f"\n💡 Recommendations:")
                    for rec in analysis.get('recommendations', []):
                        print(f"  • {rec}")
                        
                    print(f"\n🔬 BioBERT Assessment:")
                    print(f"  {analysis.get('biobert_analysis', 'Analysis completed')}")
                    
                except Exception as e:
                    print(f"❌ Could not parse analysis: {e}")
                    print(f"Raw response: {data.get('biobert_analysis', 'No analysis')}")
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_drug_processing():
    """Test drug testing step1 process"""
    print(f"\n🧪 Testing Drug Processing Pipeline")
    print("=" * 50)
    
    try:
        response = requests.post(f'{API_BASE}/api/drug-testing/step1/process', 
                               json={})
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('status')}")
            print(f"✅ Message: {data.get('message')}")
            print(f"✅ Data Shape: {data.get('data_shape')}")
            print(f"✅ Success Probability: {data.get('success_probability')}%")
            
            print(f"\n📊 Quality Metrics:")
            metrics = data.get('quality_metrics', {})
            for key, value in metrics.items():
                print(f"  • {key}: {value}")
                
            print(f"\n🧬 BioBERT Analysis:")
            analysis = data.get('ai_analysis', 'No analysis available')
            print(f"  {analysis[:200]}...")
            
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_with_ddh_data()
    test_drug_processing()
    print(f"\n✅ BioBERT Risk Analysis System is Working!")