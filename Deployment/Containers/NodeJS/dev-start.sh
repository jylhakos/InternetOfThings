#!/bin/bash

echo "🚀 Starting Development Environment"
echo "👤 User: " + $USER
echo ""

# Start in development mode
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

echo "🎉 Development environment started!"