#!/bin/bash

# Fish Weight Prediction MLflow Pipeline Setup Script
# This script sets up the complete development environment for Linux/Debian

set -e

echo "🐟 Setting up Fish Weight Prediction MLflow Pipeline"
echo "=================================================="

# Check if we're on a supported system
if ! command -v apt-get &> /dev/null && ! command -v yum &> /dev/null; then
    echo "❌ This script requires a Debian/Ubuntu (apt-get) or RHEL/CentOS (yum) system"
    exit 1
fi

# Update system packages
echo "📦 Updating system packages..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv git curl wget build-essential make
elif command -v yum &> /dev/null; then
    sudo yum update -y
    sudo yum install -y python3 python3-pip git curl wget gcc gcc-c++ make
fi

# Install Make tool (required for MLflow Pipelines)
echo "🔨 Installing Make tool..."
if ! command -v make &> /dev/null; then
    if command -v apt-get &> /dev/null; then
        sudo apt-get install -y make
    elif command -v yum &> /dev/null; then
        sudo yum install -y make
    fi
fi

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Install additional MLflow components
echo "🔄 Installing MLflow with all components..."
pip install mlflow[pipelines] --upgrade

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p models
mkdir -p plots
mkdir -p evaluation_plots
mkdir -p detailed_evaluation
mkdir -p processed_data
mkdir -p logs

# Download dataset if not present
echo "📊 Checking dataset availability..."
if [ ! -f "Dataset/Fish.csv" ]; then
    echo "⬇️ Dataset not found locally. Please download from:"
    echo "https://huggingface.co/datasets/scikit-learn/Fish"
    echo "or use the provided sample dataset"
else
    echo "✅ Dataset found at Dataset/Fish.csv"
fi

# Install AWS CLI if not present (for cloud deployment)
echo "☁️ Installing AWS CLI..."
if ! command -v aws &> /dev/null; then
    if command -v apt-get &> /dev/null; then
        sudo apt-get install -y awscli
    elif command -v yum &> /dev/null; then
        sudo yum install -y awscli
    else
        # Install via pip
        pip install awscli
    fi
fi

# Verify installations
echo "🔍 Verifying installations..."
python --version
pip --version
mlflow --version
aws --version 2>/dev/null || echo "⚠️ AWS CLI not available"
make --version

# Create environment activation script
echo "📝 Creating environment activation script..."
cat > activate_env.sh << EOF
#!/bin/bash
# Activate the MLflow Fish Weight Prediction environment

echo "🐟 Activating Fish Weight Prediction MLflow Environment"
echo "======================================================"

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export MLFLOW_TRACKING_URI=./mlruns
export PYTHONPATH=\${PYTHONPATH}:.

echo "✅ Environment activated!"
echo "📊 MLflow tracking URI: \$MLFLOW_TRACKING_URI"
echo ""
echo "Available commands:"
echo "  mlflow ui                    # Start MLflow UI"
echo "  python preprocessing.py     # Run data preprocessing"
echo "  python train.py             # Train models"
echo "  python evaluate.py          # Evaluate models"
echo "  python inference.py --samples  # Run sample predictions"
echo "  python serve_api.py          # Start REST API server"
echo "  mlflow run .                 # Run complete MLflow pipeline"
echo ""
echo "To deactivate: deactivate"
EOF

chmod +x activate_env.sh

# Create Makefile for MLflow Pipelines
echo "📝 Creating Makefile for MLflow Pipelines..."
cat > Makefile << EOF
# Makefile for Fish Weight Prediction MLflow Pipeline

.PHONY: help setup preprocess train evaluate serve clean

# Default target
help:
	@echo "Fish Weight Prediction MLflow Pipeline"
	@echo "======================================"
	@echo ""
	@echo "Available targets:"
	@echo "  setup       - Setup environment and dependencies"
	@echo "  preprocess  - Run data preprocessing"
	@echo "  train       - Train machine learning models"
	@echo "  evaluate    - Evaluate trained models"
	@echo "  serve       - Start REST API server"
	@echo "  pipeline    - Run complete pipeline (preprocess + train + evaluate)"
	@echo "  clean       - Clean generated files"
	@echo "  ui          - Start MLflow UI"

setup:
	@echo "Setting up environment..."
	bash setup.sh

preprocess:
	@echo "Running data preprocessing..."
	python preprocessing.py

train:
	@echo "Training models..."
	python train.py

evaluate:
	@echo "Evaluating models..."
	python evaluate.py

serve:
	@echo "Starting REST API server..."
	python serve_api.py

pipeline: preprocess train evaluate
	@echo "Complete pipeline executed successfully!"

ui:
	@echo "Starting MLflow UI..."
	mlflow ui --host 0.0.0.0 --port 5000

clean:
	@echo "Cleaning generated files..."
	rm -rf plots evaluation_plots detailed_evaluation processed_data models
	rm -rf mlruns
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

# MLflow pipeline commands
mlflow-run:
	mlflow run . --experiment-name fish_weight_prediction

mlflow-serve:
	mlflow models serve -m models:/fish_weight_predictor/latest -p 8001
EOF

# Initialize MLflow
echo "🎯 Initializing MLflow..."
export MLFLOW_TRACKING_URI=./mlruns
mlflow experiments create --experiment-name fish_weight_prediction 2>/dev/null || true

# Create a test script
echo "📝 Creating test script..."
cat > test_setup.py << EOF
#!/usr/bin/env python3
"""Test script to verify the setup is working correctly"""

import sys
import importlib

def test_imports():
    """Test that all required packages can be imported"""
    packages = [
        'mlflow', 'sklearn', 'pandas', 'numpy', 
        'matplotlib', 'seaborn', 'fastapi', 'uvicorn',
        'plotly', 'scipy', 'click'
    ]
    
    print("Testing package imports...")
    for package in packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            return False
    return True

def test_data_access():
    """Test that the dataset can be accessed"""
    import os
    if os.path.exists('Dataset/Fish.csv'):
        print("✅ Dataset found")
        return True
    else:
        print("❌ Dataset not found at Dataset/Fish.csv")
        return False

if __name__ == "__main__":
    print("🧪 Testing Fish Weight Prediction MLflow Setup")
    print("=" * 50)
    
    import_success = test_imports()
    data_success = test_data_access()
    
    if import_success and data_success:
        print("\n🎉 Setup test completed successfully!")
        print("You can now run the MLflow pipeline:")
        print("  source activate_env.sh")
        print("  make pipeline")
    else:
        print("\n❌ Setup test failed. Please check the errors above.")
        sys.exit(1)
EOF

chmod +x test_setup.py

echo ""
echo "🎉 Setup completed successfully!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Activate the environment: source activate_env.sh"
echo "2. Test the setup: python test_setup.py"
echo "3. Run the pipeline: make pipeline"
echo "4. Start MLflow UI: make ui"
echo "5. Start API server: make serve"
echo ""
echo "For more information, see the README.md file"
