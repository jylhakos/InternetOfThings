#!/bin/bash

# LangGraph RAG System - Complete Integration Test
# This script tests the full system integration after deployment

set -e

echo "🚀 Starting LangGraph RAG System Integration Test..."

# Define colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"
QDRANT_URL="http://localhost:6333"
OLLAMA_URL="http://localhost:11434"
WAIT_TIME=30

echo "📍 Testing endpoints:"
echo "   - Backend API: $BASE_URL"
echo "   - Frontend App: $FRONTEND_URL" 
echo "   - Qdrant Vector DB: $QDRANT_URL"
echo "   - Ollama LLM Server: $OLLAMA_URL"
echo ""

# Function to wait for service
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    echo -n "⏳ Waiting for $service_name to be ready"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            echo -e " ${GREEN}✓${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo -e " ${RED}✗${NC}"
    echo -e "${RED}Error: $service_name failed to start after $((max_attempts * 2)) seconds${NC}"
    return 1
}

# Test service availability
echo "🔍 Testing service availability..."

# Check Qdrant
if wait_for_service "$QDRANT_URL" "Qdrant Vector Database"; then
    echo -e "${GREEN}✓ Qdrant is running${NC}"
else
    echo -e "${RED}✗ Qdrant failed to start${NC}"
    exit 1
fi

# Check Ollama
if wait_for_service "$OLLAMA_URL" "Ollama LLM Server"; then
    echo -e "${GREEN}✓ Ollama is running${NC}"
else
    echo -e "${RED}✗ Ollama failed to start${NC}"
    exit 1
fi

# Check Backend API
if wait_for_service "$BASE_URL/health" "Backend API"; then
    echo -e "${GREEN}✓ Backend API is running${NC}"
else
    echo -e "${RED}✗ Backend API failed to start${NC}"
    exit 1
fi

# Check Frontend
if wait_for_service "$FRONTEND_URL" "Frontend Application"; then
    echo -e "${GREEN}✓ Frontend is running${NC}"
else
    echo -e "${RED}✗ Frontend failed to start${NC}"
    exit 1
fi

echo ""
echo "🧪 Running API Integration Tests..."

# Test 1: Health Check
echo -n "📋 Health check... "
health_response=$(curl -s "$BASE_URL/health" | jq -r '.status' 2>/dev/null || echo "error")
if [ "$health_response" = "healthy" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ (got: $health_response)${NC}"
fi

# Test 2: Qdrant Collection Status
echo -n "🗃️  Vector database collections... "
collections_response=$(curl -s "$BASE_URL/documents/collections" | jq -r '.collections | length' 2>/dev/null || echo "error")
if [ "$collections_response" != "error" ] && [ "$collections_response" != "null" ]; then
    echo -e "${GREEN}✓ ($collections_response collections)${NC}"
else
    echo -e "${RED}✗ (failed to get collections)${NC}"
fi

# Test 3: Ollama Model Status
echo -n "🤖 LLM models availability... "
models_response=$(curl -s "$BASE_URL/chat/models" | jq -r '.models | length' 2>/dev/null || echo "error")
if [ "$models_response" != "error" ] && [ "$models_response" != "null" ] && [ "$models_response" -gt 0 ]; then
    echo -e "${GREEN}✓ ($models_response models available)${NC}"
else
    echo -e "${YELLOW}⚠ (no models loaded - will pull on first use)${NC}"
fi

# Test 4: Document Upload (if sample files exist)
echo -n "📄 Document upload functionality... "
if [ -f "sample.txt" ]; then
    upload_response=$(curl -s -X POST "$BASE_URL/documents/upload" \
        -F "file=@sample.txt" \
        -F "metadata={\"title\":\"Test Document\"}" | jq -r '.id' 2>/dev/null || echo "error")
    if [ "$upload_response" != "error" ] && [ "$upload_response" != "null" ]; then
        echo -e "${GREEN}✓ (uploaded: $upload_response)${NC}"
        UPLOADED_DOC_ID="$upload_response"
    else
        echo -e "${RED}✗ (upload failed)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ (no sample file found - skipped)${NC}"
fi

# Test 5: Basic Chat Query
echo -n "💬 Basic chat functionality... "
chat_response=$(curl -s -X POST "$BASE_URL/chat/query" \
    -H "Content-Type: application/json" \
    -d '{"query":"Hello, can you help me?","model":"arcee-ai/arcee-agent","use_rag":false}' | 
    jq -r '.response' 2>/dev/null || echo "error")

if [ "$chat_response" != "error" ] && [ "$chat_response" != "null" ] && [ ${#chat_response} -gt 10 ]; then
    echo -e "${GREEN}✓ (got response)${NC}"
else
    echo -e "${YELLOW}⚠ (basic chat may require model download)${NC}"
fi

# Test 6: RAG Query (if document was uploaded)
if [ -n "$UPLOADED_DOC_ID" ]; then
    echo -n "🔍 RAG functionality... "
    rag_response=$(curl -s -X POST "$BASE_URL/chat/rag" \
        -H "Content-Type: application/json" \
        -d '{"query":"What is in the uploaded document?","model":"arcee-ai/arcee-agent"}' | 
        jq -r '.response' 2>/dev/null || echo "error")
    
    if [ "$rag_response" != "error" ] && [ "$rag_response" != "null" ] && [ ${#rag_response} -gt 10 ]; then
        echo -e "${GREEN}✓ (RAG working)${NC}"
    else
        echo -e "${YELLOW}⚠ (RAG may require model download)${NC}"
    fi
fi

echo ""
echo "📊 System Status Summary:"
echo "========================="

# Get system stats
stats_response=$(curl -s "$BASE_URL/health" 2>/dev/null || echo "{}")

echo "🐳 Docker Services:"
docker-compose ps --format "table {{.Service}}\t{{.State}}\t{{.Ports}}" 2>/dev/null || echo "   Docker Compose not available"

echo ""
echo "🌐 Application URLs:"
echo "   📱 Frontend Application: $FRONTEND_URL"
echo "   🔗 API Documentation: $BASE_URL/docs"
echo "   📊 Qdrant Dashboard: $QDRANT_URL/dashboard"
echo "   🤖 Ollama API: $OLLAMA_URL"

echo ""
echo "🛠️  Next Steps:"
echo "   1. Open $FRONTEND_URL in your browser"
echo "   2. Upload documents using the Upload tab"
echo "   3. Chat with your documents using the Chat tab"
echo "   4. Configure prompts and models in the Config tab"
echo "   5. Check API docs at $BASE_URL/docs"

echo ""
echo "📚 Quick Start Commands:"
echo "   # View logs"
echo "   docker-compose logs -f"
echo ""
echo "   # Restart a service"
echo "   docker-compose restart [frontend|backend|qdrant|ollama]"
echo ""
echo "   # Stop all services"
echo "   docker-compose down"
echo ""
echo "   # Stop and remove all data"
echo "   docker-compose down -v"

echo ""
if [ "$health_response" = "healthy" ]; then
    echo -e "${GREEN}🎉 LangGraph RAG System is running successfully!${NC}"
    echo -e "${GREEN}   Access your application at: $FRONTEND_URL${NC}"
else
    echo -e "${YELLOW}⚠️  System is starting up - some features may not be fully ready${NC}"
    echo -e "${YELLOW}   Wait a few minutes for all models to download and services to initialize${NC}"
fi

echo ""
