#!/bin/bash

# Build and run the application
echo "Building and starting the application..."

# Clean up existing containers and volumes (optional)
# docker-compose down -v

# Build and start services
docker-compose up --build -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 30

# Check if services are running
docker-compose ps

# Test the API
echo "Testing the API..."
curl -X GET http://localhost:8080/api/users
curl -X GET http://localhost:8080/actuator/health

echo "Deployment complete!"
echo "API is available at: http://localhost:8080/api/users"
echo "Health check at: http://localhost:8080/actuator/health"