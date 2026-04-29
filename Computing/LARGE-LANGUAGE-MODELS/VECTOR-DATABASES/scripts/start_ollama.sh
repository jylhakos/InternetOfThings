#!/bin/bash
# Start Ollama inference server

echo "Ollama Inference Server Startup"
echo "================================"
echo ""

# Check if Ollama is installed
if command -v ollama &> /dev/null; then
    echo "Ollama is installed"
    
    # Start Ollama server
    echo "Starting Ollama server..."
    ollama serve &
    
    # Wait for server to start
    sleep 3
    
    # Check if model is available
    echo ""
    echo "Checking available models..."
    ollama list
    
    echo ""
    read -p "Enter model name to pull (or press Enter to skip): " model_name
    
    if [ ! -z "$model_name" ]; then
        echo "Pulling model: $model_name"
        ollama pull "$model_name"
        echo "Model ready!"
    fi
    
    echo ""
    echo "Ollama server is running on http://localhost:11434"
    echo "You can now start the FastAPI application"
    
else
    echo "Ollama is not installed"
    echo ""
    echo "Installation options:"
    echo ""
    echo "1) Install via script (Linux):"
    echo "   curl -fsSL https://ollama.com/install.sh | sh"
    echo ""
    echo "2) Use Docker:"
    echo "   docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama"
    echo ""
    echo "3) Download from https://ollama.com"
    echo ""
    
    read -p "Install Ollama now using script? (y/n): " install
    
    if [ "$install" = "y" ] || [ "$install" = "Y" ]; then
        echo "Installing Ollama..."
        curl -fsSL https://ollama.com/install.sh | sh
        
        echo ""
        echo "Installation complete! Run this script again to start the server."
    fi
fi
