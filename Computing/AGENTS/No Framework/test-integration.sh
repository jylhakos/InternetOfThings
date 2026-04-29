#!/bin/bash

# Integration Test Script for AI Agent + Open WebUI
# Tests the complete stack including weather queries

set -e

BASE_URL_AGENT="http://localhost:8000"
BASE_URL_WEBUI="http://localhost:3000"

echo "🧪 AI Agent + Open WebUI Integration Tests"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

info() {
    echo -e "ℹ️  $1"
}

# Test function
test_endpoint() {
    local description="$1"
    local method="$2"
    local url="$3"
    local data="$4"
    local expected_status="$5"
    
    info "Testing: $description"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "HTTP_CODE:%{http_code}" "$url" || echo "HTTP_CODE:000")
    else
        response=$(curl -s -w "HTTP_CODE:%{http_code}" -X "$method" -H "Content-Type: application/json" -d "$data" "$url" || echo "HTTP_CODE:000")
    fi
    
    http_code=$(echo "$response" | grep -o "HTTP_CODE:[0-9]*" | cut -d: -f2)
    body=$(echo "$response" | sed 's/HTTP_CODE:[0-9]*$//')
    
    if [ "$http_code" = "$expected_status" ]; then
        success "$description (HTTP $http_code)"
        return 0
    else
        error "$description (HTTP $http_code, expected $expected_status)"
        echo "Response: $body"
        return 1
    fi
}

# Check prerequisites
echo ""
info "Checking prerequisites..."

if ! command -v curl &> /dev/null; then
    error "curl is required but not installed"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    error "Docker is required but not installed"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    error "Python 3 is required but not installed"
    exit 1
fi

success "All prerequisites met"

# Test AI Agent directly
echo ""
echo "🤖 Testing AI Agent (Direct)"
echo "============================"

test_endpoint "AI Agent Health" "GET" "$BASE_URL_AGENT/health" "" "200"
test_endpoint "AI Agent Models" "GET" "$BASE_URL_AGENT/v1/models" "" "200"

# Test greeting
greeting_data='{
  "messages": [
    {"role": "user", "content": "Hello, how are you?"}
  ],
  "temperature": 0.7
}'
test_endpoint "AI Agent Greeting" "POST" "$BASE_URL_AGENT/v1/chat/completions" "$greeting_data" "200"

# Test weather query
weather_data='{
  "messages": [
    {"role": "user", "content": "What is the temperature in London?"}
  ],
  "temperature": 0.7
}'
test_endpoint "AI Agent Weather Query" "POST" "$BASE_URL_AGENT/v1/chat/completions" "$weather_data" "200"

# Test Open WebUI
echo ""
echo "🌐 Testing Open WebUI"
echo "====================="

# Check if Open WebUI is running
if ! curl -s "$BASE_URL_WEBUI" > /dev/null; then
    warning "Open WebUI is not running. Starting it..."
    ./webui-manage.sh start
    sleep 10
fi

test_endpoint "Open WebUI Root" "GET" "$BASE_URL_WEBUI/" "" "200"

# Test integration through Open WebUI
echo ""
echo "🔗 Testing Integration (AI Agent via Open WebUI)"
echo "==============================================="

# Test models endpoint through WebUI
info "Testing model listing through Open WebUI..."
MODELS_RESPONSE=$(curl -s "$BASE_URL_WEBUI/api/models" 2>/dev/null || echo "{}")
if echo "$MODELS_RESPONSE" | grep -q "ai-agent-no-framework"; then
    success "AI Agent model detected in Open WebUI"
else
    warning "AI Agent model not found in Open WebUI models list"
    echo "Models response: $MODELS_RESPONSE"
fi

# Test chat through WebUI API
webui_chat_data='{
  "messages": [
    {"role": "user", "content": "Hello from Open WebUI integration test!"}
  ],
  "model": "ai-agent-no-framework",
  "temperature": 0.7
}'

info "Testing chat completion through Open WebUI..."
CHAT_RESPONSE=$(curl -s -X POST "$BASE_URL_WEBUI/api/chat/completions" \
    -H "Content-Type: application/json" \
    -d "$webui_chat_data" 2>/dev/null || echo '{"error":"failed"}')

if echo "$CHAT_RESPONSE" | grep -q "choices"; then
    success "Chat completion works through Open WebUI"
else
    warning "Chat completion through Open WebUI may not be working"
    echo "Chat response: $CHAT_RESPONSE"
fi

# Specific weather test through WebUI
webui_weather_data='{
  "messages": [
    {"role": "user", "content": "What is the temperature in Tokyo right now?"}
  ],
  "model": "ai-agent-no-framework",
  "temperature": 0.7
}'

info "Testing weather query through Open WebUI..."
WEATHER_RESPONSE=$(curl -s -X POST "$BASE_URL_WEBUI/api/chat/completions" \
    -H "Content-Type: application/json" \
    -d "$webui_weather_data" 2>/dev/null || echo '{"error":"failed"}')

if echo "$WEATHER_RESPONSE" | grep -q "temperature"; then
    success "Weather queries work through Open WebUI"
    # Extract and display the weather response
    WEATHER_CONTENT=$(echo "$WEATHER_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('choices', [{}])[0].get('message', {}).get('content', 'No content'))" 2>/dev/null || echo "Could not parse response")
    info "Weather response: $WEATHER_CONTENT"
else
    warning "Weather query through Open WebUI may not be working"
fi

# Performance test
echo ""
echo "⚡ Performance Test"
echo "=================="

info "Testing concurrent requests..."
start_time=$(date +%s)

# Send 5 concurrent requests
for i in {1..5}; do
    (curl -s -X POST "$BASE_URL_AGENT/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -d '{"messages":[{"role":"user","content":"Quick test '$i'"}],"temperature":0.3}' \
        > /tmp/test_response_$i.json) &
done

# Wait for all to complete
wait

end_time=$(date +%s)
duration=$((end_time - start_time))

success_count=0
for i in {1..5}; do
    if [ -f "/tmp/test_response_$i.json" ] && grep -q "choices" "/tmp/test_response_$i.json"; then
        ((success_count++))
    fi
done

success "Concurrent test completed: $success_count/5 requests succeeded in ${duration}s"

# Cleanup temp files
rm -f /tmp/test_response_*.json

# Service status summary
echo ""
echo "📊 Service Status Summary"
echo "========================"

# AI Agent status
if curl -s "$BASE_URL_AGENT/health" | python3 -c "import sys, json; data=json.load(sys.stdin); print('Status:', data.get('status', 'unknown'))" 2>/dev/null; then
    success "AI Agent is healthy"
else
    error "AI Agent has issues"
fi

# Ollama status
if curl -s http://localhost:11434/api/tags > /dev/null; then
    success "Ollama is running"
else
    warning "Ollama may not be running"
fi

# Open WebUI status
if curl -s "$BASE_URL_WEBUI/" > /dev/null; then
    success "Open WebUI is accessible"
else
    error "Open WebUI is not accessible"
fi

# Final recommendations
echo ""
echo "🎯 Test Results & Recommendations"
echo "================================="

if curl -s "$BASE_URL_AGENT/health" > /dev/null && curl -s "$BASE_URL_WEBUI/" > /dev/null; then
    success "All services are running correctly!"
    echo ""
    info "You can now:"
    echo "  • Access Open WebUI at: $BASE_URL_WEBUI"
    echo "  • Chat with your AI agent through the web interface"
    echo "  • Test weather queries like: 'What's the temperature in Paris?'"
    echo "  • Use the AI agent API directly at: $BASE_URL_AGENT"
else
    error "Some services have issues. Check the logs:"
    echo "  • AI Agent logs: Check terminal where 'python src/index.py' is running"
    echo "  • Open WebUI logs: ./webui-manage.sh logs"
    echo "  • Ollama logs: Check ollama serve terminal"
fi

echo ""
info "For ongoing monitoring, use:"
echo "  • make health       - Quick health check"
echo "  • make webui-health - Comprehensive health check"
echo "  • make webui-logs   - View Open WebUI logs"

echo ""
success "Integration testing completed!"
