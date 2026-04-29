#!/bin/bash
# Setup script for vector databases

echo "Vector Database Setup"
echo "====================="
echo ""
echo "Select a vector database to setup:"
echo "1) ChromaDB (Embedded - No setup required)"
echo "2) Qdrant (Docker)"
echo "3) Weaviate (Docker)"
echo "4) Milvus (Docker)"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo "ChromaDB selected - No additional setup required!"
        echo "Data will be stored in ./chroma_data/"
        mkdir -p chroma_data
        ;;
    2)
        echo "Setting up Qdrant with Docker..."
        docker pull qdrant/qdrant
        mkdir -p qdrant_data
        docker run -d -p 6333:6333 -p 6334:6334 \
            -v "$(pwd)/qdrant_data:/qdrant/storage" \
            --name qdrant \
            qdrant/qdrant
        echo "Qdrant started on http://localhost:6333"
        echo "Update .env file: VECTOR_DB_TYPE=qdrant"
        ;;
    3)
        echo "Setting up Weaviate with Docker..."
        mkdir -p weaviate_data
        docker run -d -p 8080:8080 \
            -v "$(pwd)/weaviate_data:/var/lib/weaviate" \
            -e QUERY_DEFAULTS_LIMIT=25 \
            -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED='true' \
            -e PERSISTENCE_DATA_PATH='/var/lib/weaviate' \
            --name weaviate \
            semitechnologies/weaviate:latest
        echo "Weaviate started on http://localhost:8080"
        echo "Update .env file: VECTOR_DB_TYPE=weaviate"
        ;;
    4)
        echo "Setting up Milvus with Docker..."
        if [ ! -f "docker-compose-milvus.yml" ]; then
            echo "Downloading Milvus docker-compose..."
            wget https://github.com/milvus-io/milvus/releases/download/v2.3.3/milvus-standalone-docker-compose.yml -O docker-compose-milvus.yml
        fi
        docker-compose -f docker-compose-milvus.yml up -d
        echo "Milvus started on localhost:19530"
        echo "Update .env file: VECTOR_DB_TYPE=milvus"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "Setup complete!"
