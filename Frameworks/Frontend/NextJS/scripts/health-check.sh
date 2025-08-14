#!/bin/bash

echo "🔍 Running application health checks..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Health check results
HEALTH_PASSED=0
HEALTH_TOTAL=0

check_service() {
    local service_name="$1"
    local check_command="$2"
    local expected_result="$3"
    
    HEALTH_TOTAL=$((HEALTH_TOTAL + 1))
    
    echo -n "Checking $service_name... "
    
    if eval "$check_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        HEALTH_PASSED=$((HEALTH_PASSED + 1))
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "   Command: $check_command"
    fi
}

check_http_endpoint() {
    local endpoint_name="$1"
    local url="$2"
    local expected_status="$3"
    
    HEALTH_TOTAL=$((HEALTH_TOTAL + 1))
    
    echo -n "Checking $endpoint_name ($url)... "
    
    local status_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC} (HTTP $status_code)"
        HEALTH_PASSED=$((HEALTH_PASSED + 1))
    else
        echo -e "${RED}❌ FAIL${NC} (HTTP $status_code, expected $expected_status)"
    fi
}

# Check Docker containers
echo "🐳 Docker Container Status:"
check_service "PostgreSQL container" "docker ps | grep webapp_postgres" ""
check_service "Redis container" "docker ps | grep webapp_redis" ""
check_service "Application container" "docker ps | grep webapp_frontend" ""

echo ""

# Check database connectivity
echo "🗄️ Database Connectivity:"
check_service "PostgreSQL connection" "docker exec webapp_postgres pg_isready -U webapp_user -d webapp_db" ""

echo ""

# Check Redis connectivity  
echo "🔄 Cache Connectivity:"
check_service "Redis connection" "docker exec webapp_redis redis-cli ping | grep PONG" ""

echo ""

# Check HTTP endpoints
echo "🌐 HTTP Endpoints:"
check_http_endpoint "Health endpoint" "http://localhost:3000/api/health" "200"
check_http_endpoint "Homepage" "http://localhost:3000/" "200"
check_http_endpoint "API Users" "http://localhost:3000/api/users" "200"
check_http_endpoint "API Products" "http://localhost:3000/api/products" "200"
check_http_endpoint "API Quotes" "http://localhost:3000/api/quotes" "200"
check_http_endpoint "API Posts" "http://localhost:3000/api/posts" "200"
check_http_endpoint "API Analytics" "http://localhost:3000/api/analytics" "200"

echo ""

# Check file system
echo "📁 File System:"
check_service "Environment file" "test -f .env" ""
check_service "Package.json" "test -f package.json" ""
check_service "Next.js config" "test -f next.config.mjs" ""
check_service "Prisma schema" "test -f prisma/schema.prisma" ""

echo ""

# Display summary
echo "📊 Health Check Summary:"
if [ $HEALTH_PASSED -eq $HEALTH_TOTAL ]; then
    echo -e "${GREEN}✅ All checks passed ($HEALTH_PASSED/$HEALTH_TOTAL)${NC}"
    echo "🚀 Application is healthy and ready for production!"
else
    FAILED=$((HEALTH_TOTAL - HEALTH_PASSED))
    echo -e "${RED}❌ $FAILED checks failed ($HEALTH_PASSED/$HEALTH_TOTAL passed)${NC}"
    echo ""
    echo "🔧 Troubleshooting suggestions:"
    echo "   1. Check if all containers are running: docker-compose ps"
    echo "   2. Check container logs: docker-compose logs [service]"
    echo "   3. Verify environment variables in .env file"
    echo "   4. Ensure database migrations are applied: npm run db:migrate"
    echo "   5. Check if ports 3000, 5432, 6379 are available"
fi

echo ""
echo "🔗 Useful commands:"
echo "   docker-compose ps                    - Check container status"
echo "   docker-compose logs -f              - Follow all logs"
echo "   docker-compose logs webapp          - Check app logs"
echo "   npm run dev                         - Start development mode"
echo "   ./scripts/backup-db.sh              - Backup database"
echo ""

# Exit with error code if any checks failed
if [ $HEALTH_PASSED -ne $HEALTH_TOTAL ]; then
    exit 1
fi
