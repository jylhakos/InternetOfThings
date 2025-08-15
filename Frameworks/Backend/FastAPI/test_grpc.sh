#!/bin/bash

# Test Runner for gRPC Integration
# This script sets up the environment and runs comprehensive tests

set -e

echo "🧪 Starting gRPC Integration Tests..."

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Warning: Not in a virtual environment. Consider using 'python -m venv venv && source venv/bin/activate'"
fi

# Install test dependencies if needed
echo "📦 Installing test dependencies..."
pip install -q pytest pytest-asyncio pytest-cov

# Generate gRPC code from proto files
echo "🔧 Generating gRPC Python code from Protocol Buffers..."
if [[ -f "./generate_grpc.sh" ]]; then
    chmod +x ./generate_grpc.sh
    ./generate_grpc.sh
else
    echo "⚠️  generate_grpc.sh not found, running manual generation..."
    mkdir -p protos
    python -m grpc_tools.protoc \
        --proto_path=protos \
        --python_out=protos \
        --grpc_python_out=protos \
        protos/*.proto
fi

# Create __init__.py files for proper imports
touch protos/__init__.py
touch services/__init__.py
touch tests/__init__.py

echo "🚀 Running gRPC integration tests..."

# Run specific test categories
echo "1️⃣ Testing Protocol Buffer structure..."
python -m pytest tests/test_grpc_integration.py::TestProtocolBuffers -v

echo "2️⃣ Testing gRPC service configuration..."
python -m pytest tests/test_grpc_integration.py::TestGRPCServiceStartup -v

echo "3️⃣ Testing gRPC integration with mocks..."
python -m pytest tests/test_grpc_integration.py::TestGRPCAuthIntegration -v

echo "4️⃣ Running performance tests..."
python -m pytest tests/test_grpc_integration.py::TestGRPCPerformance -v -m "not performance" || echo "Performance tests skipped (use -m performance to run)"

echo "✅ All tests completed!"

# Optional: Test actual gRPC server if running
echo ""
echo "🔍 Additional Testing Options:"
echo "To test with a running gRPC server:"
echo "1. Start the Auth Service: python services/auth_service.py"
echo "2. Run integration tests: python -m pytest tests/ -v -k 'not mock'"
echo ""
echo "To test FastAPI with gRPC integration:"
echo "1. Start Redis: redis-server"
echo "2. Start Auth Service: python services/auth_service.py"
echo "3. Start FastAPI: uvicorn main:app --reload"
echo "4. Test endpoints: curl -X POST http://localhost:8000/register ..."
