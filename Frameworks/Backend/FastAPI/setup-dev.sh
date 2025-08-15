#!/bin/bash

# Developer Setup Script for gRPC FastAPI Project
# This script sets up the development environment including gRPC code generation

set -e

echo "🚀 FastAPI gRPC Development Environment Setup"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running on supported OS
print_status "Checking operating system..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    print_success "Linux detected"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    print_success "macOS detected"
else
    print_warning "Unsupported OS: $OSTYPE. Proceeding anyway..."
fi

# Check Python version
print_status "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_success "Python $PYTHON_VERSION found"
    
    # Check if version is 3.9+
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -ge 9 ]]; then
        print_success "Python version is compatible (3.9+)"
    else
        print_error "Python 3.9+ required, found $PYTHON_VERSION"
        exit 1
    fi
else
    print_error "Python3 not found. Please install Python 3.9+"
    exit 1
fi

# Create virtual environment
print_status "Setting up Python virtual environment..."
if [[ ! -d "venv" ]]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
print_success "Pip upgraded to $(pip --version | awk '{print $2}')"

# Install requirements
print_status "Installing Python dependencies..."
if [[ -f "requirements.txt" ]]; then
    pip install -r requirements.txt > /dev/null 2>&1
    print_success "Dependencies installed from requirements.txt"
else
    print_warning "requirements.txt not found, installing basic dependencies..."
    pip install fastapi uvicorn grpcio grpcio-tools protobuf redis > /dev/null 2>&1
    print_success "Basic dependencies installed"
fi

# Install development dependencies
print_status "Installing development dependencies..."
pip install pytest pytest-asyncio pytest-cov black isort flake8 mypy > /dev/null 2>&1
print_success "Development tools installed"

# Generate gRPC code
print_status "Generating gRPC code from Protocol Buffers..."
if [[ -f "generate_grpc.sh" ]]; then
    chmod +x generate_grpc.sh
    ./generate_grpc.sh > /dev/null 2>&1
    print_success "gRPC code generated successfully"
else
    print_warning "generate_grpc.sh not found, attempting manual generation..."
    
    if [[ -d "protos" ]]; then
        python -m grpc_tools.protoc \
            --proto_path=protos \
            --python_out=protos \
            --grpc_python_out=protos \
            protos/*.proto 2>/dev/null
        print_success "gRPC code generated manually"
    else
        print_warning "No protos directory found, skipping gRPC generation"
    fi
fi

# Verify gRPC generation
print_status "Verifying gRPC code generation..."
EXPECTED_FILES=(
    "protos/auth_pb2.py"
    "protos/auth_pb2_grpc.py"
    "protos/user_pb2.py"
    "protos/user_pb2_grpc.py"
    "protos/common_pb2.py"
    "protos/common_pb2_grpc.py"
)

ALL_GENERATED=true
for file in "${EXPECTED_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        print_success "Generated: $file"
    else
        print_warning "Missing: $file"
        ALL_GENERATED=false
    fi
done

if [[ "$ALL_GENERATED" == "true" ]]; then
    print_success "All gRPC files generated successfully"
else
    print_warning "Some gRPC files are missing, but proceeding..."
fi

# Set up pre-commit hook
print_status "Setting up pre-commit hook..."
if [[ -f "scripts/pre-commit-hook.sh" ]]; then
    if [[ -d ".git" ]]; then
        cp scripts/pre-commit-hook.sh .git/hooks/pre-commit
        chmod +x .git/hooks/pre-commit
        print_success "Pre-commit hook installed"
    else
        print_warning "Not a Git repository, skipping pre-commit hook"
    fi
else
    print_warning "Pre-commit hook script not found"
fi

# Check for Redis (optional)
print_status "Checking for Redis..."
if command -v redis-server &> /dev/null; then
    print_success "Redis found: $(redis-server --version | head -n1)"
else
    print_warning "Redis not found. Install Redis for full functionality:"
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "  Ubuntu/Debian: sudo apt install redis-server"
        echo "  RHEL/CentOS:   sudo yum install redis"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  macOS:         brew install redis"
    fi
fi

# Check for Docker (optional)
print_status "Checking for Docker..."
if command -v docker &> /dev/null; then
    print_success "Docker found: $(docker --version)"
else
    print_warning "Docker not found. Install Docker for containerized development."
fi

# Create necessary directories
print_status "Creating project directories..."
mkdir -p tests logs
touch protos/__init__.py services/__init__.py tests/__init__.py 2>/dev/null || true
print_success "Project structure created"

# Run basic tests
print_status "Running basic tests..."
if [[ -d "tests" ]] && find tests -name "*.py" | grep -q .; then
    python -m pytest tests/ -v --tb=short > /dev/null 2>&1
    if [[ $? -eq 0 ]]; then
        print_success "All tests passed"
    else
        print_warning "Some tests failed, check test output"
    fi
else
    print_warning "No tests found to run"
fi

echo ""
echo "🎉 Setup Complete!"
echo "=================="
print_success "Development environment is ready!"
echo ""
echo "📋 Next Steps:"
echo "1. Start Redis (if not running):"
echo "   redis-server"
echo ""
echo "2. Start the gRPC Auth Service:"
echo "   python services/auth_service.py"
echo ""
echo "3. Start the FastAPI application:"
echo "   uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "4. Test the API:"
echo "   curl http://localhost:8000/health"
echo ""
echo "📚 Development Commands:"
echo "• Generate gRPC code:     ./generate_grpc.sh"
echo "• Run tests:              python -m pytest tests/ -v"
echo "• Run gRPC tests:         ./test_grpc.sh"
echo "• Format code:            black . && isort ."
echo "• Type checking:          mypy ."
echo "• Lint code:              flake8 ."
echo ""
echo "🐳 Docker Commands:"
echo "• Build image:            docker build -t fastapi-grpc ."
echo "• Run container:          docker run -p 8000:8000 fastapi-grpc"
echo "• Start with compose:     docker-compose up -d"
echo ""
echo "📖 Documentation:"
echo "• README.md                 - Project overview"
echo "• GRPC.md                   - Complete gRPC guide"
echo "• DEVOPS.md                 - CI/CD and DevOps guidance"
echo ""
print_success "Happy coding! 🚀"
