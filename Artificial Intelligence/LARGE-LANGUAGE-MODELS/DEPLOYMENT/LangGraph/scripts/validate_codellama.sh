#!/bin/bash

# CodeLlama Configuration Validation Script
# Usage: ./scripts/validate_codellama.sh

set -e

echo "🔍 CodeLlama Configuration Validation"
echo "===================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "success")
            echo -e "${GREEN}✅ $message${NC}"
            ;;
        "error")
            echo -e "${RED}❌ $message${NC}"
            ;;
        "warning")
            echo -e "${YELLOW}⚠️  $message${NC}"
            ;;
        "info")
            echo -e "${BLUE}ℹ️  $message${NC}"
            ;;
    esac
}

# Check if Ollama is running
echo -e "\n${BLUE}1. Checking Ollama Server Status${NC}"
if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    print_status "success" "Ollama server is running"
    
    # Get server info
    VERSION=$(curl -s http://localhost:11434/api/version 2>/dev/null | jq -r '.version // "unknown"' 2>/dev/null || echo "unknown")
    print_status "info" "Ollama version: $VERSION"
else
    print_status "error" "Ollama server is not running"
    echo "   Start with: ollama serve"
    echo "   Or with Docker: docker run -d -p 11434:11434 --name ollama ollama/ollama"
fi

# Check available models
echo -e "\n${BLUE}2. Checking Available Models${NC}"
if command -v ollama >/dev/null 2>&1; then
    MODELS=$(ollama list 2>/dev/null | grep -E "(codellama|arcee)" || echo "")
    
    if [ -n "$MODELS" ]; then
        print_status "success" "CodeLlama/ArceeAgent models found:"
        echo "$MODELS" | while read -r line; do
            if [ -n "$line" ]; then
                echo "   📦 $line"
            fi
        done
    else
        print_status "warning" "No CodeLlama/ArceeAgent models found"
        echo "   Install CodeLlama models with:"
        echo "   ollama pull codellama:7b-instruct"
        echo "   ollama pull codellama:13b"
        echo "   ollama pull arcee-ai/arcee-agent"
    fi
else
    print_status "warning" "Ollama CLI not found in PATH"
    echo "   Install Ollama from: https://ollama.ai"
fi

# Test CodeLlama model functionality
echo -e "\n${BLUE}3. Testing CodeLlama Model Response${NC}"
if command -v ollama >/dev/null 2>&1; then
    TEST_PROMPT="[INST] Write a simple hello world function in Python [/INST]"
    
    # Test with different model variants
    for MODEL in "codellama:7b-instruct" "codellama:7b" "codellama:13b-instruct"; do
        if ollama list 2>/dev/null | grep -q "$MODEL"; then
            echo -n "   Testing $MODEL... "
            if timeout 30s ollama generate "$MODEL" "$TEST_PROMPT" --verbose=false >/dev/null 2>&1; then
                print_status "success" "$MODEL responds correctly"
                break
            else
                print_status "error" "$MODEL test failed or timed out"
            fi
        fi
    done
else
    print_status "warning" "Cannot test models without Ollama CLI"
fi

# Check backend configuration
echo -e "\n${BLUE}4. Checking Backend Configuration${NC}"
if [ -f ".env" ]; then
    print_status "success" "Environment file found"
    
    # Check key configuration variables
    PRIMARY_MODEL=$(grep "^PRIMARY_MODEL" .env 2>/dev/null | cut -d'=' -f2 | tr -d '"' || echo "not set")
    CODELLAMA_TEMP=$(grep "^CODELLAMA_TEMPERATURE" .env 2>/dev/null | cut -d'=' -f2 || echo "not set")
    CODELLAMA_TOKENS=$(grep "^CODELLAMA_MAX_TOKENS" .env 2>/dev/null | cut -d'=' -f2 || echo "not set")
    OLLAMA_URL=$(grep "^OLLAMA_.*URL" .env 2>/dev/null | cut -d'=' -f2 | tr -d '"' || echo "not set")
    
    echo "   🔧 Configuration Summary:"
    echo "      PRIMARY_MODEL: $PRIMARY_MODEL"
    echo "      CODELLAMA_TEMPERATURE: $CODELLAMA_TEMP"
    echo "      CODELLAMA_MAX_TOKENS: $CODELLAMA_TOKENS"
    echo "      OLLAMA_URL: $OLLAMA_URL"
    
    # Validate model configuration
    if [[ "$PRIMARY_MODEL" == *"codellama"* ]]; then
        print_status "success" "Primary model is set to CodeLlama variant"
    elif [[ "$PRIMARY_MODEL" == *"arcee"* ]]; then
        print_status "warning" "Primary model is ArceeAgent, not CodeLlama"
    else
        print_status "warning" "Primary model configuration unclear: $PRIMARY_MODEL"
    fi
    
else
    print_status "error" ".env file not found"
    echo "   Create .env file with required configuration variables"
    echo "   See README.md for environment setup instructions"
fi

# Test backend API endpoints
echo -e "\n${BLUE}5. Testing Backend API${NC}"
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    print_status "success" "Backend API is responding"
    
    # Test model endpoint
    if curl -s http://localhost:8000/api/v1/models/available >/dev/null 2>&1; then
        print_status "success" "Model management endpoint is available"
        
        # Get available models from API
        AVAILABLE_MODELS=$(curl -s http://localhost:8000/api/v1/models/available 2>/dev/null | jq -r '.models[]?' 2>/dev/null || echo "")
        if [ -n "$AVAILABLE_MODELS" ]; then
            echo "   📋 Available models via API:"
            echo "$AVAILABLE_MODELS" | while read -r model; do
                if [ -n "$model" ]; then
                    echo "      - $model"
                fi
            done
        fi
    else
        print_status "warning" "Model management endpoint not available"
    fi
    
    # Test model switching
    echo -n "   Testing model switching... "
    if curl -s -X POST http://localhost:8000/api/v1/models/switch \
           -H "Content-Type: application/json" \
           -d '{"model": "codellama:7b-instruct"}' >/dev/null 2>&1; then
        print_status "success" "Model switching works"
    else
        print_status "warning" "Model switching may not be implemented"
    fi
    
else
    print_status "error" "Backend API is not responding"
    echo "   Start backend with one of:"
    echo "   - uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    echo "   - docker-compose up backend"
    echo "   - python -m app.main"
fi

# Check system resources
echo -e "\n${BLUE}6. System Resource Check${NC}"
if command -v free >/dev/null 2>&1; then
    TOTAL_RAM=$(free -h | grep "Mem:" | awk '{print $2}')
    AVAILABLE_RAM=$(free -h | grep "Mem:" | awk '{print $7}')
    print_status "info" "System RAM: $TOTAL_RAM total, $AVAILABLE_RAM available"
    
    # Check if sufficient for CodeLlama models
    TOTAL_GB=$(free -g | grep "Mem:" | awk '{print $2}')
    if [ "$TOTAL_GB" -ge 8 ]; then
        print_status "success" "Sufficient RAM for CodeLlama 7B/13B models"
    elif [ "$TOTAL_GB" -ge 4 ]; then
        print_status "warning" "Limited RAM - consider using codellama:7b only"
    else
        print_status "error" "Insufficient RAM for CodeLlama models (need 4GB+)"
    fi
fi

# Check disk space for models
if command -v df >/dev/null 2>&1; then
    DISK_AVAILABLE=$(df -h . | tail -1 | awk '{print $4}')
    print_status "info" "Available disk space: $DISK_AVAILABLE"
fi

# Docker-specific checks
echo -e "\n${BLUE}7. Docker Configuration (if applicable)${NC}"
if command -v docker >/dev/null 2>&1; then
    # Check if containers are running
    OLLAMA_CONTAINER=$(docker ps --format "{{.Names}}" | grep -i ollama || echo "")
    BACKEND_CONTAINER=$(docker ps --format "{{.Names}}" | grep -E "(backend|api)" || echo "")
    
    if [ -n "$OLLAMA_CONTAINER" ]; then
        print_status "success" "Ollama container running: $OLLAMA_CONTAINER"
        
        # Check container resource limits
        MEMORY_LIMIT=$(docker inspect "$OLLAMA_CONTAINER" --format='{{.HostConfig.Memory}}' 2>/dev/null || echo "0")
        if [ "$MEMORY_LIMIT" -gt 0 ]; then
            MEMORY_GB=$((MEMORY_LIMIT / 1024 / 1024 / 1024))
            print_status "info" "Ollama container memory limit: ${MEMORY_GB}GB"
        else
            print_status "info" "Ollama container has no memory limit set"
        fi
    else
        print_status "info" "No Ollama containers running"
    fi
    
    if [ -n "$BACKEND_CONTAINER" ]; then
        print_status "success" "Backend container running: $BACKEND_CONTAINER"
    else
        print_status "info" "No backend containers running"
    fi
else
    print_status "info" "Docker not available"
fi

# Final status summary
echo -e "\n${BLUE}📊 Configuration Summary${NC}"
echo "=========================="

# Determine overall status
ERRORS=0
WARNINGS=0

# Count status indicators (simplified approach)
if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    ((ERRORS++))
fi

if ! curl -s http://localhost:8000/health >/dev/null 2>&1; then
    ((ERRORS++))
fi

if [ ! -f ".env" ]; then
    ((WARNINGS++))
fi

# Final recommendation
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    print_status "success" "Configuration is ready for CodeLlama"
    echo ""
    echo " Next steps:"
    echo "   1. Test with: curl -X POST http://localhost:8000/api/v1/chat/query -H 'Content-Type: application/json' -d '{\"message\": \"Hello CodeLlama\", \"model\": \"codellama:7b-instruct\"}'"
    echo "   2. Open frontend: http://localhost:3000"
    echo "   3. Check API docs: http://localhost:8000/docs"
elif [ $ERRORS -eq 0 ]; then
    print_status "warning" "Configuration has warnings but should work"
    echo ""
    echo "⚡ Action items:"
    echo "   - Review warnings above"
    echo "   - Consider updating .env configuration"
else
    print_status "error" "Configuration needs attention"
    echo ""
    echo "🔧 Required fixes:"
    echo "   - Address errors above before using CodeLlama"
    echo "   - Ensure all services are running"
fi

echo ""
echo "For detailed setup instructions, see README.md"
echo "For troubleshooting, check the 'Troubleshooting CodeLlama Configuration' section"
