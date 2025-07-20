#!/bin/bash

# Test the AI Agent API
echo "Testing AI Agent API..."

# Wait for service to start
echo "Waiting for service to start..."
sleep 5

# Test health endpoint
echo "1. Testing health endpoint..."
curl -s http://localhost:8000/health || echo "Health check failed"

echo -e "\n2. Testing models endpoint..."
curl -s http://localhost:8000/v1/models | python3 -m json.tool || echo "Models endpoint failed"

echo -e "\n3. Testing chat completion with greeting..."
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ai-agent-no-framework",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }' | python3 -m json.tool || echo "Chat completion failed"

echo -e "\n4. Testing weather query..."
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ai-agent-no-framework", 
    "messages": [
      {"role": "user", "content": "What is the weather like in London?"}
    ]
  }' | python3 -m json.tool || echo "Weather query failed"

echo -e "\nTest completed!"
