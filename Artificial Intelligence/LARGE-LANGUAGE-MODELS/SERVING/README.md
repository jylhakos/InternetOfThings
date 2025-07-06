# Ollama FastAPI Server with Prompt Templates

A FastAPI server that provides HTTP JSON API endpoints to interact with Ollama LLM models using OpenAI compatible API calls with advanced prompt template support.

## Features

- 🚀 FastAPI-based HTTP server with JSON request/response
- 🦙 Integration with Ollama inference server
- 🔗 OpenAI-compatible API for seamless integration
- 🌐 CORS support for browser-based requests
- 📝 Interactive web client for testing
- ✅ Health checks and model listing
- 🎯 **Prompt Templates with System Prompts**
- 🎨 Predefined templates for different use cases
- 🔧 Custom system prompt support
- 📚 Automatic API documentation with Swagger UI

## Prompt Template System

The server includes a prompt template system that allows you to:

1. **Use predefined templates** for common scenarios (coding, teaching, creative writing, etc.)
2. **Create custom system prompts** for specific use cases
3. **Structure conversations** with appropriate context and instructions

### Available Templates

- **general**: General purpose assistant for any topic
- **code_helper**: Specialized assistant for programming and software development
- **technical_writer**: Assistant for technical explanations and documentation
- **data_analyst**: Specialized assistant for data analysis and statistics
- **creative_writer**: Assistant for creative writing and storytelling
- **teacher**: Educational assistant for learning and teaching
- **business_advisor**: Assistant for business strategy and management advice
- **researcher**: Assistant for research and fact-finding

## Architecture

```
Browser/Client  -->  FastAPI Server  -->  Ollama Server  -->  LLM Model
    (HTTP/JSON)      (Python/FastAPI)     (OpenAI API)      (llama3, etc.)
                           |
                    Prompt Templates
                    System Prompts
```
Download and install the LLM model (e.g., llama3:latest).

Connect to the Ollama server (usually running locally on http://localhost:11434).

You can start Ollama from the command line, and pull the required model (e.g., llama3:latest). 

Create a prompt template

To integrate a prompt template with system instructions into a FastAPI application interacting with an Ollama server using an OpenAI compatible API, you can use LangChain's prompt template capabilities along with the requests library to send properly formatted requests to Ollama.

OpenAI API

Ollama supports an OpenAI compatible API, which means you can use libraries designed for OpenAI to interact with your local Ollama server.

You can initialize the OpenAI client to point to the local Ollama server's URL (http://localhost:11434/v1) and use it to interact with your Llama 3 model.

```

  from openai import OpenAI

  client = OpenAI(
      base_url='http://localhost:11434/v1',
      api_key='ollama',  # required, but not used by Ollama
  )

  response = client.chat.completions.create(
      model="llama3",
      messages=[
          {"role": "system", "content": "You are a helpful assistant."},
          {"role": "user", "content": "Who won the world series in 2020?"}
      ]
  )
  print(response.choices[0].message.content)

```
Install libraries

```bash

  pip install fastapi requests uvicorn

```
fastapi:


For building the web API.

requests:

For making HTTP requests to the Ollama server.

uvicorn:

ASGI server is a program that implements the ASGI (Asynchronous Server Gateway Interface) specification, allowing it to run asynchronous Python web frameworks like FastAPI.

Uvicorn is commonly used ASGI server for FastAPI.

## Prerequisites

1. **Ollama Server**: Install and run Ollama

   ```bash

   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Start Ollama server
   ollama serve
   
   # Pull a model (e.g., Llama 3)
   ollama pull llama3

   ```

2. **Python 3.8+**: Make sure Python is installed

## Installation

1. Clone or download this project

2. Install Python dependencies:

   ```bash

   pip install -r requirements.txt

   ```

## Quick Start

### Option 1: Use the startup script

```bash

  chmod +x run_server.sh
  ./run_server.sh

```

### Option 2: Manual startup

```bash

  # Install dependencies
  pip install -r requirements.txt

  # Start the FastAPI server
  python main.py

```

The server will start on `http://localhost:8000`

## API endpoints

### Health check

```http

  GET /health

  ```
  Response:

  ```json

  {
    "status": "healthy",
    "message": "FastAPI server and Ollama are running",
    "ollama_connected": true
  }

```

### List models

```http

  GET /models

```
Response:

```json

  {
    "models": ["llama3", "codellama", "mistral"],
    "count": 3
  }

```

### Chat

```http

  POST /chat
  Content-Type: application/json

  {
    "question": "What is Python language?",
    "model": "llama3",
    "max_tokens": 500,
    "temperature": 0.7
  }

```
Response:

```json

  {
    "answer": "Python is a programming language.",
    "model": "llama3",
    "usage": {
      "prompt_tokens": 10,
      "completion_tokens": 45,
      "total_tokens": 55
    }
  }

```

### Conversation chat

```http

  POST /chat/messages
  Content-Type: application/json

  {
    "messages": [
      {"role": "system", "content": "You are a helpful assistant"},
      {"role": "user", "content": "What is FastAPI?"}
    ],
    "model": "llama3",
    "max_tokens": 500,
    "temperature": 0.7
  }

```

### Template Management

#### List Templates

```http
GET /templates
```
Response:
```json
{
  "templates": {
    "general": {"name": "general", "description": "General purpose assistant for any topic"},
    "code_helper": {"name": "code_helper", "description": "Specialized assistant for programming"},
    ...
  },
  "count": 8
}
```

#### Get Template Details
```http
GET /templates/{template_name}
```
Response:
```json
{
  "name": "code_helper",
  "description": "Specialized assistant for programming and software development",
  "system_prompt": "You are an expert programmer and coding assistant...",
  "user_template": "Programming question: {question}"
}
```

### Chat Endpoints

#### Simple Chat (with optional system prompt)
```http
POST /chat
Content-Type: application/json

{
  "question": "What is Python?",
  "model": "llama3",
  "system_prompt": "You are a helpful programming instructor",  // optional
  "template_name": "code_helper",  // optional, alternative to system_prompt
  "max_tokens": 500,
  "temperature": 0.7
}
```

#### Templated Chat
```http
POST /chat/template
Content-Type: application/json

{
  "question": "Explain machine learning",
  "template_name": "teacher",
  "model": "llama3",
  "template_variables": {},  // optional variables for template
  "max_tokens": 500,
  "temperature": 0.7
}
```

#### Response Format
```json
{
  "answer": "Python is a high-level programming language...",
  "model": "llama3",
  "system_prompt_used": "You are an expert programmer...",  // if used
  "template_used": "code_helper",  // if template was used
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 150,
    "total_tokens": 175
  }
}
```

## Usage Examples

### 1. Simple Chat (No Template)
```python
import requests

response = requests.post("http://localhost:8000/chat", json={
    "question": "What is machine learning?",
    "model": "llama3"
})
```

### 2. Using Custom System Prompt
```python
response = requests.post("http://localhost:8000/chat", json={
    "question": "Explain quantum computing",
    "system_prompt": "You are a physics professor. Use simple analogies.",
    "model": "llama3"
})
```

### 3. Using Predefined Template
```python
response = requests.post("http://localhost:8000/chat/template", json={
    "question": "How do I create a REST API?",
    "template_name": "code_helper",
    "model": "llama3"
})
```

### 4. Using Template via Chat Endpoint
```python
response = requests.post("http://localhost:8000/chat", json={
    "question": "Teach me about neural networks",
    "template_name": "teacher",
    "model": "llama3"
})
```
## Testing

### Web client

Open `client.html` in your browser or serve it with a web server:

```bash

  # Simple Python web server
  python -m http.server 8080
  # Then open http://localhost:8080/client.html

```
### Command line testing

```bash

  python test_client.py

```

### Manual API testing

```bash

  # Health check
  curl http://localhost:8000/health

  # List models
  curl http://localhost:8000/models

  # Ask a question
  curl -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"question": "What is machine learning?", "model": "llama3"}'

```

## Configuration

Edit `config.py` to customize:

- Ollama server URL
- Default model settings
- Available models list
- Server host/port

## API documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Supported LLM models

The server supports any model available in your Ollama installation:

- `llama3` (recommended)
- `llama3:8b`, `llama3:70b`
- `codellama`
- `mistral`
- `neural-chat`

## Error handling

The server includes comprehensive error handling:

- Connection errors to Ollama
- Invalid model names
- Malformed requests
- Rate limiting (if configured)

## Development

### Project
```

  ├── main.py              # FastAPI application
  ├── config.py            # Configuration settings
  ├── requirements.txt     # Python dependencies
  ├── client.html          # Web testing client
  ├── test_client.py       # Command-line test client
  ├── run_server.sh        # Startup script
  └── README.md            # This file

```

### Adding features
1. Add new endpoints in `main.py`
2. Update the Pydantic models for request/response validation
3. Test with the provided clients
4. Update documentation

## Troubleshooting

### Common Issues

1. **"Cannot connect to Ollama"**
   - Make sure Ollama is running: `ollama serve`
   - Check if Ollama is on port 11434: `curl http://localhost:11434/api/tags`

2. **"Model not found"**
   - List available models: `ollama list`
   - Pull the model: `ollama pull llama3`

3. **CORS errors in browser**
   - The server has CORS enabled for all origins
   - For production, update the CORS settings in `main.py`

4. **Import errors**
   - Install dependencies: `pip install -r requirements.txt`
   - Use a virtual environment if needed

### Performance Tips

1. **Model loading**: First request to a model may be slow (model loading)
2. **GPU usage**: Ollama will use GPU if available (NVIDIA/AMD)
3. **Memory**: Larger models (70B) require more RAM/VRAM
4. **Concurrent requests**: Ollama handles multiple requests efficiently

## License

This project is open source and available under the MIT License.

### References

Ollama

https://ollama.ai/

FastAPI

https://fastapi.tiangolo.com/

OpenAI API

https://platform.openai.com/docs/api-reference

Deploy FastAPI on Cloud Providers

https://fastapi.tiangolo.com/deployment/cloud/
