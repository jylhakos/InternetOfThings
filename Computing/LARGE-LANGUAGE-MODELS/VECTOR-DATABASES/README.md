# Vector Databases

In large language model (LLM) applications, AI agents use vector databases primarily through the Retrieval-Augmented Generation (RAG) framework. Vector databases serve as the external memory for AI agents, allowing them to access and incorporate specific, up-to-date, or proprietary data that was not part of their initial training.

## Table of Contents

1. [What is Vector Search?](#what-is-vector-search)
2. [Open Source Vector Databases](#open-source-vector-databases)
   - [Database Comparison for Agentic Workflows](#database-comparison-for-agentic-workflows)
   - [Weaviate](#weaviate)
   - [Chroma](#chroma)
   - [Qdrant](#qdrant)
   - [Milvus](#milvus)
3. [Vector Databases and Retrieval Augmented Generation (RAG)](#vector-databases-and-retrieval-augmented-generation-rag)
   - [What is RAG?](#what-is-rag)
   - [How Vector Databases Enable RAG](#how-vector-databases-enable-rag)
   - [The RAG Workflow](#the-rag-workflow)
4. [How Tokenizers Work with Vector Databases](#how-tokenizers-work-with-vector-databases)
   - [Tokenization Process](#tokenization-process)
   - [Why Chunking Matters](#why-chunking-matters)
5. [What Are Vector Databases for AI Agents?](#what-are-vector-databases-for-ai-agents)
   - [How AI Agents Use Vector Databases](#how-ai-agents-use-vector-databases)
6. [Project Structure](#project-structure)
7. [Setup and Configuration](#setup-and-configuration)
   - [Prerequisites](#prerequisites)
   - [Environment Setup](#environment-setup)
   - [Vector Database Setup](#vector-database-setup)
   - [Inference Server Setup (Ollama)](#inference-server-setup-ollama)
8. [Running the Application](#running-the-application)
9. [Testing](#testing)
   - [API Testing with CURL](#api-testing-with-curl)
   - [Testing Vector Database](#testing-vector-database)
   - [Testing AI Agent Integration](#testing-ai-agent-integration)
10. [Deployment Options](#deployment-options)
11. [References](#references)

## What is Vector Search?

Vector search is a technique that enables finding similar items by comparing their vector representations in a multi-dimensional space. Unlike traditional keyword-based search, vector search understands semantic meaning and context. It works by converting data (text, images, audio) into numerical vectors using embedding models, then finding items with similar vectors using distance metrics like cosine similarity or Euclidean distance.

For more details, see: [Improve search results with vector search](https://learn.microsoft.com/en-us/training/modules/improve-search-results-vector-search/2-vector-search)

## Open Source Vector Databases

The following open-source vector databases are available with their source code on GitHub:

### Database Comparison for Agentic Workflows

| Database | Best For      | Deployment           | GitHub Repository                                           |
|----------|---------------|----------------------|-------------------------------------------------------------|
| Weaviate | Hybrid Search | Cloud / Self-Hosted  | [weaviate/weaviate](https://github.com/weaviate/weaviate)   |
| Chroma   | Prototyping   | Local / Cloud        | [chroma-core/chroma](https://github.com/chroma-core/chroma) |
| Qdrant   | Performance   | Cloud / Self-Hosted  | [qdrant/qdrant](https://github.com/qdrant/qdrant)           |
| Milvus   | Massive Scale | Cloud / Self-Hosted  | [milvus-io/milvus](https://github.com/milvus-io/milvus)     |

### Weaviate
Weaviate is an open-source vector database that supports both vector search and hybrid search (combining vector and keyword search). It features GraphQL and REST APIs, automatic vectorization, and multi-tenancy support.

**Key Features:**
- Hybrid search capabilities
- Built-in modules for various ML models
- RESTful and GraphQL APIs
- Horizontal scalability

### Chroma
Chroma is a lightweight, easy-to-use vector database designed for prototyping and development. It focuses on simplicity and developer experience, making it ideal for getting started with vector databases.

**Key Features:**
- Simple Python API
- Built-in embedding functions
- Minimal setup required
- Local-first with cloud deployment options

### Qdrant
Qdrant is a high-performance vector database written in Rust, optimized for speed and efficiency. It offers advanced filtering capabilities and is designed for production workloads.

**Key Features:**
- High-performance Rust implementation
- Advanced filtering and payload support
- Distributed deployment support
- HNSW algorithm for fast similarity search

### Milvus
Milvus is a highly scalable vector database designed for massive-scale similarity search and AI applications. It supports multiple index types and can handle billions of vectors.

**Key Features:**
- Built for massive scale
- Multiple index types (FLAT, IVF, HNSW)
- GPU acceleration support
- Distributed architecture

## Vector Databases and Retrieval Augmented Generation (RAG)

### What is RAG?

Retrieval Augmented Generation (RAG) is a technique that enhances Large Language Models (LLMs) by providing them with relevant external information retrieved from a knowledge base. A basic RAG setup includes an embedding model, a vector database, and an LLM. The vector database is used to find the top-K documents that match the query.

### How Vector Databases Enable RAG?

Vector databases play a crucial role in RAG by:

1. **Storing Document Embeddings**: Documents are converted into vector embeddings and stored in the database
2. **Fast Similarity Search**: When a query comes in, the database quickly finds the most semantically similar documents
3. **Context Retrieval**: The top-K most relevant documents are retrieved and provided as context to the LLM
4. **Enhanced Generation**: The LLM uses the retrieved context to generate more accurate and informed responses

### The RAG Workflow

1. **Document Ingestion**: Documents are processed, split into chunks, and converted to embeddings
2. **Storage**: Vector embeddings are stored in the vector database with metadata
3. **Query Processing**: User queries are converted to vectors using the same embedding model
4. **Retrieval**: The vector database finds the most similar document chunks
5. **Generation**: Retrieved context is passed to the LLM to generate a response

For more information on vector databases in generative AI: [The role of vector datastores in generative AI applications](https://aws.amazon.com/blogs/database/the-role-of-vector-datastores-in-generative-ai-applications/)

## How Tokenizers Work with Vector Databases?

### Tokenization Process

When storing document files in vector databases, tokenization is a required step in the embedding pipeline:

1. **Text Extraction**: Documents (PDF, DOCX, TXT, etc.) are parsed to extract raw text
2. **Chunking**: Long documents are split into smaller chunks (e.g., 512 or 1024 tokens) to fit model context windows
3. **Tokenization**: Each text chunk is converted into tokens using a tokenizer
   - Tokens are subword units (words, subwords, or characters)
   - Common tokenizers: BPE (Byte-Pair Encoding), WordPiece, SentencePiece
4. **Embedding Generation**: Tokens are fed into an embedding model (e.g., BERT, sentence-transformers)
5. **Vector Storage**: The resulting vector embeddings are stored in the vector database with references to the original text

### Why Chunking Matters?

- **Context Window Limits**: Most embedding models have a maximum token limit (e.g., 512 tokens)
- **Semantic Coherence**: Smaller chunks maintain focused semantic meaning
- **Retrieval Precision**: Smaller chunks allow more precise retrieval of relevant information
- **Overlap Strategy**: Chunks often overlap (e.g., 50-100 tokens) to preserve context across boundaries

## What Are Vector Databases for AI Agents?

For AI agents, a vector database acts as long-term memory. Vector databases enable the AI agent to:

### A) Recall Past Interactions Across Different Sessions

AI agents use the database to store past interactions and retrieve them across different sessions, maintaining continuity and user context. This creates a persistent memory that survives beyond individual conversations.

### B) Retrieve Relevant Context from Millions of Documents (RAG)

AI agents use vector databases to fetch external, up-to-date, or private data to inform LLM generation. This allows agents to access knowledge beyond their training data and provide current, domain-specific information.

### C) Connect Concepts That Use Different Wording but Share the Same Meaning

Vector embeddings capture semantic meaning, allowing AI agents to understand that different phrasings express the same concept. For example, "customer support" and "help desk" would be represented by similar vectors.

### How AI Agents Use Vector Databases?

The AI agent converts queries into vectors, compares them against the stored embeddings in the database using nearest-neighbor search, and retrieves the most relevant information to act upon.

**Examples:**
- **External Knowledge Retrieval**: AI agents query the vector database to fetch relevant documents, FAQs, or knowledge base articles
- **Session Memory**: Agents store conversation history as embeddings to maintain context across interactions
- **Multi-Modal Retrieval**: Agents can retrieve images, audio, or video based on semantic similarity
- **Personalization**: Store user preferences and history for personalized responses

For more information: [Best Vector Databases for AI Agents](https://fast.io/resources/best-vector-databases-ai-agents/)

## Project Structure

This example application demonstrates how to use vector databases with Python, FastAPI, and AI agents.

```
VECTOR-DATABASES/
├── README.md
├── .gitignore
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── models.py               # Pydantic models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── documents.py        # Document ingestion endpoints
│   │   ├── search.py           # Vector search endpoints
│   │   └── agent.py            # AI agent endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── vector_db.py        # Vector database service
│   │   ├── embedding.py        # Embedding generation service
│   │   ├── llm.py              # LLM integration service
│   │   └── agent.py            # AI agent service
│   └── utils/
│       ├── __init__.py
│       ├── tokenizer.py        # Text tokenization utilities
│       └── chunking.py         # Document chunking utilities
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_vector_db.py
│   └── test_agent.py
├── scripts/
│   ├── setup_vector_db.sh      # Vector database setup script
│   ├── start_ollama.sh         # Ollama inference server starter
│   └── seed_data.py            # Sample data seeding script
├── data/
│   ├── documents/              # Sample documents
│   └── embeddings/             # Cached embeddings
└── docker/
    ├── docker-compose.yml      # Multi-container setup
    ├── Dockerfile.api          # FastAPI container
    └── Dockerfile.ollama       # Ollama container
```

## Setup and Configuration

### Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose (for containerized deployment)
- Git
- 8GB RAM minimum (16GB recommended for local LLM inference)

### Environment Setup

1. **Clone the repository** (if applicable):
```bash
cd "LARGE-LANGUAGE-MODELS/VECTOR-DATABASES"
```

2. **Create and activate virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Python dependencies**:
```bash
pip install --upgrade pip
pip install fastapi uvicorn chromadb qdrant-client sentence-transformers
pip install python-dotenv pydantic requests httpx
pip install pytest pytest-asyncio  # for testing
```

4. **Create a requirements.txt file**:
```bash
cat > requirements.txt << EOF
fastapi==0.109.0
uvicorn[standard]==0.27.0
chromadb==0.4.22
qdrant-client==1.7.3
sentence-transformers==2.3.1
python-dotenv==1.0.0
pydantic==2.5.3
pydantic-settings==2.1.0
requests==2.31.0
httpx==0.26.0
python-multipart==0.0.6
pytest==7.4.4
pytest-asyncio==0.23.3
EOF
```

5. **Install dependencies from requirements.txt**:
```bash
pip install -r requirements.txt
```

### Vector Database Setup

#### Option 1: Chroma (Local, Easiest)

Chroma is embedded and requires no separate installation:

```bash
# Already installed via pip install chromadb
# Data will be stored in ./chroma_data/
```

#### Option 2: Qdrant (Docker)

```bash
# Pull and run Qdrant
docker pull qdrant/qdrant
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_data:/qdrant/storage \
    qdrant/qdrant
```

#### Option 3: Weaviate (Docker)

```bash
# Create docker-compose.yml for Weaviate
cat > docker-compose-weaviate.yml << EOF
version: '3.4'
services:
  weaviate:
    image: semitechnologies/weaviate:latest
    ports:
      - "8080:8080"
    environment:
      QUERY_DEFAULTS_LIMIT: 25
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'true'
      PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
    volumes:
      - ./weaviate_data:/var/lib/weaviate
EOF

docker-compose -f docker-compose-weaviate.yml up -d
```

#### Option 4: Milvus (Docker)

```bash
# Download Milvus docker-compose
wget https://github.com/milvus-io/milvus/releases/download/v2.3.3/milvus-standalone-docker-compose.yml -O docker-compose-milvus.yml

# Start Milvus
docker-compose -f docker-compose-milvus.yml up -d
```

### Inference Server Setup (Ollama)

Ollama provides local LLM inference:

#### Self-Hosted (Local)

```bash
# Install Ollama (Linux)
curl -fsSL https://ollama.com/install.sh | sh

# Or using Docker
docker pull ollama/ollama
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama

# Pull a model (e.g., llama2, mistral, phi)
ollama pull llama2
ollama pull mistral
ollama pull nomic-embed-text  # For embeddings
```

#### Cloud Providers

For production deployments, consider:

- **Ollama Cloud**: Run Ollama on cloud VMs (AWS EC2, GCP Compute Engine, Azure VM)
- **Replicate**: [https://replicate.com/](https://replicate.com/) - API access to open-source models
- **Hugging Face Inference API**: [https://huggingface.co/inference-api](https://huggingface.co/inference-api)
- **Together AI**: [https://www.together.ai/](https://www.together.ai/) - Fast inference for open-source LLMs
- **Anyscale Endpoints**: [https://www.anyscale.com/endpoints](https://www.anyscale.com/endpoints)

## Running the Application

### Start the Backend Service

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

### Using Docker Compose

```bash
# Build and start all services (API, Vector DB, Ollama)
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Testing

### API Testing with CURL

#### 1. Health Check

```bash
curl -X GET http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy", "vector_db": "connected", "llm": "available"}
```

#### 2. Ingest Documents

```bash
curl -X POST http://localhost:8000/api/documents/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Vector databases store high-dimensional vectors for similarity search.",
    "metadata": {
      "source": "documentation",
      "topic": "vector-databases"
    }
  }'
```

Expected response:
```json
{"id": "doc_abc123", "status": "ingested", "chunks": 1}
```

#### 3. Vector Search

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are vector databases used for?",
    "top_k": 5
  }'
```

Expected response:
```json
{
  "results": [
    {
      "id": "doc_abc123",
      "score": 0.89,
      "text": "Vector databases store high-dimensional vectors...",
      "metadata": {"source": "documentation", "topic": "vector-databases"}
    }
  ],
  "query_time_ms": 45
}
```

#### 4. RAG Query (with LLM)

```bash
curl -X POST http://localhost:8000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain how vector databases work",
    "use_rag": true,
    "top_k": 3
  }'
```

Expected response:
```json
{
  "query": "Explain how vector databases work",
  "response": "Vector databases are specialized systems that store and retrieve high-dimensional vectors...",
  "sources": [
    {"id": "doc_abc123", "score": 0.89}
  ],
  "model": "llama2"
}
```

### Testing Vector Database

#### Test Vector Database Connection

```bash
curl -X GET http://localhost:8000/api/vector-db/status
```

Expected response:
```json
{
  "status": "connected",
  "database": "chroma",
  "collections": 1,
  "total_vectors": 42
}
```

#### Test Embedding Generation

```bash
curl -X POST http://localhost:8000/api/embeddings/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Test embedding generation"
  }'
```

Expected response:
```json
{
  "text": "Test embedding generation",
  "embedding": [0.123, -0.456, 0.789, ...],
  "dimensions": 384,
  "model": "all-MiniLM-L6-v2"
}
```

### Testing AI Agent Integration

#### Test Agent Memory (Multi-Turn Conversation)

```bash
# First query - establish context
curl -X POST http://localhost:8000/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My name is Alice and I love vector databases",
    "session_id": "session_123"
  }'

# Second query - test memory recall
curl -X POST http://localhost:8000/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my name?",
    "session_id": "session_123"
  }'
```

Expected second response:
```json
{
  "response": "Your name is Alice.",
  "session_id": "session_123",
  "context_retrieved": true
}
```

#### Test Agent Knowledge Retrieval

```bash
curl -X POST http://localhost:8000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the benefits of Qdrant?",
    "use_rag": true,
    "agent_mode": "research"
  }'
```

#### Test Agent with External Data

```bash
# Upload custom knowledge base
curl -X POST http://localhost:8000/api/agent/knowledge \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {"text": "Company policy: All employees must use 2FA"},
      {"text": "Office hours: Monday-Friday 9AM-5PM"}
    ],
    "collection": "company_policies"
  }'

# Query against custom knowledge
curl -X POST http://localhost:8000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the office hours?",
    "collection": "company_policies"
  }'
```

### Running Automated Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Testing Tools Summary

| Tool | Purpose | Command |
|------|---------|---------|
| curl | API endpoint testing | `curl -X POST http://localhost:8000/api/...` |
| pytest | Automated testing | `pytest tests/ -v` |
| httpie | Human-friendly HTTP client | `http POST :8000/api/search query="test"` |
| Postman | GUI-based API testing | Import OpenAPI spec from `/docs` |
| k6 | Load testing | `k6 run load-test.js` |

## Deployment Options

### Self-Hosted Deployment

#### Docker Compose (Recommended)

```bash
# Production deployment with all services
docker-compose -f docker-compose.prod.yml up -d
```

#### Kubernetes

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n vector-db-app
```

### Cloud Deployment

#### AWS

- **ECS/EKS**: Deploy containers on AWS Elastic Container Service or Kubernetes
- **EC2**: Run on virtual machines with GPU support (for large models)
- **Lambda**: Serverless deployment (for lighter workloads)
- **Vector Database**: Use Amazon OpenSearch Service with vector search

#### Google Cloud Platform

- **Cloud Run**: Serverless container deployment
- **GKE**: Google Kubernetes Engine for container orchestration
- **Compute Engine**: VM-based deployment with GPU options
- **Vector Database**: Use Vertex AI Vector Search

#### Azure

- **Azure Container Instances**: Quick container deployment
- **AKS**: Azure Kubernetes Service
- **Virtual Machines**: Full control with GPU support
- **Vector Database**: Azure Cognitive Search with vector capabilities

#### Specialized Platforms

- **Qdrant Cloud**: Managed Qdrant vector database
- **Weaviate Cloud**: Managed Weaviate deployment
- **Pinecone**: Fully managed vector database
- **Replicate**: Deploy models with simple API
- **Hugging Face Spaces**: Easy deployment for demos

## References

### Open Source Vector Database Repositories

- **Weaviate**: [https://github.com/weaviate/weaviate](https://github.com/weaviate/weaviate)
- **Chroma**: [https://github.com/chroma-core/chroma](https://github.com/chroma-core/chroma)
- **Qdrant**: [https://github.com/qdrant/qdrant](https://github.com/qdrant/qdrant)
- **Milvus**: [https://github.com/milvus-io/milvus](https://github.com/milvus-io/milvus)
- **FAISS (Facebook AI Similarity Search)**: [https://github.com/facebookresearch/faiss](https://github.com/facebookresearch/faiss)
- **LanceDB**: [https://github.com/lancedb/lancedb](https://github.com/lancedb/lancedb)
- **Pinecone (Python Client)**: [https://github.com/pinecone-io/pinecone-python-client](https://github.com/pinecone-io/pinecone-python-client)

### Additional Resources

- [Microsoft: Improve search results with vector search](https://learn.microsoft.com/en-us/training/modules/improve-search-results-vector-search/2-vector-search)
- [AWS: The role of vector datastores in generative AI applications](https://aws.amazon.com/blogs/database/the-role-of-vector-datastores-in-generative-ai-applications/)
- [Fast.io: Best Vector Databases for AI Agents](https://fast.io/resources/best-vector-databases-ai-agents/)
