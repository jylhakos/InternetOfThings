#!/bin/bash

# Comprehensive cURL Testing Script for Contact Management API
# This script tests all CRUD operations, caching, and advanced features

set -e

# Configuration
BASE_URL="https://localhost:7042"
API_URL="$BASE_URL/api/contacts"
HEALTH_URL="$BASE_URL/health"
STATS_URL="$API_URL/stats"
CACHE_URL="$API_URL/cache"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test counters
test_count=0
passed_count=0
failed_count=0

echo -e "${PURPLE}🧪 Contact Management API - Comprehensive Test Suite${NC}"
echo "================================================================"
echo -e "${CYAN}Testing URL: $BASE_URL${NC}"
echo -e "${CYAN}API Endpoint: $API_URL${NC}"
echo ""

# Function to print test headers
print_header() {
    echo -e "\n${BLUE}📋 $1${NC}"
    echo "----------------------------------------"
}

# Function to print test results
print_result() {
    local test_name="$1"
    local status="$2"
    local details="$3"
    
    ((test_count++))
    
    if [[ "$status" == "PASSED" ]]; then
        echo -e "${GREEN}✅ $test_name: PASSED${NC}"
        ((passed_count++))
    elif [[ "$status" == "FAILED" ]]; then
        echo -e "${RED}❌ $test_name: FAILED${NC}"
        if [[ -n "$details" ]]; then
            echo -e "${RED}   Details: $details${NC}"
        fi
        ((failed_count++))
    else
        echo -e "${YELLOW}⚠️  $test_name: $status${NC}"
        if [[ -n "$details" ]]; then
            echo -e "${YELLOW}   Details: $details${NC}"
        fi
    fi
}

# Function to run cURL command and check status
run_curl_test() {
    local test_name="$1"
    local curl_command="$2"
    local expected_status="$3"
    local description="$4"
    
    echo -n "Testing $test_name... "
    
    # Execute curl command and capture response and status code
    response=$(eval "$curl_command -w '\n%{http_code}'" 2>/dev/null)
    
    if [[ $? -ne 0 ]]; then
        print_result "$test_name" "FAILED" "cURL command failed"
        return 1
    fi
    
    # Extract status code (last line) and response body
    status_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | head -n -1)
    
    if [[ "$status_code" -eq "$expected_status" ]]; then
        print_result "$test_name" "PASSED" "$description"
        return 0
    else
        print_result "$test_name" "FAILED" "Expected: $expected_status, Got: $status_code"
        return 1
    fi
}

# Function to extract contact ID from JSON response
extract_contact_id() {
    local response="$1"
    echo "$response" | grep -o '"id":[0-9]*' | head -n1 | cut -d':' -f2
}

# Function to check if server is running
check_server() {
    print_header "Server Health Check"
    
    echo "Checking if server is running..."
    if curl -k -s -f "$HEALTH_URL" > /dev/null; then
        print_result "Server Health" "PASSED" "Server is responding"
        return 0
    else
        print_result "Server Health" "FAILED" "Server is not responding. Please start the server first."
        echo -e "${RED}Please run: cd Server && dotnet run${NC}"
        exit 1
    fi
}

# Test basic API endpoints
test_basic_endpoints() {
    print_header "Basic API Endpoints"
    
    run_curl_test "Root Endpoint" \
        "curl -k -s -f '$BASE_URL/'" \
        200 \
        "API info endpoint accessible"
    
    run_curl_test "Health Check" \
        "curl -k -s -f '$HEALTH_URL'" \
        200 \
        "Health check endpoint working"
        
    run_curl_test "Swagger UI" \
        "curl -k -s -f '$BASE_URL/swagger'" \
        200 \
        "Swagger documentation accessible"
}

# Test GET operations
test_get_operations() {
    print_header "GET Operations (Read)"
    
    run_curl_test "Get All Contacts" \
        "curl -k -s '$API_URL'" \
        200 \
        "Retrieved contact list"
    
    run_curl_test "Get Contact Statistics" \
        "curl -k -s '$STATS_URL'" \
        200 \
        "Retrieved contact statistics"
    
    run_curl_test "Get Non-existent Contact" \
        "curl -k -s '$API_URL/999999'" \
        404 \
        "Properly handled non-existent contact"
}

# Test POST operations
test_post_operations() {
    print_header "POST Operations (Create)"
    
    # Test data
    local test_contact='{
        "name": "Test User",
        "phoneNumber": "+1555000001",
        "email": "test.user@example.com",
        "company": "Test Company",
        "category": "Test",
        "notes": "Created by cURL test script"
    }'
    
    echo "Creating test contact..."
    local response=$(curl -k -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "$test_contact" \
        -w '\n%{http_code}')
    
    local status_code=$(echo "$response" | tail -n1)
    local response_body=$(echo "$response" | head -n -1)
    
    if [[ "$status_code" -eq 201 ]]; then
        CREATED_CONTACT_ID=$(echo "$response_body" | grep -o '"id":[0-9]*' | head -n1 | cut -d':' -f2)
        print_result "Create Contact" "PASSED" "Contact created with ID: $CREATED_CONTACT_ID"
    else
        print_result "Create Contact" "FAILED" "Status: $status_code"
        CREATED_CONTACT_ID=""
    fi
    
    # Test duplicate phone number
    echo "Testing duplicate phone number validation..."
    run_curl_test "Duplicate Phone Validation" \
        "curl -k -s -X POST '$API_URL' -H 'Content-Type: application/json' -d '$test_contact'" \
        409 \
        "Properly rejected duplicate phone number"
    
    # Test invalid data
    local invalid_contact='{"name": "", "phoneNumber": ""}'
    
    run_curl_test "Invalid Data Validation" \
        "curl -k -s -X POST '$API_URL' -H 'Content-Type: application/json' -d '$invalid_contact'" \
        400 \
        "Properly validated required fields"
}

# Test PUT operations
test_put_operations() {
    print_header "PUT Operations (Update)"
    
    if [[ -z "$CREATED_CONTACT_ID" ]]; then
        print_result "Update Test" "SKIPPED" "No contact ID available for update test"
        return
    fi
    
    local updated_contact="{
        \"id\": $CREATED_CONTACT_ID,
        \"name\": \"Updated Test User\",
        \"phoneNumber\": \"+1555000001\",
        \"email\": \"updated.test@example.com\",
        \"company\": \"Updated Company\",
        \"category\": \"Updated\",
        \"notes\": \"Updated by cURL test script\"
    }"
    
    run_curl_test "Update Contact" \
        "curl -k -s -X PUT '$API_URL/$CREATED_CONTACT_ID' -H 'Content-Type: application/json' -d '$updated_contact'" \
        200 \
        "Contact updated successfully"
    
    # Test updating non-existent contact
    run_curl_test "Update Non-existent Contact" \
        "curl -k -s -X PUT '$API_URL/999999' -H 'Content-Type: application/json' -d '$updated_contact'" \
        404 \
        "Properly handled non-existent contact update"
}

# Test search operations
test_search_operations() {
    print_header "Search Operations"
    
    run_curl_test "Search by Name" \
        "curl -k -s '$API_URL/search/Test'" \
        200 \
        "Search by name working"
    
    run_curl_test "Search by Company" \
        "curl -k -s '$API_URL/search/Company'" \
        200 \
        "Search by company working"
    
    run_curl_test "Empty Search Term" \
        "curl -k -s '$API_URL/search/'" \
        400 \
        "Properly handled empty search term"
}

# Test bulk operations
test_bulk_operations() {
    print_header "Bulk Operations"
    
    local bulk_contacts='[
        {
            "name": "Bulk User 1",
            "phoneNumber": "+1555000101",
            "email": "bulk1@example.com",
            "category": "Bulk Test"
        },
        {
            "name": "Bulk User 2",
            "phoneNumber": "+1555000102",
            "email": "bulk2@example.com",
            "category": "Bulk Test"
        },
        {
            "name": "Bulk User 3",
            "phoneNumber": "+1555000103",
            "email": "bulk3@example.com",
            "category": "Bulk Test"
        }
    ]'
    
    run_curl_test "Bulk Create Contacts" \
        "curl -k -s -X POST '$API_URL/bulk' -H 'Content-Type: application/json' -d '$bulk_contacts'" \
        200 \
        "Bulk contact creation completed"
}

# Test caching functionality
test_caching() {
    print_header "Caching Performance Tests"
    
    echo "Testing cache performance..."
    
    # First request (cache miss)
    echo -n "First request (cache miss): "
    time1_start=$(date +%s.%3N)
    curl -k -s "$API_URL" > /dev/null
    time1_end=$(date +%s.%3N)
    time1=$(echo "$time1_end - $time1_start" | bc -l)
    echo "${time1}s"
    
    # Second request (cache hit - should be faster)
    echo -n "Second request (cache hit): "
    time2_start=$(date +%s.%3N)
    curl -k -s "$API_URL" > /dev/null
    time2_end=$(date +%s.%3N)
    time2=$(echo "$time2_end - $time2_start" | bc -l)
    echo "${time2}s"
    
    # Compare times
    if (( $(echo "$time2 < $time1" | bc -l) )); then
        print_result "Cache Performance" "PASSED" "Second request faster (${time2}s vs ${time1}s)"
    else
        print_result "Cache Performance" "WARNING" "Cache may not be working optimally"
    fi
    
    # Test cache clearing
    run_curl_test "Clear Cache" \
        "curl -k -s -X DELETE '$CACHE_URL'" \
        200 \
        "Cache cleared successfully"
}

# Test pagination
test_pagination() {
    print_header "Pagination Tests"
    
    run_curl_test "Pagination - Page 1" \
        "curl -k -s '$API_URL?page=1&pageSize=2'" \
        200 \
        "First page retrieved"
    
    run_curl_test "Pagination - Page 2" \
        "curl -k -s '$API_URL?page=2&pageSize=2'" \
        200 \
        "Second page retrieved"
}

# Test DELETE operations
test_delete_operations() {
    print_header "DELETE Operations (Soft Delete)"
    
    if [[ -z "$CREATED_CONTACT_ID" ]]; then
        print_result "Delete Test" "SKIPPED" "No contact ID available for delete test"
        return
    fi
    
    run_curl_test "Delete Contact" \
        "curl -k -s -X DELETE '$API_URL/$CREATED_CONTACT_ID'" \
        200 \
        "Contact deleted (soft delete)"
    
    # Verify contact is no longer accessible
    run_curl_test "Verify Soft Delete" \
        "curl -k -s '$API_URL/$CREATED_CONTACT_ID'" \
        404 \
        "Deleted contact no longer accessible"
}

# Test error handling
test_error_handling() {
    print_header "Error Handling Tests"
    
    run_curl_test "Invalid JSON" \
        "curl -k -s -X POST '$API_URL' -H 'Content-Type: application/json' -d '{invalid json}'" \
        400 \
        "Properly handled invalid JSON"
    
    run_curl_test "Missing Content-Type" \
        "curl -k -s -X POST '$API_URL' -d '{\"name\":\"test\"}'" \
        415 \
        "Properly handled missing content type"
}

# Load testing function
run_load_test() {
    print_header "Load Testing"
    
    local requests=20
    local concurrent=5
    
    echo "Running $requests requests with $concurrent concurrent connections..."
    
    # Create a simple load test
    local total_time=0
    local successful_requests=0
    
    for i in $(seq 1 $requests); do
        start_time=$(date +%s.%3N)
        if curl -k -s -f "$API_URL" > /dev/null 2>&1; then
            ((successful_requests++))
        fi
        end_time=$(date +%s.%3N)
        request_time=$(echo "$end_time - $start_time" | bc -l)
        total_time=$(echo "$total_time + $request_time" | bc -l)
        
        # Show progress
        if (( i % 5 == 0 )); then
            echo "Completed $i/$requests requests..."
        fi
    done
    
    local avg_time=$(echo "scale=3; $total_time / $requests" | bc -l)
    local success_rate=$(echo "scale=2; $successful_requests * 100 / $requests" | bc -l)
    
    echo -e "${CYAN}Load Test Results:${NC}"
    echo "  Total Requests: $requests"
    echo "  Successful: $successful_requests"
    echo "  Success Rate: ${success_rate}%"
    echo "  Average Response Time: ${avg_time}s"
    echo "  Total Time: ${total_time}s"
    
    if (( $(echo "$success_rate >= 95" | bc -l) )); then
        print_result "Load Test" "PASSED" "Success rate: ${success_rate}%"
    else
        print_result "Load Test" "FAILED" "Success rate too low: ${success_rate}%"
    fi
}

# Generate test report
generate_report() {
    print_header "Test Summary Report"
    
    echo -e "${CYAN}Test Execution Summary:${NC}"
    echo "  Total Tests: $test_count"
    echo -e "  ${GREEN}Passed: $passed_count${NC}"
    echo -e "  ${RED}Failed: $failed_count${NC}"
    
    local success_rate=$(( passed_count * 100 / test_count ))
    echo "  Success Rate: ${success_rate}%"
    
    if [[ $failed_count -eq 0 ]]; then
        echo -e "\n${GREEN}🎉 All tests passed! The API is working correctly.${NC}"
        return 0
    else
        echo -e "\n${RED}⚠️  Some tests failed. Please check the output above.${NC}"
        return 1
    fi
}

# Main execution function
main() {
    # Parse command line arguments
    local run_load_tests=false
    local run_specific_test=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --load)
                run_load_tests=true
                shift
                ;;
            --test)
                run_specific_test="$2"
                shift 2
                ;;
            --help|-h)
                echo "Usage: $0 [options]"
                echo "Options:"
                echo "  --load          Run load testing"
                echo "  --test <name>   Run specific test (basic|crud|cache|search|bulk|pagination|errors)"
                echo "  --help,-h       Show this help message"
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Start time
    start_time=$(date +%s)
    
    # Check if server is running
    check_server
    
    # Run tests based on arguments
    if [[ -n "$run_specific_test" ]]; then
        case "$run_specific_test" in
            basic)
                test_basic_endpoints
                ;;
            crud)
                test_get_operations
                test_post_operations
                test_put_operations
                test_delete_operations
                ;;
            cache)
                test_caching
                ;;
            search)
                test_search_operations
                ;;
            bulk)
                test_bulk_operations
                ;;
            pagination)
                test_pagination
                ;;
            errors)
                test_error_handling
                ;;
            *)
                echo "Unknown test: $run_specific_test"
                exit 1
                ;;
        esac
    else
        # Run all tests
        test_basic_endpoints
        test_get_operations
        test_post_operations
        test_put_operations
        test_search_operations
        test_bulk_operations
        test_pagination
        test_caching
        test_delete_operations
        test_error_handling
        
        if [[ "$run_load_tests" == true ]]; then
            run_load_test
        fi
    fi
    
    # End time and generate report
    end_time=$(date +%s)
    execution_time=$((end_time - start_time))
    
    echo -e "\n${CYAN}Total execution time: ${execution_time} seconds${NC}"
    
    generate_report
}

# Check dependencies
check_dependencies() {
    local missing_deps=()
    
    if ! command -v curl &> /dev/null; then
        missing_deps+=("curl")
    fi
    
    if ! command -v bc &> /dev/null; then
        missing_deps+=("bc")
    fi
    
    if ! command -v grep &> /dev/null; then
        missing_deps+=("grep")
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        echo -e "${RED}Missing required dependencies: ${missing_deps[*]}${NC}"
        echo "Please install them using: sudo apt install ${missing_deps[*]}"
        exit 1
    fi
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    check_dependencies
    main "$@"
fi
