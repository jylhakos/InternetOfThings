#!/bin/bash

# Stop Qdrant Vector Database
# Usage: ./scripts/stop_qdrant.sh [--remove]

set -e

QDRANT_CONTAINER="qdrant_vectordb"
REMOVE_CONTAINER=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --remove)
            REMOVE_CONTAINER=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--remove]"
            echo "  --remove: Remove container and data (destructive)"
            exit 0
            ;;
        *)
            echo "Usage: $0 [--remove]"
            echo "  --remove: Remove container and data (destructive)"
            exit 1
            ;;
    esac
done

echo "🛑 Stopping Qdrant Vector Database..."

# Check if container exists
if ! docker ps -a --format 'table {{.Names}}' | grep -q "^${QDRANT_CONTAINER}$"; then
    echo "⚠️  Container $QDRANT_CONTAINER does not exist"
    exit 0
fi

# Stop container
if docker ps --format 'table {{.Names}}' | grep -q "^${QDRANT_CONTAINER}$"; then
    echo "⏹️  Stopping container..."
    docker stop "$QDRANT_CONTAINER"
    echo "✅ Container stopped"
else
    echo "ℹ️  Container is already stopped"
fi

# Remove container if requested
if [ "$REMOVE_CONTAINER" = true ]; then
    echo "🗑️  Removing container and data..."
    docker rm "$QDRANT_CONTAINER"
    echo "⚠️  Warning: All vector data has been removed"
    echo "✅ Container removed"
else
    echo "ℹ️  Container stopped but preserved (use --remove to delete)"
    echo "   Restart with: docker start $QDRANT_CONTAINER"
    echo "   Or use: ./scripts/start_qdrant.sh"
fi
