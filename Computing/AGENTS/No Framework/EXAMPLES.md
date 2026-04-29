# AI Agent usages

This document provides practical examples of how to use the AI Agent system.

## Setup and installation

```bash
# 1. Run the setup script
./setup.sh

# 2. Install and start Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama serve

# 3. Pull the LLM model (in another terminal)
ollama pull llama3.1:8b-instruct-q4_0

# 4. Start the AI Agent server
source venv/bin/activate
python src/index.py
```

## API tests

### 1. Health check

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-19T10:30:00",
  "services": {
    "llm": "healthy",
    "weather_api": "healthy"
  },
  "session_id": "abc123...",
  "agent_info": {
    "name": "AI Agent No Framework",
    "version": "1.0.0",
    "capabilities": ["chat", "weather", "greetings"]
  }
}
```

### 2. Chat completion - Greeting

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello, how are you today?"}
    ],
    "temperature": 0.7
  }'
```

**Response:**
```json
{
  "id": "chatcmpl-abc123...",
  "object": "chat.completion",
  "created": 1721376600,
  "model": "ai-agent-no-framework",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Hello! I'm doing great, thank you for asking. I'm here and ready to help you with any questions you might have, whether it's about weather information, general topics, or just having a friendly conversation. How can I assist you today?"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 6,
    "completion_tokens": 45,
    "total_tokens": 51
  },
  "metadata": {
    "agent_type": "greeting",
    "timestamp": "2025-07-19T10:30:00",
    "session_id": "abc123..."
  }
}
```

### 3. Weather query

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is the temperature in Tokyo?"}
    ]
  }'
```

**Response:**
```json
{
  "id": "chatcmpl-def456...",
  "object": "chat.completion",
  "created": 1721376700,
  "model": "ai-agent-no-framework",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "The current temperature in Tokyo, Japan is 28°C. Weather conditions: Partly cloudy"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 8,
    "completion_tokens": 15,
    "total_tokens": 23
  },
  "metadata": {
    "agent_type": "weather",
    "timestamp": "2025-07-19T10:31:40",
    "session_id": "abc123...",
    "city": "Tokyo"
  }
}
```

### 4. Use of LLM query

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Explain what artificial intelligence is in simple terms"}
    ],
    "temperature": 0.5
  }'
```

### 5. Use of weather endpoint

```bash
curl -X POST http://localhost:8000/v1/weather?city=London
```

**Response:**
```json
{
  "city": "London",
  "response": "The current temperature in London, United Kingdom is 18°C. Weather conditions: Overcast",
  "metadata": {
    "agent_type": "weather",
    "timestamp": "2025-07-19T10:32:00",
    "city": "London"
  }
}
```

## Python client examples

### Client script

```python
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"

def chat_with_agent(message, temperature=0.7):
    """Send a message to the AI agent."""
    url = f"{BASE_URL}/v1/chat/completions"
    payload = {
        "messages": [{"role": "user", "content": message}],
        "temperature": temperature
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.text}"

# Examples
print("Greeting:", chat_with_agent("Hello!"))
print("Weather:", chat_with_agent("What's the temperature in Paris?"))
print("General:", chat_with_agent("What is Python programming?"))
```

### Async client script

```python
import asyncio
import aiohttp
import json

async def async_chat_with_agent(session, message):
    """Async chat with the agent."""
    url = "http://localhost:8000/v1/chat/completions"
    payload = {
        "messages": [{"role": "user", "content": message}],
        "temperature": 0.7
    }
    
    async with session.post(url, json=payload) as response:
        if response.status == 200:
            data = await response.json()
            return data["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.status}"

async def main():
    async with aiohttp.ClientSession() as session:
        # Send multiple requests concurrently
        messages = [
            "Hello, how are you?",
            "What's the weather in Tokyo?",
            "Tell me about machine learning",
            "Good morning!"
        ]
        
        tasks = [async_chat_with_agent(session, msg) for msg in messages]
        responses = await asyncio.gather(*tasks)
        
        for msg, resp in zip(messages, responses):
            print(f"Q: {msg}")
            print(f"A: {resp[:100]}...")
            print("-" * 40)

# Run the async example
asyncio.run(main())
```

## JavaScript/Node.js examples

### Fetch

```javascript
async function chatWithAgent(message, temperature = 0.7) {
    const response = await fetch('http://localhost:8000/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            messages: [{ role: 'user', content: message }],
            temperature: temperature
        })
    });
    
    const data = await response.json();
    return data.choices[0].message.content;
}

// Usage
chatWithAgent('Hello!')
    .then(response => console.log('Response:', response))
    .catch(error => console.error('Error:', error));
```

### React component

```jsx
import React, { useState } from 'react';

function AIChat() {
    const [message, setMessage] = useState('');
    const [response, setResponse] = useState('');
    const [loading, setLoading] = useState(false);

    const sendMessage = async () => {
        setLoading(true);
        try {
            const res = await fetch('http://localhost:8000/v1/chat/completions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    messages: [{ role: 'user', content: message }]
                })
            });
            
            const data = await res.json();
            setResponse(data.choices[0].message.content);
        } catch (error) {
            setResponse('Error: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <input 
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Ask me anything..."
            />
            <button onClick={sendMessage} disabled={loading}>
                {loading ? 'Thinking...' : 'Send'}
            </button>
            <div>{response}</div>
        </div>
    );
}
```

## Testing and development

### Run component tests

```bash
# Test individual components without server
python test_components.py
```

### Run API tests

```bash
# Test API endpoints (server must be running)
./test_api.sh
```

### Development

```bash
# Start server with auto-reload
ENVIRONMENT=development python src/index.py
```

### Using Makefile commands

```bash
make help          # Show all available commands
make setup         # Full setup
make run           # Start server
make test          # Test components
make test-api      # Test API
make health        # Quick health check
make clean         # Clean up
```

## Customization

### Custom tool example

Add to `tools.py`:

```python
class CustomTool:
    async def process_custom_query(self, message: str) -> str:
        # Custom logic here
        return f"Processed: {message}"

# Add to ToolManager
async def process_message(self, message: str, temperature: float = 0.7):
    # Add custom condition
    if "custom:" in message.lower():
        custom_tool = CustomTool()
        response = await custom_tool.process_custom_query(message)
        return {
            "type": "custom",
            "content": response,
            "timestamp": datetime.now().isoformat()
        }
    # ... rest of existing logic
```

### Environment configuration

Create `.env` file:

```env
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=llama3.1:7b-instruct-q4_0
SERVER_HOST=127.0.0.1
SERVER_PORT=8080
ENVIRONMENT=production
```

## Monitoring and logging

### Health monitoring

```python
import requests
import time

def monitor_health():
    while True:
        try:
            response = requests.get("http://localhost:8000/health")
            if response.status_code == 200:
                data = response.json()
                print(f"Status: {data['status']} - LLM: {data['services']['llm']}")
            else:
                print(f"Health check failed: {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(30)  # Check every 30 seconds

monitor_health()
```

## Performance

1. **Concurrent requests**: The agent supports multiple concurrent requests
2. **Temperature settings**: Use lower temperatures (0.1-0.3) for factual queries, higher (0.7-1.0) for creative responses
3. **Model selection**: Use smaller models (7b) for faster responses, larger (8b) for better quality
4. **Caching**: Implement caching for weather data to reduce API calls
5. **Connection pooling**: Use session management for multiple requests

## Troubleshooting

### Issues

1. **Ollama connection**
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/tags
   
   # Restart Ollama
   ollama serve
   ```

2. **Model not found**
   ```bash
   # List available models
   ollama list
   
   # Pull the model
   ollama pull llama3.1:8b-instruct-q4_0
   ```

3. **Weather API**
   - Open-Meteo doesn't require API keys
   - Check internet connection
   - Try different city names

4. **Port already in use**
   ```bash
   # Change port in .env file
   SERVER_PORT=8001
   ```
