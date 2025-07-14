#!/bin/bash

# Microservices Deployment Script
set -e

echo "🚀 Starting Microservices Deployment"

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

# Check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18+"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v aws &> /dev/null; then
        print_warning "AWS CLI is not installed. Please install for AWS deployment"
    fi
    
    print_status "All dependencies are installed ✓"
}

# Install all dependencies
install_dependencies() {
    print_status "Installing dependencies for all services..."
    
    # Root dependencies
    npm install
    
    # Backend shared dependencies
    cd backend/shared && npm install && cd ../..
    
    # Auth service dependencies
    cd backend/auth-service && npm install && cd ../..
    
    # User service dependencies
    cd backend/user-service && npm install && cd ../..
    
    # API Gateway dependencies
    cd backend/api-gateway && npm install && cd ../..
    
    # Frontend dependencies
    cd frontend && npm install && cd ..
    
    # Infrastructure dependencies
    cd infrastructure && npm install && cd ..
    
    print_status "All dependencies installed ✓"
}

# Build all services
build_services() {
    print_status "Building all services..."
    
    # Build shared module
    cd backend/shared && npm run build && cd ../..
    
    # Build auth service
    cd backend/auth-service && npm run build && cd ../..
    
    # Build user service
    cd backend/user-service && npm run build && cd ../..
    
    # Build API gateway
    cd backend/api-gateway && npm run build && cd ../..
    
    # Build frontend
    cd frontend && npm run build && cd ..
    
    # Build infrastructure
    cd infrastructure && npm run build && cd ..
    
    print_status "All services built ✓"
}

# Start local development environment
start_local() {
    print_status "Starting local development environment with Docker Compose..."
    
    # Create environment files if they don't exist
    if [ ! -f backend/auth-service/.env ]; then
        cp backend/auth-service/.env.example backend/auth-service/.env
        print_status "Created .env file for auth-service"
    fi
    
    if [ ! -f backend/user-service/.env ]; then
        cp backend/user-service/.env.example backend/user-service/.env
        print_status "Created .env file for user-service"
    fi
    
    if [ ! -f backend/api-gateway/.env ]; then
        cp backend/api-gateway/.env.example backend/api-gateway/.env
        print_status "Created .env file for api-gateway"
    fi
    
    if [ ! -f frontend/.env.local ]; then
        cp frontend/.env.local.example frontend/.env.local
        print_status "Created .env.local file for frontend"
    fi
    
    # Start services with Docker Compose
    docker-compose up -d
    
    print_status "Local environment started ✓"
    print_status "Services available at:"
    echo "  - API Gateway: http://localhost:3000"
    echo "  - Auth Service: http://localhost:3001"
    echo "  - User Service: http://localhost:3002"
    echo "  - Frontend: http://localhost:3003"
    echo "  - PostgreSQL: localhost:5432"
}

# Deploy to AWS
deploy_aws() {
    print_status "Deploying to AWS using CDK..."
    
    if ! command -v cdk &> /dev/null; then
        print_error "AWS CDK is not installed. Install with: npm install -g aws-cdk"
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured. Run 'aws configure'"
        exit 1
    fi
    
    cd infrastructure
    
    # Bootstrap CDK if needed
    print_status "Bootstrapping CDK..."
    cdk bootstrap
    
    # Deploy stacks
    print_status "Deploying infrastructure stacks..."
    cdk deploy --all --require-approval never
    
    cd ..
    
    print_status "AWS deployment completed ✓"
}

# Stop local environment
stop_local() {
    print_status "Stopping local environment..."
    docker-compose down
    print_status "Local environment stopped ✓"
}

# Clean up
clean() {
    print_status "Cleaning up..."
    
    # Remove node_modules
    find . -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null || true
    
    # Remove build directories
    find . -name "dist" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name ".next" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "cdk.out" -type d -exec rm -rf {} + 2>/dev/null || true
    
    # Remove Docker containers and images
    docker-compose down --volumes --remove-orphans 2>/dev/null || true
    
    print_status "Cleanup completed ✓"
}

# Show help
show_help() {
    echo "Microservices Deployment Script"
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  install       Install all dependencies"
    echo "  build         Build all services"
    echo "  dev           Start local development environment"
    echo "  stop          Stop local development environment"
    echo "  deploy        Deploy to AWS using CDK"
    echo "  clean         Clean up build artifacts and dependencies"
    echo "  help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 install    # Install dependencies"
    echo "  $0 dev        # Start local development"
    echo "  $0 deploy     # Deploy to AWS"
}

# Main script logic
case "$1" in
    "install")
        check_dependencies
        install_dependencies
        ;;
    "build")
        check_dependencies
        build_services
        ;;
    "dev")
        check_dependencies
        install_dependencies
        build_services
        start_local
        ;;
    "stop")
        stop_local
        ;;
    "deploy")
        check_dependencies
        install_dependencies
        build_services
        deploy_aws
        ;;
    "clean")
        clean
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
