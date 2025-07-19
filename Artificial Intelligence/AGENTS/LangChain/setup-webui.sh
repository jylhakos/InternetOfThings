#!/bin/bash

# Open WebUI Setup Script for AI Agent Integration
# This script sets up Open WebUI in Docker to work with the no-framework AI agent

set -e

echo "🌐 Setting up Open WebUI for AI Agent Integration"
echo "================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/engine/install/debian/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if AI Agent is running
echo "🔍 Checking if AI Agent is running..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ AI Agent is running on port 8000"
else
    echo "⚠️  AI Agent is not running. Please start it first:"
    echo "   source venv/bin/activate"
    echo "   python src/index.py"
    echo ""
    echo "Continuing with setup anyway..."
fi

# Check if Ollama is running
echo "🦙 Checking if Ollama is running..."
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama is running on port 11434"
else
    echo "⚠️  Ollama is not running. Please start it first:"
    echo "   ollama serve"
    echo ""
fi

# Create .env file if it doesn't exist
if [ ! -f .env.docker ]; then
    echo "📄 Creating environment configuration..."
    cp .env.docker.example .env.docker 2>/dev/null || true
fi

# Generate a secure secret key
if grep -q "change-this-secret-key" .env.docker 2>/dev/null; then
    SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || echo "$(date +%s | sha256sum | head -c 64)")
    sed -i "s/change-this-secret-key-in-production-environment/$SECRET_KEY/" .env.docker
    echo "🔑 Generated secure secret key"
fi

# Create Docker network if it doesn't exist
echo "🔗 Creating Docker network..."
docker network create ai-agent-network 2>/dev/null || true

# Pull the Open WebUI image
echo "📥 Pulling Open WebUI Docker image..."
docker pull ghcr.io/open-webui/open-webui:main

# Start Open WebUI
echo "🚀 Starting Open WebUI..."
docker-compose --env-file .env.docker up -d

# Wait for the service to be ready
echo "⏳ Waiting for Open WebUI to start..."
sleep 10

# Check if the service is running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Open WebUI is running successfully!"
    echo ""
    echo "🌟 Setup completed!"
    echo "==================="
    echo ""
    echo "📱 Access Open WebUI at: http://localhost:3000"
    echo "🔧 AI Agent API at: http://localhost:8000"
    echo "🦙 Ollama API at: http://localhost:11434"
    echo ""
    echo "📋 Next steps:"
    echo "1. Open http://localhost:3000 in your browser"
    echo "2. Create an admin account (first user becomes admin)"
    echo "3. Start chatting with your AI agent!"
    echo ""
    echo "🧪 Test queries to try:"
    echo "- Hello, how are you?"
    echo "- What's the temperature in London?"
    echo "- Tell me about artificial intelligence"
    echo ""
    echo "🔍 Logs: docker-compose logs -f"
    echo "🛑 Stop: docker-compose down"
else
    echo "❌ Failed to start Open WebUI. Check logs:"
    docker-compose logs
    exit 1
fi
