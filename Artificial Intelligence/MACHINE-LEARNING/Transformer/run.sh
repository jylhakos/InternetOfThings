#!/bin/bash

# RNN + Transformer Language Model - Setup and Run Script
# This script sets up the environment and runs the demo

set -e  # Exit on error

echo "=========================================="
echo "RNN + Transformer Language Model Setup"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if Python 3 is available
print_header "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_status "Python version: $PYTHON_VERSION"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    print_header "Creating virtual environment..."
    python3 -m venv .venv
    print_status "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_header "Activating virtual environment..."
source .venv/bin/activate
print_status "Virtual environment activated"

# Upgrade pip
print_header "Upgrading pip..."
pip install --upgrade pip

# Install requirements
print_header "Installing Python packages..."
pip install -r requirements.txt
print_status "All packages installed successfully"

# Function to run demo
run_demo() {
    print_header "Running model architecture demo..."
    python demo.py
}

# Function to run quick training
run_training() {
    print_header "Running quick training demo (3 epochs)..."
    python -c "
from train import train_model
import sys

try:
    # Train a small hybrid model for demo
    model, vocab, trainer = train_model(
        model_type='hybrid',
        num_epochs=3,
        batch_size=8,
        seq_length=32
    )
    print('Training completed successfully!')
except Exception as e:
    print(f'Training failed: {e}')
    sys.exit(1)
"
}

# Function to test text generation
test_generation() {
    print_header "Testing text generation..."
    python generate.py --demo
}

# Function to start API server
start_api() {
    print_header "Starting API server..."
    print_status "API will be available at http://localhost:5000"
    print_warning "Press Ctrl+C to stop the server"
    python api.py
}

# Function to test API
test_api() {
    print_header "Testing API endpoints..."
    python test_api.py
}

# Main menu
show_menu() {
    echo ""
    echo "What would you like to do?"
    echo "1) Run architecture demo (recommended first step)"
    echo "2) Run quick training (may take 5-10 minutes)"
    echo "3) Test text generation"
    echo "4) Start API server"
    echo "5) Test API endpoints"
    echo "6) Run everything (full demo)"
    echo "7) Exit"
    echo ""
}

# Get user choice
get_choice() {
    read -p "Enter your choice [1-7]: " choice
    case $choice in
        1)
            run_demo
            ;;
        2)
            run_training
            ;;
        3)
            test_generation
            ;;
        4)
            start_api
            ;;
        5)
            test_api
            ;;
        6)
            print_header "Running complete demo..."
            run_demo
            echo ""
            read -p "Continue with training? (y/N): " continue_choice
            if [[ $continue_choice =~ ^[Yy]$ ]]; then
                run_training
                test_generation
            fi
            ;;
        7)
            print_status "Goodbye!"
            exit 0
            ;;
        *)
            print_warning "Invalid choice. Please try again."
            ;;
    esac
}

# Main execution
print_status "Setup completed successfully!"
print_status "Virtual environment: $(which python)"

# Check if this is the first run
if [ ! -f "vocab.pkl" ] && [ ! -d "checkpoints_hybrid" ]; then
    print_warning "This appears to be your first run."
    print_status "Recommended: Start with option 1 (Architecture Demo)"
fi

# Interactive menu
while true; do
    show_menu
    get_choice
    echo ""
    read -p "Press Enter to continue or Ctrl+C to exit..."
done
