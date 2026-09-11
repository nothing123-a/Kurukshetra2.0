#!/usr/bin/env python3
"""
Check available Gemini models
"""
import requests
import os

def check_gemini_models():
    api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyCUD3MXSMK6Z9Klkt-D1volQBh6MLhzEEM')
    
    try:
        # List available models
        response = requests.get(
            f'https://generativelanguage.googleapis.com/v1beta/models?key={api_key}',
            timeout=10
        )
        
        if response.status_code == 200:
            models = response.json()
            print("Available Gemini models:")
            for model in models.get('models', []):
                name = model.get('name', '')
                if 'generateContent' in model.get('supportedGenerationMethods', []):
                    print(f"✅ {name}")
                else:
                    print(f"❌ {name} (no generateContent)")
        else:
            print(f"Error listing models: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")

def test_simple_gemini():
    """Test with a simple model name"""
    api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyCUD3MXSMK6Z9Klkt-D1volQBh6MLhzEEM')
    
    # Try the most basic model name
    model = 'gemini-pro'
    
    try:
        response = requests.post(
            f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}',
            json={'contents': [{'parts': [{'text': 'Hello, analyze this data: compound_id,score\nCOMP1,7.5'}]}]},
            timeout=20
        )
        
        print(f"Testing {model}: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(result['candidates'][0]['content']['parts'][0]['text'][:100])
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    print("🔍 Checking Gemini API...")
    check_gemini_models()
    print("\n🧪 Testing simple model...")
    test_simple_gemini()