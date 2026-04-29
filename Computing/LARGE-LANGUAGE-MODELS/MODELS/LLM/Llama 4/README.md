# AI Agent & No Framework - Llama 4 (Scout)

A Python based AI agent implementation without commercial frameworks like LlamaIndex or open-source frameworks like LangChain. This AI agent uses Meta **Llama 4 Scout** with its advanced Mixture-of-Experts architecture by default, 10 million token context window, and native tool calling capabilities for LLM capabilities and provides RESTful API services with **Open WebUI integration**.

## Components

- **No Framework**: Python implementation using only standard Python libraries and lightweight dependencies
- **Llama 4 Scout integration**: Uses Meta Llama 4 (Scout) with 10M token context window and MoE architecture
- **Tool calling**: Native function calling capabilities with weather and other tools
- **Weather service**: Integrates with Open-Meteo API for weather queries with intelligent tool calling
- **RESTful API**: FastAPI-based web service with OpenAI-compatible responses
- **Web interface**: Open WebUI integration for browser-based interaction
- **Asynchronous**: Supports concurrent requests using async/await
- **Memory**: Optimized for quantized models requiring <12GB GPU VRAM and <32GB RAM
- **LLM models backward compatibility**: Supports Llama 4 and legacy Llama 3.x models

## AI Agents, Open WebUI and Ollama

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Open WebUI    │    │  AI Agent API   │    │     Ollama      │
│  (Port: 3000)   │────│  (Port: 8000)   │────│  (Port: 11434)  │
│   Docker        │    │    FastAPI      │    │   Llama 4       │
│                 │    │                 │    │    Scout        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                │                       │
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Weather API    │    │ Tool Calling    │
                       │  (Open-Meteo)   │    │   Framework     │
                       └─────────────────┘    └─────────────────┘
```

## System requirements

- Python 3.8+ (3.12 recommended for best performance)
- GPU with <12GB VRAM (for quantized Llama 4 Scout)
- <32GB RAM (recommended for optimal performance)
- Linux (Debian/Ubuntu) environment (primary)
- Internet connection for initial model download (10-20GB)

## Options

### Option 1: Setup with Llama 4 Scout (Recommended)

```bash
# 1. Run automated setup for Llama 4 Scout
./setup-llama4.sh

# 2. Start the AI Agent
./start-simple.sh

# 3. Or start full stack with web interface
make full-stack
```

### Option 2: Manual setup

```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &

# 2. Pull Llama 4 Scout model (10-30 minutes download)
ollama pull llama4:scout
# Alternative quantized version:
# ollama pull ingu627/llama4-scout-q4

# 3. Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Start AI Agent
python src/index.py
```

**Access points:**
- **Web interface**: http://localhost:3000 (Open WebUI)
- **API**: http://localhost:8000 (AI Agent with Llama 4 Scout)
- **Health check**: http://localhost:8000/health

### Option 3: Legacy support (Llama 3.x)

```bash
# For systems that can't run Llama 4, use legacy models
export MODEL_NAME="llama3.1:8b-instruct-q4_0"
./setup.sh
source venv/bin/activate
python src/index.py
```

### Option 4: Using makefile commands

```bash
make setup         # Full setup
make webui-setup   # Setup Open WebUI
make run           # Start AI Agent only
make webui-start   # Start Open WebUI only
make full-stack    # Start everything with Llama 4 Scout
make test          # Test all components
```

### Option 5: WebUI setup (Easiest)

```bash
# One-command setup for AI Agent + Open WebUI
./start-webui.sh

# Test the setup
./test_api_examples.sh

# Clean shutdown
./start-webui.sh stop
```

## Llama 4 Scout

### Capabilities
- **10 Million Token Context**: Process extremely long documents and conversations
- **Mixture of Experts (MoE)**: Efficient processing with specialized expert networks
- **Tool calling**: Built-in function calling without prompt engineering
- **Reasoning**: Logic and problem-solving capabilities
- **Multimodal**: Integration with various data types

### Tool calling example
```python
# Llama 4 Scout automatically calls tools:
User: "What's the weather in London and Paris?"
Scout: [get_weather(city="London", metric="celsius"), get_weather(city="Paris", metric="celsius")]
Agent: Executes tools and provides consolidated response
```

## API usage

### Web interface (Recommended) - Open WebUI setup

Open WebUI provides a modern chat interface similar to ChatGPT that connects to your AI Agent backend.

#### Step 1: Start AI Agent backend
```bash
# Option A: Quick start with automated setup
./setup-llama4.sh
./start-simple.sh

# Option B: Manual start
python src/index.py
```

#### Step 2: Setup and start Open WebUI with Docker
```bash
# Pull and start Open WebUI container
docker run -d \
  --name open-webui \
  --restart unless-stopped \
  -p 3000:8080 \
  -e OPENAI_API_BASE_URL=http://host.docker.internal:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -e DEFAULT_MODELS=ai-agent-llama4-scout \
  -e ENABLE_SIGNUP=true \
  -v open-webui:/app/backend/data \
  ghcr.io/open-webui/open-webui:main

# Check if container is running
docker ps | grep open-webui
```

#### Step 3: Access Open WebUI
1. **Open browser**: Navigate to `http://localhost:3000`
2. **Create account**: Sign up with any email/password (local only)
3. **Select model**: Choose "ai-agent-llama4-scout" from the model dropdown
4. **Start chatting**: Begin interacting with your AI Agent

#### Step 4: Example conversations in Open WebUI

**Weather Queries:**
```
You: "What's the temperature in London?"
AI: "The current temperature in London, United Kingdom is 18°C. Weather conditions: Partly cloudy"

You: "How's the weather in Tokyo and Paris?"
AI: "Tokyo is currently 25°C with clear skies, while Paris is 22°C with sunny conditions."
```

**Greetings:**
```
You: "Hello, how are you?"
AI: "Hello! I'm doing well, thank you for asking. I'm your AI assistant powered by Llama 4 Scout. I'm here to help you with questions, provide weather information, or just have a conversation. What can I do for you today?"
```

**Questions:**
```
You: "Explain quantum computing"
AI: "Quantum computing is a revolutionary computing paradigm that leverages quantum mechanical phenomena..."
```

### Direct API access (For developers and testing)

The AI Agent provides OpenAI-compatible REST API endpoints that can be used programmatically or for testing.

#### Health check
```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-20T10:30:00Z",
  "services": {
    "llm": "healthy",
    "weather_api": "healthy"
  },
  "agent_info": {
    "name": "AI Agent - Llama 4 Scout",
    "version": "2.0.0",
    "model": "llama4:scout",
    "capabilities": ["chat", "weather", "greetings", "tool_calling"],
    "context_window": "10M tokens"
  }
}
```

#### Chat Completion (OpenAI API compatible)

**Basic greeting:**
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello, how are you?"}
    ],
    "temperature": 0.7
  }'
```

**Weather query for single city:**
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is the temperature in London?"}
    ],
    "temperature": 0.7
  }'
```

**Multi-city weather query:**
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Compare the weather in New York, Tokyo, and Berlin"}
    ],
    "temperature": 0.7
  }'
```

**General knowledge question:**
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Explain the difference between AI and machine learning"}
    ],
    "temperature": 0.7
  }'
```

**Example API response:**
```json
{
  "id": "chatcmpl-abc123...",
  "object": "chat.completion",
  "created": 1642694800,
  "model": "ai-agent-llama4-scout",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "The current temperature in London, United Kingdom is 18°C. Weather conditions: Partly cloudy"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 12,
    "completion_tokens": 25,
    "total_tokens": 37
  },
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

## Agent capabilities

### 1. Advanced Greeting Handler (Llama 4)
- Natural conversation understanding with extended context
- Personalized responses based on conversation history
- Multi-turn dialogue management with 10M token memory

### 2. Weather service with tool calling
- **Llama 4 Scout**: Automatically detects weather queries and calls appropriate tools
- **Multi-city support**: "Weather in London, Paris, and Tokyo" → calls multiple weather APIs
- **Smart location extraction**: Understands context and ambiguous location references
- **Real-time data**: Current weather via Open-Meteo API with no API key required

### 3. LLM responses
- **Extended context**: Maintains conversation context across very long sessions
- **Mixture of Experts**: Efficient processing for different types of queries
- **Tool integration**: Seamless function calling for real-world data
- **Backward compatibility**: Falls back to traditional processing for legacy models

## AI Agents architecture

```
src/
├── agents.py         # AI agent logic and request routing
├── index.py          # FastAPI server and main application  
└── tools.py          # External tools (weather API, LLM interface)

docker-compose.yml    # Open WebUI Docker configuration
open-webui-config.json# Open WebUI customization
setup-webui.sh        # Open WebUI setup script
webui-manage.sh       # Open WebUI management script
test-integration.sh   # Integration testing script
```

### Components

1. **Agent (`agents.py`)**
   - Request classification and routing
   - Response formatting
   - Context management

2. **Tools (`tools.py`)**
   - Weather API integration
   - LLM communication (Ollama)
   - Utility functions

3. **Server (`index.py`)**
   - FastAPI web service
   - OpenAI-compatible endpoints
   - Async request handling

4. **Open WebUI integration**
   - Docker-based web interface
   - OpenAI-compatible API consumption
   - User-friendly chat interface

## AI Agent ↔ Ollama ↔ Llama 4

### Data Flow

The AI Agent communicates with Llama 4 Scout through Ollama's REST API, handling different prompt formats and message types based on the model capabilities.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Request  │────│   AI Agent      │────│     Ollama      │
│ (OpenAI Format) │    │ (tools.py)      │    │  REST API       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │ Prompt Template │    │   Llama 4       │
                       │   Formatter     │────│    Scout        │
                       └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │ Tool Detection  │    │ Tool Execution  │
                       │ & Function Call │────│   (Weather)     │
                       └─────────────────┘    └─────────────────┘
```

### Message flow and processing

#### 1. **Input processing** (`agents.py`)

The AI Agent receives OpenAI-compatible chat completion requests:

```python
# agents.py - process_chat_completion()
async def process_chat_completion(self, messages: List[Dict[str, str]], 
                                temperature: float = 0.7, 
                                max_tokens: int = 512) -> Dict[str, Any]:
    """
    Process chat completion request in OpenAI-compatible format.
    
    Input format:
    {
        "messages": [
            {"role": "user", "content": "What's the weather in London?"}
        ],
        "temperature": 0.7
    }
    """
```

**Message processing steps:**
1. **Extract user message** from OpenAI format
2. **Route to ToolManager** for processing
3. **Format response** back to OpenAI-compatible format

#### 2. **Prompt Template generation** (`tools.py`)

The system automatically detects the model type and applies appropriate prompt formatting:

##### **Llama 4 Scout Template** (Tool support)

```python
# tools.py - _create_llama4_prompt()
def _create_llama4_prompt(self, user_message: str, system_message: str, tools: List[Dict]):
    """
    Creates Llama 4 Scout prompt with tool definitions.
    """
    prompt = f"""<|begin_of_text|><|header_start|>system<|header_end|>

{system_message}

Available tools:
- get_weather(city, metric): Get weather information

<|eot|><|header_start|>user<|header_end|>

{user_message}<|eot|><|header_start|>assistant<|header_end|>

"""
    return prompt
```

**Example Llama 4 interaction:**
```
Input: "What's the weather in London and Paris?"

Generated Prompt:
<|begin_of_text|><|header_start|>system<|header_end|>

You are an advanced AI assistant powered by Llama 4 Scout. You have access to tools for real-time information.

Available tools:
- get_weather(city, metric): Get current weather information for any city

When a user asks about weather, use the get_weather tool by responding with:
[get_weather(city="<city_name>", metric="celsius")]

<|eot|><|header_start|>user<|header_end|>

What's the weather in London and Paris?<|eot|><|header_start|>assistant<|header_end|>

Llama 4 Response:
[get_weather(city="London", metric="celsius"), get_weather(city="Paris", metric="celsius")]
```

##### **Legacy Llama 3.x Template** (Backward compatibility)

```python
# tools.py - _create_llama_legacy_prompt()
def _create_llama_legacy_prompt(self, user_message: str, system_message: str):
    """
    Creates traditional Llama 3.x prompt format.
    """
    return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_message}<|eot_id|><|start_header_id|>user<|end_header_id|>

{user_message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
```

#### 3. **Ollama API communications**

The agent communicates with Ollama using HTTP REST API:

```python
# tools.py - generate_response()
async def generate_response(self, user_message: str, temperature: float = 0.7):
    """
    Sends request to Ollama API endpoint.
    """
    payload = {
        "model": self.model,  # "llama4:scout" or "llama3.1:8b-instruct-q4_0"
        "prompt": prompt,     # Formatted prompt from above
        "stream": False,
        "options": {
            "temperature": temperature,
            "top_p": 0.9,
            "top_k": 40,
            "num_ctx": 10000000,  # 10M context for Llama 4 Scout
            "max_tokens": 512
        }
    }
    
    # POST to http://localhost:11434/api/generate
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(self.api_url, json=payload)
        data = response.json()
        return data.get("response", "").strip()
```

#### 4. **Tool calling processing** (Llama 4 Scout)

When Llama 4 Scout responds with tool calls, the agent processes them:

```python
# tools.py - _handle_tool_calls()
async def _handle_tool_calls(self, response_text: str, original_message: str):
    """
    Example: Response contains: [get_weather(city="London", metric="celsius")]
    """
    # 1. Extract tool calls using regex
    tool_pattern = r'get_weather\(city="([^"]+)"(?:, metric="([^"]+)")?\)'
    matches = re.findall(tool_pattern, response_text)
    
    # 2. Execute weather API calls
    tool_results = []
    for city, metric in matches:
        weather_response = await weather_tool.get_temperature(city)
        tool_results.append({"response": weather_response})
    
    # 3. Create follow-up prompt with tool results
    follow_up_prompt = f"""<|begin_of_text|><|header_start|>user<|header_end|>

{original_message}<|eot|><|header_start|>assistant<|header_end|>

{response_text}<|eot|><|header_start|>ipython<|header_end|>

{json.dumps(tool_results, indent=2)}<|eot|><|header_start|>assistant<|header_end|>

"""
    
    # 4. Get final response from Llama 4
    # Returns: "The weather in London is 18°C with partly cloudy conditions."
```

### Message Format specifications

#### **OpenAI Input format** (What users send)
```json
{
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What's the weather in London?"}
    ],
    "temperature": 0.7,
    "max_tokens": 512
}
```

#### **Ollama API request format** (What agent sends to Ollama)
```json
{
    "model": "llama4:scout",
    "prompt": "<|begin_of_text|><|header_start|>system<|header_end|>\n\nYou are a helpful AI assistant...",
    "stream": false,
    "options": {
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 40,
        "num_ctx": 10000000,
        "max_tokens": 512
    }
}
```

#### **Ollama API response format** (What Ollama returns)
```json
{
    "model": "llama4:scout",
    "created_at": "2025-07-20T10:30:00Z",
    "response": "[get_weather(city=\"London\", metric=\"celsius\")]",
    "done": true,
    "context": [...],
    "total_duration": 2500000000,
    "load_duration": 1000000,
    "prompt_eval_count": 100,
    "prompt_eval_duration": 500000000,
    "eval_count": 25,
    "eval_duration": 1000000000
}
```

#### **OpenAI output format** (What agent returns to user)
```json
{
    "id": "chatcmpl-abc123",
    "object": "chat.completion",
    "created": 1642694800,
    "model": "ai-agent-llama4-scout",
    "choices": [{
        "index": 0,
        "message": {
            "role": "assistant",
            "content": "The current temperature in London is 18°C with partly cloudy conditions."
        },
        "finish_reason": "stop"
    }],
    "usage": {
        "prompt_tokens": 100,
        "completion_tokens": 25,
        "total_tokens": 125
    },
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

### Processing data examples

#### **Example 1: Weather query with tool calling**

```
1. User Input (OpenAI format):
   {"messages": [{"role": "user", "content": "What's the weather in Tokyo?"}]}

2. Agent Processing (agents.py):
   → Extract user message: "What's the weather in Tokyo?"
   → Send to ToolManager.process_message()

3. Prompt Generation (tools.py):
   → Detect Llama 4 Scout → Use _create_llama4_prompt()
   → Include tool definitions in system message

4. Ollama Request:
   POST http://localhost:11434/api/generate
   {
     "model": "llama4:scout",
     "prompt": "<|begin_of_text|><|header_start|>system<|header_end|>...tools...",
     "options": {"temperature": 0.7, "num_ctx": 10000000}
   }

5. Llama 4 Scout Response:
   "[get_weather(city=\"Tokyo\", metric=\"celsius\")]"

6. Tool Execution (tools.py):
   → Parse tool call: get_weather(city="Tokyo", metric="celsius")
   → Execute: weather_tool.get_temperature("Tokyo")
   → Result: "The current temperature in Tokyo is 25°C. Clear skies."

7. Second Ollama Request (with tool results):
   → Include tool results in ipython section
   → Get natural language response

8. Final Response (OpenAI format):
   {
     "choices": [{
       "message": {
         "content": "The current temperature in Tokyo is 25°C with clear skies."
       }
     }]
   }
```

#### **Example 2: Greeting (No tools)**

```
1. User Input: "Hello, how are you?"

2. Legacy Model Processing:
   → Use _create_llama_legacy_prompt()
   → No tool definitions

3. Single Ollama Request:
   → Direct prompt/response cycle
   → No tool calling

4. Response: Natural greeting from LLM
```

### Configuration and model detection

```python
# tools.py - Model detection and configuration
class LLMTool:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama4:scout"):
        self.base_url = base_url
        self.model = model
        self.api_url = f"{base_url}/api/generate"
        
        # Automatic model detection
        self.is_llama4 = "llama4" in model.lower()
        
        # Configure context window based on model
        self.context_size = 10000000 if self.is_llama4 else 4096
```

This integration provides seamless communication between the OpenAI-compatible API interface and Llama 4's advanced capabilities while maintaining backward compatibility with legacy models.

## LLM configuration

### Llama 4 Scout Template format

The agent uses Meta Llama 4 Scout with the following template format:

```
<|begin_of_text|><|header_start|>system<|header_end|>

You are a helpful AI assistant with access to tools.

Available tools:
- get_weather(city, metric): Get current weather information

<|eot|><|header_start|>user<|header_end|>

What's the weather in London?<|eot|><|header_start|>assistant<|header_end|>

[get_weather(city="London", metric="celsius")]<|eot|><|header_start|>ipython<|header_end|>

[{"response": "The current temperature in London is 18°C. Partly cloudy."}]<|eot|><|header_start|>assistant<|header_end|>

The current weather in London is 18°C with partly cloudy conditions.
```

### Legacy Llama 3.x Template (Backward compatibility)

```
<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a helpful AI assistant.<|eot_id|><|start_header_id|>user<|end_header_id|>

{user_message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
```

### Available models

#### Llama 4 models (Recommended)
- **llama4:scout** - Full Scout model with 10M context, MoE architecture
- **ingu627/llama4-scout-q4** - 4-bit quantized version (~10GB VRAM)
- **llama4:maverick** - Alternative Llama 4 variant

#### Legacy models (Fallback)
- **llama3.1:8b-instruct-q4_0** - 4-bit quantization, ~5GB VRAM
- **llama3.1:8b-instruct-q8_0** - 8-bit quantization, ~8GB VRAM
- **llama3.1:7b-instruct-q4_0** - Smaller model, ~4GB VRAM

## Weather API integration

### Open-Meteo APIs used

1. **Geocoding API**
   - Endpoint: `https://geocoding-api.open-meteo.com/v1/search`
   - Converts city names to coordinates
   - No API key required

2. **Weather API**
   - Endpoint: `https://api.open-meteo.com/v1/forecast`
   - Fetches current weather data
   - Uses latitude/longitude coordinates

### Example: Weather query flow

1. User: "What's the temperature in London?"
2. Agent extracts city name: "London"
3. Geocoding API call: Get coordinates (51.5074, -0.1278)
4. Weather API call: Get current temperature
5. Format response: "The current temperature in London is 18°C"

## Development

### Commands

```bash
make help              # Show all available commands
make setup             # Full setup
make run               # Start AI Agent
make webui-setup       # Setup Open WebUI
make webui-start       # Start Open WebUI  
make full-stack        # Start everything
make test              # Test components
make test-integration  # Test full integration
make health            # Quick health check
make webui-health      # Comprehensive health check
```

### Testing

#### Automated testing
```bash
# Test individual components
python test-llama4.py

# Test API endpoints
./test_api.sh

# Test full integration (AI Agent + Open WebUI)
./test-integration.sh
```

#### Manual testing via Open WebUI
1. **Open browser**: Navigate to `http://localhost:3000`
2. **Login**: Use your created account
3. **Test different scenarios**:

**Weather Testing:**
- "What's the temperature in Tokyo?"
- "How's the weather in London and Paris?"
- "Compare temperatures in New York, Berlin, and Sydney"
- "Is it cold in Moscow right now?"

**Greeting Testing:**
- "Hello there!"
- "Good morning, how are you?"
- "Hi, nice to meet you"

**General Q&A Testing:**
- "Explain quantum physics in simple terms"
- "What is the capital of Australia?"
- "How does machine learning work?"
- "Tell me about Python programming"

#### CURL testing

Create a test script `test_api_examples.sh`:
```bash
#!/bin/bash
echo "Testing AI Agent API..."

# Test 1: Health Check
echo "=== Health Check ==="
curl -s http://localhost:8000/health | jq '.'

# Test 2: Greeting
echo -e "\n=== Greeting Test ==="
curl -s -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello! How are you today?"}],
    "temperature": 0.7
  }' | jq '.choices[0].message.content'

# Test 3: Weather - Single City
echo -e "\n=== Weather: Single City ==="
curl -s -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "What is the temperature in London?"}],
    "temperature": 0.7
  }' | jq '.choices[0].message.content'

# Test 4: Weather - Multiple Cities
echo -e "\n=== Weather: Multiple Cities ==="
curl -s -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Compare weather in Tokyo, New York, and Berlin"}],
    "temperature": 0.7
  }' | jq '.choices[0].message.content'

# Test 5: General Question
echo -e "\n=== General Question ==="
curl -s -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Explain artificial intelligence in 50 words"}],
    "temperature": 0.7
  }' | jq '.choices[0].message.content'

echo -e "\n=== Testing Complete ==="
```

**Run the test:**
```bash
chmod +x test_api_examples.sh
./test_api_examples.sh
```

### Environment variables

Create `.env` file for AI Agent configuration:
```env
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=llama3.1:8b-instruct-q4_0
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

Create `.env.docker` for Open WebUI configuration:
```env
WEBUI_PORT=3000
OPENAI_API_BASE_URL=http://host.docker.internal:8000/v1
DEFAULT_MODELS=ai-agent-no-framework
ENABLE_SIGNUP=false
```

## Documentation

- **[INSTALLATION.md](INSTALLATION.md)** - Complete setup guide for Debian Linux
- **[DOCKER.md](DOCKER.md)** - Detailed Docker configuration
- **[EXAMPLES.md](EXAMPLES.md)** - Usage examples and API references

## Troubleshooting

### Open WebUI Issues

1. **Cannot access Open WebUI at localhost:3000**
   ```bash
   # Check if container is running
   docker ps | grep open-webui
   
   # Check container logs
   docker logs open-webui
   
   # Restart container
   docker restart open-webui
   
   # If container doesn't exist, start it again
   docker run -d \
     --name open-webui \
     --restart unless-stopped \
     -p 3000:8080 \
     -e OPENAI_API_BASE_URL=http://host.docker.internal:8000/v1 \
     -e OPENAI_API_KEY=dummy \
     ghcr.io/open-webui/open-webui:main
   ```

2. **Open WebUI shows "Connection Error" or "No models available"**
   ```bash
   # Verify AI Agent is running
   curl http://localhost:8000/health
   
   # Check if AI Agent is accessible from Docker
   docker exec open-webui curl -s http://host.docker.internal:8000/health
   
   # If using Linux, try localhost instead
   docker rm -f open-webui
   docker run -d \
     --name open-webui \
     --network host \
     -e OPENAI_API_BASE_URL=http://localhost:8000/v1 \
     -e OPENAI_API_KEY=dummy \
     ghcr.io/open-webui/open-webui:main
   ```

3. **Weather queries not working in Open WebUI**
   ```bash
   # Test AI Agent directly
   curl -X POST http://localhost:8000/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{"messages": [{"role": "user", "content": "What is the temperature in London?"}]}'
   
   # Check weather API connectivity
   curl "https://api.open-meteo.com/v1/forecast?latitude=51.5074&longitude=-0.1278&current_weather=true"
   ```

### AI Agent Issues

1. **AI Agent won't start**
   ```bash
   # Check Python environment
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Check if port is in use
   lsof -i :8000
   
   # Kill process using port 8000 if needed
   sudo kill -9 $(lsof -t -i:8000)
   ```

2. **Ollama connection errors**
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/tags
   
   # Start Ollama if not running
   ollama serve &
   
   # List available models
   ollama list
   
   # Pull model if missing
   ollama pull llama4:scout
   # OR fallback model
   ollama pull llama3.1:8b-instruct-q4_0
   ```

3. **Weather API issues**
   ```bash
   # Test weather API directly
   curl "https://api.open-meteo.com/v1/forecast?latitude=51.5074&longitude=-0.1278&current_weather=true"
   
   # Test geocoding API
   curl "https://geocoding-api.open-meteo.com/v1/search?name=London&count=1&language=en&format=json"
   
   # Check internet connectivity
   ping -c 3 api.open-meteo.com
   ```

### Docker Issues

1. **Docker commands not working**
   ```bash
   # Check Docker status
   sudo systemctl status docker
   
   # Start Docker if stopped
   sudo systemctl start docker
   
   # Add user to docker group (logout/login required)
   sudo usermod -aG docker $USER
   ```

2. **Port conflicts**
   ```bash
   # Check what's using port 3000
   sudo lsof -i :3000
   
   # Use different port for Open WebUI
   docker run -d \
     --name open-webui \
     -p 3001:8080 \
     -e OPENAI_API_BASE_URL=http://host.docker.internal:8000/v1 \
     ghcr.io/open-webui/open-webui:main
   
   # Access at http://localhost:3001
   ```

### Complete System Reset

If you encounter persistent issues, perform a complete reset:

```bash
# Stop all services
docker stop open-webui
pkill -f "python src/index.py"
pkill -f ollama

# Remove containers
docker rm open-webui

# Clean up
docker system prune -f

# Restart from scratch
./setup-llama4.sh
./start-simple.sh

# Verify everything is working
curl http://localhost:8000/health
curl http://localhost:3000  # Should show Open WebUI login page
```

## Quick Start Summary

### 🚀 **Fastest Way to Get Started**

1. **Automated Setup** (Recommended):
   ```bash
   ./setup-llama4.sh        # Install everything
   ./start-webui.sh         # Start AI Agent + Open WebUI
   ```

2. **Access the Web Interface**:
   - Open: http://localhost:3000
   - Create account (any email/password)
   - Select model: `ai-agent-llama4-scout`
   - Start chatting!

3. **Test Examples**:
   ```bash
   ./test_api_examples.sh   # Test all functionality
   ```

### 💬 **Example Conversations**

**In Open WebUI, try these:**
- `"Hello, how are you?"`
- `"What's the temperature in London?"`
- `"Compare weather in Tokyo, Berlin, and New York"`
- `"Explain quantum computing simply"`

**API Testing (CURL):**
```bash
# Weather query
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "What is the temperature in Paris?"}]}'

# Greeting
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello!"}]}'
```

### 🔧 **Key Endpoints**

- **Open WebUI**: http://localhost:3000 (Chat Interface)
- **AI Agent API**: http://localhost:8000/v1/chat/completions (OpenAI Compatible)
- **Health Check**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs

### ⚡ **Features Highlights**

- ✅ **No Frameworks**: Pure Python implementation
- ✅ **Llama 4 Scout**: 10M token context, MoE architecture
- ✅ **Smart Weather**: Multi-city support with real-time data
- ✅ **Web Interface**: Modern chat UI with Open WebUI
- ✅ **API Compatible**: OpenAI-compatible endpoints
- ✅ **Tool Calling**: Native function calling for real-world data

### 🆘 **Need Help?**

- **Logs**: `tail -f ai_agent.log` (AI Agent) | `docker logs open-webui` (WebUI)
- **Health**: `curl http://localhost:8000/health`
- **Troubleshooting**: See detailed troubleshooting section above
- **Reset**: `./start-webui.sh stop && ./start-webui.sh`

## License

This project is open source and available under the MIT License.

