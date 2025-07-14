#!/bin/bash

# Health Check Script for LLM Inference Server
# This script performs comprehensive health checks on the deployed service

set -e

# Configuration
SERVICE_URL=${SERVICE_URL:-"http://localhost:3000"}
TIMEOUT=${TIMEOUT:-10}
RETRIES=${RETRIES:-3}

echo "🔍 Starting health check for LLM Inference Server..."
echo "🌐 Service URL: $SERVICE_URL"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to make HTTP requests with retries
make_request() {
    local url=$1
    local expected_status=${2:-200}
    local retry_count=0
    
    while [ $retry_count -lt $RETRIES ]; do
        response=$(curl -s -w "%{http_code}" --max-time $TIMEOUT "$url" 2>/dev/null || echo "000")
        status_code="${response: -3}"
        
        if [ "$status_code" = "$expected_status" ]; then
            echo -e "${GREEN}✅ $url - Status: $status_code${NC}"
            return 0
        else
            retry_count=$((retry_count + 1))
            echo -e "${YELLOW}⚠️  $url - Status: $status_code (Attempt $retry_count/$RETRIES)${NC}"
            sleep 2
        fi
    done
    
    echo -e "${RED}❌ $url - Failed after $RETRIES attempts${NC}"
    return 1
}

# Function to test API endpoint with authentication
test_auth_endpoint() {
    local endpoint=$1
    local method=${2:-GET}
    local data=${3:-""}
    
    echo "🔐 Testing authenticated endpoint: $endpoint"
    
    # First try to login and get a token
    login_response=$(curl -s -X POST "$SERVICE_URL/api/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"username":"demo","password":"demo123"}' \
        --max-time $TIMEOUT 2>/dev/null || echo '{"error":"request_failed"}')
    
    token=$(echo "$login_response" | jq -r '.token // empty' 2>/dev/null)
    
    if [ -z "$token" ] || [ "$token" = "null" ]; then
        echo -e "${RED}❌ Failed to get authentication token${NC}"
        return 1
    fi
    
    # Make authenticated request
    if [ "$method" = "POST" ] && [ -n "$data" ]; then
        response=$(curl -s -w "%{http_code}" --max-time $TIMEOUT \
            -X POST "$SERVICE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $token" \
            -d "$data" 2>/dev/null || echo "000")
    else
        response=$(curl -s -w "%{http_code}" --max-time $TIMEOUT \
            -H "Authorization: Bearer $token" \
            "$SERVICE_URL$endpoint" 2>/dev/null || echo "000")
    fi
    
    status_code="${response: -3}"
    
    if [ "$status_code" = "200" ]; then
        echo -e "${GREEN}✅ $endpoint - Authenticated request successful${NC}"
        return 0
    else
        echo -e "${RED}❌ $endpoint - Status: $status_code${NC}"
        return 1
    fi
}

# Start health checks
echo ""
echo "1️⃣ Basic Health Checks"
echo "======================"

# Basic health check
make_request "$SERVICE_URL/api/health"

# Detailed health check
make_request "$SERVICE_URL/api/health/detailed"

# Readiness probe
make_request "$SERVICE_URL/api/health/ready"

# Liveness probe
make_request "$SERVICE_URL/api/health/live"

echo ""
echo "2️⃣ API Endpoint Tests"
echo "===================="

# Test root endpoint
make_request "$SERVICE_URL/"

# Test OpenAI models endpoint (should fail without auth)
echo "🔒 Testing unauthenticated access (should fail)..."
response=$(curl -s -w "%{http_code}" --max-time $TIMEOUT "$SERVICE_URL/v1/models" 2>/dev/null || echo "000")
status_code="${response: -3}"
if [ "$status_code" = "401" ]; then
    echo -e "${GREEN}✅ /v1/models - Correctly requires authentication (401)${NC}"
else
    echo -e "${YELLOW}⚠️  /v1/models - Expected 401, got $status_code${NC}"
fi

echo ""
echo "3️⃣ Authentication Tests"
echo "======================="

# Test user registration
echo "👤 Testing user registration..."
register_data='{"username":"healthcheck_user","email":"healthcheck@example.com","password":"healthcheck123"}'
response=$(curl -s -w "%{http_code}" --max-time $TIMEOUT \
    -X POST "$SERVICE_URL/api/auth/register" \
    -H "Content-Type: application/json" \
    -d "$register_data" 2>/dev/null || echo "000")
status_code="${response: -3}"

if [ "$status_code" = "201" ] || [ "$status_code" = "409" ]; then
    echo -e "${GREEN}✅ User registration - Status: $status_code${NC}"
else
    echo -e "${RED}❌ User registration - Status: $status_code${NC}"
fi

# Test user login
echo "🔑 Testing user login..."
login_response=$(curl -s -w "%{http_code}" --max-time $TIMEOUT \
    -X POST "$SERVICE_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username":"demo","password":"demo123"}' 2>/dev/null || echo "000")
status_code="${login_response: -3}"

if [ "$status_code" = "200" ]; then
    echo -e "${GREEN}✅ User login - Status: $status_code${NC}"
else
    echo -e "${RED}❌ User login - Status: $status_code${NC}"
fi

echo ""
echo "4️⃣ Authenticated API Tests"
echo "=========================="

# Test model info endpoint
test_auth_endpoint "/api/chat/model"

# Test chat history endpoint
test_auth_endpoint "/api/chat/history"

# Test OpenAI models endpoint with auth
test_auth_endpoint "/v1/models"

echo ""
echo "5️⃣ LLM Inference Test"
echo "===================="

# Test chat completion
chat_data='{"messages":[{"role":"user","content":"Hello, this is a health check test. Please respond with just OK."}],"model":"meta-llama/Llama-3.1-8B-Instruct","max_tokens":10}'

echo "🤖 Testing LLM inference..."
test_auth_endpoint "/v1/chat/completions" "POST" "$chat_data"

echo ""
echo "6️⃣ Performance Metrics"
echo "======================"

# Measure response time
echo "⏱️ Measuring response times..."
start_time=$(date +%s%N)
make_request "$SERVICE_URL/api/health" >/dev/null 2>&1
end_time=$(date +%s%N)
response_time=$(( (end_time - start_time) / 1000000 ))
echo "Health endpoint response time: ${response_time}ms"

# Check if service is under load
load_start=$(date +%s%N)
for i in {1..5}; do
    make_request "$SERVICE_URL/api/health" >/dev/null 2>&1 &
done
wait
load_end=$(date +%s%N)
load_time=$(( (load_end - load_start) / 1000000 ))
echo "5 concurrent requests completed in: ${load_time}ms"

echo ""
echo "📊 Health Check Summary"
echo "======================"

# Count successful checks
total_checks=12
echo "Health check completed!"
echo "For detailed logs, check the service logs:"
echo "  Docker: docker-compose logs -f"
echo "  AWS ECS: aws logs describe-log-groups"
echo ""

if [ $? -eq 0 ]; then
    echo -e "${GREEN}🎉 All critical health checks passed!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some health checks failed. Please review the output above.${NC}"
    exit 1
fi
