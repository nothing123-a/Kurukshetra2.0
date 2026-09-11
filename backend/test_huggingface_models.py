#!/usr/bin/env python3
"""
Test script for Hugging Face models used in Refinify
Tests all 4 models mentioned in the requirements
"""

import os
import sys
from transformers import pipeline, T5ForConditionalGeneration, AutoTokenizer, T5Tokenizer

def test_model_1():
    """Test oliverguhr/spelling-correction-english-base"""
    print("Testing Model 1: oliverguhr/spelling-correction-english-base")
    try:
        fix_spelling = pipeline("text2text-generation", model="oliverguhr/spelling-correction-english-base")
        result = fix_spelling("lets do a comparsion", max_length=2048)
        print(f"Input: 'lets do a comparsion'")
        print(f"Output: {result[0]['generated_text']}")
        print("✅ Model 1 working correctly\n")
        return True
    except Exception as e:
        print(f"❌ Model 1 failed: {e}\n")
        return False

def test_model_2():
    """Test ai-forever/T5-large-spell"""
    print("Testing Model 2: ai-forever/T5-large-spell")
    try:
        model_name = "ai-forever/T5-large-spell"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = T5ForConditionalGeneration.from_pretrained(model_name)
        
        text = "If you bought something goregous, you well be very happy."
        input_text = f"grammar: {text}"
        inputs = tokenizer(input_text, return_tensors="pt")
        outputs = model.generate(**inputs)
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        print(f"Input: '{text}'")
        print(f"Output: {result}")
        print("✅ Model 2 working correctly\n")
        return True
    except Exception as e:
        print(f"❌ Model 2 failed: {e}\n")
        return False

def test_model_3():
    """Test vennify/t5-base-grammar-correction"""
    print("Testing Model 3: vennify/t5-base-grammar-correction")
    try:
        from happytransformer import HappyTextToText, TTSettings
        
        happy_tt = HappyTextToText("T5", "vennify/t5-base-grammar-correction")
        args = TTSettings(num_beams=5, min_length=1)
        result = happy_tt.generate_text("grammar: This sentences has has bads grammar.", args=args)
        
        print(f"Input: 'This sentences has has bads grammar.'")
        print(f"Output: {result.text}")
        print("✅ Model 3 working correctly\n")
        return True
    except Exception as e:
        print(f"❌ Model 3 failed: {e}\n")
        return False

def test_model_4():
    """Test willwade/t5-small-spoken-typo"""
    print("Testing Model 4: willwade/t5-small-spoken-typo")
    try:
        model_name = "willwade/t5-small-spoken-typo"
        tokenizer = T5Tokenizer.from_pretrained(model_name)
        model = T5ForConditionalGeneration.from_pretrained(model_name)
        
        input_text = "grammar: Hihowareyoudoingtaday?."
        inputs = tokenizer(input_text, return_tensors="pt")
        output = model.generate(**inputs, num_beams=5, min_length=1, max_new_tokens=50)
        result = tokenizer.decode(output[0], skip_special_tokens=True)
        
        print(f"Input: 'Hihowareyoudoingtaday?.'")
        print(f"Output: {result}")
        print("✅ Model 4 working correctly\n")
        return True
    except Exception as e:
        print(f"❌ Model 4 failed: {e}\n")
        return False

def main():
    print("🚀 Testing Hugging Face Models for Refinify\n")
    print("=" * 60)
    
    results = []
    results.append(test_model_1())
    results.append(test_model_2())
    results.append(test_model_3())
    results.append(test_model_4())
    
    print("=" * 60)
    print("📊 Test Results Summary:")
    print(f"✅ Passed: {sum(results)}/4")
    print(f"❌ Failed: {4 - sum(results)}/4")
    
    if all(results):
        print("\n🎉 All models are working correctly!")
        return 0
    else:
        print("\n⚠️  Some models failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())