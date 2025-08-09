#!/bin/bash

# Setup script for RNN Language Model project
# This script sets up the Python environment and installs dependencies

set -e  # Exit on any error

echo "======================================"
echo "RNN Language Model Project Setup"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3 is installed
print_status "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Found $PYTHON_VERSION"
else
    print_error "Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if pip is installed
if command -v pip3 &> /dev/null; then
    print_success "pip3 is available"
else
    print_error "pip3 is not installed. Please install pip3 first."
    exit 1
fi

# Create virtual environment
print_status "Setting up virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install PyTorch (CPU version by default)
print_status "Installing PyTorch..."
echo "Choose PyTorch installation:"
echo "1) CPU only (recommended for most users)"
echo "2) GPU (CUDA 11.8)"
echo "3) GPU (CUDA 12.1)"
echo "4) Skip PyTorch installation"

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        print_status "Installing PyTorch CPU version..."
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
        ;;
    2)
        print_status "Installing PyTorch with CUDA 11.8..."
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
        ;;
    3)
        print_status "Installing PyTorch with CUDA 12.1..."
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
        ;;
    4)
        print_warning "Skipping PyTorch installation"
        ;;
    *)
        print_warning "Invalid choice. Installing CPU version..."
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
        ;;
esac

# Install other requirements
print_status "Installing other dependencies..."
pip install -r requirements.txt

# Create necessary directories
print_status "Creating project directories..."
mkdir -p data
mkdir -p checkpoints
mkdir -p logs

# Test installation
print_status "Testing installation..."
python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')"

if [ $? -eq 0 ]; then
    print_success "PyTorch installation test passed"
else
    print_error "PyTorch installation test failed"
fi

# Test other imports
python -c "import datasets, transformers, flask, numpy, pandas, matplotlib; print('All dependencies imported successfully')"

if [ $? -eq 0 ]; then
    print_success "All dependencies test passed"
else
    print_error "Some dependencies test failed"
fi

print_success "Setup completed!"

echo ""
echo "======================================"
echo "Next Steps:"
echo "======================================"
echo ""
echo "1. Activate the virtual environment:"
echo "   source .venv/bin/activate"
echo ""
echo "2. Download the dataset:"
echo "   python scripts/download_data.py"
echo ""
echo "3. Run the demo:"
echo "   python scripts/demo.py"
echo ""
echo "4. Train a model:"
echo "   python scripts/train_model.py --epochs 5"
echo ""
echo "5. Start the API server:"
echo "   python api/app.py --checkpoint checkpoints/best_model.pth"
echo ""
echo "6. Test with cURL:"
echo "   ./tests/curl_tests.sh"
echo ""
echo "7. Explore with Jupyter:"
echo "   jupyter notebook notebooks/exploration.ipynb"
echo ""
echo "For detailed instructions, see README.md"
echo ""
echo "Happy modeling! 🚀"
