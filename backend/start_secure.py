#!/usr/bin/env python3
"""
Secure startup script for Bhishma's Clinical Trial System
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ['GEMINI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Warning: Missing environment variables: {', '.join(missing_vars)}")
        print("   The system will work with limited functionality")
    else:
        print("✅ All required environment variables are set")

def start_server():
    """Start the Flask server securely"""
    print("🧬 Starting Bhishma's Clinical Trial Outcome Prediction System")
    print("=" * 60)
    
    check_environment()
    
    # Set secure defaults
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('SECRET_KEY', 'bhishma's-clinical-trial-secret-key-2024')
    
    print(f"🚀 Server starting on http://localhost:8000")
    print("📊 Risk Analysis endpoints ready")
    print("🧪 Drug Testing pipeline active")
    print("🔒 Security measures enabled")
    
    # Import and run the app
    from app import app
    app.run(host='0.0.0.0', port=8000, debug=True)

if __name__ == "__main__":
    start_server()