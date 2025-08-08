#!/bin/bash

# LangGraph RAG System Setup Script
# This script helps setup the development environment

set -e  # Exit on any error

echo "🚀 LangGraph RAG System Setup"
echo "=============================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if required tools are installed
check_requirements() {
    print_info "Checking system requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_success "Docker is installed"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_warning "docker-compose not found, checking for 'docker compose'..."
        if ! docker compose version &> /dev/null; then
            print_error "Docker Compose is not available. Please install Docker Compose."
            exit 1
        fi
        print_success "Docker Compose is available"
    else
        print_success "Docker Compose is installed"
    fi
    
    # Check if ports are available
    check_port() {
        if lsof -i :$1 &> /dev/null; then
            print_warning "Port $1 is already in use"
            return 1
        fi
        return 0
    }
    
    print_info "Checking port availability..."
    check_port 3000 || print_warning "Frontend port 3000 is in use"
    check_port 8000 || print_warning "Backend port 8000 is in use"
    check_port 6333 || print_warning "Qdrant port 6333 is in use"
    check_port 11434 || print_warning "Ollama port 11434 is in use"
}

# Setup environment file
setup_environment() {
    print_info "Setting up environment configuration..."
    
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            print_success "Created .env file from .env.example"
            print_warning "Please review and update .env file with your specific configuration"
        else
            print_error ".env.example file not found"
            exit 1
        fi
    else
        print_info ".env file already exists"
    fi
}

# Install Ollama if not present
install_ollama() {
    print_info "Checking Ollama installation..."
    
    if ! command -v ollama &> /dev/null; then
        print_info "Installing Ollama..."
        curl -fsSL https://ollama.ai/install.sh | sh
        print_success "Ollama installed"
    else
        print_success "Ollama is already installed"
    fi
    
    # Check if Ollama service is running
    if ! pgrep -x "ollama" > /dev/null; then
        print_info "Starting Ollama service..."
        ollama serve &
        sleep 5
    fi
    
    # Pull required models
    print_info "Pulling required models (this may take a while)..."
    
    print_info "Pulling ArceeAgent model..."
    if ollama pull arcee-ai/arcee-agent; then
        print_success "ArceeAgent model pulled successfully"
    else
        print_warning "Failed to pull ArceeAgent model. You may need to pull it manually."
    fi
    
    print_info "Pulling CodeLlama model..."
    if ollama pull codellama:7b; then
        print_success "CodeLlama model pulled successfully"
    else
        print_warning "Failed to pull CodeLlama model. You may need to pull it manually."
    fi
}

# Build and start services
start_services() {
    print_info "Building and starting services with Docker Compose..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose up --build -d
    else
        docker compose up --build -d
    fi
    
    print_success "Services started successfully!"
    print_info "Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    check_services_health
}

# Check if services are healthy
check_services_health() {
    print_info "Checking service health..."
    
    # Check Qdrant
    if curl -f http://localhost:6333/collections > /dev/null 2>&1; then
        print_success "Qdrant is healthy"
    else
        print_warning "Qdrant might not be ready yet"
    fi
    
    # Check Ollama
    if curl -f http://localhost:11434/api/tags > /dev/null 2>&1; then
        print_success "Ollama is healthy"
    else
        print_warning "Ollama might not be ready yet"
    fi
    
    # Check FastAPI
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_success "FastAPI backend is healthy"
    else
        print_warning "FastAPI backend might not be ready yet"
    fi
    
    # Check React frontend
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        print_success "React frontend is healthy"
    else
        print_warning "React frontend might not be ready yet"
    fi
}

# Main setup function
main() {
    echo "This script will set up your LangGraph RAG system development environment."
    echo ""
    
    # Check if running from correct directory
    if [ ! -f "docker-compose.yml" ]; then
        print_error "Please run this script from the project root directory"
        exit 1
    fi
    
    check_requirements
    setup_environment
    
    echo ""
    read -p "Do you want to install/update Ollama and pull models? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_ollama
    fi
    
    echo ""
    read -p "Do you want to start the services with Docker Compose? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        start_services
    fi
    
    echo ""
    print_success "Setup completed!"
    echo ""
    print_info "Service URLs:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000"
    echo "  API Documentation: http://localhost:8000/docs"
    echo "  Qdrant: http://localhost:6333/dashboard"
    echo "  Ollama: http://localhost:11434"
    echo ""
    print_info "To test the API, run:"
    echo "  ./tests/curl_tests.sh"
    echo ""
    print_info "To stop services:"
    echo "  docker-compose down"
    echo ""
    print_info "To view logs:"
    echo "  docker-compose logs -f"
}

# Run main function
main "$@"
