# Docker Compose for Agents - DevOps

## Overview for DevOps

This document provides deployment and operational information for running AI agents with Docker Compose in production and development environments.

## System Requirements

### Minimum Requirements

- **CPU**: 4 cores
- **RAM**: 8 GB
- **Disk**: 20 GB free space
- **Docker**: Engine 20.10+ or Desktop 4.43.0+
- **Docker Compose**: 2.38.1+

### Recommended for Production

- **CPU**: 8+ cores with GPU (NVIDIA Tesla, A100, or similar)
- **RAM**: 16+ GB
- **Disk**: 50+ GB SSD
- **Network**: Stable connection for model downloads

## Deployment Options

### Local Development

```bash
# Standard setup with local model inference
docker compose up
```

### Production with OpenAI

```bash
# Create secret file
echo "$OPENAI_API_KEY" > secret.openai-api-key

# Deploy with OpenAI backend
docker compose -f compose.yaml -f compose.openai.yaml up -d
```

### Cloud Deployment (AWS/Azure/GCP)

```bash
# Enable BuildKit for faster builds
export DOCKER_BUILDKIT=1

# Build and push to registry
docker compose build
docker compose push

# Deploy on remote host
docker compose -H ssh://user@remote-host up -d
```

## Service Architecture

### Service Dependencies

```
┌─────────────────────────────────────────┐
│          Docker Compose Stack           │
├─────────────────────────────────────────┤
│                                         │
│  agent ──────────────┐                  │
│    │                 │                  │
│    ├─▶ mcp-gateway ──┼─▶ database       │
│    │                 │                  │
│    └─▶ model-runner  │                  │
│                      │                  │
│         importer ────┘                  │
│                                         │
└─────────────────────────────────────────┘
```

### Service Descriptions

| Service        | Purpose                       | Restart Policy |
| -------------- | ----------------------------- | -------------- |
| `database`     | PostgreSQL database           | always         |
| `importer`     | SQLite → PostgreSQL migration | on-failure     |
| `agent`        | LangGraph AI agent            | on-failure     |
| `mcp-gateway`  | MCP protocol server           | unless-stopped |
| `model-runner` | Local LLM inference           | unless-stopped |

## Configuration Management

### Environment Variables

Key environment variables for customization:

```yaml
# Agent Configuration
QUESTION=Your question here
MODEL_NAME=llama3.2
DATABASE_DIALECT=PostgreSQL

# OpenAI Configuration (optional)
OPENAI_API_KEY=sk-...
OPENAI_API_BASE_URL=https://api.openai.com/v1

# MCP Configuration
MCP_SERVER_URL=http://mcp-gateway:8811/sse

# Database Configuration
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=database
DATABASE_URL=postgres://user:password@database:5432/database
```

### Secrets Management

For production deployments, use Docker secrets:

```yaml
services:
  agent:
    secrets:
      - openai_api_key
    environment:
      - OPENAI_API_KEY_FILE=/run/secrets/openai_api_key

secrets:
  openai_api_key:
    external: true
```

Create the secret:

```bash
echo "sk-your-key" | docker secret create openai_api_key -
```

## Monitoring & Logging

### Health Checks

```bash
# Check service status
docker compose ps

# Check database health
docker compose exec database pg_isready -U user -d database

# View resource usage
docker stats
```

### Centralized Logging

Configure logging driver in `compose.yaml`:

```yaml
services:
  agent:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

For production, use centralized logging:

```yaml
services:
  agent:
    logging:
      driver: "fluentd"
      options:
        fluentd-address: localhost:24224
        tag: agent.logs
```

### Metrics Collection

```bash
# Export container metrics
docker compose exec agent python -c "import psutil; print(psutil.cpu_percent())"

# Monitor logs in real-time
docker compose logs -f --tail=100
```

## Performance Tuning

### GPU Configuration

For NVIDIA GPUs:

```yaml
services:
  model-runner:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

Install NVIDIA Container Toolkit:

```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### Resource Limits

Set resource constraints:

```yaml
services:
  agent:
    deploy:
      resources:
        limits:
          cpus: "2"
          memory: 4G
        reservations:
          cpus: "1"
          memory: 2G
```

### Database Optimization

Tune PostgreSQL for performance:

```yaml
services:
  database:
    command:
      - postgres
      - -c
      - shared_buffers=256MB
      - -c
      - max_connections=100
      - -c
      - work_mem=4MB
```

## Backup & Recovery

### Database Backup

```bash
# Create backup
docker compose exec database pg_dump -U user database > backup.sql

# Restore backup
docker compose exec -T database psql -U user database < backup.sql
```

### Volume Backup

```bash
# Backup database volume
docker run --rm \
  -v compose-for-agents_db_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/db_backup.tar.gz -C /data .

# Restore volume
docker run --rm \
  -v compose-for-agents_db_data:/data \
  -v $(pwd):/backup \
  alpine sh -c "cd /data && tar xzf /backup/db_backup.tar.gz"
```

## Security Best Practices

### Network Isolation

```yaml
services:
  database:
    networks:
      - backend

  agent:
    networks:
      - backend
      - frontend

networks:
  backend:
    internal: true
  frontend:
```

### Least Privilege

Run containers as non-root:

```yaml
services:
  agent:
    user: "1000:1000"
```

### Secrets Rotation

```bash
# Update API key secret
echo "new-api-key" | docker secret create openai_api_key_v2 -
docker service update --secret-rm openai_api_key \
  --secret-add openai_api_key_v2 agent
```

## Troubleshooting

### Common Issues

**Issue**: Services not starting

```bash
# Check logs
docker compose logs

# Rebuild services
docker compose up --build --force-recreate
```

**Issue**: GPU not detected

```bash
# Verify GPU availability
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

**Issue**: Database connection errors

```bash
# Check database status
docker compose exec database pg_isready

# Restart database
docker compose restart database
```

### Debug Mode

Enable verbose logging:

```yaml
services:
  agent:
    environment:
      - LOG_LEVEL=DEBUG
      - PYTHONUNBUFFERED=1
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy Agent

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Build and deploy
        run: |
          docker compose build
          docker compose up -d

      - name: Run health checks
        run: |
          sleep 30
          docker compose ps
```

## Scaling & High Availability

### Horizontal Scaling

```yaml
services:
  agent:
    deploy:
      replicas: 3
```

### Load Balancing

Use a reverse proxy:

```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

## Maintenance

### Regular Updates

```bash
# Pull latest images
docker compose pull

# Restart with new images
docker compose up -d

# Clean old images
docker image prune -a
```

### Database Maintenance

```bash
# Vacuum database
docker compose exec database vacuumdb -U user -d database -z

# Analyze tables
docker compose exec database psql -U user -d database -c "ANALYZE;"
```

## Support & Resources

- **Docker Compose Docs**: https://docs.docker.com/compose/
- **Model Runner**: https://docs.docker.com/ai/model-runner/
- **MCP Gateway**: https://github.com/docker/mcp-gateway
- **Issue Tracker**: https://github.com/docker/compose-for-agents/issues
