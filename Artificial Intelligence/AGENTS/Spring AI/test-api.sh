#!/bin/bash

# Example API calls for Spring AI RAG Demo
# Make sure the application is running on http://localhost:8080

BASE_URL="http://localhost:8080/api/chat"

echo "========================================"
echo "Spring AI RAG Demo - API Examples"
echo "========================================"
echo ""

# Health check
echo "1. Health Check"
echo "Command: curl $BASE_URL/health"
curl -s "$BASE_URL/health"
echo ""
echo ""

# Simple question
echo "2. Simple Question (GET)"
echo "Command: curl -X POST \"$BASE_URL/ask?question=What%20is%20Spring%20AI?\""
curl -s -X POST "$BASE_URL/ask?question=What%20is%20Spring%20AI?" | jq '.'
echo ""
echo ""

# Advanced query with JSON
echo "3. Advanced Query (POST with JSON)"
echo "Command: curl -X POST $BASE_URL -H 'Content-Type: application/json' -d '{...}'"
curl -s -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How does Retrieval Augmented Generation work?",
    "includeContext": true,
    "similarityThreshold": 0.7,
    "topK": 5
  }' | jq '.'
echo ""
echo ""

# Query with high similarity threshold
echo "4. High Precision Query"
echo "Command: curl -X POST $BASE_URL -H 'Content-Type: application/json' -d '{...}'"
curl -s -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the ChatClient API?",
    "similarityThreshold": 0.85,
    "topK": 3
  }' | jq '.'
echo ""
echo ""

# Query without context (direct LLM)
echo "5. Direct Query Without RAG"
echo "Command: curl -X POST $BASE_URL -H 'Content-Type: application/json' -d '{...}'"
curl -s -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is 2 + 2?",
    "includeContext": false
  }' | jq '.'
echo ""
echo ""

echo "========================================"
echo "Examples Complete"
echo "========================================"
echo ""
echo "Note: Install 'jq' for pretty JSON output: sudo apt install jq"
echo ""
