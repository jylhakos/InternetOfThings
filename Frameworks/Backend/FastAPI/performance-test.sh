#!/bin/bash
# performance-test.sh - FastAPI Performance Testing Script

echo "Starting FastAPI Performance Tests"

# Check if FastAPI server is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "Error: FastAPI server is not running on http://localhost:8000"
    echo "Please start the server with: uvicorn main:app --reload"
    exit 1
fi

ENDPOINTS=(
    "http://localhost:8000/health"
    "http://localhost:8000/metrics"
)

for endpoint in "${ENDPOINTS[@]}"; do
    echo "Testing: $endpoint"
    
    # Single request timing
    echo "Single request test:"
    curl -w "Total: %{time_total}s, TTFB: %{time_starttransfer}s, Status: %{http_code}\n" \
         -o /dev/null -s "$endpoint"
    
    # Concurrent requests
    echo "Running 50 concurrent requests..."
    temp_file=$(mktemp)
    seq 1 50 | xargs -n1 -P10 -I{} curl -s -o /dev/null \
        -w "%{time_total}\n" "$endpoint" > "$temp_file"
    
    if [ -s "$temp_file" ]; then
        avg_time=$(awk '{sum+=$1; count++} END {print sum/count}' "$temp_file")
        min_time=$(sort -n "$temp_file" | head -n1)
        max_time=$(sort -n "$temp_file" | tail -n1)
        
        echo "Average response time: ${avg_time}s"
        echo "Min response time: ${min_time}s"
        echo "Max response time: ${max_time}s"
    fi
    
    rm -f "$temp_file"
    echo "---"
done

echo "Performance testing complete!"
