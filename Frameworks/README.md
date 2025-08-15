# Open Source Frameworks for Development and Deployment

This repository provides a collection of open source frameworks and tools for software development and production deployment, focusing on web applications, APIs, machine learning systems and support the software development lifecycle from development to production.

## Project Structure

```
Frameworks/
├── Backend/
│   ├── README.md
│   ├── ASP.NET/
│   │   └── gRPC/
│   ├── Basics/
│   │   ├── go.mod
│   │   └── main.go
│   ├── Express/
│   │   └── README.md
│   ├── FastAPI/
│   │   └── README.md
│   ├── Gin/
│   │   ├── albums.png
│   │   ├── README.md
│   │   └── web/
│   │       ├── go.mod, go.sum, main.go
│   │       ├── controllers/, database/, middleware/
│   │       ├── models/, routes/, test/, utils/
│   ├── NodeJS/
│   │   ├── README.md
│   │   └── MCP/
│   │       ├── README.md, package.json, tsconfig.json
│   │       ├── BUILD_STATUS.md, IMPLEMENTATION_COMPLETE.md
│   │       ├── Dockerfile, docker-compose.yml, setup.sh
│   │       ├── src/ (client/, server/, shared/)
│   │       ├── dist/, examples/, logs/
│   │       └── .env.example, .eslintrc.json
│   └── Spring Boot/
│       ├── build-and-push.sh, build.gradle, deploy.sh
│       ├── docker-compose.yml, Dockerfile
│       ├── k8s-deployment.yml, main.tf
│       └── bin/, build/, src/
└── Frontend/
    ├── README.md
    ├── Flutter/
    │   └── README.md
    ├── NextJS/
    │   └── README.md
    ├── React/
    │   ├── package.json, README.md
    │   ├── public/, src/
    │   └── components/
    ├── ReactNative/
    │   ├── albums/
    │   └── assets/
    ├── Vite/
    │   ├── README.md, package.json, vite.config.ts
    │   ├── COMPARISON.md, MIGRATION.md, GITIGNORE.md
    │   ├── Dockerfile, Dockerfile.dev, docker-compose.yml
    │   ├── build.sh, nginx.conf, .env.example
    │   ├── src/ (main.ts, app.ts, styles/, vite-env.d.ts)
    │   ├── nextjs-app/
    │   │   ├── next.config.js, tailwind.config.js
    │   │   ├── Dockerfile, docker-compose.yml
    │   │   └── src/, package.json, tsconfig.json
    │   └── vite-react-app/
    │       ├── vite.config.ts, package.json
    │       ├── server/, src/, index.html
    │       └── README.md, .env.example
    └── Vue/
        └── README.md
```

## Backend Frameworks

### Java - Spring Boot
**Development Environment:**
- Spring Boot DevTools for hot reloading
- Embedded Tomcat server (default port 8080)
- Maven or Gradle build tools
- IDE integration (IntelliJ IDEA, Eclipse, VS Code)

**Production Servers:**
- **Tomcat** - Lightweight servlet container
- **Jetty** - High-performance HTTP server
- **Undertow** - Flexible and performant web server
- **WildFly** - Full-featured application server

### JavaScript/TypeScript - Node.js & Express.js
**Development Environment:**
- Node.js runtime with npm/yarn package managers
- **Nodemon** for automatic restarts during development
- **Vite** - Fast build tool with HMR for TypeScript projects
- **ts-node** - TypeScript execution for Node.js
- Express.js framework for routing and middleware
- **tsx** - Enhanced TypeScript execution environment

**Vite for Node.js/Express Development:**
```bash
# Initialize Vite project with Express backend
npm create vite@latest my-express-app -- --template vanilla-ts
cd my-express-app

# Install Express and development dependencies
npm install express @types/express
npm install -D @types/node nodemon tsx

# Configure vite.config.ts for backend
import { defineConfig } from 'vite'
export default defineConfig({
  build: {
    target: 'node18',
    lib: {
      entry: 'src/server.ts',
      formats: ['es']
    },
    rollupOptions: {
      external: ['express']
    }
  }
})
```

**Production Servers:**
- **PM2** - Process manager for Node.js applications
- **Nginx** - Reverse proxy and load balancer
- **Cluster mode** - Native Node.js clustering
- **Docker containers** with multi-stage builds

### Python - FastAPI & Flask
**Development Environment:**
- Python virtual environments (venv, conda)
- Uvicorn ASGI server for FastAPI
- Flask development server
- Hot reloading with --reload flag

**Production Servers:**
- **Gunicorn** - Python WSGI HTTP Server
- **Uvicorn** - Lightning-fast ASGI server
- **uWSGI** - Application server container
- **Nginx** - Reverse proxy for static files and load balancing

### Go - Gin Framework
**Development Environment:**
- Go modules for dependency management
- Built-in HTTP server
- Air for live reloading during development
- Native compilation for target platforms

**Production Servers:**
- **Native binary** - Compile to single executable
- **Nginx** - Reverse proxy and static file serving
- **Docker containers** - Multi-stage builds for minimal images
- **Systemd services** - Process management on Linux

### C# - ASP.NET Core
**Development Environment:**
- .NET CLI tools and Visual Studio
- Kestrel web server for development
- Hot reload capabilities
- IIS Express integration

**Production Servers:**
- **Kestrel** - Cross-platform web server
- **IIS** - Windows Internet Information Services
- **Nginx** - Reverse proxy on Linux
- **Docker containers** - Cross-platform deployment

## Frontend Frameworks

### React & Next.js
**Development:**
- Create React App (CRA) or Vite for development
- Next.js for server-side rendering and static generation
- Hot Module Replacement (HMR)
- TypeScript support out of the box

**Production Deployment:**
- **Static hosting** - Netlify, Vercel, GitHub Pages
- **CDN distribution** - Cloudflare, AWS CloudFront
- **Server-side rendering** - Next.js production server
- **Docker containers** - Multi-stage builds

### Angular
**Development:**
- Angular CLI for project scaffolding
- TypeScript framework
- Hot reloading with ng serve
- Comprehensive development tools

**Production:**
- **Nginx** - Serve static assets
- **Apache HTTP Server** - Alternative web server
- **Docker containers** - Containerized deployment
- **CDN deployment** - Global content distribution

### Vue.js
**Development:**
- Vue CLI or Vite for project setup
- Vue DevTools for debugging
- Hot Module Replacement
- Single File Components

**Production:**
- **Static site generation** - Nuxt.js
- **SPA deployment** - Traditional web servers
- **JAMstack** - Pre-built markup and APIs

### Vite - Universal Build Tool & Development Environment
**Development Environment:**
- **Lightning-fast HMR** for instant development feedback
- **Native TypeScript support** without additional compilation
- **Universal framework support** - React, Vue, Vanilla JS/TS
- **Next.js migration** capabilities for seamless upgrades
- **VS Code integration** with debugging configurations

**Key Features:**
```typescript
// vite.config.ts - Universal configuration
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: '0.0.0.0'
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
```

**Project Structure:**
- **Vanilla TypeScript** setup for full control
- **React integration** with `vite-react-app/`
- **Next.js migration** path with `nextjs-app/`
- **Docker containerization** for production deployment
- **DevOps configurations** with build scripts and CI/CD

**Production Deployment:**
- **Nginx** - Static file serving and reverse proxy
- **Docker containers** - Multi-stage builds for optimization
- **CDN integration** - CloudFront, Cloudflare
- **Progressive Web Apps** - Service worker support

### Mobile Frameworks

#### Flutter
**Development:**
- Dart SDK and Flutter framework
- Hot reload for rapid development
- Cross-platform development (iOS, Android, Web, Desktop)

**Production:**
- **Native compilation** - Platform-specific binaries
- **App stores** - Google Play, Apple App Store
- **Web deployment** - Progressive Web Apps

#### React Native
**Development:**
- Expo CLI for managed workflow
- Metro bundler for JavaScript
- Hot reloading and fast refresh

**Production:**
- **Native compilation** - Platform-specific apps
- **Over-the-air updates** - Expo Updates, CodePush
- **App store distribution** - iOS and Android markets

## Development vs Production

### Development Environment Characteristics
- **Fast iteration cycles** with hot reloading
- **Detailed error messages** and debugging tools
- **Development servers** optimized for quick starts
- **Source maps** for debugging compiled code
- **Live reload** for immediate feedback

### Vite as Universal Development Tool
**Vite** has become a popular choice for both frontend and backend development due to its speed and flexibility:

#### Frontend Development with Vite
```bash
# React with TypeScript
npm create vite@latest my-react-app -- --template react-ts

# Vue with TypeScript
npm create vite@latest my-vue-app -- --template vue-ts

# Vanilla TypeScript
npm create vite@latest my-app -- --template vanilla-ts
```

#### Backend Development with Vite
```bash
# Express server with TypeScript and Vite
npm create vite@latest my-server -- --template vanilla-ts
cd my-server

# Install backend dependencies
npm install express cors helmet morgan
npm install -D @types/express @types/cors @types/morgan

# Configure package.json scripts
{
  "scripts": {
    "dev": "tsx watch src/server.ts",
    "build": "vite build",
    "start": "node dist/server.js",
    "preview": "vite preview"
  }
}
```

#### Vite Configuration for Node.js/Express
```typescript
// vite.config.ts
import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    target: 'node18',
    ssr: true,
    lib: {
      entry: 'src/server.ts',
      name: 'server',
      formats: ['es']
    },
    rollupOptions: {
      external: ['express', 'cors', 'helmet', 'morgan']
    }
  },
  optimizeDeps: {
    exclude: ['express']
  }
})
```

### Production Environment
- **Optimized builds** with minification and bundling
- **Performance monitoring** and logging
- **Load balancing** and horizontal scaling
- **Security hardening** and SSL/TLS termination
- **Caching strategies** and CDN integration
- **Process management** and automatic restarts

## High-Performance Production Servers

### Reverse Proxy Servers
- **Nginx** - High-performance HTTP server and reverse proxy
  - Excellent for serving static files
  - Load balancing capabilities
  - SSL termination
  - Gzip compression

- **Apache HTTP Server** - de-facto standard web server
  - Extensive module system
  - .htaccess configuration
  - Virtual hosting

### Application Servers by Language
- **Java**: Tomcat, Jetty, Undertow, WildFly
- **Python**: Gunicorn, uWSGI, Uvicorn (ASGI)
- **Node.js**: PM2, Cluster mode
- **Go**: Native binaries, systemd services
- **C#**: Kestrel, IIS

## Deployment

### Development
- **Local development servers**
- **Docker Compose** for multi-service applications
- **Hot reloading** and live updates
- **Development databases** (SQLite, in-memory)

### Production

#### Containerization
- **Docker** - Containerized applications
- **Docker Compose** - Multi-container orchestration
- **Kubernetes** - Container orchestration at scale
- **Helm** - Kubernetes package manager

#### Native Operating Systems
- **Linux/Debian** - systemd services, package managers
- **Ubuntu Server** - LTS releases for stability
- **CentOS/RHEL** - Enterprise Linux distributions

#### Mobile Deployment
- **Android** - Google Play Store, APK distribution
- **iOS** - Apple App Store, TestFlight

#### Cloud Platforms
- **Amazon AWS**
  - EC2 instances, ECS, EKS
  - Lambda for serverless functions
  - S3 for static file hosting
  - CloudFront CDN

- **Google Cloud Platform (GCP)**
  - Compute Engine, GKE
  - Cloud Functions
  - Cloud Storage
  - Cloud CDN

- **Microsoft Azure**
  - Virtual Machines, AKS
  - Azure Functions
  - Blob Storage
  - Azure CDN

## Automation and CI/CD Tools

### Build and Deployment Pipelines
- **Jenkins** - Open source automation server
  - Pipeline as code with Jenkinsfile
  - Extensive plugin ecosystem
  - Self-hosted solution

- **GitHub Actions** - Native GitHub CI/CD
  - YAML-based workflow definitions
  - Marketplace of pre-built actions
  - Integrated with GitHub repositories

- **GitLab CI/CD** - Integrated DevOps platform
  - Auto DevOps for automatic pipelines
  - Container registry integration

### Container Orchestration
- **Helm** - Kubernetes package manager
  - Chart-based deployments
  - Version management
  - Rollback capabilities

- **ArgoCD** - GitOps continuous delivery
  - Declarative setup
  - Automatic synchronization

## Machine Learning vs Web Applications

### Framework Differences
**Web Applications:**
- Focus on HTTP request/response cycles
- Stateless design patterns
- CRUD operations and data persistence
- Real-time user interactions

**Machine Learning Applications:**
- **Model serving** - TensorFlow Serving, TorchServe
- **Inference optimization** - TensorRT, ONNX Runtime
- **Batch processing** - Apache Spark, Ray
- **GPU acceleration** - CUDA support

### Backend Extensions for ML
- **Python ML Stack**: TensorFlow, PyTorch, scikit-learn
- **Model versioning**: MLflow, DVC
- **Feature stores**: Feast, Hopsworks
- **Monitoring**: Weights & Biases, Neptune

### Specialized ML Backends
- **TensorRT-LLM** - NVIDIA's optimized LLM inference
- **vLLM** - High-throughput LLM serving
- **Hugging Face TGI** - Text Generation Inference
- **Triton Inference Server** - Multi-framework serving

### MCP Implementation Status
The NodeJS/MCP implementation includes:
- Docker and Open WebUI support
- Main CLI loads: `node dist/index.js --help`
- Server starts in STDIO mode: `node dist/index.js server --transport stdio`
- ESLint configuration

**Available Models:**
- Llama 3.2:1b (smaller, faster)
- Llama 3.2:3b (balanced performance)
- Llama 3.2:8b (larger, more capable)
- Support for custom Ollama models

## API Technologies

### REST APIs
- **HTTP methods**: GET, POST, PUT, DELETE, PATCH
- **Status codes**: 200, 201, 400, 401, 404, 500
- **JSON** as primary data format
- **OpenAPI/Swagger** for documentation

### GraphQL
- **Single endpoint** for flexible queries
- **Type system** and schema definition
- **Real-time subscriptions**

### gRPC
- **Protocol Buffers** for serialization
- **HTTP/2** for performance
- **Bi-directional streaming**

## Frontend-Backend Communication

### HTTP Clients
**Axios (JavaScript/TypeScript):**
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://api.example.com',
  timeout: 10000,
});

const response = await api.get('/users');
```

**Fetch API (Native Web):**
```javascript
const response = await fetch('https://api.example.com/users', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  }
});
const data = await response.json();
```

**HTTP Clients by Platform:**
- **Flutter**: Dio, http package
- **React Native**: Axios, Fetch API
- **Angular**: HttpClientModule
- **Vue.js**: Axios, Vue Resource

## Security in Frameworks

### Authentication & Authorization
- **JWT (JSON Web Tokens)** - Stateless authentication
  - Header, payload, and signature
  - Short-lived access tokens
  - Refresh token rotation

- **OAuth 2.0** - Industry standard authorization
  - Authorization code flow
  - Client credentials flow
  - PKCE for mobile applications

### Transport Security
- **TLS/SSL** - Encrypted communication
  - Certificate management
  - Perfect Forward Secrecy
  - HTTP Strict Transport Security (HSTS)

### API Security Best Practices
- **Rate limiting** - Prevent abuse
- **CORS** - Cross-Origin Resource Sharing
- **Input validation** - Prevent injection attacks
- **API keys** - Service-to-service authentication

## Template Engines

### Backend Template Engines
**Java (Spring Boot):**
- **Thymeleaf** - Modern server-side template engine
- **JSP** - JavaServer Pages
- **Freemarker** - Template engine for Java

**Node.js/Express:**
- **EJS** - Embedded JavaScript templates
- **Handlebars** - Logic-less templates
- **Pug** - Clean, whitespace-sensitive syntax

**Python:**
- **Jinja2** - Modern templating engine
- **Django Templates** - Built-in Django templating
- **Mako** - Fast template library

**Go:**
- **html/template** - Built-in HTML templating
- **text/template** - Plain text templating

**C# (ASP.NET):**
- **Razor** - Built-in view engine
- **Liquid** - Safe, customer-facing template language

### Frontend Template Engines
- **React JSX** - JavaScript XML syntax extension
- **Angular Templates** - HTML with Angular directives
- **Vue Templates** - HTML-based template syntax

## Model Context Protocol (MCP)

The Model Context Protocol provides a standardized way for AI applications to securely access external data sources and tools. MCP enables seamless integration between AI models and various data sources while maintaining security and privacy.

### Features
- **Standardized interface** for AI-data source communication
- **Security-first design** with permission controls
- **Extensible architecture** for custom data sources
- **Cross-platform compatibility**

### MCP Implementation with Node.js & Llama-3.x

This project includes a complete MCP implementation using Node.js with TypeScript, integrated with Llama-3.x via Ollama. The implementation demonstrates:

#### Architecture / Components
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Open WebUI    │    │   MCP Client    │    │   Your App      │
│   (Web UI)      │    │   (Node.js)     │    │   (Custom)      │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │ JSON-RPC over HTTP/STDIO
                         ┌───────▼───────┐
                         │   MCP Server  │
                         │   (Node.js)   │
                         │   - Tools     │
                         │   - Resources │
                         │   - Prompts   │
                         └───────┬───────┘
                                 │ REST API calls
                         ┌───────▼───────┐
                         │     Ollama    │
                         │   (Llama-3.x) │
                         │   - Inference │
                         │   - Embeddings│
                         └───────────────┘
```

#### Data Flow Process
1. **Client Request**: JSON-RPC method calls to MCP server
2. **Request Validation**: Server validates and processes requests
3. **Prompt Template Application**: Context-aware prompt engineering
4. **Ollama Integration**: HTTP calls to local Ollama instance
5. **LLM Inference**: Llama-3.x model processing
6. **Response Processing**: Format validation and transformation
7. **Client Response**: Standardized MCP response format

#### LLM Inference Pipeline
- **Tokenization**: Text → Numerical tokens `"Hello!" → [15496, 0]`
- **Embedding**: Tokens → High-dimensional vectors `[15496] → [0.1, -0.3, 0.7, ...]`
- **Forward Pass**: Neural network processing through attention layers
- **Token Selection**: Probabilistic next token generation
- **Response Assembly**: Iterative token generation until completion

#### Available Tools
- **llama_generate**: Text generation with Llama-3.x
- **llama_chat**: Conversational AI with context management
- **get_system_info**: System and model information
- **list_ollama_models**: Available model enumeration

#### Prompt Templates
```typescript
const chatTemplate = `System: You are a helpful AI assistant specialized in {{domain}}.
Context: {{context_information}}
User: {{user_input}}
Please provide a helpful and accurate response.`;
```

#### Quick Start
```bash
# Install dependencies
cd Backend/NodeJS/MCP
npm install

# Setup Ollama and Llama model
ollama pull llama3.2:3b

# Start MCP server
npm run server:dev

# Start MCP client
npm run client:dev
```

### Implementation
MCP can be integrated into various backend frameworks to provide AI applications with access to:
- **Database connections** with secure query execution
- **File systems** with controlled read/write operations
- **External APIs** with authentication and rate limiting
- **Real-time data streams** with event-driven processing
- **Model serving** with multiple LLM backend support
- **Conversation management** with persistent session handling

## References and Resources

### Backend Frameworks
- [Spring Boot](https://spring.io/web-applications) - Java framework for building web applications
- [Express.js](https://expressjs.com/) - Fast, unopinionated web framework for Node.js
- [FastAPI](https://fastapi.tiangolo.com/project-generation/) - Modern Python web framework
- [Gin](https://gin-gonic.com/) - High-performance HTTP web framework for Go
- [ASP.NET Core](https://learn.microsoft.com/en-us/aspnet/core/client-side/spa/angular) - Cross-platform web framework

### Frontend Frameworks
- [React](https://create-react-app.dev/docs/adding-typescript/) - JavaScript library for user interfaces
- [React Native](https://reactnative.dev/docs/typescript) - Mobile app development with TypeScript
- [Angular](https://angular.dev/tutorials/learn-angular) - Platform for building web applications
- [Vue.js](https://vuejs.org/) - Progressive JavaScript framework
- [Flutter](https://flutter.dev/) - UI toolkit for cross-platform applications
- [Vite Setup Guide](Frontend/Vite/README.md) - Complete Vite setup for JavaScript and TypeScript development

### Vite Implementation Resources
- [Vite Configuration](Frontend/Vite/vite.config.ts) - Universal Vite configuration for development and production
- [Next.js Migration Guide](Frontend/Vite/MIGRATION.md) - Step-by-step migration from Vite to Next.js
- [Docker Setup](Frontend/Vite/Dockerfile) - Production-ready Docker configurations
- [React Integration](Frontend/Vite/vite-react-app/) - Vite with React and TypeScript
- [Next.js Example](Frontend/Vite/nextjs-app/) - Complete Next.js application setup

### Development and Production Tools
- [Docker](https://www.docker.com/) - Containerization platform
- [Kubernetes](https://kubernetes.io/) - Container orchestration
- [Jenkins](https://www.jenkins.io/) - Automation server
- [GitHub Actions](https://github.com/features/actions) - CI/CD platform
- [Nginx](https://nginx.org/) - High-performance web server
- [Vite](https://vitejs.dev/) - Fast build tool for frontend and Node.js development

### Machine Learning and AI
- [Hugging Face Transformers](https://huggingface.co/docs/transformers.js/en/tutorials/node) - Server-side inference in Node.js
- [Model Context Protocol](https://modelcontextprotocol.io/docs/getting-started/intro) - Standardized AI data access
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk) - Official TypeScript SDK
- [Ollama Documentation](https://ollama.ai/docs) - Local LLM execution platform
- [Open WebUI](https://docs.openwebui.com/) - Web interface for LLMs
- [Llama Models](https://llama.meta.com/docs/) - Meta's Llama model documentation
- [TensorFlow Serving](https://www.tensorflow.org/tfx/guide/serving) - Machine learning model serving
- [PyTorch](https://pytorch.org/) - Deep learning framework

### MCP Implementation Resources
- [MCP Server Implementation](Backend/NodeJS/MCP/) - Complete MCP server with Node.js/TypeScript
- [Build Status](Backend/NodeJS/MCP/BUILD_STATUS.md) - Implementation status and testing results
- [Implementation Guide](Backend/NodeJS/MCP/IMPLEMENTATION_COMPLETE.md) - Complete setup and usage guide
- [Llama Integration Examples](Backend/NodeJS/MCP/examples/) - Working examples and use cases

### API Documentation and Testing
- [OpenAPI/Swagger](https://swagger.io/) - API documentation standard
- [Postman](https://www.postman.com/) - API testing platform
- [REST API Tutorial](https://spring.io/guides/gs/rest-service) - Building REST services with Spring
