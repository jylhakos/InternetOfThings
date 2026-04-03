#!/bin/bash
# Execute comprehensive security test suite

set -e

echo "=========================================="
echo "LLM Security Test Suite"
echo "=========================================="

# Check if virtual environment is activated
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo "Warning: Virtual environment is not activated."
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if Ollama is running
echo ""
echo "Checking Ollama service..."
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "Error: Ollama service is not running."
    echo "Please start Ollama with: ollama serve"
    exit 1
fi

echo "Ollama service is running."

# Run tests
echo ""
echo "Running security tests..."
echo ""

# Run all tests with verbose output
pytest tests/ -v --cov=src --cov-report=html --cov-report=term

echo ""
echo "=========================================="
echo "Test Results"
echo "=========================================="
echo ""
echo "Coverage report generated: htmlcov/index.html"
echo ""
echo "To view the coverage report, run:"
echo "  python3 -m http.server --directory htmlcov 8000"
echo "  Then open: http://localhost:8000"
echo ""
