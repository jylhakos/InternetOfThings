#!/bin/bash

# Ollama FastAPI Server Setup and Run Script

echo "🦙 Ollama FastAPI Server Setup"
echo "================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python3 first."
    exit 1
fi

# Check if Ollama is running
echo "🔍 Checking if Ollama is running..."
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "❌ Ollama is not running on localhost:11434"
    echo "Please start Ollama first:"
    echo "  - Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh"
    echo "  - Start Ollama: ollama serve"
    echo "  - Pull a model: ollama pull llama3"
    exit 1
else
    echo "✅ Ollama is running"
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"

# Check available models
echo "🔍 Checking available Ollama models..."
MODELS=$(curl -s http://localhost:11434/api/tags | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    models = [model['name'] for model in data.get('models', [])]
    if models:
        print('Available models:', ', '.join(models))
    else:
        print('No models found. Please pull a model first (e.g., ollama pull llama3)')
except:
    print('Could not parse models response')
")
echo "$MODELS"

echo ""
echo "🚀 Starting FastAPI server..."
echo "Server will be available at: http://localhost:8000"
echo "API documentation: http://localhost:8000/docs"
echo "Test client: http://localhost:8000 (serve client.html)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the FastAPI server
python3 main.py
