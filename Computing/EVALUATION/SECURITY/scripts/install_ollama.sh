#!/bin/bash
# Ollama Installation and Setup Script

set -e

echo "=========================================="
echo "Ollama Installation Script"
echo "=========================================="

# Check if Ollama is already installed
if command -v ollama &> /dev/null; then
    echo "Ollama is already installed."
    ollama --version
    read -p "Do you want to reinstall? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

# Install Ollama
echo ""
echo "Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
echo ""
echo "Verifying Ollama installation..."
ollama --version

# Start Ollama service
echo ""
echo "Starting Ollama service..."
ollama serve &

sleep 5

# Pull recommended models
echo ""
echo "Pulling recommended models..."
echo "This may take several minutes depending on your internet connection."

echo ""
echo "Pulling llama3.2 (recommended for security testing)..."
ollama pull llama3.2

echo ""
echo "Pulling mistral (alternative model)..."
ollama pull mistral

# List installed models
echo ""
echo "Installed models:"
ollama list

echo ""
echo "=========================================="
echo "Ollama installation complete!"
echo "=========================================="
echo ""
echo "To start Ollama server, run:"
echo "  ollama serve"
echo ""
echo "To test the installation, run:"
echo "  ollama run llama3.2"
echo ""
echo "API endpoint: http://localhost:11434"
echo ""
