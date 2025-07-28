#!/usr/bin/env python3
"""
API Validation Script - Dry run test of API endpoints
Tests API structure and validates endpoint definitions without requiring services to be running.
"""

import sys
import os

def validate_api_endpoints():
    """Validate that the main.py file contains the correct API endpoints."""
    print("🔍 Validating API Endpoint Definitions")
    print("=" * 50)
    
    # Read the main.py file
    try:
        with open("main.py", "r") as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ main.py not found")
        return False
    
    # Required endpoints for Open WebUI integration
    required_endpoints = [
        ('POST /chat', '@app.post("/chat")'),
        ('GET /task/{task_id}', '@app.get("/task/{task_id}")'),
        ('GET /health', '@app.get("/health")'),
        ('GET /models', '@app.get("/models")'),
        ('GET /v1/models', '@app.get("/v1/models")'),
        ('POST /v1/chat/completions', '@app.post("/v1/chat/completions")'),
    ]
    
    all_found = True
    
    for endpoint_name, endpoint_pattern in required_endpoints:
        if endpoint_pattern in content:
            print(f"✅ {endpoint_name} - Found")
        else:
            print(f"❌ {endpoint_name} - Missing")
            all_found = False
    
    return all_found

def validate_pydantic_models():
    """Validate that required Pydantic models are defined."""
    print("\n🏗️ Validating Pydantic Models")
    print("=" * 50)
    
    try:
        with open("main.py", "r") as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ main.py not found")
        return False
    
    required_models = [
        'ChatRequest',
        'TaskResponse', 
        'TaskResultResponse',
        'OpenAIModel',
        'OpenAIChatCompletionRequest',
        'OpenAIChatCompletionResponse'
    ]
    
    all_found = True
    
    for model in required_models:
        if f"class {model}" in content:
            print(f"✅ {model} - Found")
        else:
            print(f"❌ {model} - Missing")
            all_found = False
    
    return all_found

def validate_cors_configuration():
    """Validate CORS configuration for Open WebUI."""
    print("\n🌐 Validating CORS Configuration")
    print("=" * 50)
    
    try:
        with open("main.py", "r") as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ main.py not found")
        return False
    
    cors_checks = [
        ('CORSMiddleware import', 'from fastapi.middleware.cors import CORSMiddleware'),
        ('CORS middleware added', 'app.add_middleware'),
        ('Allow origins configured', 'allow_origins'),
        ('Allow headers configured', 'allow_headers'),
    ]
    
    all_found = True
    
    for check_name, pattern in cors_checks:
        if pattern in content:
            print(f"✅ {check_name} - Found")
        else:
            print(f"❌ {check_name} - Missing")
            all_found = False
    
    return all_found

def generate_curl_test_file():
    """Generate a standalone cURL test file."""
    print("\n📝 Generating cURL Test File")
    print("=" * 50)
    
    curl_tests = '''#!/bin/bash
# cURL Test Script for Redis Queue API with Open WebUI integration
# Run this script to test all API endpoints

BASE_URL="http://localhost:8000"
API_KEY="dummy-key"

echo "🚀 Testing Redis Queue API Endpoints"
echo "=================================="

# Test 1: Health Check
echo "🏥 Testing Health Endpoint..."
curl -s "$BASE_URL/health" | jq . 2>/dev/null || curl -s "$BASE_URL/health"
echo -e "\\n"

# Test 2: Models List (Standard)
echo "📋 Testing Models Endpoint..."
curl -s "$BASE_URL/models" | jq . 2>/dev/null || curl -s "$BASE_URL/models"
echo -e "\\n"

# Test 3: Models List (OpenAI Format)
echo "🤖 Testing OpenAI Models Endpoint..."
curl -s -H "Authorization: Bearer $API_KEY" "$BASE_URL/v1/models" | jq . 2>/dev/null || curl -s -H "Authorization: Bearer $API_KEY" "$BASE_URL/v1/models"
echo -e "\\n"

# Test 4: Submit Chat Request
echo "💬 Testing Chat Submission..."
CHAT_RESPONSE=$(curl -s -X POST "$BASE_URL/chat" \\
  -H "Content-Type: application/json" \\
  -d '{
    "prompt": "What is the capital of France?",
    "model": "llama3.2:1b",
    "temperature": 0.7,
    "max_tokens": 100
  }')

echo "$CHAT_RESPONSE" | jq . 2>/dev/null || echo "$CHAT_RESPONSE"

# Extract task_id for status check
TASK_ID=$(echo "$CHAT_RESPONSE" | jq -r '.task_id' 2>/dev/null || echo "")

if [ "$TASK_ID" != "" ] && [ "$TASK_ID" != "null" ]; then
    echo -e "\\n📊 Testing Task Status..."
    sleep 2  # Wait a bit
    curl -s "$BASE_URL/task/$TASK_ID" | jq . 2>/dev/null || curl -s "$BASE_URL/task/$TASK_ID"
fi

echo -e "\\n"

# Test 5: OpenAI Chat Completions
echo "🗨️ Testing OpenAI Chat Completions..."
curl -s -X POST "$BASE_URL/v1/chat/completions" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer $API_KEY" \\
  -d '{
    "model": "llama3.2:1b",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Hello! How are you?"}
    ],
    "temperature": 0.7,
    "max_tokens": 50
  }' | jq . 2>/dev/null || curl -s -X POST "$BASE_URL/v1/chat/completions" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer $API_KEY" \\
  -d '{
    "model": "llama3.2:1b",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Hello! How are you?"}
    ],
    "temperature": 0.7,
    "max_tokens": 50
  }'

echo -e "\\n\\n✅ API Tests Complete!"
echo "If all endpoints returned JSON responses, your API is ready for Open WebUI integration."
'''
    
    try:
        with open("test_api_curl.sh", "w") as f:
            f.write(curl_tests)
        
        # Make it executable
        os.chmod("test_api_curl.sh", 0o755)
        
        print("✅ Created test_api_curl.sh")
        print("   Run with: ./test_api_curl.sh")
        return True
    except Exception as e:
        print(f"❌ Failed to create test file: {e}")
        return False

def generate_docker_compose_file():
    """Generate a docker-compose.yml file for easy deployment."""
    print("\n🐳 Generating Docker Compose File")
    print("=" * 50)
    
    docker_compose = '''version: '3.8'

services:
  redis:
    image: redis:7-alpine
    container_name: redis-queue-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    command: redis-server --appendonly yes

  ollama:
    image: ollama/ollama
    container_name: redis-queue-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped
    environment:
      - OLLAMA_HOST=0.0.0.0

  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: redis-queue-open-webui
    ports:
      - "3001:8080"
    environment:
      - OPENAI_API_BASE_URL=http://host.docker.internal:8000/v1
      - OPENAI_API_KEY=dummy-key
      - WEBUI_SECRET_KEY=your-secret-key-here
      - WEBUI_NAME=Redis Queue LLM Interface
    volumes:
      - open_webui_data:/app/backend/data
    extra_hosts:
      - "host.docker.internal:host-gateway"
    restart: unless-stopped
    depends_on:
      - redis
      - ollama

volumes:
  redis_data:
  ollama_data:
  open_webui_data:

networks:
  default:
    driver: bridge
'''
    
    try:
        with open("docker-compose.yml", "w") as f:
            f.write(docker_compose)
        
        print("✅ Created docker-compose.yml")
        print("   Start with: docker-compose up -d")
        print("   Note: You'll still need to run FastAPI and RQ worker separately")
        return True
    except Exception as e:
        print(f"❌ Failed to create docker-compose.yml: {e}")
        return False

def main():
    """Run validation checks."""
    print("🔍 Redis Queue API Validation for Open WebUI Integration")
    print("=" * 70)
    
    # Run validations
    endpoints_ok = validate_api_endpoints()
    models_ok = validate_pydantic_models()
    cors_ok = validate_cors_configuration()
    
    # Generate helpful files
    curl_file_ok = generate_curl_test_file()
    compose_file_ok = generate_docker_compose_file()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 VALIDATION SUMMARY")
    print("=" * 70)
    
    validations = [
        ("API Endpoints", endpoints_ok),
        ("Pydantic Models", models_ok),
        ("CORS Configuration", cors_ok),
    ]
    
    files = [
        ("cURL Test Script", curl_file_ok),
        ("Docker Compose File", compose_file_ok),
    ]
    
    for name, status in validations:
        print(f"{'✅' if status else '❌'} {name}: {'Pass' if status else 'Fail'}")
    
    print("\nGenerated Files:")
    for name, status in files:
        print(f"{'✅' if status else '❌'} {name}: {'Created' if status else 'Failed'}")
    
    all_ok = all(status for _, status in validations)
    
    if all_ok:
        print("\n🎉 All validations passed! Your API is ready for Open WebUI integration.")
        print("\nNext steps:")
        print("1. Start your services: python main.py, python worker.py")
        print("2. Test with: ./test_api_curl.sh")
        print("3. Start Open WebUI: docker-compose up -d open-webui")
        print("4. Access Open WebUI at: http://localhost:3001")
    else:
        print("\n⚠️ Some validations failed. Please check your main.py file.")
    
    return all_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
