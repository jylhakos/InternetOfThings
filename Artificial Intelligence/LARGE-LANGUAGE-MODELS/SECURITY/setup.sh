#!/bin/bash
#
# Setup script for Prompt Injection Security Demo
# This script sets up the virtual environment and installs dependencies
#

echo "========================================="
echo "  Prompt Injection Security Demo Setup  "
echo "========================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "Python version:"
python3 --version
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Check if virtual environment was created successfully
if [ ! -d "venv" ]; then
    echo "Error: Failed to create virtual environment"
    exit 1
fi

echo "Virtual environment created successfully!"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo ""
echo "========================================="
echo "  Setup Complete!                       "
echo "========================================="
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the demo:"
echo "  python src/prompt_injection_demo.py"
echo ""
echo "To run tests:"
echo "  pytest tests/ -v"
echo ""
