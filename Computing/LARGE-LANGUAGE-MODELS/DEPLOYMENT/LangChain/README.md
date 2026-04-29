# LLM inference server (Node.js) with LangChain.js

An LLM inference server built with Node.js, LangChain.js, and Meta Llama-3.1 support. This server provides OpenAI-compatible APIs for chat completions with JWT authentication, rate limiting, and AWS deployment capabilities.

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

## Features

- 🤖 **OpenAI compatible API** - Drop-in replacement for OpenAI API endpoints
- 🦙 **Meta Llama-3.1 support** - Optimized for Llama models with quantization support
- 🔐 **JWT authentication** - Secure user authentication and API key management
- 🚀 **LangChain.js integration** - Advanced chat capabilities with conversation memory
- 📈 **Production** - Rate limiting, logging, error handling, and monitoring
- 🐳 **Docker** - Containerized deployment with Docker and Docker Compose
- ☁️ **AWS deployment** - CDK infrastructure for ECS deployment with auto-scaling
- 🔒 **Security** - HTTPS, CORS, Helmet security headers, and Nginx reverse proxy
- 📊 **Monitoring** - Health checks, metrics, and CloudWatch logging
- 🧠 **Memory optimization** - Quantized models and GPU memory management

## Steps

### Prerequisites

- Node.js 18+ 
- Docker (optional)
- AWS CLI (for AWS deployment)
- CDK CLI (for infrastructure deployment)

### Local development

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd llm-inference-server
   npm install
   ```

2. **Environment configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Test the API**
   ```bash
   # Register a user
   curl -X POST http://localhost:3000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

   # Login and get token
   curl -X POST http://localhost:3000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"testuser","password":"password123"}'

   # Chat with the model
   curl -X POST http://localhost:3000/v1/chat/completions \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -d '{
       "messages": [{"role": "user", "content": "Hello, how are you?"}],
       "model": "meta-llama/Llama-3.1-8B-Instruct"
     }'
   ```

## Configuration

### Environment variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NODE_ENV` | Environment mode | `development` |
| `PORT` | Server port | `3000` |
| `LLM_MODEL_NAME` | Model identifier | `meta-llama/Llama-3.1-8B-Instruct` |
| `LLM_MODEL_PATH` | Local model path | `/models/llama-3.1-8b-instruct` |
| `OPENAI_API_KEY` | OpenAI API key (for fallback) | - |
| `HUGGINGFACE_API_KEY` | HuggingFace API key | - |
| `JWT_SECRET` | JWT signing secret | - |
| `USE_QUANTIZED_MODEL` | Enable quantization | `true` |
| `QUANTIZATION_BITS` | Quantization bits | `4` |

### Model (LLM) configuration

The server supports multiple LLM backends:

1. **HuggingFace inference API** (Llama models)
   ```bash
   HUGGINGFACE_API_KEY=your_token_here
   HUGGINGFACE_MODEL_ENDPOINT=https://api-inference.huggingface.co/models/meta-llama/Llama-3.1-8B-Instruct
   ```

2. **OpenAI API** (For testing/fallback)
   ```bash
   OPENAI_API_KEY=your_api_key_here
   OPENAI_BASE_URL=https://api.openai.com/v1
   ```

3. **Local model (LLM) server** (Ollama, vLLM, etc.)
   ```bash
   OPENAI_BASE_URL=http://localhost:11434/v1
   LLM_MODEL_NAME=llama3.1:8b
   ```

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/api-key` - Generate API key
- `GET /api/auth/profile/:userId` - Get user profile

### Chat

- `POST /api/chat/message` - Simple chat message
- `POST /api/chat/completions` - OpenAI-compatible chat completions
- `GET /api/chat/history` - Get conversation history
- `DELETE /api/chat/history` - Clear conversation history
- `GET /api/chat/model` - Get model information

### OpenAI compatible

- `POST /v1/chat/completions` - OpenAI-compatible chat completions
- `GET /v1/models` - List available models

### Health & monitoring

- `GET /api/health` - Basic health check
- `GET /api/health/detailed` - Detailed health status
- `GET /api/health/ready` - Readiness probe
- `GET /api/health/live` - Liveness probe

## Docker deployment

### Build and run

```bash
# Build the image
docker build -t llm-inference-server .

# Run with environment file
docker run -p 3000:3000 --env-file .env llm-inference-server

# Or use Docker Compose
docker-compose up -d
```

### Docker Compose with Nginx

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Scale the service
docker-compose up -d --scale llm-inference-server=3
```

## AWS deployment

### Prerequisites

```bash
# Install AWS CDK
npm install -g aws-cdk

# Configure AWS credentials
aws configure

# Bootstrap CDK (first time only)
cdk bootstrap
```

### Infrastructure

```bash
# Navigate to CDK directory
cd cdk

# Install dependencies
npm install

# Deploy the stack
cdk deploy

# View the deployment
aws ecs list-services --cluster LLMInferenceCluster
```

### Environment setup for AWS

1. **ECR Repository** - Create and push Docker image
   ```bash
   # Create ECR repository
   aws ecr create-repository --repository-name llm-inference-server

   # Get login token
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

   # Tag and push image
   docker tag llm-inference-server:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/llm-inference-server:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/llm-inference-server:latest
   ```

2. **Secrets** - Store sensitive configuration
   ```bash
   aws secretsmanager create-secret \
     --name "llm-inference-secrets" \
     --secret-string '{"JWT_SECRET":"your-secret","HUGGINGFACE_API_KEY":"your-key"}'
   ```

### Infrastructure components

- **VPC** - Custom VPC with public/private subnets
- **ECS Cluster** - Container orchestration with GPU support
- **Application Load Balancer** - HTTPS termination and routing
- **Auto Scaling** - CPU and memory-based scaling
- **CloudWatch** - Logging and monitoring
- **Secrets Manager** - Secure credential storage
- **IAM Roles** - Least privilege access

## Development

### Project

```
├── src/
│   ├── server.ts              # Main server file
│   ├── services/
│   │   ├── LLMChatService.ts  # LangChain integration
│   │   └── AuthService.ts     # Authentication logic
│   ├── middleware/
│   │   ├── auth.ts            # JWT middleware
│   │   ├── rateLimiter.ts     # Rate limiting
│   │   └── errorHandler.ts    # Error handling
│   ├── routes/
│   │   ├── chat.ts            # Chat endpoints
│   │   ├── auth.ts            # Auth endpoints
│   │   └── health.ts          # Health checks
│   └── utils/
│       └── logger.ts          # Winston logger
├── cdk/                       # AWS CDK infrastructure
├── Dockerfile                 # Container definition
├── docker-compose.yml         # Local orchestration
└── nginx.conf                 # Reverse proxy config
```

### Adding new models

1. **Update LLMChatService.ts**
   ```typescript
   // Add new model configuration
   if (process.env.NEW_MODEL_API_KEY) {
     this.llm = new ChatOpenAI({
       openAIApiKey: process.env.NEW_MODEL_API_KEY,
       modelName: process.env.NEW_MODEL_NAME,
       configuration: {
         baseURL: process.env.NEW_MODEL_ENDPOINT,
       },
     });
   }
   ```

2. **Update environment variables**
   ```bash
   NEW_MODEL_API_KEY=your_api_key
   NEW_MODEL_NAME=new-model-name
   NEW_MODEL_ENDPOINT=https://api.example.com/v1
   ```

### Middleware

Add custom middleware in the `middleware/` directory and register it in `server.ts`:

```typescript
import { customMiddleware } from './middleware/custom';
this.app.use(customMiddleware);
```

## Security

### Authentication

- JWT tokens with configurable expiration
- API key support for programmatic access
- Role-based access control (user/admin)
- Secure password hashing with bcrypt

### Rate limiting

- IP-based rate limiting
- Different limits for different endpoints
- Configurable windows and request counts

### Network security

- HTTPS termination at load balancer
- Security headers (Helmet.js)
- CORS configuration
- Nginx rate limiting and security

### Data

- No persistent storage of conversation data by default
- In-memory conversation state with optional persistence
- Secrets management with AWS Secrets Manager

## Monitoring and logging

### Application Logging

- Structured JSON logging with Winston
- Request/response logging with correlation IDs
- Error tracking and stack traces
- Configurable log levels

### Health checks

- Basic health endpoint for load balancer
- Detailed health with service status
- Kubernetes-compatible readiness/liveness probes

### Model optimization

- Quantized models (4-bit, 8-bit) for memory efficiency
- GPU memory management
- Batch processing for multiple requests
- Model caching and warm-up

### Performance

- Compression middleware
- Connection pooling
- Memory usage monitoring
- Request queuing and throttling

### Scaling

- Horizontal scaling with load balancer
- Auto-scaling based on CPU/memory
- Container resource limits
- Database connection pooling (if used)

## Troubleshooting

### Issues & errors

1. **Model Loading Errors**
   ```bash
   # Check model path and permissions
   ls -la /models/
   
   # Verify API keys
   curl -H "Authorization: Bearer $HUGGINGFACE_API_KEY" \
     https://api-inference.huggingface.co/models/meta-llama/Llama-3.1-8B-Instruct
   ```

2. **Memory**
   ```bash
   # Monitor memory usage
   docker stats
   
   # Adjust memory limits in docker-compose.yml
   mem_limit: 8g
   ```

3. **Authentication**
   ```bash
   # Verify JWT secret is set
   echo $JWT_SECRET
   
   # Check token expiration
   npm install -g jsonwebtoken
   node -e "console.log(require('jsonwebtoken').decode('YOUR_TOKEN'))"
   ```

### Debug mode

Enable debug logging:
```bash
LOG_LEVEL=debug npm run dev
```

### Health check debugging

```bash
# Check health endpoints
curl http://localhost:3000/api/health
curl http://localhost:3000/api/health/detailed

# Check Docker health
docker-compose ps
```

### Development workflow

```bash
# Install dependencies
npm install

# Run development server with hot reload
npm run dev

# Build for production
npm run build

# Run production build
npm start

# Run tests
npm test

# Check linting
npm run lint
```

## License

MIT License - see LICENSE file for details.
