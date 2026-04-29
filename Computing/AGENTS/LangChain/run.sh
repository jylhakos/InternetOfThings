#!/bin/bash

# LangChain Quick Start Script
# This script sets up and runs the LangChain AI agent demo

echo "======================================================================"
echo "LangChain AI Agent - Quick Start"
echo "======================================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3.12 -m venv venv"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo ""
    echo "To run the agent, you need to configure your API key:"
    echo "1. Copy .env.example to .env"
    echo "2. Add your OpenAI API key to .env"
    echo ""
    read -p "Do you want to create .env from .env.example now? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env
        echo "✅ Created .env file. Please edit it and add your API key."
        echo "   Then run this script again."
        exit 0
    else
        echo "Exiting. Please create .env file manually."
        exit 1
    fi
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Check if packages are installed
echo "🔍 Checking dependencies..."
if ! python -c "import langchain" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -q -r requirements.txt
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi

echo ""
echo "======================================================================"
echo "Choose an option:"
echo "======================================================================"
echo "1. Run the standalone agent demo (agent.py)"
echo "2. Start the FastAPI server (server.py)"
echo "3. Exit"
echo ""
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Running agent demo..."
        echo "======================================================================"
        python agent.py
        ;;
    2)
        echo ""
        echo "🚀 Starting FastAPI server..."
        echo "======================================================================"
        python server.py
        ;;
    3)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Exiting."
        exit 1
        ;;
esac
