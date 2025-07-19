#!/bin/bash

# Simple container startup using existing Ollama service
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_status "Building AI Agent image..."
docker build -t ai-agent-no-framework .

print_status "Starting AI Agent container (using host Ollama)..."
docker run -d \
  --name ai-agent-container \
  --network host \
  -e OLLAMA_BASE_URL=http://localhost:11434 \
  -e MODEL_NAME=llama3.1:8b-instruct-q4_0 \
  -e SERVER_HOST=0.0.0.0 \
  -e SERVER_PORT=8000 \
  -v "$(pwd)/logs:/app/logs" \
  --restart unless-stopped \
  ai-agent-no-framework

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
