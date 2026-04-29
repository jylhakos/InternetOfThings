#!/bin/bash

# Fish Weight Prediction MLflow Pipeline Setup Script (Conda Version)
# This script sets up the complete development environment using Conda

set -e

echo "🐟 Setting up Fish Weight Prediction MLflow Pipeline with Conda"
echo "=============================================================="

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "❌ Conda not found. Installing Miniconda..."
    
    # Detect architecture
    if [[ $(uname -m) == "x86_64" ]]; then
        MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
    elif [[ $(uname -m) == "aarch64" ]]; then
        MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh"
    else
        echo "❌ Unsupported architecture: $(uname -m)"
        exit 1
    fi
    
    # Download and install Miniconda
    wget -O miniconda.sh "$MINICONDA_URL"
    bash miniconda.sh -b -p $HOME/miniconda3
    rm miniconda.sh
    
    # Initialize conda
    $HOME/miniconda3/bin/conda init bash
    source ~/.bashrc
    
    echo "✅ Miniconda installed successfully"
else
    echo "✅ Conda found: $(conda --version)"
fi

# Update system packages (if needed)
echo "📦 Updating system packages..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y git curl wget build-essential make
elif command -v yum &> /dev/null; then
    sudo yum update -y
    sudo yum install -y git curl wget gcc gcc-c++ make
fi

# Install Make tool (required for MLflow Pipelines)
echo "🔨 Ensuring Make tool is available..."
if ! command -v make &> /dev/null; then
    if command -v apt-get &> /dev/null; then
        sudo apt-get install -y make
    elif command -v yum &> /dev/null; then
        sudo yum install -y make
    fi
fi

# Create conda environment from conda.yaml
echo "🐍 Creating conda environment from conda.yaml..."
if conda env list | grep -q "fish_weight_prediction"; then
    echo "⚠️ Environment 'fish_weight_prediction' already exists. Updating..."
    conda env update -f conda.yaml
else
    echo "📦 Creating new environment..."
    conda env create -f conda.yaml
fi

# Activate the environment
echo "✅ Activating conda environment..."
eval "$(conda shell.bash hook)"
conda activate fish_weight_prediction

# Verify MLflow installation
echo "🔍 Verifying MLflow installation..."
python -c "import mlflow; print(f'MLflow version: {mlflow.__version__}')"

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

# Initialize MLflow
echo "🎯 Initializing MLflow..."
export MLFLOW_TRACKING_URI=./mlruns
mlflow experiments create --experiment-name fish_weight_prediction 2>/dev/null || true

# Create conda-specific environment activation script
echo "📝 Creating conda environment activation script..."
cat > activate_conda_env.sh << 'EOF'
#!/bin/bash
# Activate the MLflow Fish Weight Prediction conda environment

echo "🐟 Activating Fish Weight Prediction MLflow Environment (Conda)"
echo "=============================================================="

# Initialize conda for the current shell
eval "$(conda shell.bash hook)"

# Check if environment exists
if ! conda env list | grep -q "fish_weight_prediction"; then
    echo "❌ Conda environment 'fish_weight_prediction' not found."
    echo "Please run: ./setup_conda.sh"
    exit 1
fi

# Activate environment
conda activate fish_weight_prediction

# Set environment variables
export MLFLOW_TRACKING_URI=./mlruns
export PYTHONPATH=${PYTHONPATH}:.

echo "✅ Conda environment activated!"
echo "📊 MLflow tracking URI: $MLFLOW_TRACKING_URI"
echo "🐍 Python: $(which python)"
echo "📦 Conda env: $CONDA_DEFAULT_ENV"
echo ""
echo "🚀 Available commands:"
echo "  make help                    # Show all available commands"
echo "  make pipeline                # Run complete pipeline"
echo "  make ui                      # Start MLflow UI (http://localhost:5000)"
echo "  make serve                   # Start REST API server (http://localhost:8000)"
echo "  python demo_pipeline.py      # Run comprehensive demo"
echo ""
echo "📋 Individual pipeline steps:"
echo "  make preprocess              # Data preprocessing"
echo "  make train                   # Model training"
echo "  make evaluate                # Model evaluation"
echo ""
echo "🧪 Testing and inference:"
echo "  python inference.py --samples           # Sample predictions"
echo "  python test_setup.py                    # Test setup"
echo ""
echo "☁️ Cloud deployment:"
echo "  make aws-deploy              # Deploy to AWS SageMaker"
echo ""
echo "🧹 Cleanup:"
echo "  make clean                   # Clean generated files"
echo "  conda deactivate             # Deactivate environment"
echo ""
echo "📚 Documentation: See README.md for detailed instructions"
EOF

chmod +x activate_conda_env.sh

# Create conda-specific test script
echo "📝 Creating conda test script..."
cat > test_conda_setup.py << 'EOF'
#!/usr/bin/env python3
"""Test script to verify the conda setup is working correctly"""

import sys
import os
import importlib

def test_conda_environment():
    """Test that we're running in the correct conda environment"""
    conda_env = os.environ.get('CONDA_DEFAULT_ENV', 'None')
    print(f"Current conda environment: {conda_env}")
    
    if conda_env != 'fish_weight_prediction':
        print("❌ Not running in the correct conda environment")
        print("Please run: conda activate fish_weight_prediction")
        return False
    
    print("✅ Running in correct conda environment")
    return True

def test_imports():
    """Test that all required packages can be imported"""
    packages = [
        'mlflow', 'sklearn', 'pandas', 'numpy', 
        'matplotlib', 'seaborn', 'fastapi', 'uvicorn',
        'plotly', 'scipy', 'click', 'joblib'
    ]
    
    print("\nTesting package imports...")
    for package in packages:
        try:
            mod = importlib.import_module(package)
            version = getattr(mod, '__version__', 'unknown')
            print(f"✅ {package} (v{version})")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            return False
    return True

def test_data_access():
    """Test that the dataset can be accessed"""
    if os.path.exists('Dataset/Fish.csv'):
        print("✅ Dataset found")
        return True
    else:
        print("❌ Dataset not found at Dataset/Fish.csv")
        return False

def test_conda_specific_features():
    """Test conda-specific optimizations"""
    try:
        import numpy as np
        # Check if numpy is using optimized BLAS
        config = np.__config__.show()
        print("✅ NumPy configuration verified")
        
        import sklearn
        print(f"✅ Scikit-learn version: {sklearn.__version__}")
        
        return True
    except Exception as e:
        print(f"⚠️ Conda optimization check failed: {e}")
        return True  # Non-critical

if __name__ == "__main__":
    print("🧪 Testing Fish Weight Prediction MLflow Setup (Conda)")
    print("=" * 60)
    
    conda_success = test_conda_environment()
    import_success = test_imports()
    data_success = test_data_access()
    conda_opt_success = test_conda_specific_features()
    
    if conda_success and import_success and data_success:
        print("\n🎉 Conda setup test completed successfully!")
        print("You can now run the MLflow pipeline:")
        print("  source activate_conda_env.sh")
        print("  make pipeline")
    else:
        print("\n❌ Setup test failed. Please check the errors above.")
        sys.exit(1)
EOF

chmod +x test_conda_setup.py

# Update Makefile for conda
echo "📝 Updating Makefile for conda support..."
cat >> Makefile << 'EOF'

# Conda-specific targets
conda-setup:
	@echo "Setting up conda environment..."
	bash setup_conda.sh

conda-activate:
	@echo "Activating conda environment..."
	source activate_conda_env.sh

conda-test:
	@echo "Testing conda setup..."
	python test_conda_setup.py

conda-clean:
	@echo "Cleaning conda environment..."
	conda env remove -n fish_weight_prediction

conda-export:
	@echo "Exporting conda environment..."
	conda env export > environment.yml
EOF

echo ""
echo "🎉 Conda setup completed successfully!"
echo "====================================="
echo ""
echo "🐍 Conda Environment: fish_weight_prediction"
echo "📦 Dependencies: Managed by conda + pip"
echo ""
echo "Next steps:"
echo "1. Activate the environment: source activate_conda_env.sh"
echo "2. Test the setup: python test_conda_setup.py"
echo "3. Run the pipeline: make pipeline"
echo "4. Start MLflow UI: make ui"
echo "5. Start API server: make serve"
echo ""
echo "🔄 To recreate environment: make conda-clean && make conda-setup"
echo "📤 To export environment: make conda-export"
echo ""
echo "For more information, see the README.md file"
