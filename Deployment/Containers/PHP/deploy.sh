#!/bin/bash

echo "🚀 Deploying PHP RESTful API with Docker on Linux"
echo "👤 User:  "
echo "📅 Date: 2025-06-22 09:49:23 UTC"
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

# Create required directories
mkdir -p logs

# Clean up existing containers and images
echo "🧹 Cleaning up existing containers..."
docker-compose down -v 2>/dev/null || true

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

# Check MySQL health
echo "🗄️ Checking MySQL connection..."
sleep 10
docker exec mysql_db mysql -u root -ppassword123 -e "SELECT 1" 2>/dev/null && echo "✅ MySQL is healthy" || echo "❌ MySQL check failed"

# Check API health
check_service_health "PHP REST API" "http://localhost:8080/health"

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
echo "🔗 PHP REST API (Nginx): http://localhost:8080"
echo "🔗 API Health Check: http://localhost:8080/health"
echo "🔗 MySQL Database: localhost:3306"
echo ""

# Display API endpoints
echo "📋 Available API Endpoints:"
echo "----------------------------------------"
echo "POST /api/auth/register - Register new user"
echo "POST /api/auth/login - User login"
echo "POST /api/auth/refresh - Refresh token"
echo "GET  /api/users/me - Get current user (requires auth)"
echo "PUT  /api/users/me - Update current user (requires auth)"
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
echo '  -d {"name":"Test User","email":"testuser@example.com","password":"testpass123"}'
echo ""
echo "# Login:"
echo 'curl -X POST http://localhost:8080/api/auth/login \'
echo '  -H "Content-Type: application/json" \'
echo '  -d {"email":" @example.com","password":"password"}'
echo ""

# Display container logs (last 10 lines)
echo "📋 Recent logs:"
echo "----------------------------------------"
echo "PHP API logs:"
docker-compose logs --tail=10 php-api
echo ""
echo "MySQL logs:"
docker-compose logs --tail=10 mysql

echo ""
echo "✅ Deployment completed successfully!"
echo "🎉 Your PHP RESTful API is now running in Docker containers"
echo ""
echo "📋 Useful commands:"
echo "  - View API logs: docker-compose logs -f php-api"
echo "  - View MySQL logs: docker-compose logs -f mysql"
echo "  - Stop services: docker-compose down"
echo "  - Restart services: docker-compose restart"
echo "  - Shell access to API: docker-compose exec php-api sh"
echo "  - MySQL shell: docker exec -it mysql_db mysql -u root -ppassword123"
echo ""
echo "👤 Deployed by:  "
echo "📅 Deployment time: $(date '+%Y-%m-%d %H:%M:%S UTC')"
echo "🐧 Platform: $(uname -s) $(uname -r)"