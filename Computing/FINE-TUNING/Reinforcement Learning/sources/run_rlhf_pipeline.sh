#!/bin/bash

################################################################################
# RLHF Training Pipeline Runner
################################################################################
# This script automates the complete RLHF training pipeline.
# It runs all three stages: SFT -> Reward Model -> PPO
#
# Usage:
#   ./run_rlhf_pipeline.sh [mode]
#
# Modes:
#   full    - Run complete pipeline (SFT + Reward + PPO)
#   dpo     - Run SFT + DPO (simpler alternative)
#   sft     - Run only supervised fine-tuning
#   test    - Run tests and inference
#   minimal - Quick test with minimal config
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MODE=${1:-full}
PYTHON=${PYTHON:-python}
SOURCES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to print colored messages
print_info() {
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

print_header() {
    echo ""
    echo "================================================================================"
    echo -e "${GREEN}$1${NC}"
    echo "================================================================================"
    echo ""
}

# Function to check GPU availability
check_gpu() {
    print_info "Checking GPU availability..."
    if command -v nvidia-smi &> /dev/null; then
        nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
        print_success "GPU detected"
    else
        print_warning "No GPU detected. Training will be slow on CPU."
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Function to check Python dependencies
check_dependencies() {
    print_info "Checking Python dependencies..."
    
    $PYTHON -c "import torch" 2>/dev/null || {
        print_error "PyTorch not found. Please install requirements:"
        echo "  pip install -r requirements.txt"
        exit 1
    }
    
    $PYTHON -c "import transformers" 2>/dev/null || {
        print_error "Transformers not found. Please install requirements."
        exit 1
    }
    
    print_success "All dependencies found"
}

# Function to run SFT
run_sft() {
    print_header "Stage 1: Supervised Fine-Tuning (SFT)"
    
    if [ -d "./sft_model" ]; then
        print_warning "SFT model directory already exists."
        read -p "Skip SFT training? (Y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
            print_info "Skipping SFT training"
            return 0
        fi
    fi
    
    print_info "Starting SFT training..."
    $PYTHON "$SOURCES_DIR/1_supervised_fine_tuning.py"
    print_success "SFT training completed!"
}

# Function to run Reward Model training
run_reward_model() {
    print_header "Stage 2: Reward Model Training"
    
    if [ ! -d "./sft_model" ]; then
        print_error "SFT model not found. Please run SFT first."
        exit 1
    fi
    
    if [ -d "./reward_model" ]; then
        print_warning "Reward model directory already exists."
        read -p "Skip reward model training? (Y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
            print_info "Skipping reward model training"
            return 0
        fi
    fi
    
    print_info "Starting reward model training..."
    $PYTHON "$SOURCES_DIR/2_reward_model_training.py"
    print_success "Reward model training completed!"
}

# Function to run PPO
run_ppo() {
    print_header "Stage 3: PPO-based RLHF"
    
    if [ ! -d "./sft_model" ]; then
        print_error "SFT model not found. Please run SFT first."
        exit 1
    fi
    
    if [ ! -d "./reward_model" ]; then
        print_error "Reward model not found. Please run reward model training first."
        exit 1
    fi
    
    print_info "Starting PPO training..."
    $PYTHON "$SOURCES_DIR/3_ppo_rlhf_training.py"
    print_success "PPO training completed!"
}

# Function to run DPO
run_dpo() {
    print_header "Stage 2: Direct Preference Optimization (DPO)"
    
    if [ ! -d "./sft_model" ]; then
        print_error "SFT model not found. Please run SFT first."
        exit 1
    fi
    
    print_info "Starting DPO training..."
    $PYTHON "$SOURCES_DIR/4_dpo_training.py"
    print_success "DPO training completed!"
}

# Function to run inference tests
run_tests() {
    print_header "Testing Trained Models"
    
    # Find available models
    models=()
    [ -d "./sft_model" ] && models+=("sft_model")
    [ -d "./dpo_model" ] && models+=("dpo_model")
    [ -d "./ppo_model" ] && models+=("ppo_model")
    
    if [ ${#models[@]} -eq 0 ]; then
        print_error "No trained models found."
        exit 1
    fi
    
    print_info "Found models: ${models[*]}"
    
    for model in "${models[@]}"; do
        print_info "Testing $model..."
        $PYTHON "$SOURCES_DIR/5_model_inference.py" --model "./$model" --mode test
    done
    
    print_success "All tests completed!"
}

# Main execution
main() {
    print_header "RLHF Training Pipeline"
    print_info "Mode: $MODE"
    
    # Check prerequisites
    check_gpu
    check_dependencies
    
    # Change to sources directory
    cd "$SOURCES_DIR/.." || exit 1
    
    case $MODE in
        full)
            print_info "Running full RLHF pipeline..."
            run_sft
            run_reward_model
            run_ppo
            print_success "Full RLHF pipeline completed!"
            ;;
        
        dpo)
            print_info "Running DPO pipeline..."
            run_sft
            run_dpo
            print_success "DPO pipeline completed!"
            ;;
        
        sft)
            print_info "Running SFT only..."
            run_sft
            ;;
        
        reward)
            print_info "Running reward model training..."
            run_reward_model
            ;;
        
        ppo)
            print_info "Running PPO training..."
            run_ppo
            ;;
        
        test)
            print_info "Running tests..."
            run_tests
            ;;
        
        minimal)
            print_info "Running minimal test pipeline..."
            export MINIMAL_MODE=1
            run_sft
            run_dpo
            print_success "Minimal pipeline completed!"
            ;;
        
        *)
            print_error "Unknown mode: $MODE"
            echo ""
            echo "Usage: $0 [mode]"
            echo ""
            echo "Available modes:"
            echo "  full    - Run complete pipeline (SFT + Reward + PPO)"
            echo "  dpo     - Run SFT + DPO (simpler alternative)"
            echo "  sft     - Run only supervised fine-tuning"
            echo "  reward  - Run only reward model training"
            echo "  ppo     - Run only PPO training"
            echo "  test    - Run inference tests"
            echo "  minimal - Quick test with minimal config"
            exit 1
            ;;
    esac
    
    print_header "Pipeline Execution Summary"
    print_success "All requested stages completed successfully!"
    
    # Show trained models
    echo ""
    print_info "Trained models:"
    [ -d "./sft_model" ] && echo "  ✓ SFT Model: ./sft_model"
    [ -d "./reward_model" ] && echo "  ✓ Reward Model: ./reward_model"
    [ -d "./ppo_model" ] && echo "  ✓ PPO Model: ./ppo_model"
    [ -d "./dpo_model" ] && echo "  ✓ DPO Model: ./dpo_model"
    
    echo ""
    print_info "Next steps:"
    echo "  1. Test your model interactively:"
    echo "     python sources/5_model_inference.py --model ./sft_model --mode interactive"
    echo ""
    echo "  2. Compare models:"
    echo "     python sources/5_model_inference.py --model ./sft_model --mode compare --compare-with ./dpo_model"
    echo ""
    echo "  3. Deploy your model (see README.md for details)"
}

# Run main function
main
