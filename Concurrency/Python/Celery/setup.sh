#!/bin/bash

# setup.sh - Setup script for LLM FastAPI + Celery + LangChain.js project

set -e

echo "🚀 Setting up LLM FastAPI + Celery + LangChain.js project..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    print_warning "This script is designed for Linux (Debian/Ubuntu). Some commands may need adjustment for other systems."
fi

# Update system packages
print_status "Updating system packages..."
sudo apt update

# Install Python and pip if not already installed
print_status "Installing Python and pip..."
sudo apt install -y python3 python3-pip python3-venv

# Install Node.js if not already installed
if ! command -v node &> /dev/null; then
    print_status "Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
else
    print_status "Node.js already installed: $(node --version)"
fi

# Install Redis if not already installed
if ! command -v redis-server &> /dev/null; then
    print_status "Installing Redis..."
    sudo apt install -y redis-server
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
else
    print_status "Redis already installed"
fi

# Install Docker if not already installed
if ! command -v docker &> /dev/null; then
    print_status "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
else
    print_status "Docker already installed: $(docker --version)"
fi

# Install Docker Compose if not already installed
if ! command -v docker-compose &> /dev/null; then
    print_status "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    print_status "Docker Compose already installed: $(docker-compose --version)"
fi

# Install Ollama if not already installed
if ! command -v ollama &> /dev/null; then
    print_status "Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
else
    print_status "Ollama already installed"
fi

# Create Python virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Node.js dependencies
print_status "Installing Node.js dependencies..."
cd langchain-service
npm install
cd ..

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p data

# Set up environment variables
if [ ! -f .env ]; then
    print_status "Creating .env file..."
    cp .env .env.example
    print_warning "Please edit .env file with your specific configuration"
else
    print_status ".env file already exists"
fi

# Test Redis connection
print_status "Testing Redis connection..."
if redis-cli ping > /dev/null 2>&1; then
    print_status "Redis is running and accessible"
else
    print_error "Redis is not accessible. Please check Redis installation."
fi

# Pull Ollama model (this may take some time)
print_status "Pulling Ollama model (this may take several minutes)..."
ollama pull llama3.1 || print_warning "Failed to pull model. You can do this manually later with: ollama pull llama3.1"

print_status "Setup completed! 🎉"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Run the development environment:"
echo "   - Start Redis: sudo systemctl start redis-server"
echo "   - Start Ollama: ollama serve"
echo "   - Start LangChain service: cd langchain-service && npm start"
echo "   - Start Celery worker: source venv/bin/activate && celery -A python-app.celery_app worker --loglevel=info"
echo "   - Start FastAPI: source venv/bin/activate && cd python-app && uvicorn main:app --reload"
echo ""
echo "Or run with Docker:"
echo "   docker-compose up --build"
echo ""
echo "API will be available at:"
echo "   - FastAPI: http://localhost:8000"
echo "   - LangChain service: http://localhost:3000"
echo "   - Flower (monitoring): http://localhost:5555"
echo "   - Open WebUI: http://localhost:3001"
