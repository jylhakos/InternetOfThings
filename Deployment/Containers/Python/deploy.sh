#!/bin/bash

echo "🚀 Deploying Python RESTful APIs + React app with Docker..."

# Create necessary directories
mkdir -p app frontend

# Clean up existing containers
echo "🧹 Cleaning up existing containers..."
docker-compose down -v

# Build and start services
echo "🏗️ Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check service status
echo "🔍 Checking service status..."
docker-compose ps

# Test the RESTful API
echo "🧪 Testing..."
curl -X GET http://localhost:8000/health
curl -X GET http://localhost:8000/

echo "✅ Deployment completed"
echo "🔗 RESTful API: http://localhost:8000"
echo "🔗 React app: http://localhost:3000"
echo "🔗 API documentation: http://localhost:8000/docs"