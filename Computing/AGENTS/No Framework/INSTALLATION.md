# Setup: AI Agent + Open WebUI on Debian Linux

This document provides step-by-step instructions to set up the complete stack on a Debian Linux system.

## System requirements

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

### Step 2: install Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service (in a new terminal or background)
ollama serve &

# Wait a moment for Ollama to start, then pull the model
sleep 5
ollama pull llama3.1:8b-instruct-q4_0

# Verify installation
ollama list
```

### Step 3: setup AI Agent

```bash
# Clone or navigate to your project directory
cd "/home/$USER/EXERCISES/IOT/InternetOfThings/Artificial Intelligence/AGENTS/No Framework"

# Run the AI agent setup
./setup.sh

# Activate virtual environment
source venv/bin/activate

# Test the AI agent
python test_components.py
```

### Step 4: setup Open WebUI

```bash
# Setup Open WebUI with Docker
./setup-webui.sh
```

### Step 5: Start services

```bash
# Option 1: Use the Makefile (recommended)
make full-stack

# Option 2: Start manually
# Terminal 1 - Start Ollama (if not already running)
ollama serve

# Terminal 2 - Start AI Agent
source venv/bin/activate
python src/index.py

# Terminal 3 - Start Open WebUI
./webui-manage.sh start
```

### Step 6: Verify installation

```bash
# Run integration tests
./test-integration.sh

# Check service health
make webui-health
```

## Service URLs

After successful setup:

- **Open WebUI**: http://localhost:3000
- **AI Agent API**: http://localhost:8000
- **Ollama API**: http://localhost:11434

## First-time usage

### 1. Access Open WebUI

1. Open browser and go to `http://localhost:3000`
2. Create an admin account (first user becomes admin)
3. Log in to the interface

### 2. Test the integration

Try these test queries in Open WebUI:

1. **Greeting**: "Hello, how are you today?"
2. **Weather**: "What's the temperature in London?"
3. **General**: "Explain machine learning in simple terms"

### 3. Verify weather functionality

Test weather queries for different cities:
- "What's the temperature in Tokyo?"
- "How's the weather in Paris right now?"
- "Tell me about the climate in New York"

## Troubleshooting

### Issues and solutions

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
