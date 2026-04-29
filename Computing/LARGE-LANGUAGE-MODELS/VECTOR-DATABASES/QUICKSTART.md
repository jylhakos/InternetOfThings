# Quick Start Guide

## Prerequisites

- Python 3.8+ installed
- Virtual environment activated
- Docker (optional, for vector databases and Ollama)

## Setup Steps

### 1. Environment Setup

```bash
# Virtual environment is already created and activated
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file to configure settings
# For quick start, default settings (ChromaDB) work out of the box
```

### 3. Choose Your Vector Database

**Option A: ChromaDB (Easiest - No setup needed)**
- Already configured by default
- No additional installation required

**Option B: Qdrant (Docker)**
```bash
./scripts/setup_vector_db.sh
# Select option 2
```

**Option C: Other databases**
```bash
./scripts/setup_vector_db.sh
# Follow the prompts
```

### 4. Setup LLM Inference (Optional)

For full AI agent functionality:

```bash
./scripts/start_ollama.sh
# Follow the prompts to install and start Ollama
```

Or use mock LLM (automatic fallback if Ollama not available)

### 5. Seed Sample Data

```bash
python scripts/seed_data.py
```

### 6. Start the API Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or with Docker:
```bash
docker-compose -f docker/docker-compose.yml up
```

### 7. Access the API

- **API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Quick Tests

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

### Test 2: Ingest Document
```bash
curl -X POST http://localhost:8000/api/documents/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Vector databases are great for AI applications",
    "metadata": {"source": "test"}
  }'
```

### Test 3: Search
```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are vector databases?",
    "top_k": 3
  }'
```

### Test 4: AI Agent Query
```bash
curl -X POST http://localhost:8000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain vector databases",
    "use_rag": true
  }'
```

## Next Steps

- Read the full README.md for detailed documentation
- Run tests: `pytest tests/ -v`
- Explore the interactive API docs at /docs
- Try different vector databases
- Integrate with your own LLM models

## Troubleshooting

### Service Initialization Errors
- Check that vector database is running (if using Qdrant/Weaviate/Milvus)
- Verify .env configuration
- Check logs for specific error messages

### Ollama Connection Issues
- Verify Ollama is running: `curl http://localhost:11434/api/tags`
- Check OLLAMA_BASE_URL in .env
- Application will use mock LLM if Ollama unavailable

### Import Errors
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

For more help, see the full documentation in README.md
