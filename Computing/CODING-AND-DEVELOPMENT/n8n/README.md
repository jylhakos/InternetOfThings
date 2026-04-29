# Chat with Local LLMs using n8n and Ollama

This project explains how to build an AI-powered chat workflow using n8n and Ollama for local Large Language Model (LLM) interactions. The workflow provides a user-friendly chat interface for seamless interaction with self-hosted LLMs.

![n8n AI Workflow](n8n.png)

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation and Setup](#installation-and-setup)
  - [Virtual Environment Setup](#virtual-environment-setup)
  - [Installing n8n](#installing-n8n)
  - [Installing Ollama](#installing-ollama)
- [Deployment Recommendations: Native vs Docker](#deployment-recommendations-native-vs-docker)
  - [Recommended Choice](#recommended-choice)
  - [GPU Configuration Comparison](#gpu-configuration-comparison)
  - [Security Considerations](#security-considerations)
  - [Performance Comparison](#performance-comparison)
  - [Recommendation Summary](#recommendation-summary)
- [Understanding Ollama and n8n Integration](#understanding-ollama-and-n8n-integration)
  - [What is Ollama?](#what-is-ollama)
  - [How Ollama Works](#how-ollama-works)
  - [How Ollama Integrates with n8n](#how-ollama-integrates-with-n8n)
  - [Available Open Source Models](#available-open-source-models)
  - [Deploying and Using Models with Ollama](#deploying-and-using-models-with-ollama)
  - [Model Selection Guidelines](#model-selection-guidelines)
  - [Workflow Integration Details](#workflow-integration-details)
  - [Testing Different Models in the Workflow](#testing-different-models-in-the-workflow)
  - [Advanced Ollama Configuration](#advanced-ollama-configuration)
  - [Ollama Workflow Interaction Summary](#ollama-workflow-interaction-summary)
- [Running the Application](#running-the-application)
  - [Local Development](#local-development)
  - [Docker Deployment](#docker-deployment)
- [Workflow Components](#workflow-components)
  - [How It Works](#how-it-works)
  - [Node Configuration](#node-configuration)
- [AI Concepts in n8n](#ai-concepts-in-n8n)
  - [What is an AI Agent](#what-is-an-ai-agent)
  - [What is a Tool in AI](#what-is-a-tool-in-ai)
- [Testing the Application](#testing-the-application)
  - [Unit Testing](#unit-testing)
  - [Integration Testing](#integration-testing)
  - [Manual Testing](#manual-testing)
- [DevOps Setup Guide](#devops-setup-guide)
  - [Environment Configuration](#environment-configuration)
  - [Monitoring and Logs](#monitoring-and-logs)
  - [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)
- [References](#references)

## Overview

This n8n workflow allows you to interact with your self-hosted Large Language Models (LLMs) through a user-friendly chat interface. By connecting to Ollama, a powerful tool for managing local LLMs, you can send prompts and receive AI-generated responses directly within n8n.

### Use Cases

- **Private AI Interactions**: Appropriate for scenarios where data privacy and confidentiality are important
- **Cost-Effective LLM Usage**: Avoid ongoing cloud API costs by running models on your own hardware
- **Experimentation & Learning**: A great way to explore and experiment with different LLMs in a local, controlled environment
- **Prototyping & Development**: Build and test AI-powered applications without relying on external services

## Project Structure

```
n8n/
├── 📁 workflows/
│   └── 📄 chat_with_local_llms_ollama.json
├── 📁 tests/
│   ├── 📄 test_workflow.py
│   └── 📄 test_integration.py
├── 📁 docs/
│   └── 📄 architecture.md
├── 📁 src/
│   └── 📄 helpers.py
├── 📄 .gitignore
├── 📄 README.md
├── 📄 requirements.txt
├── 📄 docker-compose.yml
├── 📄 Dockerfile
└── 📄 n8n.png
```

## Prerequisites

Before you begin, ensure you have the following installed:

### Required Software

- **Python 3.8 or higher**: For running test scripts and automation
- **Node.js 18 or higher**: Required for n8n installation
- **npm or pnpm**: Node package manager
- **Docker & Docker Compose** (optional but recommended): For containerized deployment
- **Ollama**: Local LLM runtime

### System Requirements

- **RAM**: Minimum 8GB (16GB recommended for larger models)
- **Storage**: At least 10GB free space for models
- **OS**: Linux (Ubuntu recommended), macOS, or Windows with WSL2

## Installation and Setup

### Virtual Environment Setup

It is recommended to use a Python virtual environment to isolate project dependencies.

#### On Linux/macOS:

```bash
# Navigate to project directory
cd "/path/to/n8n"

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (should show path to venv python)
which python
python --version
```

#### On Windows:

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Verify activation
where python
python --version
```

#### Deactivating Virtual Environment

```bash
deactivate
```

### Installing n8n

#### Using npm (Recommended for Quick Start)

```bash
# Install n8n globally
npm install -g n8n

# Or run without installing
npx n8n
```

#### Using Docker

```bash
# Create volume for data persistence
docker volume create n8n_data

# Run n8n container
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  docker.n8n.io/n8nio/n8n
```

### Installing Ollama

Ollama can be installed in two ways: directly on your host system (recommended for better performance) or in a Docker container (better isolation).

#### Option 1: Local Installation (Recommended)

Installing Ollama directly on your host provides better performance and less complex configuration.

**On Linux:**

```bash
# Download and install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
ollama serve

# Verify installation
curl http://localhost:11434/api/version
```

**On macOS:**

```bash
# Download from https://ollama.com/download
# Or use Homebrew
brew install ollama

# Start Ollama
ollama serve

# Verify installation
curl http://localhost:11434/api/version
```

**On Windows:**

```powershell
# Download installer from https://ollama.com/download
# Run the installer
# Ollama will start automatically as a service

# Verify installation
curl http://localhost:11434/api/version
```

#### Option 2: Docker Installation

Running Ollama in Docker provides better isolation but may have slightly reduced performance.

**Using Docker Run:**

```bash
# Pull Ollama image
docker pull ollama/ollama

# Run Ollama container
docker run -d \
  --name ollama \
  -p 11434:11434 \
  -v ollama_data:/root/.ollama \
  ollama/ollama

# Verify Ollama is running
curl http://localhost:11434/api/version
```

**With GPU Support (NVIDIA):**

```bash
# Install NVIDIA Container Toolkit first
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

# Run with GPU support
docker run -d \
  --gpus=all \
  --name ollama \
  -p 11434:11434 \
  -v ollama_data:/root/.ollama \
  ollama/ollama
```

**Using Docker Compose:**

Add Ollama service to your docker-compose.yml:

```yaml
services:
  ollama:
    image: ollama/ollama
    container_name: ollama
    restart: unless-stopped
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    networks:
      - n8n-network
    # For GPU support (uncomment if you have NVIDIA GPU)
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: 1
    #           capabilities: [gpu]

volumes:
  ollama_data:
```

#### Pull a Model

**For Local Installation:**

```bash
# Pull Llama2 model (default)
ollama pull llama2

# Or pull other models
ollama pull llama2:13b
ollama pull llama2:70b
ollama pull codellama
ollama pull mistral
```

**For Docker Installation:**

```bash
# Execute pull command inside the container
docker exec -it ollama ollama pull llama2

# Or pull other models
docker exec -it ollama ollama pull llama2:13b
docker exec -it ollama ollama pull mistral
docker exec -it ollama ollama pull codellama
```

#### Verify Ollama Installation

**For Local Installation:**

```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# List installed models
ollama list
```

**For Docker Installation:**

```bash
# Check if Ollama container is running
docker ps | grep ollama

# Verify Ollama API
curl http://localhost:11434/api/version

# List installed models
docker exec -it ollama ollama list
```

## Deployment Recommendations: Native vs Docker

### Recommended Choice

**Native/Local Installation (Recommended for most users):**

Best for:
- Development and testing environments
- Maximum performance requirements
- Direct GPU access without additional layers
- Simplified troubleshooting and debugging
- Users familiar with their operating system

**Docker Installation (Recommended for production):**

Best for:
- Production deployments requiring isolation
- Multi-tenant environments
- Consistent deployment across different systems
- Easy rollback and version management
- Teams using containerized infrastructure

### GPU Configuration Comparison

#### Native Installation with GPU

**Linux (NVIDIA GPUs):**

```bash
# Install NVIDIA drivers
sudo ubuntu-drivers autoinstall

# Verify NVIDIA driver installation
nvidia-smi

# Ollama automatically detects and uses available GPUs
ollama run llama2

# Monitor GPU usage
watch -n 1 nvidia-smi
```

**Advantages:**
- Direct GPU access with minimal overhead
- Better performance (5-15% faster than Docker)
- Simpler driver management
- Lower latency for inference requests
- No containerization overhead

**Configuration:**
- No additional configuration required
- Ollama automatically detects CUDA-compatible GPUs
- Supports multiple GPUs (automatically load-balanced)

#### Docker Installation with GPU

**Linux (NVIDIA Docker):**

```bash
# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# Run Ollama with GPU support
docker run -d \
  --gpus=all \
  --name ollama \
  -p 11434:11434 \
  -v ollama_data:/root/.ollama \
  ollama/ollama

# Verify GPU is accessible inside container
docker exec -it ollama nvidia-smi
```

**Docker Compose with GPU:**

```yaml
services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    restart: unless-stopped
```

**Advantages:**
- Process isolation and resource limits
- Easy to update and rollback versions
- Consistent environment across deployments
- Better for multi-GPU resource allocation

**Considerations:**
- Requires NVIDIA Container Toolkit installation
- Slightly reduced performance (5-15% overhead)
- Additional layer of complexity in troubleshooting

### Security Considerations

#### Native Linux Installation

**Security Aspects:**

1. **Process Isolation:**
   - Ollama runs as a system service (typically under ollama user)
   - Limited isolation from host system
   - Shares kernel and system resources with other processes

2. **Network Exposure:**
   - Default: binds to localhost:11434 (local access only)
   - Can be configured to bind to 0.0.0.0 (all interfaces)
   - Recommendation: Use firewall rules to restrict access

   ```bash
   # Check Ollama binding
   sudo netstat -tulpn | grep 11434
   
   # Configure firewall (ufw example)
   sudo ufw allow from 192.168.1.0/24 to any port 11434
   sudo ufw deny 11434
   ```

3. **File System Access:**
   - Full access to system files (within user permissions)
   - Models stored in ~/.ollama or /usr/share/ollama
   - Potential risk if service account is compromised

4. **Updates and Patching:**
   - Manual update process required
   - User responsible for security patches
   - System-wide dependencies may conflict

**Security Recommendations:**
- Run Ollama service under dedicated user account (non-root)
- Use firewall rules to restrict network access
- Keep system and Ollama updated regularly
- Monitor system logs for unusual activity
- Consider AppArmor or SELinux profiles for additional sandboxing

#### Docker Installation

**Security Aspects:**

1. **Process Isolation:**
   - Container provides namespace isolation
   - Separate process tree from host
   - Limited access to host resources by default
   - Uses Linux cgroups for resource constraints

2. **Network Isolation:**
   - Runs in isolated network namespace
   - Port mapping required for external access
   - Can use Docker networks for service-to-service communication
   
   ```bash
   # Restrict to localhost only
   docker run -d \
     --name ollama \
     -p 127.0.0.1:11434:11434 \
     -v ollama_data:/root/.ollama \
     ollama/ollama
   ```

3. **File System Isolation:**
   - Models stored in Docker volumes (isolated from host)
   - Read-only root filesystem possible
   - Limited host file system access
   
   ```yaml
   # Docker Compose with read-only root
   services:
     ollama:
       image: ollama/ollama:latest
       read_only: true
       volumes:
         - ollama_data:/root/.ollama
         - /tmp
   ```

4. **Resource Limits:**
   - CPU and memory limits enforceable
   - Prevents resource exhaustion attacks
   
   ```yaml
   services:
     ollama:
       deploy:
         resources:
           limits:
             cpus: '4'
             memory: 8G
           reservations:
             cpus: '2'
             memory: 4G
   ```

5. **Updates and Patching:**
   - Simple image update process
   - Immutable infrastructure approach
   - Easier rollback if issues occur

**Security Recommendations:**
- Use official Ollama Docker images only
- Run containers as non-root user when possible
- Enable Docker content trust (DCT) for image verification
- Use Docker secrets for sensitive configuration
- Implement network policies to restrict inter-container communication
- Regularly scan images for vulnerabilities
- Enable Docker logging and monitoring
- Use read-only root filesystem where applicable

### Security Comparison Summary

| Aspect | Native Linux | Docker |
|--------|-------------|---------|
| Process Isolation | Limited (user-based) | Strong (namespace) |
| Network Isolation | Firewall-dependent | Built-in network isolation |
| File System Security | Host filesystem access | Volume-based isolation |
| Resource Control | OS-level limits | cgroups enforcement |
| Attack Surface | Larger (system-wide) | Smaller (containerized) |
| Update Process | Manual, system-wide | Image-based, isolated |
| Audit Trail | System logs | Container + system logs |
| Compliance | Standard Linux auditing | Container-specific tools |

### Performance Comparison

| Metric | Native Linux | Docker |
|--------|-------------|---------|
| Inference Speed | Baseline (100%) | 85-95% of native |
| GPU Performance | Optimal | 90-95% of native |
| Memory Overhead | Minimal | +100-500MB |
| Startup Time | ~2-5 seconds | ~5-10 seconds |
| Model Loading | Direct disk access | Volume mapping overhead |

### Recommendation Summary

**Use Native Installation when:**
- Running on development machines
- Maximum performance is critical
- You need direct system access for debugging
- Working with resource-constrained environments
- Single-user or trusted environments

**Use Docker Installation when:**
- Deploying to production environments
- Security and isolation are priorities
- Managing multiple Ollama instances
- Requiring consistent deployment across teams
- Using container orchestration (Kubernetes, Docker Swarm)
- Need easy version management and rollback
- Implementing resource quotas and limits

**Hybrid Approach:**
Many teams use native installation for development and Docker for production, balancing performance during development with security and manageability in production.

## Understanding Ollama and n8n Integration

### What is Ollama?

Ollama is a lightweight, open-source runtime that enables you to run Large Language Models (LLMs) locally on your own hardware. It provides a simple interface for downloading, managing, and running various open-source language models without requiring cloud services or external APIs.

**Key Features:**
- **Local Execution**: All model inference happens on your machine (Docker)
- **Model Management**: Easy download, update, and version control of models
- **REST API**: Simple HTTP API for model interaction
- **Optimized Performance**: CPU and GPU acceleration support
- **Memory Efficient**: Smart model loading and caching
- **Cross-Platform**: Runs on Linux, macOS, and Windows

### How Ollama Works

Ollama operates as a local server that manages and executes LLM models:

1. **Model Storage**: Models are downloaded and stored in a local directory (typically `~/.ollama/models`)
2. **Server Process**: Runs as a background service on port 11434
3. **API Interface**: Exposes REST endpoints for model inference
4. **Runtime Optimization**: Automatically optimizes models for your hardware (CPU/GPU)
5. **Memory Management**: Loads models into RAM on-demand and caches them for performance

**Architecture Flow:**
```
Client Request → Ollama API (Port 11434) → Model Manager → 
Inference Engine (CPU/GPU) → Token Generation → Response Stream
```

### How Ollama Integrates with n8n

The integration between Ollama and n8n happens through the **Ollama Chat Model Node**, which is part of n8n's LangChain integration:

1. **Node Connection**: The Ollama Chat Model node connects to the Ollama API via HTTP
2. **Request Transmission**: n8n sends user prompts to `http://localhost:11434/api/generate` or `/api/chat`
3. **Model Execution**: Ollama processes the request using the selected model
4. **Response Streaming**: Ollama streams tokens back to n8n in real-time
5. **Chain Integration**: The LLM Chain node manages context and formats responses

**Communication Protocol:**
```
n8n Workflow → LangChain LLM Chain → Ollama Chat Model Node →
HTTP POST to Ollama API → Model Inference → JSON Response →
Response Processing → Chat Interface Display
```

**API Request Example:**
```json
POST http://localhost:11434/api/generate
{
  "model": "llama2",
  "prompt": "What is n8n?",
  "stream": false
}
```

**API Response Example:**
```json
{
  "model": "llama2",
  "response": "n8n is a workflow automation platform...",
  "done": true,
  "total_duration": 5000000000,
  "load_duration": 500000000
}
```

### Available Open Source Models

Ollama supports a wide range of open-source LLMs. Here are the most popular models for local deployment:

#### General Purpose Models

| Model | Parameters | Size | RAM Required | Use Case |
|-------|------------|------|--------------|----------|
| **Llama 2** | 7B | 3.8GB | 8GB | General chat, Q&A |
| **Llama 2** | 13B | 7.3GB | 16GB | Better reasoning, longer context |
| **Llama 2** | 70B | 39GB | 64GB | Production-quality responses |
| **Llama 3** | 8B | 4.7GB | 8GB | Improved performance over Llama 2 |
| **Llama 3** | 70B | 40GB | 64GB | State-of-the-art open source |
| **Mistral** | 7B | 4.1GB | 8GB | Fast inference, good quality |
| **Mixtral** | 8x7B | 26GB | 32GB | Mixture of experts, high quality |
| **Phi-3** | 3.8B | 2.3GB | 4GB | Small, efficient, Microsoft model |

#### Code-Specialized Models

| Model | Parameters | Size | RAM Required | Use Case |
|-------|------------|------|--------------|----------|
| **CodeLlama** | 7B | 3.8GB | 8GB | Code generation, debugging |
| **CodeLlama** | 13B | 7.3GB | 16GB | Advanced code tasks |
| **CodeLlama** | 34B | 19GB | 32GB | Complex code generation |
| **DeepSeek Coder** | 6.7B | 3.8GB | 8GB | Code completion, explanation |
| **StarCoder** | 15B | 8.4GB | 16GB | Code generation across languages |

#### Specialized Models

| Model | Parameters | Size | Description |
|-------|------------|------|-------------|
| **Vicuna** | 7B/13B | 3.8GB/7.3GB | Fine-tuned for conversation |
| **Orca 2** | 7B/13B | 3.8GB/7.3GB | Reasoning and logic tasks |
| **Neural Chat** | 7B | 4.1GB | Optimized for dialogue |
| **Dolphin** | 7B/13B | 3.8GB/7.3GB | Uncensored, versatile |
| **Solar** | 10.7B | 6.1GB | Korean-English bilingual |

### Deploying and Using Models with Ollama

#### Pulling Models

```bash
# General purpose models
ollama pull llama2           # Default 7B version
ollama pull llama2:13b       # 13B version
ollama pull llama2:70b       # 70B version
ollama pull llama3           # Latest Llama 3
ollama pull mistral          # Mistral 7B
ollama pull mixtral          # Mixtral 8x7B
ollama pull phi3             # Microsoft Phi-3

# Code models
ollama pull codellama        # Code-focused Llama
ollama pull deepseek-coder   # DeepSeek Coder
ollama pull starcoder        # StarCoder

# Specialized models
ollama pull vicuna           # Conversation-optimized
ollama pull orca2            # Reasoning tasks
ollama pull neural-chat      # Dialogue model
```

#### Listing Available Models

```bash
# List all models in Ollama library
ollama list

# Search for specific models
ollama search llama
```

#### Running Models

```bash
# Interactive chat mode
ollama run llama2

# Specify a different model
ollama run mistral

# Run with custom parameters
ollama run llama2 --temperature 0.8 --top-p 0.9
```

#### Removing Models

```bash
# Remove a model to free up space
ollama rm llama2:70b

# Remove specific version
ollama rm codellama:13b
```

### Model Selection Guidelines

Choose the right model based on your requirements:

**For Learning and Experimentation:**
- **Llama 2 (7B)**: Best starting point, good balance of speed and quality
- **Phi-3 (3.8B)**: Fastest, lowest resource requirements
- **Mistral (7B)**: Excellent performance for the size

**For Code-Related Tasks:**
- **CodeLlama (7B/13B)**: Specialized for programming tasks
- **DeepSeek Coder**: Strong code understanding
- **StarCoder**: Multi-language support

**For Production Use:**
- **Llama 3 (70B)**: Best open-source quality
- **Mixtral (8x7B)**: Great quality with better efficiency
- **Llama 2 (70B)**: Proven, stable performance

**For Resource-Constrained Environments:**
- **Phi-3**: Minimal RAM usage
- **Llama 2 (7B)**: Good quality on 8GB RAM
- **Mistral (7B)**: Efficient inference

### Workflow Integration Details

When you configure the n8n workflow to use Ollama:

1. **Model Configuration**: Select the model in the Ollama Chat Model node
2. **Connection Setup**: Point to `http://localhost:11434` (or `host.docker.internal:11434` for Docker)
3. **Parameter Tuning**: Adjust temperature, top_k, top_p for response characteristics
4. **Context Management**: The LLM Chain handles conversation history
5. **Response Handling**: Streaming responses for real-time chat experience

**Example Configuration in n8n:**

```
Ollama Chat Model Node Settings:
├── Base URL: http://localhost:11434
├── Model: llama2 (or any installed model)
├── Temperature: 0.7 (randomness: 0=deterministic, 1=creative)
├── Top K: 40 (consider top 40 tokens)
├── Top P: 0.9 (nucleus sampling threshold)
├── Max Tokens: 2048 (maximum response length)
└── Context Window: 4096 (conversation history size)
```

### Testing Different Models in the Workflow

You can easily switch between models to compare performance:

1. **Pull Multiple Models:**
   ```bash
   ollama pull llama2
   ollama pull mistral
   ollama pull codellama
   ollama pull phi3
   ```

2. **Configure in n8n:**
   - Open the Ollama Chat Model node
   - Select different models from the dropdown
   - Test with the same prompts to compare

3. **Performance Comparison:**
   ```bash
   # Test response time for different models
   time ollama run llama2 "Explain n8n in one sentence"
   time ollama run mistral "Explain n8n in one sentence"
   time ollama run phi3 "Explain n8n in one sentence"
   ```

### Advanced Ollama Configuration

#### Custom Model Parameters

```bash
# Create a custom model with specific parameters
ollama create mymodel -f Modelfile

# Example Modelfile:
# FROM llama2
# PARAMETER temperature 0.8
# PARAMETER top_k 40
# PARAMETER top_p 0.9
# SYSTEM You are a helpful coding assistant specialized in automation.
```

#### Multi-Model Workflows

You can create workflows that use different models for different tasks:

```
User Query →
├── Code Questions → CodeLlama (7B)
├── General Chat → Llama 2 (7B)
├── Complex Analysis → Mixtral (8x7B)
└── Quick Answers → Phi-3 (3.8B)
```

#### GPU Acceleration

If you have an NVIDIA GPU:

```bash
# Check GPU availability
nvidia-smi

# Ollama automatically uses GPU if available
# Verify GPU usage during inference
watch -n 1 nvidia-smi
```

### Ollama Workflow Interaction Summary

The complete interaction flow in the "Chat with Local LLMs using n8n and Ollama" workflow:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. User sends message in n8n chat interface                 │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Chat Trigger Node captures input                         │
│    - Message text                                           │
│    - Session context                                        │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. LLM Chain Node processes request                         │
│    - Retrieves conversation history                         │
│    - Formats prompt with context                            │
│    - Prepares for LLM                                       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Ollama Chat Model Node sends HTTP request                │
│    POST http://localhost:11434/api/generate                 │
│    {                                                        │
│      "model": "llama2",                                     │
│      "prompt": "User message with context",                 │
│      "stream": false                                        │
│    }                                                        │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Ollama Server processes request                          │
│    - Loads model into memory (if not cached)                │
│    - Tokenizes input prompt                                 │
│    - Runs inference through transformer                     │
│    - Generates tokens sequentially                          │
│    - Formats response                                       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Ollama returns JSON response                             │
│    {                                                        │
│      "model": "llama2",                                     │
│      "response": "Generated text...",                       │
│      "done": true,                                          │
│      "context": [token_ids],                                │
│      "eval_duration": 1500000000                            │
│    }                                                        │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. LLM Chain processes response                             │
│    - Updates conversation context                           │
│    - Formats for display                                    │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 8. Response displayed in chat interface                     │
└─────────────────────────────────────────────────────────────┘
```

**Key Integration Points:**

1. **HTTP Communication**: n8n communicates with Ollama via REST API
2. **Model Selection**: Configured in the Ollama Chat Model node
3. **Context Persistence**: LLM Chain manages conversation history
4. **Local Processing**: All inference happens locally, no external API calls
5. **Real-time Streaming**: Supports streaming responses for immediate feedback

## Running the Application

### Local Development

1. **Ensure Virtual Environment is Active**:

```bash
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows
```

2. **Start Ollama** (in a separate terminal):

```bash
ollama serve
```

3. **Start n8n**:

```bash
n8n
```

4. **Access n8n Editor**:

Open your browser and navigate to:
```
http://localhost:5678
```

5. **Import Workflow**:

- Click on "Workflows" in the left sidebar
- Click "Import from File" or "Import from URL"
- Select `workflows/chat_with_local_llms_ollama.json`
- Click "Import"

6. **Configure Credentials**:

- Open the "Ollama Chat Model" node
- Click on "Create New Credential"
- Set the Base URL: `http://localhost:11434`
- Save the credential

7. **Test the Workflow**:

- Click "Execute Workflow" or use the Chat interface
- Enter a message in the chat window
- Observe the AI response

### Docker Deployment

Docker deployment is recommended for production environments as it provides better isolation and reproducibility.

#### Using Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  n8n:
    image: docker.n8n.io/n8nio/n8n
    container_name: n8n
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=${N8N_HOST:-localhost}
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=http://${N8N_HOST:-localhost}:5678/
      - GENERIC_TIMEZONE=${GENERIC_TIMEZONE:-UTC}
    volumes:
      - n8n_data:/home/node/.n8n
      - ./workflows:/home/node/.n8n/workflows
    networks:
      - n8n-network
    # Enable access to host network if Ollama runs on host
    # Comment this out if using Ollama in Docker
    extra_hosts:
      - "host.docker.internal:host-gateway"

  # Optional: Ollama service (uncomment to run Ollama in Docker)
  # If you uncomment this, update n8n Ollama node Base URL to: http://ollama:11434
  # ollama:
  #   image: ollama/ollama:latest
  #   container_name: ollama
  #   restart: unless-stopped
  #   ports:
  #     - "11434:11434"
  #   volumes:
  #     - ollama_data:/root/.ollama
  #   networks:
  #     - n8n-network

volumes:
  n8n_data:
  # ollama_data:  # Uncomment if using Ollama in Docker

networks:
  n8n-network:
    driver: bridge
```

#### Run with Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f n8n

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

#### Docker Network Configuration for Ollama

The network configuration depends on how you deployed both n8n and Ollama:

**Scenario 1: Both n8n and Ollama in Docker (Same Network)**

If both services are in the same Docker network (recommended):

```yaml
# In docker-compose.yml
services:
  n8n:
    image: docker.n8n.io/n8nio/n8n
    networks:
      - n8n-network
    # ...
  
  ollama:
    image: ollama/ollama
    networks:
      - n8n-network
    # ...

networks:
  n8n-network:
    driver: bridge
```

In n8n Ollama Chat Model node:
- **Base URL**: `http://ollama:11434`

**Scenario 2: n8n in Docker, Ollama on Host**

If n8n runs in Docker but Ollama is on the host:

```bash
# Option 1: Use host network mode
docker run -it --rm \
  --name n8n \
  --net=host \
  -v n8n_data:/home/node/.n8n \
  docker.n8n.io/n8nio/n8n

# Option 2: Access via host.docker.internal (recommended)
# Add to docker-compose.yml:
services:
  n8n:
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

In n8n Ollama Chat Model node:
- **Base URL**: `http://host.docker.internal:11434`

**Scenario 3: Both n8n and Ollama on Host (Local Development)**

If both services run directly on your machine:

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start n8n
n8n
```

In n8n Ollama Chat Model node:
- **Base URL**: `http://localhost:11434`

**Scenario 4: n8n on Host, Ollama in Docker**

If n8n runs on the host but Ollama is in Docker:

```bash
# Run Ollama with port mapping
docker run -d \
  --name ollama \
  -p 11434:11434 \
  ollama/ollama
```

In n8n Ollama Chat Model node:
- **Base URL**: `http://localhost:11434`

## Workflow Components

### How It Works

The workflow consists of three main components that work together to create an interactive chat experience:

1. **When chat message received** (`chatTrigger`):
   - Captures user input from the chat interface
   - Triggers the workflow when a new message is received
   - Passes the message to the next node

2. **Chat LLM Chain** (`chainLlm`):
   - Orchestrates the conversation flow
   - Manages the connection between the trigger and the AI model
   - Handles message formatting and response streaming

3. **Ollama Chat Model** (`lmChatOllama`):
   - Connects to your local Ollama server
   - Sends the user's message to the LLM
   - Receives and returns the AI-generated response

**Data Flow**:
```
User Input → Chat Trigger → LLM Chain → Ollama Chat Model → AI Response → User
```

### Node Configuration

#### Chat Trigger Node

- **Type**: `@n8n/n8n-nodes-langchain.chatTrigger`
- **Version**: 1.1
- **Purpose**: Entry point for user messages
- **Configuration**: Default settings are sufficient

#### Chat LLM Chain Node

- **Type**: `@n8n/n8n-nodes-langchain.chainLlm`
- **Version**: 1.4
- **Purpose**: Manages conversation flow and context
- **Configuration**: Connect to Chat Trigger and Ollama Chat Model

#### Ollama Chat Model Node

- **Type**: `@n8n/n8n-nodes-langchain.lmChatOllama`
- **Version**: 1
- **Configuration**:
  - **Base URL**: `http://localhost:11434` (default)
  - **Model**: Select from available models (llama2, llama2:13b, llama2:70b, etc.)
  - **Temperature**: Control randomness (0.0 - 1.0)
  - **Top K**: Number of token choices (default: 40)
  - **Top P**: Probability threshold (default: 0.9)

## AI Concepts in n8n

### What is an AI Agent

An AI agent builds on Large Language Models (LLMs) to create goal-oriented functionality. While LLMs generate text based on input by predicting the next word, AI agents add the ability to:

- **Use Tools**: Access external APIs, databases, and services
- **Act on Decisions**: Execute actions based on LLM outputs
- **Complete Tasks**: Work towards specific goals autonomously
- **Solve Problems**: Break down complex tasks into manageable steps

#### LLM vs AI Agent Comparison

| Core Capability | LLM | AI Agent |
|----------------|-----|----------|
| Primary Function | Text generation | Goal-oriented task completion |
| Decision-Making | Simulates choices in text | Selects and executes actions |
| Uses Tools/APIs | No | Yes |
| Workflow Complexity | Single-step | Multi-step |
| Scope | Generates language | Performs complex, real-world tasks |
| Example | Generating a paragraph | Scheduling an appointment |

### What is a Tool in AI

In AI, 'tools' has a specific meaning. Tools act like add-ons that your AI can use to access extra context or resources. They are interfaces that an agent can use to interact with the world.

#### Available Tools in n8n

n8n provides several tool sub-nodes:

1. **Call n8n Workflow Tool**: Load any n8n workflow as a tool
2. **Custom Code Tool**: Write JavaScript/Python code for custom functionality
3. **HTTP Request Tool**: Make API calls to fetch data or interact with services
4. **Calculator Tool**: Perform mathematical calculations
5. **Wikipedia Tool**: Search and retrieve Wikipedia content
6. **SerpAPI Tool**: Perform Google searches programmatically

#### Tool Use Cases

- Access real-time data from APIs
- Query databases for business intelligence
- Perform calculations and data transformations
- Search the web for current information
- Execute custom business logic
- Integrate with third-party services

## Testing the Application

### Unit Testing

Create test files to validate individual components.

#### Example Test: `tests/test_workflow.py`

```python
import pytest
import requests
import json

def test_ollama_connection():
    """Test Ollama server connectivity"""
    response = requests.get('http://localhost:11434/api/version')
    assert response.status_code == 200
    data = response.json()
    assert 'version' in data

def test_ollama_model_available():
    """Test if required model is available"""
    response = requests.get('http://localhost:11434/api/tags')
    assert response.status_code == 200
    data = response.json()
    models = [model['name'] for model in data.get('models', [])]
    assert any('llama2' in model for model in models)

def test_n8n_health():
    """Test n8n server health"""
    response = requests.get('http://localhost:5678/healthz')
    assert response.status_code == 200
```

#### Run Unit Tests

```bash
# Ensure virtual environment is active
source venv/bin/activate

# Install pytest
pip install pytest requests

# Run tests
pytest tests/test_workflow.py -v

# Run with coverage
pytest tests/test_workflow.py --cov=src --cov-report=html
```

### Integration Testing

Test the complete workflow end-to-end.

#### Example Integration Test: `tests/test_integration.py`

```python
import pytest
import requests
import time

@pytest.fixture
def n8n_webhook_url():
    """Webhook URL for the chat workflow"""
    return "http://localhost:5678/webhook-test/chat"

def test_chat_workflow_response(n8n_webhook_url):
    """Test complete chat workflow"""
    # Send a test message
    payload = {
        "chatInput": "Hello, what is 2+2?"
    }
    
    response = requests.post(
        n8n_webhook_url,
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert 'output' in data
    assert len(data['output']) > 0

def test_chat_workflow_latency(n8n_webhook_url):
    """Test response time"""
    payload = {"chatInput": "Hi"}
    
    start_time = time.time()
    response = requests.post(n8n_webhook_url, json=payload)
    end_time = time.time()
    
    latency = end_time - start_time
    assert response.status_code == 200
    assert latency < 30  # Should respond within 30 seconds
```

### Manual Testing

#### Test Checklist

1. **Ollama Service**:
   ```bash
   # Check Ollama is running
   curl http://localhost:11434/api/version
   
   # List available models
   ollama list
   ```

2. **n8n Service**:
   ```bash
   # Check n8n is accessible
   curl http://localhost:5678/healthz
   ```

3. **Workflow Import**:
   - Import the workflow JSON file
   - Verify all nodes are connected properly
   - Check for any error indicators

4. **Chat Interface**:
   - Open the chat interface
   - Send a simple greeting: "Hello"
   - Verify response is received
   - Test with various prompts:
     - "What is Python?"
     - "Write a haiku about automation"
     - "Explain n8n in one sentence"

5. **Model Performance**:
   - Monitor response times
   - Check memory usage: `docker stats` or `htop`
   - Verify model quality with complex questions

## DevOps Setup Guide

### Environment Configuration

#### Environment Variables

Create a `.env` file for configuration:

```bash
# n8n Configuration
N8N_HOST=localhost
N8N_PORT=5678
N8N_PROTOCOL=http
WEBHOOK_URL=http://localhost:5678/

# Timezone
GENERIC_TIMEZONE=UTC

# Database (optional for production)
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=localhost
DB_POSTGRESDB_PORT=5432
DB_POSTGRESDB_DATABASE=n8n
DB_POSTGRESDB_USER=n8n_user
DB_POSTGRESDB_PASSWORD=your_secure_password

# Execution
EXECUTIONS_MODE=regular
EXECUTIONS_TIMEOUT=300
EXECUTIONS_TIMEOUT_MAX=600

# Security
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=your_secure_password
```

#### Load Environment in Virtual Environment

```bash
# Activate virtual environment
source venv/bin/activate

# Load environment variables
export $(cat .env | xargs)

# Or use python-dotenv
pip install python-dotenv
```

### Monitoring and Logs

#### n8n Logs

```bash
# View n8n logs (npm installation)
n8n --log-level=debug

# Docker logs
docker logs -f n8n

# Docker Compose logs
docker-compose logs -f
```

#### Ollama Logs

```bash
# View Ollama logs
journalctl -u ollama -f

# Docker logs (if running Ollama in Docker)
docker logs -f ollama
```

#### Health Checks

```bash
# n8n health endpoint
curl http://localhost:5678/healthz

# Ollama health check
curl http://localhost:11434/api/version

# Create monitoring script
cat > check_health.sh << 'EOF'
#!/bin/bash
echo "Checking n8n..."
curl -s http://localhost:5678/healthz

echo -e "\nChecking Ollama..."
curl -s http://localhost:11434/api/version
EOF

chmod +x check_health.sh
./check_health.sh
```

### Security Considerations

#### Authentication

1. **Enable Basic Auth** for n8n:
   ```bash
   export N8N_BASIC_AUTH_ACTIVE=true
   export N8N_BASIC_AUTH_USER=admin
   export N8N_BASIC_AUTH_PASSWORD=your_secure_password
   ```

2. **Use HTTPS** in production:
   ```bash
   export N8N_PROTOCOL=https
   export N8N_SSL_KEY=/path/to/ssl/key.pem
   export N8N_SSL_CERT=/path/to/ssl/cert.pem
   ```

#### Network Security

1. **Firewall Rules**:
   ```bash
   # Allow only necessary ports
   sudo ufw allow 5678/tcp  # n8n
   sudo ufw enable
   ```

2. **Docker Network Isolation**:
   - Use Docker networks to isolate services
   - Avoid exposing Ollama port externally
   - Use `--net=host` only when necessary

#### Data Security

1. **Encrypt Credentials**:
   - n8n encrypts credentials by default
   - Backup encryption key: `~/.n8n/config`

2. **Backup Strategy**:
   ```bash
   # Backup n8n data
   docker run --rm -v n8n_data:/data -v $(pwd):/backup \
     ubuntu tar czf /backup/n8n_backup_$(date +%Y%m%d).tar.gz /data
   
   # Restore n8n data
   docker run --rm -v n8n_data:/data -v $(pwd):/backup \
     ubuntu tar xzf /backup/n8n_backup_YYYYMMDD.tar.gz -C /
   ```

## Troubleshooting

### Common Issues

#### 1. Ollama Connection Failed

**Symptoms**: "Unable to connect to Ollama server"

**Solutions**:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# Start Ollama service
ollama serve

# Check port availability
netstat -tuln | grep 11434

# For Docker, use host.docker.internal
# In Ollama node: http://host.docker.internal:11434
```

#### 2. n8n Port Already in Use

**Symptoms**: "Port 5678 is already in use"

**Solutions**:
```bash
# Find process using the port
lsof -i :5678
# or
netstat -tuln | grep 5678

# Kill the process
kill -9 <PID>

# Or use a different port
export N8N_PORT=5679
n8n
```

#### 3. Virtual Environment Not Activating

**Symptoms**: Commands not found, wrong Python version

**Solutions**:
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# Verify activation
which python
echo $VIRTUAL_ENV
```

#### 4. Model Not Found

**Symptoms**: "Model 'llama2' not found"

**Solutions**:
```bash
# List available models
ollama list

# Pull the required model
ollama pull llama2

# Check disk space
df -h
```

#### 5. Slow Response Times

**Symptoms**: Chat takes too long to respond

**Solutions**:
- Use smaller models (llama2:7b instead of llama2:70b)
- Increase available RAM
- Check CPU/GPU utilization
- Reduce context window size
- Optimize Ollama settings

#### 6. Workflow Import Fails

**Symptoms**: Error importing workflow JSON

**Solutions**:
```bash
# Validate JSON syntax
cat workflows/chat_with_local_llms_ollama.json | jq .

# Check file permissions
chmod 644 workflows/chat_with_local_llms_ollama.json

# Re-download workflow file
# Ensure no corruption during transfer
```

## References

### Official Documentation

- [n8n Documentation](https://docs.n8n.io/) - The n8n platform documentation
- [n8n GitHub Repository](https://github.com/n8n-io/n8n) - Source code and contribution guidelines
- [n8n Workflow Templates](https://n8n.io/workflows) - 900+ ready-to-use workflow templates
- [Ollama Documentation](https://ollama.com/library) - Ollama models library and documentation
- [Ollama GitHub](https://github.com/ollama/ollama) - Ollama source code

### AI and Workflow Resources

- [AI Concepts in n8n](https://docs.n8n.io/advanced-ai/intro-tutorial/) - Tutorial for building AI workflows
- [What's a Tool in AI?](https://docs.n8n.io/advanced-ai/examples/understand-tools/) - Understanding AI tools
- [Ollama Chat Model Node](https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.lmchatollama/) - Node-specific documentation
- [Chat with Local LLMs Workflow](https://n8n.io/workflows/2384-chat-with-local-llms-using-n8n-and-ollama/) - Original workflow template
- [n8n AI Agent Examples](https://docs.n8n.io/advanced-ai/examples/introduction/) - AI workflow examples and concepts
- [LangChain in n8n](https://docs.n8n.io/advanced-ai/langchain/overview/) - LangChain integration overview

### Installation and Setup Guides

- [n8n Installation Guide](https://docs.n8n.io/hosting/installation/) - Various installation methods
- [Docker Setup for n8n](https://docs.n8n.io/hosting/installation/docker/) - Containerized deployment
- [n8n with Docker Compose](https://docs.n8n.io/hosting/installation/server-setups/docker-compose/) - Multi-container setup
- [Self-hosting n8n](https://docs.n8n.io/hosting/) - Complete self-hosting guide

### Testing and DevOps

- [Python pytest Documentation](https://docs.pytest.org/) - Testing framework
- [Docker Documentation](https://docs.docker.com/) - Container platform
- [Docker Compose Documentation](https://docs.docker.com/compose/) - Multi-container applications

### Community and Support

- [n8n Community Forum](https://community.n8n.io/) - Ask questions and share knowledge
- [n8n Discord Server](https://discord.gg/n8n) - Real-time community chat
- [n8n YouTube Channel](https://www.youtube.com/c/n8n-io) - Video tutorials and demos

### Related Projects and Tools

- [LangChain](https://langchain.com/) - Framework for developing LLM applications
- [Llama 2](https://ai.meta.com/llama/) - Meta's open-source LLM
- [Node.js](https://nodejs.org/) - JavaScript runtime
- [Python](https://www.python.org/) - Programming language for testing and automation

---

**License**: This project follows n8n's license model. See [n8n License](https://github.com/n8n-io/n8n/blob/master/LICENSE.md) for details.

**Last Updated**: April 1, 2026