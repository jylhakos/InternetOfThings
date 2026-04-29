#!/bin/bash
"""
Environment Setup Script for BERT Fine-tuning with Apache Airflow
Supports both venv and conda environments
"""

set -e  # Exit on any error

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

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    print_warning "This script is designed for Linux. You may need to adapt commands for your OS."
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect GPU
detect_gpu() {
    if command_exists nvidia-smi; then
        echo "gpu"
    else
        echo "cpu"
    fi
}

# Function to setup venv environment
setup_venv() {
    print_status "Setting up Python virtual environment..."
    
    # Check Python version
    python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
    print_status "Detected Python version: $python_version"
    
    if [[ $(echo "$python_version >= 3.8" | bc -l) -eq 0 ]]; then
        print_error "Python 3.8+ required. Current version: $python_version"
        exit 1
    fi
    
    # Create virtual environment
    if [ ! -d "bert_airflow_env" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv bert_airflow_env
    else
        print_status "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source bert_airflow_env/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    install_dependencies_venv
}

# Function to setup conda environment
setup_conda() {
    print_status "Setting up Conda environment..."
    
    # Check if conda is installed
    if ! command_exists conda; then
        print_error "Conda not found. Please install Miniconda or Anaconda first."
        print_status "Download from: https://docs.conda.io/en/latest/miniconda.html"
        exit 1
    fi
    
    # Create conda environment
    if ! conda env list | grep -q "bert_airflow"; then
        print_status "Creating conda environment..."
        conda create -n bert_airflow python=3.9 -y
    else
        print_status "Conda environment 'bert_airflow' already exists"
    fi
    
    # Activate conda environment
    print_status "Activating conda environment..."
    eval "$(conda shell.bash hook)"
    conda activate bert_airflow
    
    # Install dependencies
    install_dependencies_conda
}

# Function to install dependencies with venv
install_dependencies_venv() {
    print_status "Installing dependencies with pip..."
    
    # Detect GPU support
    gpu_support=$(detect_gpu)
    
    # Install core dependencies
    pip install -r requirements.txt
    
    # Install PyTorch based on GPU support
    if [ "$gpu_support" == "gpu" ]; then
        print_status "GPU detected - installing PyTorch with CUDA support..."
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    else
        print_status "No GPU detected - installing CPU-only PyTorch..."
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    fi
    
    # Install Apache Airflow
    print_status "Installing Apache Airflow..."
    pip install apache-airflow==2.7.2
    pip install apache-airflow-providers-docker==3.7.2
    
    # Install additional ML packages
    pip install datasets accelerate evaluate
}

# Function to install dependencies with conda
install_dependencies_conda() {
    print_status "Installing dependencies with conda..."
    
    # Detect GPU support
    gpu_support=$(detect_gpu)
    
    # Install core packages via conda (better dependency resolution)
    print_status "Installing core packages..."
    conda install -y pandas numpy scikit-learn matplotlib seaborn requests
    
    # Install PyTorch based on GPU support
    if [ "$gpu_support" == "gpu" ]; then
        print_status "GPU detected - installing PyTorch with CUDA support..."
        conda install -y pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
    else
        print_status "No GPU detected - installing CPU-only PyTorch..."
        conda install -y pytorch torchvision torchaudio cpuonly -c pytorch
    fi
    
    # Install remaining packages via pip
    print_status "Installing additional packages..."
    pip install transformers apache-airflow==2.7.2 fastapi uvicorn textstat wordcloud plotly
    pip install apache-airflow-providers-docker==3.7.2
    pip install datasets accelerate evaluate
}

# Function to verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    # Test Python imports
    python3 -c "
import sys
print(f'Python version: {sys.version}')

try:
    import torch
    print(f'✅ PyTorch: {torch.__version__}')
    print(f'✅ CUDA available: {torch.cuda.is_available()}')
    if torch.cuda.is_available():
        print(f'✅ CUDA version: {torch.version.cuda}')
        print(f'✅ GPU count: {torch.cuda.device_count()}')
except ImportError as e:
    print(f'❌ PyTorch import failed: {e}')

try:
    import transformers
    print(f'✅ Transformers: {transformers.__version__}')
except ImportError as e:
    print(f'❌ Transformers import failed: {e}')

try:
    import pandas as pd
    print(f'✅ Pandas: {pd.__version__}')
except ImportError as e:
    print(f'❌ Pandas import failed: {e}')

try:
    import airflow
    print(f'✅ Airflow: {airflow.__version__}')
except ImportError as e:
    print(f'❌ Airflow import failed: {e}')
"
    
    # Test project imports
    if python3 -c "from src.dataset_manager import DatasetManager; print('✅ Dataset Manager imported successfully')" 2>/dev/null; then
        print_success "Project modules working correctly"
    else
        print_warning "Project modules may need additional setup"
    fi
    
    # Test basic functionality
    if [ -f "tests/test_setup.py" ]; then
        print_status "Running basic tests..."
        python3 tests/test_setup.py
    fi
}

# Function to setup Airflow
setup_airflow() {
    print_status "Setting up Apache Airflow..."
    
    # Create Airflow directories
    mkdir -p airflow/dags airflow/logs airflow/plugins airflow/config
    
    # Set Airflow home
    export AIRFLOW_HOME=$(pwd)/airflow
    
    # Initialize Airflow database
    print_status "Initializing Airflow database..."
    airflow db init
    
    # Create admin user
    print_status "Creating Airflow admin user..."
    airflow users create \
        --username admin \
        --firstname Admin \
        --lastname User \
        --role Admin \
        --email admin@example.com \
        --password admin
    
    # Copy DAG files
    if [ -d "dags" ]; then
        print_status "Copying DAG files..."
        cp dags/*.py airflow/dags/
    fi
    
    print_success "Airflow setup complete!"
    print_status "To start Airflow:"
    print_status "  airflow webserver --port 8080 &"
    print_status "  airflow scheduler &"
    print_status "Then visit: http://localhost:8080"
}

# Function to create activation script
create_activation_script() {
    env_type=$1
    
    if [ "$env_type" == "venv" ]; then
        cat > activate_env.sh << 'EOF'
#!/bin/bash
# Activate virtual environment for BERT Airflow project
source bert_airflow_env/bin/activate
export AIRFLOW_HOME=$(pwd)/airflow
echo "✅ Virtual environment activated"
echo "🌊 Airflow home: $AIRFLOW_HOME"
echo "🐍 Python: $(which python)"
EOF
    else
        cat > activate_env.sh << 'EOF'
#!/bin/bash
# Activate conda environment for BERT Airflow project
eval "$(conda shell.bash hook)"
conda activate bert_airflow
export AIRFLOW_HOME=$(pwd)/airflow
echo "✅ Conda environment activated"
echo "🌊 Airflow home: $AIRFLOW_HOME"
echo "🐍 Python: $(which python)"
EOF
    fi
    
    chmod +x activate_env.sh
    print_success "Created activation script: activate_env.sh"
}

# Main script
main() {
    print_status "BERT Fine-tuning with Apache Airflow - Environment Setup"
    print_status "========================================================"
    
    # Check if environment type is specified
    env_type=${1:-"venv"}
    
    if [ "$env_type" != "venv" ] && [ "$env_type" != "conda" ]; then
        print_error "Usage: $0 [venv|conda]"
        print_status "  venv  - Use Python virtual environment (default)"
        print_status "  conda - Use Conda environment"
        exit 1
    fi
    
    print_status "Environment type: $env_type"
    
    # Setup environment
    if [ "$env_type" == "conda" ]; then
        setup_conda
    else
        setup_venv
    fi
    
    # Verify installation
    verify_installation
    
    # Setup Airflow
    read -p "Setup Apache Airflow? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        setup_airflow
    fi
    
    # Create activation script
    create_activation_script "$env_type"
    
    print_success "Environment setup complete!"
    print_status ""
    print_status "Next steps:"
    print_status "1. Activate environment: source activate_env.sh"
    print_status "2. Test dataset manager: python3 src/dataset_manager.py"
    print_status "3. Run demo: python3 demo_complete_pipeline.py"
    print_status "4. Start training: python3 src/enhanced_bert_training.py"
    
    if [ "$env_type" == "venv" ]; then
        print_status "5. Deactivate when done: deactivate"
    else
        print_status "5. Deactivate when done: conda deactivate"
    fi
}

# Run main function with arguments
main "$@"
