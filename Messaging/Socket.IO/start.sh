#!/bin/bash

# Weather Streaming Application Startup Script
# This script helps you start the development environment

set -e

echo "🌤️  Weather Streaming Application Startup"
echo "========================================"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Check dependencies
echo "📋 Checking dependencies..."

if ! command_exists python3; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is not installed"
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is not installed"
    exit 1
fi

echo " All dependencies found"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run setup.sh first."
    exit 1
fi

# Check if ports are available
if port_in_use 8000; then
    echo "⚠️  Port 8000 is already in use. Please stop the process or use a different port."
    exit 1
fi

if port_in_use 5173; then
    echo "⚠️  Port 5173 is already in use. Please stop the process or use a different port."
    exit 1
fi

# Start backend
echo "🚀 Starting backend server..."
cd backend
source ../venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.production.example .env
    echo "📝 Please edit backend/.env with your configuration"
fi

# Start backend in background
nohup python main.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "📍 Backend started with PID: $BACKEND_PID"

cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Check if backend is running
if ! curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "❌ Backend failed to start. Check logs/backend.log"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi
echo " Backend is running on http://localhost:8000"

# Start frontend
echo "🎨 Starting frontend server..."
cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Start frontend in background
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "📍 Frontend started with PID: $FRONTEND_PID"

cd ..

# Create logs directory
mkdir -p logs

# Save PIDs for cleanup
echo $BACKEND_PID > logs/backend.pid
echo $FRONTEND_PID > logs/frontend.pid

echo ""
echo "🎉 Application started successfully!"
echo ""
echo "📱 Frontend: http://localhost:5173"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "📋 Useful commands:"
echo "   View backend logs: tail -f logs/backend.log"
echo "   View frontend logs: tail -f logs/frontend.log"
echo "   Stop application: ./stop.sh"
echo ""
echo "⏳ Waiting for frontend to start..."
sleep 10

if curl -f http://localhost:5173 >/dev/null 2>&1; then
    echo " Frontend is running!"
    echo "🌐 Open http://localhost:5173 in your browser"
else
    echo "⚠️  Frontend might still be starting. Check logs/frontend.log"
fi

echo ""
echo "🏁 Setup complete! Press Ctrl+C to stop monitoring, or run ./stop.sh to stop all services."

# Monitor processes
trap 'echo "Stopping..."; ./stop.sh 2>/dev/null || true; exit 0' INT TERM

# Keep script running
tail -f logs/backend.log logs/frontend.log