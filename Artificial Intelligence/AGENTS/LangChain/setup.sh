#!/bin/bash

# AI Agent Setup Script
# This script sets up the Python environment and installs dependencies

set -e

echo "🚀 Setting up AI Agent - No Framework"
echo "======================================"

# Check if Python 3.12 is available
if command -v python3.12 &> /dev/null; then
    PYTHON_CMD=python3.12
elif command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "❌ Python not found. Please install Python 3.12 or compatible version."
    exit 1
fi

echo "✅ Using Python: $($PYTHON_CMD --version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
$PYTHON_CMD -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    echo "📄 Creating .env file..."
    cp .env.example .env
fi

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Install and setup Ollama:"
echo "   curl -fsSL https://ollama.com/install.sh | sh"
echo ""
echo "2. Start Ollama service:"
echo "   ollama serve"
echo ""
echo "3. Pull the Llama model (in another terminal):"
echo "   ollama pull llama3.1:8b-instruct-q4_0"
echo ""
echo "4. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "5. Start the AI Agent server:"
echo "   python src/index.py"
echo ""
echo "6. Test the API:"
echo "   curl http://localhost:8000/health"
echo ""
echo "📚 Documentation will be available at: http://localhost:8000/docs"
echo ""
