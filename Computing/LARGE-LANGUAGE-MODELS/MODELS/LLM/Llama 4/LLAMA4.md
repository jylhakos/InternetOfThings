# Meta Llama 4 (Scout) integration

## Overview

This document provides information about integrating Meta Llama 4 (Scout) into the AI Agent framework without using commercial frameworks. Llama 4 (Scout) brings advanced capabilities including Mixture-of-Experts (MOE) architecture, 10 million token context window, and native tool calling.

## Table of contents

1. [Llama 4 Scout features](#llama-4-scout-features)
2. [Installation and setup](#installation-and-setup)
3. [Architecture and implementation](#architecture-and-implementation)
4. [Tool Calling framework](#tool-calling-framework)
5. [Prompt Template](#prompt-template-guide)
6. [API reference](#api-reference)
7. [Performance](#performance-optimization)
8. [Troubleshooting](#troubleshooting)
9. [Cloud deployment](#cloud-deployment)

## Llama 4 Scout features

### Capabilities

- **Mixture of Experts (MoE) architecture**: Efficient processing through specialized expert networks
- **10 Million Token context**: Process extremely long documents and maintain extended conversations
- **Native Tool Calling**: Built-in function calling without prompt engineering
- **Reasoning**: Logic, mathematics, and problem-solving
- **Multimodal**: Integration with various data formats
- **Instruction Following**: Improved adherence to complex instructions

### Performance

- **Model sizes**: Available in various quantization levels
- **Memory requirements**: 
  - Full precision: ~40GB VRAM
  - INT4 quantized: ~10-12GB VRAM
  - INT8 quantized: ~20GB VRAM
- **Context processing**: Up to 10M tokens (vs 4K-8K in legacy models)
- **Inference speed**: Optimized through MoE architecture

## Installation and setup

### Automated setup (Recommended)

```bash
# Run the Llama 4 setup script
chmod +x setup-llama4.sh
./setup-llama4.sh
```

### Manual setup

#### 1. Install Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
ollama serve &
```

#### 2. Pull Llama 4 Scout model

```bash
# Primary model (full Scout)
ollama pull llama4:scout

# Alternative quantized version (if primary fails)
ollama pull ingu627/llama4-scout-q4

# Legacy fallback
ollama pull llama3.1:8b-instruct-q4_0
```

#### 3. Python virtual environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 4. Configuration

Create `.env` file:

```env
# Llama 4 Configuration
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=llama4:scout
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Advanced settings
CONTEXT_WINDOW=10000000
ENABLE_TOOL_CALLING=true
TEMPERATURE_DEFAULT=0.7
MAX_TOKENS_DEFAULT=512
```

## Architecture and implementation

### Class structure

```python
# Enhanced LLMTool for Llama 4
class LLMTool:
    def __init__(self, base_url, model):
        self.is_llama4 = "llama4" in model.lower()
        # ... initialization
    
    def _create_llama4_prompt(self, user_message, system_message, tools):
        # Llama 4 specific prompt formatting
        
    def _handle_tool_calls(self, response_text, original_message):
        # Process tool calls from Llama 4 response
```

### Components

1. **LLMTool**: Handles model communication and prompt formatting
2. **ToolManager**: Orchestrates tool calling and response processing
3. **AIAgent**: Provides OpenAI-compatible interface
4. **WeatherTool**: Example tool implementation

### Data flow

```
User Input → ToolManager → LLMTool → Ollama (Llama 4) → Tool Calls → Response
                ↑                                              ↓
            Tool Results ←←←←←← External Tools ←←←←←←←←←←←←←←←←←↙
```

## Tool Calling framework

### Available tools

#### Weather tool
```python
{
    "name": "get_weather",
    "description": "Get current weather information for a specific city",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City name"},
            "metric": {"type": "string", "description": "celsius or fahrenheit", "default": "celsius"}
        },
        "required": ["city"]
    }
}
```

### Tool Call process

1. **User query**: "What's the weather in London and Paris?"

2. **Llama 4 response**: 
   ```
   [get_weather(city="London", metric="celsius"), get_weather(city="Paris", metric="celsius")]
   ```

3. **Tool execution**: Agent processes both weather API calls

4. **Tool results**: 
   ```json
   [
     {"response": "London: 18°C, partly cloudy"},
     {"response": "Paris: 22°C, sunny"}
   ]
   ```

5. **Final Response**: "The weather in London is 18°C with partly cloudy conditions, while Paris is 22°C and sunny."

### Custom Tools

```python
# Define new tool in LLMTool._get_available_tools()
{
    "name": "calculate",
    "description": "Perform mathematical calculations",
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {"type": "string", "description": "Mathematical expression"}
        },
        "required": ["expression"]
    }
}

# Implement tool handler in ToolManager
async def _handle_calculate_tool(self, expression):
    # Safe mathematical evaluation
    try:
        result = eval(expression)  # Use safe_eval in production
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {e}"
```

## Prompt Template

### Llama 4 Scout Template

```
<|begin_of_text|><|header_start|>system<|header_end|>

{system_message}

Available tools:
- get_weather(city, metric): Get weather information

<|eot|><|header_start|>user<|header_end|>

{user_message}<|eot|><|header_start|>assistant<|header_end|>

{assistant_response}<|eot|><|header_start|>ipython<|header_end|>

{tool_results}<|eot|><|header_start|>assistant<|header_end|>

{final_response}
```

### Legacy Llama 3.x Template (Backward compatibility)

```
<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_message}<|eot_id|><|start_header_id|>user<|end_header_id|>

{user_message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

{response}
```

### Roles

- **system**: Defines assistant behavior and available tools
- **user**: User input and queries
- **assistant**: Model responses and tool calls
- **ipython**: Tool execution results (Llama 4 specific)

## API reference

### Health check

```bash
GET /health

Response:
{
    "status": "healthy",
    "services": {
        "llm": "healthy",
        "weather_api": "healthy"
    },
    "agent_info": {
        "name": "AI Agent - Llama 4 Scout",
        "version": "2.0.0",
        "model": "llama4:scout",
        "capabilities": ["chat", "weather", "greetings", "tool_calling"],
        "context_window": "10M tokens",
        "features": {
            "mixture_of_experts": true,
            "tool_calling": true,
            "extended_context": true
        }
    }
}
```

### Chat Completion

```bash
POST /v1/chat/completions

Request:
{
    "messages": [
        {"role": "user", "content": "What's the weather in Tokyo?"}
    ],
    "temperature": 0.7
}

Response:
{
    "id": "chatcmpl-...",
    "object": "chat.completion",
    "model": "ai-agent-llama4-scout",
    "choices": [{
        "message": {
            "role": "assistant",
            "content": "The current temperature in Tokyo is 25°C with clear skies."
        },
        "finish_reason": "stop"
    }],
    "metadata": {
        "agent_type": "weather",
        "model_backend": "llama4:scout",
        "llama4_features": {
            "context_window": "10M tokens",
            "tool_calling": true,
            "mixture_of_experts": true
        }
    }
}
```

## Performance

### Memory management

```python
# Optimize for available VRAM
payload = {
    "model": self.model,
    "prompt": prompt,
    "options": {
        "num_ctx": 10000000,  # Full context for Llama 4
        "num_gpu": 1,         # Use single GPU
        "num_thread": 8,      # Optimize CPU threads
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 40
    }
}
```

### Batch processing

```python
# Process multiple requests efficiently
async def batch_process(self, messages_list):
    tasks = [self.process_message(msg) for msg in messages_list]
    results = await asyncio.gather(*tasks)
    return results
```

### Context Window management

```python
# Manage long conversations
def manage_context(self, messages, max_tokens=10000000):
    total_tokens = sum(len(msg['content'].split()) for msg in messages)
    if total_tokens > max_tokens * 0.9:  # Leave 10% buffer
        # Implement sliding window or summarization
        messages = self.compress_context(messages)
    return messages
```

## Troubleshooting

### Issues

#### 1. Model download failures
```bash
# Check network connection
curl -I https://ollama.com

# Try alternative model
ollama pull ingu627/llama4-scout-q4

# Check disk space
df -h
```

#### 2. Memory issues
```bash
# Check available memory
free -h
nvidia-smi  # For GPU memory

# Use smaller context window
export NUM_CTX=100000  # 100K instead of 10M
```

#### 3. Tool Calling not working
```python
# Debug tool calls
print(f"Raw LLM response: {response_text}")
print(f"Tool pattern matches: {re.findall(tool_pattern, response_text)}")

# Verify tool definitions
print(f"Available tools: {self._get_available_tools()}")
```

#### 4. Performance issues
```bash
# Monitor system resources
htop
nvidia-smi -l 1

# Adjust Ollama settings
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_MAX_LOADED_MODELS=1
```

### Debugging

```bash
# Test Ollama directly
curl http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama4:scout",
    "prompt": "Hello, respond with OK",
    "stream": false
  }'

# Test Python components
python test-llama4.py

# Check logs
tail -f /var/log/ollama.log
```

## Cloud deployment

### AWS EC2 setup

```bash
# Launch EC2 instance with GPU support
# Recommended: g4dn.xlarge or p3.2xlarge

# Install NVIDIA drivers
sudo apt update
sudo apt install -y nvidia-driver-535

# Install Docker for containerized deployment
sudo apt install -y docker.io
sudo usermod -aG docker $USER

# Deploy using Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

### Environment variables for cloud

```env
# Production configuration
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=llama4:scout
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Security
API_KEY=your-secure-api-key
CORS_ORIGINS=https://yourdomain.com

# Scaling
MAX_CONCURRENT_REQUESTS=10
TIMEOUT_SECONDS=60
```

### Kubernetes deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-agent-llama4
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ai-agent-llama4
  template:
    spec:
      containers:
      - name: ai-agent
        image: your-registry/ai-agent:llama4
        resources:
          requests:
            memory: "32Gi"
            nvidia.com/gpu: 1
          limits:
            memory: "64Gi"
            nvidia.com/gpu: 1
        env:
        - name: MODEL_NAME
          value: "llama4:scout"
```

## Recommended

### 1. Prompt Engineering for Llama 4

```python
# Effective system prompts
system_prompt = """You are an advanced AI assistant powered by Llama 4 Scout.

Core Principles:
- Use tools when real-time data is needed
- Be precise and helpful
- Leverage your extended context window for complex tasks

Available Tools: {tools}

Guidelines:
- For weather queries, use get_weather(city, metric)
- For calculations, show your work
- For long documents, utilize full context window
"""
```

### 2. Error handling

```python
async def safe_llm_call(self, prompt, retries=3):
    for attempt in range(retries):
        try:
            response = await self.llm_call(prompt)
            return response
        except Exception as e:
            if attempt == retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### 3. Monitoring and logging

```python
import logging

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_agent.log'),
        logging.StreamHandler()
    ]
)

# Log tool calls and responses
logger.info(f"Tool call: {tool_name}({parameters})")
logger.info(f"Response time: {response_time}ms")
```
