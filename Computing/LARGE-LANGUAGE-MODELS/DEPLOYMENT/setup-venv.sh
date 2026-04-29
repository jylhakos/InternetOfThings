#!/bin/bash

# Setup script for LLM Deployment project
# This script creates and activates a virtual environment

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=================================="
echo "LLM Deployment Environment Setup"
echo "=================================="
echo

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✓ Found $PYTHON_VERSION"
echo

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet
echo "✓ pip upgraded"
echo

# Install common dependencies (optional)
if [ -f "requirements.txt" ]; then
    read -p "Do you want to install common dependencies from requirements.txt? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Installing dependencies..."
        pip install -r requirements.txt
        echo "✓ Dependencies installed"
    else
        echo "Skipping dependency installation"
    fi
    echo
fi

# Display next steps
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo
echo "Virtual environment is activated in this terminal session."
echo
echo "To activate it in a new terminal session, run:"
echo "  source venv/bin/activate"
echo
echo "To deactivate, run:"
echo "  deactivate"
echo
echo "Next steps:"
echo "1. Navigate to a specific project folder (LangChain, LangGraph, Python, etc.)"
echo "2. Follow the instructions in that folder's README.md"
echo "3. Install project-specific dependencies as needed"
echo
echo "To install dependencies for a specific project:"
echo "  cd LangChain && npm install      # For Node.js projects"
echo "  cd Python && pip install -r requirements.txt  # For Python projects"
echo "  cd 'Spring Boot' && mvn clean install        # For Java projects"
echo
