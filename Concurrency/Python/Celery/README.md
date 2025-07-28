# FastAPI + Celery + LangChain.js + Ollama Integration

This project demonstrates how to build a scalable asynchronous system using FastAPI as an API gateway, Celery for task management, LangChain.js for LLM interactions, and Ollama for hosting LLM models.

## Architecture

```
Client → FastAPI → Celery → LangChain.js → Ollama (LLM)
   ↑        ↓        ↓          ↓           ↓
   └── Response ← Result ← Task ← HTTP ← Inference
```

### Components
1. **FastAPI**: RESTful API gateway for client requests
2. **Celery**: Asynchronous task queue for background processing
3. **Redis**: Message broker for Celery tasks
4. **LangChain.js**: JavaScript framework for LLM interactions
5. **Ollama**: Local LLM server hosting models like Llama

## What is Celery?

Celery is a distributed task queue for Python that allows you to run time-consuming tasks asynchronously. It's particularly useful for:

- **Background Processing**: Execute long-running tasks without blocking the main application
- **Scalability**: Distribute tasks across multiple worker processes/machines
- **Reliability**: Automatic retries, task routing, and monitoring
- **Flexibility**: Support for various message brokers (Redis, RabbitMQ, etc.)

### Celery concepts

1. **Tasks**: Functions decorated with `@celery.task` that can be executed asynchronously
2. **Workers**: Processes that execute tasks
3. **Broker**: Message queue system (Redis/RabbitMQ) that stores task messages
4. **Backend**: Storage for task results (Redis, databases, etc.)

## Setup

### 1. Python Virtual Environment setup (Linux/Debian)

First, ensure Python is installed and create a virtual environment:

```bash
# Update package list
sudo apt update

# Install Python and pip if not already installed
sudo apt install python3 python3-pip python3-venv

# Create project directory
mkdir -p ~/projects/llm-celery-api
cd ~/projects/llm-celery-api

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 2. Install Python dependencies

```bash
# Install required packages
pip install fastapi uvicorn celery redis python-multipart requests python-dotenv

# Create requirements.txt
pip freeze > requirements.txt
```

### 3. Redis installation (Message Broker)

```bash
# Install Redis server
sudo apt install redis-server

# Start Redis service
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis connection
redis-cli ping
```

### 4. Node.js and LangChain.js setup

```bash
# Install Node.js (if not already installed)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Create Node.js project directory
mkdir langchain-service
cd langchain-service

# Initialize Node.js project
npm init -y

# Install LangChain and dependencies
npm install langchain @langchain/community express cors dotenv
npm install @langchain/ollama

# Create package.json scripts
```

### 5. Ollama installation

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model (e.g., Llama 3.1)
ollama pull llama3.1

# Start Ollama server (runs on localhost:11434)
ollama serve
```

## Project

```
.
├── README.md
├── SETUP.md                 # Setup and quick start guide
├── API.md          # API usage examples
├── DEPLOYMENT.md            # Production deployment guide
├── requirements.txt
├── setup.sh                 # Automated setup script
├── start_dev.sh             # Development startup script
├── test_system.py           # System testing script
├── .env
├── .gitignore
├── docker-compose.yml
├── python-app/
│   ├── Dockerfile
│   ├── main.py              # FastAPI application
│   ├── celery_app.py        # Celery configuration
│   ├── tasks.py             # Celery tasks
│   └── config.py            # Configuration settings
├── langchain-service/
│   ├── Dockerfile
│   ├── package.json
│   ├── server.js            # Express.js server
│   ├── llm_service.js       # LangChain integration
│   └── prompt_templates.js  # Prompt templates
└── docker/
    └── redis/
        └── redis.conf
```

## How Asynchronous Tasks work with Celery

### 1. Task definition
```python
from celery import Celery

app = Celery('llm_tasks')

@app.task
def process_llm_request(prompt, model_name="llama3.1"):
    # This function runs asynchronously
    # Call to LangChain.js service
    return result
```

### 2. Task execution flow

1. **Client Request**: Client sends request to FastAPI endpoint
2. **Task Dispatch**: FastAPI creates a Celery task and returns task ID immediately
3. **Background Processing**: Celery worker picks up the task
4. **LLM Processing**: Worker calls LangChain.js service → Ollama
5. **Result Storage**: Task result is stored in Redis backend
6. **Result Retrieval**: Client polls for result using task ID

### 3. Benefits

- **Non-blocking**: API remains responsive during LLM processing
- **Scalable**: Multiple workers can handle concurrent requests
- **Fault-tolerant**: Tasks can be retried on failure
- **Monitorable**: Task status and progress tracking

## Prompt Templates

Prompt templates in LangChain provide structured ways to format inputs for LLMs:

```javascript
const promptTemplate = new PromptTemplate({
  template: "You are a helpful assistant. Question: {question}\nAnswer:",
  inputVariables: ["question"]
});
```

### Template features
- **Variable Substitution**: Dynamic content insertion
- **Consistency**: Standardized prompt formats
- **Reusability**: Template sharing across different contexts
- **Validation**: Input variable checking

## API Endpoints

### FastAPI Endpoints

1. `POST /chat` - Submit chat request
2. `GET /task/{task_id}` - Check task status
3. `GET /health` - Health check
4. `GET /models` - List available models

### LangChain.js service Endpoints

1. `POST /generate` - Generate LLM response
2. `GET /models` - Available models
3. `GET /health` - Service health

## Running the application

### Development mode

```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Ollama
ollama serve

# Terminal 3: Start LangChain.js service
cd langchain-service
npm start

# Terminal 4: Start Celery worker
cd python-app
celery -A celery_app worker --loglevel=info

# Terminal 5: Start FastAPI
cd python-app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production mode (Docker)

```bash
# Build and start all services
docker-compose up --build

# Scale workers
docker-compose up --scale celery-worker=3
```

## Docker deployment

The project includes Docker configuration for production deployment:

- **FastAPI**: Python web server
- **Celery Workers**: Background task processors
- **Redis**: Message broker and result backend
- **LangChain.js**: Node.js LLM service
- **Ollama**: LLM model server
- **Open WebUI**: Web interface for chat

## Environment variables

Create a `.env` file with:

```
REDIS_URL=redis://localhost:6379/0
OLLAMA_URL=http://localhost:11434
LANGCHAIN_SERVICE_URL=http://localhost:3000
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## Monitoring and logging

- **Celery Flower**: Web-based monitoring tool
- **FastAPI Docs**: Automatic API documentation at `/docs`
- **Health Checks**: Built-in health monitoring endpoints

## Integration with Open WebUI

The system provides OpenAI-compatible APIs that can be integrated with Open WebUI for a chat interface, allowing users to interact with local LLM models through a familiar chat interface.

### References

[Introduction to Celery](https://docs.celeryq.dev/en/latest/getting-started/introduction.html)
