# Docker configuration for Open WebUI integration

This document explains how to set up Open WebUI in Docker to work with the no-framework AI agent.

## Overview

Open WebUI is a web-based interface for language models that can connect to any OpenAI-compatible API. Since our AI agent provides OpenAI-compatible endpoints, we can easily integrate them.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Open WebUI    │    │  AI Agent API   │    │     Ollama      │
│  (Docker)       │────│  (FastAPI)      │────│   (Local)       │
│  Port: 3000     │    │  Port: 8000     │    │  Port: 11434    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                │
                       ┌─────────────────┐
                       │  Weather API    │
                       │  (Open-Meteo)   │
                       └─────────────────┘
```

## Prerequisites

1. **Docker and Docker Compose** installed
2. **AI Agent running** on `http://localhost:8000`
3. **Ollama service running** on `http://localhost:11434`
4. **Internet connection** for weather API

## Setup

### Step 1: Create Docker Compose configuration

Create `docker-compose.yml` in your project root:

```yaml
version: '3.8'

services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui-aiagent
    ports:
      - "3000:8080"
    environment:
      # Connect to your AI Agent API instead of OpenAI
      - OPENAI_API_BASE_URL=http://host.docker.internal:8000/v1
      - OPENAI_API_KEY=not-needed
      - DEFAULT_MODELS=ai-agent-no-framework
      - WEBUI_NAME=AI Agent Interface
      - ENABLE_SIGNUP=false
      # Optional: Enable additional features
      - ENABLE_LOGIN_FORM=true
      - DEFAULT_USER_ROLE=admin
    volumes:
      - open-webui-data:/app/backend/data
    extra_hosts:
      # Allow container to access host services
      - "host.docker.internal:host-gateway"
    restart: unless-stopped
    networks:
      - ai-agent-network

networks:
  ai-agent-network:
    driver: bridge

volumes:
  open-webui-data:
```

### Step 2: Create environment configuration

Create `.env.docker`:

```env
# Open WebUI Configuration
WEBUI_PORT=3000
WEBUI_NAME=AI Agent No Framework Interface

# AI Agent API Configuration
AI_AGENT_URL=http://host.docker.internal:8000
AI_AGENT_API_KEY=not-needed

# Default model
DEFAULT_MODEL=ai-agent-no-framework

# Security settings
ENABLE_SIGNUP=false
DEFAULT_USER_ROLE=admin
WEBUI_SECRET_KEY=your-secret-key-here
```

### Step 3: Start Open WebUI

```bash
# Make sure your AI Agent is running first
python src/index.py

# Start Open WebUI
docker-compose up -d

# Check logs
docker-compose logs -f open-webui
```

### Step 4: Access Open WebUI

1. Open your browser and go to `http://localhost:3000`
2. Create an admin account (first user becomes admin)
3. The interface should automatically detect your AI agent models

## Advanced configuration

### Custom Open WebUI configuration

Create `open-webui-config.json`:

```json
{
  "ui": {
    "title": "AI Agent - No Framework",
    "default_locale": "en-US",
    "prompt_suggestions": [
      {
        "title": "Weather Query",
        "content": "What's the temperature in London?"
      },
      {
        "title": "Greeting",
        "content": "Hello, how are you today?"
      },
      {
        "title": "General Question",
        "content": "Explain artificial intelligence in simple terms"
      }
    ]
  },
  "models": {
    "default": "ai-agent-no-framework",
    "list": [
      {
        "id": "ai-agent-no-framework",
        "name": "AI Agent (No Framework)",
        "description": "Custom AI agent with weather capabilities"
      }
    ]
  }
}
```

### Docker Compose with configuration

Create `docker-compose.override.yml`:

```yaml
version: '3.8'

services:
  open-webui:
    volumes:
      - ./open-webui-config.json:/app/backend/open-webui-config.json:ro
    environment:
      - OPENAI_API_BASE_URL=http://host.docker.internal:8000/v1
      - OPENAI_API_KEY=sk-dummy-key
      - DEFAULT_MODELS=ai-agent-no-framework
      - WEBUI_NAME=AI Agent No Framework
      - ENABLE_SIGNUP=false
      - DEFAULT_USER_ROLE=admin
      - WEBUI_SECRET_KEY=your-secret-key-change-this
```

## Testing the integration

### 1. Health check

```bash
# Check AI Agent health
curl http://localhost:8000/health

# Check Open WebUI health
curl http://localhost:3000/health
```

### 2. Test queries via Open WebUI

1. **Weather Query**: "What's the temperature in Tokyo?"
2. **Greeting**: "Hello, how are you?"
3. **General Question**: "What is Python programming?"

### 3. API integration test

```bash
# Test the integration via Open WebUI's API
curl -X POST http://localhost:3000/api/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is the temperature in Paris?"}
    ],
    "model": "ai-agent-no-framework"
  }'
```

## Troubleshooting

### Issues

1. **Connection refused**
   - Ensure AI Agent is running on port 8000
   - Check if Ollama is running on port 11434
   - Verify Docker can access host services

2. **Model not found**
   - Check if `ai-agent-no-framework` model is listed in `/v1/models`
   - Restart Open WebUI container

3. **Authentication issues**
   - Set `OPENAI_API_KEY=sk-dummy-key` (any value works)
   - Disable authentication if needed

### Debug

```bash
# Check container logs
docker-compose logs open-webui

# Access container shell
docker exec -it open-webui-aiagent /bin/bash

# Test network connectivity from container
docker exec -it open-webui-aiagent curl http://host.docker.internal:8000/health

# Restart services
docker-compose restart
```

## Production

### Security

1. **Enable authentication**
   ```yaml
   environment:
     - ENABLE_SIGNUP=false
     - ENABLE_LOGIN_FORM=true
     - WEBUI_SECRET_KEY=your-secure-secret-key
   ```

2. **Use reverse proxy** (Nginx)
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:3000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. **SSL/TLS configuration**
   ```yaml
   labels:
     - "traefik.enable=true"
     - "traefik.http.routers.open-webui.rule=Host(`your-domain.com`)"
     - "traefik.http.routers.open-webui.tls.certresolver=letsencrypt"
   ```

### Performance

1. **Resource limits**
   ```yaml
   services:
     open-webui:
       deploy:
         resources:
           limits:
             memory: 1G
             cpus: '0.5'
   ```

2. **Persistent data**
   ```yaml
   volumes:
     - ./open-webui-data:/app/backend/data
   ```

## Maintenance

### Backup and restore

```bash
# Backup Open WebUI data
docker exec open-webui-aiagent tar czf - /app/backend/data > backup.tar.gz

# Restore data
docker exec -i open-webui-aiagent tar xzf - -C / < backup.tar.gz
```

### Updates

```bash
# Update Open WebUI
docker-compose pull
docker-compose up -d

# View changelog
docker exec open-webui-aiagent cat /app/CHANGELOG.md
```

## Custom features

### Weather widget

You can add custom JavaScript to enhance weather queries:

```html
<!-- Add to Open WebUI custom HTML -->
<script>
function addWeatherWidget() {
    const weatherButton = document.createElement('button');
    weatherButton.textContent = '🌤️ Weather';
    weatherButton.onclick = () => {
        const city = prompt('Enter city name:');
        if (city) {
            sendMessage(`What's the temperature in ${city}?`);
        }
    };
    document.querySelector('.chat-input').appendChild(weatherButton);
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', addWeatherWidget);
</script>
```