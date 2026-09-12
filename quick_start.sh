#!/bin/bash

# Quick Start Script for Refinify
echo "🚀 Starting Refinify..."

# Kill any existing processes
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "node.*vite" 2>/dev/null || true

# Start backend
echo "📡 Starting backend..."
cd backend
source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1
python3 app.py &
BACKEND_PID=$!
cd ..

# Start frontend
echo "🌐 Starting frontend..."
cd frontend
npm install > /dev/null 2>&1
npm run dev &
FRONTEND_PID=$!
cd ..

echo "✅ Refinify is starting..."
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap 'echo "Stopping services..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0' INT
wait