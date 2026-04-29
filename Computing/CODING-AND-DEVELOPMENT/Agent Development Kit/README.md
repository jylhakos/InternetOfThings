# Agent Development Kit

## Table of Contents

- [What is Agent Development Kit?](#what-is-agent-development-kit)
- [Why Choose ADK for Software Development?](#why-choose-adk-for-software-development)
  - [Stateful Memory Management](#stateful-memory-management)
  - [Key Advantages](#key-advantages)
- [Introducing Agent Development Kit for TypeScript: Build AI Agents](#introducing-agent-development-kit-for-typescript-build-ai-agents)
  - [Getting Started with TypeScript](#getting-started-with-typescript)
- [Ollama Model Host for ADK Agents](#ollama-model-host-for-adk-agents)
  - [Setting Up Ollama with ADK (Linux)](#setting-up-ollama-with-adk-linux)
- [Working with Open Source Libraries](#working-with-open-source-libraries)
  - [Python Libraries](#python-libraries)
  - [TypeScript/JavaScript Libraries](#typescriptjavascript-libraries)
  - [Example: Integrating with Open Source Libraries](#example-integrating-with-open-source-libraries)
- [What's a Multi-Agent System?](#whats-a-multi-agent-system)
  - [Key Characteristics](#key-characteristics)
  - [Multi-Agent Patterns in ADK](#multi-agent-patterns-in-adk)
  - [Real-World Use Cases](#real-world-use-cases)
  - [Example: Building a Multi-Agent System with ADK](#example-building-a-multi-agent-system-with-adk)
- [Deploying Your Agent](#deploying-your-agent)
  - [Deployment Options](#deployment-options)
  - [Deployment Process](#deployment-process)
  - [Deployment Best Practices](#deployment-best-practices)
- [Build and Deploy an ADK Agent on Cloud Run](#build-and-deploy-an-adk-agent-on-cloud-run)
- [Step-by-Step: How ADK Helps in Software Development](#step-by-step-how-adk-helps-in-software-development)
- [References](#references)
  - [Official Documentation](#official-documentation)
  - [Deployment Guides](#deployment-guides)
  - [Model Integration](#model-integration)
  - [Repositories](#repositories)
  - [Articles](#articles)

---

## What is Agent Development Kit?

The [Agent Development Kit](https://google.github.io/adk-docs/) (ADK) is Google's framework for building, orchestrating, evaluating, and deploying AI-powered agents using Gemini and other Large Language Models (LLMs). ADK transforms stateless AI interactions into stateful, complex workflows, enabling developers to create sophisticated multi-agent systems with persistent memory and coordinated behaviors.

ADK is available for both **Python** and **TypeScript**, making it accessible to a wide range of developers and easily integrable with modern development ecosystems.

## Why Choose ADK for Software Development?

### Stateful Memory Management
Unlike standard LLM APIs that treat each request independently, ADK supports **session-based memory**, allowing agents to:
- Remember previous interactions across conversations
- Maintain context and state throughout complex workflows
- Build sophisticated conversational experiences with continuity
- Track user preferences and historical data

### Key Advantages

1. **Multi-Agent Orchestration**: Build systems where multiple specialized agents collaborate to solve complex problems
2. **Framework Flexibility**: Works with various LLMs (Gemini, OpenAI, Ollama, and more)
3. **Production-Ready**: Built-in tools for evaluation, testing, and deployment to cloud platforms
4. **Open Source Integration**: Fully compatible with open-source libraries and models
5. **Developer-Friendly**: Integrates seamlessly with modern IDEs like VS Code, especially in Linux environments
6. **Cloud-Native**: First-class support for Google Cloud deployment (Cloud Run, Vertex AI) with straightforward deployment pipelines

## Introducing Agent Development Kit for TypeScript: Build AI Agents

ADK provides TypeScript support, enabling JavaScript/TypeScript developers to build production-grade AI agents with the same power as the Python version. The TypeScript SDK offers:

- **Type-Safe Development**: Full TypeScript type definitions for robust development
- **Modern JavaScript Ecosystem**: Seamless integration with Node.js, npm, and popular frameworks
- **Async/Await Support**: Natural asynchronous programming patterns
- **Cross-Platform**: Run on Linux, macOS, and Windows development environments

> ** Quick Start:** See [QUICKSTART.md](QUICKSTART.md) for a condensed setup guide and VS Code workflow tips.

### Getting Started with TypeScript

Follow these steps to begin building with ADK in TypeScript:

**Project Structure:**
```
my-adk-agent/
├── index.ts              # Your agent code
├── package.json          # Dependencies and scripts
├── tsconfig.json         # TypeScript configuration
├── .gitignore           # Git exclusions (node_modules, build files, secrets)
├── dist/                # Compiled output (generated)
└── node_modules/        # Dependencies (generated, not in Git)
```

#### Step 1: Prerequisites (Linux Environment)
```bash
# Ensure Node.js 18+ is installed
node --version  # Should be v18 or higher

# Install npm if not already available
sudo apt update
sudo apt install nodejs npm
```

**Note on TypeScript Environment Management:**
Unlike Python's virtual environments (venv), TypeScript/Node.js uses project-local `node_modules` directories for dependency isolation. Each project has its own `node_modules` folder where all dependencies are installed, keeping projects independent. No additional virtual environment setup is needed!

#### Step 2: Create Your Project
```bash
# Create a new directory for your agent
mkdir my-adk-agent
cd my-adk-agent

# Initialize a TypeScript project
npm init -y
npm install typescript @types/node --save-dev
npx tsc --init
```

#### Step 3: Install ADK
```bash
# Install the ADK TypeScript SDK
npm install @google/adk
```

#### Step 4: Create Your First Agent

Create an `index.ts` file (see the included [index.ts](index.ts) in this repository):

```typescript
import { Agent, createAgent } from '@google/adk';

// Define your agent with specific capabilities
const myAgent = createAgent({
  name: 'MyFirstAgent',
  model: 'gemini-pro',
  memory: true,  // Enable stateful memory
  systemPrompt: 'You are a helpful assistant designed to help with software development tasks.',
  tools: [
    // Add custom tools and functions here
  ]
});

// Run your agent
async function main() {
  const response = await myAgent.run({
    prompt: 'Hello, how can you help me?'
  });
  console.log(response);
}

main();
```

**Project Files Included:**
- [index.ts](index.ts) - Complete agent implementation with examples
- [package.json](package.json) - Project dependencies and scripts
- [tsconfig.json](tsconfig.json) - TypeScript configuration
- [.gitignore](.gitignore) - Excludes node_modules, build files, secrets, and binaries from Git
- [.env.example](.env.example) - Environment variables template (copy to `.env`)
- [QUICKSTART.md](QUICKSTART.md) - Quick reference guide for VS Code setup

**Quick Start:**
```bash
# Install dependencies
npm install

# Set up environment variables (optional)
cp .env.example .env
# Edit .env with your API keys

# Run in development mode
npm run dev

# Build for production
npm run build

# Run compiled version
npm start
```

#### Step 5: VS Code Integration (Linux)

ADK works seamlessly with VS Code on Linux:

1. **Install VS Code Extensions**:
   - TypeScript and JavaScript Language Features (built-in)
   - Prettier for code formatting
   - ESLint for code quality

2. **Configure Your Workspace**:
   Create a `.vscode/settings.json`:
   ```json
   {
     "typescript.tsdk": "node_modules/typescript/lib",
     "editor.formatOnSave": true,
     "editor.codeActionsOnSave": {
       "source.fixAll.eslint": true
     }
   }
   ```

3. **Debug Configuration**:
   Create a `.vscode/launch.json`:
   ```json
   {
     "version": "0.2.0",
     "configurations": [
       {
         "name": "Debug ADK Agent",
         "type": "node",
         "request": "launch",
         "program": "${workspaceFolder}/dist/index.js",
         "preLaunchTask": "tsc: build",
         "outFiles": ["${workspaceFolder}/dist/**/*.js"]
       }
     ]
   }
   ```

4. **Run and Debug**: Press F5 to start debugging your ADK agent directly in VS Code

## Ollama Model Host for ADK Agents

ADK supports [Ollama](https://ollama.com/), enabling you to run open-source LLMs locally for development and testing. This is particularly valuable for:
- Offline development
- Cost-effective experimentation
- Privacy-sensitive applications
- Custom model fine-tuning

### Setting Up Ollama with ADK (Linux)

#### Step 1: Install Ollama
```bash
# Install Ollama on Linux
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version
```

#### Step 2: Pull a Model
```bash
# Download a model (e.g., llama2, mistral, codellama)
ollama pull llama2

# List available models
ollama list
```

#### Step 3: Start Ollama Service
```bash
# Ollama typically runs as a service after installation
# If needed, start it manually:
ollama serve
```

#### Step 4: Configure ADK to Use Ollama

**Python Example**:
```python
from adk import Agent

agent = Agent(
    model="ollama/llama2",
    endpoint="http://localhost:11434"
)
```

**TypeScript Example**:
```typescript
import { createAgent } from '@google/adk';

const agent = createAgent({
  model: 'ollama/llama2',
  endpoint: 'http://localhost:11434'
});
```

#### Step 5: Test Your Setup
```bash
# Test Ollama directly
curl http://localhost:11434/api/generate -d '{
  "model": "llama2",
  "prompt": "Hello, world!"
}'
```

## Working with Open Source Libraries

ADK is designed to integrate seamlessly with the open-source ecosystem:

### Python Libraries
- **LangChain**: Use LangChain tools and chains within ADK agents
- **Hugging Face**: Integrate Hugging Face models and datasets
- **NumPy/Pandas**: Process and analyze data within agent workflows
- **FastAPI**: Build REST APIs around your ADK agents

### TypeScript/JavaScript Libraries
- **Express.js**: Create web servers hosting ADK agents
- **React/Next.js**: Build frontend interfaces for your agents
- **Axios**: Make HTTP requests from agent tools
- **Zod**: Runtime type validation for agent inputs/outputs

### Example: Integrating with Open Source Libraries
```typescript
import { createAgent } from '@google/adk';
import axios from 'axios';
import { z } from 'zod';

// Define tool with Zod validation
const weatherTool = {
  name: 'get_weather',
  schema: z.object({
    city: z.string()
  }),
  execute: async ({ city }) => {
    // Use axios to fetch weather data
    const response = await axios.get(
      `https://api.weather.com/v1/current?city=${city}`
    );
    return response.data;
  }
};

const agent = createAgent({
  name: 'WeatherAgent',
  tools: [weatherTool]
});
```

## What's a Multi-Agent System?

A **multi-agent system** is an architecture where multiple AI agents work together, each with specialized roles and capabilities, to accomplish complex tasks that would be difficult for a single agent to handle alone.

### Key Characteristics

1. **Specialization**: Each agent has specific expertise (e.g., one for research, one for analysis, one for writing)
2. **Communication**: Agents can share information and coordinate actions
3. **Autonomy**: Each agent makes independent decisions within its domain
4. **Collaboration**: Agents work toward common goals while handling different aspects

### Multi-Agent Patterns in ADK

ADK supports several multi-agent patterns:

#### Sequential Pipeline
Agents process tasks in sequence, each building on the previous agent's output:
```
Input → Agent A → Agent B → Agent C → Final Output
```

#### Hierarchical Orchestration
A coordinator agent delegates tasks to specialized worker agents:
```
        Coordinator Agent
           /    |    \
       Agent A Agent B Agent C
```

#### Collaborative Swarm
Multiple agents work in parallel, then combine their results:
```
Input → [Agent A, Agent B, Agent C] → Aggregator → Output
```

### Real-World Use Cases

- **Software Development**: One agent writes code, another reviews it, a third writes tests
- **Research**: One agent searches sources, another analyzes data, a third synthesizes findings
- **Customer Service**: Routing agent directs to specialized support, technical, or billing agents
- **Content Creation**: Research agent gathers information, writing agent drafts content, editing agent refines

### Example: Building a Multi-Agent System with ADK

```typescript
import { createAgent, Orchestrator } from '@google/adk';

// Create specialized agents
const researchAgent = createAgent({
  name: 'Researcher',
  model: 'gemini-pro',
  systemPrompt: 'You are a research specialist. Gather and analyze information.'
});

const writerAgent = createAgent({
  name: 'Writer',
  model: 'gemini-pro',
  systemPrompt: 'You are a content writer. Create engaging, well-structured content.'
});

const editorAgent = createAgent({
  name: 'Editor',
  model: 'gemini-pro',
  systemPrompt: 'You are an editor. Review and refine content for clarity and quality.'
});

// Orchestrate the multi-agent workflow
const orchestrator = new Orchestrator({
  agents: [researchAgent, writerAgent, editorAgent],
  workflow: 'sequential'
});

// Execute the workflow
async function createArticle(topic: string) {
  const result = await orchestrator.run({
    initialPrompt: `Create an article about: ${topic}`,
    steps: [
      { agent: researchAgent, task: 'Research the topic' },
      { agent: writerAgent, task: 'Write the article based on research' },
      { agent: editorAgent, task: 'Edit and refine the article' }
    ]
  });
  return result;
}
```

## Deploying Your Agent

ADK provides multiple deployment options to bring your agents from development to production:

### Deployment Options

1. **Google Cloud Run** (Recommended for production)
   - Fully managed serverless platform
   - Auto-scaling based on demand
   - Pay-per-use pricing
   - Built-in SSL/TLS and custom domains

2. **Vertex AI**
   - Integrated with Google Cloud AI services
   - Advanced monitoring and logging
   - Enterprise-grade security

3. **Self-Hosted**
   - Deploy to your own infrastructure
   - Kubernetes support
   - Docker containerization

### Deployment Process

#### Step 1: Prepare Your Agent for Production
```bash
# Ensure all dependencies are specified
npm install  # or pip install -r requirements.txt

# Run tests
npm test

# Build for production
npm run build
```

#### Step 2: Create a Dockerfile
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 8080

CMD ["node", "dist/index.js"]
```

#### Step 3: Configure Environment Variables
```bash
# Create .env.production
API_KEY=your_api_key
MODEL=gemini-pro
PORT=8080
```

#### Step 4: Deploy to Cloud Run (Linux)
```bash
# Install Google Cloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# Build and push container
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/adk-agent

# Deploy to Cloud Run
gcloud run deploy adk-agent \
  --image gcr.io/YOUR_PROJECT_ID/adk-agent \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars API_KEY=your_api_key
```

#### Step 5: Monitor and Scale
```bash
# View logs
gcloud run logs read adk-agent

# Update configuration
gcloud run services update adk-agent \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10
```

### Deployment Best Practices

- **Health Checks**: Implement `/health` endpoints for monitoring
- **Secrets Management**: Use Google Secret Manager for sensitive data
- **Logging**: Integrate with Cloud Logging for debugging
- **Rate Limiting**: Protect your agent from abuse
- **Versioning**: Use container tags for version control
- **CI/CD**: Automate deployments with GitHub Actions or Cloud Build

## Build and Deploy an ADK Agent on Cloud Run

For hands-on tutorial on building and deploying production-ready ADK agents, follow the official Google Codelabs guide. This step-by-step tutorial covers:

- Setting up your development environment
- Building a complete ADK agent with real-world functionality
- Containerizing your agent with Docker
- Deploying to Cloud Run with proper configuration
- Implementing monitoring and logging
- Managing secrets and environment variables
- Setting up CI/CD pipelines

**Tutorial Link**: [Deploy an ADK Agent to Cloud Run - Google Codelabs](https://codelabs.developers.google.com/codelabs/production-ready-ai-with-gc/5-deploying-agents/deploy-an-adk-agent-to-cloud-run#0)

This hands-on guide provides production-ready patterns and best practices for enterprise deployments.

## Step-by-Step: How ADK Helps in Software Development

### 1. **Rapid Prototyping**
   - Quickly build AI-powered features without managing infrastructure
   - Test different LLMs and compare results
   - Iterate on agent behaviors with immediate feedback

### 2. **Code Quality and Testing**
   - Built-in evaluation frameworks for agent performance
   - Unit testing support for agent behaviors
   - Integration testing for multi-agent workflows

### 3. **IDE Integration (VS Code on Linux)**
   - Full IntelliSense and autocomplete support
   - Debugging with breakpoints in agent code
   - Terminal integration for running agents
   - Git integration for version control

### 4. **Collaboration**
   - Share agent configurations as code
   - Version control agent definitions
   - Collaborative debugging with team members

### 5. **Production Deployment**
   - Seamless path from development to production
   - Cloud-native deployment options
   - Monitoring and observability out of the box

### 6. **Cost Optimization**
   - Local development with Ollama (free)
   - Pay-per-use cloud deployment
   - Efficient token usage with stateful memory

## References

### Official Documentation
- [ADK Documentation](https://google.github.io/adk-docs/)
- [ADK Overview - Google Cloud](https://docs.cloud.google.com/agent-builder/agent-development-kit/overview)
- [TypeScript Quickstart for ADK](https://google.github.io/adk-docs/get-started/typescript/)

### Deployment Guides
- [Deploying Your Agent](https://google.github.io/adk-docs/deploy/)
- [Deploy an ADK Agent to Cloud Run - Codelabs](https://codelabs.developers.google.com/codelabs/production-ready-ai-with-gc/5-deploying-agents/deploy-an-adk-agent-to-cloud-run#0)

### Model Integration
- [Ollama Model Host for ADK](https://google.github.io/adk-docs/agents/models/ollama/)
- [Ollama Official Website](https://ollama.com/)

### Repositories
- [ADK Python Repository](https://github.com/google/adk-python)

### Articles
- [Agent Development Kit: Making it easy to build multi-agent applications](https://developers.googleblog.com/en/agent-development-kit-easy-to-build-multi-agent-applications/)


