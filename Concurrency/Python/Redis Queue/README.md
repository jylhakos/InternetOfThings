# Redis Queue (RQ) with FastAPI, LangChain, and Ollama

The application demonstrates RESTful API usage with asynchronous processing using Redis Queue (RQ) with FastAPI, LangChain.js, and Ollama for LLM-powered responses.

## Project

This project showcases how to build a scalable asynchronous system that offloads computationally intensive LLM inference to background workers, ensuring a responsive user experience. The system uses Redis Queue for task management and integrates with Ollama for local LLM processing.

## Architecture

1. **User Request**: A user sends a request to the FastAPI endpoint (`POST /chat`)
2. **Task Enqueuing**: FastAPI enqueues the Ollama interaction task to Redis using RQ and immediately returns a `task_id`
3. **Background Processing**: An RQ worker picks up the task from the queue and executes the `process_ollama_request` function
4. **LLM Interaction**: The worker interacts with Ollama via LangChain.js and stores the result in Redis
5. **Result Retrieval**: The user polls the `GET /task/{task_id}` endpoint to retrieve the completed result

## Pre-requisites

### 1. Python Virtual Environment

```bash
# Install Python virtual environment
sudo apt update
sudo apt install python3 python3-venv python3-pip

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install fastapi uvicorn redis rq requests python-dotenv
```

### 2. Redis

```bash
# Install Redis
sudo apt install redis-server

# Start Redis service
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify Redis is running
redis-cli ping
```

### 3. Ollama

#### Option A: Native installation
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull Llama model (example)
ollama pull llama3.2:1b
```

#### Option B: Docker installation
```bash
# Run Ollama in Docker
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama

# Pull model in Docker
docker exec -it ollama ollama pull llama3.2:1b
```

### 4. Node.js and LangChain.js setup

```bash
# Install Node.js (if not already installed)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Initialize Node.js project
npm init -y

# Install LangChain.js dependencies
npm install langchain @langchain/community @langchain/ollama express cors dotenv
```

## Components

### FastAPI server (Python)
- **Endpoint**: `POST /chat` - Submit chat requests for asynchronous processing
- **Endpoint**: `GET /task/{task_id}` - Check task status and retrieve results
- **Endpoint**: `GET /health` - System health check with detailed information
- **Endpoint**: `GET /models` - List available models with descriptions
- **Endpoint**: `POST /v1/chat/completions` - OpenAI-compatible chat endpoint for Open WebUI
- **Endpoint**: `GET /v1/models` - OpenAI-compatible models list for Open WebUI

### RQ Worker (Python)
- Connects to Redis instance and listens for jobs
- Executes background tasks by calling LangChain.js processes
- Stores results in Redis for retrieval

### LangChain.js Process (JavaScript)
- Utilizes `@langchain/ollama` to interact with local Ollama server
- Processes prompts using predefined templates
- Returns LLM responses to the Python worker

### Prompt Templates
Prompt templates provide pre-defined structures for creating consistent prompts sent to LLMs:

```javascript
const promptTemplate = PromptTemplate.fromTemplate(
  "You are a helpful assistant. Answer the following question: {question}"
);
```

## How RQ works for Q&A Chat?

1. **Request Reception**: FastAPI receives a question from the client
2. **Job Creation**: A job containing the question is created and added to the Redis queue
3. **Worker Processing**: An RQ worker picks up the job and processes it asynchronously
4. **LLM Inference**: The worker calls the LangChain.js script which interacts with Ollama
5. **Response Storage**: The LLM response is stored in Redis with the job ID
6. **Result Retrieval**: Client can poll for results using the job ID

## Installation

1. **Clone and setup environment**
   ```bash
   # Navigate to project directory
   cd "/home/laptop/EXERCISES/IOT/InternetOfThings/Concurrency/Python/Redis Queue"
   
   # Activate virtual environment
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   # Python dependencies
   pip install -r requirements.txt
   
   # JavaScript dependencies
   npm install
   ```

3. **Start services**
   ```bash
   # Terminal 1: Start Redis (if not running as service)
   redis-server
   
   # Terminal 2: Start Ollama (if not running as service)
   ollama serve
   
   # Terminal 3: Start RQ Worker
   python worker.py
   
   # Terminal 4: Start FastAPI Server
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   
   # Terminal 5: Start LangChain.js Service (optional HTTP server)
   node langchain_service.js
   ```

## API Endpoints

### POST `/generate_async/`
Enqueue a new LLM processing job.

**Request Body**:
```json
{
  "question": "What is the capital of France?",
  "model": "llama3.2:1b"
}
```

**Response**:
```json
{
  "job_id": "uuid-string",
  "status": "queued",
  "message": "Your request is being processed"
}
```

### GET `/get_result/{job_id}`
Retrieve the result of a processed job.

**Response** (Success):
```json
{
  "job_id": "uuid-string",
  "status": "finished",
  "result": "The capital of France is Paris.",
  "processing_time": 2.34
}
```

**Response** (In Progress):
```json
{
  "job_id": "uuid-string",
  "status": "started",
  "message": "Job is still processing"
}
```

### GET `/job_status/{job_id}`
Get current status of a job.

**Response**:
```json
{
  "job_id": "uuid-string",
  "status": "started",
  "progress": "Processing with Ollama..."
}
```

## Asynchronous data flow

```
Client Request
     ↓
FastAPI Endpoint (/generate_async/)
     ↓
RQ Job Enqueue (Redis)
     ↓
Return job_id to Client
     ↓
RQ Worker picks up job
     ↓
Worker calls LangChain.js process
     ↓
LangChain.js → Ollama → LLM Response
     ↓
Worker stores result in Redis
     ↓
Client polls /get_result/{job_id}
     ↓
Return final result
```

## Configuration

Create a `.env` file for environment variables:

```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
OLLAMA_HOST=http://localhost:11434
DEFAULT_MODEL=llama3.2:1b
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
LANGCHAIN_SERVICE_PORT=3000
```

## Open WebUI integration

Open WebUI provides a user-friendly web interface for interacting with the LLM system. This section covers how to integrate Open WebUI with our Redis Queue system.

> 📖 **Quick Start Guide**: For a streamlined setup process, see [OPEN_WEBUI.md](OPEN_WEBUI.md) for step-by-step instructions.

### Setting up Open WebUI with Docker

Open WebUI can be configured to use our FastAPI backend as a custom OpenAI-compatible API endpoint.

#### Option 1: Docker run command
```bash
# Run Open WebUI with custom API endpoint
docker run -d \
  --name open-webui \
  -p 3001:8080 \
  -e OPENAI_API_BASE_URL="http://host.docker.internal:8000/v1" \
  -e OPENAI_API_KEY="dummy-key" \
  -v open-webui:/app/backend/data \
  --add-host=host.docker.internal:host-gateway \
  ghcr.io/open-webui/open-webui:main
```

#### Option 2: Docker Compose
Add this service to your existing `docker-compose.yml`:

```yaml
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: rq-open-webui
    ports:
      - "3001:8080"
    environment:
      - OPENAI_API_BASE_URL=http://fastapi:8000/v1
      - OPENAI_API_KEY=dummy-key
      - WEBUI_SECRET_KEY=your-secret-key
    volumes:
      - open-webui:/app/backend/data
    depends_on:
      - fastapi
    networks:
      - rq-network
    restart: unless-stopped
```

### OpenAI compatible API Endpoints

To make our FastAPI server compatible with OpenAI's API format, we need to add OpenAI-compatible endpoints:

- `GET /v1/models` - List available models
- `POST /v1/chat/completions` - Chat completions endpoint
- `POST /v1/completions` - Text completions endpoint

### Using Open WebUI with Prompt Templates

Once Open WebUI is running, you can access it at `http://localhost:3001` and configure it to use different prompt templates:

#### 1. System Prompts for different use cases

**Technical Assistant:**
```
You are a technical expert assistant. Provide detailed, accurate technical responses with examples and explanations. Focus on clarity and practical implementation details.
```

**Creative Writer:**
```
You are a creative writing assistant. Generate imaginative, engaging content with rich descriptions and creative flair. Feel free to be expressive and artistic in your responses.
```

**Chat Assistant:**
```
You are a helpful, friendly AI assistant. Provide conversational, approachable responses while being informative and supportive. Keep a warm, professional tone.
```

#### 2. Custom model parameters

In Open WebUI, you can configure:
- **Temperature**: 0.1-1.0 (creativity level)
- **Max Tokens**: 100-2000 (response length)
- **Top P**: 0.1-1.0 (nucleus sampling)
- **Frequency Penalty**: -2.0 to 2.0 (repetition control)

### Test Cases for Open WebUI

#### Q&A
1. **Prompt**: "What is the capital of France?"
2. **Expected**: Clear, factual answer about Paris
3. **Template**: Default/Chat

#### Query
1. **Prompt**: "Explain how Redis Queue works in a distributed system"
2. **Expected**: Detailed technical explanation with examples
3. **Template**: Technical

#### Writing
1. **Prompt**: "Write a short story about an AI learning to paint"
2. **Expected**: Creative narrative with descriptive language
3. **Template**: Creative

#### Problem solving
1. **Prompt**: "How would you design a scalable microservices architecture for an e-commerce platform?"
2. **Expected**: Structured, comprehensive solution
3. **Template**: Technical

### Equivalent cURL commands

For comparison, here are the equivalent cURL commands for the same tests:

#### Q&A test
```bash
# Submit question
curl -X POST "http://localhost:8000/generate_async/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the capital of France?",
    "model": "llama3.2:1b",
    "temperature": 0.7
  }'

# Get result (replace JOB_ID with actual ID)
curl "http://localhost:8000/get_result/JOB_ID"
```

#### Query test
```bash
curl -X POST "http://localhost:8000/generate_async/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain how Redis Queue works in a distributed system",
    "model": "llama3.2:1b",
    "temperature": 0.3
  }'
```

#### OpenAI compatible format (for Open WebUI)
```bash
# Chat completions format
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dummy-key" \
  -d '{
    "model": "llama3.2:1b",
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful assistant."
      },
      {
        "role": "user",
        "content": "What is the capital of France?"
      }
    ],
    "temperature": 0.7,
    "max_tokens": 500
  }'
```

### Running Open WebUI

1. **Start the main system**:
   ```bash
   ./start.sh start
   ```

2. **Start Open WebUI**:
   ```bash
   # Using Docker run
   docker run -d \
     --name open-webui \
     -p 3001:8080 \
     -e OPENAI_API_BASE_URL="http://host.docker.internal:8000/v1" \
     -e OPENAI_API_KEY="dummy-key" \
     -v open-webui:/app/backend/data \
     --add-host=host.docker.internal:host-gateway \
     ghcr.io/open-webui/open-webui:main

   # Or using Docker Compose (if added to compose file)
   docker-compose up -d open-webui
   ```

3. **Access Open WebUI**:
   - Open browser to `http://localhost:3001`
   - Create an account (first user becomes admin)
   - Configure the API endpoint if needed

4. **Configure Models**:
   - Go to Settings → Models
   - Add custom model: `llama3.2:1b`
   - Set API base URL: `http://host.docker.internal:8000/v1`

### Advanced Open WebUI features

#### Model management
- Switch between different Ollama models
- Configure model-specific parameters
- Set default models for different use cases

#### Conversation management
- Save important conversations
- Export chat history
- Share conversations with team members

#### Custom functions
Open WebUI supports custom functions that can integrate with our Redis Queue system:

```python
# Example custom function for Open WebUI
def get_queue_status():
    """Get current Redis Queue status"""
    import requests
    try:
        response = requests.get("http://localhost:8000/queue_info")
        return response.json()
    except Exception as e:
        return {"error": str(e)}
```

### Monitoring and analytics

Open WebUI provides built-in analytics for:
- Response times
- Token usage
- Model performance
- User interaction patterns

This data can help optimize your Redis Queue system performance.

### Troubleshooting Open WebUI

#### Issues:

1. **Cannot connect to API**:
   - Check if FastAPI server is running on port 8000
   - Verify the API base URL configuration
   - Ensure Docker network connectivity

2. **Models not loading**:
   - Verify Ollama is running and models are pulled
   - Check the `/v1/models` endpoint response
   - Restart Open WebUI container

3. **Slow responses**:
   - Monitor Redis Queue length
   - Check RQ worker status
   - Scale up workers if needed

## Testing and validation

### Automated tests

The project includes comprehensive test suites for validation:

#### 1. System tests
```bash
# Test the core Redis Queue system
python test_client.py

# Run batch tests with multiple questions
python test_client.py batch

# Check system health
python test_client.py health
```

#### 2. Open WebUI tests
```bash
# Run comprehensive Open WebUI tests
python open_webui_tests.py

# Test only OpenAI endpoints
python open_webui_tests.py models

# Show equivalent cURL commands
python open_webui_tests.py curl

# Demonstrate prompt templates
python open_webui_tests.py templates
```

#### 3. Prompt Template tests
```bash
# Show all available templates
python prompt_templates_library.py list

# Export configuration for Open WebUI
python prompt_templates_library.py export

# Generate cURL examples
python prompt_templates_library.py curl

# Create test scenarios
python prompt_templates_library.py test
```

### Manual testing

#### Step 1: System Health Check
1. Start all services: `./start.sh start`
2. Check health endpoint: `curl http://localhost:8000/health`
3. Verify queue status: `curl http://localhost:8000/queue_info`

#### Step 2: API Endpoint testing
1. Test basic endpoint:
   ```bash
   curl -X POST "http://localhost:8000/generate_async/" \
     -H "Content-Type: application/json" \
     -d '{"question": "Hello, world!", "model": "llama3.2:1b"}'
   ```

2. Test OpenAI compatibility:
   ```bash
   curl -X GET "http://localhost:8000/v1/models" \
     -H "Authorization: Bearer sk-dummy-key"
   ```

#### Step 3: Open WebUI validation
1. Start Open WebUI: `./open_webui.sh start`
2. Access interface: `http://localhost:3001`
3. Test different prompt templates
4. Verify response quality and timing

### Performance

#### Load testing with multiple concurrent requests
```bash
# Test 10 concurrent requests
for i in {1..10}; do
  curl -X POST "http://localhost:8000/generate_async/" \
    -H "Content-Type: application/json" \
    -d "{\"question\": \"Test request $i\", \"model\": \"llama3.2:1b\"}" &
done
wait
```

#### Queue performance monitoring
```bash
# Monitor queue length over time
watch -n 5 'curl -s http://localhost:8000/queue_info | jq .queue_length'
```

### Integration validation

#### End-to-end workflow
1. Submit question via Open WebUI
2. Monitor job in Redis Queue
3. Verify LangChain.js processing
4. Confirm Ollama interaction
5. Validate response delivery

#### Cross platform testing
- Test on different browsers (Chrome, Firefox, Safari)
- Validate mobile responsiveness
- Check Docker container behavior
- Verify network connectivity across services

### Test data

#### Sample Questions for different Templates
```json
{
  "technical_expert": [
    "Explain microservices architecture patterns",
    "How to implement Redis caching strategies?",
    "What are Docker best practices?"
  ],
  "creative_writer": [
    "Write a story about AI and creativity",
    "Create a poem about programming",
    "Describe a futuristic smart city"
  ],
  "business_analyst": [
    "Analyze AI impact on small businesses",
    "What are key SaaS success metrics?",
    "How to calculate automation ROI?"
  ]
}
```

#### Expected Response characteristics
- **Technical responses**: Detailed, accurate, with examples
- **Creative responses**: Imaginative, descriptive, engaging
- **Business responses**: Strategic, data-driven, actionable

### Continuous integration testing

For production deployment, consider automated testing:

```bash
# Health check script for CI/CD
#!/bin/bash
curl -f http://localhost:8000/health || exit 1
curl -f http://localhost:3001 || exit 1

# Basic functionality test
RESPONSE=$(curl -s -X POST "http://localhost:8000/generate_async/" \
  -H "Content-Type: application/json" \
  -d '{"question": "Test", "model": "llama3.2:1b"}')

JOB_ID=$(echo $RESPONSE | jq -r .job_id)
if [ "$JOB_ID" != "null" ]; then
  echo "✅ Basic functionality test passed"
else
  echo "❌ Basic functionality test failed"
  exit 1
fi
```

## Errors

The system includes comprehensive error handling for:
- Redis connection failures
- Ollama service unavailability
- LangChain.js process errors
- Job timeout handling
- Invalid job IDs
- OpenAI API compatibility issues
- Open WebUI connection problems

## References

- [Redis Queue (RQ)](https://python-rq.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain.js Documentation](https://js.langchain.com/docs/introduction/)
- [Ollama Documentation](https://ollama.ai/docs/)
- [LangChain.js Tutorials](https://js.langchain.com/docs/tutorials/)
- [LLM Chain Tutorial](https://js.langchain.com/docs/tutorials/llm_chain/)
- [Hugging Face Integration](https://python.langchain.com/docs/integrations/providers/huggingface/)

