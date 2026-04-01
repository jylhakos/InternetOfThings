# Spring AI RAG Demo - Quick Start

## Quick Start

### 1. Run the setup script

```bash
chmod +x setup.sh
./setup.sh
```

This will check and start all prerequisites:
- Java 17+
- Docker
- Ollama (with llama3.2 and nomic-embed-text models)
- Qdrant vector database

### 2. Start the application

```bash
./gradlew bootRun
```

### 3. Test the API

```bash
# Simple question
curl -X POST "http://localhost:8080/api/chat/ask?question=What%20is%20Spring%20AI?"

# Advanced query
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Explain RAG", "topK": 3}'
```

## Manual Setup

If you prefer to set up manually:

### 1. Install Prerequisites

**Java 17+**
```bash
java -version
```

**Ollama**
```bash
# Install from https://ollama.com/
curl -fsSL https://ollama.com/install.sh | sh

# Pull models
ollama pull llama3.2
ollama pull nomic-embed-text
```

**Qdrant (Docker)**
```bash
docker-compose up -d
```

### 2. Add Documents

Place your PDF files in:
```
src/main/resources/documents/
```

### 3. Build and Run

```bash
./gradlew build
./gradlew bootRun
```

## Example Queries

```bash
# What is Spring AI?
curl -X POST "http://localhost:8080/api/chat/ask?question=What%20is%20Spring%20AI?"

# How does RAG work?
curl -X POST "http://localhost:8080/api/chat/ask?question=How%20does%20RAG%20work?"

# What are vector databases?
curl -X POST "http://localhost:8080/api/chat/ask?question=What%20are%20vector%20databases?"

# Advanced query with parameters
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain the ChatClient API",
    "similarityThreshold": 0.8,
    "topK": 3
  }'
```

## Troubleshooting

**Ollama not responding**
```bash
# Check if running
curl http://localhost:11434

# Restart Ollama
pkill ollama
ollama serve
```

**Qdrant not responding**
```bash
# Check if running
curl http://localhost:6333

# Restart Qdrant
docker-compose restart qdrant
```

**Port already in use**
```bash
# Change port in application.yml
server:
  port: 8081
```

## Next Steps

1. Add your own PDF documents to `src/main/resources/documents/`
2. Customize the RAG parameters in `application.yml`
3. Implement custom tools in `ToolConfiguration.java`
4. Explore the API endpoints in `ChatController.java`

For full documentation, see [README.md](README.md)
