#!/bin/bash

# Test script for the Bike Rental Agent API

BASE_URL="http://localhost:8000"

echo "🧪 Testing European Bike Rental Agent API..."

# Check if server is running
if ! curl -s "$BASE_URL/health" > /dev/null; then
    echo "❌ Server is not running. Please start the server first:"
    echo "python main.py"
    exit 1
fi

echo "✅ Server is running"

# Test 1: Health check
echo ""
echo "🏥 Testing health endpoint..."
curl -s "$BASE_URL/health" | python3 -m json.tool

# Test 2: Get supported cities
echo ""
echo "🏙️ Testing cities endpoint..."
curl -s "$BASE_URL/api/cities" | python3 -m json.tool

# Test 3: Chat with agent
echo ""
echo "💬 Testing chat endpoint..."
curl -X POST "$BASE_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to rent a bike in Amsterdam near Central Station",
    "session_id": "test-session-123"
  }' | python3 -m json.tool

# Test 4: Find bikes
echo ""
echo "🔍 Testing find bikes endpoint..."
curl -X POST "$BASE_URL/api/find-bikes" \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Amsterdam",
    "location": "Central Station",
    "max_distance_km": 2.0
  }' | python3 -m json.tool

# Test 5: Calculate rental cost
echo ""
echo "💰 Testing rental cost..."
curl -X POST "$BASE_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How much does it cost to rent a bike for 3 hours in Paris?"
  }' | python3 -m json.tool

# Test 6: Geocoding
echo ""
echo "🗺️ Testing geocoding endpoint..."
curl -X POST "$BASE_URL/api/geocode" \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Berlin",
    "address": "Brandenburg Gate"
  }' | python3 -m json.tool

# Test 7: Available models
echo ""
echo "🤖 Testing models endpoint..."
curl -s "$BASE_URL/api/models" | python3 -m json.tool

echo ""
echo "✅ All tests completed!"
echo ""
echo "You can also test interactively at: $BASE_URL/docs"
