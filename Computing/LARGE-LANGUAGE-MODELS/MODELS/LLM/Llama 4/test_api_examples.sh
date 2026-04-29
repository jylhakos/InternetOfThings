#!/bin/bash
# Test script for AI Agent API endpoints
# Tests various functionality including weather queries, greetings, and general Q&A

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

API_BASE="http://localhost:8000"

print_test() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check if AI Agent is running
check_agent() {
    print_test "Checking AI Agent Status"
    if curl -s "$API_BASE/health" > /dev/null 2>&1; then
        print_success "AI Agent is running"
        return 0
    else
        print_error "AI Agent is not running at $API_BASE"
        print_info "Please start the AI Agent first: python src/index.py"
        return 1
    fi
}

# Test health endpoint
test_health() {
    print_test "Health Check"
    response=$(curl -s "$API_BASE/health")
    
    if echo "$response" | grep -q "healthy"; then
        print_success "Health check passed"
        echo "$response" | jq '.' 2>/dev/null || echo "$response"
    else
        print_error "Health check failed"
        echo "$response"
    fi
    echo
}

# Test greeting functionality
test_greeting() {
    print_test "Greeting Test"
    print_info "Sending: 'Hello! How are you today?'"
    
    response=$(curl -s -X POST "$API_BASE/v1/chat/completions" \
      -H "Content-Type: application/json" \
      -d '{
        "messages": [{"role": "user", "content": "Hello! How are you today?"}],
        "temperature": 0.7
      }')
    
    if echo "$response" | grep -q "choices"; then
        print_success "Greeting test passed"
        content=$(echo "$response" | jq -r '.choices[0].message.content' 2>/dev/null || echo "Could not parse response")
        echo "AI Response: $content"
    else
        print_error "Greeting test failed"
        echo "$response"
    fi
    echo
}

# Test weather functionality - single city
test_weather_single() {
    print_test "Weather Test: Single City"
    print_info "Sending: 'What is the temperature in London?'"
    
    response=$(curl -s -X POST "$API_BASE/v1/chat/completions" \
      -H "Content-Type: application/json" \
      -d '{
        "messages": [{"role": "user", "content": "What is the temperature in London?"}],
        "temperature": 0.7
      }')
    
    if echo "$response" | grep -q "choices"; then
        print_success "Single city weather test passed"
        content=$(echo "$response" | jq -r '.choices[0].message.content' 2>/dev/null || echo "Could not parse response")
        echo "AI Response: $content"
    else
        print_error "Single city weather test failed"
        echo "$response"
    fi
    echo
}

# Test weather functionality - multiple cities
test_weather_multiple() {
    print_test "Weather Test: Multiple Cities"
    print_info "Sending: 'Compare weather in Tokyo, New York, and Berlin'"
    
    response=$(curl -s -X POST "$API_BASE/v1/chat/completions" \
      -H "Content-Type: application/json" \
      -d '{
        "messages": [{"role": "user", "content": "Compare weather in Tokyo, New York, and Berlin"}],
        "temperature": 0.7
      }')
    
    if echo "$response" | grep -q "choices"; then
        print_success "Multiple cities weather test passed"
        content=$(echo "$response" | jq -r '.choices[0].message.content' 2>/dev/null || echo "Could not parse response")
        echo "AI Response: $content"
    else
        print_error "Multiple cities weather test failed"
        echo "$response"
    fi
    echo
}

# Test general Q&A functionality
test_general_qa() {
    print_test "General Q&A Test"
    print_info "Sending: 'Explain artificial intelligence in 50 words'"
    
    response=$(curl -s -X POST "$API_BASE/v1/chat/completions" \
      -H "Content-Type: application/json" \
      -d '{
        "messages": [{"role": "user", "content": "Explain artificial intelligence in 50 words"}],
        "temperature": 0.7
      }')
    
    if echo "$response" | grep -q "choices"; then
        print_success "General Q&A test passed"
        content=$(echo "$response" | jq -r '.choices[0].message.content' 2>/dev/null || echo "Could not parse response")
        echo "AI Response: $content"
    else
        print_error "General Q&A test failed"
        echo "$response"
    fi
    echo
}

# Test model capabilities
test_model_info() {
    print_test "Model Information"
    
    response=$(curl -s "$API_BASE/v1/models")
    
    if echo "$response" | grep -q "data"; then
        print_success "Model info retrieved"
        echo "$response" | jq '.' 2>/dev/null || echo "$response"
    else
        print_error "Could not retrieve model information"
        echo "$response"
    fi
    echo
}

# Test OpenAI compatibility
test_openai_compatibility() {
    print_test "OpenAI API Compatibility Test"
    print_info "Testing standard OpenAI format with conversation context"
    
    response=$(curl -s -X POST "$API_BASE/v1/chat/completions" \
      -H "Content-Type: application/json" \
      -d '{
        "model": "ai-agent-llama4-scout",
        "messages": [
          {"role": "system", "content": "You are a helpful assistant."},
          {"role": "user", "content": "Hello"},
          {"role": "assistant", "content": "Hello! How can I help you today?"},
          {"role": "user", "content": "What can you do?"}
        ],
        "temperature": 0.7,
        "max_tokens": 200
      }')
    
    if echo "$response" | grep -q "choices"; then
        print_success "OpenAI compatibility test passed"
        content=$(echo "$response" | jq -r '.choices[0].message.content' 2>/dev/null || echo "Could not parse response")
        echo "AI Response: $content"
        
        # Check for metadata
        if echo "$response" | grep -q "metadata"; then
            print_info "Enhanced metadata detected (Llama 4 features)"
            echo "$response" | jq '.metadata' 2>/dev/null || true
        fi
    else
        print_error "OpenAI compatibility test failed"
        echo "$response"
    fi
    echo
}

# Main execution
main() {
    echo -e "${GREEN}🚀 Starting AI Agent API Tests...${NC}"
    echo "Testing API at: $API_BASE"
    echo
    
    # Check if jq is available for JSON parsing
    if ! command -v jq &> /dev/null; then
        print_info "jq not found. Install with: sudo apt install jq (responses will show raw JSON)"
    fi
    
    # Check agent status first
    if ! check_agent; then
        exit 1
    fi
    
    echo
    
    # Run all tests
    test_health
    test_model_info  
    test_greeting
    test_weather_single
    test_weather_multiple
    test_general_qa
    test_openai_compatibility
    
    echo -e "${GREEN}🏁 Testing Complete!${NC}"
    echo
    echo "Next steps:"
    echo "1. Open WebUI: http://localhost:3000"
    echo "2. API Documentation: http://localhost:8000/docs"
    echo "3. Health Check: $API_BASE/health"
}

# Run main function
main "$@"
