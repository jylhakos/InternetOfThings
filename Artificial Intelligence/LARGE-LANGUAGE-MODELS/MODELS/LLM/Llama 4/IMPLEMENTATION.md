# **No Framework (Python)**

## Overview

I have successfully updated your Python AI Agent to support Meta Llama 4 Scout while maintaining backward compatibility with Llama 3.x models. The implementation provides advanced tool calling capabilities, extended context window support (10M tokens), and enhanced reasoning through the Mixture-of-Experts architecture.

## Features

### 1. **Llama 4 Scout integration**
- **Native Tool Calling**: Implemented Llama 4's built-in function calling capabilities
- **10M Token Context**: Support for extremely long conversations and document processing
- **MoE Architecture**: Optimized for Llama 4's Mixture-of-Experts design
- **Enhanced Prompt Templates**: Updated to use Llama 4's new prompt format

### 2. **Advanced Tool framework**
- **Weather Tool**: Enhanced with intelligent multi-city support
- **Automatic Tool Detection**: Llama 4 automatically determines when to call tools
- **Tool Result Processing**: Seamless integration of tool responses back into conversations
- **Extensible Architecture**: Easy to add new tools without framework dependencies

### 3. **Backward compatibility**
- **Legacy Support**: Full compatibility with Llama 3.x models
- **Automatic Detection**: System automatically detects model type and adjusts behavior
- **Graceful Fallback**: Falls back to traditional processing for older models

### 4. **No Framework approach**
- **Pure Python**: No commercial frameworks (LlamaIndex, LangChain) required
- **Lightweight Dependencies**: Only essential libraries (FastAPI, httpx, pydantic)
- **Custom Implementation**: Full control over agent behavior and tool calling

## Technical details

### Components

#### 1. **LLMTool Class (`src/tools.py`)**
```python
class LLMTool:
    def __init__(self, base_url, model="llama4:scout"):
        self.is_llama4 = "llama4" in model.lower()
        # Automatic model detection and configuration
        
    def _create_llama4_prompt(self, user_message, system_message, tools):
        # Llama 4 specific prompt formatting with tool definitions
        
    async def _handle_tool_calls(self, response_text, original_message):
        # Process tool calls from Llama 4 response
```

#### 2. **ToolManager Class enhancement**
```python
async def _process_with_llama4(self, message, temperature):
    # Enhanced processing for Llama 4 with native tool calling
    # Automatically handles multi-tool scenarios
```

#### 3. **AIAgent Class updates**
```python
def __init__(self, ollama_model="llama4:scout"):
    self.is_llama4 = "llama4" in ollama_model.lower()
    # Enhanced metadata and capabilities reporting
```

### Prompt Template

#### Llama 4 Scout format
```
<|begin_of_text|><|header_start|>system<|header_end|>

{system_message}

Available tools:
- get_weather(city, metric): Get weather information

<|eot|><|header_start|>user<|header_end|>

{user_message}<|eot|><|header_start|>assistant<|header_end|>

[get_weather(city="London", metric="celsius")]<|eot|><|header_start|>ipython<|header_end|>

[{"response": "London: 18°C, partly cloudy"}]<|eot|><|header_start|>assistant<|header_end|>

The current weather in London is 18°C with partly cloudy conditions.
```

#### Legacy Llama 3.x format (Backward compatibility)
```
<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a helpful AI assistant.<|eot_id|><|start_header_id|>user<|end_header_id|>

{user_message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
```

### Tool Calling framework

#### Weather Tool
```python
async def get_temperature(self, city_name: str) -> Optional[str]:
    # Enhanced with better error handling and response formatting
    # Uses Open-Meteo API with coordinates-based queries
    
    # 1. Get coordinates from city name
    coords = await self.get_coordinates(city_name)
    
    # 2. Query weather API with latitude/longitude
    weather = await self.get_weather(coords["latitude"], coords["longitude"])
    
    # 3. Format comprehensive response
    return formatted_weather_response
```

## File structure

### Python architecture

The project now maintains a clean Python-only structure with no JavaScript dependencies:

```
src/
├── agents.py     # AI Agent orchestration and OpenAI-compatible API
├── index.py      # FastAPI server and main application
└── tools.py      # LLM integration and tool framework

Root Directory:
├── requirements.txt     # Python dependencies only
├── setup-llama4.sh     # Automated setup script
├── run.py              # Simple Python runner
├── test-llama4.py      # Comprehensive test suite
└── README.md           # Updated documentation
```

### Files

1. **`src/tools.py`** - Core tool and LLM integration
   - Added Llama 4 Scout support
   - Implemented native tool calling
   - Enhanced weather tool with better API integration
   - Added backward compatibility for Llama 3.x

2. **`src/agents.py`** - AI Agent orchestration  
   - Updated for Llama 4 Scout integration
   - Enhanced metadata reporting
   - Added model capability detection

3. **`src/index.py`** - FastAPI server
   - Updated default model to Llama 4 Scout
   - Enhanced health check reporting
   - Added model-specific metadata

4. **`README.md`** - Updated documentation
   - Llama 4 Scout installation instructions
   - Enhanced feature descriptions
   - Updated architecture diagrams

5. **`requirements.txt`** - Dependencies
   - Updated with enhanced dependency documentation
   - Added development and testing packages

### Files created

1. **`setup-llama4.sh`** - Automated setup script
   - Intelligent model detection and installation
   - Fallback to quantized or legacy models
   - Complete environment setup

2. **`test-llama4.py`** - Comprehensive test suite
   - Tests both Llama 4 and legacy models
   - Validates tool calling functionality
   - Performance and capability testing

3. **`run.py`** - Simple Python runner
   - Development server without Docker
   - Automatic model detection
   - Environment validation

4. **`LLAMA4.md`** - Comprehensive documentation
   - Detailed implementation guide
   - API reference and examples
   - Troubleshooting and best practices

## Usage

### 1. **Basic setup and running**
```bash
# Automated setup
./setup-llama4.sh

# Run the agent
python run.py
# OR
./start-simple.sh
```

### 2. **API usage with Llama 4**
```bash
# Test health check
curl http://localhost:8000/health

# Test weather with tool calling
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "What is the weather in London and Paris?"}],
    "temperature": 0.7
  }'
```

### 3. **Multi-city weather query**
```bash
# Llama 4 automatically handles multiple cities
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Compare weather in Tokyo, New York, and London"}]
  }'
```

## Advantages

### 1. **No Framework dependencies**
- **Pure Python Implementation**: No commercial frameworks required
- **Lightweight**: Minimal dependencies, maximum control
- **Customizable**: Full control over agent behavior and responses

### 2. **Llama 4**
- **10M Token Context**: Handle extremely long conversations and documents
- **Native Tool Calling**: No prompt engineering required for function calls
- **MoE**: Efficient processing through specialized experts
- **Reasoning**: Superior problem-solving capabilities

### 3. **Production**
- **Async/Await**: Full asynchronous support for concurrent requests
- **FastAPI integration**: High-performance REST API with OpenAI compatibility
- **Docker**: Containerized deployment options
- **Health monitoring**: Comprehensive health checks and monitoring

### 4. **Architecture**
- **Model agnostic**: Works with Llama 4 Scout, quantized versions, and legacy models
- **Tool**: Easy to add new tools and capabilities
- **Cloud**: Supports both local and cloud deployments

## Performance

### Memory requirements
- **Llama 4 Scout (Full)**: ~40GB VRAM, 64GB RAM
- **Llama 4 Scout (INT4)**: ~10-12GB VRAM, 32GB RAM
- **Llama 3.1 fallback**: ~5-8GB VRAM, 16GB RAM

### Context Window
- **Llama 4 Scout**: 10 million tokens
- **Llama 3.1**: 4,096-8,192 tokens

### Tool Calling performance
- **Llama 4**: Native function calling, single inference pass
- **Legacy**: Pattern matching and multiple API calls
