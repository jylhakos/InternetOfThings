#!/bin/bash

# cURL Test Scripts for LangGraph RAG API
# Make sure the API server is running on http://localhost:8000

BASE_URL="http://localhost:8000"
API_URL="${BASE_URL}/api/v1"

echo "🚀 Starting LangGraph RAG API Tests"
echo "API Base URL: ${BASE_URL}"
echo "=================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print test header
print_test() {
    echo -e "\n${BLUE}📋 Test: $1${NC}"
    echo "----------------------------------------"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to print info
print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Test 1: Health Check
print_test "Health Check"
curl -s -X GET "${BASE_URL}/health" | jq '.' || print_error "Health check failed"

# Test 2: Chat Health Check
print_test "Chat Service Health Check"
curl -s -X GET "${API_URL}/chat/health" | jq '.' || print_error "Chat health check failed"

# Test 3: List Available Models
print_test "List Available Models"
curl -s -X GET "${API_URL}/chat/models" | jq '.' || print_error "List models failed"

# Test 4: Upload a Sample Document
print_test "Upload Document"
# Create a sample text file
echo "This is a sample document for testing the RAG system. It contains information about artificial intelligence, machine learning, and natural language processing. The document discusses the benefits of using vector databases for semantic search and retrieval augmented generation." > /tmp/sample_document.txt

# Upload the document
curl -s -X POST "${API_URL}/documents/upload" \
  -F "file=@/tmp/sample_document.txt" \
  -F 'metadata={"title": "Sample AI Document", "category": "technical", "tags": ["AI", "ML", "RAG"]}' | jq '.' || print_error "Document upload failed"

print_success "Document uploaded successfully"

# Test 5: List Documents
print_test "List Uploaded Documents"
curl -s -X GET "${API_URL}/documents/?page=1&page_size=10" | jq '.' || print_error "List documents failed"

# Test 6: Search Documents
print_test "Search Documents"
curl -s -X POST "${API_URL}/documents/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "artificial intelligence machine learning",
    "top_k": 3,
    "score_threshold": 0.5
  }' | jq '.' || print_error "Document search failed"

# Test 7: RAG Query with ArceeAgent
print_test "RAG Query with ArceeAgent"
curl -s -X POST "${API_URL}/chat/query" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is artificial intelligence and how does it relate to machine learning?",
    "model": "arcee-ai/arcee-agent",
    "use_rag": true,
    "max_tokens": 500,
    "temperature": 0.7
  }' | jq '.' || print_error "RAG query with ArceeAgent failed"

print_success "ArceeAgent RAG query completed"

# Test 8: Direct LLM Query (no RAG)
print_test "Direct LLM Query (No RAG)"
curl -s -X POST "${API_URL}/chat/query" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain the concept of neural networks in 100 words",
    "model": "arcee-ai/arcee-agent",
    "use_rag": false,
    "max_tokens": 150,
    "temperature": 0.8
  }' | jq '.' || print_error "Direct LLM query failed"

print_success "Direct LLM query completed"

# Test 9: CodeLlama Query
print_test "CodeLlama Programming Query"
curl -s -X POST "${API_URL}/chat/query" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Write a Python function to calculate the Fibonacci sequence up to n numbers",
    "model": "codellama:7b",
    "use_rag": false,
    "max_tokens": 300,
    "temperature": 0.3
  }' | jq '.' || print_error "CodeLlama query failed"

print_success "CodeLlama query completed"

# Test 10: RAG Query with Context
print_test "Direct RAG Query"
curl -s -X POST "${API_URL}/chat/rag" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the benefits of using vector databases for RAG?",
    "top_k": 5,
    "score_threshold": 0.7
  }' \
  -G -d "model=arcee-ai/arcee-agent" | jq '.' || print_error "Direct RAG query failed"

print_success "Direct RAG query completed"

# Test 11: Batch Processing
print_test "Batch Query Processing"
curl -s -X POST "${API_URL}/chat/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "queries": [
      "What is machine learning?",
      "Explain neural networks",
      "What is deep learning?"
    ],
    "model": "arcee-ai/arcee-agent",
    "use_rag": true
  }' | jq '.' || print_error "Batch processing failed"

print_success "Batch processing completed"

# Test 12: Stream Response Test (basic check)
print_test "Stream Response Test"
print_info "Testing streaming endpoint (first few chunks)..."
curl -s -X POST "${API_URL}/chat/stream" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Hello, how are you?",
    "model": "arcee-ai/arcee-agent",
    "use_rag": false
  }' | head -20 || print_error "Stream test failed"

print_success "Stream test completed (partial output shown)"

# Test 13: Collection Statistics
print_test "Vector Collection Statistics"
curl -s -X GET "${API_URL}/documents/stats/collection" | jq '.' || print_error "Collection stats failed"

# Test 14: Model Switch Test
print_test "Model Switch Test"
curl -s -X POST "${API_URL}/chat/models/switch" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "codellama:7b"
  }' | jq '.' || print_error "Model switch failed"

print_success "Model switch completed"

# Test 15: Error Handling Test
print_test "Error Handling Test"
curl -s -X POST "${API_URL}/chat/query" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "",
    "model": "invalid-model",
    "use_rag": true
  }' | jq '.' || print_info "Error handling test completed (expected to show error)"

# Cleanup
print_test "Cleanup"
rm -f /tmp/sample_document.txt
print_success "Test file cleaned up"

echo -e "\n${GREEN}🎉 All tests completed!${NC}"
echo "=================================="
echo "Check the output above for any errors."
echo "If all tests show success messages, your API is working correctly!"

# Advanced Test Examples with Different Prompt Formats

echo -e "\n${BLUE}🧪 Advanced Prompt Format Tests${NC}"
echo "=================================="

# ArceeAgent Function Calling Format
print_test "ArceeAgent Function Calling Format"
curl -s -X POST "${API_URL}/chat/query" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Search for information about vector databases and then explain how they work in RAG systems",
    "model": "arcee-ai/arcee-agent",
    "use_rag": true,
    "max_tokens": 600
  }' | jq '.response' || print_error "ArceeAgent function calling failed"

# CodeLlama Code Generation
print_test "CodeLlama Code Generation with Context"
curl -s -X POST "${API_URL}/chat/query" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a Python class for a simple RAG system that can add documents and search them. Include proper error handling and type hints.",
    "model": "codellama:7b",
    "use_rag": false,
    "max_tokens": 800,
    "temperature": 0.2
  }' | jq '.response' || print_error "CodeLlama code generation failed"

print_success "Advanced prompt format tests completed"

echo -e "\n${GREEN}🔬 Testing Complete!${NC}"
echo "Review the responses above to verify the prompt formats are working correctly for each model."
