#!/bin/bash

# AI Agent Observability - Setup Script for Linux
# This script sets up the virtual environment and installs all dependencies

set -e  # Exit on error

echo "=========================================="
echo "AI Agent Observability Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "$1"
}

# Check if Python 3 is installed
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    echo "Please install Python 3.9 or higher:"
    echo "  sudo apt update"
    echo "  sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_success "Python $PYTHON_VERSION found"

# Check Python version (require 3.9+)
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]; }; then
    print_error "Python 3.9 or higher is required (found $PYTHON_VERSION)"
    exit 1
fi

print_success "Python version is compatible (3.9+)"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        print_info "Removed existing virtual environment"
    else
        print_info "Using existing virtual environment"
    fi
fi

if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel
print_success "pip upgraded"

# Install dependencies
echo ""
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt
print_success "Dependencies installed"

# Create necessary directories
echo ""
echo "Creating project directories..."
mkdir -p data
mkdir -p results
mkdir -p notebooks
mkdir -p configs
print_success "Directories created"

# Setup .env file
echo ""
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    print_warning ".env file created - PLEASE EDIT IT WITH YOUR API KEYS"
    print_info "Edit .env file to add your API keys:"
    print_info "  - OPENAI_API_KEY"
    print_info "  - LANGFUSE_PUBLIC_KEY"
    print_info "  - LANGFUSE_SECRET_KEY"
else
    print_info ".env file already exists"
fi

# Check if Docker is installed (for Langfuse local deployment)
echo ""
echo "Checking for Docker (optional, for local Langfuse deployment)..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | tr -d ',')
    print_success "Docker $DOCKER_VERSION found"
    
    if command -v docker-compose &> /dev/null; then
        print_success "Docker Compose found"
        print_info "You can deploy Langfuse locally with:"
        print_info "  cd langfuse-local && docker-compose up -d"
    else
        print_warning "Docker Compose not found"
        print_info "Install with: sudo apt install docker-compose"
    fi
else
    print_warning "Docker not found"
    print_info "For local Langfuse deployment, install Docker:"
    print_info "  sudo apt install docker.io docker-compose"
fi

# Run installation verification
echo ""
echo "=========================================="
echo "Verifying Installation"
echo "=========================================="
python sources/test_installation.py

# Final instructions
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
print_success "Virtual environment is ready"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit .env file with your API keys:"
echo "   nano .env"
echo ""
echo "2. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. Run the agent evaluation example:"
echo "   python sources/agent_evaluation.py"
echo ""
echo "4. Run batch evaluation:"
echo "   python sources/run_evaluation.py"
echo ""
echo "5. (Optional) Deploy Langfuse locally:"
echo "   mkdir -p langfuse-local"
echo "   cd langfuse-local"
echo "   curl -o docker-compose.yml https://raw.githubusercontent.com/langfuse/langfuse/main/docker-compose.yml"
echo "   docker-compose up -d"
echo "   # Access at http://localhost:3000"
echo ""
echo "For more information, see README.md"
echo ""
