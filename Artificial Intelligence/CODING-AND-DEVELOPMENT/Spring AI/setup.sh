#!/bin/bash

# Setup script for Spring AI RAG Demo
# This script checks prerequisites and starts the necessary services

set -e

echo "========================================"
echo "Spring AI RAG Demo - Setup Script"
echo "========================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Java
echo "Checking Java installation..."
if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}')
    echo -e "${GREEN}✓${NC} Java found: $JAVA_VERSION"
    
    # Extract major version
    JAVA_MAJOR=$(echo "$JAVA_VERSION" | cut -d'.' -f1)
    if [ "$JAVA_MAJOR" -lt 17 ]; then
        echo -e "${RED}✗${NC} Java 17+ is required, but found Java $JAVA_MAJOR"
        exit 1
    fi
else
    echo -e "${RED}✗${NC} Java not found. Please install Java 17 or higher"
    exit 1
fi
echo ""

# Check Docker
echo "Checking Docker installation..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo -e "${GREEN}✓${NC} $DOCKER_VERSION"
else
    echo -e "${RED}✗${NC} Docker not found. Please install Docker"
    exit 1
fi
echo ""

# Check Ollama
echo "Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓${NC} Ollama is installed"
    
    # Check if Ollama server is running
    if curl -s http://localhost:11434 > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Ollama server is running"
    else
        echo -e "${YELLOW}!${NC} Ollama is installed but not running"
        echo "  Starting Ollama server..."
        ollama serve &
        sleep 3
    fi
    
    # Check for required models
    echo "Checking Ollama models..."
    if ollama list | grep -q "llama3.2"; then
        echo -e "${GREEN}✓${NC} llama3.2 model found"
    else
        echo -e "${YELLOW}!${NC} llama3.2 model not found"
        echo "  Pulling llama3.2 model..."
        ollama pull llama3.2
    fi
    
    if ollama list | grep -q "nomic-embed-text"; then
        echo -e "${GREEN}✓${NC} nomic-embed-text model found"
    else
        echo -e "${YELLOW}!${NC} nomic-embed-text model not found"
        echo "  Pulling nomic-embed-text model..."
        ollama pull nomic-embed-text
    fi
else
    echo -e "${RED}✗${NC} Ollama not found"
    echo "  Install Ollama from: https://ollama.com/"
    exit 1
fi
echo ""

# Start Qdrant with Docker Compose
echo "Starting Qdrant vector database..."
if docker-compose up -d qdrant; then
    echo -e "${GREEN}✓${NC} Qdrant started successfully"
    
    # Wait for Qdrant to be ready
    echo "Waiting for Qdrant to be ready..."
    sleep 3
    
    if curl -s http://localhost:6333 > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Qdrant is ready"
    else
        echo -e "${YELLOW}!${NC} Qdrant may not be ready yet, give it a few more seconds"
    fi
else
    echo -e "${RED}✗${NC} Failed to start Qdrant"
    exit 1
fi
echo ""

# Check if documents exist
echo "Checking for documents..."
if [ -d "src/main/resources/documents" ] && [ "$(ls -A src/main/resources/documents)" ]; then
    DOC_COUNT=$(ls -1 src/main/resources/documents | wc -l)
    echo -e "${GREEN}✓${NC} Found $DOC_COUNT document(s) in documents folder"
else
    echo -e "${YELLOW}!${NC} No documents found in src/main/resources/documents/"
    echo "  Add PDF files to this directory for document ingestion"
fi
echo ""

echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "All prerequisites are ready. You can now run the application:"
echo ""
echo "  ./gradlew bootRun"
echo ""
echo "Or build and run the JAR:"
echo ""
echo "  ./gradlew build"
echo "  java -jar build/libs/spring-ai-rag-demo-0.0.1-SNAPSHOT.jar"
echo ""
echo "Then access the API at: http://localhost:8080"
echo ""
