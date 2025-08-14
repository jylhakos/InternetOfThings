#!/bin/bash

# Development Workflow Script for Vite + React + ASP.NET Core
# This script demonstrates various development scenarios

set -e

echo "🔧 Vite + React + ASP.NET Core Development Workflow"
echo "==================================================="

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

# Check if we're in the right directory
if [[ ! -f "vite.config.ts" && ! -f "../Server/Program.cs" ]]; then
    print_error "This script should be run from the Client directory of a Vite+React+ASP.NET project"
    exit 1
fi

# Function to check if port is available
check_port() {
    local port=$1
    if netstat -tuln | grep -q ":$port "; then
        return 1  # Port is in use
    else
        return 0  # Port is available
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    print_info "Waiting for $service_name to be ready at $url..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            print_status "$service_name is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name failed to start within $((max_attempts * 2)) seconds"
    return 1
}

# Function to start backend
start_backend() {
    print_info "Starting ASP.NET Core backend..."
    
    if [[ ! -d "../Server" ]]; then
        print_error "Server directory not found. Make sure you're in the correct project structure."
        return 1
    fi
    
    cd ../Server
    
    # Check if backend is already running
    if check_port 7042; then
        print_info "Starting backend on https://localhost:7042"
        dotnet run &
        BACKEND_PID=$!
        
        # Wait for backend to be ready
        if wait_for_service "https://localhost:7042/health" "ASP.NET Core Backend"; then
            print_status "Backend started successfully (PID: $BACKEND_PID)"
        else
            print_warning "Backend may not be fully ready, but continuing..."
        fi
    else
        print_warning "Port 7042 is already in use. Backend may already be running."
    fi
    
    cd ../Client
}

# Function to start frontend
start_frontend() {
    print_info "Starting Vite React frontend..."
    
    # Check if frontend is already running
    if check_port 5173; then
        print_info "Installing dependencies if needed..."
        if [[ ! -d "node_modules" ]]; then
            npm install
        fi
        
        print_info "Starting frontend on http://localhost:5173"
        npm run dev &
        FRONTEND_PID=$!
        
        # Wait for frontend to be ready
        if wait_for_service "http://localhost:5173" "Vite Dev Server"; then
            print_status "Frontend started successfully (PID: $FRONTEND_PID)"
        else
            print_warning "Frontend may not be fully ready, but continuing..."
        fi
    else
        print_warning "Port 5173 is already in use. Frontend may already be running."
    fi
}

# Function to run development mode
run_dev() {
    print_info "🚀 Starting development environment..."
    
    # Create a process group for cleanup
    trap cleanup EXIT
    
    start_backend
    sleep 3  # Give backend time to start
    start_frontend
    
    print_status "Development environment is ready!"
    echo ""
    print_info "📝 Available URLs:"
    echo "   🔗 Frontend (React): http://localhost:5173"
    echo "   🔗 Backend API:      https://localhost:7042"
    echo "   🔗 Swagger UI:       https://localhost:7042/swagger"
    echo "   🔗 Health Check:     https://localhost:7042/health"
    echo ""
    print_info "Press Ctrl+C to stop all services"
    
    # Wait for user to stop
    wait
}

# Function to build for production
build_production() {
    print_info "🏗️  Building for production..."
    
    # Build React app
    print_info "Building React application with Vite..."
    npm run build
    
    if [[ $? -eq 0 ]]; then
        print_status "React build completed successfully"
        print_info "Build output is in the 'dist' directory"
        
        # Show build info
        echo ""
        print_info "📊 Build Statistics:"
        du -sh dist/
        find dist/ -type f -name "*.js" -o -name "*.css" | head -10
        
        # Build backend
        print_info "Building ASP.NET Core application..."
        cd ../Server
        dotnet build -c Release
        
        if [[ $? -eq 0 ]]; then
            print_status "Backend build completed successfully"
        else
            print_error "Backend build failed"
            return 1
        fi
        
        cd ../Client
    else
        print_error "React build failed"
        return 1
    fi
}

# Function to test the application
test_application() {
    print_info "🧪 Testing application endpoints..."
    
    # Test backend health
    print_info "Testing backend health endpoint..."
    if curl -s -f "https://localhost:7042/health" > /dev/null; then
        print_status "Backend health check passed"
    else
        print_error "Backend health check failed"
    fi
    
    # Test API endpoint
    print_info "Testing weather API endpoint..."
    if curl -s -f "https://localhost:7042/api/weatherforecast" > /dev/null; then
        print_status "Weather API endpoint is working"
    else
        print_error "Weather API endpoint failed"
    fi
    
    # Test frontend
    print_info "Testing frontend..."
    if curl -s -f "http://localhost:5173" > /dev/null; then
        print_status "Frontend is accessible"
    else
        print_error "Frontend is not accessible"
    fi
}

# Function to cleanup processes
cleanup() {
    print_info "🧹 Cleaning up processes..."
    
    if [[ -n "$BACKEND_PID" ]]; then
        kill $BACKEND_PID 2>/dev/null || true
        print_info "Stopped backend process"
    fi
    
    if [[ -n "$FRONTEND_PID" ]]; then
        kill $FRONTEND_PID 2>/dev/null || true
        print_info "Stopped frontend process"
    fi
    
    # Kill any remaining processes on our ports
    pkill -f "dotnet run" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    
    print_status "Cleanup completed"
}

# Function to show project info
show_info() {
    print_info "📋 Project Information"
    echo ""
    echo "Project Structure:"
    tree -I 'node_modules|bin|obj|dist' ../. 2>/dev/null || find ../. -type d -name node_modules -prune -o -type d -name bin -prune -o -type d -name obj -prune -o -type d -name dist -prune -o -type f -print | head -20
    
    echo ""
    echo "Package Versions:"
    echo "Node.js: $(node --version 2>/dev/null || echo 'Not found')"
    echo "npm: $(npm --version 2>/dev/null || echo 'Not found')"
    echo ".NET: $(cd ../Server && dotnet --version 2>/dev/null || echo 'Not found')"
    
    echo ""
    echo "Development Ports:"
    echo "Frontend: http://localhost:5173"
    echo "Backend:  https://localhost:7042"
}

# Function to open URLs in browser
open_browser() {
    print_info "🌐 Opening application in browser..."
    
    # Detect OS and open browser accordingly
    if command -v xdg-open > /dev/null; then
        xdg-open "http://localhost:5173"
    elif command -v open > /dev/null; then
        open "http://localhost:5173"
    elif command -v start > /dev/null; then
        start "http://localhost:5173"
    else
        print_warning "Could not detect how to open browser. Please manually visit: http://localhost:5173"
    fi
}

# Main menu
show_menu() {
    echo ""
    echo "Choose an action:"
    echo "1) 🚀 Start Development Environment"
    echo "2) 🏗️  Build for Production" 
    echo "3) 🧪 Test Application"
    echo "4) 📋 Show Project Info"
    echo "5) 🌐 Open Browser"
    echo "6) 🧹 Cleanup Processes"
    echo "7) ❌ Exit"
    echo ""
}

# Main script logic
main() {
    if [[ $# -eq 0 ]]; then
        # Interactive mode
        while true; do
            show_menu
            read -p "Enter your choice (1-7): " choice
            
            case $choice in
                1) run_dev ;;
                2) build_production ;;
                3) test_application ;;
                4) show_info ;;
                5) open_browser ;;
                6) cleanup ;;
                7) 
                    print_info "Goodbye!"
                    cleanup
                    exit 0
                    ;;
                *)
                    print_warning "Invalid option. Please choose 1-7."
                    ;;
            esac
        done
    else
        # Command line mode
        case $1 in
            "dev"|"start")
                run_dev
                ;;
            "build")
                build_production
                ;;
            "test")
                test_application
                ;;
            "info")
                show_info
                ;;
            "open")
                open_browser
                ;;
            "clean"|"cleanup")
                cleanup
                ;;
            "help"|"--help"|"-h")
                echo "Usage: $0 [dev|build|test|info|open|clean]"
                echo ""
                echo "Commands:"
                echo "  dev     - Start development environment"
                echo "  build   - Build for production"
                echo "  test    - Test application endpoints"
                echo "  info    - Show project information"
                echo "  open    - Open browser"
                echo "  clean   - Cleanup processes"
                ;;
            *)
                print_error "Unknown command: $1"
                print_info "Use '$0 help' for available commands"
                exit 1
                ;;
        esac
    fi
}

# Run main function
main "$@"
