#!/bin/bash

# Simple container startup for Llama 4 Scout AI Agent
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    print_warning "Ollama is not running. Starting Ollama..."
    if command -v ollama > /dev/null 2>&1; then
        ollama serve &
        sleep 5
    else
        echo "❌ Ollama not found. Please install Ollama first:"
        echo "curl -fsSL https://ollama.com/install.sh | sh"
        exit 1
    fi
fi

# Check for Llama 4 Scout model
MODEL_NAME="llama4:scout"
if ! ollama list | grep -q "llama4:scout"; then
    print_warning "Llama 4 Scout not found. Checking alternatives..."
    
    if ollama list | grep -q "ingu627/llama4-scout-q4"; then
        MODEL_NAME="ingu627/llama4-scout-q4"
        print_status "Using quantized Llama 4 Scout"
    elif ollama list | grep -q "llama3.1:8b-instruct-q4_0"; then
        MODEL_NAME="llama3.1:8b-instruct-q4_0"
        print_warning "Falling back to Llama 3.1"
    else
        print_warning "No suitable model found. Downloading Llama 3.1 fallback..."
        ollama pull llama3.1:8b-instruct-q4_0
        MODEL_NAME="llama3.1:8b-instruct-q4_0"
    fi
fi

print_status "Using model: $MODEL_NAME"

print_status "Building AI Agent image..."
docker build -t ai-agent-llama4 .

print_status "Starting AI Agent container with Llama 4 support..."
docker run -d \
  --name ai-agent-llama4-container \
  --network host \
  -e OLLAMA_BASE_URL=http://localhost:11434 \
  -e MODEL_NAME="$MODEL_NAME" \
  -e SERVER_HOST=0.0.0.0 \
  -e SERVER_PORT=8000 \
  -v "$(pwd)/logs:/app/logs" \
  --restart unless-stopped \
  ai-agent-llama4

print_status "Starting Open WebUI container..."
docker run -d \
  --name open-webui-container \
  --network host \
  -e OPENAI_API_BASE_URL=http://localhost:8000/v1 \
  -e OPENAI_API_KEY=sk-aiagent-key \
  -e DEFAULT_MODELS=ai-agent-no-framework \
  -e WEBUI_NAME="AI Agent No-Framework Interface" \
  -e ENABLE_SIGNUP=false \
  -v open-webui-data:/app/backend/data \
  --restart unless-stopped \
  ghcr.io/open-webui/open-webui:main

echo ""
print_status "Services started!"
echo -e "${BLUE}URLs:${NC}"
echo "  AI Agent API: http://localhost:8000"
echo "  Open WebUI:   http://localhost:3000"
echo "  Ollama:       http://localhost:11434 (host service)"
echo ""
echo "Wait 30-60 seconds for services to start completely."
echo ""
echo "Test the API:"
echo "  curl http://localhost:8000/health"
echo ""
echo "Stop containers:"
echo "  docker stop ai-agent-container open-webui-container"
echo "  docker rm ai-agent-container open-webui-container"
