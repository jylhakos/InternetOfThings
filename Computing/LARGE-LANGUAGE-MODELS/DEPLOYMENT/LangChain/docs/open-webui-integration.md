# Open WebUI integration

This guide shows how to integrate the LLM inference server with Open WebUI for a complete chat interface.

## Prerequisites

- Running LLM Inference Server
- Docker installed
- Open WebUI (https://github.com/open-webui/open-webui)

## Setup open WebUI

### 1. Run Open WebUI with Docker

```bash
# Run Open WebUI
docker run -d \
  --name open-webui \
  --restart always \
  -p 8080:8080 \
  -e OPENAI_API_BASE_URL="http://host.docker.internal:3000/v1" \
  -e OPENAI_API_KEY="your-jwt-token-here" \
  -v open-webui:/app/backend/data \
  ghcr.io/open-webui/open-webui:main
```

### 2. Configure the connection

1. Open http://localhost:8080 in your browser
2. Create an account or sign in
3. Go to Settings → Connections
4. Add new connection:
   - **Name**: LLM Inference Server
   - **API Base URL**: `http://host.docker.internal:3000/v1`
   - **API Key**: Your JWT token from login

### 3. Get JWT token

```bash
# Login to get JWT token
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}' | jq -r '.token'
```

### 4. Test connection

1. Go to the chat interface
2. Select the LLM Inference Server model
3. Start chatting!

## Docker Compose setup

Create a `docker-compose.openwebui.yml`:

```yaml
version: '3.8'

services:
  llm-inference-server:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - PORT=3000
      - JWT_SECRET=your-secret
      - HUGGINGFACE_API_KEY=your-key
    networks:
      - llm-network

  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "8080:8080"
    environment:
      - OPENAI_API_BASE_URL=http://llm-inference-server:3000/v1
      - OPENAI_API_KEY=demo-token
    volumes:
      - open-webui-data:/app/backend/data
    depends_on:
      - llm-inference-server
    networks:
      - llm-network

volumes:
  open-webui-data:

networks:
  llm-network:
    driver: bridge
```

Run with:
```bash
docker-compose -f docker-compose.openwebui.yml up -d
```

## Configuration

### Environment variables for Open WebUI

- `OPENAI_API_BASE_URL`: Your LLM server URL + `/v1`
- `OPENAI_API_KEY`: JWT token or API key
- `DEFAULT_MODELS`: Comma-separated model names
- `DEFAULT_USER_ROLE`: Default role for new users

### Model configuration

Add your models to Open WebUI:

```bash
# Get available models
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:3000/v1/models
```

## Troubleshooting

### Issues

1. **CORS Errors**: Ensure CORS is properly configured
2. **Authentication**: Check JWT token validity
3. **Network**: Verify container networking

### Solutions

```bash
# Check container logs
docker logs open-webui
docker logs llm-inference-server

# Test API directly
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:3000/v1/chat/completions \
  -d '{"messages":[{"role":"user","content":"Hello"}]}'
```

## Features

- ✅ Chat completions
- ✅ Model selection
- ✅ Conversation history
- ✅ User authentication
- ✅ Custom system prompts
- ⏳ File uploads (future)
- ⏳ Function calling (future)

## Security

- Use HTTPS in production
- Rotate JWT tokens regularly
- Implement proper user management
- Monitor API usage
