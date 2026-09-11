#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from typo_correction import typo_corrector

def test_gemini_correction():
    print("Testing Gemini API correction...")
    test_text = "This is a test sentance with some typos and grammer mistakes."
    result = typo_corrector.correct_with_gemini(test_text)
    print(f"Original: {test_text}")
    print(f"Corrected: {result}")
    print("-" * 50)

def test_all_methods():
    print("Testing all correction methods...")
    test_text = "lets do a comparsion of diferent methds"
    results = typo_corrector.correct_all_methods(test_text)
    
    for method, corrected in results.items():
        print(f"{method.upper()}: {corrected}")
    print("-" * 50)

if __name__ == "__main__":
    print("🔧 Testing Typo Correction Service")
    print("=" * 50)
    
    try:
        test_gemini_correction()
        # test_all_methods()  # Comment out to avoid loading heavy models for now
        print("✅ Typo correction service is working!")
    except Exception as e:
        print(f"❌ Error: {e}")