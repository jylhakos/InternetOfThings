# RESTful API & cURL test cases for Open WebUI

> **Main Documentation**: See [README.md](README.md) for complete project overview
> **Quick Setup**: For fast Open WebUI deployment, see [OPEN_WEBUI.md](OPEN_WEBUI.md)

## API Endpoint

Your Redis Queue FastAPI server provides the following endpoints for Open WebUI integration:

### Chat API
- **POST /chat** - Submit asynchronous chat requests
- **GET /task/{task_id}** - Check task status and retrieve results
- **GET /health** - System health check with detailed status
- **GET /models** - List available models with descriptions

### OpenAI compatible API (Required for Open WebUI)
- **GET /v1/models** - OpenAI-format model list
- **POST /v1/chat/completions** - OpenAI-compatible chat completions
- **POST /v1/completions** - OpenAI-compatible text completions

## API validation

**Endpoint**
-  POST /chat - Available at line 292 in main.py
- GET /task/{task_id} - Available at line 387 in main.py  
- GET /health - Available at line 178 in main.py
- GET /models - Available at line 197 in main.py
- GET /v1/models - Available at line 589 in main.py
- POST /v1/chat/completions - Available at line 627 in main.py

**CORS**
- CORS middleware properly configured for cross-origin requests
- Allows all origins, methods, and headers (adjust for production)

**Pydantic models**
- ChatRequest, TaskResponse, TaskResultResponse
- OpenAI-compatible models: OpenAIChatCompletionRequest, OpenAIChatCompletionResponse

## cURL test cases

### 1. Health Check
```bash
curl -s "http://localhost:8000/health"
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "Redis Queue LLM API",
  "version": "1.0.0",
  "redis": "healthy",
  "queue_size": 0,
  "timestamp": 1699123456.789
}
```

### 2. List models (Standard Format)
```bash
curl -s "http://localhost:8000/models"
```

**Expected Response:**
```json
{
  "models": [
    {
      "id": "llama3.2:1b",
      "name": "Llama 3.2 1B",
      "description": "Fast, lightweight model for quick responses",
      "parameters": "1B",
      "recommended_use": "Chat, Q&A, lightweight tasks"
    }
  ],
  "default_model": "llama3.2:1b",
  "total_models": 5
}
```

### 3. List models (OpenAI Format - required for Open WebUI)
```bash
curl -s -H "Authorization: Bearer dummy-key" "http://localhost:8000/v1/models"
```

**Expected Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "llama3.2:1b",
      "object": "model",
      "created": 1699123456,
      "owned_by": "ollama"
    }
  ]
}
```

### 4. Submit Asynchronous Chat Request
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is the capital of France?",
    "model": "llama3.2:1b",
    "temperature": 0.7,
    "max_tokens": 100
  }'
```

**Expected Response:**
```json
{
  "task_id": "uuid-string",
  "message": "Task submitted successfully",
  "status": "pending"
}
```

### 5. Check Task status
```bash
curl -s "http://localhost:8000/task/YOUR_TASK_ID_HERE"
```

**Expected Response (Pending):**
```json
{
  "task_id": "uuid-string",
  "status": "pending",
  "message": "Task is being processed"
}
```

**Expected Response (Completed):**
```json
{
  "task_id": "uuid-string", 
  "status": "completed",
  "result": {
    "response": "The capital of France is Paris.",
    "model": "llama3.2:1b",
    "timestamp": 1699123456.789,
    "processing_time": 2.34
  }
}
```

### 6. OpenAI Chat Completions (Primary endpoint for Open WebUI)
```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dummy-key" \
  -d '{
    "model": "llama3.2:1b",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Explain quantum computing in simple terms."}
    ],
    "temperature": 0.7,
    "max_tokens": 300
  }'
```

**Expected Response:**
```json
{
  "id": "chatcmpl-uuid",
  "object": "chat.completion",
  "created": 1699123456,
  "model": "llama3.2:1b",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Quantum computing is a revolutionary technology..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 150,
    "total_tokens": 175
  }
}
```

## Open WebUI

### Docker command for Open WebUI
```bash
# Remove any existing container
docker stop open-webui 2>/dev/null || true
docker rm open-webui 2>/dev/null || true

# Start Open WebUI with FastAPI backend
docker run -d \
  --name open-webui \
  -p 3001:8080 \
  -e OPENAI_API_BASE_URL="http://host.docker.internal:8000/v1" \
  -e OPENAI_API_KEY="dummy-key" \
  -v open-webui:/app/backend/data \
  --add-host=host.docker.internal:host-gateway \
  --restart unless-stopped \
  ghcr.io/open-webui/open-webui:main
```

### Configuration for Open WebUI
- **API Base URL:** `http://host.docker.internal:8000/v1`
- **API Key:** `dummy-key`
- **Models:** Will be automatically discovered from `/v1/models` endpoint
- **Web Interface:** `http://localhost:3001`

1. **Start services**
   ```bash
   python3 main.py      # FastAPI server
   python3 worker.py    # Redis Queue worker 
   node langchain_service.js  # LangChain.js service
   ```

2. **Test API**
   ```bash
   ./test_api_curl.sh
   ```

3. **Start Open WebUI**
   ```bash
   docker run -d --name open-webui -p 3001:8080 \
     -e OPENAI_API_BASE_URL="http://host.docker.internal:8000/v1" \
     -e OPENAI_API_KEY="dummy-key" \
     -v open-webui:/app/backend/data \
     --add-host=host.docker.internal:host-gateway \
     ghcr.io/open-webui/open-webui:main
   ```

4. **Access interface**
   - Open browser to `http://localhost:3001`

## Automated testing

### Run tests
```bash
# Test all endpoints with detailed output
python3 test_curl_api.py

# Quick validation of key endpoints
python3 test_curl_api.py quick

# Generate cURL examples
python3 test_curl_api.py examples

# Test Open WebUI integration specifically
python3 test_openwebui_integration.py

# Run the generated cURL test script
./test_api_curl.sh
```

### Docker-Based testing
```bash
# Start supporting services
docker-compose up -d redis ollama

# Test API endpoints
./test_api_curl.sh

# Start Open WebUI
docker-compose up -d open-webui
```

## Troubleshooting

### Issues

**1. CORS errors in Open WebUI**
- Already configured: CORS middleware allows all origins
- Check: FastAPI server is running on correct port (8000)

**2. Models not loading in Open WebUI**
- Test: `curl -H "Authorization: Bearer dummy-key" http://localhost:8000/v1/models`
- Verify: Response contains valid model list

**3. Chat Requests failing**
- Test: `curl -X POST http://localhost:8000/v1/chat/completions ...`
- Check: LangChain.js service and Redis Queue worker are running

**4. Docker Network issues**
- Linux alternative: Use `172.17.0.1` instead of `host.docker.internal`
- Verify: `docker exec open-webui ping host.docker.internal`

### Validation
```bash
# Check if API is ready for Open WebUI
curl -s http://localhost:8000/health | jq .status
curl -s -H "Authorization: Bearer dummy-key" http://localhost:8000/v1/models | jq .object

# Test OpenAI compatibility
python3 test_openwebui_integration.py quick

# Validate endpoint definitions
python3 validate_api.py
```