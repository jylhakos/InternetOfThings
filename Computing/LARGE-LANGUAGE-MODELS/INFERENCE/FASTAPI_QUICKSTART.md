# FastAPI Quick Start

This guide helps you get started with the FastAPI inference server quickly.

## Why FastAPI?

FastAPI is a high-performance web framework for building APIs with Python 3.7+ based on standard Python type hints.

**Key Advantages:**
- **Fast**: 2-3x faster than Flask, comparable to NodeJS and Go
- **Async Native**: Built-in async/await support for concurrent requests
- **Auto Docs**: Automatic interactive API documentation (Swagger UI)
- **Type Safety**: Pydantic models provide runtime validation
- **Production Ready**: Used by vLLM, TGI, and major ML frameworks

## Quick Setup

### 1. Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install FastAPI and uvicorn (if not already installed)
pip install fastapi uvicorn[standard] pydantic
```

### 2. Start the Server

```bash
python sources/inference_server_fastapi.py
```

Or with uvicorn directly:

```bash
uvicorn sources.inference_server_fastapi:app --reload --port 8000
```

### 3. Access Interactive Documentation

Open your browser and visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Interactive Testing

The Swagger UI at `/docs` provides a fully interactive interface where you can:

1. **See all endpoints** with descriptions
2. **Try out requests** directly in your browser
3. **View request/response schemas** with examples
4. **Test authentication** (if configured)
5. **Download OpenAPI spec** for client generation

### Example: Using Swagger UI

1. Visit http://localhost:8000/docs
2. Click on `POST /api/v1/inference`
3. Click "Try it out"
4. Modify the request body:
   ```json
   {
     "prompt": "Explain async programming",
     "max_tokens": 100,
     "temperature": 0.7,
     "top_p": 0.9
   }
   ```
5. Click "Execute"
6. See the response with all metrics!

## Testing with Python Client

```bash
# Run the FastAPI client examples
python sources/client_example_fastapi.py
```

This will run through all examples:
- Health checks
- Single inference
- Batch inference (concurrent!)
- Streaming inference
- Model listing
- Metrics monitoring
- Load testing
- Error handling demonstration

## Testing with cURL

### Health Check
```bash
curl http://localhost:8000/health
```

### Single Inference
```bash
curl -X POST http://localhost:8000/api/v1/inference \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is FastAPI?",
    "max_tokens": 100,
    "temperature": 0.7
  }'
```

### Batch Inference (Concurrent!)
```bash
curl -X POST http://localhost:8000/api/v1/batch_inference \
  -H "Content-Type: application/json" \
  -d '{
    "prompts": [
      "What is async?",
      "Explain FastAPI",
      "What is Pydantic?"
    ],
    "max_tokens": 50
  }'
```

### Streaming Inference
```bash
curl -X POST http://localhost:8000/api/v1/stream_inference \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Count to 10",
    "max_tokens": 20
  }'
```

### Get Metrics
```bash
curl http://localhost:8000/metrics
```

### List Models
```bash
curl http://localhost:8000/api/v1/models
```

## Key Differences from Flask

### 1. Async/Await Support

**Flask (synchronous):**
```python
@app.route('/inference', methods=['POST'])
def inference():
    result = model.generate(prompt)  # Blocks thread
    return result
```

**FastAPI (asynchronous):**
```python
@app.post('/api/v1/inference')
async def inference(request: InferenceRequest):
    result = await model.generate(request.prompt)  # Non-blocking
    return result
```

### 2. Request Validation

**Flask:**
```python
# Manual validation
data = request.get_json()
if not data or 'prompt' not in data:
    return jsonify({"error": "Missing prompt"}), 400
prompt = data['prompt']
```

**FastAPI:**
```python
# Automatic validation with Pydantic
async def inference(request: InferenceRequest):
    # 'request.prompt' is guaranteed to exist and be valid
    # FastAPI automatically returns 422 for invalid requests
```

### 3. API Documentation

**Flask:** Manual - you must write documentation separately

**FastAPI:** Automatic - generated from code and type hints

## Performance Tips

### 1. Use Async Everywhere
```python
# Good
async def generate(prompt: str):
    result = await model.generate(prompt)
    return result

# Avoid blocking calls in async functions
async def bad_example():
    time.sleep(1)  # WRONG - blocks event loop
    await asyncio.sleep(1)  # CORRECT
```

### 2. Concurrent Processing
```python
# Process multiple prompts concurrently
async def batch_generate(prompts: List[str]):
    tasks = [model.generate(p) for p in prompts]
    results = await asyncio.gather(*tasks)  # All run concurrently!
    return results
```

### 3. Use Connection Pooling
For production, use proper database connection pools and HTTP client sessions.

## Production Deployment

### With Uvicorn (Development)
```bash
uvicorn sources.inference_server_fastapi:app --reload --port 8000
```

### With Uvicorn (Production)
```bash
uvicorn sources.inference_server_fastapi:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level info
```

### With Gunicorn + Uvicorn Workers (Recommended)
```bash
gunicorn sources.inference_server_fastapi:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --log-level info
```

### With Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY sources/ ./sources/

CMD ["uvicorn", "sources.inference_server_fastapi:app", \
     "--host", "0.0.0.0", "--port", "8000"]
```

## Monitoring

### Check Server Metrics
```bash
# Get performance statistics
curl http://localhost:8000/metrics

# Sample response:
{
  "total_requests": 150,
  "successful_requests": 148,
  "failed_requests": 2,
  "average_latency_ms": 125.5,
  "p95_latency_ms": 245.0,
  "success_rate": 98.67
}
```

### Health Checks
```bash
# Simple health check
curl http://localhost:8000/health

# Use in Kubernetes liveness/readiness probes
# or load balancer health checks
```

## Common Issues

### 1. Import Error: No module named 'fastapi'
```bash
pip install fastapi uvicorn[standard]
```

### 2. Port Already in Use
```bash
# Change port
uvicorn sources.inference_server_fastapi:app --port 8001
```

### 3. Async Function Not Awaited
Make sure to use `await` with async functions:
```python
# Wrong
result = model.generate(prompt)

# Correct
result = await model.generate(prompt)
```

## Next Steps

1. Explore the interactive docs at http://localhost:8000/docs
2. Run `python sources/client_example_fastapi.py` to see all examples
3. Compare with Flask version (port 5000) to see performance difference
4. Try load testing with Apache Bench or Locust
5. Read FastAPI docs: https://fastapi.tiangolo.com/

## Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Pydantic Documentation**: https://docs.pydantic.dev/
- **Uvicorn Documentation**: https://www.uvicorn.org/
- **Async Programming**: https://docs.python.org/3/library/asyncio.html

## Flask vs FastAPI Summary

| Feature | Flask | FastAPI |
|---------|-------|---------|
| **Port** | 5000 | 8000 |
| **Performance** | Good | Excellent |
| **Async** | Limited | Native |
| **Validation** | Manual | Automatic |
| **Docs** | Manual | Automatic |
| **Learning** | Easy | Moderate |
| **Production** | Yes | Yes (Recommended) |

**Bottom Line:** Use Flask for learning, FastAPI for production!
