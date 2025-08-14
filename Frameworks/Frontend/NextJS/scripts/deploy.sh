#!/bin/bash

echo "🚀 Deploying to production..."

# Set production environment
export NODE_ENV=production

# Check if .env.production exists
if [ ! -f .env.production ]; then
    echo "❌ .env.production file not found!"
    echo "   Please create .env.production with production settings"
    exit 1
fi

# Copy production environment
cp .env.production .env

# Build and push Docker image
echo "🔨 Building Docker image..."
docker build -t webapp:latest .

# Check if build was successful
if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

# Create production docker-compose file if it doesn't exist
if [ ! -f docker-compose.production.yml ]; then
    echo "📝 Creating production docker-compose file..."
    cat > docker-compose.production.yml << EOL
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: webapp_postgres_prod
    restart: unless-stopped
    environment:
      POSTGRES_USER: \${POSTGRES_USER}
      POSTGRES_PASSWORD: \${POSTGRES_PASSWORD}
      POSTGRES_DB: \${POSTGRES_DB}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data_prod:/var/lib/postgresql/data
    networks:
      - webapp_network_prod
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U \${POSTGRES_USER} -d \${POSTGRES_DB}"]
      interval: 30s
      timeout: 10s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: webapp_redis_prod
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data_prod:/data
    networks:
      - webapp_network_prod
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5

  webapp:
    image: webapp:latest
    container_name: webapp_frontend_prod
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=\${DATABASE_URL}
      - DIRECT_URL=\${DIRECT_URL}
      - REDIS_URL=redis://redis:6379
      - NODE_ENV=production
      - NEXTAUTH_SECRET=\${NEXTAUTH_SECRET}
      - JWT_SECRET=\${JWT_SECRET}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - webapp_network_prod
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    container_name: webapp_nginx_prod
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./docker/nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - webapp
    networks:
      - webapp_network_prod

volumes:
  postgres_data_prod:
    driver: local
  redis_data_prod:
    driver: local

networks:
  webapp_network_prod:
    driver: bridge
EOL
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.production.yml down

# Start production environment
echo "▶️ Starting production environment..."
docker-compose -f docker-compose.production.yml up -d

# Wait for application to be ready
echo "⏳ Waiting for application to be ready..."
sleep 30

# Run migrations
echo "🗄️ Running database migrations..."
docker exec webapp_frontend_prod npx prisma migrate deploy

# Check if deployment was successful
if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
    echo ""
    echo "✅ Deployment complete!"
    echo "🌐 Application is running at http://localhost"
    echo "📊 Health check: http://localhost/api/health"
    echo ""
    echo "🔗 Useful commands:"
    echo "   docker-compose -f docker-compose.production.yml logs -f  - View logs"
    echo "   docker-compose -f docker-compose.production.yml down     - Stop services"
    echo "   ./scripts/backup-db.sh                                   - Backup database"
else
    echo "❌ Deployment failed! Application health check failed."
    echo "📋 Check logs: docker-compose -f docker-compose.production.yml logs"
    exit 1
fi
