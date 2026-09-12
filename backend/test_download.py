#!/usr/bin/env python3
"""
Test script to verify download functionality
"""

import requests
import json
import os

def test_download_functionality():
    """Test the download functionality"""
    
    base_url = "http://localhost:8000"
    
    # Test data
    test_user = {
        "username": "admin",
        "password": "admin123"
    }
    
    print("🧪 Testing Download Functionality")
    print("=" * 50)
    
    try:
        # 1. Login to get session
        print("1. Logging in...")
        session = requests.Session()
        login_response = session.post(f"{base_url}/login", json=test_user)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
        
        print("✅ Login successful")
        
        # 2. Create sample history with file
        print("\n2. Creating sample history...")
        sample_response = session.post(f"{base_url}/api/test/create-sample-history")
        
        if sample_response.status_code != 200:
            print(f"❌ Failed to create sample history: {sample_response.status_code}")
            return False
        
        sample_data = sample_response.json()
        history_id = sample_data['history_id']
        file_path = sample_data['file_path']
        
        print(f"✅ Sample history created with ID: {history_id}")
        print(f"   File path: {file_path}")
        
        # 3. Verify file exists
        if not os.path.exists(file_path):
            print(f"❌ File not found at: {file_path}")
            return False
        
        print("✅ File exists on disk")
        
        # 4. Test download endpoint
        print(f"\n3. Testing download endpoint...")
        download_url = f"{base_url}/api/history/{history_id}/download"
        download_response = session.get(download_url)
        
        if download_response.status_code != 200:
            print(f"❌ Download failed: {download_response.status_code}")
            print(f"   Response: {download_response.text}")
            return False
        
        print("✅ Download successful!")
        print(f"   Content-Type: {download_response.headers.get('Content-Type')}")
        print(f"   Content-Length: {len(download_response.content)} bytes")
        
        # 5. Save downloaded file
        output_file = f"downloaded_test_{history_id}.csv"
        with open(output_file, 'wb') as f:
            f.write(download_response.content)
        
        print(f"✅ Downloaded file saved as: {output_file}")
        
        # 6. Clean up
        print("\n4. Cleaning up...")
        try:
            os.remove(file_path)
            print("✅ Sample file removed")
        except Exception as e:
            print(f"⚠️  Could not remove sample file: {e}")
        
        try:
            os.remove(output_file)
            print("✅ Downloaded file removed")
        except Exception as e:
            print(f"⚠️  Could not remove downloaded file: {e}")
        
        print("\n🎉 All tests passed! Download functionality is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    print("Make sure your backend is running on http://localhost:8000")
    print("You can start it with: python start_simple.py")
    print()
    
    test_download_functionality()
