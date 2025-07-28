#!/bin/bash

# start_dev.sh - Development startup script for LLM system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_service() {
    echo -e "${CYAN}[SERVICE]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found. Please run this script from the project root directory."
    exit 1
fi

# Function to check if service is running
check_service() {
    local service_name=$1
    local url=$2
    local max_attempts=30
    local attempt=1

    print_info "Checking $service_name at $url..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            print_info "$service_name is ready! ✅"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name failed to start after $((max_attempts * 2)) seconds"
    return 1
}

# Function to show service status
show_status() {
    echo ""
    print_step "Service Status Check"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    services=(
        "Redis:http://localhost:6379"
        "Ollama:http://localhost:11434"
        "LangChain:http://localhost:3000/health"
        "FastAPI:http://localhost:8000/health"
        "Flower:http://localhost:5555"
    )
    
    for service_info in "${services[@]}"; do
        IFS=':' read -ra PARTS <<< "$service_info"
        service_name="${PARTS[0]}"
        service_url="${PARTS[1]}:${PARTS[2]}"
        
        if curl -s "$service_url" > /dev/null 2>&1; then
            print_service "$service_name: ✅ Running"
        else
            print_service "$service_name: ❌ Not accessible"
        fi
    done
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Function to show URLs
show_urls() {
    echo ""
    print_step "Service URLs"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🌐 FastAPI (Main API):       http://localhost:8000"
    echo "📚 API Documentation:       http://localhost:8000/docs"
    echo "🔧 LangChain Service:       http://localhost:3000"
    echo "🌺 Flower (Monitoring):     http://localhost:5555"
    echo "🌍 Open WebUI (Chat):       http://localhost:3001"
    echo "🦙 Ollama API:              http://localhost:11434"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Function to show useful commands
show_commands() {
    echo ""
    print_step "Useful Commands"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 Test the system:         ./test_system.py"
    echo "📝 View logs:               docker-compose logs -f"
    echo "🔄 Restart services:        docker-compose restart"
    echo "🛑 Stop services:           docker-compose down"
    echo "🧹 Clean up:                docker-compose down -v"
    echo "⚖️  Scale workers:           docker-compose up --scale celery-worker=4"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Main execution
echo "🚀 Starting LLM FastAPI + Celery + LangChain.js Development Environment"
echo "════════════════════════════════════════════════════════════════════════"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose."
    exit 1
fi

print_step "Stopping any existing containers..."
docker-compose down 2>/dev/null || true

print_step "Pulling latest images..."
docker-compose pull

print_step "Building and starting services..."
docker-compose up -d --build

print_step "Waiting for services to start..."
echo "This may take a few minutes, especially for Ollama to download models..."

# Wait for core services
sleep 10

# Check Redis
print_info "Checking Redis..."
if ! check_service "Redis" "http://localhost:6379"; then
    print_error "Redis failed to start"
    docker-compose logs redis
    exit 1
fi

# Check Ollama (may take longer)
print_info "Checking Ollama (this may take a while for first-time model download)..."
if ! check_service "Ollama" "http://localhost:11434"; then
    print_warning "Ollama may still be downloading models. Check with: docker-compose logs ollama"
fi

# Check LangChain service
print_info "Checking LangChain service..."
if ! check_service "LangChain Service" "http://localhost:3000/health"; then
    print_warning "LangChain service not ready. Check logs with: docker-compose logs langchain-service"
fi

# Check FastAPI
print_info "Checking FastAPI..."
if ! check_service "FastAPI" "http://localhost:8000/health"; then
    print_warning "FastAPI not ready. Check logs with: docker-compose logs fastapi"
fi

# Show final status
show_status
show_urls
show_commands

echo ""
print_info "🎉 Development environment is starting up!"
print_info "💡 Run './test_system.py' to verify everything is working correctly"
print_info "📋 Use 'docker-compose logs -f' to view all service logs"

# Option to run tests
echo ""
read -p "Would you like to run the system tests now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_step "Running system tests..."
    sleep 5  # Give services a bit more time
    python3 test_system.py --verbose
fi

echo ""
print_info "🔥 Ready to go! Happy coding! 🔥"
