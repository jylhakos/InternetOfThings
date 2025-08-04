#!/bin/bash
"""
Docker build and deployment script: Builds Docker image and provides deployment options
"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

IMAGE_NAME="bert-classifier"
TAG="latest"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}BERT Classifier Docker Build Script${NC}"
echo -e "${BLUE}========================================${NC}"

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if Docker is installed and running
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker service."
        exit 1
    fi
    
    print_status "Docker is available and running"
}

# Build Docker image
build_image() {
    print_info "Building Docker image: ${IMAGE_NAME}:${TAG}"
    
    # Create .dockerignore if it doesn't exist
    if [ ! -f .dockerignore ]; then
        cat << 'EOF' > .dockerignore
bert_env/
.git/
.gitignore
*.md
test_*.py
examples.py
project_summary.py
__pycache__/
*.pyc
.pytest_cache/
.vscode/
.idea/
*.log
EOF
        print_status "Created .dockerignore file"
    fi
    
    # Build image
    docker build -t ${IMAGE_NAME}:${TAG} .
    
    if [ $? -eq 0 ]; then
        print_status "Docker image built successfully: ${IMAGE_NAME}:${TAG}"
    else
        print_error "Docker build failed"
        exit 1
    fi
}

# Run container
run_container() {
    print_info "Starting container on port 8000..."
    
    # Stop existing container if running
    if docker ps -q --filter "name=${IMAGE_NAME}" | grep -q .; then
        print_warning "Stopping existing container..."
        docker stop ${IMAGE_NAME} && docker rm ${IMAGE_NAME}
    fi
    
    # Run new container
    docker run -d \
        --name ${IMAGE_NAME} \
        -p 8000:8000 \
        --health-cmd="curl -f http://localhost:8000/health || exit 1" \
        --health-interval=30s \
        --health-timeout=10s \
        --health-start-period=60s \
        --health-retries=3 \
        ${IMAGE_NAME}:${TAG}
    
    print_status "Container started successfully"
    print_info "API will be available at: http://localhost:8000"
    print_info "API docs at: http://localhost:8000/docs"
}

# Wait for API to be ready
wait_for_api() {
    print_info "Waiting for API to be ready..."
    
    for i in {1..60}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            print_status "API is ready!"
            return 0
        fi
        sleep 1
    done
    
    print_error "API did not become ready within 60 seconds"
    docker logs ${IMAGE_NAME}
    return 1
}

# Test API
test_api() {
    print_info "Testing API endpoints..."
    
    # Test health endpoint
    response=$(curl -s http://localhost:8000/health)
    if echo "$response" | grep -q "healthy"; then
        print_status "Health check passed"
    else
        print_error "Health check failed"
        return 1
    fi
    
    # Test classification endpoint
    response=$(curl -s -X POST "http://localhost:8000/classify" \
        -H "Content-Type: application/json" \
        -d '{"text": "I love this product!"}')
    
    if echo "$response" | grep -q "prediction"; then
        print_status "Classification test passed"
        print_info "Sample response: $response"
    else
        print_error "Classification test failed"
        return 1
    fi
}

# Show usage information
show_usage() {
    echo -e "${YELLOW}Usage: $0 [OPTION]${NC}"
    echo ""
    echo "Options:"
    echo "  build     Build Docker image only"
    echo "  run       Build and run container"
    echo "  test      Build, run, and test API"
    echo "  stop      Stop running container"
    echo "  logs      Show container logs"
    echo "  clean     Remove container and image"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 test              # Full build, run, and test"
    echo "  $0 build             # Just build the image"
    echo "  $0 run               # Build and run"
    echo "  $0 stop              # Stop container"
    echo ""
}

# Stop container
stop_container() {
    if docker ps -q --filter "name=${IMAGE_NAME}" | grep -q .; then
        print_info "Stopping container..."
        docker stop ${IMAGE_NAME}
        print_status "Container stopped"
    else
        print_warning "No running container found"
    fi
}

# Show logs
show_logs() {
    if docker ps -a -q --filter "name=${IMAGE_NAME}" | grep -q .; then
        print_info "Container logs:"
        docker logs ${IMAGE_NAME}
    else
        print_warning "No container found"
    fi
}

# Clean up
cleanup() {
    print_info "Cleaning up containers and images..."
    
    # Stop and remove container
    if docker ps -a -q --filter "name=${IMAGE_NAME}" | grep -q .; then
        docker stop ${IMAGE_NAME} 2>/dev/null || true
        docker rm ${IMAGE_NAME} 2>/dev/null || true
        print_status "Container removed"
    fi
    
    # Remove image
    if docker images -q ${IMAGE_NAME}:${TAG} | grep -q .; then
        docker rmi ${IMAGE_NAME}:${TAG}
        print_status "Image removed"
    fi
}

# Main execution
main() {
    case "$1" in
        "build")
            check_docker
            build_image
            ;;
        "run")
            check_docker
            build_image
            run_container
            print_info "Container is running. Use '$0 test' to test the API."
            ;;
        "test")
            check_docker
            build_image
            run_container
            wait_for_api && test_api
            ;;
        "stop")
            stop_container
            ;;
        "logs")
            show_logs
            ;;
        "clean")
            cleanup
            ;;
        "help"|"--help"|"-h")
            show_usage
            ;;
        "")
            print_warning "No option specified. Use 'help' for usage information."
            show_usage
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
