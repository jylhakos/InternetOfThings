#!/bin/bash

# LLM Inference Server Setup Script
# This script sets up the virtual environment and installs dependencies

set -e  # Exit on error

echo "=================================="
echo "  LLM Inference Server Setup"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    echo "  Please install Python 3.8 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✓ Found Python $PYTHON_VERSION${NC}"

# Check Python version (need 3.8+)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo -e "${RED}✗ Python 3.8 or higher is required${NC}"
    echo "  Current version: $PYTHON_VERSION"
    exit 1
fi

echo ""

# Check if virtual environment already exists
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠ Virtual environment already exists${NC}"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing virtual environment..."
        rm -rf venv
    else
        echo "Keeping existing virtual environment"
        echo ""
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✓ pip upgraded${NC}"
echo ""

# Install dependencies
echo "Installing dependencies from requirements.txt..."
echo ""

if pip install -r requirements.txt; then
    echo ""
    echo -e "${GREEN}✓ All dependencies installed successfully${NC}"
else
    echo ""
    echo -e "${RED}✗ Failed to install dependencies${NC}"
    exit 1
fi

echo ""
echo "=================================="
echo "  Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Activate the virtual environment:"
echo -e "   ${GREEN}source venv/bin/activate${NC}"
echo ""
echo "2. Start the inference server:"
echo -e "   ${GREEN}python sources/inference_server.py${NC}"
echo ""
echo "3. In another terminal, run the client examples:"
echo -e "   ${GREEN}python sources/client_example.py${NC}"
echo ""
echo "4. Test with cURL:"
echo -e "   ${GREEN}curl http://localhost:5000/health${NC}"
echo ""
echo "5. Try RAG example:"
echo -e "   ${GREEN}python sources/rag_example.py${NC}"
echo ""
echo "6. Try Vector DB example:"
echo -e "   ${GREEN}python sources/vector_db_example.py${NC}"
echo ""
echo "For more information, see README.md"
echo ""
