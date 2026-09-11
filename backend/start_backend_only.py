#!/usr/bin/env python3
"""
Quick backend startup script for testing
"""
import subprocess
import sys
import os
import time

def start_backend():
    print("🚀 Starting Refinify Backend...")
    
    # Kill any existing process on port 8000
    try:
        subprocess.run(["lsof", "-ti:8000"], capture_output=True, check=True)
        print("🔄 Killing existing process on port 8000...")
        subprocess.run(["lsof", "-ti:8000", "|", "xargs", "kill", "-9"], shell=True)
        time.sleep(2)
    except subprocess.CalledProcessError:
        print("✅ Port 8000 is free")
    
    # Start backend
    try:
        print("🔧 Activating virtual environment and starting Flask...")
        os.chdir("backend")
        
        # Activate venv and start app
        if os.path.exists("venv/bin/activate"):
            cmd = "source venv/bin/activate && python app.py"
        else:
            cmd = "python app.py"
        
        subprocess.run(cmd, shell=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Backend stopped by user")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")

if __name__ == "__main__":
    start_backend()