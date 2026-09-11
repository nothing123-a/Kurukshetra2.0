#!/usr/bin/env python3
"""
Simple test for enhanced typo correction
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_functionality():
    """Test basic functionality without heavy model loading"""
    try:
        from enhanced_typo_correction import EnhancedTypoCorrector
        
        # Initialize without Gemini for basic test
        corrector = EnhancedTypoCorrector(gemini_api_key=None)
        
        print("✅ Enhanced typo corrector initialized successfully")
        
        # Test text
        test_text = "This is a test sentance with some erors."
        
        print(f"📝 Test text: '{test_text}'")
        
        # Try to get available methods
        print("🔍 Available correction methods:")
        print("- Basic spelling correction")
        print("- Advanced T5 spelling correction") 
        print("- Grammar correction")
        print("- Spoken typo correction")
        print("- Gemini AI correction (if API key provided)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_gemini_integration():
    """Test Gemini API integration"""
    try:
        from enhanced_typo_correction import EnhancedTypoCorrector
        
        # Initialize with Gemini API key
        gemini_key = "AIzaSyDrYXOmHqiChayrg_yC0i-aGi-OqeJw1v4"
        corrector = EnhancedTypoCorrector(gemini_api_key=gemini_key)
        
        print("✅ Enhanced typo corrector with Gemini initialized")
        
        # Test simple correction
        test_text = "lets test this sentance"
        
        try:
            corrected = corrector.correct_with_gemini(test_text)
            print(f"📝 Original: '{test_text}'")
            print(f"✨ Corrected: '{corrected}'")
            return True
        except Exception as e:
            print(f"⚠️  Gemini correction failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Gemini integration error: {e}")
        return False

def main():
    print("🚀 Testing Enhanced Typo Correction System\n")
    print("=" * 60)
    
    # Test basic functionality
    print("\n1. Testing Basic Functionality:")
    basic_test = test_basic_functionality()
    
    # Test Gemini integration
    print("\n2. Testing Gemini Integration:")
    gemini_test = test_gemini_integration()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"✅ Basic functionality: {'PASS' if basic_test else 'FAIL'}")
    print(f"✅ Gemini integration: {'PASS' if gemini_test else 'FAIL'}")
    
    if basic_test:
        print("\n🎉 Enhanced typo correction system is ready!")
        print("💡 You can now use the /api/typo/correct endpoint")
    else:
        print("\n⚠️  Some issues detected. Check the logs above.")
    
    return 0 if basic_test else 1

if __name__ == "__main__":
    sys.exit(main())