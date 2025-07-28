# Deployment

This guide covers deploying the LLM FastAPI + Celery + LangChain.js system in production.

## Table of contents

1. [Prerequisites](#prerequisites)
2. [Environment](#environment-setup)
3. [Docker deployment](#docker-deployment)
4. [Kubernetes deployment](#kubernetes-deployment)
5. [Monitoring and logging](#monitoring-and-logging)
6. [Security](#security-considerations)
7. [Performance](#performance-tuning)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### System requirements

**Minimum requirements:**
- CPU: 4 cores
- RAM: 8GB
- Storage: 50GB SSD
- Network: 1Gbps

**Recommended for production:**
- CPU: 8+ cores
- RAM: 16GB+
- Storage: 100GB+ SSD
- Network: 1Gbps+
- GPU: Optional (for larger models)

### Software requirements

- Docker 20.10+
- Docker Compose 2.0+
- Linux kernel 4.0+
- Git

## Environment

### 1. Clone and setup

```bash
git clone <your-repository>
cd llm-fastapi-celery-system
```

### 2. Configuration

Create production environment file:

```bash
cp .env .env.production
```

Edit `.env.production`:

```bash
# Production Configuration
ENVIRONMENT=production
DEBUG=false

# Redis Configuration
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Ollama Configuration
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=llama3.1

# LangChain Service Configuration
LANGCHAIN_SERVICE_URL=http://langchain-service:3000

# FastAPI Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Celery Configuration
CELERY_WORKER_CONCURRENCY=8
CELERY_TASK_TIMEOUT=600

# Security
SECRET_KEY=your-very-secure-secret-key-here-change-this
ALLOWED_HOSTS=your-domain.com,api.your-domain.com

# Monitoring
FLOWER_BASIC_AUTH=admin:secure-password

# SSL/TLS
USE_SSL=true
SSL_CERT_PATH=/etc/ssl/certs/cert.pem
SSL_KEY_PATH=/etc/ssl/private/key.pem
```

## Docker deployment

### 1. Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: llm-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/ssl
      - ./nginx/logs:/var/log/nginx
    depends_on:
      - fastapi
      - langchain-service
    networks:
      - llm-network

  # Redis with persistence
  redis:
    image: redis:7-alpine
    container_name: llm-redis
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
      - ./redis/redis.conf:/etc/redis/redis.conf
    networks:
      - llm-network
    healthcheck:
      test: ["CMD", "redis-cli", "--no-auth-warning", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5

  # Ollama with GPU support
  ollama:
    image: ollama/ollama:latest
    container_name: llm-ollama
    restart: unless-stopped
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0
      - OLLAMA_ORIGINS=*
    networks:
      - llm-network
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  # LangChain.js Service
  langchain-service:
    build:
      context: ./langchain-service
      dockerfile: Dockerfile.prod
    container_name: llm-langchain
    restart: unless-stopped
    environment:
      - NODE_ENV=production
      - PORT=3000
      - OLLAMA_URL=http://ollama:11434
    depends_on:
      - ollama
    networks:
      - llm-network
    deploy:
      replicas: 2

  # FastAPI
  fastapi:
    build:
      context: ./python-app
      dockerfile: Dockerfile.prod
    container_name: llm-fastapi
    restart: unless-stopped
    environment:
      - ENVIRONMENT=production
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - CELERY_RESULT_BACKEND=redis://:${REDIS_PASSWORD}@redis:6379/0
    depends_on:
      - redis
      - langchain-service
    networks:
      - llm-network
    deploy:
      replicas: 2

  # Celery Workers
  celery-worker:
    build:
      context: ./python-app
      dockerfile: Dockerfile.prod
    restart: unless-stopped
    command: celery -A celery_app worker --loglevel=info --concurrency=4
    environment:
      - ENVIRONMENT=production
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - CELERY_RESULT_BACKEND=redis://:${REDIS_PASSWORD}@redis:6379/0
    depends_on:
      - redis
      - langchain-service
    networks:
      - llm-network
    deploy:
      replicas: 4

  # Monitoring
  flower:
    build:
      context: ./python-app
      dockerfile: Dockerfile.prod
    container_name: llm-flower
    restart: unless-stopped
    command: celery -A celery_app flower --port=5555 --basic_auth=${FLOWER_BASIC_AUTH}
    environment:
      - CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
    depends_on:
      - redis
    networks:
      - llm-network

  # Log aggregation
  fluentd:
    image: fluent/fluentd:edge-debian
    container_name: llm-fluentd
    restart: unless-stopped
    volumes:
      - ./fluentd/fluent.conf:/fluentd/etc/fluent.conf
      - ./logs:/fluentd/log
    networks:
      - llm-network

volumes:
  redis_data:
    driver: local
  ollama_data:
    driver: local

networks:
  llm-network:
    driver: bridge
```

### 2. Production Dockerfiles

**python-app/Dockerfile.prod:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

**langchain-service/Dockerfile.prod:**
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Copy application code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodeuser -u 1001
RUN chown -R nodeuser:nodejs /app
USER nodeuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

EXPOSE 3000

CMD ["node", "server.js"]
```

### 3. Deploy with Docker Compose

```bash
# Pull latest images
docker-compose -f docker-compose.prod.yml pull

# Build and start services
docker-compose -f docker-compose.prod.yml up -d --build

# Check service status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

## Kubernetes deployment

### 1. Namespace and ConfigMap

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: llm-system

---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: llm-config
  namespace: llm-system
data:
  OLLAMA_URL: "http://ollama-service:11434"
  LANGCHAIN_SERVICE_URL: "http://langchain-service:3000"
  REDIS_URL: "redis://redis-service:6379/0"
```

### 2. Redis deployment

```yaml
# k8s/redis.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: llm-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        volumeMounts:
        - name: redis-storage
          mountPath: /data
      volumes:
      - name: redis-storage
        persistentVolumeClaim:
          claimName: redis-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
  namespace: llm-system
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: redis-pvc
  namespace: llm-system
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

### 3. Deploy to Kubernetes

```bash
# Apply configurations
kubectl apply -f k8s/

# Check deployments
kubectl get pods -n llm-system

# Get service URLs
kubectl get services -n llm-system
```

## Monitoring and logging

### 1. Prometheus monitoring

Add to `docker-compose.prod.yml`:

```yaml
  prometheus:
    image: prom/prometheus
    container_name: llm-prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - llm-network

  grafana:
    image: grafana/grafana
    container_name: llm-grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana:/etc/grafana/provisioning
    networks:
      - llm-network
```

### 2. Logs

**fluentd/fluent.conf:**
```xml
<source>
  @type forward
  port 24224
  bind 0.0.0.0
</source>

<match docker.**>
  @type file
  path /fluentd/log/docker
  time_slice_format %Y%m%d
  time_slice_wait 10m
  time_format %Y%m%dT%H%M%S%z
  compress gzip
  utc
</match>
```

## Security

### 1. SSL/TLS

**nginx/nginx.conf:**
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

    location / {
        proxy_pass http://fastapi:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /langchain/ {
        proxy_pass http://langchain-service:3000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. Firewall rules

```bash
# Allow only necessary ports
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 3. Security Headers

Add to FastAPI application:

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["your-domain.com"])
app.add_middleware(HTTPSRedirectMiddleware)
```

## Performance

### 1. Redis optimization

**redis/redis.conf:**
```
maxmemory 4gb
maxmemory-policy allkeys-lru
tcp-keepalive 60
timeout 300
```

### 2. Celery optimization

```python
# celery_app.py
celery_app.conf.update(
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    task_time_limit=600,
    task_soft_time_limit=580,
)
```

### 3. FastAPI optimization

```python
# main.py
app = FastAPI(
    title="LLM Processing API",
    docs_url=None if not settings.DEBUG else "/docs",
    redoc_url=None if not settings.DEBUG else "/redoc"
)

# Use gunicorn in production
# gunicorn main:app -k uvicorn.workers.UvicornWorker --workers 4
```

## Troubleshooting

### Issues

1. **High Memory Usage**
   ```bash
   # Check container memory usage
   docker stats
   
   # Limit container memory
   docker run --memory=2g your-image
   ```

2. **Slow Response Times**
   ```bash
   # Check Celery queue length
   celery -A celery_app inspect active_queues
   
   # Scale workers
   docker-compose up --scale celery-worker=8
   ```

3. **Connection Issues**
   ```bash
   # Test service connectivity
   docker exec -it llm-fastapi curl http://langchain-service:3000/health
   
   # Check DNS resolution
   docker exec -it llm-fastapi nslookup redis
   ```

### Monitoring

```bash
# Check service health
curl http://localhost:8000/health

# Monitor Celery workers
celery -A celery_app inspect stats

# Check Redis memory usage
redis-cli info memory

# View container logs
docker-compose logs -f --tail=100 fastapi
```

### Backup and recovery

```bash
# Backup Redis data
docker exec llm-redis redis-cli --rdb /data/backup.rdb

# Backup Ollama models
docker cp llm-ollama:/root/.ollama ./ollama-backup

# Database backup (if using database)
docker exec postgres pg_dump -U user database > backup.sql
```
