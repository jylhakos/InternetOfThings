#!/bin/bash

echo "🚀 Deploying ASP.NET Core Web API with MongoDB on Docker (Linux)"
echo "👤 User: "
echo "📅 Date: 2025-06-22 09:28:27 UTC"
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

# Set proper permissions for Linux
echo "🔒 Setting permissions..."
sudo chown -R $USER:$USER .
chmod +x deploy.sh
chmod -R 755 .

# Clean up existing containers and images
echo "🧹 Cleaning up existing containers and images..."
docker-compose down -v 2>/dev/null || true
docker system prune -f 2>/dev/null || true

# Build and start services
echo "🏗️ Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 60

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
        sleep 3
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_name health check failed"
    return 1
}

# Check MongoDB health
echo "🔗 Checking MongoDB connection..."
sleep 10
docker exec mongodb mongosh --eval "db.adminCommand('ping')" --quiet 2>/dev/null && echo "✅ MongoDB is healthy" || echo "❌ MongoDB check failed"

# Check API health
check_service_health "ASP.NET Core API" "http://localhost:8080/health"

# Test API endpoints
echo ""
echo "🧪 Testing API endpoints..."

# Test root endpoint
echo "Testing root endpoint..."
curl -s http://localhost:8080/ | jq . 2>/dev/null || curl -s http://localhost:8080/

echo ""
echo "Testing health endpoint..."
curl -s http://localhost:8080/health | jq . 2>/dev/null || curl -s http://localhost:8080/health

# Display service information
echo ""
echo "📊 Service Information:"
echo "----------------------------------------"
echo "🔗 ASP.NET Core API: http://localhost:8080"
echo "🔗 API Health Check: http://localhost:8080/health"
echo "🔗 Swagger Documentation: http://localhost:8080/swagger"
echo "🔗 MongoDB: localhost:27017"
echo ""

# Display API endpoints
echo "📋 Available API Endpoints:"
echo "----------------------------------------"
echo "POST /api/auth/register - Register new user"
echo "POST /api/auth/login - User login"
echo "GET  /api/tasks - Get all tasks (requires auth)"
echo "POST /api/tasks - Create new task (requires auth)"
echo "GET  /api/tasks/{id} - Get specific task (requires auth)"
echo "PUT  /api/tasks/{id} - Update task (requires auth)"
echo "DELETE /api/tasks/{id} - Delete task (requires auth)"
echo ""

# Display sample API calls
echo "🔧 Sample API Usage:"
echo "----------------------------------------"
echo "# Register a new user:"
echo 'curl -X POST http://localhost:8080/api/auth/register \'
echo '  -H "Content-Type: application/json" \'
echo '  -d {"name":"Test User","email":"test@example.com","password":"testpass123"}'
echo ""
echo "# Login:"
echo 'curl -X POST http://localhost:8080/api/auth/login \'
echo '  -H "Content-Type: application/json" \'
echo '  -d {"email":"test@example.com","password":"testpass123"}'
echo ""

# Display container logs (last 10 lines)
echo "📋 Recent logs:"
echo "----------------------------------------"
echo "ASP.NET Core API logs:"
docker-compose logs --tail=10 taskapi
echo ""
echo "MongoDB logs:"
docker-compose logs --tail=10 mongo

echo ""
echo "✅ Deployment completed successfully!"
echo "🎉 Your ASP.NET Core Web API with MongoDB is now running in Docker containers"
echo ""
echo "📋 Useful commands:"
echo "  - View API logs: docker-compose logs -f taskapi"
echo "  - View MongoDB logs: docker-compose logs -f mongo"
echo "  - Stop services: docker-compose down"
echo "  - Restart services: docker-compose restart"
echo "  - Shell access to API: docker-compose exec taskapi bash"
echo "  - MongoDB shell: docker exec -it mongodb mongosh -u root -p password123"
echo ""
echo "👤 Deployed by: "
echo "📅 Deployment time: $(date '+%Y-%m-%d %H:%M:%S UTC')"
echo "🐧 Platform: $(uname -s) $(uname -r)"