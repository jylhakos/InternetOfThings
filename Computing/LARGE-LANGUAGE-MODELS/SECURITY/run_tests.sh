#!/bin/bash
#
# Script to run all tests with coverage
#

echo "========================================="
echo "  Running Prompt Injection Tests        "
echo "========================================="
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Virtual environment is not activated!"
    echo "Activating virtual environment..."
    source venv/bin/activate
    
    if [ -z "$VIRTUAL_ENV" ]; then
        echo "Error: Failed to activate virtual environment"
        echo "Please run: source venv/bin/activate"
        exit 1
    fi
fi

echo "Virtual environment: $VIRTUAL_ENV"
echo ""

# Check if Ollama is running
echo "Checking if Ollama is running..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "Warning: Ollama server is not responding at http://localhost:11434"
    echo "Please make sure Ollama is running. You can start it with:"
    echo "  ollama serve"
    echo ""
    echo "Some tests will be skipped."
    echo ""
fi

# Run tests
echo "Running tests..."
echo ""
pytest tests/ -v -s --tb=short

echo ""
echo "========================================="
echo "  Test Run Complete                     "
echo "========================================="
