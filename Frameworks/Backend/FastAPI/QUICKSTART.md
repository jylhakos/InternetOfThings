# FastAPI for DevOps

## Quick Start

```bash
# 1. Run the DevOps setup script
./setup-devops.sh

# 2. Activate virtual environment
source venv/bin/activate

# 3. Start development server
./start-dev.sh

# 4. In another terminal, run tests
./curl-tests.sh
```

## Benchmarking (Performance)

### Stack Performance

**Performance Hierarchy (fastest to slowest):**

1. **Uvicorn** - Pure ASGI server (~65,000 req/s)
2. **Starlette** - Web microframework (~60,000 req/s)
3. **FastAPI** - API framework with validation (~45,000 req/s)

### Production Deployment - Options

```bash
# Single process (development)
uvicorn main:app --host 0.0.0.0 --port 8000

# Multiple workers (production)
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000

# Gunicorn + Uvicorn workers (recommended)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Testing Commands

### Health Check

```bash
curl -X GET http://localhost:8000/health
```

### Load Testing

```bash
# Simple load test (100 requests, 10 concurrent)
seq 1 100 | xargs -n1 -P10 -I{} curl -s -o /dev/null http://localhost:8000/health

# With Apache Bench
ab -n 1000 -c 50 http://localhost:8000/health

# With wrk (if installed)
wrk -t12 -c400 -d30s http://localhost:8000/health
```

### Authentication Flow

```bash
# Register user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1234567890", "password": "SecurePass123!", "email": "test@example.com"}'

# Login and get token
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=%2B1234567890&password=SecurePass123!" \
  -s | jq -r .access_token)

# Use token
curl -X GET http://localhost:8000/users/profile \
  -H "Authorization: Bearer $TOKEN"
```

## 🐳 Docker Commands

```bash
# Start infrastructure
docker-compose up -d postgres redis

# Check status
docker ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🔧 Jenkins Virtual Environment

Jenkins automatically creates and manages Python virtual environments.

```groovy
stage('Setup Environment') {
    steps {
        sh '''
            python3 -m venv venv
            . venv/bin/activate
            pip install --upgrade pip
            pip install -r requirements.txt
        '''
    }
}
```

## Monitoring

- **Health**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics
- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3000 (if monitoring stack is running)
- **Prometheus**: http://localhost:9090

## Troubleshooting

```bash
# Check service status
docker ps
systemctl status nginx

# Check ports
netstat -tulpn | grep :8000

# Test database connection
docker exec -it postgres psql -U postgres -d microservices

# Test Redis connection
docker exec -it redis redis-cli ping

# Check FastAPI logs
tail -f /var/log/fastapi.log
```

For detailed information, see the [README.md](README.md) file.

## Optimization

1. **Use multiple workers in production**
2. **Enable connection pooling for database**
3. **Implement caching with Redis**
4. **Use Nginx for static files and SSL termination**
5. **Monitor with Prometheus + Grafana**
6. **Set up distributed tracing with Jaeger**

---
