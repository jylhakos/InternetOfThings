#!/bin/bash

# cURL test cases for RNN Text Generation API
# Run this script to test all API endpoints

API_URL="http://localhost:5000"
CONTENT_TYPE="Content-Type: application/json"

echo "======================================"
echo "RNN Text Generation API Test Suite"
echo "======================================"
echo "API URL: $API_URL"
echo "Make sure the API server is running!"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print test headers
print_test() {
    echo -e "${BLUE}===============================================${NC}"
    echo -e "${BLUE}Test $1: $2${NC}"
    echo -e "${BLUE}===============================================${NC}"
}

# Function to check if API is running
check_api() {
    echo -e "${YELLOW}Checking if API is running...${NC}"
    response=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/health")
    if [ "$response" -eq 200 ]; then
        echo -e "${GREEN}✓ API is running${NC}"
        return 0
    else
        echo -e "${RED}✗ API is not responding (HTTP $response)${NC}"
        echo -e "${RED}Please start the API server first:${NC}"
        echo -e "${RED}  python api/app.py --checkpoint checkpoints/best_model.pth${NC}"
        return 1
    fi
}

# Test 1: Health Check
test_health() {
    print_test "1" "Health Check"
    
    echo "Command:"
    echo "curl -X GET $API_URL/health"
    echo ""
    
    response=$(curl -s -w "\nHTTP Status: %{http_code}\n" "$API_URL/health")
    echo "Response:"
    echo "$response"
    echo ""
}

# Test 2: Model Info
test_model_info() {
    print_test "2" "Model Information"
    
    echo "Command:"
    echo "curl -X GET $API_URL/model/info"
    echo ""
    
    response=$(curl -s -w "\nHTTP Status: %{http_code}\n" "$API_URL/model/info")
    echo "Response:"
    echo "$response"
    echo ""
}

# Test 3: Basic Text Generation
test_basic_generation() {
    print_test "3" "Basic Text Generation"
    
    echo "Command:"
    echo "curl -X POST $API_URL/generate -H \"$CONTENT_TYPE\" -d '{\"prompt\": \"Once upon a time\", \"max_length\": 30}'"
    echo ""
    
    response=$(curl -s -w "\nHTTP Status: %{http_code}\n" -X POST "$API_URL/generate" \
        -H "$CONTENT_TYPE" \
        -d '{"prompt": "Once upon a time", "max_length": 30}')
    echo "Response:"
    echo "$response"
    echo ""
}

# Test 4: Generation with Temperature Control
test_temperature_generation() {
    print_test "4" "Temperature-Controlled Generation"
    
    echo "Command:"
    echo "curl -X POST $API_URL/generate -H \"$CONTENT_TYPE\" -d '{\"prompt\": \"The future of artificial intelligence\", \"max_length\": 50, \"temperature\": 1.2}'"
    echo ""
    
    response=$(curl -s -w "\nHTTP Status: %{http_code}\n" -X POST "$API_URL/generate" \
        -H "$CONTENT_TYPE" \
        -d '{"prompt": "The future of artificial intelligence", "max_length": 50, "temperature": 1.2}')
    echo "Response:"
    echo "$response"
    echo ""
}

# Test 5: Creative Writing with Top-k Sampling
test_topk_generation() {
    print_test "5" "Top-k Sampling Generation"
    
    echo "Command:"
    echo "curl -X POST $API_URL/generate -H \"$CONTENT_TYPE\" -d '{\"prompt\": \"In a world where technology\", \"max_length\": 40, \"temperature\": 0.9, \"top_k\": 20}'"
    echo ""
    
    response=$(curl -s -w "\nHTTP Status: %{http_code}\n" -X POST "$API_URL/generate" \
        -H "$CONTENT_TYPE" \
        -d '{"prompt": "In a world where technology", "max_length": 40, "temperature": 0.9, "top_k": 20}')
    echo "Response:"
    echo "$response"
    echo ""
}

# Test 6: Multiple Samples Generation
test_multiple_samples() {
    print_test "6" "Multiple Samples Generation"
    
    echo "Command:"
    echo "curl -X POST $API_URL/generate/multiple -H \"$CONTENT_TYPE\" -d '{\"prompt\": \"Machine learning algorithms\", \"max_length\": 30, \"num_samples\": 3}'"
    echo ""
    
    response=$(curl -s -w "\nHTTP Status: %{http_code}\n" -X POST "$API_URL/generate/multiple" \
        -H "$CONTENT_TYPE" \
        -d '{"prompt": "Machine learning algorithms", "max_length": 30, "num_samples": 3}')
    echo "Response:"
    echo "$response"
    echo ""
}

# Test 7: Empty Prompt Handling
test_empty_prompt() {
    print_test "7" "Empty Prompt Handling"
    
    echo "Command:"
    echo "curl -X POST $API_URL/generate -H \"$CONTENT_TYPE\" -d '{\"prompt\": \"\", \"max_length\": 20}'"
    echo ""
    
    response=$(curl -s -w "\nHTTP Status: %{http_code}\n" -X POST "$API_URL/generate" \
        -H "$CONTENT_TYPE" \
        -d '{"prompt": "", "max_length": 20}')
    echo "Response:"
    echo "$response"
    echo ""
}

# Test 8: Long Text Generation
test_long_generation() {
    print_test "8" "Long Text Generation"
    
    echo "Command:"
    echo "curl -X POST $API_URL/generate -H \"$CONTENT_TYPE\" -d '{\"prompt\": \"Deep learning neural networks\", \"max_length\": 100, \"temperature\": 0.7, \"top_k\": 50}'"
    echo ""
    
    response=$(curl -s -w "\nHTTP Status: %{http_code}\n" -X POST "$API_URL/generate" \
        -H "$CONTENT_TYPE" \
        -d '{"prompt": "Deep learning neural networks", "max_length": 100, "temperature": 0.7, "top_k": 50}')
    echo "Response:"
    echo "$response"
    echo ""
}

# Test 9: Error Handling - Invalid Parameters
test_invalid_parameters() {
    print_test "9" "Error Handling - Invalid Parameters"
    
    echo "Command:"
    echo "curl -X POST $API_URL/generate -H \"$CONTENT_TYPE\" -d '{\"prompt\": \"test\", \"max_length\": -5}'"
    echo ""
    
    response=$(curl -s -w "\nHTTP Status: %{http_code}\n" -X POST "$API_URL/generate" \
        -H "$CONTENT_TYPE" \
        -d '{"prompt": "test", "max_length": -5}')
    echo "Response:"
    echo "$response"
    echo ""
}

# Test 10: Error Handling - Invalid JSON
test_invalid_json() {
    print_test "10" "Error Handling - Invalid JSON"
    
    echo "Command:"
    echo "curl -X POST $API_URL/generate -H \"$CONTENT_TYPE\" -d 'invalid json'"
    echo ""
    
    response=$(curl -s -w "\nHTTP Status: %{http_code}\n" -X POST "$API_URL/generate" \
        -H "$CONTENT_TYPE" \
        -d 'invalid json')
    echo "Response:"
    echo "$response"
    echo ""
}

# Performance Test
test_performance() {
    print_test "Performance" "Response Time Test"
    
    echo "Testing response times for 5 requests..."
    echo ""
    
    for i in {1..5}; do
        echo "Request $i:"
        start_time=$(date +%s.%N)
        response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL/generate" \
            -H "$CONTENT_TYPE" \
            -d '{"prompt": "Performance test", "max_length": 20}')
        end_time=$(date +%s.%N)
        duration=$(echo "$end_time - $start_time" | bc)
        echo "  HTTP Status: $response, Time: ${duration}s"
    done
    echo ""
}

# Main execution
main() {
    echo -e "${YELLOW}Starting API tests...${NC}"
    echo ""
    
    # Check if API is running
    if ! check_api; then
        exit 1
    fi
    
    echo ""
    
    # Run all tests
    test_health
    test_model_info
    test_basic_generation
    test_temperature_generation
    test_topk_generation
    test_multiple_samples
    test_empty_prompt
    test_long_generation
    test_invalid_parameters
    test_invalid_json
    test_performance
    
    echo -e "${GREEN}===============================================${NC}"
    echo -e "${GREEN}All tests completed!${NC}"
    echo -e "${GREEN}===============================================${NC}"
    echo ""
    echo "Test Summary:"
    echo "✓ Health check and model info"
    echo "✓ Basic text generation"
    echo "✓ Advanced generation parameters"
    echo "✓ Multiple samples"
    echo "✓ Error handling"
    echo "✓ Performance testing"
    echo ""
    echo "For interactive testing, try:"
    echo "  curl -X POST $API_URL/generate -H \"$CONTENT_TYPE\" -d '{\"prompt\":\"Your prompt here\", \"max_length\":50}'"
}

# Run main function
main
