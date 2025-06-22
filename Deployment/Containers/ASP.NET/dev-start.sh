#!/bin/bash

echo "🚀 Starting Development Environment"
echo "👤 User: "
echo "📅 Date: 2025-06-22 09:28:27 UTC"
echo ""

# Set development environment
export ASPNETCORE_ENVIRONMENT=Development

# Start MongoDB first
echo "🍃 Starting MongoDB..."
docker-compose up -d mongo

# Wait for MongoDB to be ready
echo "⏳ Waiting for MongoDB to be ready..."
sleep 20

# Start the API in development mode
echo "🚀 Starting ASP.NET Core API in development mode..."
dotnet run --urls="http://localhost:5000"