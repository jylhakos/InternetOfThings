#!/bin/bash

# Start Qdrant Vector Database
# Usage: ./scripts/start_qdrant.sh

set -e

QDRANT_CONTAINER="qdrant_vectordb"
QDRANT_IMAGE="qdrant/qdrant:latest"
QDRANT_DATA_DIR="./data/qdrant_storage"

echo "🚀 Starting Qdrant Vector Database..."

# Create data directory if it doesn't exist
mkdir -p "$QDRANT_DATA_DIR"

# Check if container already exists
if docker ps -a --format 'table {{.Names}}' | grep -q "^${QDRANT_CONTAINER}$"; then
    echo "📦 Container $QDRANT_CONTAINER already exists"
    
    if docker ps --format 'table {{.Names}}' | grep -q "^${QDRANT_CONTAINER}$"; then
        echo "✅ Qdrant is already running"
        docker ps --filter "name=$QDRANT_CONTAINER" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    else
        echo "🔄 Starting existing container..."
        docker start "$QDRANT_CONTAINER"
    fi
else
    echo "🆕 Creating new Qdrant container..."
    docker run -d \
        --name "$QDRANT_CONTAINER" \
        -p 6333:6333 \
        -p 6334:6334 \
        -v "$(pwd)/${QDRANT_DATA_DIR}:/qdrant/storage:z" \
        -e QDRANT__SERVICE__HTTP_PORT=6333 \
        -e QDRANT__SERVICE__GRPC_PORT=6334 \
        "$QDRANT_IMAGE"
fi

# Wait for Qdrant to be ready
echo "⏳ Waiting for Qdrant to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:6333/health >/dev/null 2>&1; then
        echo "✅ Qdrant is ready!"
        break
    fi
    echo -n "."
    sleep 2
done

# Display status
echo ""
echo "📊 Qdrant Status:"
echo "   🌐 Web UI: http://localhost:6333/dashboard"
echo "   🔗 API Endpoint: http://localhost:6333"
echo "   📁 Data Directory: $QDRANT_DATA_DIR"
echo ""

# Show collections
if curl -s http://localhost:6333/collections >/dev/null 2>&1; then
    echo "📚 Collections:"
    curl -s http://localhost:6333/collections | jq -r '.result.collections[]? | "   - \(.name) (vectors: \(.vectors_count // 0))"' 2>/dev/null || echo "   No collections found"
else
    echo "⚠️  Unable to connect to Qdrant API"
fi
