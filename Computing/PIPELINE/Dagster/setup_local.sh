#!/bin/bash
# Local Development Setup Script for Dagster BERT Pipeline

set -euo pipefail

# Configuration
VENV_NAME="bert_dagster_env"
PROJECT_DIR=$(pwd)
DAGSTER_HOME="$PROJECT_DIR/dagster_home"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Function to check Python installation
check_python() {
    log_step "Checking Python installation..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed. Please install Python 3.8 or later."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    log_info "Python version: $PYTHON_VERSION"
    
    # Check if Python version is >= 3.8
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        log_info "Python version is compatible"
    else
        log_error "Python 3.8 or later is required"
        exit 1
    fi
}

# Function to create virtual environment
create_venv() {
    log_step "Creating Python virtual environment..."
    
    if [ -d "$VENV_NAME" ]; then
        log_warn "Virtual environment already exists"
        read -p "Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$VENV_NAME"
            log_info "Removed existing virtual environment"
        else
            log_info "Using existing virtual environment"
            return 0
        fi
    fi
    
    python3 -m venv "$VENV_NAME"
    log_info "Virtual environment created: $VENV_NAME"
}

# Function to activate virtual environment and install dependencies
install_dependencies() {
    log_step "Installing dependencies..."
    
    # Activate virtual environment
    source "$VENV_NAME/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    pip install -r requirements-dagster.txt
    
    # Also install the original requirements for backward compatibility
    if [ -f requirements.txt ]; then
        pip install -r requirements.txt
    fi
    
    if [ -f requirements-api.txt ]; then
        pip install -r requirements-api.txt
    fi
    
    log_info "Dependencies installed successfully"
}

# Function to setup Dagster home directory
setup_dagster_home() {
    log_step "Setting up Dagster home directory..."
    
    mkdir -p "$DAGSTER_HOME"
    
    # Create local development dagster.yaml
    cat > "$DAGSTER_HOME/dagster.yaml" << EOF
# Local Development Dagster Configuration

# SQLite storage for local development
storage:
  sqlite:
    base_dir: $DAGSTER_HOME/storage

# Default run launcher
run_launcher:
  module: dagster.core.launcher
  class: DefaultRunLauncher

# Queue run coordinator
run_coordinator:
  module: dagster.core.run_coordinator
  class: QueuedRunCoordinator
  config:
    max_concurrent_runs: 3

# Local compute log storage
compute_logs:
  module: dagster.core.storage.local_compute_log_manager
  class: LocalComputeLogManager
  config:
    base_dir: $DAGSTER_HOME/compute_logs

# Local schedule storage
schedule_storage:
  module: dagster.core.storage.sql
  class: DagsterSqliteScheduleStorage
  config:
    base_dir: $DAGSTER_HOME/schedules

# Local event log storage
event_log_storage:
  module: dagster.core.storage.sql
  class: DagsterSqliteEventLogStorage
  config:
    base_dir: $DAGSTER_HOME/history

# Local run storage
run_storage:
  module: dagster.core.storage.sql
  class: DagsterSqliteRunStorage
  config:
    base_dir: $DAGSTER_HOME/runs
EOF
    
    # Set environment variable
    export DAGSTER_HOME="$DAGSTER_HOME"
    
    log_info "Dagster home configured: $DAGSTER_HOME"
}

# Function to create workspace configuration
create_workspace() {
    log_step "Creating workspace configuration..."
    
    cat > workspace.yaml << EOF
# Dagster Workspace Configuration

load_from:
  - python_module:
      module_name: dagster_project
      working_directory: $PROJECT_DIR
EOF
    
    log_info "Workspace configuration created"
}

# Function to setup directories
setup_directories() {
    log_step "Setting up project directories..."
    
    mkdir -p data/training
    mkdir -p models/bert_fine_tuned
    mkdir -p results/evaluation
    mkdir -p results/inference_tests
    mkdir -p deployed_models/bert_classifier
    mkdir -p logs
    
    log_info "Project directories created"
}

# Function to create local environment file
create_env_file() {
    log_step "Creating environment configuration..."
    
    cat > .env.local << EOF
# Local Development Environment Configuration

# Dagster Configuration
DAGSTER_HOME=$DAGSTER_HOME
DAGSTER_IS_DEV_CLI=1
PYTHONPATH=$PROJECT_DIR

# Local S3 (if using LocalStack)
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=us-east-1
AWS_ENDPOINT_URL=http://localhost:4566

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Model Configuration
MODEL_NAME=bert-base-uncased
MAX_LENGTH=128
BATCH_SIZE=16
LEARNING_RATE=2e-5
EPOCHS=3
EOF
    
    log_info "Environment file created: .env.local"
}

# Function to verify installation
verify_installation() {
    log_step "Verifying installation..."
    
    # Activate virtual environment
    source "$VENV_NAME/bin/activate"
    
    # Check Dagster installation
    if python -c "import dagster; print(f'Dagster version: {dagster.__version__}')" 2>/dev/null; then
        log_info "Dagster installation verified"
    else
        log_error "Dagster installation failed"
        exit 1
    fi
    
    # Check PyTorch installation
    if python -c "import torch; print(f'PyTorch version: {torch.__version__}')" 2>/dev/null; then
        log_info "PyTorch installation verified"
    else
        log_error "PyTorch installation failed"
        exit 1
    fi
    
    # Check Transformers installation
    if python -c "import transformers; print(f'Transformers version: {transformers.__version__}')" 2>/dev/null; then
        log_info "Transformers installation verified"
    else
        log_error "Transformers installation failed"
        exit 1
    fi
    
    log_info "All installations verified successfully"
}

# Function to test Dagster setup
test_dagster() {
    log_step "Testing Dagster setup..."
    
    # Activate virtual environment
    source "$VENV_NAME/bin/activate"
    
    # Set environment variables
    export DAGSTER_HOME="$DAGSTER_HOME"
    export PYTHONPATH="$PROJECT_DIR"
    
    # Test Dagster CLI
    if dagster --version > /dev/null 2>&1; then
        log_info "Dagster CLI is working"
    else
        log_error "Dagster CLI test failed"
        exit 1
    fi
    
    # Check if the project can be loaded
    if python -c "from dagster_project import defs; print('Project loaded successfully')" 2>/dev/null; then
        log_info "Project can be loaded successfully"
    else
        log_warn "Project loading failed - this is expected if dependencies are not fully installed"
    fi
}

# Function to display usage instructions
show_usage() {
    echo ""
    echo "=== Dagster BERT Pipeline - Local Development Setup Complete ==="
    echo ""
    echo "To start using the pipeline:"
    echo ""
    echo "1. Activate the virtual environment:"
    echo "   source $VENV_NAME/bin/activate"
    echo ""
    echo "2. Set environment variables:"
    echo "   export DAGSTER_HOME=$DAGSTER_HOME"
    echo "   export PYTHONPATH=$PROJECT_DIR"
    echo ""
    echo "3. Start Dagster development server:"
    echo "   dagster dev -f workspace.yaml"
    echo ""
    echo "4. Open Dagster UI in browser:"
    echo "   http://localhost:3000"
    echo ""
    echo "5. Or run specific assets:"
    echo "   dagster asset materialize --select training_dataset"
    echo ""
    echo "6. To start the API server (in another terminal):"
    echo "   source $VENV_NAME/bin/activate"
    echo "   python api.py"
    echo ""
    echo "Available scripts:"
    echo "   ./setup_local.sh check     - Check Python installation"
    echo "   ./setup_local.sh install   - Install dependencies only"
    echo "   ./setup_local.sh test      - Test Dagster setup"
    echo "   ./setup_local.sh clean     - Clean up installation"
    echo ""
}

# Function to clean up installation
clean_installation() {
    log_warn "Cleaning up installation..."
    
    read -p "This will remove the virtual environment and Dagster home. Continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$VENV_NAME"
        rm -rf "$DAGSTER_HOME"
        rm -f workspace.yaml
        rm -f .env.local
        log_info "Cleanup completed"
    else
        log_info "Cleanup cancelled"
    fi
}

# Main execution
main() {
    echo "=== Dagster BERT Pipeline - Local Development Setup ==="
    echo ""
    
    case "${1:-full}" in
        "check")
            check_python
            ;;
        "install")
            check_python
            create_venv
            install_dependencies
            ;;
        "test")
            verify_installation
            test_dagster
            ;;
        "clean")
            clean_installation
            ;;
        "full")
            check_python
            create_venv
            install_dependencies
            setup_dagster_home
            create_workspace
            setup_directories
            create_env_file
            verify_installation
            test_dagster
            show_usage
            ;;
        *)
            echo "Usage: $0 {check|install|test|clean|full}"
            echo ""
            echo "Commands:"
            echo "  check   - Check Python installation"
            echo "  install - Install dependencies only"
            echo "  test    - Test installation"
            echo "  clean   - Clean up installation"
            echo "  full    - Complete setup (default)"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
