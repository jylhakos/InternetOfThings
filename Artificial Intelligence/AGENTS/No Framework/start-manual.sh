#!/bin/bash

# Manual Docker container startup script for AI Agent No-Framework
# This script runs containers individually without docker-compose

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

# Create network if it doesn't exist
docker network inspect ai-agent-network >/dev/null 2>&1 || docker network create ai-agent-network

print_status "Starting Ollama service..."
docker run -d \
  --name ollama-service \
  --network ai-agent-network \
  -p 11434:11434 \
  -v ollama-data:/root/.ollama \
  --restart unless-stopped \
  ollama/ollama:latest

# Wait for Ollama to start
sleep 10

print_status "Pulling Llama 3.1 model (this may take a while)..."
docker exec ollama-service ollama pull llama3.1:8b-instruct-q4_0 || echo "Model pull failed, continuing..."

print_status "Building AI Agent image..."
docker build -t ai-agent-no-framework .

print_status "Starting AI Agent service..."
docker run -d \
  --name ai-agent-service \
  --network ai-agent-network \
  -p 8000:8000 \
  -e OLLAMA_BASE_URL=http://ollama-service:11434 \
  -e MODEL_NAME=llama3.1:8b-instruct-q4_0 \
  -e SERVER_HOST=0.0.0.0 \
  -e SERVER_PORT=8000 \
  -v "$(pwd)/logs:/app/logs" \
  --restart unless-stopped \
  ai-agent-no-framework

print_status "Starting Open WebUI..."
docker run -d \
  --name open-webui-service \
  --network ai-agent-network \
  -p 3000:8080 \
  -e OPENAI_API_BASE_URL=http://ai-agent-service:8000/v1 \
  -e OPENAI_API_KEY=sk-aiagent-key \
  -e DEFAULT_MODELS=ai-agent-no-framework \
  -e WEBUI_NAME="AI Agent No-Framework Interface" \
  -e ENABLE_SIGNUP=false \
  -v open-webui-data:/app/backend/data \
  --restart unless-stopped \
  ghcr.io/open-webui/open-webui:main

print_status "Services starting up..."
echo ""
echo -e "${BLUE}Service URLs:${NC}"
echo "  AI Agent API: http://localhost:8000"
echo "  Open WebUI:   http://localhost:3000"
echo "  Ollama API:   http://localhost:11434"
echo ""
echo "Wait 30-60 seconds for all services to be fully ready."
echo ""
echo "Check service status with:"
echo "  docker ps"
echo ""
echo "View logs with:"
echo "  docker logs ai-agent-service"
echo "  docker logs open-webui-service"
echo "  docker logs ollama-service"
echo ""
echo "Stop services with:"
echo "  docker stop ai-agent-service open-webui-service ollama-service"
echo "  docker rm ai-agent-service open-webui-service ollama-service"
