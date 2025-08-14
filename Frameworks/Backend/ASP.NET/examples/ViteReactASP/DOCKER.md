# Docker Deployment

## Docker Compose Files

Your project uses **Docker Compose files**

### 1. `docker-compose.yml` (Production)
- **Purpose**: Production deployment configuration
- **Contains**: Complete stack with all services
- **Database**: PostgreSQL for production
- **Cache**: Redis for distributed caching
- **Proxy**: Nginx for load balancing and SSL
- **Build**: Optimized production Docker image

### 2. `docker-compose.dev.yml` (Development)
- **Purpose**: Development-specific overrides
- **Contains**: Hot reload, debugging features
- **Database**: SQLite for simplicity
- **Cache**: Disabled for development
- **Proxy**: Direct access for debugging

## Deployment Scenarios

### **Development Mode** (Hot Reload)
```bash
# Option 1: Lightweight development (SQLite + Hot Reload)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Option 2: Full development stack (PostgreSQL + Redis)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --profile full-dev up

# Option 3: Just the API for testing
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up vite-react-asp
```

### **Production Mode**
```bash
# Full production deployment
docker-compose up -d

# Scale the application
docker-compose up -d --scale vite-react-asp=3

# Production with monitoring
docker-compose --profile monitoring up -d
```

### **Testing Mode**
```bash
# Start services for testing
docker-compose up -d postgres redis

# Run integration tests
docker-compose -f docker-compose.yml -f docker-compose.test.yml run --rm tests
```

## 🔧 Docker Commands

### **Build and Deploy**
```bash
# Build images
docker-compose build

# Build with no cache
docker-compose build --no-cache

# Pull latest images
docker-compose pull

# Deploy production
docker-compose up -d
```

### **Development Workflow**
```bash
# Start development environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Rebuild after dependency changes
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# View logs
docker-compose logs -f vite-react-asp

# Execute commands in running container
docker-compose exec vite-react-asp bash
```

### **Maintenance**
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ Data loss)
docker-compose down -v

# View service status
docker-compose ps

# Scale services
docker-compose up -d --scale vite-react-asp=2
```

## Services

```
┌─────────────────────────────────────────────────────────┐
│                    DOCKER NETWORK                       │
│                   (app-network)                         │
│                                                         │
│  ┌─────────────┐    ┌──────────────┐    ┌────────────┐  │
│  │             │    │              │    │            │  │
│  │   Nginx     │    │ Vite+React+  │    │PostgreSQL  │  │
│  │   :80/443   │◄──►│  ASP.NET     │◄──►│   :5432    │  │
│  │             │    │    :8080     │    │            │  │
│  │ Load        │    │              │    │ Persistent │  │
│  │ Balancer    │    │ Application  │    │ Storage    │  │
│  └─────────────┘    │ Container    │    └────────────┘  │
│                     └──────────────┘           │        │
│                             │                  │        │
│                             ▼                  │        │
│                     ┌──────────────┐           │        │
│                     │              │           │        │
│                     │    Redis     │           │        │
│                     │    :6379     │           │        │
│                     │              │           │        │
│                     │ Distributed  │           │        │
│                     │ Cache        │           │        │
│                     └──────────────┘           │        │
│                                                │        │
│                     ┌──────────────┐           │        │
│                     │              │           │        │
│                     │   Volumes    │◄──────────┘        │
│                     │              │                    │
│                     │ postgres_data│                    │
│                     │ redis_data   │                    │
│                     └──────────────┘                    │
└─────────────────────────────────────────────────────────┘
```

## Environment Configurations

### **Production Environment Variables**
```yaml
environment:
  - ASPNETCORE_ENVIRONMENT=Production
  - ConnectionStrings__DefaultConnection=Host=postgres;Database=ViteReactAspDb;Username=appuser;Password=devpassword123
  - ConnectionStrings__Redis=redis:6379
  - CacheSettings__DefaultExpirationMinutes=30
```

### **Development Environment Variables**
```yaml
environment:
  - ASPNETCORE_ENVIRONMENT=Development
  - ConnectionStrings__DefaultConnection=Data Source=/app/data/contacts-dev.db
  - DOTNET_USE_POLLING_FILE_WATCHER=true
  - DOTNET_WATCH_RESTART_ON_RUDE_EDIT=true
```

## Health Checks and Monitoring

### **Built-in Health Checks**
- **Application**: `http://localhost:8080/health`
- **Database**: PostgreSQL ready check
- **Cache**: Redis ping check
- **Proxy**: Nginx status check

### **Monitoring Commands**
```bash
# Check service health
docker-compose ps

# View resource usage
docker stats

# Monitor logs
docker-compose logs -f --tail=100

# Database connection test
docker-compose exec postgres pg_isready -U appuser

# Cache test
docker-compose exec redis redis-cli ping
```

## Start Commands

### **For Development**
```bash
# Quick development start
./quick-start.sh

# Or manually
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### **For Production**
```bash
# Production deployment
docker-compose up -d

# Check deployment status
docker-compose ps
docker-compose logs vite-react-asp

# Access the application
curl http://localhost/health
curl http://localhost/api/contacts
```

### **For Testing**
```bash
# Start services
docker-compose up -d

# Wait for services to be ready
sleep 30

# Run tests
./test-contacts-api.sh

# Load testing
./load-test-api.sh
```

## 🔒 Security Considerations

### **Production Security**
- Environment variables for secrets
- Non-root user in containers
- Security headers enabled
- Network isolation
- Volume permissions
- SSL/TLS termination at Nginx

### **Development Security**
- Isolated development network
- Local databases only
- Debug information enabled
- CORS relaxed for development

## Scaling and Performance

### **Horizontal Scaling**
```bash
# Scale application instances
docker-compose up -d --scale vite-react-asp=3

# Database read replicas (advanced)
docker-compose -f docker-compose.yml -f docker-compose.replica.yml up -d
```

### **Performance Optimization**
- Redis caching layer
- Connection pooling
- Static file serving via Nginx
- Gzip compression
- Container resource limits

## 🛠️ Troubleshooting

### Issues
```bash
# Port conflicts
netstat -tulpn | grep :8080

# Container logs
docker-compose logs vite-react-asp

# Database connection issues
docker-compose exec vite-react-asp curl -f http://postgres:5432

# Cache connection issues
docker-compose exec vite-react-asp telnet redis 6379

# Cleanup and restart
docker-compose down && docker-compose up -d
```

### **Development Issues**
```bash
# Hot reload not working
docker-compose -f docker-compose.yml -f docker-compose.dev.yml restart vite-react-asp

# File permission issues (Linux/macOS)
sudo chown -R $USER:$USER ./

# Node modules issues
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down
docker volume prune
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```
