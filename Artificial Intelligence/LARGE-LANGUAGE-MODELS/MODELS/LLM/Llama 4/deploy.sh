#!/bin/bash

# AI Agent No-Framework - Docker Deployment Script
# This script sets up and starts the fully containerized AI agent stack

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
PROD_COMPOSE_FILE="docker-compose.prod.yml"
PROJECT_NAME="ai-agent-no-framework"

print_header() {
    echo -e "${BLUE}"
    echo "=========================================="
    echo "  AI Agent No-Framework Docker Setup"
    echo "=========================================="
    echo -e "${NC}"
}

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "✓ Docker and Docker Compose are available"
}

create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs
    mkdir -p ollama-models
    mkdir -p ssl
    
    # Set proper permissions
    chmod 755 logs ollama-models
    
    print_status "✓ Directories created"
}

setup_environment() {
    print_status "Setting up environment configuration..."
    
    # Create .env.development if it doesn't exist
    if [ ! -f ".env.development" ]; then
        cat > .env.development << EOF
# Development Environment Configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=debug

# API Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
OLLAMA_BASE_URL=http://ollama:11434
MODEL_NAME=llama3.1:8b-instruct-q4_0

# WebUI Configuration
WEBUI_SECRET_KEY=dev-secret-key-change-in-production
EOF
        print_status "✓ Created .env.development"
    fi
    
    # Check if .env.production exists
    if [ ! -f ".env.production" ]; then
        print_warning ".env.production not found. Using development settings."
    fi
}

pull_models() {
    print_status "Pulling required models..."
    
    # Start only Ollama service first
    docker-compose up -d ollama
    
    # Wait for Ollama to be ready
    echo "Waiting for Ollama service to start..."
    for i in {1..30}; do
        if docker-compose exec ollama ollama list &> /dev/null; then
            break
        fi
        sleep 2
        echo -n "."
    done
    echo ""
    
    # Pull the required model
    print_status "Pulling Llama 3.1 model (this may take several minutes)..."
    docker-compose exec ollama ollama pull llama3.1:8b-instruct-q4_0
    
    print_status "✓ Model pulled successfully"
}

start_services() {
    local mode=${1:-development}
    local compose_file=$COMPOSE_FILE
    
    if [ "$mode" = "production" ]; then
        compose_file=$PROD_COMPOSE_FILE
    fi
    
    print_status "Starting AI Agent services in $mode mode..."
    
    # Build and start all services
    docker-compose -f $compose_file up --build -d
    
    # Wait for services to be healthy
    print_status "Waiting for services to be ready..."
    
    local max_attempts=60
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        local ai_agent_health=$(docker-compose -f $compose_file exec -T ai-agent curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000")
        
        if [ "$ai_agent_health" = "200" ]; then
            print_status "✓ AI Agent service is healthy"
            break
        fi
        
        sleep 5
        ((attempt++))
        echo -n "."
    done
    
    if [ $attempt -eq $max_attempts ]; then
        print_warning "AI Agent service may not be fully ready. Check logs with: docker-compose logs ai-agent"
    fi
    
    print_status "✓ Services started successfully"
}

show_service_info() {
    print_status "Service Information:"
    echo ""
    echo -e "${BLUE}AI Agent API:${NC}      http://localhost:8000"
    echo -e "${BLUE}Open WebUI:${NC}        http://localhost:3000"
    echo -e "${BLUE}Ollama API:${NC}        http://localhost:11434"
    echo ""
    echo -e "${BLUE}Health Check:${NC}      http://localhost:8000/health"
    echo -e "${BLUE}API Models:${NC}        http://localhost:8000/v1/models"
    echo ""
}

show_usage_examples() {
    echo -e "${BLUE}Usage Examples:${NC}"
    echo ""
    echo "1. Test the API directly:"
    echo "   curl -X POST http://localhost:8000/v1/chat/completions \\"
    echo "        -H 'Content-Type: application/json' \\"
    echo "        -d '{\"model\":\"ai-agent-no-framework\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello!\"}]}'"
    echo ""
    echo "2. Test weather functionality:"
    echo "   curl -X POST http://localhost:8000/v1/chat/completions \\"
    echo "        -H 'Content-Type: application/json' \\"
    echo "        -d '{\"model\":\"ai-agent-no-framework\",\"messages\":[{\"role\":\"user\",\"content\":\"What is the weather in London?\"}]}'"
    echo ""
    echo "3. Access Open WebUI at http://localhost:3000"
    echo ""
}

main() {
    print_header
    
    local mode="development"
    local pull_model=false
    local skip_deps=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --production)
                mode="production"
                shift
                ;;
            --pull-model)
                pull_model=true
                shift
                ;;
            --skip-deps)
                skip_deps=true
                shift
                ;;
            --help)
                echo "Usage: $0 [--production] [--pull-model] [--skip-deps]"
                echo "  --production: Use production configuration"
                echo "  --pull-model: Pull Llama model during setup"
                echo "  --skip-deps: Skip dependency checks"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    if [ "$skip_deps" = false ]; then
        check_dependencies
    fi
    
    create_directories
    setup_environment
    
    if [ "$pull_model" = true ]; then
        pull_models
    fi
    
    start_services "$mode"
    show_service_info
    show_usage_examples
    
    echo ""
    print_status "🚀 AI Agent No-Framework is now running!"
    print_status "View logs with: docker-compose logs -f"
    print_status "Stop services with: docker-compose down"
    
    if [ "$mode" = "production" ]; then
        print_warning "Remember to update security settings in .env.production for production use!"
    fi
}

# Run main function with all arguments
main "$@"
