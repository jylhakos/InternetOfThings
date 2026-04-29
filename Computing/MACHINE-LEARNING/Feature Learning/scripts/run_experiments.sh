#!/bin/bash

# Run Experiments Script for Feature Learning Project
# This script runs all the feature learning experiments

set -e  # Exit on any error

echo "Running Feature Learning experiments..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_experiment() {
    echo -e "${BLUE}[EXPERIMENT]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    print_warning "Virtual environment not activated. Activating..."
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        print_error "Virtual environment not found. Please run setup_environment.sh first."
        exit 1
    fi
fi

# Create necessary directories
mkdir -p models
mkdir -p results
mkdir -p logs

# Function to run experiment with error handling
run_experiment() {
    local name="$1"
    local script="$2"
    local logfile="logs/${name}_$(date +%Y%m%d_%H%M%S).log"
    
    print_experiment "Starting $name..."
    echo "Log file: $logfile"
    
    if python "$script" 2>&1 | tee "$logfile"; then
        print_status "✓ $name completed successfully"
        return 0
    else
        print_error "✗ $name failed. Check log: $logfile"
        return 1
    fi
}

# Check if source files exist
if [ ! -f "src/training/train_cnn.py" ]; then
    print_error "Training scripts not found. Please ensure all source files are created."
    exit 1
fi

successful_experiments=0
total_experiments=4

echo ""
echo "Starting Feature Learning Experiments"
echo "========================================"

# 1. CNN Feature Learning
print_experiment "Experiment 1/4: CNN Feature Learning on MNIST"
echo "Training CNN model for image feature extraction..."
if run_experiment "CNN_MNIST" "src/training/train_cnn.py"; then
    ((successful_experiments++))
fi

echo ""

# 2. RNN Feature Learning
print_experiment "Experiment 2/4: RNN Feature Learning on WikiText-2"
echo "Training RNN model for sequence feature extraction..."
if run_experiment "RNN_WikiText2" "src/training/train_rnn.py"; then
    ((successful_experiments++))
fi

echo ""

# 3. Autoencoder Feature Learning
print_experiment "Experiment 3/4: Autoencoder Feature Learning on Fashion-MNIST"
echo "Training Autoencoder for unsupervised feature learning..."
if run_experiment "Autoencoder_FashionMNIST" "src/training/train_autoencoder.py"; then
    ((successful_experiments++))
fi

echo ""

# 4. Transfer Learning
print_experiment "Experiment 4/4: Transfer Learning with Pre-trained Models"
echo "Using pre-trained models for feature extraction..."
if run_experiment "Transfer_Learning" "src/training/train_transfer_learning.py"; then
    ((successful_experiments++))
fi

echo ""
echo "EXPERIMENT SUMMARY"
echo "====================="
echo "Successful experiments: $successful_experiments/$total_experiments"

if [ $successful_experiments -eq $total_experiments ]; then
    print_status "The experiments completed successfully!"
    
    echo ""
    echo "1. Check model files in models/ directory"
    echo "2. View training logs in logs/ directory"
    echo "3. Run feature evaluation: python src/evaluation/evaluate_features.py"
    echo "4. Generate visualizations: python src/utils/visualization.py"
    
else
    failed=$((total_experiments - successful_experiments))
    print_warning "⚠️  $failed experiments failed. Check the logs for details."
    
    echo ""
    echo "🔧 Troubleshooting:"
    echo "1. Check log files in logs/ directory for error details"
    echo "2. Verify datasets are downloaded: bash scripts/download_datasets.sh"
    echo "3. Check system resources (RAM, GPU memory)"
    echo "4. Try running individual experiments manually"
fi

# Generate experiment report
cat > results/experiment_report.txt << EOF
Feature Learning Experiments Report
Generated on: $(date)

Experiments Summary:
- Total experiments: $total_experiments
- Successful: $successful_experiments  
- Failed: $((total_experiments - successful_experiments))

Experiment Details:
1. CNN Feature Learning: $([ -f "models/cnn_model.pth" ] && echo "✓ Success" || echo "✗ Failed")
2. RNN Feature Learning: $([ -f "models/rnn_model.pth" ] && echo "✓ Success" || echo "✗ Failed") 
3. Autoencoder Feature Learning: $([ -f "models/autoencoder_model.pth" ] && echo "✓ Success" || echo "✗ Failed")
4. Transfer Learning: $([ -f "models/transfer_model.pth" ] && echo "✓ Success" || echo "✗ Failed")

Model Files:
$(ls -la models/ 2>/dev/null || echo "No models found")

Log Files:
$(ls -la logs/ 2>/dev/null || echo "No logs found")
EOF

print_status "Experiment report saved to results/experiment_report.txt"
