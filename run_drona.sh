#!/bin/bash

# Bhishma's Clinical Trial Prediction System - Enhanced Startup Script
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

echo "🚀 Starting Bhishma's Clinical Trial Prediction System..."
echo "📁 Project directory: $SCRIPT_DIR"

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "node.*vite" 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true
sleep 2

# Setup Backend
echo "📡 Setting up backend..."
cd "$BACKEND_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install -q -r requirements.txt
fi

# Start backend
echo "Starting backend server on port 8000..."
nohup python3 app.py > "$BACKEND_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo "✅ Backend started with PID: $BACKEND_PID"

# Wait for backend to initialize
echo "⏳ Waiting for backend to initialize..."
sleep 5

# Setup Frontend
echo "🌐 Setting up frontend..."
cd "$FRONTEND_DIR"

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

# Start frontend
echo "Starting frontend server on port 5173..."
nohup npm run dev > "$FRONTEND_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend started with PID: $FRONTEND_PID"

# Wait for services to start
sleep 5

echo ""
echo "🎉 Bhishma's System is running!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Frontend:  http://localhost:5173"
echo "🔧 Backend:   http://localhost:8000"
echo "📊 Health:    http://localhost:8000/health"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 Logs:"
echo "   Backend:  $BACKEND_DIR/backend.log"
echo "   Frontend: $FRONTEND_DIR/frontend.log"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Press Ctrl+C to stop all services"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    pkill -f "python.*app.py" 2>/dev/null || true
    pkill -f "node.*vite" 2>/dev/null || true
    echo "✅ All services stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Keep script running
while true; do
    sleep 30
done