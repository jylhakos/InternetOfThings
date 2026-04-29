#!/bin/bash
# Quick Start Script for RAG Project

echo "========================================="
echo "RAG Project - Quick Start"
echo "========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
echo "This may take a few minutes..."
pip install -r requirements.txt

echo ""
echo "========================================="
echo "Installation Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and add your API keys:"
echo "   cp .env.example .env"
echo ""
echo "2. Edit .env and add your keys:"
echo "   - OPENAI_API_KEY=your_key_here"
echo "   - OPENWEATHER_API_KEY=your_key_here"
echo ""
echo "3. Run tests:"
echo "   pytest tests/ -v"
echo ""
echo "4. Run the example agent:"
echo "   python src/agent.py"
echo ""
echo "========================================="
