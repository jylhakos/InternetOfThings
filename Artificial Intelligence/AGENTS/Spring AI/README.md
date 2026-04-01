# Spring AI - RAG Chat Application

A tutorial of Spring AI framework capabilities featuring Retrieval-Augmented Generation (RAG) for building a "Chat with your documentation" system.

## Table of Contents

- [Overview](#overview)
- [What is Spring AI?](#what-is-spring-ai)
- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Starting the Server](#starting-the-server)
  - [Client Interaction](#client-interaction)
    - [Using cURL](#using-curl)
    - [Using HTTPie](#using-httpie)
    - [Using Python](#using-python)
    - [Using JavaScript/Node.js](#using-javascriptnodejs)
- [API Endpoints](#api-endpoints)
- [RAG Pipeline](#rag-pipeline)
- [Tool Calling](#tool-calling)
- [Troubleshooting](#troubleshooting)
- [References](#references)

## Overview

This project presents how to build an AI-powered application using Spring AI that can answer questions based on your own documentation. It implements Retrieval-Augmented Generation (RAG) pattern to provide accurate, context-aware responses.

At its core, **Spring AI addresses the fundamental challenge of AI integration: Connecting your enterprise Data and APIs with the AI Models**.

## What is Spring AI?

Spring AI is an application framework for AI engineering that applies Spring ecosystem design principles such as portability and modular design to the AI domain. It promotes using POJOs as the building blocks of AI applications.

### Core Principles

- **Portability**: Write once, run with any AI model provider
- **Modular Design**: Compose AI capabilities using Spring's dependency injection
- **POJO-Based**: Standard Java objects for AI interactions
- **Production-Ready**: Built on Spring Boot with enterprise features

## Features

This demonstration includes:

- **RAG Implementation**: Question-answering based on ingested documents
- **Document Ingestion**: Automatic PDF processing and vectorization
- **Multiple Vector Stores**: Support for Qdrant and Chroma databases
- **Ollama Integration**: Local LLM inference using Ollama
- **Tool/Function Calling**: Extensible function execution framework
- **REST API**: Easy-to-use endpoints for chat interactions
- **Configurable Parameters**: Adjustable similarity thresholds and result counts
- **Source Attribution**: Track which documents contributed to answers

## Architecture

```
User Query → ChatClient → QuestionAnswerAdvisor → VectorStore (similarity search)
                ↓                                        ↓
            Ollama LLM ← Augmented Prompt ← Retrieved Documents
                ↓
            Response
```

### RAG Flow

1. **Retrieve**: When a user asks a question, the system searches the vector database for relevant documents using semantic similarity
2. **Augment**: Retrieved documents are added to the user's question, creating an augmented prompt with context
3. **Generate**: The augmented prompt is sent to the LLM (Ollama), which generates an accurate answer based on the provided context

## Technology Stack

- **Java**: 17+
- **Spring Boot**: 3.4.0
- **Spring AI**: 1.0.0
- **LLM Provider**: Ollama (llama3.2 model)
- **Embedding Model**: nomic-embed-text
- **Vector Database**: Qdrant (or Chroma as alternative)
- **Build Tool**: Gradle 8.x
- **Document Format**: PDF (extensible to other formats)

## Prerequisites

Before running this application, ensure you have:

### 1. Java Development Kit
```bash
java -version  # Should be 17 or higher
```

### 2. Ollama Installation

Install Ollama from [ollama.com](https://ollama.com/)

```bash
# Install Ollama (Linux/Mac)
curl -fsSL https://ollama.com/install.sh | sh

# Pull required models
ollama pull llama3.2
ollama pull nomic-embed-text
```

Verify Ollama is running:
```bash
# Ollama should be accessible at http://localhost:11434
curl http://localhost:11434
```

### 3. Vector Database - Qdrant

Install Qdrant using Docker:

```bash
# Run Qdrant in Docker
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant
```

Verify Qdrant is running:
```bash
curl http://localhost:6333
```

**Alternative: Chroma Vector Database**

```bash
# Run Chroma in Docker
docker run -p 8000:8000 chromadb/chroma

# Update application.yml to use Chroma instead of Qdrant
```

## Setup Instructions

### Step 1: Clone or Download the Project

```bash
cd /path/to/Spring\ AI
```

### Step 2: Verify Prerequisites

Ensure all prerequisites are installed and running:
- Ollama (http://localhost:11434)
- Qdrant (http://localhost:6333)

### Step 3: Add Your Documentation

Place PDF documents you want to chat with in the `src/main/resources/documents/` directory.

```bash
# Example: Add your documentation
cp /path/to/your/documentation.pdf src/main/resources/documents/
```

### Step 4: Build the Project

```bash
# Make gradlew executable (Linux/Mac)
chmod +x gradlew

# Build the project
./gradlew build

# Or on Windows
gradlew.bat build
```

### Step 5: Run the Application

```bash
# Run with Gradle
./gradlew bootRun

# Or run the JAR directly
java -jar build/libs/spring-ai-rag-demo-0.0.1-SNAPSHOT.jar
```

The application will:
1. Start on port 8080
2. Automatically ingest documents from `src/main/resources/documents/`
3. Generate embeddings and store them in Qdrant
4. Be ready to answer questions

## Project Structure

```
spring-ai-rag-demo/
├── build.gradle                          # Gradle build configuration
├── settings.gradle                       # Gradle settings
├── gradlew                               # Gradle wrapper (Unix)
├── gradlew.bat                           # Gradle wrapper (Windows)
├── .gitignore                            # Git ignore rules
│
├── src/main/java/com/example/springaidemo/
│   ├── SpringAiDemoApplication.java      # Main application class
│   │
│   ├── config/
│   │   └── VectorStoreConfig.java        # Vector store configuration
│   │
│   ├── controller/
│   │   └── ChatController.java           # REST API endpoints
│   │
│   ├── service/
│   │   └── DocumentIngestionService.java # Document processing & ingestion
│   │
│   ├── model/
│   │   ├── ChatRequest.java              # Request DTOs
│   │   └── ChatResponse.java             # Response DTOs
│   │
│   └── tools/
│       └── ToolConfiguration.java        # Function/tool calling examples
│
└── src/main/resources/
    ├── application.yml                   # Application configuration
    └── documents/                        # Document storage (PDF files)
        └── spring-ai-overview.txt        # Sample document
```

## Source Code Structure

```
src/main/java/com/example/springaidemo/
├── SpringAiDemoApplication.java       # Main Spring Boot application
│
├── config/
│   └── VectorStoreConfig.java         # Vector store configuration
│
├── controller/
│   └── ChatController.java            # REST API endpoints for chat
│
├── model/
│   ├── ChatRequest.java               # Request DTO
│   └── ChatResponse.java              # Response DTO
│
├── service/
│   └── DocumentIngestionService.java  # Document processing & ingestion
│
└── tools/
    └── ToolConfiguration.java         # Function/tool calling examples
```

### Resources

```
src/main/resources/
├── application.yml                    # Application configuration
└── documents/                         # Document storage directory
    └── spring-ai-overview.txt         # Sample documentation
```

### Tests

```
src/test/java/com/example/springaidemo/
└── SpringAiDemoApplicationTests.java  # Integration tests
```

## Configuration

### Build & Configuration Files

- `build.gradle` - Gradle build configuration with Spring AI dependencies
- `settings.gradle` - Gradle settings
- `gradlew` - Gradle wrapper script (Unix/Linux/Mac)
- `gradlew.bat` - Gradle wrapper script (Windows)
- `docker-compose.yml` - Docker Compose for Qdrant vector database
- `.gitignore` - Git ignore rules for binaries and temporary files

### application.yml

Key configuration options:

```yaml
spring:
  ai:
    ollama:
      base-url: http://localhost:11434
      chat:
        options:
          model: llama3.2              # LLM model
          temperature: 0.7             # Response creativity (0-1)
      embedding:
        options:
          model: nomic-embed-text      # Embedding model
    
    qdrant:
      host: localhost
      port: 6334
      collection-name: spring-ai-documentation
      use-tls: false

app:
  documents:
    path: classpath:documents/         # Document location
    auto-ingest: true                  # Auto-process on startup
```

### Environment Variables

You can override configuration using environment variables:

```bash
export OLLAMA_BASE_URL=http://localhost:11434
export QDRANT_HOST=localhost
export QDRANT_PORT=6334
```

## Usage

## API Endpoints

1. `GET /api/chat/health` - Health check
2. `POST /api/chat/ask` - Simple question (query param)
3. `POST /api/chat` - Advanced query (JSON body)
4. `GET /api/chat/stream` - Streaming responses

## Client Examples

Three client implementations are provided:

1. **Shell/cURL** - `test-api.sh`
2. **Python** - `client-example.py`
3. **JavaScript** - `client-example.js`

## Getting Started

1. Run setup script: `./setup.sh`
2. Start application: `./gradlew bootRun`
3. Test API: `./test-api.sh`

### Starting the Server

```bash
./gradlew bootRun
```

Expected output:
```
Started SpringAiDemoApplication in X seconds
Starting automatic document ingestion...
Found N PDF document(s) to ingest
Processing document: spring-ai-overview.txt
Successfully stored X chunks in vector database
```

### Client Interaction

#### Using cURL

**Simple Question:**
```bash
curl -X POST "http://localhost:8080/api/chat/ask?question=What%20is%20Spring%20AI?"
```

**Advanced Query with Parameters:**
```bash
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How does RAG work in Spring AI?",
    "includeContext": true,
    "similarityThreshold": 0.8,
    "topK": 3
  }'
```

#### Using HTTPie

```bash
http POST :8080/api/chat/ask question=="What is Spring AI?"

http POST :8080/api/chat question="How does RAG work?" topK:=3
```

#### Using Python

```python
import requests

# Simple question
response = requests.post(
    "http://localhost:8080/api/chat/ask",
    params={"question": "What is Spring AI?"}
)
print(response.json())

# Advanced query
response = requests.post(
    "http://localhost:8080/api/chat",
    json={
        "question": "Explain vector databases",
        "similarityThreshold": 0.75,
        "topK": 5
    }
)
print(response.json()['answer'])
```

#### Using JavaScript/Node.js

```javascript
// Simple question
fetch('http://localhost:8080/api/chat/ask?question=What%20is%20Spring%20AI?', {
    method: 'POST'
})
.then(res => res.json())
.then(data => console.log(data.answer));

// Advanced query
fetch('http://localhost:8080/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        question: 'How does RAG work?',
        similarityThreshold: 0.8,
        topK: 3
    })
})
.then(res => res.json())
.then(data => console.log(data));
```

## API Endpoints

### Chat Endpoints

#### POST /api/chat/ask
Simple question-answering with default RAG settings.

**Parameters:**
- `question` (query param, required): The question to ask

**Response:**
```json
{
  "answer": "Spring AI is an application framework...",
  "sources": [],
  "responseTimeMs": 1234,
  "model": "llama3.2"
}
```

#### POST /api/chat
Advanced chat with customizable RAG parameters.

**Request Body:**
```json
{
  "question": "What is Spring AI?",
  "includeContext": true,
  "similarityThreshold": 0.7,
  "topK": 5
}
```

**Parameters:**
- `question`: The question to ask
- `includeContext`: Use RAG (true) or direct query (false)
- `similarityThreshold`: Minimum similarity score (0.0-1.0)
- `topK`: Number of documents to retrieve

**Response:**
```json
{
  "answer": "Spring AI is...",
  "sources": ["spring-ai-overview.pdf"],
  "responseTimeMs": 1234,
  "model": "llama3.2"
}
```

#### GET /api/chat/stream
Streaming responses for real-time output.

**Parameters:**
- `question` (query param): The question to ask

#### GET /api/chat/health
Health check endpoint.

**Response:**
```
Chat service is running with model: llama3.2
```

## RAG Pipeline

### Components

The Spring AI RAG pipeline uses these key components:

#### 1. Document
Represents a piece of text and its metadata.

#### 2. EmbeddingModel
Converts text chunks into numerical vectors (embeddings) using the `nomic-embed-text` model.

#### 3. VectorStore
Stores and retrieves document embeddings via similarity search. Supports:
- Qdrant
- Chroma
- PostgreSQL with pgvector
- Pinecone
- Milvus
- Others

#### 4. TextSplitter
Breaks large documents into smaller chunks. Uses `TokenTextSplitter` to ensure chunks fit within the embedding model's token limit.

#### 5. ChatClient
Main interface for interacting with Large Language Models (LLMs) like Ollama.

#### 6. PromptTemplate
Defines the prompt structure sent to the LLM, including placeholders for retrieved context.

#### 7. QuestionAnswerAdvisor
Orchestrates document retrieval and prompt augmentation automatically.

### Document Ingestion Process

```java
// 1. Read PDF document
PagePdfDocumentReader pdfReader = new PagePdfDocumentReader(resource, config);
List<Document> documents = pdfReader.get();

// 2. Split into chunks
TokenTextSplitter textSplitter = new TokenTextSplitter();
List<Document> chunks = textSplitter.apply(documents);

// 3. Add metadata
for (Document chunk : chunks) {
    chunk.getMetadata().put("source", filename);
}

// 4. Generate embeddings and store
vectorStore.add(chunks);
```

### Query Process

```java
// Build ChatClient with RAG advisor
ChatClient chatClient = ChatClient.builder(chatModel)
    .defaultAdvisors(
        QuestionAnswerAdvisor.builder(vectorStore)
            .searchRequest(SearchRequest.builder()
                .similarityThreshold(0.7)
                .topK(5)
                .build())
            .build()
    )
    .build();

// Execute query with RAG
String answer = chatClient.prompt()
    .user(question)
    .call()
    .content();
```

## Tool Calling

Tool calling (function calling) allows the AI model to interact with external APIs and tools.

### Defining Tools

Tools are defined as Spring beans with `@Description` annotation:

```java
@Bean
@Description("Get the current date and time")
public Function<DateTimeRequest, DateTimeResponse> getCurrentDateTime() {
    return request -> {
        LocalDateTime now = LocalDateTime.now();
        String formatted = now.format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
        return new DateTimeResponse(formatted, request.timezone());
    };
}
```

### Using Tools

```java
String response = chatClient.prompt()
    .user("What's the weather in London and what time is it?")
    .functions("getCurrentDateTime", "getWeather")
    .call()
    .content();
```

### Available Tool Examples

The project includes three example tools:

1. **getCurrentDateTime**: Returns current date and time
2. **getWeather**: Returns weather information (mock data)
3. **calculate**: Performs mathematical calculations

See `ToolConfiguration.java` for implementation details.

### Creating Custom Tools

1. Create a `Function<Request, Response>` bean
2. Add `@Description` annotation explaining what the tool does
3. Define request and response records
4. Register the function name when calling `ChatClient`

## Troubleshooting

### Ollama Connection Issues

**Problem**: Cannot connect to Ollama

**Solution**:
```bash
# Check if Ollama is running
curl http://localhost:11434

# Start Ollama if not running
ollama serve

# Verify models are pulled
ollama list
```

### Qdrant Connection Issues

**Problem**: Cannot connect to Qdrant

**Solution**:
```bash
# Check if Qdrant container is running
docker ps | grep qdrant

# Restart Qdrant
docker restart <qdrant-container-id>

# Check Qdrant logs
docker logs <qdrant-container-id>
```

### No Documents Found

**Problem**: "No PDF documents found" message

**Solution**:
- Add PDF files to `src/main/resources/documents/`
- Rebuild the project: `./gradlew build`
- Or set `app.documents.path` to an external directory

### Out of Memory Errors

**Problem**: JVM runs out of memory

**Solution**:
```bash
# Increase heap size
export JAVA_OPTS="-Xmx2g -Xms512m"
./gradlew bootRun

# Or when running JAR
java -Xmx2g -jar build/libs/spring-ai-rag-demo-0.0.1-SNAPSHOT.jar
```

### Slow Response Times

**Problem**: Query responses are slow

**Solution**:
- Reduce `topK` parameter (fewer documents to process)
- Increase `similarityThreshold` (more selective retrieval)
- Use a faster LLM model
- Use GPU acceleration for Ollama

### Model Not Found

**Problem**: Ollama model not available

**Solution**:
```bash
# Pull the required models
ollama pull llama3.2
ollama pull nomic-embed-text

# List available models
ollama list
```

## API Reference

Spring AI provides numerous APIs:

- **Chat Models**: [https://docs.spring.io/spring-ai/reference/api/chatmodel.html](https://docs.spring.io/spring-ai/reference/api/chatmodel.html)
- **ChatClient API**: [https://docs.spring.io/spring-ai/reference/api/chatclient.html](https://docs.spring.io/spring-ai/reference/api/chatclient.html)
- **Ollama Chat**: [https://docs.spring.io/spring-ai/reference/api/chat/ollama-chat.html](https://docs.spring.io/spring-ai/reference/api/chat/ollama-chat.html)
- **Vector Stores**: [https://docs.spring.io/spring-ai/reference/api/vectordbs.html](https://docs.spring.io/spring-ai/reference/api/vectordbs.html)
- **RAG**: [https://docs.spring.io/spring-ai/reference/api/retrieval-augmented-generation.html](https://docs.spring.io/spring-ai/reference/api/retrieval-augmented-generation.html)
- **Tool Calling**: [https://docs.spring.io/spring-ai/reference/api/tools.html](https://docs.spring.io/spring-ai/reference/api/tools.html)
- **All APIs**: [https://docs.spring.io/spring-ai/reference/api/index.html](https://docs.spring.io/spring-ai/reference/api/index.html)

## References

### Documentation

- Spring AI Project: [https://spring.io/projects/spring-ai](https://spring.io/projects/spring-ai)
- Getting Started: [https://docs.spring.io/spring-ai/reference/getting-started.html](https://docs.spring.io/spring-ai/reference/getting-started.html)
- Spring Initializr: [https://start.spring.io/](https://start.spring.io/)
- Blog Post: [https://spring.io/blog/2025/05/20/your-first-spring-ai-1](https://spring.io/blog/2025/05/20/your-first-spring-ai-1)

### Technologies

- Ollama: [https://ollama.com/](https://ollama.com/)
- Qdrant: [https://qdrant.tech/](https://qdrant.tech/)
- Chroma: [https://www.trychroma.com/](https://www.trychroma.com/)

### GitHub

- Spring AI Repository: [https://github.com/spring-projects/spring-ai](https://github.com/spring-projects/spring-ai)

## License

Please refer to Spring AI's license for production use.

---

Built with Spring AI - Making AI integration as simple as Spring Boot

---

**Last Updated**: March 31, 2026
