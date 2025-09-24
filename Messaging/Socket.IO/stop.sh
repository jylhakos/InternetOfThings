#!/bin/bash

# Weather Streaming Application Stop Script

echo "🛑 Stopping Weather Streaming Application..."

# Function to kill process by PID file
kill_by_pid_file() {
    local pid_file=$1
    local service_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo "🔴 Stopping $service_name (PID: $pid)..."
            kill "$pid"
            # Wait a bit and force kill if necessary
            sleep 2
            if kill -0 "$pid" 2>/dev/null; then
                echo "⚠️  Force killing $service_name..."
                kill -9 "$pid"
            fi
        fi
        rm -f "$pid_file"
        echo " $service_name stopped"
    else
        echo "ℹ️  No PID file found for $service_name"
    fi
}

# Stop services
kill_by_pid_file "logs/backend.pid" "Backend"
kill_by_pid_file "logs/frontend.pid" "Frontend"

# Kill any remaining processes on the ports
echo "🧹 Cleaning up any remaining processes..."

# Kill processes on port 8000 (backend)
if lsof -i :8000 >/dev/null 2>&1; then
    echo "🔴 Killing processes on port 8000..."
    lsof -ti :8000 | xargs kill -9 2>/dev/null || true
fi

# Kill processes on port 5173 (frontend)
if lsof -i :5173 >/dev/null 2>&1; then
    echo "🔴 Killing processes on port 5173..."
    lsof -ti :5173 | xargs kill -9 2>/dev/null || true
fi

# Kill any uvicorn processes
pkill -f "uvicorn.*main:socket_app" 2>/dev/null || true

# Kill any vite processes
pkill -f "vite" 2>/dev/null || true

echo "🏁 All services stopped successfully!"

# Clean up log files if they exist
if [ -d "logs" ]; then
    echo "🧹 Cleaning up log files..."
    rm -f logs/*.pid
    # Optionally archive logs
    if [ -f "logs/backend.log" ] || [ -f "logs/frontend.log" ]; then
        timestamp=$(date +"%Y%m%d_%H%M%S")
        mkdir -p logs/archive
        [ -f "logs/backend.log" ] && mv logs/backend.log "logs/archive/backend_$timestamp.log"
        [ -f "logs/frontend.log" ] && mv logs/frontend.log "logs/archive/frontend_$timestamp.log"
        echo "📦 Logs archived to logs/archive/"
    fi
fi

echo "✨ Cleanup complete!"