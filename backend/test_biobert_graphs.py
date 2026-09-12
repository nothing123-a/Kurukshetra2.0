#!/usr/bin/env python3
"""
Test BioBERT Risk Analysis with Graph Generation
"""

import requests
import json

def test_biobert_with_graphs():
    """Test BioBERT with comprehensive graph data"""
    print("🧬 Testing BioBERT with Graph Generation")
    print("=" * 60)
    
    # Create comprehensive sample data
    sample_csv = """compound_id,toxicity,efficacy,pIC50,quality,SMILES
COMP001,2.1,7.8,6.5,95.2,CCO
COMP002,3.2,6.5,5.8,88.5,CCC
COMP003,1.8,8.2,7.2,92.1,CCCO
COMP004,2.5,7.1,6.8,90.3,CCCC
COMP005,1.9,8.5,7.5,96.8,CCCCO
COMP006,3.5,5.9,5.2,85.4,CC(C)C
COMP007,2.2,7.9,6.9,93.7,CCC(C)C
COMP008,1.7,8.8,7.8,97.2,CCCCCO
COMP009,2.8,6.8,6.1,89.1,CC(C)CO
COMP010,2.0,8.1,7.3,94.5,CCCCC"""
    
    try:
        files = {'file': ('test_compounds.csv', sample_csv, 'text/csv')}
        response = requests.post('http://localhost:8000/api/risk-analysis/upload', files=files)
        
        if response.status_code == 200:
            data = response.json()
            analysis = json.loads(data['biobert_analysis'])
            
            print(f"\n✅ Analysis Complete!")
            print(f"   Risk Level: {analysis['risk_level']}")
            print(f"   Success Probability: {analysis['success_probability']}%")
            
            print(f"\n📊 Bio Metrics:")
            for key, value in analysis['bio_metrics'].items():
                print(f"   {key}: {value}")
            
            print(f"\n📈 Graphs Generated:")
            if 'graphs' in analysis:
                for graph_name, graph_data in analysis['graphs'].items():
                    print(f"   ✓ {graph_name}: {graph_data['type']} chart")
                    print(f"     Title: {graph_data['title']}")
                    print(f"     Data points: {len(graph_data.get('data', []))}")
                    if 'stats' in graph_data:
                        print(f"     Stats: {graph_data['stats']}")
            else:
                print("   ❌ No graphs found!")
            
            print(f"\n⚠️  Risk Factors ({len(analysis['risk_factors'])}):")
            for factor in analysis['risk_factors']:
                print(f"   • {factor}")
            
            print(f"\n💡 Recommendations ({len(analysis['recommendations'])}):")
            for rec in analysis['recommendations']:
                print(f"   • {rec}")
            
            print(f"\n🔬 BioBERT Analysis:")
            print(f"   {analysis['biobert_analysis']}")
            
            return True
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_biobert_with_graphs():
        print("\n" + "=" * 60)
        print("🎉 BioBERT Graph Generation Test PASSED!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ BioBERT Graph Generation Test FAILED!")
        print("=" * 60)
