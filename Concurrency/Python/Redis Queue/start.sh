#!/bin/bash

# Startup script for Redis Queue + FastAPI + LangChain + Ollama system
# This script helps start all the required services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a service is running on a port
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Python
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3.8+."
        exit 1
    fi
    
    # Check Node.js
    if ! command_exists node; then
        print_error "Node.js is not installed. Please install Node.js 18+."
        exit 1
    fi
    
    # Check Redis
    if ! command_exists redis-server && ! check_port 6379; then
        print_error "Redis is not installed or running. Please install and start Redis."
        exit 1
    fi
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_warning "Python virtual environment not found. Creating one..."
        python3 -m venv venv
    fi
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_warning "Node.js dependencies not installed. Installing..."
        npm install
    fi
    
    print_success "All prerequisites checked!"
}

# Start Redis if not running
start_redis() {
    if check_port 6379; then
        print_success "Redis is already running on port 6379"
    else
        print_status "Starting Redis server..."
        if command_exists systemctl; then
            sudo systemctl start redis-server
            print_success "Redis started via systemctl"
        elif command_exists brew; then
            brew services start redis
            print_success "Redis started via brew"
        else
            redis-server --daemonize yes
            print_success "Redis started as daemon"
        fi
    fi
}

# Start Ollama if not running
start_ollama() {
    if check_port 11434; then
        print_success "Ollama is already running on port 11434"
    else
        print_status "Starting Ollama server..."
        if command_exists ollama; then
            ollama serve &
            sleep 5
            print_success "Ollama server started"
        else
            print_warning "Ollama not found. Please install Ollama manually."
            print_status "You can install it from: https://ollama.ai/"
        fi
    fi
}

# Install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
    print_success "Python dependencies installed"
}

# Install Node.js dependencies
install_node_deps() {
    print_status "Installing Node.js dependencies..."
    npm install
    print_success "Node.js dependencies installed"
}

# Function to start all services
start_services() {
    print_status "Starting all services..."
    
    # Start LangChain service
    print_status "Starting LangChain.js service..."
    npm start &
    LANGCHAIN_PID=$!
    sleep 3
    
    if check_port 3000; then
        print_success "LangChain.js service started on port 3000"
    else
        print_error "Failed to start LangChain.js service"
        exit 1
    fi
    
    # Start RQ Worker
    print_status "Starting RQ Worker..."
    source venv/bin/activate
    python worker.py &
    WORKER_PID=$!
    sleep 2
    print_success "RQ Worker started"
    
    # Start FastAPI server
    print_status "Starting FastAPI server..."
    source venv/bin/activate
    uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
    FASTAPI_PID=$!
    sleep 3
    
    if check_port 8000; then
        print_success "FastAPI server started on port 8000"
    else
        print_error "Failed to start FastAPI server"
        exit 1
    fi
    
    # Save PIDs for cleanup
    echo "$LANGCHAIN_PID $WORKER_PID $FASTAPI_PID" > .service_pids
    
    print_success "All services started successfully!"
    print_status "Services running:"
    print_status "  - FastAPI: http://localhost:8000"
    print_status "  - LangChain.js: http://localhost:3000"
    print_status "  - Redis: localhost:6379"
    print_status "  - Ollama: http://localhost:11434"
    print_status ""
    print_status "You can now test the system with:"
    print_status "  python test_client.py"
    print_status ""
    print_status "To stop all services, run: ./start.sh stop"
}

# Function to stop all services
stop_services() {
    print_status "Stopping all services..."
    
    if [ -f ".service_pids" ]; then
        read LANGCHAIN_PID WORKER_PID FASTAPI_PID < .service_pids
        
        if [ ! -z "$LANGCHAIN_PID" ]; then
            kill $LANGCHAIN_PID 2>/dev/null || true
            print_status "Stopped LangChain.js service"
        fi
        
        if [ ! -z "$WORKER_PID" ]; then
            kill $WORKER_PID 2>/dev/null || true
            print_status "Stopped RQ Worker"
        fi
        
        if [ ! -z "$FASTAPI_PID" ]; then
            kill $FASTAPI_PID 2>/dev/null || true
            print_status "Stopped FastAPI server"
        fi
        
        rm .service_pids
    fi
    
    # Kill any remaining processes
    pkill -f "uvicorn main:app" 2>/dev/null || true
    pkill -f "python worker.py" 2>/dev/null || true
    pkill -f "node langchain_service.js" 2>/dev/null || true
    
    print_success "All services stopped"
}

# Function to show service status
show_status() {
    print_status "Service Status:"
    
    if check_port 6379; then
        print_success "Redis: Running on port 6379"
    else
        print_error "Redis: Not running"
    fi
    
    if check_port 11434; then
        print_success "Ollama: Running on port 11434"
    else
        print_warning "Ollama: Not running"
    fi
    
    if check_port 3000; then
        print_success "LangChain.js: Running on port 3000"
    else
        print_error "LangChain.js: Not running"
    fi
    
    if check_port 8000; then
        print_success "FastAPI: Running on port 8000"
    else
        print_error "FastAPI: Not running"
    fi
}

# Function to show help
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start    Start all services (default)"
    echo "  stop     Stop all services"
    echo "  restart  Restart all services"
    echo "  status   Show service status"
    echo "  setup    Setup dependencies only"
    echo "  test     Run test client"
    echo "  webui    Start with Open WebUI"
    echo "  help     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start    # Start all services"
    echo "  $0 webui    # Start all services + Open WebUI"
    echo "  $0 status   # Check service status"
    echo "  $0 test     # Run interactive test"
}

# Main script logic
case "${1:-start}" in
    "start")
        check_prerequisites
        start_redis
        start_ollama
        start_services
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        stop_services
        sleep 2
        check_prerequisites
        start_redis
        start_ollama
        start_services
        ;;
    "status")
        show_status
        ;;
    "setup")
        check_prerequisites
        install_python_deps
        install_node_deps
        print_success "Setup completed!"
        ;;
    "test")
        python test_client.py
        ;;
    "webui")
        check_prerequisites
        start_redis
        start_ollama
        start_services
        sleep 5
        print_status "Starting Open WebUI..."
        ./open_webui.sh start
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
