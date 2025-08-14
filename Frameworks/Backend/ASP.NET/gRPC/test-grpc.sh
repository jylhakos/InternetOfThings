#!/bin/bash

# gRPC Service Test Script
# Tests the gRPC Greeter Service and Client

set -e

echo "🧪 gRPC Service Test Script"
echo "=========================="

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GRPC_DIR="$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command_exists dotnet; then
        print_error ".NET SDK is not installed. Please install .NET 8.0 SDK."
        exit 1
    fi
    
    print_success ".NET SDK is available: $(dotnet --version)"
}

# Build the gRPC service
build_service() {
    print_status "Building gRPC Greeter Service..."
    cd "$GRPC_DIR/GrpcGreeterService"
    
    if dotnet build --configuration Release; then
        print_success "gRPC Service built successfully"
    else
        print_error "Failed to build gRPC Service"
        exit 1
    fi
}

# Build the gRPC client
build_client() {
    print_status "Building gRPC Greeter Client..."
    cd "$GRPC_DIR/GrpcGreeterClient"
    
    if dotnet build --configuration Release; then
        print_success "gRPC Client built successfully"
    else
        print_error "Failed to build gRPC Client"
        exit 1
    fi
}

# Start the gRPC service in background
start_service() {
    print_status "Starting gRPC Greeter Service..."
    cd "$GRPC_DIR/GrpcGreeterService"
    
    # Start service in background
    dotnet run --configuration Release --urls="https://localhost:7042" > /tmp/grpc_service.log 2>&1 &
    SERVICE_PID=$!
    
    # Wait a moment for service to start
    sleep 3
    
    # Check if service is still running
    if kill -0 $SERVICE_PID 2>/dev/null; then
        print_success "gRPC Service started (PID: $SERVICE_PID)"
        return 0
    else
        print_error "Failed to start gRPC Service"
        cat /tmp/grpc_service.log
        exit 1
    fi
}

# Test the gRPC client
test_client() {
    print_status "Testing gRPC Client..."
    cd "$GRPC_DIR/GrpcGreeterClient"
    
    # Give service a moment to fully initialize
    sleep 2
    
    if timeout 30s dotnet run --configuration Release; then
        print_success "gRPC Client test completed successfully"
    else
        print_error "gRPC Client test failed"
        print_warning "Service logs:"
        cat /tmp/grpc_service.log
        return 1
    fi
}

# Stop the gRPC service
stop_service() {
    if [ ! -z "$SERVICE_PID" ] && kill -0 $SERVICE_PID 2>/dev/null; then
        print_status "Stopping gRPC Service (PID: $SERVICE_PID)..."
        kill $SERVICE_PID
        wait $SERVICE_PID 2>/dev/null || true
        print_success "gRPC Service stopped"
    fi
}

# Cleanup function
cleanup() {
    stop_service
    rm -f /tmp/grpc_service.log
}

# Set trap for cleanup on script exit
trap cleanup EXIT INT TERM

# Main execution
main() {
    print_status "Starting gRPC Service and Client Test"
    echo
    
    check_prerequisites
    echo
    
    build_service
    echo
    
    build_client
    echo
    
    start_service
    echo
    
    if test_client; then
        echo
        print_success "✅ All gRPC tests passed!"
        echo
        print_status "🎯 Service is running at: https://localhost:7042"
        print_status "📝 You can now test manually with grpcurl:"
        echo "   grpcurl -plaintext -d '{\"name\":\"World\",\"message\":\"Hello\"}' localhost:7042 greet.Greeter/SayHello"
        echo
    else
        echo
        print_error "❌ gRPC tests failed!"
        exit 1
    fi
}

# Show usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -q, --quiet    Suppress verbose output"
    echo ""
    echo "Examples:"
    echo "  $0             Run full gRPC test suite"
    echo "  $0 --quiet     Run tests with minimal output"
    echo ""
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -q|--quiet)
            # Redirect output for quiet mode
            exec > /dev/null 2>&1
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Run main function
main
