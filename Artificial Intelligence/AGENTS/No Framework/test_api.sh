#!/bin/bash

# Test script for the AI Agent API
# Tests various endpoints and functionalities

set -e

BASE_URL="http://localhost:8000"

echo "🧪 Testing AI Agent API"
echo "======================"

# Function to test API endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    echo ""
    echo "Testing: $description"
    echo "Endpoint: $method $endpoint"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "HTTP_CODE:%{http_code}" "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "HTTP_CODE:%{http_code}" -X "$method" -H "Content-Type: application/json" -d "$data" "$BASE_URL$endpoint")
    fi
    
    http_code=$(echo "$response" | grep -o "HTTP_CODE:[0-9]*" | cut -d: -f2)
    body=$(echo "$response" | sed 's/HTTP_CODE:[0-9]*$//')
    
    if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 201 ]; then
        echo "✅ Success ($http_code)"
        echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
    else
        echo "❌ Failed ($http_code)"
        echo "$body"
    fi
    
    sleep 1
}

# Test health endpoint
test_endpoint "GET" "/health" "" "Health Check"

# Test root endpoint
test_endpoint "GET" "/" "" "Root Information"

# Test models endpoint
test_endpoint "GET" "/v1/models" "" "List Models"

# Test greeting
greeting_data='{
  "messages": [
    {"role": "user", "content": "Hello, how are you?"}
  ],
  "temperature": 0.7
}'
test_endpoint "POST" "/v1/chat/completions" "$greeting_data" "Greeting Message"

# Test weather query
weather_data='{
  "messages": [
    {"role": "user", "content": "What is the temperature in London?"}
  ],
  "temperature": 0.7
}'
test_endpoint "POST" "/v1/chat/completions" "$weather_data" "Weather Query"

# Test general query
general_data='{
  "messages": [
    {"role": "user", "content": "What is Python programming?"}
  ],
  "temperature": 0.7
}'
test_endpoint "POST" "/v1/chat/completions" "$general_data" "General Query"

# Test weather convenience endpoint
test_endpoint "POST" "/v1/weather?city=Paris" "" "Weather Convenience Endpoint"

# Test agents list
test_endpoint "GET" "/v1/agents" "" "List Agents"

echo ""
echo "🎉 Testing completed!"
echo ""
echo "For interactive testing, visit: $BASE_URL/docs"
