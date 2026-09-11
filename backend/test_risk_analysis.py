#!/usr/bin/env python3
"""
Test script for risk analysis functionality
"""

import requests
import json
import os

def test_risk_analysis():
    """Test the risk analysis endpoint"""
    
    # Create a sample CSV file for testing
    sample_csv_content = """Compound No.,SMILES,pIC50,Toxicity,Safety_Score
1,CCO,-2.5,High,3.2
2,CCC,-1.8,Medium,4.1
3,CCCC,-3.2,High,2.8
4,CC(C)C,-1.2,Low,5.5
5,C1CCCCC1,-2.1,Medium,3.9"""
    
    # Save sample CSV
    os.makedirs('uploads/risk_analysis', exist_ok=True)
    with open('uploads/risk_analysis/test_compounds.csv', 'w') as f:
        f.write(sample_csv_content)
    
    # Test status endpoint
    print("Testing risk analysis status...")
    try:
        response = requests.get('http://localhost:8000/api/risk-analysis/status')
        print(f"Status response: {response.status_code}")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Status test failed: {e}")
    
    # Test upload endpoint
    print("\nTesting risk analysis upload...")
    try:
        with open('uploads/risk_analysis/test_compounds.csv', 'rb') as f:
            files = {'file': ('test_compounds.csv', f, 'text/csv')}
            response = requests.post('http://localhost:8000/api/risk-analysis/upload', files=files)
        
        print(f"Upload response: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("Risk Analysis Results:")
            print(f"- Overall Risk Score: {result.get('overall_risk_score', 'N/A')}")
            print(f"- Success Probability: {result.get('success_probability', 'N/A')}%")
            print(f"- Risk Factors: {len(result.get('risk_factors', []))}")
            print(f"- Recommendations: {len(result.get('recommendations', []))}")
            print(f"- Charts Generated: {len(result.get('charts', {}))}")
            
            if 'gemini_analysis' in result:
                gemini = result['gemini_analysis']
                if isinstance(gemini, dict) and 'risk_score' in gemini:
                    print(f"- Gemini Risk Score: {gemini['risk_score']}")
                    print(f"- Gemini Analysis Available: Yes")
                else:
                    print(f"- Gemini Analysis: {type(gemini)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Upload test failed: {e}")

if __name__ == "__main__":
    test_risk_analysis()