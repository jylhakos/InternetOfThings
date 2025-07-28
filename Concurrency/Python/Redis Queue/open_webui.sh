#!/bin/bash

# Open WebUI Setup and Launch Script
# This script helps set up and run Open WebUI with the Redis Queue system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if a service is running on a port
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Check if Docker is installed and running
check_docker() {
    if ! command -v docker >/dev/null 2>&1; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    print_success "Docker is available and running"
}

# Check if the main system is running
check_main_system() {
    print_status "Checking if the main Redis Queue system is running..."
    
    if ! check_port 8000; then
        print_error "FastAPI server is not running on port 8000"
        print_status "Please start the main system first: ./start.sh start"
        exit 1
    fi
    
    # Test the health endpoint
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        print_success "Main system is running and healthy"
    else
        print_warning "Main system is running but may not be healthy"
    fi
    
    # Test OpenAI endpoints
    if curl -s -H "Authorization: Bearer test" http://localhost:8000/v1/models >/dev/null 2>&1; then
        print_success "OpenAI-compatible endpoints are available"
    else
        print_warning "OpenAI-compatible endpoints may not be working"
    fi
}

# Start Open WebUI using Docker
start_open_webui() {
    print_status "Starting Open WebUI..."
    
    # Check if Open WebUI is already running
    if check_port 3001; then
        print_warning "Open WebUI appears to be already running on port 3001"
        read -p "Do you want to restart it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Stopping existing Open WebUI container..."
            docker stop open-webui >/dev/null 2>&1 || true
            docker rm open-webui >/dev/null 2>&1 || true
        else
            print_status "Using existing Open WebUI instance"
            return 0
        fi
    fi
    
    # Start Open WebUI
    print_status "Pulling Open WebUI Docker image..."
    docker pull ghcr.io/open-webui/open-webui:main
    
    print_status "Starting Open WebUI container..."
    docker run -d \
        --name open-webui \
        -p 3001:8080 \
        -e OPENAI_API_BASE_URL="http://host.docker.internal:8000/v1" \
        -e OPENAI_API_KEY="sk-dummy-key-for-redis-queue-system" \
        -e WEBUI_SECRET_KEY="redis-queue-secret-key-change-in-production" \
        -e WEBUI_NAME="Redis Queue LLM Interface" \
        -e DEFAULT_USER_ROLE="user" \
        -e ENABLE_SIGNUP="true" \
        -v open-webui:/app/backend/data \
        --add-host=host.docker.internal:host-gateway \
        ghcr.io/open-webui/open-webui:main
    
    # Wait for Open WebUI to start
    print_status "Waiting for Open WebUI to start..."
    for i in {1..30}; do
        if check_port 3001; then
            print_success "Open WebUI is running on port 3001"
            break
        fi
        sleep 2
        if [ $i -eq 30 ]; then
            print_error "Open WebUI failed to start within 60 seconds"
            exit 1
        fi
    done
}

# Start using Docker Compose
start_with_compose() {
    print_status "Starting Open WebUI with Docker Compose..."
    
    if [ ! -f "docker-compose.yml" ]; then
        print_error "docker-compose.yml not found in current directory"
        exit 1
    fi
    
    # Start only Open WebUI service
    docker-compose up -d open-webui
    
    print_success "Open WebUI started with Docker Compose"
}

# Stop Open WebUI
stop_open_webui() {
    print_status "Stopping Open WebUI..."
    
    # Stop standalone container
    if docker ps -q -f name=open-webui >/dev/null 2>&1; then
        docker stop open-webui >/dev/null 2>&1
        docker rm open-webui >/dev/null 2>&1
        print_success "Stopped standalone Open WebUI container"
    fi
    
    # Stop compose service
    if [ -f "docker-compose.yml" ]; then
        docker-compose stop open-webui >/dev/null 2>&1 || true
        print_success "Stopped Open WebUI compose service"
    fi
}

# Show Open WebUI status
show_status() {
    print_status "Open WebUI Status Check"
    echo "=" * 30
    
    if check_port 3001; then
        print_success "Open WebUI: Running on port 3001"
        echo "   🌐 Web Interface: http://localhost:3001"
    else
        print_error "Open WebUI: Not running"
    fi
    
    if check_port 8000; then
        print_success "FastAPI Backend: Running on port 8000"
        echo "   🔗 API Base URL: http://localhost:8000/v1"
    else
        print_error "FastAPI Backend: Not running"
    fi
    
    # Check Docker container
    if docker ps -q -f name=open-webui >/dev/null 2>&1; then
        print_success "Docker Container: Running"
        echo "   📦 Container: open-webui"
    else
        print_warning "Docker Container: Not found"
    fi
}

# Setup and configuration guide
show_setup_guide() {
    print_status "Open WebUI Setup Guide"
    echo "=" * 40
    
    echo "
1. 🚀 Starting Open WebUI:
   ./open_webui.sh start

2. 🌐 Accessing the Interface:
   Open your browser to: http://localhost:3001

3. 🔧 Initial Configuration:
   - Create an account (first user becomes admin)
   - Go to Settings → Models
   - Verify API Base URL: http://host.docker.internal:8000/v1
   - API Key: sk-dummy-key-for-redis-queue-system

4. 📝 Available Models:
   - llama3.2:1b (recommended for testing)
   - llama3.2:3b
   - llama3.1:8b
   - codellama:7b
   - mistral:7b

5. 🎯 Prompt Templates:
   Use system prompts to configure different behaviors:
   
   Technical Expert:
   'You are a senior software engineer. Provide detailed technical explanations.'
   
   Creative Writer:
   'You are a creative writer. Generate imaginative, engaging content.'
   
   Friendly Tutor:
   'You are a patient tutor. Explain complex topics in simple terms.'

6. 🧪 Testing:
   Run test cases: python open_webui_tests.py
   Check cURL examples: python open_webui_tests.py curl

7. 🛑 Stopping:
   ./open_webui.sh stop
"
}

# Run tests
run_tests() {
    print_status "Running Open WebUI integration tests..."
    
    if [ -f "open_webui_tests.py" ]; then
        python3 open_webui_tests.py
    else
        print_error "Test file open_webui_tests.py not found"
        exit 1
    fi
}

# Show help
show_help() {
    echo "Open WebUI Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Start Open WebUI (default)"
    echo "  stop        Stop Open WebUI"
    echo "  restart     Restart Open WebUI"
    echo "  status      Show service status"
    echo "  compose     Start with Docker Compose"
    echo "  test        Run integration tests"
    echo "  setup       Show setup guide"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start    # Start Open WebUI"
    echo "  $0 status   # Check status"
    echo "  $0 test     # Run tests"
}

# Main script logic
case "${1:-start}" in
    "start")
        check_docker
        check_main_system
        start_open_webui
        echo ""
        print_success "Open WebUI is ready!"
        print_status "🌐 Web Interface: http://localhost:3001"
        print_status "🔗 API Base URL: http://localhost:8000/v1"
        print_status "🔑 API Key: sk-dummy-key-for-redis-queue-system"
        echo ""
        print_status "Run './open_webui.sh setup' for configuration guide"
        ;;
    "stop")
        stop_open_webui
        ;;
    "restart")
        stop_open_webui
        sleep 2
        check_docker
        check_main_system
        start_open_webui
        ;;
    "status")
        show_status
        ;;
    "compose")
        check_docker
        check_main_system
        start_with_compose
        ;;
    "test")
        run_tests
        ;;
    "setup")
        show_setup_guide
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
