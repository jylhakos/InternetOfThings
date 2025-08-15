# Microservices with FastAPI + (React)

Microservices built with FastAPI backend, React frontend, JWT authentication, Redis caching, gRPC internal communication, and debugging tools.

## Table of Contents

- [Architecture](#architecture)
- [Setup](#setup)
- [Microservices](#microservices)
- [Debugging](#debugging)
- [Performance Metrics](#performance-metrics)
- [Development Pipeline](#development-pipeline)
- [Data Flow Diagram](#data-flow-diagram)
- [DevOps Guide: Production-Ready FastAPI Deployment](#devops-guide-production-ready-fastapi-deployment)
- [References](#references)

## Architecture

This project implements microservices architecture.

- **FastAPI**: RESTful API gateway and microservices
- **React + Vite**: Single Page Application frontend
- **JWT**: Authentication and session management
- **Redis**: Session caching and performance optimization
- **PostgreSQL**: Primary database (Dockerized)
- **gRPC**: Internal microservice communication
- **Nginx**: Reverse proxy with SSL/TLS termination
- **Docker**: Containerization for all services

### Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React SPA     │    │     Nginx        │    │   FastAPI       │
│   (Vite)        │◄──►│  Reverse Proxy   │◄──►│   Gateway       │
│                 │    │   (SSL/TLS)      │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│     Redis       │    │   PostgreSQL     │    │   Auth Service  │
│    (Cache)      │◄──►│   (Database)     │◄──►│    (gRPC)       │
│                 │    │   (Docker)       │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
                                               ┌─────────────────┐
                                               │  User Service   │
                                               │    (gRPC)       │
                                               │                 │
                                               └─────────────────┘
```

#### **Backend (FastAPI)**

- **FastAPI** with async/await support
- 🔒 **JWT Authentication** with secure session management
- **Redis Caching** for performance optimization
- **PostgreSQL Database** with SQLAlchemy ORM
- 🔧 **gRPC Integration** points for internal communication
- **Prometheus Metrics** collection
- 🔍 **OpenTelemetry Tracing** for observability
- ⚡ **Performance Middleware** with timing
- 🛡️ **CORS Configuration** for secure cross-origin requests
- **Pydantic Validation** for request/response models

#### **Frontend (React + Vite)**

- ⚛️ **React SPA** with TypeScript support
- ⚡ **Vite Development Server** with HMR and instant reloads
- **Tailwind CSS** for responsive, modern UI design
- 🔐 **JWT Authentication** with login/register forms
- **Phone Number Login** with password
- **Redux Toolkit** for state management
- **React Hook Form** with Zod validation
- **Toast Notifications** for user feedback
- 🔄 **Axios HTTP Client** with request/response interceptors

#### **Infrastructure & DevOps**

- 🐳 **Docker Containerization** for all services
- 🔄 **Docker Compose** orchestration
- 🌐 **Nginx Reverse Proxy** with SSL/TLS termination
- 🔒 **SSL/HTTPS Security** with security headers
- 📈 **Monitoring Stack** (Prometheus + Grafana + Jaeger)
- 🔧 **Jenkins CI/CD Pipeline** automation
- **Testing** (unit, integration, load)
- 🔍 **Code Quality Tools** (linting, formatting, security scans)
- **Make Automation** for development workflows

#### **Security**

- 🔐 **JWT Token Authentication** with Redis session storage
- 🛡️ **Rate Limiting** to prevent abuse
- 🔒 **HTTPS/SSL Encryption** in production
- 🚫 **CORS Protection** with configurable origins
- 🔧 **Security Headers** (HSTS, CSP, XSS protection)
- 🔐 **Password Hashing** with bcrypt
- 🕵️ **Security Scanning** with Bandit

#### **Development**

- 🔧 **VS Code Integration** with debugging configurations
- **Hot Module Replacement** for instant development feedback
- **Test-Driven Development** with pytest and Vitest
- 📊 **Performance Profiling** tools (py-spy, cProfile)
- 📝 **Logging** with structured logs
- 🔍 **API Documentation** with interactive Swagger UI
- 🛠️ **Make Commands** for common development tasks

### 📁 Project Structure

```
FastAPI/
├── frontend/                          # React + Vite Frontend
│   ├── src/
│   │   ├── components/Layout.tsx      # Main layout with navigation
│   │   ├── pages/
│   │   │   ├── Login.tsx             # Phone number login
│   │   │   ├── Register.tsx          # User registration
│   │   │   ├── Dashboard.tsx         # Main dashboard
│   │   │   └── Profile.tsx           # User profile
│   │   ├── services/api.ts           # Axios API client
│   │   ├── store/                    # Redux state management
│   │   └── App.tsx                   # Main app component
│   ├── vite.config.ts               # Vite configuration
│   ├── tailwind.config.js           # Tailwind CSS config
│   └── package.json                 # Frontend dependencies
├── tests/                           # Backend tests
│   ├── test_main.py                # Unit tests
│   └── load_test.py                # Locust load tests
├── .vscode/                        # VS Code configuration
│   ├── launch.json                 # Debug configurations
│   ├── settings.json               # Editor settings
│   └── fastapi-microservices.code-workspace
├── main.py                         # FastAPI application
├── requirements.txt                # Python dependencies
├── docker-compose.yml              # Development services
├── Dockerfile                      # Backend container
├── nginx.conf                      # Production Nginx config
├── Makefile                        # Development automation
├── Jenkinsfile                     # CI/CD pipeline
├── performance-test.sh             # cURL performance testing
└── .env.example                    # Environment variables template
```

### Quick Start

1. **Clone and Setup**:

   ```bash
   make install          # Install all dependencies
   make dev-start        # Start infrastructure services
   ```

2. **Start Development**:

   ```bash
   # Terminal 1: Backend
   make backend-dev

   # Terminal 2: Frontend
   make frontend-dev
   ```

3. **Access Applications**:

   - **Frontend**: http://localhost:5173
   - **Backend API**: http://localhost:8000
   - **API Docs**: http://localhost:8000/docs

4. **Run Tests**:
   ```bash
   make test             # All tests
   make test-load        # Performance tests
   ```

### 🔧 Features

- **Phone Number Authentication** as requested
- **React SPA** with modern TypeScript setup
- **JWT Session Management** with Redis caching
- **SSL/HTTPS Diagrams** and Nginx configuration
- **gRPC Architecture** integration points
- **Performance Monitoring** with metrics and tracing
- **DevOps Pipeline** with comprehensive CI/CD
- **cURL Testing** with performance measurement
- **VS Code Debugging** configurations
- **Docker Containerization** for all services

## Setup

### Prerequisites

- Python 3.9+
- Node.js 18+
- Docker & Docker Compose
- Git
- Redis server
- PostgreSQL (or Docker)

### 1. Virtual Environment Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
# venv\Scripts\activate  # Windows

# Upgrade pip
pip install --upgrade pip
```

### 2. Backend Dependencies

```bash
# Install FastAPI and dependencies
pip install fastapi uvicorn[standard]
pip install sqlalchemy psycopg2-binary
pip install redis python-jose[cryptography]
pip install python-multipart bcrypt
pip install grpcio grpcio-tools
pip install prometheus-client
pip install opentelemetry-api opentelemetry-sdk
pip install opentelemetry-instrumentation-fastapi
pip install prometheus-fastapi-instrumentator
pip install py-spy cProfile

# Save dependencies
pip freeze > requirements.txt
```

### 3. Frontend Setup (React + Vite)

#### What is Vite?

Vite is a frontend build tool that provides a fast development experience for web projects.

- **Instant Server Start**: Leverages native ES modules for lightning-fast cold starts
- **Hot Module Replacement (HMR)**: Updates modules instantly without losing state
- **Optimized Builds**: Uses Rollup for production builds with tree-shaking
- **TypeScript Support**: Built-in TypeScript support without configuration
- **Plugin Ecosystem**: Rich ecosystem of plugins for various frameworks

#### Create React Application with Vite

```bash
# Navigate to project root
cd /home/laptop/EXERCISES/IOT/InternetOfThings/Frameworks/Backend/FastAPI

# Create React app with TypeScript template
npm create vite@latest frontend -- --template react-ts
cd frontend

# Install dependencies
npm install

# Install additional packages for authentication and state management
npm install axios @reduxjs/toolkit react-redux react-router-dom
npm install react-hook-form @hookform/resolvers zod
npm install tailwindcss postcss autoprefixer
npm install lucide-react react-hot-toast

# Install development dependencies
npm install -D @types/node @testing-library/react @testing-library/jest-dom vitest

# Initialize Tailwind CSS
npx tailwindcss init -p
```

#### Frontend Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── Layout.tsx           # Main layout component
│   ├── pages/
│   │   ├── Login.tsx            # Login page with phone/password
│   │   ├── Register.tsx         # Registration page
│   │   ├── Dashboard.tsx        # Main dashboard
│   │   └── Profile.tsx          # User profile page
│   ├── services/
│   │   └── api.ts               # Axios API client with interceptors
│   ├── store/
│   │   ├── store.ts             # Redux toolkit store configuration
│   │   └── authSlice.ts         # Authentication state slice
│   ├── App.tsx                  # Main app component with routing
│   ├── main.tsx                 # Entry point
│   └── index.css                # Global styles with Tailwind
├── public/
├── index.html
├── vite.config.ts               # Vite configuration
├── tailwind.config.js           # Tailwind CSS configuration
├── postcss.config.js            # PostCSS configuration
├── tsconfig.json                # TypeScript configuration
└── package.json
```

#### Frontend Environment Variables

Create `frontend/.env` file:

```bash
# API Configuration
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=FastAPI Microservices
VITE_APP_VERSION=1.0.0

# Development Settings
VITE_DEBUG=true
VITE_LOG_LEVEL=debug
```

#### Vite Configuration for FastAPI Integration

The `vite.config.ts` includes proxy configuration for seamless development:

```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
```

#### Start Development Servers

```bash
# Terminal 1: Start FastAPI backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start Vite development server
cd frontend
npm run dev
```

#### Building for Production

```bash
# Build optimized production bundle
npm run build

# Preview production build locally
npm run preview

# Production build outputs to frontend/dist/
ls -la frontend/dist/
```

### 4. Docker Setup

```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Or individual containers
docker run -d --name postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=microservices \
  -p 5432:5432 postgres:14

docker run -d --name redis \
  -p 6379:6379 redis:alpine
```

### 5. Environment Variables

Create `.env` file:

```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/microservices
REDIS_URL=redis://localhost:6379

# JWT
SECRET_KEY=your-super-secret-jwt-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# gRPC
GRPC_PORT=50051
AUTH_SERVICE_URL=localhost:50051

# Application
DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## Microservices

### What are Microservices?

Microservices architecture is a design pattern that structures an application as a collection of relatively coupled services.

- **Single Responsibility**: Handles one business capability
- **Independent Deployment**: Can be deployed separately
- **Technology Agnostic**: Can use different tech stacks
- **Fault Isolation**: Failure in one service doesn't crash others
- **Scalable**: Services can be scaled independently

### Microservices Architecture

1. **API Gateway (FastAPI)**

   - Entry point for all external requests
   - Handles authentication and routing
   - Rate limiting and request validation

2. **Authentication Service (gRPC)**

   - User registration and login
   - JWT token generation and validation
   - Password hashing and verification

3. **User Service (gRPC)**

   - User profile management
   - CRUD operations for user data
   - User preferences and settings

4. **Caching Layer (Redis)**
   - Session storage
   - Temporary data caching
   - Rate limiting counters

### Internal vs External Communication

- **External (HTTP/HTTPS)**: Client ↔ API Gateway
- **Internal (gRPC)**: Gateway ↔ Microservices
- **Database**: Direct connections with connection pooling

## Debugging

### Visual Studio Code Setup

#### 1. Launch Configuration (.vscode/launch.json)

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI Debug",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/main.py",
      "console": "integratedTerminal",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      },
      "args": []
    },
    {
      "name": "FastAPI Uvicorn",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
      "console": "integratedTerminal"
    },
    {
      "name": "Attach to PID",
      "type": "python",
      "request": "attach",
      "processId": "${command:pickProcess}"
    }
  ]
}
```

#### 2. VS Code Settings (.vscode/settings.json)

```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true
}
```

### Debugging Techniques

#### 1. Breakpoints

Set breakpoints in VS Code by clicking on the line number gutter or pressing F9.

#### 2. Print Statements

```python
@app.get("/debug/{item_id}")
async def debug_endpoint(item_id: int):
    print(f"Debugging Value: {item_id}")
    return {"item_id": item_id}
```

#### 3. Python Debugger

```python
def debug_function():
    x = 10
    breakpoint()  # Built-in debugger
    y = x * 2
    return y
```

#### 4. Logging Setup

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    logger.info(f"Fetching item with ID: {item_id}")
    logger.debug(f"Debug info for item: {item_id}")
    return {"item_id": item_id}
```

#### 5. Pydantic Debugging

```python
from pydantic import BaseModel, ValidationError

class Item(BaseModel):
    name: str
    price: float
    quantity: int = 1

@app.post("/items/")
async def create_item(item: Item):
    try:
        # Pydantic automatically validates
        logger.info(f"Created item: {item.dict()}")
        return item
    except ValidationError as e:
        logger.error(f"Validation error: {e.errors()}")
        raise HTTPException(status_code=422, detail=e.errors())
```

### Getting Process ID (Linux/Debian)

```bash
# Find FastAPI process
ps aux | grep uvicorn
ps aux | grep python | grep main.py

# Using pgrep
pgrep -f uvicorn
pgrep -f "main.py"

# Get detailed process info
ps -eo pid,ppid,cmd,%mem,%cpu | grep uvicorn

# Using netstat to find process by port
netstat -tlnp | grep 8000
lsof -i :8000
```

### Attaching Debugger to Running Process

1. Start your FastAPI app: `uvicorn main:app --reload`
2. Find the PID: `ps aux | grep uvicorn`
3. In VS Code: Run > Start Debugging > "Attach to PID"
4. Select the uvicorn process

## Performance Metrics

### 1. OpenTelemetry Integration

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Setup tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)
```

### 2. Prometheus Metrics

```python
from prometheus_fastapi_instrumentator import Instrumentator

# Initialize instrumentator
instrumentator = Instrumentator()
instrumentator.instrument(app)
instrumentator.expose(app)

# Custom metrics
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    'app_requests_total',
    'Total app requests',
    ['method', 'endpoint']
)

REQUEST_LATENCY = Histogram(
    'app_request_duration_seconds',
    'Request latency'
)
```

### 3. Custom Timing Middleware

```python
import time
from fastapi import Request

@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"Request processed in {process_time:.4f} seconds")
    return response
```

### 4. Profiling Tools

#### cProfile

```python
import cProfile
import pstats
from functools import wraps

def profile(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        stats.print_stats(10)  # Top 10
        return result
    return wrapper

@profile
@app.get("/heavy-operation")
async def heavy_operation():
    # Simulate heavy work
    return {"status": "completed"}
```

#### py-spy (External Profiling)

```bash
# Install py-spy
pip install py-spy

# Profile running FastAPI process
py-spy record -o profile.svg --pid <PID>
py-spy record -o profile.svg --duration 30 -- python main.py

# Live profiling
py-spy top --pid <PID>
```

### 5. APM Tools Integration

```python
# Example with custom APM
import asyncio
from datetime import datetime

class PerformanceMonitor:
    def __init__(self):
        self.metrics = []

    async def log_performance(self, endpoint: str, duration: float, status: int):
        metric = {
            "timestamp": datetime.utcnow(),
            "endpoint": endpoint,
            "duration": duration,
            "status": status
        }
        self.metrics.append(metric)

        # Send to APM service
        await self.send_to_apm(metric)

    async def send_to_apm(self, metric):
        # Implementation for sending to APM service
        pass

monitor = PerformanceMonitor()
```

## Development Pipeline

### Jenkins Pipeline

```groovy
pipeline {
    agent any

    environment {
        PYTHON_VERSION = '3.9'
        NODE_VERSION = '18'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python') {
            steps {
                sh '''
                    python3 -m venv venv
                    source venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Python Tests') {
            steps {
                sh '''
                    source venv/bin/activate
                    pytest tests/ --junitxml=results.xml --cov=./ --cov-report=xml
                '''
            }
        }

        stage('Frontend Setup') {
            steps {
                dir('frontend') {
                    sh '''
                        npm install
                        npm run build
                        npm run test
                    '''
                }
            }
        }

        stage('Security Scan') {
            steps {
                sh '''
                    source venv/bin/activate
                    pip install bandit
                    bandit -r . -f json -o bandit-report.json
                '''
            }
        }

        stage('Docker Build') {
            steps {
                script {
                    docker.build("fastapi-app:${env.BUILD_ID}")
                }
            }
        }

        stage('Deploy to Staging') {
            when {
                branch 'develop'
            }
            steps {
                sh 'docker-compose -f docker-compose.staging.yml up -d'
            }
        }

        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                input 'Deploy to production?'
                sh 'docker-compose -f docker-compose.prod.yml up -d'
            }
        }
    }

    post {
        always {
            junit 'results.xml'
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: false,
                keepAll: true,
                reportDir: 'htmlcov',
                reportFiles: 'index.html',
                reportName: 'Coverage Report'
            ])
        }
    }
}
```

### Setup: Development and Production

#### Prerequisites for DevOps

- **Linux/Debian System** (Ubuntu 20.04+ recommended)
- **Docker & Docker Compose** (v20.10+)
- **Python 3.9+** with virtual environment support
- **Node.js 18+** with npm
- **Git** for version control
- **Make** for build automation
- **nginx** for reverse proxy (production)

#### Local Development Environment (Linux/Debian)

```bash
# 1. Install system dependencies
sudo apt update && sudo apt install -y \
    python3 python3-venv python3-pip \
    nodejs npm \
    docker.io docker-compose \
    nginx \
    curl wget \
    build-essential \
    git

# 2. Configure Docker (add user to docker group)
sudo usermod -aG docker $USER
newgrp docker

# 3. Verify installations
python3 --version  # Should be 3.9+
node --version     # Should be 18+
docker --version   # Should be 20.10+
```

#### Development Workflow

```bash
# 1. Clone and setup project
git clone <repository-url>
cd FastAPI

# 2. Backend setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Frontend setup
cd frontend
npm install
cd ..

# 4. Start infrastructure services
docker-compose up -d postgres redis

# 5. Wait for services to be ready
echo "Waiting for PostgreSQL..."
until docker exec fastapi_postgres pg_isready -U postgres; do sleep 1; done
echo "Waiting for Redis..."
until docker exec fastapi_redis redis-cli ping; do sleep 1; done

# 6. Start development servers (use separate terminals or tmux)
# Terminal 1: Backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Optional monitoring
docker-compose logs -f
```

#### Development with VS Code

1. **Install VS Code Extensions**:

   ```bash
   code --install-extension ms-python.python
   code --install-extension bradlc.vscode-tailwindcss
   code --install-extension esbenp.prettier-vscode
   code --install-extension ms-vscode.vscode-typescript-next
   ```

2. **Open Workspace**:

   ```bash
   code .vscode/fastapi-microservices.code-workspace
   ```

3. **Debug Configuration**:
   - Use F5 to start debugging FastAPI with VS Code
   - Breakpoints work in both Python and TypeScript
   - Integrated terminal for testing

#### Production Deployment Pipeline

```bash
# 1. Build production images
docker-compose -f docker-compose.prod.yml build

# 2. Run security scans
docker run --rm -v "$(pwd)":/app \
  securecodewarrior/docker-image-scanner:latest \
  scan /app/Dockerfile

# 3. Deploy to production
docker-compose -f docker-compose.prod.yml up -d

# 4. Verify deployment
curl -f https://your-domain.com/health
curl -f https://your-domain.com/metrics
```

#### Development Testing Workflow

```bash
# Backend Tests
source venv/bin/activate
pytest tests/ -v --cov=./ --cov-report=html
python -m pytest tests/integration/ -v

# Frontend Tests
cd frontend
npm test
npm run build  # Test production build
npm run preview  # Test production build locally

# Load Testing
./performance-test.sh
locust -f tests/load_test.py --headless -u 50 -r 10 -t 30s

# Security Testing
bandit -r . -f json -o bandit-report.json
npm audit
```

#### Environment Management

```bash
# Development
cp .env.example .env
cp frontend/.env.example frontend/.env

# Staging
cp .env.example .env.staging
# Edit .env.staging with staging configurations

# Production
cp .env.example .env.production
# Edit .env.production with production configurations
```

#### Nginx Configuration for Production

Create `/etc/nginx/sites-available/fastapi-microservices`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/ssl/certs/your-domain.crt;
    ssl_certificate_key /etc/ssl/private/your-domain.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Frontend (React build)
    location / {
        root /var/www/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }

    # Metrics (restrict access)
    location /metrics {
        proxy_pass http://localhost:8000/metrics;
        allow 127.0.0.1;
        allow your-monitoring-ip;
        deny all;
    }
}
```

#### SSL Certificate Setup

```bash
# Using Let's Encrypt (Certbot)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com

# Or using self-signed for development
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/your-domain.key \
    -out /etc/ssl/certs/your-domain.crt
```

#### Monitoring and Observability Setup

```bash
# Start monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# Access dashboards
echo "Prometheus: http://localhost:9090"
echo "Grafana: http://localhost:3000 (admin/admin)"
echo "Jaeger: http://localhost:16686"

# Import Grafana dashboards
curl -X POST \
  -H 'Content-Type: application/json' \
  -d '@monitoring/grafana/fastapi-dashboard.json' \
  http://admin:admin@localhost:3000/api/dashboards/db
```

#### Continuous Integration/Continuous Deployment (CI/CD)

The Jenkins pipeline includes:

1. **Code Quality Checks**: Linting, type checking, security scanning
2. **Testing**: Unit tests, integration tests, load tests
3. **Building**: Docker images for both frontend and backend
4. **Deployment**: Automated deployment to staging/production
5. **Monitoring**: Post-deployment health checks and monitoring setup

#### Troubleshooting

```bash
# Check service status
docker-compose ps
docker-compose logs fastapi
docker-compose logs postgres

# Check network connectivity
curl -f http://localhost:8000/health
curl -f http://localhost:5173

# Check database connection
docker exec -it fastapi_postgres psql -U postgres -d microservices -c "\dt"

# Check Redis connection
docker exec -it fastapi_redis redis-cli ping

# Check disk space
df -h
docker system prune -f

# Check memory usage
free -h
docker stats
```

#### Performance Optimization

```bash
# Backend optimization
source venv/bin/activate
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# Frontend optimization
cd frontend
npm run build
npm run preview

# Database optimization
docker exec fastapi_postgres psql -U postgres -c "
    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_phone ON users(phone);
    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_token ON sessions(token);
"

# Redis optimization
docker exec fastapi_redis redis-cli CONFIG SET maxmemory 256mb
docker exec fastapi_redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

### Local Development Workflow Summary

```bash
# Quick start (run from project root)
make dev-start    # Start all services
make dev-stop     # Stop all services
make dev-reset    # Reset all data and restart
make test         # Run all tests
make lint         # Run linting
make build        # Build for production
```

## Data Flow Diagram

### SSL/HTTPS Security with Nginx

The following diagram shows the complete security architecture with SSL/TLS termination at Nginx:

```
Internet Security Flow:
┌─────────────────┐   HTTPS (SSL/TLS)   ┌──────────────────┐   HTTP (Internal)   ┌─────────────────┐
│   Client        │   Port 443          │     Nginx        │   Port 8000         │   FastAPI       │
│   (Browser)     │ ──────────────────► │  Reverse Proxy   │ ──────────────────► │   Gateway       │
│   React SPA     │                     │   SSL Termination│                     │                 │
└─────────────────┘                     └──────────────────┘                     └─────────────────┘
       │                                         │                                         │
       │ ┌─ Certificate Verification             │                                         │
       │ ├─ TLS 1.2/1.3 Encryption               │                                         │
       │ └─ HSTS Headers                         │                                         │
       │                                         │                                         │
       ▼                                         ▼                                         ▼
┌─────────────────┐                     ┌──────────────────┐                     ┌─────────────────┐
│  Local Storage  │                     │  Load Balancer   │                     │  CORS Headers   │
│  JWT Tokens     │                     │  Rate Limiting   │                     │  Authentication │
│  Session Data   │                     │  Security Headers│                     │  Authorization  │
└─────────────────┘                     └──────────────────┘                     └─────────────────┘
```

### Communication Flow: Frontend to Backend

```
React + Vite Development Flow:
┌─────────────────┐   Vite Dev Server   ┌─────────────────┐   Proxy to API      ┌─────────────────┐
│   Developer     │   Port 5173         │   Vite Proxy    │   Port 8000         │   FastAPI       │
│   Browser       │ ──────────────────► │   Dev Server    │ ──────────────────► │   Backend       │
│                 │                     │   (HMR/Reload)  │                     │                 │
└─────────────────┘                     └─────────────────┘                     └─────────────────┘

Production Deployment Flow:
┌─────────────────┐   HTTPS/443         ┌─────────────────┐   Static Files      ┌─────────────────┐
│   User Browser  │ ──────────────────► │     Nginx       │ ──────────────────► │   React Build   │
│                 │                     │                 │   /static/*         │   (dist/)       │
└─────────────────┘                     │                 │                     └─────────────────┘
                                        │                 │   API Requests
                                        │                 │ ──────────────────► ┌─────────────────┐
                                        │                 │   /api/*            │   FastAPI       │
                                        └─────────────────┘                     │   Backend       │
                                                                                └─────────────────┘
```

### Authentication Flow with JWT and Redis

```
Login Process Flow:
┌─────────────────┐   1. Login Request  ┌─────────────────┐   2. Validate       ┌─────────────────┐
│   React App     │ ──────────────────► │   FastAPI       │ ──────────────────► │   Auth Service  │
│   Login Form    │   POST /auth/login  │   Gateway       │   gRPC Call         │   (Password)    │
└─────────────────┘                     └─────────────────┘                     └─────────────────┘
       │                                         │                                         │
       │                                         │ 3. Generate JWT                         │
       │                                         │ ──────────────────►                     │
       │                                         │                                         │
       │ 4. JWT Token                            │ 5. Cache Session                        │
       │ ◄───────────────────────────────────────│ ──────────────────►                     │
       │                                         │                   ┌─────────────────┐   │
       ▼                                         ▼                   │     Redis       │   │
┌─────────────────┐                     ┌─────────────────┐          │   Session       │   │
│  localStorage   │                     │  Response with  │          │   Storage       │   │
│  JWT Storage    │                     │  HTTP-Only      │          └─────────────────┘   │
│  Auto Headers   │                     │  Secure Cookie  │                                │
└─────────────────┘                     └─────────────────┘ ◄──────────────────────────────┘
```

### External HTTP Requests

```
Client Request Flow:
┌─────────────┐    HTTPS     ┌─────────────┐    HTTP      ┌─────────────┐
│   Browser   │ ──────────►  │    Nginx    │ ──────────►  │   FastAPI   │
│   (React)   │              │   Proxy     │              │   Gateway   │
└─────────────┘              └─────────────┘              └─────────────┘
       │                                                          │
       │                                                          │
       ▼                                                          ▼
┌─────────────┐                                          ┌─────────────┐
│ JWT Token   │                                          │ Validate    │
│ Storage     │                                          │ JWT Token   │
└─────────────┘                                          └─────────────┘
```

### Internal gRPC Communication

```
Internal Service Communication:
┌─────────────┐    gRPC      ┌─────────────┐    gRPC      ┌─────────────┐
│   FastAPI   │ ──────────►  │    Auth     │ ──────────►  │    User     │
│   Gateway   │              │  Service    │              │  Service    │
└─────────────┘              └─────────────┘              └─────────────┘
       │                            │                            │
       │                            │                            │
       ▼                            ▼                            ▼
┌─────────────┐              ┌─────────────┐              ┌─────────────┐
│    Redis    │              │    Redis    │              │ PostgreSQL  │
│   Cache     │              │   Sessions  │              │  Database   │
└─────────────┘              └─────────────┘              └─────────────┘
```

### CRUD Operations Data Flow

```
CRUD Operation Example (User Registration):
┌─────────────┐
│   POST      │
│ /register   │
└──────┬──────┘
       │
       ▼
┌─────────────┐    1. Validate    ┌─────────────┐
│   FastAPI   │ ────────────────► │  Pydantic   │
│   Endpoint  │                   │  Model      │
└──────┬──────┘                   └─────────────┘
       │
       │ 2. Hash Password
       ▼
┌─────────────┐    3. gRPC Call   ┌─────────────┐
│   Auth      │ ◄──────────────── │    Auth     │
│  Service    │                   │   Service   │
└──────┬──────┘                   └─────────────┘
       │
       │ 4. Store User
       ▼
┌─────────────┐    5. Cache       ┌─────────────┐
│ PostgreSQL  │ ────────────────► │    Redis    │
│  Database   │                   │   Cache     │
└─────────────┘                   └─────────────┘
```

## DevOps Guide: Production-Ready FastAPI Deployment

### Virtual Environment Setup for Python (Debian/Ubuntu)

#### Step 1: System Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python development packages
sudo apt install -y \
    python3 python3-dev python3-venv python3-pip \
    build-essential \
    libpq-dev \
    pkg-config \
    curl wget git

# Verify Python version (should be 3.9+)
python3 --version
```

#### Step 2: Virtual Environment Creation and Management

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment (Linux/macOS)
source venv/bin/activate

# Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# Install FastAPI and production dependencies
pip install fastapi uvicorn[standard]
pip install sqlalchemy psycopg2-binary
pip install redis python-jose[cryptography]
pip install python-multipart bcrypt
pip install grpcio grpcio-tools
pip install prometheus-client
pip install opentelemetry-api opentelemetry-sdk
pip install opentelemetry-instrumentation-fastapi
pip install prometheus-fastapi-instrumentator

# For production ASGI server
pip install gunicorn

# Save requirements
pip freeze > requirements.txt

# Deactivate when done
deactivate
```

#### Step 3: Docker Infrastructure Setup

```bash
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Start PostgreSQL container
docker run -d --name postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=microservices \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:14

# Start Redis container
docker run -d --name redis \
  -p 6379:6379 \
  -v redis_data:/data \
  redis:7-alpine redis-server --appendonly yes

# Verify containers are running
docker ps
```

#### Step 4: FastAPI Application Startup

```bash
# Activate virtual environment
source venv/bin/activate

# Development server (single process)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production server (multiple workers)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# With specific worker configuration
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
```

### Jenkins Pipeline Setup for Python Virtual Environments

#### Jenkins Environment Configuration

```groovy
// Jenkinsfile for FastAPI with Virtual Environment
pipeline {
    agent any

    environment {
        PYTHON_VERSION = '3.9'
        VENV_PATH = "${WORKSPACE}/venv"
    }

    stages {
        stage('Setup Python Virtual Environment') {
            steps {
                script {
                    // Create virtual environment
                    sh """
                        python3 -m venv ${VENV_PATH}
                        . ${VENV_PATH}/bin/activate
                        pip install --upgrade pip setuptools wheel
                        pip install -r requirements.txt
                    """
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                sh """
                    . ${VENV_PATH}/bin/activate
                    pip install pytest pytest-cov bandit safety
                    pip freeze > installed_packages.txt
                """
            }
        }

        stage('Security Scanning') {
            steps {
                sh """
                    . ${VENV_PATH}/bin/activate
                    bandit -r . -f json -o bandit-report.json || true
                    safety check --json --output safety-report.json || true
                """
            }
        }

        stage('Testing') {
            steps {
                sh """
                    . ${VENV_PATH}/bin/activate
                    pytest tests/ -v --cov=./ --cov-report=html --cov-report=xml
                """
            }
        }

        stage('Performance Testing') {
            steps {
                sh """
                    . ${VENV_PATH}/bin/activate
                    # Start FastAPI in background for testing
                    uvicorn main:app --host 0.0.0.0 --port 8000 &
                    SERVER_PID=\$!
                    sleep 10

                    # Run performance tests
                    ./performance-test.sh

                    # Cleanup
                    kill \$SERVER_PID
                """
            }
        }
    }

    post {
        always {
            // Cleanup virtual environment
            sh "rm -rf ${VENV_PATH}"
        }
    }
}
```

### Testing with cURL - Comprehensive Test Cases

#### System Health and Performance Testing

```bash
# Create timing format file for detailed metrics
cat > curl-format.txt << 'EOF'
     time_namelookup:  %{time_namelookup}s\n
        time_connect:  %{time_connect}s\n
     time_appconnect:  %{time_appconnect}s\n
    time_pretransfer:  %{time_pretransfer}s\n
       time_redirect:  %{time_redirect}s\n
  time_starttransfer:  %{time_starttransfer}s\n
                     ----------\n
          time_total:  %{time_total}s\n
           http_code:  %{http_code}\n
       response_size:  %{size_download} bytes\n
EOF

# Basic health check
curl -X GET http://localhost:8000/health \
  -w "@curl-format.txt" \
  -o /dev/null -s

# Metrics endpoint
curl -X GET http://localhost:8000/metrics \
  -w "Metrics fetch time: %{time_total}s\n" \
  -s | head -20

# API documentation
curl -X GET http://localhost:8000/docs \
  -w "Docs load time: %{time_total}s\n" \
  -o /dev/null -s
```

#### Authentication Flow Testing

```bash
# 1. User Registration
echo "=== Testing User Registration ==="
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+1234567890",
    "password": "SecurePassword123!",
    "email": "devops@example.com",
    "full_name": "DevOps Engineer"
  }' \
  -w "Registration time: %{time_total}s, Status: %{http_code}\n" \
  -v

# 2. User Login (get JWT token)
echo "=== Testing User Login ==="
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=%2B1234567890&password=SecurePassword123!" \
  -s | jq -r .access_token)

echo "JWT Token: ${TOKEN:0:50}..."

# 3. Profile Access (authenticated)
echo "=== Testing Authenticated Profile Access ==="
curl -X GET http://localhost:8000/users/profile \
  -H "Authorization: Bearer $TOKEN" \
  -w "Profile fetch time: %{time_total}s, Status: %{http_code}\n" \
  -s | jq .

# 4. Token Refresh
echo "=== Testing Token Refresh ==="
curl -X POST http://localhost:8000/auth/refresh \
  -H "Authorization: Bearer $TOKEN" \
  -w "Token refresh time: %{time_total}s\n" \
  -s
```

#### Load Testing and Stress Testing

```bash
#!/bin/bash
# comprehensive-load-test.sh

echo "=== FastAPI Load Testing Suite ==="

BASE_URL="http://localhost:8000"
CONCURRENT_USERS=50
REQUESTS_PER_USER=20
DURATION=60

# Test 1: Health endpoint load test
echo "1. Health Endpoint Load Test"
seq 1 $((CONCURRENT_USERS * REQUESTS_PER_USER)) | \
xargs -n1 -P$CONCURRENT_USERS -I{} curl -s -o /dev/null \
  -w "Request {}: %{time_total}s %{http_code}\n" \
  $BASE_URL/health | \
awk '
  /200/ { success++ }
  /[45][0-9][0-9]/ { errors++ }
  { total++; sum+=$3 }
  END {
    print "Total requests: " total
    print "Successful: " success
    print "Errors: " errors
    print "Average response time: " sum/total "s"
    print "Success rate: " (success/total)*100 "%"
  }'

# Test 2: Authentication load test
echo "2. Authentication Load Test"
for i in $(seq 1 10); do
  time curl -X POST $BASE_URL/auth/login \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=%2B1234567890&password=SecurePassword123!" \
    -s -o /dev/null \
    -w "Login $i: %{time_total}s %{http_code}\n"
done

# Test 3: Mixed endpoint testing
echo "3. Mixed Endpoint Load Test"
ENDPOINTS=(
  "$BASE_URL/health"
  "$BASE_URL/metrics"
  "$BASE_URL/auth/login"
)

for endpoint in "${ENDPOINTS[@]}"; do
  echo "Testing: $endpoint"
  seq 1 25 | xargs -n1 -P10 -I{} curl -s -o /dev/null \
    -w "%{time_total}\n" "$endpoint" | \
    awk '{ sum+=$1; count++ } END {
      print "Average: " sum/count "s for " count " requests"
    }'
done
```

#### Database and Cache Testing

```bash
# Test database connectivity through API
echo "=== Database Connectivity Test ==="
curl -X GET http://localhost:8000/users \
  -H "Authorization: Bearer $TOKEN" \
  -w "DB query time: %{time_total}s\n" \
  -s

# Test Redis cache performance
echo "=== Redis Cache Performance Test ==="
for i in {1..10}; do
  curl -X GET http://localhost:8000/users/profile \
    -H "Authorization: Bearer $TOKEN" \
    -w "Cache hit $i: %{time_total}s\n" \
    -s -o /dev/null
done
```

### FastAPI Benchmarking and Performance

#### Understanding the Performance

Based on [FastAPI's official benchmarks](https://fastapi.tiangolo.com/benchmarks/), here's the performance hierarchy:

**Performance Stack (fastest to slowest):**

1. **Uvicorn** (ASGI server)

   - Pure ASGI server implementation
   - Best performance for raw HTTP handling
   - No framework overhead

2. **Starlette** (uses Uvicorn)

   - Web microframework built on Uvicorn
   - Adds routing, middleware, and basic web features
   - Minimal performance impact over Uvicorn

3. **FastAPI** (uses Starlette)
   - API framework with automatic validation, serialization
   - OpenAPI/Swagger documentation generation
   - Type hints and dependency injection
   - Slight overhead for additional features

#### Production Deployment

```bash
# Single Process (Development)
uvicorn main:app --host 0.0.0.0 --port 8000

# Multiple Workers (Production)
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000

# Using Gunicorn with Uvicorn workers (Recommended for Production)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# With specific configuration
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --worker-connections 1000 \
  --max-requests 10000 \
  --max-requests-jitter 1000 \
  --preload \
  --timeout 120
```

#### Performance Benchmarking Scripts

```bash
#!/bin/bash
# fastapi-benchmark.sh

echo "FastAPI Production Performance Benchmark"

# Server configurations to test
declare -a servers=(
  "uvicorn main:app --host 0.0.0.0 --port 8000"
  "uvicorn main:app --workers 2 --host 0.0.0.0 --port 8001"
  "gunicorn main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8002"
)

declare -a ports=(8000 8001 8002)

for i in "${!servers[@]}"; do
  server="${servers[$i]}"
  port="${ports[$i]}"

  echo "Testing: $server"

  # Start server in background
  eval "$server" &
  server_pid=$!
  sleep 5

  # Benchmark with wrk (if available)
  if command -v wrk &> /dev/null; then
    echo "wrk benchmark results:"
    wrk -t12 -c400 -d30s "http://localhost:$port/health"
  fi

  # Benchmark with Apache Bench
  if command -v ab &> /dev/null; then
    echo "Apache Bench results:"
    ab -n 10000 -c 100 "http://localhost:$port/health"
  fi

  # Custom curl benchmark
  echo "Custom curl benchmark (1000 requests, 50 concurrent):"
  seq 1 1000 | xargs -n1 -P50 -I{} curl -s -o /dev/null \
    -w "%{time_total}\n" "http://localhost:$port/health" | \
    awk '{ sum+=$1; count++ } END {
      print "Average response time: " sum/count "s"
      print "Total requests: " count
    }'

  # Kill server
  kill $server_pid
  sleep 2
  echo "----------------------------------------"
done
```

#### Memory and Resource Monitoring

```bash
#!/bin/bash
# resource-monitor.sh

echo "FastAPI Resource Monitoring"

# Start FastAPI with multiple workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 &
SERVER_PID=$!

echo "Server PID: $SERVER_PID"
sleep 5

# Monitor for 60 seconds
for i in {1..60}; do
  echo "=== Monitoring cycle $i ==="

  # Memory usage
  ps -p $SERVER_PID -o pid,ppid,cmd,pcpu,pmem,vsz,rss

  # System resources
  echo "System Load: $(uptime | awk '{print $10, $11, $12}')"
  echo "Available Memory: $(free -h | awk '/^Mem:/ {print $7}')"

  # Network connections
  echo "Active connections: $(netstat -an | grep :8000 | wc -l)"

  # Generate load during monitoring
  curl -s -o /dev/null http://localhost:8000/health &

  sleep 1
done

# Cleanup
kill $SERVER_PID
```

### Production Optimization Checklist

#### Server Configuration

- Use multiple workers: `--workers $(nproc)`
- Configure worker connections: `--worker-connections 1000`
- Set appropriate timeouts: `--timeout 120`
- Enable preloading: `--preload`
- Configure max requests: `--max-requests 10000`

#### Database Optimization

- Use connection pooling
- Configure appropriate pool sizes
- Enable query optimization
- Set up read replicas for heavy read workloads

#### Caching Strategy

- Implement Redis for session storage
- Cache frequently accessed data
- Use appropriate TTL values
- Monitor cache hit rates

#### Monitoring and Observability

- Set up Prometheus metrics
- Configure Grafana dashboards
- Implement distributed tracing
- Set up log aggregation
- Configure alerting rules

## Debugging Tools and Performance Measurement Links

### FastAPI Resources

- **[FastAPI Debugging Guide](https://fastapi.tiangolo.com/tutorial/debugging/)** - Official debugging documentation
- **[FastAPI CORS Setup](https://fastapi.tiangolo.com/tutorial/cors/)** - Cross-Origin Resource Sharing configuration
- **[FastAPI Benchmarks](https://fastapi.tiangolo.com/benchmarks/)** - Performance comparisons
- **[Uvicorn Server Workers](https://fastapi.tiangolo.com/deployment/server-workers/)** - Production deployment guide

### Python Debugging

- **[VS Code Python Debugging](https://code.visualstudio.com/docs/python/debugging)** - Comprehensive debugging setup for Python in VS Code

### gRPC and Protocol Buffers

#### What is gRPC?

**gRPC** (gRPC Remote Procedure Calls) is a high-performance, open-source universal RPC framework developed by Google. It uses **Protocol Buffers** (protobuf) as the interface definition language and serialization format.

#### Why gRPC for Microservices?

- **High Performance**: Binary serialization, HTTP/2 transport
- **Language Agnostic**: Generated clients for multiple languages
- **Type Safety**: Strong typing with protocol buffers
- **Streaming**: Supports client, server, and bidirectional streaming
- **Load Balancing**: Built-in load balancing and service discovery
- **Authentication**: Support for various authentication mechanisms

#### Protocol Buffers Implementation

Our microservices use Protocol Buffers to define service contracts:

**Auth Service (`protos/auth.proto`):**

```protobuf
syntax = "proto3";

package auth;

service AuthService {
  rpc RegisterUser(RegisterUserRequest) returns (RegisterUserResponse);
  rpc AuthenticateUser(AuthenticateUserRequest) returns (AuthenticateUserResponse);
  rpc ValidateToken(ValidateTokenRequest) returns (ValidateTokenResponse);
  rpc RefreshToken(RefreshTokenRequest) returns (RefreshTokenResponse);
  rpc LogoutUser(LogoutUserRequest) returns (LogoutUserResponse);
}

message RegisterUserRequest {
  string phone = 1;
  string email = 2;
  string password = 3;
  string full_name = 4;
  optional string country_code = 5;
}

message AuthenticateUserRequest {
  string phone = 1;
  string password = 2;
}

message UserData {
  string user_id = 1;
  string phone = 2;
  string email = 3;
  string full_name = 4;
  bool is_active = 5;
  bool is_verified = 6;
  // ... more fields
}
```

**User Service (`protos/user.proto`):**

```protobuf
syntax = "proto3";

package user;

service UserService {
  rpc GetUserProfile(GetUserProfileRequest) returns (GetUserProfileResponse);
  rpc UpdateUserProfile(UpdateUserProfileRequest) returns (UpdateUserProfileResponse);
  rpc DeleteUser(DeleteUserRequest) returns (DeleteUserResponse);
  // ... more RPC methods
}
```

#### gRPC Services

```
┌─────────────────┐    gRPC Calls    ┌─────────────────┐
│   FastAPI       │ ──────────────►  │   Auth Service  │
│   Gateway       │                  │   (Port 50051)  │
│   (Port 8000)   │                  │                 │
└─────────────────┘                  └─────────────────┘
         │                                     │
         │ gRPC Calls                          │ Database
         ▼                                     ▼
┌─────────────────┐                  ┌─────────────────┐
│   User Service  │                  │     Redis       │
│   (Port 50052)  │ ◄──────────────► │    Session      │
│                 │                  │    Storage      │
└─────────────────┘                  └─────────────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │
│    Database     │
│                 │
└─────────────────┘
```

#### Setup gRPC Services

**1. Install gRPC Dependencies:**

```bash
# Install gRPC tools
pip install grpcio grpcio-tools

# Install additional dependencies
pip install protobuf googleapis-common-protos
```

**2. Generate Python Code from Proto Files:**

```bash
# Make script executable and run
chmod +x ./generate_grpc.sh
./generate_grpc.sh
```

This generates:

- `protos/auth_pb2.py` - Auth service message classes
- `protos/auth_pb2_grpc.py` - Auth service client/server stubs
- `protos/user_pb2.py` - User service message classes
- `protos/user_pb2_grpc.py` - User service client/server stubs
- `protos/common_pb2.py` - Common message classes

**3. Start Auth Service:**

```bash
# In terminal 1: Start Auth gRPC Service
source venv/bin/activate
python services/auth_service.py

# Output:
# INFO:auth_service:Starting Auth Service gRPC server on [::]:50051
```

**4. Start FastAPI Gateway:**

```bash
# In terminal 2: Start FastAPI Gateway
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# FastAPI will automatically connect to gRPC services
```

#### How FastAPI Uses gRPC Auth Service

**Registration Flow:**

```python
# FastAPI endpoint calls gRPC service
@app.post("/auth/register")
async def register_user(user: UserRegistration):
    async with AuthServiceClient() as auth_service:
        result = await auth_service.register_user(
            phone=user.phone,
            email=user.email,
            password=user.password,
            full_name=user.full_name
        )
        return result
```

**Authentication Flow:**

```python
# FastAPI login endpoint
@app.post("/auth/login")
async def login_user(username: str = Form(...), password: str = Form(...)):
    async with AuthServiceClient() as auth_service:
        result = await auth_service.authenticate_user(username, password)

        if result.get("success"):
            return TokenResponse(
                access_token=result.get("access_token"),
                refresh_token=result.get("refresh_token"),
                expires_in=result.get("expires_in")
            )
```

**Token Validation (Middleware):**

```python
# JWT token validation via gRPC
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    async with AuthServiceClient() as auth_service:
        result = await auth_service.validate_token(credentials.credentials)

        if not result.get("valid"):
            raise HTTPException(status_code=401, detail="Invalid token")

        return result.get("user")
```

#### gRPC Client Usage Examples

**Async gRPC Client:**

```python
# Async usage in FastAPI
async with AuthServiceClient("localhost:50051") as client:
    result = await client.register_user(
        phone="+1234567890",
        email="user@example.com",
        password="securepass",
        full_name="John Doe"
    )
    print(result)
```

**Synchronous gRPC Client:**

```python
# Sync usage (blocking)
from services.auth_client import SyncAuthServiceClient

sync_client = SyncAuthServiceClient("localhost:50051")
result = sync_client.authenticate_user("+1234567890", "securepass")
print(result)
```

#### Testing gRPC Services

**1. Test Auth Service with cURL (via FastAPI):**

```bash
# Register user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+1234567890",
    "password": "SecurePassword123!",
    "email": "test@example.com",
    "full_name": "Test User"
  }'

# Login user
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=%2B1234567890&password=SecurePassword123!"

# Access protected endpoint
curl -X GET http://localhost:8000/users/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**2. Direct gRPC Testing (using grpcurl):**

```bash
# Install grpcurl
go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest

# List services
grpcurl -plaintext localhost:50051 list

# Call RegisterUser method
grpcurl -plaintext -d '{
  "phone": "+1234567890",
  "email": "test@example.com",
  "password": "secure123",
  "full_name": "Test User"
}' localhost:50051 auth.AuthService/RegisterUser
```

#### Production Considerations

**Service Discovery:**

```python
# Use proper service discovery in production
import consul

def get_auth_service_address():
    consul_client = consul.Consul()
    services = consul_client.health.service('auth-service', passing=True)
    if services:
        return f"{services[0]['Service']['Address']}:{services[0]['Service']['Port']}"
    return "localhost:50051"
```

**Load Balancing:**

```python
# gRPC client with load balancing
channel = grpc.aio.insecure_channel(
    'dns:///auth-service:50051',
    options=[
        ('grpc.lb_policy_name', 'round_robin'),
        ('grpc.keepalive_time_ms', 30000),
        ('grpc.keepalive_timeout_ms', 5000),
    ]
)
```

**SSL/TLS for gRPC:**

```python
# Secure gRPC channel
credentials = grpc.ssl_channel_credentials()
channel = grpc.aio.secure_channel('auth-service:50051', credentials)
```

#### Performance Benefits

- **50-100x faster** than REST/JSON for large payloads
- **Smaller payload size** due to binary serialization
- **HTTP/2 multiplexing** for multiple concurrent requests
- **Built-in compression** (gzip, deflate)
- **Schema evolution** support with protobuf

#### Development Workflow

```bash
# 1. Edit proto files
vim protos/auth.proto

# 2. Regenerate Python code
./generate_grpc.sh

# 3. Update service implementation
vim services/auth_service.py

# 4. Update client usage
vim services/auth_client.py

# 5. Test the integration
pytest tests/test_grpc_integration.py
```

This gRPC implementation provides a robust, high-performance communication layer between your FastAPI gateway and internal microservices, with strong typing and excellent tooling support.

### Monitoring and Observability Tools

1. **Prometheus + Grafana**

   - Real-time metrics collection and visualization
   - Custom dashboards for FastAPI applications

2. **OpenTelemetry**

   - Distributed tracing and metrics collection
   - Integration with Jaeger, Zipkin

3. **py-spy**

   - Sampling profiler for Python programs
   - No code changes required

4. **cProfile + snakeviz**
   - Built-in Python profiler with web-based visualization

### APM Solutions

- **DataDog APM**
- **New Relic**
- **AppSignal**
- **Sentry** (Error tracking)

### Load Testing Tools

- **Apache Bench (ab)** - Simple HTTP benchmarking
- **wrk** - Modern HTTP benchmarking tool
- **Locust** - Python-based load testing
- **Artillery** - Node.js load testing toolkit

## References

### Documentation

- [FastAPI Debugging](https://fastapi.tiangolo.com/tutorial/debugging/)
- [VS Code Python Debugging](https://code.visualstudio.com/docs/python/debugging)
- [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/)
- [Protocol Buffers Overview](https://protobuf.dev/overview/)
- [FastAPI Benchmarks](https://fastapi.tiangolo.com/benchmarks/)
- [Uvicorn Server Workers](https://fastapi.tiangolo.com/deployment/server-workers/)

### Resources

- **Redis Documentation**: https://redis.io/documentation
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **Docker Documentation**: https://docs.docker.com/
- **Nginx Configuration**: https://nginx.org/en/docs/
- **JWT.io**: https://jwt.io/
- **React Documentation**: https://reactjs.org/docs/
- **Vite Documentation**: https://vitejs.dev/guide/

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
