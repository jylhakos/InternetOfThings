#!/bin/bash

echo "🧪 Testing ASP.NET Core Web API"
echo "👤 User: "
echo "📅 Date: 2025-06-22 09:28:27 UTC"
echo ""

API_URL="http://localhost:8080"

# Test 1: Health check
echo "1. Testing health endpoint..."
curl -X GET "$API_URL/health" -w "\nStatus: %{http_code}\n\n"

# Test 2: Root endpoint
echo "2. Testing root endpoint..."
curl -X GET "$API_URL/" -w "\nStatus: %{http_code}\n\n"

# Test 3: Register a new user
echo "3. Testing user registration..."
REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"testuser@example.com","password":"testpass123"}' \
  -w "%{http_code}")

echo "Registration response: $REGISTER_RESPONSE"
echo ""

# Extract token from registration response (if successful)
TOKEN=$(echo "$REGISTER_RESPONSE" | jq -r '.token // empty' 2>/dev/null)

if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
    echo "✅ Registration successful, token obtained"
    
    # Test 4: Create a task
    echo "4. Testing task creation..."
    curl -X POST "$API_URL/api/tasks" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d '{"title":"Test Task","description":"This is a test task","priority":"High"}' \
      -w "\nStatus: %{http_code}\n\n"
    
    # Test 5: Get all tasks
    echo "5. Testing get all tasks..."
    curl -X GET "$API_URL/api/tasks" \
      -H "Authorization: Bearer $TOKEN" \
      -w "\nStatus: %{http_code}\n\n"
else
    echo "❌ Registration failed or token not received"
    
    # Try to login with existing user
    echo "4. Testing login with existing user..."
    LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/api/auth/login" \
      -H "Content-Type: application/json" \
      -d '{"email":"test@example.com","password":"testpassword123"}' \
      -w "%{http_code}")
    
    echo "Login response: $LOGIN_RESPONSE"
    
    TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.token // empty' 2>/dev/null)
    
    if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
        echo "✅ Login successful, token obtained"
        
        # Test get tasks with login token
        echo "5. Testing get all tasks with login token..."
        curl -X GET "$API_URL/api/tasks" \
          -H "Authorization: Bearer $TOKEN" \
          -w "\nStatus: %{http_code}\n\n"
    fi
fi

echo "🏁 API testing completed"