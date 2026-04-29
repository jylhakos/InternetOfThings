# Architecture Documentation: Chat with Local LLMs using n8n and Ollama

## Table of Contents

- [System Overview](#system-overview)
- [Architecture Diagram](#architecture-diagram)
- [Component Architecture](#component-architecture)
  - [n8n Workflow Engine](#n8n-workflow-engine)
  - [Ollama LLM Runtime](#ollama-llm-runtime)
  - [LangChain Integration Layer](#langchain-integration-layer)
- [Data Flow Architecture](#data-flow-architecture)
- [Technology Stack](#technology-stack)
- [Deployment Architecture](#deployment-architecture)
  - [Local Development](#local-development)
  - [Docker Deployment](#docker-deployment)
  - [Production Deployment](#production-deployment)
- [Network Architecture](#network-architecture)
- [Security Architecture](#security-architecture)
- [Scalability Considerations](#scalability-considerations)
- [Integration Points](#integration-points)

## System Overview

The chat application leverages n8n, a workflow automation platform, to orchestrate conversational interactions with locally hosted Large Language Models (LLMs) managed by Ollama. This architecture enables privacy-preserving AI chat capabilities without relying on external cloud services.

### Key Architectural Principles

1. **Privacy-First Design**: All data processing occurs locally without external API calls
2. **Loose Coupling**: Components communicate through well-defined interfaces
3. **Modularity**: Each component can be replaced or upgraded independently
4. **Scalability**: Architecture supports horizontal scaling for increased load
5. **Observability**: Built-in monitoring and logging capabilities

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          User Interface Layer                       │
│                     (Browser / API Client)                          │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTP/WebSocket
                             │ Port 5678
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        n8n Platform                                 │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │                  Workflow Engine                          │      │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │      │
│  │  │   Chat      │  │  LLM Chain   │  │  Ollama Chat    │   │      │
│  │  │   Trigger   │─▶│   Node       │─▶│  Model Node     │   │      │
│  │  └─────────────┘  └──────────────┘  └─────────────────┘   │      │
│  └───────────────────────────────────────────────────────────┘      │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │              LangChain Integration Layer                  │      │
│  │  - Chain Management                                       │      │
│  │  - Context Handling                                       │      │
│  │  - Response Streaming                                     │      │
│  └───────────────────────────────────────────────────────────┘      │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │                  Data Persistence                         │      │
│  │  - Workflow Definitions (SQLite/PostgreSQL)               │      │
│  │  - Execution History                                      │      │
│  │  - Credentials Store (Encrypted)                          │      │
│  └───────────────────────────────────────────────────────────┘      │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTP REST API
                             │ Port 11434
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Ollama Runtime                                 │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │                   Model Manager                           │      │
│  │  - Model Loading/Unloading                                │      │
│  │  - Model Version Control                                  │      │
│  │  - Resource Allocation                                    │      │
│  └───────────────────────────────────────────────────────────┘      │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │                 Inference Engine                          │      │
│  │  - Token Generation                                       │      │
│  │  - Context Management                                     │      │
│  │  - Response Generation                                    │      │
│  └───────────────────────────────────────────────────────────┘      │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │              LLM Models (File System)                     │      │
│  │  - llama2 (7B, 13B, 70B)                                  │      │
│  │  - codellama                                              │      │
│  │  - Other Models                                           │      │
│  └───────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### n8n Workflow Engine

The n8n workflow engine serves as the orchestration layer for the chat application.

#### Core Components

1. **Workflow Execution Runtime**
   - Node.js-based execution environment
   - Event-driven architecture
   - Asynchronous processing
   - Worker queue management

2. **Node System**
   - Modular node architecture
   - Input/output connection system
   - Parameter configuration
   - Credential management

3. **Trigger System**
   - Chat interface trigger
   - Webhook triggers
   - Scheduled triggers
   - Manual execution triggers

4. **Data Storage**
   - SQLite (development)
   - PostgreSQL (production)
   - Binary data handling
   - Execution history retention

#### Workflow Nodes

**Chat Trigger Node**
```
Type: @n8n/n8n-nodes-langchain.chatTrigger
Version: 1.1
Purpose: Entry point for user messages
Inputs: None (entry point)
Outputs: User message object
```

**LLM Chain Node**
```
Type: @n8n/n8n-nodes-langchain.chainLlm
Version: 1.4
Purpose: Orchestration of conversation flow
Inputs: Chat trigger, LLM model
Outputs: Processed response
Features:
  - Conversation context management
  - Memory integration
  - Response streaming
```

**Ollama Chat Model Node**
```
Type: @n8n/n8n-nodes-langchain.lmChatOllama
Version: 1
Purpose: Interface to Ollama LLM
Configuration:
  - Base URL: http://localhost:11434
  - Model selection
  - Temperature control
  - Token limits
```

### Ollama LLM Runtime

Ollama provides the local LLM hosting and inference capabilities.

#### Architecture Components

1. **REST API Server**
   - HTTP server on port 11434
   - RESTful endpoint design
   - Streaming response support
   - Model management endpoints

2. **Model Manager**
   - Model downloading and storage
   - Version management
   - Model loading/unloading
   - Resource optimization

3. **Inference Engine**
   - Transformer-based architecture
   - GPU acceleration support (optional)
   - CPU-optimized inference
   - Batch processing capabilities

4. **Context Manager**
   - Conversation history tracking
   - Context window management
   - Token counting
   - Memory optimization

### LangChain Integration Layer

LangChain provides the abstraction layer for AI interactions.

#### Key Features

1. **Chain Composition**
   - Sequential chains
   - Parallel execution
   - Conditional branching
   - Error handling

2. **Memory Systems**
   - Conversation buffer memory
   - Summary memory
   - Entity memory
   - Vector store memory

3. **Tool Integration**
   - API integration capabilities
   - Custom tool definition
   - Tool selection logic
   - Result processing

## Data Flow Architecture

### Request Flow

```
1. User Input
   │
   ├─▶ Browser sends message via WebSocket/HTTP
   │
2. n8n Chat Trigger
   │
   ├─▶ Captures user input
   ├─▶ Creates execution context
   │
3. LLM Chain Processing
   │
   ├─▶ Retrieves conversation context
   ├─▶ Formats prompt with context
   ├─▶ Prepares request for LLM
   │
4. Ollama Chat Model
   │
   ├─▶ Sends HTTP POST to Ollama API
   ├─▶ Endpoint: http://localhost:11434/api/generate
   │
5. Ollama Inference
   │
   ├─▶ Loads model into memory (if not loaded)
   ├─▶ Processes prompt through transformer
   ├─▶ Generates tokens sequentially
   │
6. Response Streaming
   │
   ├─▶ Streams tokens back to n8n
   ├─▶ Accumulates response
   │
7. Response Processing
   │
   ├─▶ Formats response
   ├─▶ Updates conversation context
   │
8. User Response
   │
   └─▶ Displays in chat interface
```

### Data Models

#### User Message Object
```json
{
  "chatInput": "string",
  "sessionId": "string",
  "timestamp": "ISO8601",
  "metadata": {
    "userId": "string",
    "conversationId": "string"
  }
}
```

#### Ollama Request Object
```json
{
  "model": "llama2",
  "prompt": "string",
  "stream": false,
  "options": {
    "temperature": 0.7,
    "top_k": 40,
    "top_p": 0.9,
    "num_predict": 128
  }
}
```

#### Ollama Response Object
```json
{
  "model": "llama2",
  "response": "string",
  "done": true,
  "context": [int],
  "total_duration": int,
  "load_duration": int,
  "prompt_eval_count": int,
  "eval_count": int,
  "eval_duration": int
}
```

## Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Workflow Engine | n8n | Latest | Automation platform |
| Runtime | Node.js | 18+ | JavaScript runtime |
| LLM Runtime | Ollama | Latest | Local LLM hosting |
| AI Framework | LangChain | Latest | AI orchestration |
| Database | SQLite/PostgreSQL | - | Data persistence |
| Web Server | Express.js | - | HTTP server |
| WebSocket | Socket.io | - | Real-time communication |

### Development Technologies

| Purpose | Technology | Usage |
|---------|------------|-------|
| Testing | pytest | Python unit/integration tests |
| HTTP Client | requests | API testing |
| Containerization | Docker | Deployment packaging |
| Orchestration | Docker Compose | Multi-container management |
| Version Control | Git | Source code management |
| Environment | Python venv | Dependency isolation |

### Language Models

| Model | Parameters | Use Case | Memory Required |
|-------|------------|----------|-----------------|
| llama2 | 7B | General chat | 8GB RAM |
| llama2:13b | 13B | Enhanced quality | 16GB RAM |
| llama2:70b | 70B | Production quality | 64GB RAM |
| codellama | 7B | Code generation | 8GB RAM |

## Deployment Architecture

### Local Development

```
Developer Machine
├── n8n (Port 5678)
│   └── Node.js Runtime
│       └── Workflow Execution
├── Ollama (Port 11434)
│   └── Model: llama2
├── Python Virtual Environment
│   └── Testing Framework
└── Browser
    └── Chat Interface
```

**Resource Requirements:**
- CPU: 4+ cores
- RAM: 8GB minimum, 16GB recommended
- Storage: 20GB for models
- Network: Localhost only

### Docker Deployment

```
Docker Host
├── n8n Container
│   ├── Image: docker.n8n.io/n8nio/n8n
│   ├── Port: 5678
│   ├── Volume: n8n_data
│   └── Network: n8n-network
│       └── Extra Host: host.docker.internal
├── Ollama (Host System)
│   ├── Port: 11434
│   └── Accessed via: host.docker.internal:11434
└── PostgreSQL Container (Optional)
    ├── Image: postgres:15-alpine
    ├── Port: 5432
    ├── Volume: postgres_data
    └── Network: n8n-network
```

**Container Configuration:**
```yaml
n8n:
  - Environment: Production
  - Restart Policy: unless-stopped
  - Health Check: /healthz endpoint
  - Resource Limits: Configurable

postgres:
  - Environment: Production
  - Persistence: Volume-backed
  - Backup: Automated
```

### Production Deployment

```
Production Environment
├── Load Balancer (Optional)
│   └── SSL Termination
│       └── Port 443 → 5678
├── n8n Application Layer
│   ├── Multiple Instances (Horizontal Scaling)
│   ├── Shared Database
│   └── Shared File Storage
├── Database Layer
│   ├── PostgreSQL Primary
│   └── PostgreSQL Replica (Optional)
├── LLM Layer
│   ├── Dedicated Ollama Servers
│   ├── GPU Acceleration
│   └── Model Caching
└── Monitoring Stack
    ├── Prometheus (Metrics)
    ├── Grafana (Visualization)
    └── Loki (Logs)
```

**High Availability Setup:**
- Multiple n8n instances behind load balancer
- Shared PostgreSQL database with replication
- Centralized Ollama service with dedicated hardware
- Redis for session management
- S3-compatible storage for binary data

## Network Architecture

### Port Allocation

| Service | Port | Protocol | Access |
|---------|------|----------|--------|
| n8n Web UI | 5678 | HTTP/WebSocket | Public |
| n8n Webhooks | 5678 | HTTP | Public |
| Ollama API | 11434 | HTTP | Internal |
| PostgreSQL | 5432 | TCP | Internal |
| Redis | 6379 | TCP | Internal |

### Network Topology

**Development:**
```
Localhost (127.0.0.1)
├── n8n: http://localhost:5678
└── Ollama: http://localhost:11434
```

**Docker Environment:**
```
Docker Network: n8n-network (Bridge)
├── n8n Container: 172.18.0.2
├── PostgreSQL Container: 172.18.0.3
└── Host System (Ollama): host.docker.internal
```

**Production:**
```
Public Network
├── Load Balancer: 203.0.113.10
│   └── SSL Certificate
Internal Network (10.0.0.0/24)
├── n8n-01: 10.0.0.10
├── n8n-02: 10.0.0.11
├── PostgreSQL: 10.0.0.20
├── Redis: 10.0.0.21
└── Ollama: 10.0.0.30
```

### Communication Protocols

1. **User to n8n**
   - Protocol: HTTP/HTTPS
   - Format: JSON
   - Connection: WebSocket for real-time chat

2. **n8n to Ollama**
   - Protocol: HTTP REST API
   - Format: JSON
   - Method: POST /api/generate
   - Connection: Keep-alive

3. **n8n to Database**
   - Protocol: PostgreSQL wire protocol
   - Connection: Connection pooling
   - Encryption: TLS (production)

## Security Architecture

### Authentication & Authorization

1. **n8n Access Control**
   ```
   Basic Authentication
   ├── Username/Password
   ├── Session Management
   └── API Token Support
   
   Optional: OAuth2 Integration
   ├── Google
   ├── GitHub
   └── SAML
   ```

2. **Credential Management**
   - Encrypted credential storage
   - AES-256 encryption
   - Key derivation from master password
   - Credential access logging

### Data Security

1. **Data at Rest**
   - Database encryption (PostgreSQL)
   - Encrypted workflow definitions
   - Secure credential vault
   - Binary data encryption

2. **Data in Transit**
   - TLS/SSL for external connections
   - Internal network encryption (production)
   - Certificate management
   - Perfect forward secrecy

3. **Privacy Considerations**
   - All LLM processing local
   - No external API calls
   - No data leaving network
   - GDPR compliant (configurable)

### Network Security

```
Security Layers
├── Application Layer
│   ├── Input validation
│   ├── Output sanitization
│   ├── CSRF protection
│   └── XSS prevention
├── Network Layer
│   ├── Firewall rules
│   ├── Port restrictions
│   ├── IP whitelisting
│   └── Rate limiting
└── Infrastructure Layer
    ├── Container isolation
    ├── Least privilege access
    ├── Security updates
    └── Vulnerability scanning
```

## Scalability Considerations

### Vertical Scaling

**n8n Scaling:**
- Increase Node.js memory allocation
- Enable worker threads
- Optimize database connections
- Increase execution timeout

**Ollama Scaling:**
- Add GPU acceleration
- Increase RAM for larger models
- Optimize model quantization
- Enable model caching

### Horizontal Scaling

**n8n Cluster:**
```
Load Balancer
├── n8n Instance 1
├── n8n Instance 2
└── n8n Instance N

Shared Resources:
├── PostgreSQL Database
├── Redis Session Store
└── S3 Binary Storage
```

**Requirements:**
- Queue mode execution
- Shared database
- Session synchronization
- Sticky sessions (WebSocket)

### Performance Optimization

1. **Database Optimization**
   - Connection pooling
   - Query optimization
   - Index management
   - Execution history cleanup

2. **Caching Strategy**
   - Model caching (Ollama)
   - Response caching
   - Static asset caching
   - CDN integration (optional)

3. **Resource Management**
   - Memory limits per execution
   - Concurrent execution limits
   - Queue prioritization
   - Timeout configuration

## Integration Points

### Extensibility

1. **Custom Nodes**
   - Create custom n8n nodes
   - TypeScript/JavaScript API
   - NPM package distribution
   - Community node support

2. **Tool Integration**
   - LangChain tool system
   - HTTP Request tools
   - API integrations
   - Custom code execution

3. **Webhook Integration**
   - Incoming webhooks
   - Outgoing webhooks
   - Event-driven triggers
   - Third-party service integration

### API Endpoints

**n8n REST API:**
```
GET    /workflows              List workflows
POST   /workflows              Create workflow
GET    /workflows/:id          Get workflow
PUT    /workflows/:id          Update workflow
DELETE /workflows/:id          Delete workflow
POST   /workflows/:id/activate Activate workflow
POST   /workflow/:id/execute   Execute workflow
GET    /executions             List executions
GET    /executions/:id         Get execution
```

**Ollama API:**
```
GET    /api/version            Get version
GET    /api/tags               List models
POST   /api/generate           Generate completion
POST   /api/chat               Chat completion
POST   /api/pull               Pull model
POST   /api/push               Push model
DELETE /api/delete             Delete model
```

### Event System

```
Workflow Execution Events
├── workflow.started
├── workflow.completed
├── workflow.failed
├── node.started
├── node.completed
└── node.failed

System Events
├── server.started
├── server.stopped
├── database.connected
└── error.occurred
```

---

**Last Updated:** April 1, 2026
