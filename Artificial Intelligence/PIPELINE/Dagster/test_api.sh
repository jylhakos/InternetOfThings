#!/bin/bash
"""
API Testing Script for BERT Text Classification
Tests all endpoints with curl commands and validates responses
"""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# API base URL (change if needed)
API_URL="http://localhost:8000"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}BERT Text Classification API Tests${NC}"
echo -e "${BLUE}========================================${NC}"

# Function to test endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    echo -e "\n${YELLOW}Testing: ${description}${NC}"
    echo -e "${BLUE}Endpoint: ${method} ${endpoint}${NC}"
    
    if [ -n "$data" ]; then
        echo -e "${BLUE}Data: ${data}${NC}"
        response=$(curl -s -w "\n%{http_code}" -X ${method} \
            -H "Content-Type: application/json" \
            -d "${data}" \
            "${API_URL}${endpoint}")
    else
        response=$(curl -s -w "\n%{http_code}" -X ${method} "${API_URL}${endpoint}")
    fi
    
    # Split response and status code
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    echo -e "${BLUE}Response:${NC}"
    echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
    
    if [[ $status_code -ge 200 && $status_code -lt 300 ]]; then
        echo -e "${GREEN}✓ Success (Status: ${status_code})${NC}"
    else
        echo -e "${RED}✗ Failed (Status: ${status_code})${NC}"
    fi
    
    echo -e "${BLUE}----------------------------------------${NC}"
}

# Wait for API to be ready
echo -e "${YELLOW}Waiting for API to be ready...${NC}"
for i in {1..30}; do
    if curl -s "${API_URL}/health" > /dev/null; then
        echo -e "${GREEN}✓ API is ready!${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}✗ API not responding after 30 seconds${NC}"
        exit 1
    fi
    sleep 1
done

# Test 1: Root endpoint
test_endpoint "GET" "/" "" "Root endpoint"

# Test 2: Health check
test_endpoint "GET" "/health" "" "Health check"

# Test 3: Model info
test_endpoint "GET" "/model/info" "" "Model information"

# Test 4: Single text classification (basic)
test_endpoint "POST" "/classify" \
    '{"text": "I absolutely love this product! It works perfectly!"}' \
    "Single positive text classification"

# Test 5: Single text classification with confidence
test_endpoint "POST" "/classify" \
    '{"text": "This is terrible and completely useless.", "return_confidence": true}' \
    "Single negative text with confidence"

# Test 6: Batch text classification
test_endpoint "POST" "/classify/batch" \
    '{"texts": ["I love this!", "This is bad.", "Pretty good product.", "Worst ever!"], "return_confidence": true}' \
    "Batch text classification"

# Test 7: Demo endpoint
test_endpoint "GET" "/classify/demo" "" "Demo classifications"

# Test 8: Error handling - empty text
test_endpoint "POST" "/classify" \
    '{"text": ""}' \
    "Error handling - empty text (should fail)"

# Test 9: Error handling - too long text
long_text=$(python3 -c "print('a' * 1000)")
test_endpoint "POST" "/classify" \
    "{\"text\": \"${long_text}\"}" \
    "Error handling - very long text"

# Test 10: Error handling - invalid JSON
echo -e "\n${YELLOW}Testing: Invalid JSON (should fail)${NC}"
echo -e "${BLUE}Endpoint: POST /classify${NC}"
echo -e "${BLUE}Data: Invalid JSON${NC}"
response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d '{"text": "test"' \
    "${API_URL}/classify")
status_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')
echo -e "${BLUE}Response:${NC}"
echo "$body"
if [[ $status_code -ge 400 ]]; then
    echo -e "${GREEN}✓ Correctly handled invalid JSON (Status: ${status_code})${NC}"
else
    echo -e "${RED}✗ Should have failed with invalid JSON (Status: ${status_code})${NC}"
fi
echo -e "${BLUE}----------------------------------------${NC}"

echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}API Testing Complete!${NC}"
echo -e "${BLUE}========================================${NC}"

# Additional curl command examples for manual testing
echo -e "\n${YELLOW}Manual Testing Examples:${NC}"
echo -e "${BLUE}========================================${NC}"

cat << 'EOF'

# Basic text classification
curl -X POST "http://localhost:8000/classify" \
  -H "Content-Type: application/json" \
  -d '{"text": "I really enjoyed this movie!"}'

# Text classification with confidence scores
curl -X POST "http://localhost:8000/classify" \
  -H "Content-Type: application/json" \
  -d '{"text": "This product is amazing!", "return_confidence": true}'

# Batch classification
curl -X POST "http://localhost:8000/classify/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Great service!",
      "Terrible experience.",
      "It was okay."
    ],
    "return_confidence": true
  }'

# Health check
curl -X GET "http://localhost:8000/health"

# Model information
curl -X GET "http://localhost:8000/model/info"

# API documentation (open in browser)
# http://localhost:8000/docs

# Alternative documentation
# http://localhost:8000/redoc

EOF
