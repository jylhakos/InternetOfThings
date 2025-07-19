#!/bin/bash

# LangChain.js AI Agent Complete Setup Script
# This script sets up the entire LangChain.js AI Agent system

set -e  # Exit on any error

echo "🚀 LangChain.js AI Agent Setup"
echo "============================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if running on supported OS
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    print_warning "This script is optimized for Linux. Some steps may need manual adjustment on other OS."
fi

# Step 1: Check Node.js
print_info "Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed!"
    echo "Please install Node.js 18+ from: https://nodejs.org/"
    echo "Or use a package manager:"
    echo "  curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -"
    echo "  sudo apt-get install -y nodejs"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2)
REQUIRED_VERSION="18.0.0"

# Simple version comparison
if [[ "$(printf '%s\n' "$REQUIRED_VERSION" "$NODE_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]]; then
    print_error "Node.js version $NODE_VERSION is too old. Please upgrade to Node.js 18+."
    exit 1
fi

print_status "Node.js version: $(node -v)"
print_status "NPM version: $(npm -v)"

# Step 2: Install Node.js dependencies
print_info "Installing Node.js dependencies..."
if npm install; then
    print_status "Node.js dependencies installed successfully!"
else
    print_error "Failed to install Node.js dependencies"
    exit 1
fi

# Step 3: Check/Install Ollama
print_info "Checking Ollama installation..."
if ! command -v ollama &> /dev/null; then
    print_warning "Ollama is not installed. Installing now..."
    if curl -fsSL https://ollama.com/install.sh | sh; then
        print_status "Ollama installed successfully!"
    else
        print_error "Failed to install Ollama"
        exit 1
    fi
else
    print_status "Ollama is already installed: $(ollama --version)"
fi

# Step 4: Check if Ollama is running
print_info "Checking if Ollama service is running..."
if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    print_status "Ollama service is running"
else
    print_warning "Ollama service is not running. Starting it..."
    
    # Try to start Ollama in background
    if command -v systemctl &> /dev/null; then
        # Systemd system
        if sudo systemctl start ollama 2>/dev/null; then
            print_status "Ollama service started via systemd"
        else
            print_info "Starting Ollama manually..."
            nohup ollama serve >/dev/null 2>&1 &
            sleep 3
        fi
    else
        # Non-systemd system
        print_info "Starting Ollama manually..."
        nohup ollama serve >/dev/null 2>&1 &
        sleep 3
    fi
    
    # Verify it's running
    for i in {1..10}; do
        if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
            print_status "Ollama service is now running"
            break
        fi
        if [ $i -eq 10 ]; then
            print_error "Failed to start Ollama service"
            print_info "Please start Ollama manually: ollama serve"
            exit 1
        fi
        sleep 2
    done
fi

# Step 5: Check/Pull required model
MODEL_NAME="llama3.1:8b-instruct-q4_0"
print_info "Checking for required model: $MODEL_NAME"

if ollama list | grep -q "$MODEL_NAME"; then
    print_status "Model $MODEL_NAME is already available"
else
    print_warning "Model $MODEL_NAME not found. Downloading..."
    print_info "This may take several minutes depending on your internet connection..."
    
    if ollama pull "$MODEL_NAME"; then
        print_status "Model $MODEL_NAME downloaded successfully!"
    else
        print_error "Failed to download model $MODEL_NAME"
        print_info "You can try downloading it manually later: ollama pull $MODEL_NAME"
        exit 1
    fi
fi

# Step 6: Create/verify environment file
print_info "Setting up environment configuration..."
if [ ! -f .env ]; then
    cat > .env << EOF
# LangChain.js AI Agent Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b-instruct-q4_0
AGENT_PORT=8000
OPEN_METEO_GEOCODING_URL=https://geocoding-api.open-meteo.com/v1/search
OPEN_METEO_WEATHER_URL=https://api.open-meteo.com/v1/forecast
EOF
    print_status "Environment file (.env) created"
else
    print_status "Environment file (.env) already exists"
fi

# Step 7: Test the installation
print_info "Testing the installation..."

# Start the agent in background for testing
print_info "Starting LangChain.js AI Agent for testing..."
node src/agents.js &
AGENT_PID=$!

# Give it time to start
sleep 5

# Test health endpoint
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    print_status "AI Agent is responding correctly!"
    
    # Get health info
    HEALTH_INFO=$(curl -s http://localhost:8000/health)
    echo "$HEALTH_INFO" | grep -q '"status":"healthy"' && print_status "Health check passed"
    
else
    print_error "AI Agent is not responding on http://localhost:8000"
    kill $AGENT_PID 2>/dev/null || true
    exit 1
fi

# Stop the test instance
kill $AGENT_PID 2>/dev/null || true
sleep 2

# Step 8: Installation complete
echo ""
echo "🎉 Setup completed successfully!"
echo "==============================="
echo ""
print_status "All components are installed and configured:"
echo "  ✅ Node.js $(node -v) with NPM $(npm -v)"
echo "  ✅ LangChain.js dependencies"
echo "  ✅ Ollama service"
echo "  ✅ Llama-3.1 model (quantized)"
echo "  ✅ Environment configuration"
echo ""
echo "🚀 Quick Start Commands:"
echo "  npm start          # Start the LangChain.js AI Agent"
echo "  npm test           # Run tests"
echo "  npm run demo       # Run interactive demo"
echo "  npm run health     # Check agent health"
echo ""
echo "🌐 Endpoints (when running):"
echo "  http://localhost:8000/health               # Health check"
echo "  http://localhost:8000/v1/chat/completions  # OpenAI-compatible chat"
echo "  http://localhost:8000/agent/query          # Direct agent queries"
echo ""
echo "💡 Usage Examples:"
echo "  # Start the agent"
echo "  npm start"
echo ""
echo "  # In another terminal, test with curl:"
echo "  curl -X POST http://localhost:8000/agent/query \\"
echo "       -H 'Content-Type: application/json' \\"
echo "       -d '{\"query\": \"Hello! What can you do?\"}'"
echo ""
echo "🔗 Integration with Open WebUI:"
echo "  Set OpenAI API Base URL to: http://localhost:8000/v1"
echo "  No API key required"
echo ""

print_status "Setup completed! You can now start using the LangChain.js AI Agent."
