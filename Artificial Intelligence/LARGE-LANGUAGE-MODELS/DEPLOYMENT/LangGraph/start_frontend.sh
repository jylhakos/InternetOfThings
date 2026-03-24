#!/bin/bash

# Frontend Development Server Starter
# Usage: ./start_frontend.sh [options]

set -e

FRONTEND_DIR="frontend"
DEFAULT_PORT=3000
DEFAULT_HOST="0.0.0.0"
NODE_VERSION_REQUIRED="16"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

show_help() {
    echo "Frontend Development Server Starter"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --port PORT     Set custom port (default: 3000)"
    echo "  --host HOST     Set custom host (default: 0.0.0.0)"
    echo "  --build         Build for production instead of dev"
    echo "  --preview       Preview production build"
    echo "  --install       Install dependencies only"
    echo "  --help          Show this help"
    echo ""
    echo "Examples:"
    echo "  $0                    # Start dev server on default port"
    echo "  $0 --port 3001       # Start on custom port"
    echo "  $0 --build           # Build for production"
    echo "  $0 --preview         # Preview production build"
}

check_node() {
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js is not installed${NC}"
        echo "Please install Node.js version $NODE_VERSION_REQUIRED or higher"
        echo "Visit: https://nodejs.org/"
        exit 1
    fi
    
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt "$NODE_VERSION_REQUIRED" ]; then
        echo -e "${RED}❌ Node.js version $NODE_VERSION_REQUIRED or higher required${NC}"
        echo "Current version: $(node --version)"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Node.js $(node --version) detected${NC}"
}

check_frontend_dir() {
    if [ ! -d "$FRONTEND_DIR" ]; then
        echo -e "${RED}❌ Frontend directory not found: $FRONTEND_DIR${NC}"
        exit 1
    fi
    
    if [ ! -f "$FRONTEND_DIR/package.json" ]; then
        echo -e "${RED}❌ package.json not found in $FRONTEND_DIR${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Frontend directory found${NC}"
}

install_dependencies() {
    echo -e "${BLUE}📦 Installing Node.js dependencies...${NC}"
    cd "$FRONTEND_DIR"
    
    if [ -f "package-lock.json" ]; then
        npm ci
    else
        npm install
    fi
    
    echo -e "${GREEN}✅ Dependencies installed${NC}"
    cd ..
}

check_backend_connection() {
    echo -e "${BLUE}🔍 Checking backend connection...${NC}"
    
    BACKEND_URL="http://localhost:8000"
    if curl -s "$BACKEND_URL/health" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is running at $BACKEND_URL${NC}"
    else
        echo -e "${YELLOW}⚠️  Backend not detected at $BACKEND_URL${NC}"
        echo "   Frontend will start but API calls may fail"
        echo "   Start backend with: uvicorn app.main:app --reload"
    fi
}

start_dev_server() {
    local port=${1:-$DEFAULT_PORT}
    local host=${2:-$DEFAULT_HOST}
    
    echo -e "${BLUE}🚀 Starting Frontend Development Server...${NC}"
    echo "   Technology: Node.js + Vite + React"
    echo "   Port: $port"
    echo "   Host: $host"
    echo "   Hot Reload: Enabled"
    echo ""
    
    cd "$FRONTEND_DIR"
    
    # Set environment variables
    export VITE_API_BASE_URL="http://localhost:8000"
    export VITE_DEV_HOST="$host"
    export VITE_DEV_PORT="$port"
    
    echo -e "${GREEN}🌐 Frontend will be available at: http://localhost:$port${NC}"
    echo -e "${BLUE}📡 API calls will go to: $VITE_API_BASE_URL${NC}"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    # Start Vite dev server
    npx vite --host "$host" --port "$port"
}

build_production() {
    echo -e "${BLUE}🏗️  Building for production...${NC}"
    cd "$FRONTEND_DIR"
    
    export VITE_API_BASE_URL="http://localhost:8000"
    
    npm run build
    
    echo -e "${GREEN}✅ Production build complete${NC}"
    echo "   Build output: $FRONTEND_DIR/dist/"
    echo "   To serve: npm run preview"
}

preview_production() {
    echo -e "${BLUE}👁️  Starting production preview...${NC}"
    cd "$FRONTEND_DIR"
    
    if [ ! -d "dist" ]; then
        echo -e "${YELLOW}⚠️  No production build found. Building first...${NC}"
        build_production
    fi
    
    echo -e "${GREEN}🌐 Production preview at: http://localhost:4173${NC}"
    npm run preview
}

# Parse command line arguments
PORT=$DEFAULT_PORT
HOST=$DEFAULT_HOST
ACTION="dev"

while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --build)
            ACTION="build"
            shift
            ;;
        --preview)
            ACTION="preview"
            shift
            ;;
        --install)
            ACTION="install"
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Main execution
echo -e "${BLUE}🎯 LangGraph RAG System - Frontend Server${NC}"
echo "=========================================="

check_node
check_frontend_dir

case $ACTION in
    "install")
        install_dependencies
        echo -e "${GREEN}✅ Installation complete${NC}"
        ;;
    "build")
        install_dependencies
        build_production
        ;;
    "preview")
        preview_production
        ;;
    "dev")
        install_dependencies
        check_backend_connection
        start_dev_server "$PORT" "$HOST"
        ;;
esac
