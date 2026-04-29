#!/bin/bash
# Quick start script for Open WebUI with AI Agent backend

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_status "Docker is installed"
    
    # Check if Docker daemon is running
    if ! docker ps &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker."
        exit 1
    fi
    print_status "Docker daemon is running"
    
    # Check if AI Agent is running
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_status "AI Agent is running at http://localhost:8000"
    else
        print_warning "AI Agent is not running at http://localhost:8000"
        print_status "Will attempt to start AI Agent..."
        start_ai_agent
    fi
}

# Start AI Agent if not running
start_ai_agent() {
    print_header "Starting AI Agent"
    
    # Check if Python virtual environment exists
    if [ -d "venv" ]; then
        print_status "Using existing virtual environment"
        source venv/bin/activate
    else
        print_warning "Virtual environment not found. Creating one..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    fi
    
    # Check if Ollama is running
    if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        print_warning "Ollama is not running. Please start Ollama first:"
        echo "  ollama serve &"
        echo "  ollama pull llama4:scout"
        exit 1
    fi
    
    # Start AI Agent in background
    print_status "Starting AI Agent in background..."
    nohup python src/index.py > ai_agent.log 2>&1 &
    AI_AGENT_PID=$!
    echo $AI_AGENT_PID > ai_agent.pid
    
    # Wait for AI Agent to start
    print_status "Waiting for AI Agent to start..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            print_status "AI Agent started successfully"
            break
        fi
        sleep 1
    done
    
    # Check if it actually started
    if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_error "Failed to start AI Agent. Check ai_agent.log for details."
        exit 1
    fi
}

# Start Open WebUI
start_open_webui() {
    print_header "Starting Open WebUI"
    
    # Check if container already exists
    if docker ps -a | grep -q "open-webui"; then
        print_status "Stopping existing Open WebUI container..."
        docker stop open-webui 2>/dev/null || true
        docker rm open-webui 2>/dev/null || true
    fi
    
    # Start Open WebUI container
    print_status "Starting Open WebUI container..."
    docker run -d \
        --name open-webui \
        --restart unless-stopped \
        -p 3000:8080 \
        -e OPENAI_API_BASE_URL=http://host.docker.internal:8000/v1 \
        -e OPENAI_API_KEY=dummy \
        -e DEFAULT_MODELS=ai-agent-llama4-scout \
        -e ENABLE_SIGNUP=true \
        -e WEBUI_NAME="AI Agent - Llama 4 Scout" \
        -e DEFAULT_USER_ROLE=admin \
        -v open-webui-data:/app/backend/data \
        ghcr.io/open-webui/open-webui:main
    
    # Wait for Open WebUI to start
    print_status "Waiting for Open WebUI to start..."
    for i in {1..60}; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            print_status "Open WebUI started successfully"
            break
        fi
        sleep 2
    done
    
    # Check if it actually started
    if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
        print_error "Failed to start Open WebUI. Check container logs:"
        echo "  docker logs open-webui"
        exit 1
    fi
}

# Test the setup
test_setup() {
    print_header "Testing Setup"
    
    # Test AI Agent health
    print_status "Testing AI Agent..."
    health_response=$(curl -s http://localhost:8000/health)
    if echo "$health_response" | grep -q "healthy"; then
        print_status "AI Agent health check passed"
    else
        print_error "AI Agent health check failed"
    fi
    
    # Test Open WebUI
    print_status "Testing Open WebUI..."
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        print_status "Open WebUI is accessible"
    else
        print_error "Open WebUI is not accessible"
    fi
    
    # Test API endpoint
    print_status "Testing API endpoint..."
    api_response=$(curl -s -X POST http://localhost:8000/v1/chat/completions \
        -H "Content-Type: application/json" \
        -d '{"messages": [{"role": "user", "content": "Hello, test message"}], "temperature": 0.1}')
    
    if echo "$api_response" | grep -q "choices"; then
        print_status "API endpoint test passed"
    else
        print_error "API endpoint test failed"
    fi
}

# Show status and instructions
show_instructions() {
    print_header "Setup Complete!"
    echo
    echo "🌐 Access points:"
    echo "   • Open WebUI: http://localhost:3000"
    echo "   • AI Agent API: http://localhost:8000"
    echo "   • Health Check: http://localhost:8000/health"
    echo "   • API Docs: http://localhost:8000/docs"
    echo
    echo "📝 How to use Open WebUI:"
    echo "   1. Open http://localhost:3000 in your browser"
    echo "   2. Create an account (any email/password works)"
    echo "   3. Select 'ai-agent-llama4-scout' model"
    echo "   4. Start chatting!"
    echo
    echo "💬 Example messages to try:"
    echo "   • \"Hello, how are you?\""
    echo "   • \"What's the temperature in London?\""
    echo "   • \"Compare weather in Tokyo and Paris\""
    echo "   • \"Explain quantum computing\""
    echo
    echo "🧪 Test the API directly:"
    echo "   ./test_api_examples.sh"
    echo
    echo "🔧 Management commands:"
    echo "   • View AI Agent logs: tail -f ai_agent.log"
    echo "   • View WebUI logs: docker logs open-webui"
    echo "   • Stop WebUI: docker stop open-webui"
    echo "   • Stop AI Agent: kill \$(cat ai_agent.pid 2>/dev/null) 2>/dev/null"
    echo "   • Restart everything: $0"
}

# Cleanup function
cleanup() {
    print_header "Cleaning Up"
    docker stop open-webui 2>/dev/null || true
    docker rm open-webui 2>/dev/null || true
    if [ -f ai_agent.pid ]; then
        kill $(cat ai_agent.pid) 2>/dev/null || true
        rm ai_agent.pid
    fi
    print_status "Cleanup complete"
}

# Handle script arguments
case "${1:-}" in
    "stop"|"cleanup")
        cleanup
        exit 0
        ;;
    "test")
        test_setup
        exit 0
        ;;
esac

# Main execution
main() {
    echo -e "${GREEN}🚀 Starting AI Agent + Open WebUI Setup${NC}"
    echo
    
    check_prerequisites
    start_open_webui
    test_setup
    show_instructions
}

# Trap cleanup on script exit
trap cleanup EXIT

# Run main function
main "$@"
