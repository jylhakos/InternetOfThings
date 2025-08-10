#!/bin/bash

# Quick Start Script for Feature Learning Demo
# This script activates the virtual environment and runs the demo

echo " Feature Learning"
echo "================================"

# Change to project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Working directory: $(pwd)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "🔧 Please run setup_environment.sh first"
    exit 1
fi

echo "Virtual environment found"

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if activation was successful
if [ "$VIRTUAL_ENV" = "" ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

echo "Virtual environment activated: $VIRTUAL_ENV"

# Check Python and key packages
echo "Checking Python environment..."
python --version
echo "📦 Checking key packages..."

# Quick package check
python -c "
import sys
packages_to_check = ['torch', 'numpy', 'matplotlib', 'sklearn']
missing = []

for package in packages_to_check:
    try:
        __import__(package)
        print(f' {package}: Available')
    except ImportError:
        print(f'❌ {package}: Missing')
        missing.append(package)

if missing:
    print(f'\\n⚠️  Missing packages: {missing}')
    print('🔧 Installing missing packages...')
    sys.exit(1)
else:
    print('\\nThe packages available!')
    sys.exit(0)
"

# Install missing packages if needed
if [ $? -ne 0 ]; then
    echo "📦 Installing missing packages..."
    pip install torch torchvision numpy matplotlib scikit-learn
    if [ $? -ne 0 ]; then
        echo "❌ Package installation failed"
        exit 1
    fi
fi

# Run the demo
echo ""
echo "Running Feature Learning..."
echo "===================================="
python demo_feature_learning.py

# Check if demo was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "Demo completed successfully!"
    echo "📁 Check the 'results/' directory for visualizations"
    echo "See README.md for more information"
else
    echo ""
    echo "❌ Demo failed. Check the error messages above."
fi

echo ""
echo " To manually activate the environment, run:"
echo "   source venv/bin/activate"
