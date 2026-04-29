#!/bin/bash

# European Bike Rental Agent Setup Script

echo "🚲 Setting up European Bike Rental Agent..."

# Check if Python 3.9+ is available
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
required_version="3.9"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $python_version detected. Please install Python 3.9 or higher."
    exit 1
fi

echo "✅ Python $python_version detected"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📋 Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Python dependencies installed successfully"

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "⚠️ Ollama is not installed. Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    echo "✅ Ollama installed"
else
    echo "✅ Ollama is already installed"
fi

# Check if Ollama service is running
if ! pgrep -f "ollama serve" > /dev/null; then
    echo "🚀 Starting Ollama service..."
    ollama serve &
    sleep 5
    echo "✅ Ollama service started"
else
    echo "✅ Ollama service is already running"
fi

# Pull required model
echo "📥 Pulling Llama-3.1 8B model..."
ollama pull llama3.1:8b

echo "✅ Model downloaded successfully"

# Make the script executable
chmod +x setup.sh

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "To start the application:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run the server: python main.py"
echo "3. Open browser: http://localhost:8000/docs"
echo ""
echo "To test with cURL:"
echo "curl -X POST http://localhost:8000/api/chat -H 'Content-Type: application/json' -d '{\"message\": \"I want to rent a bike in Amsterdam\"}'"
