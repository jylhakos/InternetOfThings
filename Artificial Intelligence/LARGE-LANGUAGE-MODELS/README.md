# Large Language Models

## Overview

Large Language Models (LLMs) are advanced artificial intelligence systems built on transformer architectures that process and generate human-like text. In the context of AI, LLMs represent a breakthrough in natural language understanding and generation, enabling applications such as conversational AI, content generation, code assistance, question answering, and complex reasoning tasks. This repository provides resources for deploying, orchestrating, and integrating LLMs into production applications, covering everything from model inference to retrieval-augmented generation (RAG) systems.

## Folder Structure

```
📁 LARGE-LANGUAGE-MODELS/
├── 📄 README.md
├── 📁 DEPLOYMENT/
├── 📁 INFERENCE/
├── 📁 MODELS/
├── 📁 ORCHESTRATION/
├── 📁 PROMPTS/
├── 📁 RAG/
├── 📁 SECURITY/
└── 📁 VECTOR-DATABASES/
```

## Folder Descriptions

### DEPLOYMENT
Contains deployment configurations and infrastructure code for deploying LLM applications across various platforms and frameworks. Includes:
- **LangChain**: AWS CDK infrastructure for deploying LangChain-based applications with Docker support
- **LangGraph**: Multi-agent workflow deployment with frontend and backend integration
- **Python**: FastAPI-based LLM server deployment with client examples
- **Serverless**: Serverless architecture implementations for LLM services
- **Spring Boot**: Java-based LLM application deployment with Docker and Terraform configurations

### INFERENCE
Provides inference server implementations and examples for running LLM models. Includes FastAPI and standard Python server implementations with client examples, RAG integration, and vector database connectivity.

### MODELS
Documentation and resources for specific LLM models, including Claude and Llama 4, covering model characteristics, usage guidelines, and best practices.

### ORCHESTRATION
Framework implementations for orchestrating LLM workflows and multi-agent systems:
- **LangChain**: Complete LangChain setup with Docker, Open WebUI integration, deployment scripts, and testing examples
- **LangGraph**: Graph-based workflow orchestration for complex multi-step LLM applications

### PROMPTS
Prompt engineering resources including templates, examples, and best practices for designing effective prompts to optimize LLM outputs.

### RAG
Retrieval-Augmented Generation (RAG) pipeline implementations combining LLMs with external knowledge bases:
- Vector database integration
- Document processing and chunking
- LlamaIndex framework examples
- Agent implementations with tool usage

### SECURITY
Common security resources focused on protecting LLM applications from prompt injection attacks and other vulnerabilities. This folder provides in-depth coverage of:

#### Prompt Injection Attacks
- **Direct Prompt Injection**: Malicious instructions sent directly to override system prompts
- **Indirect Prompt Injection**: Hidden instructions in external data sources (web pages, documents, emails)
- **Jailbreaking Techniques**: Methods to bypass LLM safety guardrails and ethical constraints
- **Attack Vectors**: Code injection, multimodal attacks, payload splitting, persona switching, multilingual obfuscation

#### Detection Methods
- **TaskTracker**: Activation-based detection analyzing LLM internal states (activations) during inference to identify task drift caused by injection attempts. Achieves ROC AUC greater than 0.99 across multiple models
- **Automated Monitors**: Pattern detection for known injection techniques and anomaly detection for unusual behavior
- **Logging and Alerting**: Real-time monitoring of interactions to identify suspicious prompts and track security events
- **Red Teaming**: Continuous adversarial testing using simulated attacks to validate system resilience

#### Prevention Strategies
- **Design-Time Mitigations**: System prompt engineering, instruction hierarchy, spotlighting with delimiters, least privilege access control, and parameterization
- **Runtime Mitigations**: Input validation and moderation, output validation, data loss prevention (DLP), and human-in-the-loop oversight for sensitive operations

#### Open-Source Security Tools
- **Augustus**: LLM vulnerability scanner
- **promptmap2**: Automated injection scanner
- **Promptfoo**: Red team testing framework
- **Garak**: NVIDIA LLM security scanner

#### Implementation Resources
- Docker deployment configurations
- Python-based demonstration modules
- PyTest test suites for validation
- Setup scripts for Ollama with open-source models (Llama, Mistral, Phi, Gemma, Qwen)
- Security testing techniques including fuzzing, obfuscation testing, and few-shot attacks

The SECURITY folder emphasizes practical demonstrations using local LLM deployments with Ollama, enabling hands-on testing and validation of security measures without dependency on external API services.

### VECTOR-DATABASES
Vector database setup, configuration, and usage examples for storing and retrieving embeddings used in semantic search and RAG applications.

## Example: Large Language Models deployed on AWS

To utilize AWS for AI, you can leverage services like Amazon SageMaker for model development and deployment, Amazon Bedrock for accessing and customizing foundation models.

Client (React) → API Gateway → Lambda/ECS → Vector DB (OpenSearch/Pinecone) → LLM (Ollama/vLLM)

1. Setting up the AWS

Amazon S3

Store your documents in an S3 bucket.

S3 bucket provides scalable and durable storage for your knowledge base.

Amazon SageMaker

Consider using SageMaker for deploying your LLM server and potentially other components like the embedding model.

Vector database

Choose a vector database like Pinecone, Milvus, or a managed service like Amazon OpenSearch Service or Amazon Aurora PostgreSQL with pgvector for storing document embeddings.

API Gateway

Set up API Gateway to handle incoming requests from your client application and route them to your backend service. 

Lambda Functions

Use Lambda functions to handle specific tasks like document processing, embedding generation, and RAG logic.

IAM Roles and Policies:

Ensure proper access control for your services using IAM roles and policies.

2. Deploying the LLM Server (e.g., Ollama)

Instance Type

Choose an appropriate EC2 instance type for your chosen LLM (e.g., GPU instances for larger models).

Ollama Setup

Install and configure Ollama on the EC2 instance, and download your desired open-source LLM (e.g., Llama 2, Mistral).

API endpoint

Expose an API endpoint from your Ollama server to receive requests and send responses.

3. Document processing and Embedding generation

Chunking

Break down your documents into smaller chunks to optimize embedding generation and search.

Embeddings model

Use an embedding model (e.g., SentenceTransformers, BGE embeddings) to convert text chunks into vector representations.

Vector storage

Store the generated embeddings in your chosen vector database, along with metadata about the original document chunks.

4. Building the RAG workflow

User Input

The client sends a question to your API endpoint.

Vector Search

Your application queries the vector database to find the most relevant document chunks based on semantic similarity with the user's question.

Contextualization

Retrieve the content of the relevant document chunks.

Prompt Engineering

Construct a prompt that includes the user's question and the retrieved context.

LLM Inference

Send the prompt to your Ollama server (or your deployed LLM) to generate a response.

Response

Return the LLM's response to the client. 

References

Amazon SageMaker

https://aws.amazon.com/sagemaker/

