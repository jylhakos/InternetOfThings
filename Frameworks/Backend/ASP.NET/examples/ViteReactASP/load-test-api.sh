#!/bin/bash

# Simple Load Testing Script for Contact API
# Tests API performance and caching effectiveness

BASE_URL="https://localhost:7042"
API_URL="$BASE_URL/api/contacts"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🚀 Contact API Load Testing${NC}"
echo "==============================="

# Configuration
REQUESTS=${1:-100}
CONCURRENT=${2:-10}
TEST_DURATION=${3:-30}

echo "Configuration:"
echo "  Requests: $REQUESTS"
echo "  Concurrent: $CONCURRENT"
echo "  Duration: ${TEST_DURATION}s"
echo ""

# Function to create test data
create_test_data() {
    echo "📝 Creating test data..."
    
    local contacts='[
        {"name": "Load Test User 1", "phoneNumber": "+1555001001", "email": "load1@test.com", "category": "Load Test"},
        {"name": "Load Test User 2", "phoneNumber": "+1555001002", "email": "load2@test.com", "category": "Load Test"},
        {"name": "Load Test User 3", "phoneNumber": "+1555001003", "email": "load3@test.com", "category": "Load Test"},
        {"name": "Load Test User 4", "phoneNumber": "+1555001004", "email": "load4@test.com", "category": "Load Test"},
        {"name": "Load Test User 5", "phoneNumber": "+1555001005", "email": "load5@test.com", "category": "Load Test"}
    ]'
    
    curl -k -s -X POST "$API_URL/bulk" \
        -H "Content-Type: application/json" \
        -d "$contacts" > /dev/null
    
    echo -e "${GREEN}✅ Test data created${NC}"
}

# Function to test single request performance
test_single_request() {
    echo "🔍 Testing single request performance..."
    
    echo "First request (cache miss):"
    time curl -k -s "$API_URL" | jq 'length' 2>/dev/null || echo "Response received"
    
    echo "Second request (cache hit):"
    time curl -k -s "$API_URL" | jq 'length' 2>/dev/null || echo "Response received"
    
    echo "Third request (cache hit):"
    time curl -k -s "$API_URL" | jq 'length' 2>/dev/null || echo "Response received"
    
    echo ""
}

# Function to run concurrent requests
run_concurrent_test() {
    echo "⚡ Running concurrent request test..."
    
    local start_time=$(date +%s.%3N)
    local pids=()
    local success_count=0
    local error_count=0
    
    # Function for background requests
    make_request() {
        local id=$1
        local result=$(curl -k -s -w "%{http_code}" "$API_URL" 2>/dev/null)
        local status_code="${result: -3}"
        
        if [[ "$status_code" == "200" ]]; then
            echo "SUCCESS:$id" > "/tmp/load_test_result_$id"
        else
            echo "ERROR:$id:$status_code" > "/tmp/load_test_result_$id"
        fi
    }
    
    # Start concurrent requests
    for i in $(seq 1 $CONCURRENT); do
        make_request $i &
        pids+=($!)
    done
    
    # Wait for all to complete
    for pid in "${pids[@]}"; do
        wait $pid
    done
    
    # Count results
    for i in $(seq 1 $CONCURRENT); do
        if [[ -f "/tmp/load_test_result_$i" ]]; then
            result=$(cat "/tmp/load_test_result_$i")
            if [[ "$result" == SUCCESS:* ]]; then
                ((success_count++))
            else
                ((error_count++))
            fi
            rm -f "/tmp/load_test_result_$i"
        fi
    done
    
    local end_time=$(date +%s.%3N)
    local total_time=$(echo "$end_time - $start_time" | bc -l)
    local avg_time=$(echo "scale=3; $total_time / $CONCURRENT" | bc -l)
    
    echo "Results:"
    echo "  Successful requests: $success_count"
    echo "  Failed requests: $error_count"
    echo "  Total time: ${total_time}s"
    echo "  Average time per request: ${avg_time}s"
    echo ""
}

# Function to run sustained load test
run_sustained_test() {
    echo "🔥 Running sustained load test for ${TEST_DURATION}s..."
    
    local start_time=$(date +%s)
    local end_time=$((start_time + TEST_DURATION))
    local request_count=0
    local success_count=0
    local error_count=0
    local total_response_time=0
    
    while [[ $(date +%s) -lt $end_time ]]; do
        local req_start=$(date +%s.%3N)
        local response=$(curl -k -s -w "%{http_code}" "$API_URL" 2>/dev/null)
        local req_end=$(date +%s.%3N)
        local req_time=$(echo "$req_end - $req_start" | bc -l)
        
        ((request_count++))
        total_response_time=$(echo "$total_response_time + $req_time" | bc -l)
        
        local status_code="${response: -3}"
        if [[ "$status_code" == "200" ]]; then
            ((success_count++))
        else
            ((error_count++))
        fi
        
        # Show progress every 10 requests
        if (( request_count % 10 == 0 )); then
            local elapsed=$(($(date +%s) - start_time))
            echo "  $request_count requests in ${elapsed}s..."
        fi
        
        # Small delay to prevent overwhelming the server
        sleep 0.1
    done
    
    local actual_duration=$(($(date +%s) - start_time))
    local requests_per_sec=$(echo "scale=2; $request_count / $actual_duration" | bc -l)
    local avg_response_time=$(echo "scale=3; $total_response_time / $request_count" | bc -l)
    local success_rate=$(echo "scale=2; $success_count * 100 / $request_count" | bc -l)
    
    echo -e "${CYAN}Sustained Load Test Results:${NC}"
    echo "  Duration: ${actual_duration}s"
    echo "  Total requests: $request_count"
    echo "  Successful: $success_count"
    echo "  Failed: $error_count"
    echo "  Requests/second: $requests_per_sec"
    echo "  Success rate: ${success_rate}%"
    echo "  Average response time: ${avg_response_time}s"
    echo ""
}

# Function to test different endpoints
test_endpoints() {
    echo "🎯 Testing different endpoints..."
    
    local endpoints=(
        "$API_URL|Get All Contacts"
        "$API_URL/stats|Statistics"
        "$API_URL/search/Load|Search"
        "$BASE_URL/health|Health Check"
    )
    
    for endpoint_info in "${endpoints[@]}"; do
        IFS='|' read -r endpoint name <<< "$endpoint_info"
        
        echo "Testing $name..."
        local start_time=$(date +%s.%3N)
        local response=$(curl -k -s -w "%{http_code}" "$endpoint" 2>/dev/null)
        local end_time=$(date +%s.%3N)
        local response_time=$(echo "$end_time - $start_time" | bc -l)
        local status_code="${response: -3}"
        
        if [[ "$status_code" == "200" ]]; then
            echo -e "  ${GREEN}✅ $name: ${response_time}s${NC}"
        else
            echo -e "  ${YELLOW}⚠️  $name: ${response_time}s (Status: $status_code)${NC}"
        fi
    done
    echo ""
}

# Function to cleanup
cleanup() {
    echo "🧹 Cleaning up test data..."
    
    # Clear cache
    curl -k -s -X DELETE "$API_URL/cache" > /dev/null
    
    echo -e "${GREEN}✅ Cleanup completed${NC}"
}

# Main execution
main() {
    echo "Starting load testing at $(date)"
    echo ""
    
    # Check if server is running
    echo "🔍 Checking server availability..."
    if ! curl -k -s -f "$BASE_URL/health" > /dev/null; then
        echo -e "${YELLOW}⚠️  Server is not running or not responding${NC}"
        echo "Please start the server with: cd Server && dotnet run"
        exit 1
    fi
    echo -e "${GREEN}✅ Server is running${NC}"
    echo ""
    
    # Run tests
    create_test_data
    test_single_request
    test_endpoints
    run_concurrent_test
    run_sustained_test
    cleanup
    
    echo -e "${GREEN}🎉 Load testing completed!${NC}"
}

# Check dependencies
if ! command -v bc &> /dev/null; then
    echo "bc is required but not installed. Please install it: sudo apt install bc"
    exit 1
fi

# Run main function
main "$@"
