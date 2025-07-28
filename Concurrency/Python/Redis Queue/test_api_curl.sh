#!/bin/bash
# cURL Test Script for Redis Queue API with Open WebUI integration
# Run this script to test all API endpoints

BASE_URL="http://localhost:8000"
API_KEY="dummy-key"

echo "🚀 Testing Redis Queue API Endpoints"
echo "=================================="

# Test 1: Health Check
echo "🏥 Testing Health Endpoint..."
curl -s "$BASE_URL/health" | jq . 2>/dev/null || curl -s "$BASE_URL/health"
echo -e "\n"

# Test 2: Models List (Standard)
echo "📋 Testing Models Endpoint..."
curl -s "$BASE_URL/models" | jq . 2>/dev/null || curl -s "$BASE_URL/models"
echo -e "\n"

# Test 3: Models List (OpenAI Format)
echo "🤖 Testing OpenAI Models Endpoint..."
curl -s -H "Authorization: Bearer $API_KEY" "$BASE_URL/v1/models" | jq . 2>/dev/null || curl -s -H "Authorization: Bearer $API_KEY" "$BASE_URL/v1/models"
echo -e "\n"

# Test 4: Submit Chat Request
echo "💬 Testing Chat Submission..."
CHAT_RESPONSE=$(curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
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
    echo -e "\n📊 Testing Task Status..."
    sleep 2  # Wait a bit
    curl -s "$BASE_URL/task/$TASK_ID" | jq . 2>/dev/null || curl -s "$BASE_URL/task/$TASK_ID"
fi

echo -e "\n"

# Test 5: OpenAI Chat Completions
echo "🗨️ Testing OpenAI Chat Completions..."
curl -s -X POST "$BASE_URL/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "model": "llama3.2:1b",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Hello! How are you?"}
    ],
    "temperature": 0.7,
    "max_tokens": 50
  }' | jq . 2>/dev/null || curl -s -X POST "$BASE_URL/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "model": "llama3.2:1b",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Hello! How are you?"}
    ],
    "temperature": 0.7,
    "max_tokens": 50
  }'

echo -e "\n\n✅ API Tests Complete!"
echo "If all endpoints returned JSON responses, your API is ready for Open WebUI integration."
