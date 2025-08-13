#!/bin/bash

# MCP Setup Script for Linux/Debian
# This script automates the setup of MCP server with Ollama and Open WebUI

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Linux
check_os() {
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        log_error "This script is designed for Linux systems only"
        exit 1
    fi
    log_info "Running on Linux - proceeding with setup"
}

# Check if running as root (not recommended)
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "Running as root is not recommended for this setup"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Install Node.js and npm
install_nodejs() {
    log_info "Installing Node.js and npm..."
    
    # Check if Node.js is already installed
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version | cut -d'v' -f2)
        REQUIRED_VERSION="18.0.0"
        
        if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$NODE_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
            log_success "Node.js $NODE_VERSION is already installed and meets requirements"
            return
        else
            log_warning "Node.js $NODE_VERSION is installed but version >= $REQUIRED_VERSION is required"
        fi
    fi
    
    # Install Node.js via NodeSource repository
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
    
    # Verify installation
    if command -v node &> /dev/null && command -v npm &> /dev/null; then
        log_success "Node.js $(node --version) and npm $(npm --version) installed successfully"
    else
        log_error "Node.js installation failed"
        exit 1
    fi
}

# Install Docker
install_docker() {
    log_info "Installing Docker..."
    
    if command -v docker &> /dev/null; then
        log_success "Docker is already installed"
        return
    fi
    
    # Update package index
    sudo apt-get update
    
    # Install prerequisites
    sudo apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Set up stable repository
    echo \
        "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker Engine
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Add current user to docker group
    sudo usermod -aG docker $USER
    
    # Start Docker service
    sudo systemctl enable docker
    sudo systemctl start docker
    
    log_success "Docker installed successfully"
    log_warning "Please log out and back in for Docker group membership to take effect"
}

# Install Ollama
install_ollama() {
    log_info "Installing Ollama..."
    
    if command -v ollama &> /dev/null; then
        log_success "Ollama is already installed"
    else
        # Install Ollama
        curl -fsSL https://ollama.ai/install.sh | sh
        
        # Verify installation
        if command -v ollama &> /dev/null; then
            log_success "Ollama installed successfully"
        else
            log_error "Ollama installation failed"
            exit 1
        fi
    fi
    
    # Start Ollama service
    log_info "Starting Ollama service..."
    sudo systemctl enable ollama 2>/dev/null || true
    sudo systemctl start ollama 2>/dev/null || true
    
    # Wait for Ollama to start
    sleep 5
    
    # Check if Ollama is running
    if curl -s http://localhost:11434/api/version >/dev/null; then
        log_success "Ollama service is running"
    else
        log_warning "Ollama service may not be running properly"
        log_info "Starting Ollama in background..."
        nohup ollama serve > /dev/null 2>&1 &
        sleep 5
    fi
}

# Pull Llama models
pull_llama_models() {
    log_info "Pulling Llama-3.2 models..."
    
    # Pull different sizes of Llama 3.2
    models=("llama3.2:1b" "llama3.2:3b" "llama3.2:latest")
    
    for model in "${models[@]}"; do
        log_info "Pulling $model..."
        if ollama pull "$model"; then
            log_success "$model pulled successfully"
        else
            log_warning "Failed to pull $model - continuing with other models"
        fi
    done
    
    # List installed models
    log_info "Available models:"
    ollama list
}

# Setup project
setup_project() {
    log_info "Setting up MCP project..."
    
    # Create project directory if it doesn't exist
    if [ ! -d "$(pwd)" ]; then
        log_error "Please run this script from the MCP project directory"
        exit 1
    fi
    
    # Install Node.js dependencies
    log_info "Installing Node.js dependencies..."
    npm install
    
    # Install global development tools
    npm install -g tsx
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        log_info "Creating .env file..."
        cp .env.example .env
        log_success ".env file created from example"
    fi
    
    # Create logs directory
    mkdir -p logs
    
    # Build the project
    log_info "Building the project..."
    npm run build
    
    log_success "Project setup completed"
}

# Test the setup
test_setup() {
    log_info "Testing the setup..."
    
    # Test Ollama connection
    if curl -s http://localhost:11434/api/version >/dev/null; then
        log_success "Ollama is accessible"
    else
        log_error "Ollama is not accessible"
        return 1
    fi
    
    # Test if models are available
    if ollama list | grep -q "llama3.2"; then
        log_success "Llama-3.2 models are available"
    else
        log_warning "No Llama-3.2 models found"
    fi
    
    # Test MCP server (basic build check)
    if [ -f "dist/index.js" ]; then
        log_success "MCP server built successfully"
    else
        log_error "MCP server build not found"
        return 1
    fi
    
    log_success "Setup test completed successfully"
}

# Start services
start_services() {
    log_info "Starting services..."
    
    # Start with Docker Compose
    if [ -f "docker-compose.yml" ]; then
        log_info "Starting services with Docker Compose..."
        docker-compose up -d
        
        # Wait for services to start
        sleep 10
        
        # Check service health
        log_info "Checking service health..."
        
        if curl -s http://localhost:11434/api/version >/dev/null; then
            log_success "Ollama service is healthy"
        else
            log_warning "Ollama service health check failed"
        fi
        
        if curl -s http://localhost:3000/health >/dev/null; then
            log_success "MCP server is healthy"
        else
            log_warning "MCP server health check failed"
        fi
        
        if curl -s http://localhost:8080 >/dev/null; then
            log_success "Open WebUI is healthy"
        else
            log_warning "Open WebUI health check failed"
        fi
        
    else
        log_info "Starting MCP server directly..."
        npm run server &
        SERVER_PID=$!
        
        # Wait for server to start
        sleep 5
        
        if curl -s http://localhost:3000/health >/dev/null; then
            log_success "MCP server started successfully (PID: $SERVER_PID)"
        else
            log_error "Failed to start MCP server"
        fi
    fi
}

# Show usage information
show_usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  --install-deps    Install system dependencies only"
    echo "  --setup-project   Setup project only"
    echo "  --pull-models     Pull Llama models only"
    echo "  --start-services  Start services only"
    echo "  --test           Test setup only"
    echo "  --help           Show this help message"
    echo ""
    echo "If no options are provided, full setup will be performed."
}

# Main function
main() {
    log_info "🚀 Starting MCP setup for Linux/Debian..."
    
    # Parse command line arguments
    case "${1:-}" in
        --install-deps)
            check_os
            check_root
            install_nodejs
            install_docker
            install_ollama
            ;;
        --setup-project)
            setup_project
            ;;
        --pull-models)
            pull_llama_models
            ;;
        --start-services)
            start_services
            ;;
        --test)
            test_setup
            ;;
        --help)
            show_usage
            exit 0
            ;;
        "")
            # Full setup
            check_os
            check_root
            install_nodejs
            install_docker
            install_ollama
            pull_llama_models
            setup_project
            test_setup
            
            # Ask if user wants to start services
            echo
            read -p "Would you like to start the services now? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                start_services
            fi
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
    
    echo
    log_success "🎉 Setup completed successfully!"
    echo
    echo "Next steps:"
    echo "1. If you installed Docker, log out and back in for group membership to take effect"
    echo "2. Start the services:"
    echo "   - Docker Compose: docker-compose up -d"
    echo "   - Direct: npm run server"
    echo "3. Access the services:"
    echo "   - MCP Server: http://localhost:3000/health"
    echo "   - Open WebUI: http://localhost:8080"
    echo "   - Ollama API: http://localhost:11434/api/version"
    echo "4. Test the client: npm run client"
    echo
    echo "For more information, see the README.md file."
}

# Run main function
main "$@"
