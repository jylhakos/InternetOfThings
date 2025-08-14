#!/bin/bash

# Flutter SPA Development Setup Script
# This script sets up the development environment and starts all services

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
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

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    local missing_tools=()
    
    # Check Flutter
    if ! command_exists flutter; then
        missing_tools+=("flutter")
    fi
    
    # Check Node.js
    if ! command_exists node; then
        missing_tools+=("node")
    fi
    
    # Check npm
    if ! command_exists npm; then
        missing_tools+=("npm")
    fi
    
    # Check Docker
    if ! command_exists docker; then
        missing_tools+=("docker")
    fi
    
    # Check Docker Compose
    if ! command_exists docker-compose; then
        missing_tools+=("docker-compose")
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        print_error "Missing required tools: ${missing_tools[*]}"
        print_error "Please install them and run this script again."
        exit 1
    fi
    
    print_success "All prerequisites are installed"
}

# Install Flutter dependencies
setup_flutter() {
    print_status "Setting up Flutter..."
    
    # Enable web support
    flutter config --enable-web
    
    # Get dependencies
    flutter pub get
    
    # Generate code (if build_runner is configured)
    if grep -q "build_runner" pubspec.yaml; then
        flutter packages pub run build_runner build --delete-conflicting-outputs
    fi
    
    print_success "Flutter setup completed"
}

# Install Node.js dependencies
setup_backend() {
    print_status "Setting up Node.js backend..."
    
    cd backend
    
    # Install dependencies
    npm install
    
    # Create uploads directory
    mkdir -p uploads
    
    cd ..
    
    print_success "Backend setup completed"
}

# Setup environment variables
setup_environment() {
    print_status "Setting up environment variables..."
    
    # Copy example environment file if .env doesn't exist
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            print_warning "Created .env file from .env.example template"
            print_warning "Please update the values in .env file with your actual configuration"
        else
            print_warning "No .env.example file found"
        fi
    else
        print_status ".env file already exists"
    fi
    
    # Create backend .env file
    if [ ! -f backend/.env ]; then
        cat > backend/.env << EOF
# Backend Environment Variables
NODE_ENV=development
PORT=3000
MONGODB_URI=mongodb://localhost:27017/flutter_spa
JWT_SECRET=your-development-jwt-secret-key
JWT_REFRESH_SECRET=your-development-refresh-secret-key
JWT_EXPIRE=24h
JWT_REFRESH_EXPIRE=7d
ALLOWED_ORIGINS=http://localhost:8080,http://localhost:3000
EOF
        print_success "Created backend/.env file"
    fi
}

# Start MongoDB with Docker
start_mongodb() {
    print_status "Starting MongoDB with Docker..."
    
    # Use the dedicated MongoDB script if available
    if [ -f "./scripts/mongodb-dev.sh" ]; then
        print_status "Using dedicated MongoDB management script..."
        ./scripts/mongodb-dev.sh start
    else
        # Fallback to inline MongoDB setup
        print_status "Using fallback MongoDB setup..."
        
        # Check if MongoDB container is already running
        if docker ps | grep -q flutter-spa-mongodb; then
            print_warning "MongoDB container is already running"
            return
        fi
        
        # Start MongoDB container
        docker run -d \
            --name flutter-spa-mongodb \
            -p 27017:27017 \
            -e MONGO_INITDB_ROOT_USERNAME=admin \
            -e MONGO_INITDB_ROOT_PASSWORD=password \
            -e MONGO_INITDB_DATABASE=flutter_spa \
            -v flutter-spa-mongodb-data:/data/db \
            mongo:7.0
        
        # Wait for MongoDB to be ready
        print_status "Waiting for MongoDB to be ready..."
        sleep 10
        
        print_success "MongoDB started successfully"
    fi
}

# Start all services with Docker Compose
start_with_docker_compose() {
    print_status "Starting all services with Docker Compose..."
    
    # Build and start services
    docker-compose up -d --build
    
    # Wait a bit for services to start
    sleep 5
    
    # Show service status
    docker-compose ps
    
    print_success "All services started with Docker Compose"
    print_status "Access the application at:"
    print_status "  Frontend: http://localhost:8080"
    print_status "  Backend API: http://localhost:3000"
    print_status "  Backend Health: http://localhost:3000/health"
}

# Start services in development mode
start_development() {
    print_status "Starting development servers..."
    
    # Start MongoDB
    start_mongodb
    
    # Start backend in development mode
    print_status "Starting Node.js backend..."
    cd backend
    npm run dev &
    BACKEND_PID=$!
    cd ..
    
    # Wait a bit for backend to start
    sleep 3
    
    # Start Flutter web development server
    print_status "Starting Flutter web development server..."
    flutter run -d web-server --web-port=8080 --web-hostname=0.0.0.0 &
    FLUTTER_PID=$!
    
    # Store PIDs for cleanup
    echo $BACKEND_PID > .dev-pids
    echo $FLUTTER_PID >> .dev-pids
    
    print_success "Development servers started"
    print_status "Access the application at:"
    print_status "  Frontend: http://localhost:8080"
    print_status "  Backend API: http://localhost:3000"
    print_status "  Backend Health: http://localhost:3000/health"
    
    # Wait for user input to stop
    echo ""
    print_status "Press Ctrl+C to stop all services"
    
    # Trap SIGINT to cleanup
    trap 'stop_development' SIGINT
    
    # Wait for background processes
    wait
}

# Stop development services
stop_development() {
    print_status "Stopping development servers..."
    
    # Kill background processes
    if [ -f .dev-pids ]; then
        while read pid; do
            if kill -0 $pid 2>/dev/null; then
                kill $pid
            fi
        done < .dev-pids
        rm .dev-pids
    fi
    
    # Stop MongoDB container
    docker stop flutter-spa-mongodb || true
    docker rm flutter-spa-mongodb || true
    
    print_success "Development servers stopped"
    exit 0
}

# Stop Docker Compose services
stop_docker_compose() {
    print_status "Stopping Docker Compose services..."
    docker-compose down
    print_success "All services stopped"
}

# Run tests
run_tests() {
    print_status "Running tests..."
    
    # Backend tests
    if [ -d "backend" ]; then
        print_status "Running backend tests..."
        cd backend
        if [ -f "package.json" ] && grep -q '"test"' package.json; then
            npm test
        else
            print_warning "No backend tests configured"
        fi
        cd ..
    fi
    
    # Flutter tests
    print_status "Running Flutter tests..."
    flutter test
    
    # API integration tests
    if [ -f "scripts/test-api.sh" ]; then
        print_status "Running API integration tests..."
        ./scripts/test-api.sh basic
    fi
    
    print_success "All tests completed"
}

# Clean up development environment
cleanup() {
    print_status "Cleaning up development environment..."
    
    # Stop all services
    stop_development
    stop_docker_compose
    
    # Clean Flutter build cache
    flutter clean
    flutter pub get
    
    # Clean Node.js modules (optional)
    if [ "$1" = "deep" ]; then
        print_status "Deep cleaning - removing node_modules..."
        rm -rf backend/node_modules
        cd backend && npm install && cd ..
    fi
    
    # Clean Docker resources
    docker system prune -f
    
    print_success "Cleanup completed"
}

# Show help
show_help() {
    echo "Flutter SPA Development Setup Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup          Setup development environment (default)"
    echo "  start          Start development servers"
    echo "  docker         Start all services with Docker Compose"
    echo "  stop           Stop development servers"
    echo "  stop-docker    Stop Docker Compose services"
    echo "  test           Run all tests"
    echo "  clean          Clean up development environment"
    echo "  clean-deep     Deep clean including node_modules"
    echo "  help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Setup and start development environment"
    echo "  $0 start        # Start development servers"
    echo "  $0 docker       # Start with Docker Compose"
    echo "  $0 test         # Run all tests"
    echo "  $0 clean        # Clean up environment"
}

# Main execution
main() {
    case ${1:-setup} in
        "setup")
            check_prerequisites
            setup_environment
            setup_flutter
            setup_backend
            print_success "Development environment setup completed"
            print_status "Run '$0 start' to start development servers"
            ;;
        "start")
            check_prerequisites
            start_development
            ;;
        "docker")
            check_prerequisites
            start_with_docker_compose
            ;;
        "stop")
            stop_development
            ;;
        "stop-docker")
            stop_docker_compose
            ;;
        "test")
            run_tests
            ;;
        "clean")
            cleanup
            ;;
        "clean-deep")
            cleanup deep
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
