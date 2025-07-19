# AI Agent - No Framework

A Python based AI agent implementation without commercial frameworks like LlamaIndex or open-source frameworks like LangChain. This AIagent uses Meta Llama-3.1 (quantized) for LLM capabilities and provides RESTful API services with **Open WebUI integration**.

## Features

- **No Framework**: Python implementation using only standard libraries and lightweight dependencies
- **LLM integration**: Uses Meta Llama-3.1 quantized models (4-bit/8-bit) via Ollama
- **Weather service**: Integrates with Open-Meteo API for weather queries
- **RESTful API**: FastAPI-based web service with OpenAI-compatible responses
- **Web interface**: Open WebUI integration for browser-based interaction
- **Asynchronous**: Supports concurrent requests using async/await
- **Memory**: Requires <12GB GPU VRAM and <32GB RAM

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Open WebUI    │    │  AI Agent API   │    │     Ollama      │
│  (Port: 3000)   │────│  (Port: 8000)   │────│  (Port: 11434)  │
│   Docker        │    │    FastAPI      │    │   Llama-3.1     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                │
                       ┌─────────────────┐
                       │  Weather API    │
                       │  (Open-Meteo)   │
                       └─────────────────┘
```

## System requirements

- Python 3.12 or compatible version
- GPU with <12GB VRAM (for quantized Llama-3.1)
- <32GB RAM
- Linux (Debian) environment

## Options

### Option 1: Full stack with web interface (Recommended)

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
- 🌐 **Web Interface**: http://localhost:3000 (Open WebUI)
- 🤖 **API**: http://localhost:8000 (AI Agent)

### Option 2: API only

```bash
# Setup and start AI Agent only
./setup.sh
source venv/bin/activate
python src/index.py
```

### Option 3: Using makefile commands

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

#### Chat Completion (OpenAI API compatible)
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

## LLM Configuration

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

- 📖 **[INSTALLATION.md](INSTALLATION.md)** - Complete setup guide for Debian Linux
- 🐳 **[DOCKER.md](DOCKER.md)** - Detailed Docker configuration
- 💡 **[EXAMPLES.md](EXAMPLES.md)** - Usage examples and API references

## Troubleshooting

### Issues

1. **Open WebUI can't connect to AI Agent**
   ```bash
   # Check if AI Agent is running
   curl http://localhost:8000/health
   
   # Restart services
   make full-stack
   ```

2. **Ollama connection**
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

### Performance optimization

- Use async/await for concurrent requests
- Implement response caching
- Use connection pooling for external APIs
- Monitor memory usage and implement garbage collection

## Contributing

1. Follow Python PEP 8 style guidelines
2. Add type hints to all functions
3. Write comprehensive docstrings
4. Test with multiple concurrent requests
5. Ensure compatibility with Python 3.12

## License

This project is open source and available under the MIT License.

