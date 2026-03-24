#!/bin/bash

# Docker-based local setup script
# This script sets up the LLM Chat Service using Docker Compose

set -e

echo "🐳 Setting up LLM Chat Service with Docker"

# Check if required tools are installed
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed. Aborting." >&2; exit 1; }

echo "✅ Docker and Docker Compose detected"

# Check if Docker daemon is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker daemon is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker daemon is running"

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up -d --build

echo "⏳ Waiting for services to be ready..."

# Wait for Ollama to be ready
echo "Waiting for Ollama service..."
for i in {1..60}; do
    if curl -s http://localhost:11434/api/version >/dev/null 2>&1; then
        echo "✅ Ollama is ready"
        break
    fi
    sleep 5
    if [ $i -eq 60 ]; then
        echo "❌ Ollama failed to start after 5 minutes"
        echo "Check logs with: docker-compose logs ollama"
        exit 1
    fi
done

# Pull Llama-3 model
echo "📥 Pulling Llama-3 model (this may take a while)..."
docker-compose exec ollama ollama pull llama3

# Wait for Spring Boot application
echo "Waiting for Spring Boot application..."
for i in {1..60}; do
    if curl -s http://localhost:8080/actuator/health >/dev/null 2>&1; then
        echo "✅ Spring Boot application is ready"
        break
    fi
    sleep 5
    if [ $i -eq 60 ]; then
        echo "❌ Spring Boot application failed to start after 5 minutes"
        echo "Check logs with: docker-compose logs llm-chat-service"
        exit 1
    fi
done

echo "✅ All services are running!"
echo ""
echo "🎯 Access your application:"
echo "Web Interface: http://localhost:8080"
echo "API Endpoint: http://localhost:8080/api/v1/chat"
echo "Health Check: http://localhost:8080/actuator/health"
echo "Via Nginx: http://localhost (if nginx service is enabled)"
echo ""
echo "📊 Monitoring:"
echo "View logs: docker-compose logs -f"
echo "View Ollama logs: docker-compose logs -f ollama"
echo "View app logs: docker-compose logs -f llm-chat-service"
echo ""
echo "🛑 To stop services:"
echo "docker-compose down"
echo ""
echo "🗑️ To clean up everything:"
echo "docker-compose down -v --rmi all"
