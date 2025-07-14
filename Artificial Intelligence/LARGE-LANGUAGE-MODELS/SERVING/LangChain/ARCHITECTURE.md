# 🚀 LLM inference server

## What is implemented for LLM inference server?

The LLM inference server built with Node.js, TypeScript, and LangChain.js that provides OpenAI compatible APIs for Meta Llama-3.1 and other language models.

## 🏗️ Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Client Apps   │    │   Load Balancer  │    │  LLM Inference  │
│  (OpenWebUI,    │───▶│    (Nginx)       │───▶│     Server      │
│   Custom Apps)  │    │                  │    │  (Node.js +     │
└─────────────────┘    └──────────────────┘    │   LangChain)    │
                                               └─────────────────┘
                                                        │
                                               ┌─────────────────┐
                                               │   LLM Models    │
                                               │ (Llama-3.1,     │
                                               │  OpenAI, etc.)  │
                                               └─────────────────┘
```

## 📁 Project

```
llm-inference-server/
├── src/                          # Source code
│   ├── server.ts                 # Main server
│   ├── services/
│   │   ├── LLMChatService.ts     # LangChain integration
│   │   └── AuthService.ts        # JWT authentication
│   ├── middleware/               # Express middleware
│   ├── routes/                   # API endpoints
│   └── utils/                    # Utilities
├── cdk/                          # AWS CDK infrastructure
├── scripts/                      # Deployment & utility scripts
├── docs/                         # Documentation
├── Dockerfile                    # Container definition
├── docker-compose.yml            # Local orchestration
└── README.md                     # Main documentation
```

## 🔧 Features

### Core LLM
- ✅ **OpenAI-Compatible API** - Drop-in replacement for OpenAI endpoints
- ✅ **LangChain.js Integration** - Advanced chat capabilities with memory
- ✅ **Meta Llama-3.1 Support** - Optimized for Llama models
- ✅ **Conversation Memory** - Persistent chat history with LangGraph
- ✅ **Message Trimming** - Automatic context window management
- ✅ **Multiple Model Backends** - OpenAI API, HuggingFace, Local servers

### Security & authentication
- ✅ **JWT Authentication** - Secure token-based auth
- ✅ **API Key Support** - Alternative authentication method
- ✅ **Rate Limiting** - IP and user-based limits
- ✅ **CORS & Security Headers** - Production security
- ✅ **Role-Based Access** - User/admin roles

### Production
- ✅ **Docker Support** - Full containerization
- ✅ **Health Checks** - Kubernetes-compatible probes
- ✅ **Structured Logging** - Winston with JSON format
- ✅ **Error Handling** - Comprehensive error management
- ✅ **Request Validation** - Input sanitization
- ✅ **Compression** - Response optimization

### Deployment & infrastructure
- ✅ **AWS CDK Stack** - Infrastructure as Code
- ✅ **ECS Deployment** - Container orchestration
- ✅ **Auto Scaling** - CPU/memory-based scaling
- ✅ **Load Balancer** - HTTPS termination
- ✅ **Secrets Management** - AWS Secrets Manager
- ✅ **CloudWatch Logging** - Centralized logs

### Development tools
- ✅ **TypeScript** - Full type safety
- ✅ **Jest testing** - Test framework setup
- ✅ **Development scripts** - Easy local development
- ✅ **Build pipeline** - Automated compilation
- ✅ **Health check scripts** - Automated testing

## 🚀 Start commands

### Local development
```bash
# Setup
npm install
cp .env.example .env
# Edit .env with your API keys

# Development
npm run dev                 # Start with hot reload
npm run build              # Build for production
npm start                  # Run production build

# Testing
./scripts/test-server.sh   # Test running server
./scripts/health-check.sh  # Comprehensive health check
```

### Docker deployment
```bash
# Single container
docker build -t llm-inference-server .
docker run -p 3000:3000 --env-file .env llm-inference-server

# Full stack with Nginx
docker-compose up -d
```

### AWS deployment
```bash
# Deploy to AWS
./scripts/deploy-aws.sh

# Monitor deployment
aws ecs list-services --cluster LLMInferenceCluster
```

## 🌐 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/api-key` - Generate API key

### Chat & LLM
- `POST /v1/chat/completions` - OpenAI-compatible chat
- `POST /api/chat/message` - Simplified chat
- `GET /api/chat/history` - Conversation history
- `GET /v1/models` - Available models

### Health & monitoring
- `GET /api/health` - Basic health check
- `GET /api/health/detailed` - Detailed status
- `GET /api/health/ready` - Readiness probe
- `GET /api/health/live` - Liveness probe

## 🔧 Configuration

### Model backends

**1. HuggingFace (Llama)**
```bash
HUGGINGFACE_API_KEY=hf_your_token
HUGGINGFACE_MODEL_ENDPOINT=https://api-inference.huggingface.co/models/meta-llama/Llama-3.1-8B-Instruct
```

**2. OpenAI API (Testing/Fallback)**
```bash
OPENAI_API_KEY=sk-your_key
OPENAI_BASE_URL=https://api.openai.com/v1
```

**3. Local Ollama**
```bash
OPENAI_BASE_URL=http://localhost:11434/v1
LLM_MODEL_NAME=llama3.1:8b
```

**4. Custom inference server**
```bash
OPENAI_BASE_URL=http://your-server:8000/v1
OPENAI_API_KEY=your_custom_key
```

### Security
```bash
JWT_SECRET=your-super-secret-key
JWT_EXPIRES_IN=24h
RATE_LIMIT_MAX_REQUESTS=100
RATE_LIMIT_WINDOW_MS=900000
```

### Model optimization
```bash
USE_QUANTIZED_MODEL=true
QUANTIZATION_BITS=4
GPU_MEMORY_FRACTION=0.8
MAX_SEQUENCE_LENGTH=4096
```

## 🔌 Integration

### OpenWebUI integration
```bash
# Run OpenWebUI pointing to your server
docker run -p 8080:8080 \
  -e OPENAI_API_BASE_URL="http://host.docker.internal:3000/v1" \
  -e OPENAI_API_KEY="your-jwt-token" \
  ghcr.io/open-webui/open-webui:main
```

### Custom client integration
```typescript
import OpenAI from 'openai';

const client = new OpenAI({
  apiKey: 'your-jwt-token',
  baseURL: 'https://your-server.com/v1',
});

const response = await client.chat.completions.create({
  messages: [{ role: 'user', content: 'Hello!' }],
  model: 'meta-llama/Llama-3.1-8B-Instruct',
});
```

## 📊 Monitoring & observability

### Health monitoring
- Application health endpoints
- Container health checks
- AWS ECS service health
- Auto-scaling metrics

### Logging
- Structured JSON logging
- Request/response correlation
- Error tracking with stack traces
- CloudWatch integration

## 📚 Documentation

- **Documentation**: `README.md`
- **API Reference**: `docs/api-reference.md`
- **OpenWebUI integration**: `docs/open-webui-integration.md`
- **Deployment scripts**: `scripts/README.md`
