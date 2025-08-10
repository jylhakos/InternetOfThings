#!/bin/bash

# 🔧 CUDA-enabled PyTorch Environment Setup Script
# This script automatically detects your system configuration and installs
# the appropriate PyTorch version with CUDA support

set -e  # Exit on any error

echo "🔧 Setting up CUDA-enabled PyTorch environment for Feature Learning..."
echo "=================================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if virtual environment is activated
check_virtual_env() {
    if [[ -z "$VIRTUAL_ENV" ]]; then
        print_warning "Virtual environment not detected"
        if [[ -d "venv" ]]; then
            print_info "Activating existing virtual environment..."
            source venv/bin/activate
            print_status "Virtual environment activated"
        else
            print_info "Creating new virtual environment..."
            python3 -m venv venv
            source venv/bin/activate
            print_status "Virtual environment created and activated"
        fi
    else
        print_status "Virtual environment already active: $VIRTUAL_ENV"
    fi
}

# Detect system information
detect_system() {
    echo ""
    print_info "Detecting system configuration..."
    
    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        print_status "OS: Linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_status "OS: macOS"
    else
        OS="unknown"
        print_warning "OS: $OSTYPE (may not be fully supported)"
    fi
    
    # Detect architecture
    ARCH=$(uname -m)
    print_status "Architecture: $ARCH"
}

# Check for NVIDIA GPU and drivers
check_gpu() {
    echo ""
    print_info "Checking for NVIDIA GPU and drivers..."
    
    if command -v nvidia-smi &> /dev/null; then
        print_status "NVIDIA GPU detected"
        nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader | while read line; do
            print_info "  $line"
        done
        HAS_GPU=true
        
        # Get driver version
        DRIVER_VERSION=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader,nounits | head -n 1)
        print_status "NVIDIA Driver Version: $DRIVER_VERSION"
    else
        print_warning "No NVIDIA GPU detected or drivers not installed"
        HAS_GPU=false
    fi
}

# Check for CUDA toolkit
check_cuda() {
    echo ""
    print_info "Checking for CUDA toolkit..."
    
    if command -v nvcc &> /dev/null; then
        CUDA_VERSION=$(nvcc --version | grep "release" | sed -n 's/.*release \([0-9]\+\.[0-9]\+\).*/\1/p')
        print_status "CUDA toolkit detected: $CUDA_VERSION"
        HAS_CUDA=true
    else
        print_warning "CUDA toolkit not found"
        HAS_CUDA=false
        
        if [[ "$HAS_GPU" == true ]]; then
            print_info "Consider installing CUDA toolkit:"
            print_info "  https://developer.nvidia.com/cuda-downloads"
        fi
    fi
}

# Install system dependencies
install_system_deps() {
    echo ""
    print_info "Installing system dependencies..."
    
    if [[ "$OS" == "linux" ]]; then
        # Check if running as root or with sudo access
        if command -v apt &> /dev/null; then
            print_info "Installing build dependencies (requires sudo)..."
            sudo apt update
            sudo apt install -y build-essential python3-dev python3-pip
            sudo apt install -y libblas-dev liblapack-dev libatlas-base-dev gfortran
            sudo apt install -y libjpeg-dev libpng-dev libtiff-dev
            print_status "System dependencies installed"
        else
            print_warning "apt not found - please install build dependencies manually"
        fi
    elif [[ "$OS" == "macos" ]]; then
        if command -v brew &> /dev/null; then
            print_info "Installing dependencies with Homebrew..."
            brew install libjpeg libpng libtiff
            print_status "System dependencies installed"
        else
            print_warning "Homebrew not found - install from https://brew.sh/"
        fi
    fi
}

# Determine PyTorch installation command
determine_pytorch_install() {
    echo ""
    print_info "Determining appropriate PyTorch installation..."
    
    if [[ "$HAS_GPU" == true && "$HAS_CUDA" == true ]]; then
        # GPU with CUDA - install CUDA version
        case $CUDA_VERSION in
            "11.8")
                TORCH_INDEX="https://download.pytorch.org/whl/cu118"
                print_status "Will install PyTorch with CUDA 11.8 support"
                ;;
            "12.1")
                TORCH_INDEX="https://download.pytorch.org/whl/cu121"
                print_status "Will install PyTorch with CUDA 12.1 support"
                ;;
            "12.2")
                TORCH_INDEX="https://download.pytorch.org/whl/cu121"  # Use 12.1 for 12.2
                print_status "Will install PyTorch with CUDA 12.1 support (compatible with 12.2)"
                ;;
            *)
                TORCH_INDEX=""
                print_warning "Unknown CUDA version $CUDA_VERSION - will install default PyTorch"
                ;;
        esac
    elif [[ "$HAS_GPU" == true ]]; then
        # GPU but no CUDA toolkit
        print_warning "NVIDIA GPU found but no CUDA toolkit - installing CPU version"
        print_info "To use GPU acceleration, install CUDA toolkit first"
        TORCH_INDEX="https://download.pytorch.org/whl/cpu"
    else
        # No GPU - CPU only
        print_info "No NVIDIA GPU detected - installing CPU-only PyTorch"
        TORCH_INDEX="https://download.pytorch.org/whl/cpu"
    fi
}

# Install PyTorch and dependencies
install_pytorch() {
    echo ""
    print_info "Installing PyTorch and dependencies..."
    
    # Upgrade pip first
    pip install --upgrade pip
    
    # Uninstall existing PyTorch if present
    pip uninstall -y torch torchvision torchaudio 2>/dev/null || true
    
    # Install PyTorch
    if [[ -n "$TORCH_INDEX" ]]; then
        print_info "Installing PyTorch from: $TORCH_INDEX"
        pip install torch torchvision torchaudio --index-url "$TORCH_INDEX"
    else
        print_info "Installing default PyTorch"
        pip install torch torchvision torchaudio
    fi
    
    print_status "PyTorch installation complete"
}

# Install additional dependencies
install_dependencies() {
    echo ""
    print_info "Installing additional dependencies..."
    
    pip install numpy matplotlib scikit-learn seaborn pandas jupyter
    pip install Pillow  # PIL
    
    # Optional dependencies
    print_info "Installing optional dependencies..."
    pip install datasets transformers  # Hugging Face
    pip install psutil  # System monitoring
    
    print_status "All dependencies installed"
}

# Verify installation
verify_installation() {
    echo ""
    print_info "Verifying PyTorch installation..."
    
    python -c "
import torch
import torchvision
print('✅ PyTorch installation verified')
print(f'PyTorch version: {torch.__version__}')
print(f'TorchVision version: {torchvision.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')

if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
    print(f'GPU count: {torch.cuda.device_count()}')
    for i in range(torch.cuda.device_count()):
        print(f'GPU {i}: {torch.cuda.get_device_name(i)}')
else:
    print('Running in CPU-only mode')

# Test basic operations
try:
    x = torch.randn(10, 10)
    y = torch.mm(x, x)
    print(' CPU operations: OK')
    
    if torch.cuda.is_available():
        x_gpu = x.cuda()
        y_gpu = torch.mm(x_gpu, x_gpu)
        print(' GPU operations: OK')
except Exception as e:
    print(f'❌ Error in tensor operations: {e}')
    exit(1)

print(' Installation verification complete!')
"
    
    if [[ $? -eq 0 ]]; then
        print_status "PyTorch installation verified successfully!"
    else
        print_error "PyTorch installation verification failed"
        exit 1
    fi
}

# Create diagnostic script shortcut
create_shortcuts() {
    echo ""
    print_info "Creating diagnostic shortcuts..."
    
    # Create a simple activation script
    cat > activate_env.sh << 'EOF'
#!/bin/bash
echo " Activating Feature Learning Environment..."
source venv/bin/activate
echo "✅ Environment activated!"
echo "Run 'python diagnose_setup.py' to check your setup"
echo "Run 'python demo_comprehensive_feature_engineering.py' to test all scripts"
EOF
    
    chmod +x activate_env.sh
    print_status "Created activation script: ./activate_env.sh"
}

# Main installation process
main() {
    echo "Starting automated setup process..."
    echo ""
    
    # Check virtual environment
    check_virtual_env
    
    # System detection
    detect_system
    check_gpu
    check_cuda
    
    # Install dependencies
    install_system_deps
    determine_pytorch_install
    install_pytorch
    install_dependencies
    
    # Verify and finalize
    verify_installation
    create_shortcuts
    
    echo ""
    echo "=================================================================="
    print_status "CUDA-enabled PyTorch environment setup complete."
    echo "=================================================================="
    echo ""
    print_info "Next steps:"
    echo "  1. Run diagnostics: python diagnose_setup.py"
    echo "  2. Test feature engineering: python demo_comprehensive_feature_engineering.py"
    echo "  3. Start experimenting: python src/feature_engineering/cnn_feature_engineering.py --help"
    echo ""
    
    if [[ "$HAS_GPU" == true && "$HAS_CUDA" == true ]]; then
        print_status " GPU acceleration is available - your scripts will run faster!"
    else
        print_info " Running in CPU-only mode - scripts will work but may be slower"
        if [[ "$HAS_GPU" == true ]]; then
            print_info "To enable GPU acceleration, install CUDA toolkit and re-run this script"
        fi
    fi
    
    echo ""
}

# Run main function
main "$@"
