#!/bin/bash

# Simple run script for local development
echo "🚀 Starting LLM Chat Service..."

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/version >/dev/null 2>&1; then
    echo "⚠️  Ollama is not running. Starting Ollama..."
    ollama serve &
    echo "⏳ Waiting for Ollama to start..."
    sleep 10
    
    # Check if Llama-3 model is available
    if ! ollama list | grep -q "llama3"; then
        echo "📥 Pulling Llama-3 model..."
        ollama pull llama3
    fi
fi

echo "✅ Ollama is ready"

# Run Spring Boot application
echo "🔄 Starting Spring Boot application..."
mvn spring-boot:run
