# Setup: Redis Queue + FastAPI + LangChain + Ollama

This document describes the Redis Queue + FastAPI + LangChain + Ollama system.

> **Documentation**: See [README.md](README.md) for detailed architecture and usage  
> **Open WebUI setup**: See [OPEN_WEBUI.md](OPEN_WEBUI.md) for web interface installation  
> **API testing**: See [API.md](API.md) for cURL examples and validation


## Automatic setup

1. **Clone or navigate to the project directory**:
   ```bash
   cd "/home/laptop/EXERCISES/IOT/InternetOfThings/Concurrency/Python/Redis Queue"
   ```

2. **Run the setup script**:
   ```bash
   ./start.sh setup
   ```

3. **Start all services**:
   ```bash
   ./start.sh start
   ```

4. **Test the system**:
   ```bash
   ./start.sh test
   ```

## Manual setup (Step by step)

### 1. Install dependencies

```bash
# Update system
sudo apt update

# Install Python and Node.js
sudo apt install python3 python3-venv python3-pip nodejs npm

# Install Redis
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify Redis
redis-cli ping  # Should return "PONG"
```

### 2. Install Ollama

**Option A: Direct installation**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve &
ollama pull llama3.2:1b  # or your preferred model
```

**Option B: Docker installation**
```bash
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
docker exec -it ollama ollama pull llama3.2:1b
```

### 3. Setup Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 4. Setup Node.js environment

```bash
# Install Node.js dependencies
npm install
```

### 5. Start services (Manually)

**Terminal 1: Redis (if not running as service)**
```bash
redis-server
```

**Terminal 2: Ollama (if not running as service)**
```bash
ollama serve
```

**Terminal 3: LangChain.js Service**
```bash
npm start
```

**Terminal 4: RQ Worker**
```bash
source venv/bin/activate
python worker.py
```

**Terminal 5: FastAPI Server**
```bash
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Verification

1. **Check service health**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Test with curl**:
   ```bash
   # Submit a question
   curl -X POST "http://localhost:8000/generate_async/" \
        -H "Content-Type: application/json" \
        -d '{"question": "What is the capital of France?"}'
   
   # Get result (replace JOB_ID with actual job ID)
   curl "http://localhost:8000/get_result/JOB_ID"
   ```

3. **Use the interactive test client**:
   ```bash
   python test_client.py
   ```

## Docker Setup (Alternative)

If you prefer using Docker:

1. **Build and start with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

2. **Check logs**:
   ```bash
   docker-compose logs -f
   ```

3. **Stop services**:
   ```bash
   docker-compose down
   ```

## Issues

### Redis connection issues
```bash
# Check if Redis is running
sudo systemctl status redis-server

# Start Redis if not running
sudo systemctl start redis-server
```

### Ollama not responding
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
pkill ollama
ollama serve &
```

### Port conflicts
```bash
# Check what's using a port
sudo lsof -i :8000  # Replace 8000 with the port number

# Kill process using a port
sudo kill -9 PID  # Replace PID with actual process ID
```

### Node.js dependencies
```bash
# Clear npm cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Python dependencies
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## API Endpoints

Once running, these endpoints are available:

- **FastAPI Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Submit Question**: POST http://localhost:8000/generate_async/
- **Get Result**: GET http://localhost:8000/get_result/{job_id}
- **Job Status**: GET http://localhost:8000/job_status/{job_id}
- **Queue Info**: GET http://localhost:8000/queue_info

## Next

1. Explore the prompt templates example:
   ```bash
   python prompt_templates_example.py explain
   ```

2. Run batch tests:
   ```bash
   python test_client.py batch
   ```

3. Check out the full README.md for detailed architecture information.
