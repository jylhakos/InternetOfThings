# Setup

Get up and running with the LLM FastAPI + Celery + LangChain.js system in minutes!

## Docker

```bash
# Clone and enter the project directory
cd /path/to/project

# Start everything with one command
./start_dev.sh
```

The script will:
- ✅ Start all services (Redis, Ollama, LangChain.js, FastAPI, Celery)
- ✅ Download LLM models automatically
- ✅ Check service health
- ✅ Show you all the URLs
- ✅ Optionally run system tests

## Manual setup (Development)

### 1. Prerequisites
```bash
# Install Docker and Docker Compose
sudo apt update
sudo apt install docker.io docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in for group changes to take effect
```

### 2. Start services
```bash
# Start all services
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Verify setup
```bash
# Run comprehensive tests
./test_system.py

# Or test manually
curl http://localhost:8000/health
curl http://localhost:3000/health
```

## Using the API

### Simple Chat Request
```bash
# Submit a chat request
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, how are you?"}'

# Response: {"task_id": "abc123...", "status": "PENDING", "message": "Request submitted"}

# Check result (replace with actual task_id)
curl "http://localhost:8000/task/abc123..."
```

### Python client
```python
import requests
import time

# Submit request
response = requests.post("http://localhost:8000/chat", json={
    "prompt": "Explain Python in one sentence"
})
task_id = response.json()["task_id"]

# Wait for result
while True:
    result = requests.get(f"http://localhost:8000/task/{task_id}").json()
    if result["status"] == "SUCCESS":
        print("Response:", result["result"]["response"])
        break
    elif result["status"] == "FAILURE":
        print("Error:", result["error"])
        break
    time.sleep(2)
```

### JavaScript client
```javascript
async function chatWithLLM(prompt) {
  // Submit request
  const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({prompt})
  });
  
  const {task_id} = await response.json();
  
  // Poll for result
  while (true) {
    const result = await fetch(`http://localhost:8000/task/${task_id}`);
    const data = await result.json();
    
    if (data.status === 'SUCCESS') {
      return data.result.response;
    } else if (data.status === 'FAILURE') {
      throw new Error(data.error);
    }
    
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
}

// Usage
chatWithLLM("What is machine learning?")
  .then(response => console.log(response))
  .catch(error => console.error(error));
```

## Service URLs

Once everything is running:

| Service | URL | Description |
|---------|-----|-------------|
| **FastAPI** | http://localhost:8000 | Main API endpoints |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **LangChain** | http://localhost:3000 | Direct LLM service |
| **Flower** | http://localhost:5555 | Celery task monitoring |
| **Open WebUI** | http://localhost:3001 | Chat interface |
| **Ollama** | http://localhost:11434 | LLM model server |

## Testing different features

### 1. Chat
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello world!"}'
```

### 2. Code generation
```bash
curl -X POST "http://localhost:3000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a Python function",
    "template_type": "code",
    "template_variables": {
      "language": "Python",
      "request": "function to reverse a string"
    }
  }'
```

### 3. OpenAI compatible API
```bash
curl -X POST "http://localhost:3000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1",
    "messages": [{"role": "user", "content": "Hi there!"}],
    "temperature": 0.7
  }'
```

## Monitoring

### Check service Health
```bash
# Overall system health
curl http://localhost:8000/health

# Individual service health
curl http://localhost:3000/health

# Celery worker status
curl http://localhost:5555/api/workers
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f fastapi
docker-compose logs -f celery-worker
docker-compose logs -f langchain-service
```

### Monitor tasks
- **Flower UI**: http://localhost:5555
- **API endpoint**: `GET /task/{task_id}`

## Commands

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart fastapi

# Scale Celery workers
docker-compose up --scale celery-worker=4

# Stop everything
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v

# View running containers
docker-compose ps

# Execute command in container
docker-compose exec fastapi bash
```

## Troubleshooting

1. **Check logs**: `docker-compose logs [service_name]`
2. **Run tests**: `./test_system.py --verbose`
3. **Health checks**: Visit `/health` endpoints
4. **Documentation**: Check `/docs` for API documentation

### Services not start
```bash
# Check Docker status
docker info

# Check port conflicts
sudo netstat -tulpn | grep :8000

# Restart Docker
sudo systemctl restart docker
```

### Slow LLM responses
```bash
# Check if Ollama has downloaded models
docker-compose exec ollama ollama list

# Download model manually
docker-compose exec ollama ollama pull llama3.1
```

### Memory issues
```bash
# Check container memory usage
docker stats

# Limit container memory in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
```

### Connection errors
```bash
# Test internal connectivity
docker-compose exec fastapi curl http://langchain-service:3000/health
docker-compose exec fastapi curl http://redis:6379

# Check network
docker network ls
docker network inspect celery_default
```

## Next

1. **Customize Models**: Edit `.env` to use different Ollama models
2. **Add Authentication**: Implement API keys or JWT tokens
3. **Scale Production**: Use the deployment guide for production setup
4. **Custom Prompts**: Modify `prompt_templates.js` for your use case
5. **Web Interface**: Connect Open WebUI or build your own frontend

## Tips

- **First run**: Ollama may take 5-10 minutes to download models
- **Development**: Use `docker-compose logs -f` to watch real-time logs
- **Testing**: Run `./test_system.py` after any changes
- **Performance**: Increase Celery workers for better throughput
- **Models**: Try different models like `codellama`, `mistral`, or `llama3.1:13b`

