#!/bin/bash

# Simple test script to verify the LLM Inference Server

echo "🧪 Testing LLM Inference Server..."

# Check if server is running
SERVER_URL="http://localhost:3000"

# Function to test endpoint
test_endpoint() {
    local url=$1
    local expected_status=${2:-200}
    
    response=$(curl -s -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    status_code="${response: -3}"
    
    if [ "$status_code" = "$expected_status" ]; then
        echo "✅ $url - OK ($status_code)"
        return 0
    else
        echo "❌ $url - Failed ($status_code)"
        return 1
    fi
}

echo "Testing basic endpoints..."
test_endpoint "$SERVER_URL/"
test_endpoint "$SERVER_URL/api/health"

echo ""
echo "Testing authentication..."

# Test login with demo user
echo "Logging in with demo user..."
login_response=$(curl -s -X POST "$SERVER_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username":"demo","password":"demo123"}' 2>/dev/null)

token=$(echo "$login_response" | jq -r '.token // empty' 2>/dev/null)

if [ -n "$token" ] && [ "$token" != "null" ]; then
    echo "✅ Login successful"
    echo "🔑 Token: ${token:0:20}..."
    
    # Test authenticated endpoint
    echo "Testing authenticated chat endpoint..."
    chat_response=$(curl -s -w "%{http_code}" \
        -X POST "$SERVER_URL/api/chat/message" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $token" \
        -d '{"message":"Hello, this is a test!"}' 2>/dev/null)
    
    status_code="${chat_response: -3}"
    if [ "$status_code" = "200" ]; then
        echo "✅ Chat endpoint works"
    else
        echo "❌ Chat endpoint failed ($status_code)"
    fi
else
    echo "❌ Login failed"
fi

echo ""
echo "🎉 Test completed!"
