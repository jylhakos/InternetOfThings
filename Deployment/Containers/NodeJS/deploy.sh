#!/bin/bash

echo "🚀 Deploying Node.js Express + React application with Docker"
echo "👤 User: " + $USER
echo "📅 Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo "🐧 Platform: Linux"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "🔍 Checking prerequisites..."
if ! command_exists docker; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command_exists docker-compose; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if Docker daemon is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker daemon is not running. Please start Docker first."
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Create project directories
echo "📁 Creating project structure..."
mkdir -p backend frontend

# Set proper permissions for Linux
echo "🔒 Setting permissions..."
sudo chown -R $USER:$USER .
chmod -R 755 .

# Clean up existing containers (optional)
echo "🧹 Cleaning up existing containers..."
docker-compose down -v 2>/dev/null || true

# Remove old images (optional)
echo "🗑️ Removing old images..."
docker image prune -f 2>/dev/null || true

# Build and start services
echo "🏗️ Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 45

# Check service status
echo "🔍 Checking service status..."
docker-compose ps

# Function to check service health
check_service_health() {
    local service_name=$1
    local url=$2
    local max_attempts=30
    local attempt=1

    echo "🏥 Checking $service_name health..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" >/dev/null 2>&1; then
            echo "✅ $service_name is healthy"
            return 0
        fi
        
        echo "⏳ Attempt $attempt/$max_attempts - waiting for $service_name..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_name health check failed"
    return 1
}

# Check backend health
check_service_health "Backend API" "http://localhost:5000/health"

# Check frontend health
check_service_health "React Frontend" "http://localhost:3000"

# Display service information
echo ""
echo "📊 Service information:"
echo "----------------------------------------"
echo "🔗 React Frontend: http://localhost:3000"
echo "🔗 Node.js Backend: http://localhost:5000"
echo "🔗 Backend Health: http://localhost:5000/health"
echo "🔗 MongoDB: localhost:27017"
echo ""

# Display container logs (last 10 lines)
echo "📋 Recent logs:"
echo "----------------------------------------"
echo "Backend logs:"
docker-compose logs --tail=10 backend
echo ""
echo "Frontend logs:"
docker-compose logs --tail=10 frontend

echo ""
echo "✅ Deployment completed successfully."
echo "🎉 Your Node.js Express + React application is now running in Docker containers"
echo ""
echo "📋 Useful commands:"
echo "  - View logs: docker-compose logs -f [service_name]"
echo "  - Stop services: docker-compose down"
echo "  - Restart services: docker-compose restart"
echo "  - Shell access: docker-compose exec [service_name] sh"
echo ""
echo "👤 Deployed by: " + $USER
echo "📅 Deployment time: $(date '+%Y-%m-%d %H:%M:%S UTC')"