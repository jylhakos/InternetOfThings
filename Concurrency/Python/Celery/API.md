# API usage

This document provides examples of how to interact with the LLM processing API.

## URL
- Development: `http://localhost:8000`
- Production: Update with your deployed URL

## Authentication
Currently, no authentication is required. In production, implement appropriate authentication mechanisms.

## Endpoints

### 1. Submit Chat Request

Submit a prompt for LLM processing.

**Endpoint:** `POST /chat`

**Request Body:**
```json
{
  "prompt": "Explain the concept of machine learning",
  "model": "llama3.1",
  "temperature": 0.7,
  "max_tokens": 1000
}
```

**Response:**
```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "PENDING",
  "message": "Request submitted for processing"
}
```

**cURL example:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is Python programming?",
    "temperature": 0.7,
    "max_tokens": 500
  }'
```

### 2. Check Task Status

Check the status and get results of a submitted task.

**Endpoint:** `GET /task/{task_id}`

**Response (Pending):**
```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "PENDING",
  "meta": {
    "message": "Task is waiting to be processed"
  }
}
```

**Response (Processing):**
```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "PROCESSING",
  "meta": {
    "status": "Sending request to LangChain service..."
  }
}
```

**Response (Success):**
```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "SUCCESS",
  "result": {
    "success": true,
    "response": "Python is a high-level programming language...",
    "model": "llama3.1",
    "tokens_used": 245,
    "processing_time": 3.2,
    "timestamp": "2025-07-28T10:30:00Z"
  }
}
```

**cURL Example:**
```bash
curl "http://localhost:8000/task/abc123-def456-ghi789"
```

### 3. Health Check

Check the health of the API and its services.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-28T10:30:00Z",
  "services": {
    "celery": "healthy",
    "langchain_service": "healthy",
    "redis": "healthy"
  }
}
```

**cURL example:**
```bash
curl "http://localhost:8000/health"
```

### 4. Get available LLM models

Get a list of available LLM models.

**Endpoint:** `GET /models`

**Response:**
```json
{
  "models": [
    {
      "name": "llama3.1",
      "description": "Llama 3.1 - General purpose LLM",
      "size": "4.7GB"
    },
    {
      "name": "codellama",
      "description": "Code Llama - Specialized for code generation",
      "size": "3.8GB"
    }
  ],
  "default_model": "llama3.1",
  "status": "success"
}
```

**cURL example:**
```bash
curl "http://localhost:8000/models"
```

## LangChain.js service examples

The LangChain.js service runs on port 3000 and provides direct LLM interaction.

### Generate Response

**Endpoint:** `POST http://localhost:3000/generate`

**Request Body:**
```json
{
  "prompt": "Write a Python function to calculate fibonacci numbers",
  "model": "codellama",
  "temperature": 0.3,
  "max_tokens": 500,
  "template_type": "code",
  "template_variables": {
    "language": "Python",
    "request": "fibonacci function"
  }
}
```

**Response:**
```json
{
  "success": true,
  "response": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
  "model": "codellama",
  "tokens_used": 125,
  "processing_time": 2.1,
  "timestamp": "2025-07-28T10:30:00Z",
  "prompt_template": "code"
}
```

### OpenAI-Compatible Endpoint (for Open WebUI)

**Endpoint:** `POST http://localhost:3000/v1/chat/completions`

**Request Body:**
```json
{
  "model": "llama3.1",
  "messages": [
    {
      "role": "user",
      "content": "Hello, how are you?"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 100
}
```

**Response:**
```json
{
  "id": "chatcmpl-1690523400000",
  "object": "chat.completion",
  "created": 1690523400,
  "model": "llama3.1",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! I'm doing well, thank you for asking. I'm here to help you with any questions or tasks you might have. How can I assist you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 12,
    "completion_tokens": 28,
    "total_tokens": 40
  }
}
```

## Python client example

Here's a simple Python client to interact with the API:

```python
import requests
import time
import json

class LLMClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def submit_chat(self, prompt, model=None, temperature=0.7, max_tokens=1000):
        """Submit a chat request"""
        url = f"{self.base_url}/chat"
        data = {
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        if model:
            data["model"] = model
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()
    
    def get_task_status(self, task_id):
        """Get task status and result"""
        url = f"{self.base_url}/task/{task_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def wait_for_result(self, task_id, timeout=300, poll_interval=2):
        """Wait for task completion and return result"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            result = self.get_task_status(task_id)
            
            if result["status"] == "SUCCESS":
                return result["result"]
            elif result["status"] == "FAILURE":
                raise Exception(f"Task failed: {result.get('error')}")
            
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Task {task_id} did not complete within {timeout} seconds")
    
    def chat(self, prompt, **kwargs):
        """Submit chat request and wait for result"""
        response = self.submit_chat(prompt, **kwargs)
        task_id = response["task_id"]
        return self.wait_for_result(task_id)

# Usage example
if __name__ == "__main__":
    client = LLMClient()
    
    try:
        result = client.chat("Explain quantum computing in simple terms")
        print("Response:", result["response"])
        print("Tokens used:", result["tokens_used"])
        print("Processing time:", result["processing_time"])
    except Exception as e:
        print(f"Error: {e}")
```

## JavaScript client example

```javascript
class LLMClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async submitChat(prompt, options = {}) {
    const response = await fetch(`${this.baseUrl}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt,
        ...options
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  }

  async getTaskStatus(taskId) {
    const response = await fetch(`${this.baseUrl}/task/${taskId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  }

  async waitForResult(taskId, timeout = 300000, pollInterval = 2000) {
    const startTime = Date.now();
    
    while (Date.now() - startTime < timeout) {
      const result = await this.getTaskStatus(taskId);
      
      if (result.status === 'SUCCESS') {
        return result.result;
      } else if (result.status === 'FAILURE') {
        throw new Error(`Task failed: ${result.error}`);
      }
      
      await new Promise(resolve => setTimeout(resolve, pollInterval));
    }
    
    throw new Error(`Task ${taskId} did not complete within ${timeout}ms`);
  }

  async chat(prompt, options = {}) {
    const response = await this.submitChat(prompt, options);
    return await this.waitForResult(response.task_id);
  }
}

// Usage example
(async () => {
  const client = new LLMClient();
  
  try {
    const result = await client.chat('What is machine learning?');
    console.log('Response:', result.response);
    console.log('Tokens used:', result.tokens_used);
  } catch (error) {
    console.error('Error:', error.message);
  }
})();
```

## Testing with different Prompt Templates

```bash
# Code generation
curl -X POST "http://localhost:3000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a REST API endpoint",
    "template_type": "code",
    "template_variables": {
      "language": "Python",
      "request": "REST API endpoint using FastAPI"
    }
  }'

# Explanation
curl -X POST "http://localhost:3000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Docker containers",
    "template_type": "explanation",
    "template_variables": {
      "topic": "Docker containers",
      "level": "intermediate"
    }
  }'

# Analysis
curl -X POST "http://localhost:3000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Performance metrics data",
    "template_type": "analysis",
    "template_variables": {
      "content": "CPU: 80%, Memory: 60%, Disk: 45%",
      "type": "system performance"
    }
  }'
```

## Errors

The API returns appropriate HTTP status codes and error messages:

- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Task not found
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service dependencies unavailable

Example error response:
```json
{
  "detail": "Prompt is required",
  "error": "Validation error"
}
```
