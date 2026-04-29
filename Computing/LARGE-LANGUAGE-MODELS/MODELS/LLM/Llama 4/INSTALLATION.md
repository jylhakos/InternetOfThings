# Setup: AI Agent + Meta Llama 4 Scout + Open WebUI on Debian Linux

This document provides step-by-step instructions to set up the complete Meta Llama 4 Scout AI Agent stack with Open WebUI on a Debian Linux system.

## Meta Llama 4 Scout overview

**Meta Llama 4 Scout** is the latest generation LLM featuring:
- **10 Million Token Context Window**: Process extremely long documents and conversations
- **Mixture of Experts (MoE) Architecture**: Efficient processing with specialized expert networks
- **Native Tool Calling**: Built-in function calling without complex prompt engineering
- **Enhanced Reasoning**: Advanced logic and problem-solving capabilities
- **Multi-modal Integration**: Support for various data types and formats

This setup guide focuses on Llama 4 Scout as the primary model, with fallback instructions for legacy Llama 3.x models.

## System requirements

### Recommended configuration (Meta Llama 4 Scout)
- **OS**: Debian 11+ or Ubuntu 20.04+ LTS
- **RAM**: 32GB recommended, 16GB minimum
- **GPU**: NVIDIA GPU with 12GB+ VRAM
- **CPU**: Multi-core processor (Intel i7/AMD Ryzen 7+)
- **Disk**: 50GB+ free space (for models and Docker images)
- **Network**: High-speed internet for initial 15-20GB model download

### Minimum configuration (Quantized models)
- **OS**: Debian 11+ or Ubuntu 20.04+
- **RAM**: 16GB minimum, 24GB recommended
- **GPU**: NVIDIA GPU with 8GB+ VRAM or CPU-only mode
- **Disk**: 30GB+ free space
- **Network**: Internet connection required

### Legacy configuration (Llama 3.x fallback)
- **OS**: Debian 11+ or Ubuntu 20.04+
- **RAM**: 8GB minimum, 16GB+ recommended
- **GPU**: NVIDIA GPU with 6GB+ VRAM (for Ollama) or CPU-only mode
- **Disk**: 20GB+ free space
- **Network**: Internet connection required

## Installation

### Step 1: system preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y curl wget git python3 python3-pip python3-venv \
    build-essential software-properties-common apt-transport-https \
    ca-certificates gnupg lsb-release make

# Install Docker
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify Docker installation
docker --version
docker compose version
```

### Step 2: Install Ollama and Meta Llama 4 Scout

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service (in a new terminal or background)
ollama serve &

# Wait a moment for Ollama to start, then pull Meta Llama 4 Scout
# WARNING: This is a large download (15-20GB), ensure good internet connection
ollama pull llama4:scout

# Alternative: Pull quantized version (smaller, ~10GB)
# ollama pull ingu627/llama4-scout-q4

# Verify model installation
ollama list

# Test basic model functionality
ollama run llama4:scout "Hello, please introduce yourself"
```

**Expected output:**
```
NAME              ID             SIZE      MODIFIED
llama4:scout      abc123...      18GB      2 minutes ago
```

#### Fallback: Legacy Llama 3.x models

If your system cannot handle Llama 4 Scout, use these alternatives:

```bash
# Option 1: Llama 3.1 8B (Recommended fallback)
ollama pull llama3.1:8b-instruct-q4_0

# Option 2: Llama 3.1 7B (Lower resource usage)
ollama pull llama3.1:7b-instruct-q4_0

# Option 3: Llama 3.1 8B with higher precision
ollama pull llama3.1:8b-instruct-q8_0

# Test installation
ollama run llama3.1:8b-instruct-q4_0 "Hello, how are you?"
```
sleep 5
ollama pull llama3.1:8b-instruct-q4_0

# Verify installation
ollama list
```

### Step 3: Setup AI Agent with Meta Llama 4 Scout

```bash
# Navigate to your project directory
cd "/home/$USER/EXERCISES/IOT/InternetOfThings/Artificial Intelligence/LARGE-LANGUAGE-MODELS/MODELS/LLM/Llama 4"

# Option 1: Automated setup for Llama 4 Scout (Recommended)
./setup-llama4.sh

# Option 2: Manual setup
./setup.sh

# Activate virtual environment
source venv/bin/activate

# Configure for Meta Llama 4 Scout
export MODEL_NAME="llama4:scout"
export OLLAMA_BASE_URL="http://localhost:11434"

# Test the AI agent components
python test_components.py
```

#### Environment configuration for Meta Llama 4 Scout

Create `.env` file with Llama 4 Scout configuration:

```bash
cat > .env << 'EOF'
# Meta Llama 4 Scout Configuration
MODEL_NAME=llama4:scout
OLLAMA_BASE_URL=http://localhost:11434
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Llama 4 Scout Specific Settings
LLAMA4_CONTEXT_SIZE=10000000
LLAMA4_TOOL_CALLING=true
LLAMA4_MOE_EXPERTS=8

# Weather API Settings
WEATHER_API_BASE_URL=https://api.open-meteo.com/v1
GEOCODING_API_BASE_URL=https://geocoding-api.open-meteo.com/v1
EOF
```

#### Fallback configuration for Legacy Models

If using Llama 3.x models instead:

```bash
cat > .env << 'EOF'
# Legacy Llama 3.x Configuration
MODEL_NAME=llama3.1:8b-instruct-q4_0
OLLAMA_BASE_URL=http://localhost:11434
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Legacy Settings
CONTEXT_SIZE=4096
TOOL_CALLING=false
LEGACY_PROMPT_FORMAT=true
EOF
```

### Step 4: Setup Open WebUI with Meta Llama 4

```bash
# Setup Open WebUI with Docker for Llama 4 Scout
./setup-webui.sh

# Alternative: Manual Docker setup
docker run -d \
  --name open-webui \
  --restart unless-stopped \
  -p 3000:8080 \
  -e OPENAI_API_BASE_URL=http://host.docker.internal:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -e DEFAULT_MODELS=ai-agent-llama4-scout \
  -e WEBUI_NAME="Meta Llama 4 Scout AI Agent" \
  -e ENABLE_SIGNUP=true \
  -e ENABLE_OAUTH_SIGNUP=false \
  -v open-webui:/app/backend/data \
  ghcr.io/open-webui/open-webui:main

# Verify Open WebUI is running
docker ps | grep open-webui
docker logs open-webui
```

#### Open WebUI configuration for Meta Llama 4 Scout

Create Open WebUI configuration file:

```bash
cat > open-webui-config.json << 'EOF'
{
  "WEBUI_NAME": "Meta Llama 4 Scout AI Agent",
  "DEFAULT_MODELS": "ai-agent-llama4-scout",
  "MODEL_FILTER_LIST": ["ai-agent-llama4-scout", "ai-agent-no-framework"],
  "ENABLE_SIGNUP": true,
  "ENABLE_LOGIN_FORM": true,
  "WEBUI_AUTH": true,
  "WEBUI_SESSION_COOKIE_SAME_SITE": "lax",
  "TASK_MODEL": "ai-agent-llama4-scout",
  "TITLE_GENERATION_PROMPT_TEMPLATE": "Create a concise, 3-5 word title for this conversation about: {{prompt}}",
  "TOOLS": {
    "weather": {
      "enabled": true,
      "description": "Get real-time weather information for any city using Meta Llama 4 Scout's tool calling"
    },
    "greeting": {
      "enabled": true,
      "description": "Natural conversation with advanced context understanding"
    }
  },
  "MODELS": {
    "ai-agent-llama4-scout": {
      "name": "Meta Llama 4 Scout",
      "description": "Advanced AI agent with 10M token context, MoE architecture, and native tool calling",
      "capabilities": ["chat", "weather", "tool_calling", "long_context"],
      "context_length": 10000000,
      "temperature": 0.7,
      "top_p": 0.9,
      "max_tokens": 512
    }
  }
}
EOF
```

### Step 5: Start services with Meta Llama 4 Scout

```bash
# Option 1: Use the Makefile (Recommended for Llama 4)
make full-stack-llama4

# Option 2: Use the WebUI management script
./start-webui.sh

# Option 3: Start manually
# Terminal 1 - Start Ollama (if not already running)
ollama serve

# Terminal 2 - Start AI Agent with Llama 4 Scout
source venv/bin/activate
export MODEL_NAME="llama4:scout"
python src/index.py

# Terminal 3 - Start Open WebUI
docker start open-webui
# OR if container doesn't exist:
./webui-manage.sh start
```

**Expected output:**
```
AI Agent Server starting...
Model: llama4:scout
Context Window: 10,000,000 tokens
Tool Calling: Enabled
MoE Experts: Active
Server running on: http://0.0.0.0:8000
Health endpoint: http://localhost:8000/health
```

#### Service start verification

```bash
# Check all services are running
make health-check

# Individual service checks
curl http://localhost:8000/health          # AI Agent
curl http://localhost:3000                 # Open WebUI
curl http://localhost:11434/api/tags       # Ollama

# Check Docker containers
docker ps | grep open-webui
```

### Step 6: Verify Meta Llama 4 Scout installation

```bash
# Run comprehensive integration tests for Llama 4
./test-integration.sh

# Test Llama 4 Scout specific features
./test_api_examples.sh

# Check service health with Llama 4 metadata
make webui-health

# Test tool calling capabilities
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "What is the temperature in London and Paris?"}],
    "temperature": 0.7
  }'
```

**Expected Llama 4 Scout health response:**
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
    "capabilities": ["chat", "weather", "greetings", "tool_calling", "long_context"],
    "context_window": "10M tokens",
    "architecture": "MoE (Mixture of Experts)",
    "tool_calling": "native_support"
  },
  "llama4_features": {
    "context_window": "10M tokens",
    "mixture_of_experts": true,
    "native_tool_calling": true,
    "advanced_reasoning": true,
    "multimodal_ready": true
  }
}
```

## Service URLs

After successful Meta Llama 4 Scout setup:

- **Open WebUI**: http://localhost:3000 (Modern chat interface for Llama 4 Scout)
- **AI Agent API**: http://localhost:8000 (OpenAI-compatible endpoints with Llama 4 features)
- **API Documentation**: http://localhost:8000/docs (FastAPI interactive docs)
- **Health Check**: http://localhost:8000/health (Llama 4 Scout system status)
- **Ollama API**: http://localhost:11434 (Direct LLM access)
- **Ollama Models**: http://localhost:11434/api/tags (Available models)

## First-time Usage with Meta Llama 4 Scout

### 1. Access Open WebUI for Llama 4 Scout

1. **Open browser** and navigate to `http://localhost:3000`
2. **Create admin account** (first user becomes admin)
   - Email: your-email@domain.com (can be fake for local setup)
   - Password: your-secure-password
   - Full Name: Your Name
3. **Log in** to the interface
4. **Select Model**: Choose "ai-agent-llama4-scout" from the model dropdown
5. **Verify Llama 4 Features**: Look for "10M tokens" and "Tool Calling" in the model description

### 2. Test Meta Llama 4 Scout integration

Try these test queries in Open WebUI to verify Llama 4 Scout functionality:

#### **Basic Greeting (Context Window test)**
```
"Hello! I'm testing your Meta Llama 4 Scout capabilities. Can you tell me about your features?"
```

**Expected response:**
> "Hello! I'm powered by Meta Llama 4 Scout with several advanced features:
> - 10 million token context window for processing very long conversations
> - Mixture of Experts architecture for efficient processing
> - Native tool calling capabilities for real-time information
> - Enhanced reasoning and problem-solving abilities
> I'm ready to help with questions, weather information, or complex discussions!"

#### **Weather Tool Calling test (Tool support)**
```
"What's the temperature in London, Tokyo, and New York right now?"
```

**Expected behavior:**
- Llama 4 Scout automatically detects the weather request
- Calls get_weather tools for each city
- Provides consolidated response with current temperatures

#### **Advanced context test (10M Token Window)**
```
"Please remember this conversation for our entire session. Now, what can you tell me about quantum computing?"
```

#### **Multi-turn Tool Calling test**
```
First: "What's the weather in Paris?"
Then: "How does that compare to London?"
Finally: "Which city would be better for outdoor activities today?"
```

### 3. Verify weather tool calling

Test specific weather queries to ensure Llama 4 Scout tool calling works:

#### **Single city query**
- "What's the temperature in Tokyo?"
- "How's the weather in Berlin today?"
- "Is it raining in Seattle right now?"

#### **Multi-city comparisons** 
- "Compare weather in London, Paris, and Rome"
- "Which is warmer: New York or Los Angeles?"
- "What are the temperatures in all major European capitals?"

#### **Contextual weather queries**
- "I'm planning to visit London next week, what's the current weather like?"
- "Should I bring an umbrella to Paris based on today's weather?"
- "Tell me about the climate in New York"

## Troubleshooting

### Issues

#### 1. Docker permission denied

```bash
# Add user to docker group and restart session
sudo usermod -aG docker $USER
newgrp docker
```

#### 2. Ollama connection

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
pkill ollama
ollama serve
```

#### 3. AI Agent not starting

```bash
# Check Python environment
source venv/bin/activate
python --version
pip list

# Check for missing dependencies
pip install -r requirements.txt

# Test components individually
python test_components.py
```

#### 4. Open WebUI connection

```bash
# Check Docker container status
docker ps

# Check logs
./webui-manage.sh logs

# Restart container
./webui-manage.sh restart
```

#### 5. Weather API not working

```bash
# Test weather API directly
curl "https://api.open-meteo.com/v1/forecast?latitude=51.5074&longitude=-0.1278&current_weather=true"

# Check internet connection
ping google.com
```

### Memory and performance

#### For low RAM systems (< 16GB)

```bash
# Use smaller model
ollama pull llama3.1:7b-instruct-q4_0

# Update model in .env
echo "MODEL_NAME=llama3.1:7b-instruct-q4_0" >> .env
```

#### For CPU only systems

```bash
# Ollama will automatically use CPU if no GPU is available
# Performance will be slower but functional

# Monitor resource usage
htop
```

## Maintenance and updates

### Regular

```bash
# Update AI Agent code
git pull

# Update Python dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Update Open WebUI
./webui-manage.sh update

# Update Ollama models
ollama pull llama3.1:8b-instruct-q4_0
```

### Backup and restore

```bash
# Backup Open WebUI data
./webui-manage.sh backup

# Backup AI Agent configuration
cp .env .env.backup
cp -r venv/lib/python*/site-packages/your_custom_modules ./backup/

# Restore from backup
./webui-manage.sh restore backup-file.tar.gz
```

### Logs

```bash
# View AI Agent logs
tail -f logs/agent.log

# View Open WebUI logs
./webui-manage.sh logs

# View Ollama logs
journalctl -u ollama -f
```

## Advanced configuration

### Custom system messages

Edit `src/tools.py` to customize system messages:

```python
# In the LLMTool class
system_message = "You are a helpful AI assistant specialized in weather information and general knowledge. Always be concise and accurate."
```

### API rate limiting

Add rate limiting to `src/index.py`:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@limiter.limit("30/minute")
@app.post("/v1/chat/completions")
async def chat_completions(request: Request, ...):
    # existing code
```

### HTTPS configuration

For production deployment with HTTPS:

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - open-webui
```

## Performance

### For production

1. **Use GPU acceleration** for Ollama
2. **Enable model caching** for faster responses  
3. **Use CDN** for static assets
4. **Implement connection pooling** for database connections
5. **Use reverse proxy** (Nginx) for load balancing

### Monitoring setup

```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Monitor in real-time
watch -n 1 'free -h && echo "---" && df -h && echo "---" && docker stats --no-stream'
```

## Security

### Production

1. **Change default passwords** and API keys
2. **Enable firewall** and restrict ports
3. **Use HTTPS** for all connections
4. **Regular security updates**
5. **Monitor logs** for suspicious activity

```bash
# Basic firewall setup
sudo ufw enable
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw allow 3000  # Open WebUI (restrict as needed)
```
