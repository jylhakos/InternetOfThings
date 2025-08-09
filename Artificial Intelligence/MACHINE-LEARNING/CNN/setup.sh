#!/bin/bash

# MNIST CNN PyTorch Setup Script
# This script helps set up the environment for the MNIST CNN project

echo "🚀 MNIST CNN PyTorch Setup Script"
echo "================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python3 found: $(python3 --version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv mnist_env

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source mnist_env/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing PyTorch and dependencies..."
if pip install -r requirements.txt; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies. Trying alternative installation..."
    
    # Try installing PyTorch separately
    echo "📥 Installing PyTorch..."
    if command -v nvidia-smi &> /dev/null; then
        echo "🎮 NVIDIA GPU detected. Installing CUDA version..."
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    else
        echo "💻 Installing CPU version..."
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    fi
    
    # Install other dependencies
    pip install matplotlib numpy Pillow
fi

# Verify installation
echo "🔍 Verifying installation..."
python3 -c "import torch; print('✅ PyTorch version:', torch.__version__)"
python3 -c "import torch; print('🎮 CUDA available:', torch.cuda.is_available())"
python3 -c "import torchvision; print('✅ TorchVision version:', torchvision.__version__)"
python3 -c "import matplotlib; print('✅ Matplotlib version:', matplotlib.__version__)"
python3 -c "import numpy; print('✅ NumPy version:', numpy.__version__)"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To activate the environment in future sessions, run:"
echo "  source mnist_env/bin/activate"
echo ""
echo "To start training, run:"
echo "  python3 mnist_cnn.py"
echo ""
echo "To run inference demo, run:"
echo "  python3 inference_demo.py"
