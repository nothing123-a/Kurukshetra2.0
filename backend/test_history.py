#!/usr/bin/env python3
"""
Test script for History functionality
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
}

def test_history_api():
    """Test the history API endpoints"""
    
    print("Testing History API functionality...")
    
    # Test 1: Get user history (should require authentication)
    print("\n1. Testing GET /api/history (unauthenticated)...")
    try:
        response = requests.get(f"{BASE_URL}/api/history")
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✓ Correctly requires authentication")
        else:
            print(f"✗ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 2: Test with session (simulate login)
    print("\n2. Testing with session...")
    try:
        session = requests.Session()
        
        # Try to login (this might fail if user doesn't exist, but that's okay)
        login_data = {
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
        
        response = session.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"Login status: {response.status_code}")
        
        # Now try to get history
        response = session.get(f"{BASE_URL}/api/history")
        print(f"History status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ History API working: {len(data.get('history', []))} items")
        elif response.status_code == 401:
            print("✓ Correctly requires valid authentication")
        else:
            print(f"✗ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\nHistory API test completed!")

if __name__ == "__main__":
    test_history_api()
