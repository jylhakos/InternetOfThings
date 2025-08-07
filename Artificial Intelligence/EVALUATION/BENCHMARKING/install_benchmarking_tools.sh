#!/bin/bash
# LLM Benchmarking Tools Installation Script for Linux/Debian

set -e

echo "=========================================="
echo "LLM Benchmarking Tools Installation Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Check if running on supported OS
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    print_error "This script is designed for Linux systems only."
    exit 1
fi

# Check if running as root (not recommended)
if [[ $EUID -eq 0 ]]; then
    print_warning "Running as root is not recommended. Consider running as a regular user."
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

print_status "Starting installation process..."

# Update system packages
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
print_status "Installing system dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    curl \
    wget \
    build-essential \
    libssl-dev \
    libffi-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libffi-dev \
    liblzma-dev

# Check Python version
python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
min_version="3.8"

if [ "$(printf '%s\n' "$min_version" "$python_version" | sort -V | head -n1)" = "$min_version" ]; then
    print_status "Python version $python_version is supported."
else
    print_error "Python version $python_version is not supported. Minimum required: $min_version"
    exit 1
fi

# Create project directory
PROJECT_DIR="$HOME/llm_benchmarking"
print_status "Creating project directory at $PROJECT_DIR..."
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Create virtual environment
VENV_NAME="benchmark_env"
print_status "Creating virtual environment '$VENV_NAME'..."
python3 -m venv "$VENV_NAME"

# Activate virtual environment
print_status "Activating virtual environment..."
source "$VENV_NAME/bin/activate"

# Upgrade pip and tools
print_status "Upgrading pip and setuptools..."
pip install --upgrade pip setuptools wheel

# Install PyTorch (CPU version for compatibility)
print_status "Installing PyTorch..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install core ML/NLP libraries
print_status "Installing core ML/NLP libraries..."
pip install \
    transformers \
    datasets \
    evaluate \
    accelerate \
    tokenizers \
    scikit-learn \
    pandas \
    numpy \
    matplotlib \
    seaborn \
    plotly

# Install benchmarking tools
print_status "Installing benchmarking frameworks..."
pip install \
    deepeval \
    deepchecks[nlp] \
    wandb \
    tensorboard

# Install evaluation metrics
print_status "Installing evaluation metrics..."
pip install \
    nltk \
    rouge-score \
    sacrebleu \
    bert-score \
    sentence-transformers \
    spacy

# Install Jupyter for interactive development
print_status "Installing Jupyter..."
pip install \
    jupyter \
    notebook \
    ipykernel \
    ipywidgets

# Install additional utilities
print_status "Installing additional utilities..."
pip install \
    tqdm \
    requests \
    beautifulsoup4 \
    pyyaml \
    python-dotenv

# Download NLTK data
print_status "Downloading NLTK data..."
python -c "
import nltk
try:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('wordnet')
    print('NLTK data downloaded successfully')
except Exception as e:
    print(f'Error downloading NLTK data: {e}')
"

# Download spaCy model
print_status "Installing spaCy English model..."
python -m spacy download en_core_web_sm

# Create requirements.txt
print_status "Creating requirements.txt..."
pip freeze > requirements.txt

# Create directory structure
print_status "Creating directory structure..."
mkdir -p {data,models,results,scripts,notebooks,configs}

# Create sample configuration file
print_status "Creating sample configuration..."
cat > configs/benchmark_config.yaml << EOL
# LLM Benchmarking Configuration

models:
  - name: "BERT"
    model_name: "bert-base-uncased"
    task_types: ["classification", "qa"]
  - name: "DistilBERT" 
    model_name: "distilbert-base-uncased"
    task_types: ["classification", "qa"]
  - name: "ALBERT"
    model_name: "albert-base-v2"
    task_types: ["classification", "qa"]

benchmarks:
  question_answering:
    dataset: "squad"
    num_samples: 100
    metrics: ["exact_match", "f1_score"]
  
  text_classification:
    dataset: "imdb"
    num_samples: 500
    metrics: ["accuracy", "f1_score", "precision", "recall"]
  
  mathematical_reasoning:
    num_problems: 50
    metrics: ["accuracy"]

output:
  results_dir: "results"
  save_predictions: true
  generate_plots: true
EOL

# Create activation script
print_status "Creating activation script..."
cat > activate_env.sh << EOL
#!/bin/bash
# Activation script for LLM benchmarking environment

echo "Activating LLM benchmarking environment..."
cd "$PROJECT_DIR"
source $VENV_NAME/bin/activate

echo "Environment activated!"
echo "Project directory: \$(pwd)"
echo "Python: \$(which python)"
echo "Pip packages: \$(pip list | wc -l) installed"

# Optional: set environment variables
export TOKENIZERS_PARALLELISM=false
export HF_HOME="\$HOME/.cache/huggingface"

echo ""
echo "Available commands:"
echo "  jupyter notebook    - Start Jupyter notebook server"
echo "  python scripts/benchmark_runner.py - Run benchmarks"
echo "  deactivate         - Exit virtual environment"
EOL

chmod +x activate_env.sh

# Create basic benchmark script
print_status "Creating basic benchmark script..."
mkdir -p scripts
cat > scripts/quick_benchmark.py << 'EOL'
#!/usr/bin/env python3
"""
Quick LLM Benchmark Script
A simple script to test the installation and run basic benchmarks
"""

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import time

def test_installation():
    """Test if all components are installed correctly"""
    print("=== Installation Test ===")
    
    # Test imports
    try:
        import transformers
        import datasets
        import sklearn
        import deepeval
        print("✓ All required packages imported successfully")
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    
    # Test model loading
    try:
        print("Testing model loading...")
        tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased')
        model = AutoModelForSequenceClassification.from_pretrained('distilbert-base-uncased')
        print("✓ Model loaded successfully")
    except Exception as e:
        print(f"✗ Model loading error: {e}")
        return False
    
    return True

def quick_benchmark():
    """Run a quick benchmark test"""
    print("\n=== Quick Benchmark Test ===")
    
    # Sample texts
    texts = [
        "This movie is absolutely fantastic!",
        "I hate this terrible film.",
        "The weather is nice today.",
        "This product is okay, nothing special."
    ]
    
    # Load model
    tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased')
    model = AutoModelForSequenceClassification.from_pretrained('distilbert-base-uncased')
    
    print("Running inference on sample texts...")
    start_time = time.time()
    
    for i, text in enumerate(texts):
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        
        with torch.no_grad():
            outputs = model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
        print(f"Text {i+1}: {predictions.numpy()}")
    
    end_time = time.time()
    print(f"Total inference time: {end_time - start_time:.2f} seconds")
    print("✓ Quick benchmark completed successfully!")

if __name__ == "__main__":
    print("LLM Benchmarking Tools - Quick Test")
    print("=" * 40)
    
    if test_installation():
        quick_benchmark()
        print("\n🎉 Installation verified successfully!")
        print("You can now run full benchmarks using the benchmark_runner.py script.")
    else:
        print("\n❌ Installation test failed. Please check the error messages above.")
EOL

chmod +x scripts/quick_benchmark.py

# Create README for the project
print_status "Creating project README..."
cat > PROJECT_README.md << EOL
# LLM Benchmarking Environment

This environment has been set up for benchmarking Large Language Models.

## Quick Start

1. Activate the environment:
   \`\`\`bash
   ./activate_env.sh
   \`\`\`

2. Test the installation:
   \`\`\`bash
   python scripts/quick_benchmark.py
   \`\`\`

3. Start Jupyter notebook:
   \`\`\`bash
   jupyter notebook
   \`\`\`

## Directory Structure

- \`data/\` - Datasets and input files
- \`models/\` - Downloaded model files
- \`results/\` - Benchmark results and outputs
- \`scripts/\` - Python scripts
- \`notebooks/\` - Jupyter notebooks
- \`configs/\` - Configuration files

## Installed Tools

- DeepEval - LLM evaluation framework
- Deepchecks - ML validation and monitoring
- Transformers - Hugging Face transformers library
- PyTorch - Deep learning framework
- Various evaluation metrics (BLEU, ROUGE, etc.)

## Configuration

Edit \`configs/benchmark_config.yaml\` to customize benchmarking parameters.

## Documentation

For detailed setup and usage instructions, see:
- Main documentation: README.md
- Setup and usage guide: SETUP_AND_USAGE.md
EOL

# Final setup steps
print_status "Performing final setup..."

# Create a sample notebook
print_status "Creating sample Jupyter notebook..."
cat > notebooks/LLM_Benchmark_Tutorial.ipynb << 'EOL'
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# LLM Benchmarking Tutorial\n",
    "\n",
    "This notebook demonstrates how to benchmark Large Language Models using the installed tools."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Import required libraries\n",
    "import torch\n",
    "from transformers import AutoTokenizer, AutoModelForSequenceClassification\n",
    "import pandas as pd\n",
    "import matplotlib.pyplot as plt\n",
    "import time\n",
    "\n",
    "print(\"Libraries imported successfully!\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Load Models\n",
    "\n",
    "Let's load different BERT variants for comparison."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Define models to compare\n",
    "models = {\n",
    "    'BERT': 'bert-base-uncased',\n",
    "    'DistilBERT': 'distilbert-base-uncased',\n",
    "    'ALBERT': 'albert-base-v2'\n",
    "}\n",
    "\n",
    "# This cell is ready to run - uncomment when you want to load models\n",
    "# loaded_models = {}\n",
    "# tokenizers = {}\n",
    "# \n",
    "# for name, model_name in models.items():\n",
    "#     print(f\"Loading {name}...\")\n",
    "#     tokenizers[name] = AutoTokenizer.from_pretrained(model_name)\n",
    "#     loaded_models[name] = AutoModelForSequenceClassification.from_pretrained(model_name)\n",
    "#     print(f\"{name} loaded successfully!\")"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
EOL

print_status "Installation completed successfully! 🎉"
echo ""
echo "=========================================="
echo "          INSTALLATION SUMMARY"
echo "=========================================="
echo "Project directory: $PROJECT_DIR"
echo "Virtual environment: $VENV_NAME"
echo "Python version: $(python --version)"
echo "Installed packages: $(pip list | wc -l)"
echo ""
echo "To get started:"
echo "1. Run: ./activate_env.sh"
echo "2. Test: python scripts/quick_benchmark.py"
echo "3. Explore: jupyter notebook"
echo ""
echo "For more information:"
echo "- Project setup: PROJECT_README.md"
echo "- Detailed guide: SETUP_AND_USAGE.md"
echo "=========================================="

# Test the installation
print_status "Running installation test..."
python scripts/quick_benchmark.py
