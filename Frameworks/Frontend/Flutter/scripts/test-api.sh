#!/bin/bash

# Flutter SPA API Test Script
# This script contains CURL test cases for the REST API

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BASE_URL=${API_BASE_URL:-"http://localhost:3000"}
API_URL="${BASE_URL}/api"
AUTH_URL="${API_URL}/auth"
USERS_URL="${API_URL}/users"

# Test credentials
TEST_USER_EMAIL="test@example.com"
TEST_USER_PHONE="+1234567890"
TEST_USER_PASSWORD="TestPassword123!"
TEST_USER_NAME="Test User"

# Global variables for storing tokens
ACCESS_TOKEN=""
REFRESH_TOKEN=""
USER_ID=""

# Print functions
print_test() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Helper function to make HTTP requests
make_request() {
    local method=$1
    local url=$2
    local data=$3
    local headers=$4
    local expected_status=$5

    print_info "Making $method request to: $url"
    
    local curl_cmd="curl -s -w '\nHTTP_STATUS:%{http_code}\nTIME_TOTAL:%{time_total}' -X $method"
    
    if [ ! -z "$headers" ]; then
        curl_cmd="$curl_cmd $headers"
    fi
    
    if [ ! -z "$data" ]; then
        curl_cmd="$curl_cmd -d '$data'"
    fi
    
    curl_cmd="$curl_cmd '$url'"
    
    local response=$(eval $curl_cmd)
    local http_status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)
    local time_total=$(echo "$response" | grep "TIME_TOTAL:" | cut -d: -f2)
    local body=$(echo "$response" | sed '/^HTTP_STATUS:/d' | sed '/^TIME_TOTAL:/d')
    
    echo "Response Status: $http_status"
    echo "Response Time: ${time_total}s"
    echo "Response Body: $body"
    
    if [ "$http_status" = "$expected_status" ]; then
        print_success "Test passed (Expected: $expected_status, Got: $http_status)"
        echo "$body"
    else
        print_error "Test failed (Expected: $expected_status, Got: $http_status)"
        return 1
    fi
}

# Test health check endpoint
test_health_check() {
    print_test "Health Check"
    make_request "GET" "${BASE_URL}/health" "" "" "200"
}

# Test user registration
test_user_registration() {
    print_test "User Registration"
    
    local data="{
        \"name\": \"$TEST_USER_NAME\",
        \"email\": \"$TEST_USER_EMAIL\",
        \"phone\": \"$TEST_USER_PHONE\",
        \"password\": \"$TEST_USER_PASSWORD\"
    }"
    
    local response=$(make_request "POST" "${AUTH_URL}/register" "$data" "-H 'Content-Type: application/json'" "201")
    
    if [ $? -eq 0 ]; then
        # Extract tokens from response
        ACCESS_TOKEN=$(echo "$response" | jq -r '.data.accessToken' 2>/dev/null)
        REFRESH_TOKEN=$(echo "$response" | jq -r '.data.refreshToken' 2>/dev/null)
        USER_ID=$(echo "$response" | jq -r '.data.user.id' 2>/dev/null)
        
        print_success "Registration successful. Tokens extracted."
    fi
}

# Test user login
test_user_login() {
    print_test "User Login"
    
    local data="{
        \"username\": \"$TEST_USER_EMAIL\",
        \"password\": \"$TEST_USER_PASSWORD\"
    }"
    
    local response=$(make_request "POST" "${AUTH_URL}/login" "$data" "-H 'Content-Type: application/json'" "200")
    
    if [ $? -eq 0 ]; then
        # Extract tokens from response
        ACCESS_TOKEN=$(echo "$response" | jq -r '.data.accessToken' 2>/dev/null)
        REFRESH_TOKEN=$(echo "$response" | jq -r '.data.refreshToken' 2>/dev/null)
        USER_ID=$(echo "$response" | jq -r '.data.user.id' 2>/dev/null)
        
        print_success "Login successful. Tokens extracted."
    fi
}

# Test login with phone number
test_phone_login() {
    print_test "Login with Phone Number"
    
    local data="{
        \"username\": \"$TEST_USER_PHONE\",
        \"password\": \"$TEST_USER_PASSWORD\"
    }"
    
    make_request "POST" "${AUTH_URL}/login" "$data" "-H 'Content-Type: application/json'" "200"
}

# Test invalid login
test_invalid_login() {
    print_test "Invalid Login"
    
    local data="{
        \"username\": \"invalid@example.com\",
        \"password\": \"wrongpassword\"
    }"
    
    make_request "POST" "${AUTH_URL}/login" "$data" "-H 'Content-Type: application/json'" "401"
}

# Test token refresh
test_token_refresh() {
    print_test "Token Refresh"
    
    if [ -z "$REFRESH_TOKEN" ]; then
        print_error "No refresh token available. Run login test first."
        return 1
    fi
    
    local data="{
        \"refreshToken\": \"$REFRESH_TOKEN\"
    }"
    
    local response=$(make_request "POST" "${AUTH_URL}/refresh" "$data" "-H 'Content-Type: application/json'" "200")
    
    if [ $? -eq 0 ]; then
        # Update access token
        ACCESS_TOKEN=$(echo "$response" | jq -r '.data.accessToken' 2>/dev/null)
        print_success "Token refresh successful. New access token extracted."
    fi
}

# Test get user profile
test_get_profile() {
    print_test "Get User Profile"
    
    if [ -z "$ACCESS_TOKEN" ]; then
        print_error "No access token available. Run login test first."
        return 1
    fi
    
    make_request "GET" "${USERS_URL}/profile" "" "-H 'Authorization: Bearer $ACCESS_TOKEN'" "200"
}

# Test update user profile
test_update_profile() {
    print_test "Update User Profile"
    
    if [ -z "$ACCESS_TOKEN" ]; then
        print_error "No access token available. Run login test first."
        return 1
    fi
    
    local data="{
        \"name\": \"Updated Test User\",
        \"preferences\": {
            \"notifications\": {
                \"email\": true,
                \"sms\": false,
                \"push\": true
            },
            \"language\": \"en\"
        }
    }"
    
    make_request "PUT" "${USERS_URL}/profile" "$data" "-H 'Authorization: Bearer $ACCESS_TOKEN' -H 'Content-Type: application/json'" "200"
}

# Test get all users (requires admin or returns paginated results)
test_get_all_users() {
    print_test "Get All Users"
    
    if [ -z "$ACCESS_TOKEN" ]; then
        print_error "No access token available. Run login test first."
        return 1
    fi
    
    make_request "GET" "${USERS_URL}" "" "-H 'Authorization: Bearer $ACCESS_TOKEN'" "200"
}

# Test get users with pagination and search
test_get_users_paginated() {
    print_test "Get Users with Pagination"
    
    if [ -z "$ACCESS_TOKEN" ]; then
        print_error "No access token available. Run login test first."
        return 1
    fi
    
    make_request "GET" "${USERS_URL}?page=1&limit=5&search=test" "" "-H 'Authorization: Bearer $ACCESS_TOKEN'" "200"
}

# Test create user (admin only)
test_create_user() {
    print_test "Create User (Admin Only)"
    
    if [ -z "$ACCESS_TOKEN" ]; then
        print_error "No access token available. Run login test first."
        return 1
    fi
    
    local data="{
        \"name\": \"Admin Created User\",
        \"email\": \"admin.created@example.com\",
        \"phone\": \"+1987654321\",
        \"role\": \"user\"
    }"
    
    # This will likely return 403 unless the test user is an admin
    make_request "POST" "${USERS_URL}" "$data" "-H 'Authorization: Bearer $ACCESS_TOKEN' -H 'Content-Type: application/json'" "403"
}

# Test unauthorized access
test_unauthorized_access() {
    print_test "Unauthorized Access"
    
    make_request "GET" "${USERS_URL}/profile" "" "" "401"
}

# Test invalid token
test_invalid_token() {
    print_test "Invalid Token"
    
    make_request "GET" "${USERS_URL}/profile" "" "-H 'Authorization: Bearer invalid_token'" "401"
}

# Test logout
test_logout() {
    print_test "User Logout"
    
    make_request "POST" "${AUTH_URL}/logout" "" "-H 'Content-Type: application/json'" "200"
}

# Test forgot password
test_forgot_password() {
    print_test "Forgot Password"
    
    local data="{
        \"email\": \"$TEST_USER_EMAIL\"
    }"
    
    make_request "POST" "${AUTH_URL}/forgot-password" "$data" "-H 'Content-Type: application/json'" "200"
}

# Test password reset (with mock token)
test_password_reset() {
    print_test "Password Reset"
    
    local data="{
        \"token\": \"mock_reset_token\",
        \"password\": \"NewPassword123!\"
    }"
    
    make_request "POST" "${AUTH_URL}/reset-password" "$data" "-H 'Content-Type: application/json'" "200"
}

# Test email verification (with mock token)
test_email_verification() {
    print_test "Email Verification"
    
    make_request "GET" "${AUTH_URL}/verify-email/mock_verification_token" "" "" "200"
}

# Test validation errors
test_validation_errors() {
    print_test "Validation Errors"
    
    # Test registration with invalid data
    local data="{
        \"name\": \"\",
        \"email\": \"invalid-email\",
        \"phone\": \"invalid-phone\",
        \"password\": \"123\"
    }"
    
    make_request "POST" "${AUTH_URL}/register" "$data" "-H 'Content-Type: application/json'" "400"
}

# Test rate limiting (requires multiple requests)
test_rate_limiting() {
    print_test "Rate Limiting"
    
    print_info "Making multiple rapid requests to test rate limiting..."
    
    local data="{
        \"username\": \"test@example.com\",
        \"password\": \"wrongpassword\"
    }"
    
    for i in {1..6}; do
        print_info "Request $i/6"
        curl -s -X POST "${AUTH_URL}/login" \
            -H 'Content-Type: application/json' \
            -d "$data" > /dev/null
        
        if [ $i -eq 6 ]; then
            # The 6th request should be rate limited (depending on configuration)
            make_request "POST" "${AUTH_URL}/login" "$data" "-H 'Content-Type: application/json'" "429"
        fi
    done
}

# Performance test
test_performance() {
    print_test "Performance Test"
    
    if [ -z "$ACCESS_TOKEN" ]; then
        print_error "No access token available. Run login test first."
        return 1
    fi
    
    print_info "Running performance test with 10 concurrent requests..."
    
    # Create multiple background requests
    for i in {1..10}; do
        {
            start_time=$(date +%s%N)
            curl -s -X GET "${USERS_URL}/profile" \
                -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null
            end_time=$(date +%s%N)
            duration=$(( (end_time - start_time) / 1000000 ))
            echo "Request $i: ${duration}ms"
        } &
    done
    
    # Wait for all background requests to complete
    wait
    print_success "Performance test completed"
}

# Cleanup function
cleanup_test_data() {
    print_test "Cleanup Test Data"
    print_info "In a real implementation, you would clean up test users and data here."
    print_success "Cleanup completed"
}

# Main test runner
run_tests() {
    print_test "Starting Flutter SPA API Tests"
    print_info "Base URL: $BASE_URL"
    
    # Check if jq is available for JSON parsing
    if ! command -v jq &> /dev/null; then
        print_error "jq is not installed. Some token extraction features will not work."
        print_info "Install jq with: sudo apt-get install jq (Ubuntu/Debian) or brew install jq (macOS)"
    fi
    
    # Run tests
    test_health_check
    test_user_registration
    test_user_login
    test_phone_login
    test_invalid_login
    test_token_refresh
    test_get_profile
    test_update_profile
    test_get_all_users
    test_get_users_paginated
    test_create_user
    test_unauthorized_access
    test_invalid_token
    test_forgot_password
    test_password_reset
    test_email_verification
    test_validation_errors
    test_logout
    
    # Stress tests (optional)
    if [ "$1" = "full" ] || [ "$1" = "performance" ]; then
        test_rate_limiting
        test_performance
    fi
    
    # Cleanup
    cleanup_test_data
    
    print_test "API Tests Completed"
    print_success "All tests have been executed. Check the output above for results."
}

# Handle command line arguments
case ${1:-basic} in
    "basic")
        run_tests
        ;;
    "full")
        run_tests full
        ;;
    "performance")
        test_performance
        ;;
    "health")
        test_health_check
        ;;
    "auth")
        test_user_registration
        test_user_login
        test_token_refresh
        test_logout
        ;;
    "users")
        # Need to login first for user tests
        test_user_login
        test_get_profile
        test_update_profile
        test_get_all_users
        ;;
    *)
        echo "Usage: $0 {basic|full|performance|health|auth|users}"
        echo "  basic       - Run basic API tests (default)"
        echo "  full        - Run all tests including performance tests"
        echo "  performance - Run only performance tests"
        echo "  health      - Run only health check"
        echo "  auth        - Run only authentication tests"
        echo "  users       - Run only user management tests"
        exit 1
        ;;
esac
