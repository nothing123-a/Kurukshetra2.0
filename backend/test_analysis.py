#!/usr/bin/env python3
import sys
sys.path.append('.')
from drug_testing_routes import perform_risk_analysis_comparison

def test_analysis():
    """Test the updated analysis function"""
    
    csv_path = "../step 1/DDH Data.csv"
    
    print("Testing drug analysis...")
    result = perform_risk_analysis_comparison(csv_path)
    
    print(f"✅ Overall Score: {result.get('overall_score', 'N/A')}")
    print(f"✅ Risk Level: {result.get('risk_level', 'N/A')}")
    print(f"✅ Next Step Available: {result.get('next_step_available', False)}")
    print(f"✅ Graph Data: {result.get('graph_data', {})}")
    print(f"✅ Test Results: {len(result.get('test_results', {}).get('toxicity_tests', []))} toxicity tests")
    print(f"✅ Recommendations: {len(result.get('recommendations', []))} recommendations")
    
    return result

if __name__ == "__main__":
    test_analysis()