import requests
import json
import os

def test_gemini_api():
    """Test Gemini API connection"""
    api_key = "AIzaSyDrYXOmHqiChayrg_yC0i-aGi-OqeJw1v4"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{"text": "Hello, can you respond with 'API working correctly'?"}]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 100
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                text = result['candidates'][0]['content']['parts'][0]['text']
                print(f"✅ API Response: {text}")
                return True
            else:
                print("❌ No candidates in response")
                return False
        else:
            print(f"❌ API Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Gemini API...")
    success = test_gemini_api()
    print(f"Result: {'✅ SUCCESS' if success else '❌ FAILED'}")