#!/bin/bash

# Quick Start Script for Testing Contact Management API
# This script builds, runs, and tests the API

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 Contact Management API - Quick Start${NC}"
echo "======================================="

PROJECT_DIR="/home/laptop/EXERCISES/IOT/InternetOfThings/Frameworks/Backend/ASP.NET/examples/ViteReactASP"
SERVER_DIR="$PROJECT_DIR/Server"

# Function to check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}📋 Checking prerequisites...${NC}"
    
    if ! command -v dotnet &> /dev/null; then
        echo -e "${RED}❌ .NET SDK not found${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ .NET SDK: $(dotnet --version)${NC}"
}

# Function to restore and build
build_project() {
    echo -e "${YELLOW}🔨 Building project...${NC}"
    
    cd "$SERVER_DIR"
    
    # Restore packages
    dotnet restore
    
    # Build project
    dotnet build
    
    echo -e "${GREEN}✅ Build completed${NC}"
}

# Function to run the server in background
start_server() {
    echo -e "${YELLOW}🖥️  Starting server...${NC}"
    
    cd "$SERVER_DIR"
    
    # Kill any existing process on port 7042
    pkill -f "dotnet.*ViteReactASP" 2>/dev/null || true
    
    # Start server in background
    nohup dotnet run > server.log 2>&1 &
    SERVER_PID=$!
    
    echo "Server PID: $SERVER_PID"
    
    # Wait for server to start
    echo "Waiting for server to start..."
    for i in {1..30}; do
        if curl -k -s -f "https://localhost:7042/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Server is running on https://localhost:7042${NC}"
            return 0
        fi
        sleep 2
        echo -n "."
    done
    
    echo -e "${RED}❌ Server failed to start${NC}"
    return 1
}

# Function to run tests
run_tests() {
    echo -e "${YELLOW}🧪 Running API tests...${NC}"
    
    cd "$PROJECT_DIR"
    
    # Run comprehensive tests
    ./test-contacts-api.sh
}

# Function to run load tests
run_load_tests() {
    echo -e "${YELLOW}⚡ Running load tests...${NC}"
    
    cd "$PROJECT_DIR"
    
    # Run load tests
    ./load-test-api.sh 50 5 20
}

# Function to show server info
show_info() {
    echo -e "${BLUE}📋 Server Information${NC}"
    echo "================================"
    echo "🔗 API Base URL: https://localhost:7042"
    echo "📚 Swagger UI: https://localhost:7042/swagger"
    echo "❤️  Health Check: https://localhost:7042/health"
    echo "📊 Statistics: https://localhost:7042/api/contacts/stats"
    echo ""
    echo "📖 Available Endpoints:"
    echo "  GET    /api/contacts         - List all contacts"
    echo "  GET    /api/contacts/{id}    - Get contact by ID"
    echo "  POST   /api/contacts         - Create new contact"
    echo "  PUT    /api/contacts/{id}    - Update contact"
    echo "  DELETE /api/contacts/{id}    - Delete contact"
    echo "  GET    /api/contacts/search/{term} - Search contacts"
    echo "  POST   /api/contacts/bulk    - Bulk create contacts"
    echo "  GET    /api/contacts/stats   - Get statistics"
    echo "  DELETE /api/contacts/cache   - Clear cache"
    echo ""
    echo "🔧 Features:"
    echo "  ✅ SQLite Database with Entity Framework"
    echo "  ✅ Memory Caching with invalidation"
    echo "  ✅ Database transactions for CRUD operations"
    echo "  ✅ Soft delete functionality"
    echo "  ✅ Bulk operations support"
    echo "  ✅ Advanced search capabilities"
    echo "  ✅ Comprehensive error handling"
    echo "  ✅ API documentation with Swagger"
}

# Function to stop server
stop_server() {
    echo -e "${YELLOW}🛑 Stopping server...${NC}"
    
    if [[ -n "$SERVER_PID" ]]; then
        kill $SERVER_PID 2>/dev/null || true
    fi
    
    pkill -f "dotnet.*ViteReactASP" 2>/dev/null || true
    
    echo -e "${GREEN}✅ Server stopped${NC}"
}

# Function to cleanup
cleanup() {
    stop_server
    exit 0
}

# Trap cleanup on exit
trap cleanup EXIT INT TERM

# Main menu
show_menu() {
    echo ""
    echo "Choose an action:"
    echo "1) 🚀 Quick Start (Build + Run + Test)"
    echo "2) 🔨 Build Only"
    echo "3) 🖥️  Start Server Only"
    echo "4) 🧪 Run Tests Only"
    echo "5) ⚡ Run Load Tests"
    echo "6) 📋 Show Server Info"
    echo "7) 🌐 Open Swagger UI"
    echo "8) 🛑 Stop Server"
    echo "9) ❌ Exit"
    echo ""
}

# Function to open browser
open_browser() {
    echo -e "${YELLOW}🌐 Opening Swagger UI...${NC}"
    
    if command -v xdg-open > /dev/null; then
        xdg-open "https://localhost:7042/swagger"
    elif command -v open > /dev/null; then
        open "https://localhost:7042/swagger"
    else
        echo "Please manually visit: https://localhost:7042/swagger"
    fi
}

# Main function
main() {
    check_prerequisites
    
    if [[ $# -eq 0 ]]; then
        # Interactive mode
        show_info
        
        while true; do
            show_menu
            read -p "Enter your choice (1-9): " choice
            
            case $choice in
                1)
                    build_project
                    start_server
                    sleep 3
                    run_tests
                    ;;
                2)
                    build_project
                    ;;
                3)
                    start_server
                    echo "Server is running. Press Ctrl+C to stop."
                    sleep infinity
                    ;;
                4)
                    run_tests
                    ;;
                5)
                    run_load_tests
                    ;;
                6)
                    show_info
                    ;;
                7)
                    open_browser
                    ;;
                8)
                    stop_server
                    ;;
                9)
                    echo -e "${GREEN}Goodbye!${NC}"
                    exit 0
                    ;;
                *)
                    echo -e "${RED}Invalid option. Please choose 1-9.${NC}"
                    ;;
            esac
        done
    else
        # Command line mode
        case $1 in
            "quick"|"start")
                build_project
                start_server
                sleep 3
                run_tests
                ;;
            "build")
                build_project
                ;;
            "run"|"server")
                start_server
                echo "Server is running. Press Ctrl+C to stop."
                sleep infinity
                ;;
            "test")
                run_tests
                ;;
            "load")
                run_load_tests
                ;;
            "info")
                show_info
                ;;
            "stop")
                stop_server
                ;;
            *)
                echo "Usage: $0 [quick|build|run|test|load|info|stop]"
                echo ""
                echo "Commands:"
                echo "  quick - Build, run server, and run tests"
                echo "  build - Build the project"
                echo "  run   - Start the server"
                echo "  test  - Run API tests"
                echo "  load  - Run load tests"
                echo "  info  - Show server information"
                echo "  stop  - Stop the server"
                ;;
        esac
    fi
}

# Run main function
main "$@"
