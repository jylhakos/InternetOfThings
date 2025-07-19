# AI Agents

### **Choose Python implementation when:**
-  **Existing Python** infrastructure/expertise
-  **Specific Python libraries** required (scikit-learn, pandas, NumPy)
-  **ML pipeline integration** with Python-based tools
-  **Jupyter notebook** workflows needed
-  **Legacy system compatibility** with Python

**Python implementation Options:**
1. **Framework-free** (current): Minimal dependencies, educational
2. **Python + LangChain**: Enhanced with [LangChain Python libraries](https://python.langchain.com/docs/tutorials/)

** LangChain Python setup:**
```bash
# Install LangChain Python dependencies
pip install -r requirements-langchain-python.txt

# Follow tutorials: https://python.langchain.com/docs/tutorials/
```

### **Production deployment comparison**

| Production | JavaScript/LangChain.js | Python/FastAPI | Python + LangChain |
|------------------|---------------------------|-------------------|----------------------|
| **Priority** | Primary | Alternative | Use Cases |
| **Port** | 8000 | 8001 | 8002 |
| **Container** | Multi-stage optimized | Basic Python image | Python + LangChain deps |
| **Startup time** | ~5-10 seconds | ~15-30 seconds | ~20-40 seconds |
| **Memory usage** | 200-400MB | 400-800MB | 500-1000MB |
| **Scaling** | Horizontal (event-driven) | Vertical (thread-based) | Vertical + Framework |
| **DevOps** | Lower | Higher | Highest |
| **Maintenance** | npm ecosystem | pip/conda management | LangChain + Python deps |
| **Documentation** | LangChain.js docs | Custom docs | [python.langchain.com](https://python.langchain.com/docs/tutorials/) |t/LangChain.js (Prioritized) & Python Implementations

This project provides **two AI agent implementations** with **JavaScript/LangChain.js as the prioritized choice** for production deployment:

##  **Primary: JavaScript/LangChain.js implementation (Recommended)**
- ** Production**: Modern LangChain.js framework with ReAct agents
- **Performance**: Node.js/Express.js for concurrent request handling
- **Containerized**: Multi-stage Docker builds optimized for production
- **Enterprise features**: Built-in monitoring, health checks, structured logging
- **Standard APIs**: OpenAI-compatible endpoints for seamless integration

## **Alternative: Python implementation (Optional)**
- **No Framework**: Python implementation without external frameworks
- **Custom integration**: For environments requiring specific Python libraries
- **Educational**: Demonstrates core AI agent concepts from scratch

Both JavaScript/Python implementations support:
- **Meta Llama-3.1** quantized models (8B-instruct-q4_0) via Ollama/vLLM
- **Weather APIs** with Open-Meteo integration (geocoding + current conditions)
- **Open WebUI** compatibility for browser-based interaction
- **RESTful APIs** with OpenAI-compatible response formats

---

## **Start - JavaScript implementation (Recommended)**

## **LangChain.js**

The JavaScript implementation uses the **LangChain.js framework** to create a AI Agent with:

### LangChain.js libraries
- **ReAct Agent**: Uses ReAct (Reason + Act) pattern for intelligent tool usage
- **Tools**: Weather, Location, and Greeting tools built with LangChain.js
- **Ollama integration**: Direct integration with Ollama LLM service
- **Conversation history**: Maintains session-based conversation history
- **Express.js Server**: RESTful API with OpenAI-compatible endpoints
- **Tool routing**: Intelligent routing to appropriate tools based on user input
- **Structured Output**: Uses Zod schemas for tool parameter validation

### Architecture

```
┌─────────────────┐    ┌─────────────────────────────────┐    ┌─────────────────┐
│   Open WebUI    │    │        AI Agent API            │    │     Ollama      │
│  (Port: 3000)   │────│  1. JavaScript (Port: 8000)    │────│  (Port: 11434)  │
│   Browser UI    │    │  2. Python (Port: 8001)        │    │ Llama-3.1 8B-Q4 │
└─────────────────┘    └─────────────────────────────────┘    └─────────────────┘
                                      │
                                      │
                              ┌─────────────────┐
                              │  Open-Meteo API │
                              │ Weather+Geocode │
                              └─────────────────┘
```

**Production deployment priority:**
1. **JavaScript/LangChain.js** (Primary - Port 8000)
2. **Python/FastAPI** (Alternative - Port 8001)

---

## **LangChain.js features (Primary)**

## System Requirements

### For Python Implementation
- Python 3.12 or compatible version
- GPU with <12GB VRAM (for quantized Llama-3.1)
- <32GB RAM
- Linux (Debian) environment

### For LangChain.js Implementation
- Node.js 18+
- NPM 8+
- Same GPU/RAM requirements as Python implementation
- Access to Ollama service

### Both Implementations Require
- **Ollama**: For running Llama-3.1 quantized models
- **Internet Connection**: For Open-Meteo API weather services

## Start

### **Option 1: JavaScript/LangChain.js (Prioritized for Production)**

```bash
#  Complete setup with dependencies
./install-langchain.sh

# Install and start Ollama with required model
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull llama3.1:8b-instruct-q4_0

# Start JavaScript AI Agent (production-ready)
npm start

# Test the implementation
npm test

# Interactive demo
npm run demo
```

**Access points:**
- **AI Agent API**: http://localhost:8000
- **Health check**: http://localhost:8000/health
- **API docs**: http://localhost:8000/agent/tools

### **Docker deployment (Recommended for production)**

```bash
# One-command deployment (JavaScript prioritized)
./deploy-langchain.sh

# Or using npm scripts
npm run deploy

# Full production deployment with monitoring
npm run deploy:production

# Manual Docker Compose
npm run docker:deploy
```

**Full stack:**
-  **AI Agent (JS)**: http://localhost:8000 - *Primary service*
-  **Ollama LLM**: http://localhost:11434 - *Model backend*  
-  **Open WebUI**: http://localhost:3000 - *Browser interface*

### 🔧 **Native deployment (Development)**

```bash
# Native Node.js deployment  
./deploy-langchain.sh native

# Or using npm
npm run deploy:native
```

### **Option 2: Python implementation (Alternative)**

```bash
# No Framework Python implementation  
./setup.sh
source venv/bin/activate
python src/index.py

# Or with Docker (runs on port 8001)
docker-compose --profile python-alternative up -d
```

**Access points:**
- **Python API**: http://localhost:8001 - *Alternative implementation*
- **Health check**: http://localhost:8001/health

#### **Python + LangChain option**

For teams preferring Python with LangChain framework, see the **[LangChain Python Documentation](https://python.langchain.com/docs/tutorials/)** for comprehensive tutorials and implementation guides.

**Python LangChain:**
- **Native Python ecosystem**: Seamless integration with scikit-learn, pandas, NumPy
- **Documentation**: Extensive tutorials at [python.langchain.com/docs/tutorials/](https://python.langchain.com/docs/tutorials/)
- **ML/AI libraries**: Direct access to Python's machine learning ecosystem
- **Jupyter compatibility**: Perfect for notebook-based development workflows
- **Research integration**: Easy integration with research libraries and custom models

**Implementation options:**
1. **Current**: o Framework Python (minimal dependencies)
2. **Enhanced**: Python + LangChain libraries (following [official tutorials](https://python.langchain.com/docs/tutorials/))

**LangChain Python setup:**
```bash
# Install LangChain Python libraries
pip install langchain langchain-community langchain-ollama
pip install langchain-openai langchain-experimental

# Follow tutorials at: https://python.langchain.com/docs/tutorials/
```

---

## LangChain.js details

### Architecture

1. **Agent (`src/agents.js`)**
   - LangChain.js ReAct Agent with tool execution
   - Express.js server for API endpoints
   - Session-based conversation management
   - OpenAI-compatible response format

2. **Tools (`src/tools.js`)**
   - **WeatherTool**: Fetches current weather using Open-Meteo API
   - **GreetingTool**: Handles greetings with contextual responses  
   - **LocationTool**: Provides detailed location/coordinate information
   - **ToolManager**: Manages tool routing and selection

3. **API endpoints**
   - `POST /v1/chat/completions` - OpenAI-compatible chat interface
   - `POST /agent/query` - Direct agent query with session management
   - `GET /health` - Service health and status
   - `GET /agent/tools` - List available tools
   - `GET /agent/history/:sessionId` - Conversation history
   - `DELETE /agent/history/:sessionId` - Clear conversation

### Tool capabilities

#### Weather tool
```javascript
// Handles queries like:
"What's the weather in London?"
"Temperature in Tokyo?"
"How's the climate in Paris?"

// Returns formatted weather data:
🌡️ Temperature: 22°C
🌤️ Conditions: Partly cloudy
💨 Wind Speed: 15 km/h
📍 Location: 51.5074°N, -0.1278°E
```

#### Greeting tool
```javascript
// Handles greetings like:
"Hello", "Good morning", "Hi there"

// Returns contextual responses:
"Good morning! I hope you're having a wonderful start to your day..."
```

#### Location tool
```javascript
// Handles location queries:
"Where is Paris?", "Coordinates of New York?"

// Returns detailed location info:
 Location Information for Paris:
 Country: France
 Coordinates: 48.8566°N, 2.3522°E
 Elevation: 35m above sea level
 Timezone: Europe/Paris
```

### Usages

#### 1. Direct Node.js
```javascript
import LangChainAIAgent from './src/agents.js';

const agent = new LangChainAIAgent({
  ollamaBaseUrl: 'http://localhost:11434',
  ollamaModel: 'llama3.1:8b-instruct-q4_0',
  port: 8000
});

await agent.start();
```

#### 2. API client
```javascript
// Test with curl
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "What's the weather in London?"}],
    "temperature": 0.7
  }'

// Test with JavaScript fetch
const response = await fetch('http://localhost:8000/agent/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'Good morning! How are you?',
    session_id: 'my-session-123'
  })
});

const result = await response.json();
console.log(result.response);
```

#### 3. Integration with Open WebUI

The LangChain.js agent is compatible with Open WebUI. Set the OpenAI API base URL to:
```
http://localhost:8000/v1
```

### Configuration

Environment variables in `.env`:
```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b-instruct-q4_0  
AGENT_PORT=8000
OPEN_METEO_GEOCODING_URL=https://geocoding-api.open-meteo.com/v1/search
OPEN_METEO_WEATHER_URL=https://api.open-meteo.com/v1/forecast
```

### Dependencies

Key LangChain.js packages:
- `@langchain/core` - Core LangChain functionality
- `@langchain/ollama` - Ollama LLM integration
- `@langchain/community` - Community tools and integrations
- `langchain` - Main LangChain package with agents
- `zod` - Schema validation for tools
- `express` - Web server framework
- `axios` - HTTP client for API calls

### Development and testing

```bash
# Development mode with auto-reload
npm run dev

# Run tests
npm test

# Install dependencies
npm install

# Check health
curl http://localhost:8000/health
```

---

## Implementation comparison

| Feature | Python (Framework-free) | **Python + LangChain** | **LangChain.js** |
|---------|-------------------------|------------------------|------------------|
| **Framework** | None (Pure Python) | LangChain Python | LangChain.js ReAct Agent |
| **Language** | Python 3.12+ | Python 3.8+ | Node.js 18+ |
| **Web Server** | FastAPI | FastAPI | Express.js |
| **Agent Pattern** | Custom routing logic | LangChain Agents | ReAct (Reason + Act) |
| **Tool Management** | Manual tool selection | LangChain Tools | Automatic tool routing |
| **Memory** | Simple conversation history | LangChain Memory | Session-based with LangChain |
| **Schema Validation** | Manual validation | Pydantic | Zod schemas |
| **Async Support** | Native async/await | LangChain async | Native async/await |
| **Learning Curve** | Lower (standard libraries) | Moderate (LangChain concepts) | Moderate (framework concepts) |
| **Extensibility** | Manual implementation | LangChain ecosystem | Framework-based extensions |
| **Documentation** | Custom docs | [python.langchain.com](https://python.langchain.com/docs/tutorials/) | LangChain.js docs |
| **Production Ready** | (Option) | (Option) | (Recommended) |

### When to use each implementation

**Choose Python (No Framework) implementation if:**
- You prefer minimal dependencies and full control over agent logic
- Want to understand core AI agent concepts from first principles
- Need maximum customization for specific use cases
- Working in constrained environments with minimal dependencies

**Choose Python + LangChain implementation if:**
- You prefer Python ecosystem but want framework benefits
- Need seamless integration with Python ML libraries (scikit-learn, pandas, NumPy)
- Want to follow comprehensive [LangChain Python tutorials](https://python.langchain.com/docs/tutorials/)
- Team has strong Python expertise but wants structured agent patterns
- Working with Jupyter notebooks and research-oriented workflows
- Need custom model integration with Python-based ML pipelines

**Choose LangChain.js implementation if: Recommended for production**
- You want optimal production performance and resource efficiency
- Need rapid development with battle-tested patterns
- Want advanced agent capabilities (reasoning, planning, complex tool use)
- Prefer modern JavaScript/Node.js ecosystem and tooling
- Need excellent containerization and horizontal scaling capabilities
- Want the fastest startup times and lowest memory footprint

---

## Setup Steps

### 1. Install Ollama and Model

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
ollama serve &

# Pull the quantized Llama-3.1 model (recommended <16GB model)
ollama pull llama3.1:8b-instruct-q4_0

# Verify installation
ollama list
```

### 2. Verify Ollama is running

```bash
# Test Ollama API
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1:8b-instruct-q4_0",
  "prompt": "Hello, how are you?",
  "stream": false
}'
```

### 3. Configure environment

Create `.env` file:
```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b-instruct-q4_0
AGENT_PORT=8000
OPEN_METEO_GEOCODING_URL=https://geocoding-api.open-meteo.com/v1/search
OPEN_METEO_WEATHER_URL=https://api.open-meteo.com/v1/forecast
```

---

## Testing both implementations

### Test LangChain.js Agent
```bash
# Start the agent
npm start

# In another terminal, run tests
npm test

# Manual test
curl -X POST http://localhost:8000/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the weather in Paris?"}'
```

### Test Python Agent
```bash
# Start the agent
source venv/bin/activate
python src/index.py

# In another terminal, run tests
python test_components.py

# Manual test
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

---

## Open WebUI integration

Both implementations are compatible with Open WebUI:

1. **Start Open WebUI**:
```bash
# Using Docker
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data --name open-webui --restart always \
  ghcr.io/open-webui/open-webui:main

# Or using provided script
./setup-webui.sh
```

2. **Configure Open WebUI**:
   - Navigate to http://localhost:3000
   - Go to Settings → Connections
   - Set OpenAI API Base URL: `http://host.docker.internal:8000/v1`
   - No API key required

3. **Test integration**:
   - Start your chosen agent implementation (Python or LangChain.js)
   - Use Open WebUI to chat with the agent
   - Test weather queries, greetings, and general questions

---

## Interactions

### Greeting examples
```
User: Hello, how are you?
Agent: Hello! It's great to meet you! I'm your AI assistant, ready to help with questions, weather information, or just have a friendly chat. What would you like to know?

User: Good morning!
Agent: Good morning! I hope you're having a wonderful start to your day. How can I assist you today?
```

### Weather examples
```
User: What's the weather like in London?
Agent: Current weather in London, United Kingdom:
🌡️ Temperature: 15°C
🌤️ Conditions: Partly cloudy
💨 Wind Speed: 12 km/h
📍 Location: 51.5074°N, -0.1278°E

User: Temperature in Tokyo?
Agent: Current weather in Tokyo, Japan:
🌡️ Temperature: 28°C
🌤️ Conditions: Clear sky
💨 Wind Speed: 8 km/h
📍 Location: 35.6762°N, 139.6503°E
```

### Location examples
```
User: Where is Paris located?
Agent: 📍 Location Information for Paris:
🌍 Country: France
🗺️ Coordinates: 48.8566°N, 2.3522°E
🏔️ Elevation: 35m above sea level
🕐 Timezone: Europe/Paris
👥 Population: 2,161,000
```

### Questions
```
User: Explain machine learning
Agent: Machine learning is a subset of artificial intelligence (AI) that focuses on developing algorithms and statistical models that enable computer systems to improve their performance on a specific task through experience, without being explicitly programmed for that task...
```

---

## Python implementation (Original)

### Option 2: Python implementation (Original)

```bash
# 1. Run complete setup
./setup.sh

# 2. Install and start Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull llama3.1:8b-instruct-q4_0

# 3. Start full stack (AI Agent + Open WebUI)
make full-stack
```

**Access points:**
- **Web interface**: http://localhost:3000 (Open WebUI)
- **API**: http://localhost:8000 (AI Agent)

### Option 2: API only

```bash
# Setup and start AI Agent only
./setup.sh
source venv/bin/activate
python src/index.py
```

### Option 3: Using Makefile commands

```bash
make setup         # Full setup
make webui-setup   # Setup Open WebUI
make run           # Start AI Agent only
make webui-start   # Start Open WebUI only
make full-stack    # Start everything
```

## API usage

### Web interface (Recommended)

1. Access Open WebUI at `http://localhost:3000`
2. Create account and log in
3. Start chatting with these examples:
   - "Hello, how are you?"
   - "What's the temperature in London?"
   - "Explain artificial intelligence"

### Direct API access

#### Health check
```bash
curl http://localhost:8000/health
```

#### Chat Completion (OpenAI compatible)
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

#### Weather query
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is the temperature in London?"}
    ]
  }'
```

## Agent capabilities

### 1. Greeting handler
- Detects greeting messages ("hello", "hi", "good morning", etc.)
- Uses LLM to generate natural responses
- Returns responses in OpenAI-compatible JSON format

### 2. Weather service
- Extracts city names from user queries
- Uses Open-Meteo Geocoding API to get coordinates
- Fetches current weather data using Open-Meteo API
- No API key required

### 3. General LLM responses
- Falls back to LLM for general questions
- Uses Meta Llama-3.1 prompt template syntax
- Maintains conversation context

## Architecture

```
src/
├── agents.py         # AI agent logic and request routing
├── index.py          # FastAPI server and main application  
├── tools.py          # External tools (weather API, LLM interface)
└── agents.js         # JavaScript client example

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

## LLM configuration

The agent uses Meta Llama-3.1 with the following template format:

```
<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a helpful AI assistant.<|eot_id|><|start_header_id|>user<|end_header_id|>

{user_message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
```

### Models

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

### Example weather query flow

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

```bash
# Test individual components
python test_components.py

# Test API endpoints
./test_api.sh

# Test full integration (AI Agent + Open WebUI)
./test-integration.sh

# Test via web interface
# 1. Open http://localhost:3000
# 2. Try: "What's the temperature in Tokyo?"
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

### Issues

1. **Open WebUI can't connect to AI Agent**
   ```bash
   # Check if AI Agent is running
   curl http://localhost:8000/health
   
   # Restart services
   make full-stack
   ```

2. **Ollama connection error**
   ```bash
   # Check if Ollama is running
   ollama list
   
   # Restart Ollama
   ollama serve
   ```

3. **Weather API issues**
   ```bash
   # Test weather API directly
   curl "https://api.open-meteo.com/v1/forecast?latitude=51.5074&longitude=-0.1278&current_weather=true"
   ```

4. **Docker issues**
   ```bash
   # Check Docker status
   docker ps
   
   # View logs
   ./webui-manage.sh logs
   
   # Restart container
   ./webui-manage.sh restart
   ```

### Performance

- Use async/await for concurrent requests
- Implement response caching
- Use connection pooling for external APIs
- Monitor memory usage and implement garbage collection

### **Production deployment commands**

```bash
# 1. Deploy JavaScript Implementation (Recommended)
./deploy-langchain.sh production

# 2. Deploy Python Implementation (when JavaScript unsuitable)
docker-compose --profile python-alternative up -d

# Deploy Both (JavaScript as primary, Python as fallback)  
./deploy-langchain.sh both

# Check deployment status
./deploy-langchain.sh status
```

### **Recommendation for system administrators**

1. **START WITH JAVASCRIPT**: Default choice for new deployments
2. **EVALUATE**: Only consider Python if specific Python ecosystem needs
3. **PERFORMANCE FIRST**: JavaScript provides better resource utilization
4. **CONTAINERIZATION**: JavaScript has simpler, more efficient containers
5. **SCALING**: JavaScript scales more naturally in cloud environments

**Decision**: Choose JavaScript unless you have clear Python specific requirements.

---

## License

This project is open source and available under the MIT License.
