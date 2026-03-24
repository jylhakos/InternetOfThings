# API documentation

## Overview

The LLM inference server provides OpenAI compatible APIs for chat completions using Meta Llama-3.1 and other language models through LangChain.js integration.

## Base URL

```
https://your-domain.com/
```

## Authentication

All API endpoints (except health checks) require authentication using JWT tokens or API keys.

### JWT token authentication

```bash
Authorization: Bearer <jwt_token>
```

### API key authentication

```bash
X-API-Key: <api_key>
```

## Endpoints

### Authentication

#### POST /api/auth/register

Register a new user account.

**Request body:**
```json
{
  "username": "string (3-50 chars)",
  "email": "string (valid email)",
  "password": "string (min 6 chars)"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "token": "jwt_token_here",
  "expiresIn": "24h",
  "user": {
    "id": "user_id",
    "username": "username",
    "email": "email",
    "role": "user"
  }
}
```

#### POST /api/auth/login

Login with existing credentials.

**Request body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "token": "jwt_token_here",
  "expiresIn": "24h",
  "user": {
    "id": "user_id",
    "username": "username",
    "role": "user"
  }
}
```

### Chat completions

#### POST /v1/chat/completions

OpenAI-compatible chat completions endpoint.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request body:**
```json
{
  "messages": [
    {
      "role": "system|user|assistant",
      "content": "string"
    }
  ],
  "model": "meta-llama/Llama-3.1-8B-Instruct",
  "temperature": 0.7,
  "max_tokens": 4096,
  "stream": false
}
```

**Response:**
```json
{
  "id": "chatcmpl-unique-id",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "meta-llama/Llama-3.1-8B-Instruct",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Response from the model"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

#### POST /api/chat/message

Simplified chat endpoint.

**Request body:**
```json
{
  "message": "Your question here"
}
```

**Response:**
```json
{
  "message": "Model response",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  },
  "model": "meta-llama/Llama-3.1-8B-Instruct"
}
```

#### GET /api/chat/history

Get conversation history for the authenticated user.

**Response:**
```json
{
  "history": [
    {
      "role": "user",
      "content": "Hello"
    },
    {
      "role": "assistant", 
      "content": "Hi there!"
    }
  ]
}
```

#### DELETE /api/chat/history

Clear conversation history for the authenticated user.

**Response:**
```json
{
  "message": "Chat history cleared successfully"
}
```

### Models

#### GET /v1/models

List available models (OpenAI compatible).

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "meta-llama/Llama-3.1-8B-Instruct",
      "object": "model",
      "created": 1234567890,
      "owned_by": "local"
    }
  ]
}
```

#### GET /api/chat/model

Get detailed model information.

**Response:**
```json
{
  "model": "meta-llama/Llama-3.1-8B-Instruct",
  "maxTokens": 4096,
  "temperature": 0.7,
  "quantized": true,
  "memoryOptimized": true,
  "supportedFeatures": [
    "chat_completion",
    "conversation_history",
    "message_trimming",
    "multi_language"
  ]
}
```

### Health Checks

#### GET /api/health

Basic health check (no authentication required).

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "uptime": 3600,
  "environment": "production",
  "version": "1.0.0"
}
```

#### GET /api/health/detailed

Detailed health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "checks": {
    "database": {
      "status": "healthy",
      "message": "In-memory storage operational"
    },
    "llm_service": {
      "status": "healthy", 
      "message": "LLM service initialized and ready"
    }
  },
  "metrics": {
    "uptime_seconds": 3600,
    "memory_usage_mb": 512,
    "memory_total_mb": 1024
  }
}
```

## Error responses

All endpoints return error responses in the following format:

```json
{
  "error": {
    "message": "Error description",
    "type": "error_type",
    "details": ["Additional error details"]
  }
}
```

### Error types

- `authentication_error` (401) - Invalid or missing authentication
- `authorization_error` (403) - Insufficient permissions
- `validation_error` (400) - Invalid request data
- `rate_limit_exceeded` (429) - Too many requests
- `internal_error` (500) - Server error
- `not_found_error` (404) - Resource not found

## Rate limits

- **Authentication endpoints**: 5 requests per 15 minutes per IP
- **Chat endpoints**: 50 requests per hour per user
- **General API**: 100 requests per 15 minutes per IP

Rate limit headers are included in responses:
```
Retry-After: 60
```

## Usage

### cURL

```bash
# Register user
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# Login
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'

# Chat completion
curl -X POST http://localhost:3000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}],
    "model": "meta-llama/Llama-3.1-8B-Instruct"
  }'
```

### JavaScript/TypeScript

```typescript
// Login and get token
const loginResponse = await fetch('http://localhost:3000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'testuser',
    password: 'password123'
  })
});
const { token } = await loginResponse.json();

// Make chat completion request
const chatResponse = await fetch('http://localhost:3000/v1/chat/completions', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    messages: [{ role: 'user', content: 'Hello!' }],
    model: 'meta-llama/Llama-3.1-8B-Instruct'
  })
});
const completion = await chatResponse.json();
```

### Python

```python
import requests

# Login
login_response = requests.post('http://localhost:3000/api/auth/login', json={
    'username': 'testuser',
    'password': 'password123'
})
token = login_response.json()['token']

# Chat completion
chat_response = requests.post('http://localhost:3000/v1/chat/completions', 
    headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    },
    json={
        'messages': [{'role': 'user', 'content': 'Hello!'}],
        'model': 'meta-llama/Llama-3.1-8B-Instruct'
    }
)
completion = chat_response.json()
print(completion['choices'][0]['message']['content'])
```

## Integration with OpenAI SDK

The server is compatible with OpenAI SDKs:

```typescript
import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: 'your-jwt-token',
  baseURL: 'http://localhost:3000/v1',
});

const completion = await openai.chat.completions.create({
  messages: [{ role: 'user', content: 'Hello!' }],
  model: 'meta-llama/Llama-3.1-8B-Instruct',
});
```

## WebSocket (Option)

Streaming chat completions will be supported via WebSocket connections:

```typescript
// Future implementation
const ws = new WebSocket('ws://localhost:3000/v1/chat/stream');
ws.send(JSON.stringify({
  messages: [{ role: 'user', content: 'Hello!' }],
  stream: true
}));
```
