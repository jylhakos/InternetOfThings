# Chat service (LLMs)

This project involves creating a chat application utilizing Java and Spring Boot to facilitate the use of Large Language Models (LLMs) via Ollama, specifically targeting the Llama-3 model.

The chat service provides a RESTful API and web interface for chat interactions.

## 🌟 Features

- **RESTful API** for chat interactions with LLMs
- **Testing with a web application** for testing and interaction
- **Ollama integration** for local LLM inference
- **Configurable System Templates** for customizing AI behavior
- **Health checks** and monitoring endpoints
- **Docker support** for Docker deployment
- **AWS deployment scripts** for production environments
- **CORS support** for web applications
- **Error handling**

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web client    │────│  Spring Boot    │────│     Ollama      │
│   (Browser)     │    │   application   │    │   (Llama-3)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick start

### Option 1: Docker (Recommended)

```bash
# Setup with Docker
chmod +x scripts/setup-docker.sh
./scripts/setup-docker.sh
```

### Option 2: Local development

```bash
# Setup local environment
chmod +x scripts/setup-local.sh
./scripts/setup-local.sh

# Run the application
./run-local.sh
```

### Option 3: Manual setup

1. **Install Prerequisites**
   - Java 17+
   - Maven 3.6+
   - Ollama

2. **Install and setup Ollama**
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Start Ollama service
   ollama serve
   
   # Pull Llama-3 model
   ollama pull llama3
   ```

3. **Build and run**
   ```bash
   # Build application
   mvn clean compile
   
   # Run application
   mvn spring-boot:run
   ```

## 📡 API endpoints

### Chat API
- **POST** `/api/v1/chat` - Send chat messages
- **GET** `/api/v1/chat/health` - Service health check
- **GET** `/api/v1/chat/info` - Service information

### Request format

```json
{
  "message": "Hello, how are you?",
  "use_system_template": true,
  "temperature": 0.7,
  "max_tokens": 2048
}
```

### Response format

```json
{
  "response": "Hello! I'm doing well, thank you for asking...",
  "model_used": "llama3",
  "tokens_used": 156,
  "response_time_ms": 1234,
  "timestamp": "2025-07-07T10:30:00",
  "success": true
}
```

### Health check

```bash
curl http://localhost:8080/api/v1/chat/health
```

## 🌐 Web application

Access the web application at `http://localhost:8080` for an interactive chat experience.

Features:
- Real-time chat interface
- Configurable parameters (temperature, max tokens)
- System template toggle
- Response time monitoring

## ⚙️ Configuration

### Application properties

```properties
# Ollama Configuration
spring.ai.ollama.base-url=http://localhost:11434
spring.ai.ollama.chat.options.model=llama3
spring.ai.ollama.chat.options.temperature=0.7

# System Template
llm.system.template=You are a helpful AI assistant...
llm.max-tokens=2048
llm.timeout=30000
```

### Environment variables

- `OLLAMA_BASE_URL` - Ollama server URL
- `SPRING_PROFILES_ACTIVE` - Active Spring profiles
- `JAVA_OPTS` - JVM options for containerized deployments

## 🐳 Docker deployment

### Local Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Custom Docker build

```bash
# Build image
docker build -t llm-chat-service .

# Run container
docker run -p 8080:8080 \
  -e SPRING_AI_OLLAMA_BASE_URL=http://ollama:11434 \
  llm-chat-service
```

## ☁️ AWS deployment

### Option 1: An EC2 instance

```bash
# Deploy to EC2
chmod +x scripts/deploy-aws.sh
./scripts/deploy-aws.sh

# Deploy application
./deploy-app.sh
```

This creates:
- EC2 instance (m5.xlarge recommended)
- Security groups with appropriate ports
- Ollama installation and Llama-3 model
- Automatic application deployment

### Option 2: ECS Fargate (Production)

```bash
# Deploy to ECS
chmod +x scripts/deploy-aws-ecs.sh
./scripts/deploy-aws-ecs.sh
```

This creates:
- ECS cluster with Fargate tasks
- ECR repository for Docker images
- CloudWatch logging
- Load balancer (optional)
- Auto-scaling capabilities

### AWS requirements

- AWS CLI configured with appropriate permissions
- EC2, ECS, ECR, IAM permissions
- Default VPC with public subnets

## 🔧 Development

### Project structure

```
src/
├── main/java/com/llm/serving/
│   ├── LlmChatServiceApplication.java
│   ├── config/
│   │   ├── LlmProperties.java
│   │   └── WebConfig.java
│   ├── controller/
│   │   └── ChatController.java
│   ├── dto/
│   │   ├── ChatRequest.java
│   │   └── ChatResponse.java
│   ├── exception/
│   │   └── GlobalExceptionHandler.java
│   └── service/
│       └── LlmChatService.java
└── main/resources/
    ├── application.properties
    ├── application-docker.properties
    └── static/
        └── index.html
```

### Testing

```bash
# Run tests
mvn test

# Run with test profile
mvn spring-boot:run -Dspring-boot.run.profiles=test
```

### Building

```bash
# Clean build
mvn clean package

# Skip tests
mvn clean package -DskipTests

# Build Docker image
docker build -t llm-chat-service .
```

## 📊 Monitoring and observability

### Health checks

- Application: `http://localhost:8080/actuator/health`
- Ollama: `http://localhost:11434/api/version`

### Metrics

- Prometheus metrics: `http://localhost:8080/actuator/prometheus`
- Application info: `http://localhost:8080/actuator/info`

### Logging

- Application logs include request/response times
- Ollama integration logging
- Error tracking with stack traces

## 🔒 Security considerations

### Production deployment

1. **Network security**
   - Use private subnets for Ollama
   - Implement proper security groups
   - Use Application Load Balancer with SSL

2. **Authentication**
   - Add API key authentication
   - Implement rate limiting
   - Use WAF for additional protection

3. **Monitoring**
   - Set up CloudWatch alarms
   - Monitor costs and usage
   - Implement log aggregation

## 🧪 Testing the Chat

### Using curl

```bash
# Basic chat request
curl -X POST http://localhost:8080/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the capital of France?",
    "use_system_template": true,
    "temperature": 0.7
  }'

# Health check
curl http://localhost:8080/api/v1/chat/health
```

### Using the Web application

1. Open `http://localhost:8080` in your browser
2. Type your message in the input field
3. Adjust parameters using the option buttons
4. Click send or press Enter

## 🔧 Troubleshooting

### Common Issues

1. **Ollama not responding**
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/version
   
   # Restart Ollama
   ollama serve
   ```

2. **Model not found**
   ```bash
   # Pull the model manually
   ollama pull llama3
   
   # List available models
   ollama list
   ```

3. **Out of memory**
   - Use a larger EC2 instance type (m5.xlarge or larger)
   - Increase Docker memory limits
   - Check available system memory

4. **Slow responses**
   - Check system resources (CPU, memory)
   - Consider using GPU instances for faster inference
   - Adjust temperature and max_tokens settings

### Logs

```bash
# Application logs
docker-compose logs llm-chat-service

# Ollama logs
docker-compose logs ollama

# System logs (EC2)
sudo journalctl -u ollama -f
```

## 📋 Requirements

### System sequirements

- **CPU**: Minimum 4 cores (8+ recommended for production)
- **Memory**: Minimum 8GB RAM (16GB+ recommended)
- **Storage**: 20GB+ for models and application
- **Network**: Stable internet connection for model downloads

### Software

- Java 17+
- Maven 3.6+
- Docker 20.10+
- Docker Compose 2.0+
- Ollama (latest version)

## 🚀 Performance optimization

### JVM Tuning

```bash
export JAVA_OPTS="-Xmx4g -Xms2g -XX:+UseG1GC"
```

### Ollama optimization

- Use GPU instances (p3, g4 series on AWS)
- Increase Ollama memory limits
- Use SSD storage for model files

## 📚 Additional resources

- [Ollama Documentation](https://ollama.ai/docs)
- [Spring AI Documentation](https://docs.spring.io/spring-ai/reference/)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Ensure all prerequisites are installed
4. Verify network connectivity to Ollama

---

**Note**: This application is designed for learning purposes. For production use, implement additional security measures and scalability considerations.
