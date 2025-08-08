#!/bin/bash

# Initialize Qdrant Collections
# Usage: ./scripts/init_collections.sh

set -e

QDRANT_URL="http://localhost:6333"
COLLECTION_NAME="documents"
VECTOR_SIZE=384  # Size for sentence-transformers/all-MiniLM-L6-v2

echo "🏗️  Initializing Qdrant Collections..."

# Wait for Qdrant to be available
echo "⏳ Waiting for Qdrant..."
for i in {1..30}; do
    if curl -s "$QDRANT_URL/health" >/dev/null 2>&1; then
        echo "✅ Qdrant is available"
        break
    fi
    echo -n "."
    sleep 2
    if [ $i -eq 30 ]; then
        echo ""
        echo "❌ Qdrant is not available. Please start it first:"
        echo "   ./scripts/start_qdrant.sh"
        exit 1
    fi
done

# Check if collection already exists
if curl -s "$QDRANT_URL/collections/$COLLECTION_NAME" | grep -q "\"result\""; then
    echo "📚 Collection '$COLLECTION_NAME' already exists"
    collection_info=$(curl -s "$QDRANT_URL/collections/$COLLECTION_NAME")
    echo "   Current status: $(echo "$collection_info" | jq -r '.result.status')"
    echo "   Vector count: $(echo "$collection_info" | jq -r '.result.vectors_count // 0')"
    exit 0
fi

# Create documents collection
echo "📚 Creating '$COLLECTION_NAME' collection..."
create_response=$(curl -s -X PUT "$QDRANT_URL/collections/$COLLECTION_NAME" \
    -H "Content-Type: application/json" \
    -d '{
        "vectors": {
            "size": '$VECTOR_SIZE',
            "distance": "Cosine"
        },
        "optimizers_config": {
            "default_segment_number": 2
        },
        "replication_factor": 1
    }')

if echo "$create_response" | jq -e '.result' >/dev/null 2>&1; then
    echo "✅ Collection created successfully"
else
    echo "❌ Failed to create collection:"
    echo "$create_response" | jq '.' 2>/dev/null || echo "$create_response"
    exit 1
fi

# Create payload indexes for better performance
echo "🔍 Creating payload indexes..."

# Index for document type
curl -s -X PUT "$QDRANT_URL/collections/$COLLECTION_NAME/index" \
    -H "Content-Type: application/json" \
    -d '{
        "field_name": "document_type",
        "field_schema": "keyword"
    }' >/dev/null

# Index for document ID
curl -s -X PUT "$QDRANT_URL/collections/$COLLECTION_NAME/index" \
    -H "Content-Type: application/json" \
    -d '{
        "field_name": "document_id",
        "field_schema": "keyword"
    }' >/dev/null

# Index for timestamp
curl -s -X PUT "$QDRANT_URL/collections/$COLLECTION_NAME/index" \
    -H "Content-Type: application/json" \
    -d '{
        "field_name": "timestamp",
        "field_schema": "datetime"
    }' >/dev/null

echo "✅ Payload indexes created"

# Verify collection
collection_info=$(curl -s "$QDRANT_URL/collections/$COLLECTION_NAME")
echo ""
echo "📊 Collection Summary:"
echo "   Name: $COLLECTION_NAME"
echo "   Vector Size: $VECTOR_SIZE"
echo "   Distance Metric: Cosine"
echo "   Status: $(echo "$collection_info" | jq -r '.result.status')"
echo "   Indexed Fields: document_type, document_id, timestamp"
echo ""
echo "🎉 Collection initialization complete!"
echo "   Dashboard: $QDRANT_URL/dashboard"
echo "   Collection URL: $QDRANT_URL/collections/$COLLECTION_NAME"
