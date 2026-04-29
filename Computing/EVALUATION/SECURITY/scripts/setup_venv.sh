#!/bin/bash
# Virtual Environment Setup Script for LLM Security Evaluation

set -e

echo "=========================================="
echo "LLM Security Evaluation - Environment Setup"
echo "=========================================="

# Check Python version
echo "Checking Python version..."
python3 --version

if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Verify installation
echo ""
echo "Verifying installation..."
pip list

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To deactivate, run:"
echo "  deactivate"
echo ""
