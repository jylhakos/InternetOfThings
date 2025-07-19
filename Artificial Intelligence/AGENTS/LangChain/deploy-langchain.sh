#!/bin/bash

# JavaScript/LangChain.js AI Agent Deployment Script
# Prioritized deployment for production environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 LangChain.js AI Agent Deployment${NC}"
echo -e "${BLUE}=================================${NC}"
echo -e "${GREEN}🥇 PRIORITIZED JavaScript Implementation${NC}"
echo ""

# Default configuration
MODE=${1:-"docker"}
FORCE_SETUP=${2:-"false"}

show_help() {
    echo "Usage: $0 [MODE] [FORCE]"
    echo ""
    echo "Modes:"
    echo "  docker      Deploy with Docker (default, recommended)"
    echo "  native      Deploy natively with Node.js"
    echo "  production  Full production setup with monitoring"
    echo "  test        Deploy and run tests"
    echo "  status      Show service status"
    echo "  stop        Stop all services"
    echo "  clean       Clean up containers and data"
    echo "  help        Show this help"
    echo ""
    echo "Force Setup:"
    echo "  true        Force fresh installation"
    echo "  false       Use existing setup (default)"
    echo ""
    echo "Examples:"
    echo "  $0                     # Docker deployment (recommended)"
    echo "  $0 native              # Native Node.js deployment"
    echo "  $0 production          # Full production stack"
    echo "  $0 docker true         # Force fresh Docker setup"
}

case $MODE in
    help|--help|-h)
        show_help
        exit 0
        ;;
esac

# Check prerequisites
check_prerequisites() {
    echo -e "${BLUE}🔍 Checking prerequisites...${NC}"
    
    case $MODE in
        docker|production)
            if ! command -v docker &> /dev/null; then
                echo -e "${RED}❌ Docker not found${NC}"
                exit 1
            fi
            echo -e "${GREEN}✅ Docker available${NC}"
            ;;
        native|test)
            if ! command -v node &> /dev/null; then
                echo -e "${RED}❌ Node.js not found${NC}"
                exit 1
            fi
            NODE_VERSION=$(node -v)
            echo -e "${GREEN}✅ Node.js $NODE_VERSION available${NC}"
            ;;
    esac
}

# Setup Ollama
setup_ollama() {
    echo -e "${BLUE}🧠 Setting up Ollama...${NC}"
    
    if ! command -v ollama &> /dev/null; then
        echo -e "${YELLOW}📥 Installing Ollama...${NC}"
        curl -fsSL https://ollama.com/install.sh | sh
    fi
    
    # Start Ollama if not running
    if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${BLUE}🔄 Starting Ollama...${NC}"
        ollama serve > /dev/null 2>&1 &
        
        # Wait for Ollama to start
        for i in {1..30}; do
            if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
                break
            fi
            sleep 1
            echo -n "."
        done
        echo ""
    fi
    
    echo -e "${BLUE}📥 Ensuring model is available...${NC}"
    ollama pull llama3.1:8b-instruct-q4_0
    echo -e "${GREEN}✅ Ollama ready${NC}"
}

# Docker deployment
deploy_docker() {
    echo -e "${BLUE}🐳 Docker deployment${NC}"
    
    if [[ $FORCE_SETUP == "true" ]]; then
        echo -e "${YELLOW}🧹 Cleaning existing containers...${NC}"
        docker-compose -f docker-compose.langchain.yml down --volumes || true
    fi
    
    echo -e "${BLUE}🚀 Starting services...${NC}"
    docker-compose -f docker-compose.langchain.yml up -d
    
    echo -e "${BLUE}⏳ Waiting for services...${NC}"
    sleep 10
    
    # Health checks
    check_service_health
}

# Native deployment  
deploy_native() {
    echo -e "${BLUE}📦 Native deployment${NC}"
    
    # Setup dependencies
    if [[ ! -d "node_modules" ]] || [[ $FORCE_SETUP == "true" ]]; then
        echo -e "${BLUE}📥 Installing dependencies...${NC}"
        npm install
    fi
    
    # Setup Ollama
    setup_ollama
    
    echo -e "${BLUE}🚀 Starting AI Agent...${NC}"
    npm start &
    
    # Wait for service
    echo -e "${BLUE}⏳ Waiting for service to start...${NC}"
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            break
        fi
        sleep 1
        echo -n "."
    done
    echo ""
    
    check_service_health
}

# Production deployment
deploy_production() {
    echo -e "${BLUE}🏢 Production deployment with monitoring${NC}"
    
    if [[ $FORCE_SETUP == "true" ]]; then
        echo -e "${YELLOW}🧹 Cleaning existing setup...${NC}"
        docker-compose -f docker-compose.langchain.yml down --volumes || true
    fi
    
    echo -e "${BLUE}🚀 Starting production stack...${NC}"
    # Include monitoring stack if available
    if [[ -f "monitoring/docker-compose.monitoring.yml" ]]; then
        docker-compose -f docker-compose.langchain.yml -f monitoring/docker-compose.monitoring.yml up -d
    else
        docker-compose -f docker-compose.langchain.yml up -d
    fi
    
    echo -e "${BLUE}⏳ Waiting for production stack...${NC}"
    sleep 15
    
    check_service_health
    show_production_endpoints
}

# Health checks
check_service_health() {
    echo -e "${BLUE}🏥 Checking service health...${NC}"
    
    # AI Agent health
    if curl -s http://localhost:8000/health | grep -q "healthy\|status"; then
        echo -e "${GREEN}✅ AI Agent is healthy${NC}"
    else
        echo -e "${RED}❌ AI Agent health check failed${NC}"
        return 1
    fi
    
    # Ollama health
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Ollama is healthy${NC}"
    else
        echo -e "${YELLOW}⚠️  Ollama may not be ready${NC}"
    fi
    
    # Open WebUI (if running)
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Open WebUI is healthy${NC}"
    fi
}

# Run tests
run_tests() {
    echo -e "${BLUE}🧪 Running deployment tests...${NC}"
    
    # Ensure service is ready
    deploy_native
    
    echo -e "${BLUE}📋 Running test suite...${NC}"
    npm test
    
    echo -e "${BLUE}🎯 Running demo...${NC}"
    timeout 60 npm run demo || true
    
    echo -e "${GREEN}✅ Tests completed${NC}"
}

# Show service status
show_status() {
    echo -e "${BLUE}📊 Service Status${NC}"
    echo "=================="
    
    # AI Agent
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "AI Agent (JS):  ${GREEN}✅ Running${NC} - http://localhost:8000"
    else
        echo -e "AI Agent (JS):  ${RED}❌ Not running${NC}"
    fi
    
    # Ollama
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "Ollama LLM:     ${GREEN}✅ Running${NC} - http://localhost:11434"
    else
        echo -e "Ollama LLM:     ${RED}❌ Not running${NC}"
    fi
    
    # Open WebUI
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "Open WebUI:     ${GREEN}✅ Running${NC} - http://localhost:3000"
    else
        echo -e "Open WebUI:     ${YELLOW}⚠️  Not running${NC}"
    fi
    
    # Docker containers (if applicable)
    if command -v docker &> /dev/null; then
        echo ""
        echo -e "${BLUE}🐳 Docker Containers:${NC}"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" --filter "name=langchain\|ollama\|webui" 2>/dev/null || echo "No containers found"
    fi
}

# Stop services
stop_services() {
    echo -e "${YELLOW}🛑 Stopping services...${NC}"
    
    # Docker services
    docker-compose -f docker-compose.langchain.yml down 2>/dev/null || true
    
    # Native processes
    pkill -f "node src/index.js" 2>/dev/null || true
    pkill -f "ollama serve" 2>/dev/null || true
    
    echo -e "${GREEN}✅ Services stopped${NC}"
}

# Clean up
clean_up() {
    echo -e "${YELLOW}🧹 Cleaning up...${NC}"
    
    stop_services
    
    # Remove Docker volumes
    docker-compose -f docker-compose.langchain.yml down --volumes --remove-orphans 2>/dev/null || true
    
    # Clean Docker images (optional)
    read -p "Remove Docker images? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker rmi ai-agent-langchain-js 2>/dev/null || true
        echo -e "${GREEN}✅ Docker images removed${NC}"
    fi
    
    echo -e "${GREEN}✅ Cleanup completed${NC}"
}

# Show production endpoints
show_production_endpoints() {
    echo -e "${GREEN}🎉 Production Deployment Complete!${NC}"
    echo "=================================="
    echo ""
    echo -e "${GREEN}🔗 Service Endpoints:${NC}"
    echo -e "  🤖 AI Agent API:    http://localhost:8000"
    echo -e "  📊 Health Check:    http://localhost:8000/health"
    echo -e "  💬 Chat API:        http://localhost:8000/v1/chat/completions"
    echo -e "  🧠 Ollama API:      http://localhost:11434"
    echo -e "  🌐 Open WebUI:      http://localhost:3000"
    echo ""
    echo -e "${BLUE}🛠️  Quick Test:${NC}"
    echo 'curl -X POST http://localhost:8000/v1/chat/completions \'
    echo '  -H "Content-Type: application/json" \'
    echo '  -d '\''{"messages":[{"role":"user","content":"Hello!"}]}'\'''
    echo ""
    echo -e "${GREEN}🎯 Ready for production use!${NC}"
}

# Main execution
main() {
    check_prerequisites
    
    case $MODE in
        docker)
            deploy_docker
            show_production_endpoints
            ;;
        native)
            deploy_native
            show_production_endpoints
            ;;
        production)
            deploy_production
            ;;
        test)
            run_tests
            ;;
        status)
            show_status
            ;;
        stop)
            stop_services
            ;;
        clean)
            clean_up
            ;;
        *)
            echo -e "${RED}❌ Unknown mode: $MODE${NC}"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main
