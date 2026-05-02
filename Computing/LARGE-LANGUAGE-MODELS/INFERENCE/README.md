# Inference for Large Language Models

This document explains what's Inference for Large Language Models.

## Table of Contents

- [What is LLM Inference?](#what-is-llm-inference)
- [How LLM Inference Works](#how-llm-inference-works)
  - [Prompt Processing Phase](#prompt-processing-phase)
  - [Decode Phase](#decode-phase)
- [What is an Inference Server?](#what-is-an-inference-server)
- [Inference Server Architecture](#inference-server-architecture)
- [Agents and LLMs](#agents-and-llms)
- [Retrieval-Augmented Generation (RAG)](#retrieval-augmented-generation-rag)
- [Vector Databases](#vector-databases)
- [Challenges in LLM Inference](#challenges-in-llm-inference)
- [Inference Optimization Techniques](#inference-optimization-techniques)
  - [Model Optimization](#model-optimization)
  - [Inference Techniques](#inference-techniques)
  - [Attention Mechanisms](#attention-mechanisms)
  - [Quantization](#quantization)
  - [KV Caching](#kv-caching)
  - [Batching](#batching)
  - [Model Parallelization](#model-parallelization)
- [Inference Performance Metrics](#inference-performance-metrics)
- [Inference Serving Frameworks](#inference-serving-frameworks)
- [Open-Source Inference Engines for Self-Hosted Deployment](#open-source-inference-engines-for-self-hosted-deployment)
  - [vLLM: High-Throughput Memory-Efficient Engine](#vllm-high-throughput-memory-efficient-engine)
  - [llama.cpp: C/C++ Implementation for Edge and Consumer Hardware](#llamacpp-cc-implementation-for-edge-and-consumer-hardware)
  - [SGLang: Structured Generation and High-Performance LLM Serving](#sglang-structured-generation-and-high-performance-llm-serving)
  - [NVIDIA Triton Inference Server](#nvidia-triton-inference-server)
  - [Text Generation Inference: Hugging Face Ecosystem](#text-generation-inference-hugging-face-ecosystem)
  - [ONNX Runtime](#onnx-runtime)
  - [DeepSpeed Model Implementations for Inference (MII)](#deepspeed-model-implementations-for-inference-mii)
  - [LMDeploy: Compressing, Deploying, and Serving LLMs](#lmdeploy-compressing-deploying-and-serving-llms)
  - [Ollama: Simplified Local Deployment](#ollama-simplified-local-deployment)
  - [Sampling Strategies and Temperature](#sampling-strategies-and-temperature)
  - [Context Window](#context-window)
  - [Optimization Strategies for Self-Hosted Models](#optimization-strategies-for-self-hosted-models)
  - [Comparative Overview of Open-Source Inference Engines](#comparative-overview-of-open-source-inference-engines)
- [Choosing the Right Inference for Production](#choosing-the-right-inference-for-production)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Example Use Case](#example-use-case)
- [References](#references)

---

## What is LLM Inference?

**Large Language Model (LLM) inference is the process of running a pre-trained model on new data to generate text one token at a time.**

At its core, **inference is the application of a trained machine learning model to new, unseen data**. In the context of LLMs, inference involves taking a user's input (a prompt) and processing it through the model's parameters to generate relevant outputs like text, code, or translations.

**Inference optimization** is a set of techniques to make LLM inference faster, cheaper, and more efficient. Optimization focuses on **reducing latency, improving throughput, and lowering hardware costs** without degrading model quality.

**Definition:** Inference is the active usage phase where the AI model uses its training data to generate results, unlike the training phase where it learns.

> **Reference:** [LLM Fundamentals – Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/journey/llm-fundamentals)

**Key Characteristics:**
- **Operational Phase**: AI inference is the operational phase of AI, where the model is able to apply what it's learned from training to real-world situations.
- **Pattern Recognition**: AI's ability to identify patterns and reach conclusions.
- **Computational Requirements**: For inference to be successful, AI models need to do a lot of math in a short period of time.
- **Real-Time Processing**: Unlike training, which is a one-time, resource-intensive process, inference happens repeatedly, often in real-time.

### Example Use Case

When you ask an AI assistant a question, the model processes your query token by token, predicting the next likely word or phrase in a sequence based on patterns it learned during training.

For instance:
- **User Input**: "What is the capital of France?"
- **Inference Process**: The model tokenizes the input, processes it through transformer layers, and predicts the most likely response tokens.
- **Output**: "The capital of France is Paris."

This entire process happens in milliseconds, demonstrating the power of optimized inference systems.

---

## How LLM Inference Works

LLM inference is the mechanism large language models use to generate human-like responses. Once a generative model receives an input prompt from the user, it draws on knowledge gained during training to predict the most likely tokens in the sequence before decoding those tokens into text outputs.

Inference begins with **tokenization**, where the input text is broken down into tokens that the model understands. These tokens are then passed through the model's **transformer layers**, which apply learned weights to produce contextual embeddings. Finally, a **decoding strategy** (like greedy search or beam search) generates the next most likely token, continuing until the response is complete.

This process takes place in two stages: the **prefill** and **decode** phases.

### Prompt Processing Phase

During the prefill stage, user inputs are converted into tokens before being converted into numerical values the model can understand and work with. In the context of generative LLM inference, **tokens represent words or parts of words**.

**Process:**
1. Input text is received
2. Tokenization converts text into token IDs
3. Tokens are embedded into vector representations
4. Position encodings are added
5. The entire prompt is processed through the model in parallel
6. Key-Value (KV) cache is populated for efficient future token generation

### Decode Phase

In the decoding phase, the model responds to the user prompt by generating a series of vector embeddings, the deep learning algorithm's response to the input prompt. It does this by **sequentially predicting the next token based on context and prior knowledge**.

**Process:**
1. The model generates predictions for the next token
2. A decoding strategy selects the most appropriate token
3. The new token is appended to the sequence
4. The KV cache is updated
5. The process iterates until:
   - An end-of-sequence token is generated
   - Maximum length is reached
   - A stopping criterion is met
6. Output tokens are converted back into human-readable language

---

## What is an Inference Server?

An **inference server is the component that manages how LLM inference runs**. It loads the models, connects to the required hardware (such as GPUs), and processes application requests. When a prompt arrives, the server allocates resources, executes the model, and returns the output.

### How Inference Servers Work

An inference server works by receiving input data, typically in the form of requests from clients, which can include queries, images, text, or other forms of data. It then processes this data through trained machine learning models or algorithms to generate predictions, classifications, or other outputs.

**Workflow:**
1. **Client Request**: A client application sends an HTTP/gRPC request with input data
2. **Request Queue**: The server queues incoming requests for processing
3. **Resource Allocation**: GPU memory and compute resources are allocated
4. **Model Loading**: The model is loaded into memory (if not already cached)
5. **Inference Execution**: The forward pass is executed through the model
6. **Response Generation**: Output tokens are generated iteratively
7. **Response Delivery**: Results are returned to the client via the API

### Infrastructure on a Server for LLMs

**Inference on a server for large language models (LLMs) is the process of using a pre-trained model to generate text, predictions, or code in real-time based on new, unseen input prompts.** It involves deploying the model on powerful hardware (typically GPUs) via an inference server to manage:
- High-throughput computing
- Low latency
- Efficient GPU memory management

---

## Inference Server Architecture

### Components of an Inference Server

1. **Model Repository**: Stores different versions of the LLM
2. **Runtime Engine**: Executes the model computations (e.g., ONNX Runtime, TensorRT)
3. **Backend Server**: Manages input/output queues and API endpoints
4. **Request Handler**: Processes HTTP/gRPC requests
5. **Model Loader**: Loads models into GPU memory
6. **Batch Manager**: Groups requests for efficient processing
7. **KV Cache Manager**: Manages attention cache for efficient token generation

### Request Flow

```
Client Application
    ↓ (HTTP/gRPC Request)
Load Balancer
    ↓
Inference Server (REST API)
    ↓
Request Queue & Batch Manager
    ↓
GPU Cluster (Tensor Parallelism)
    ↓
Model Execution (Forward Pass)
    ↓
Token Generation (Prefill + Decode)
    ↓
Response (JSON/Stream)
    ↓
Client Application
```

### Role of Inference Servers

They serve as the backend software, such as **NVIDIA Triton Inference Server** or **vLLM**, which connect user applications to the LLMs, managing:
- HTTP/gRPC requests
- Model loading
- Hardware acceleration
- Resource management
- Concurrent request handling

### Optimization Challenges

Because LLMs are massive, servers must handle significant computation costs. They use strategies like:
- **Tensor Parallelism**: Distributing models across multiple GPUs
- **Optimized Kernels**: Using highly optimized CUDA kernels for matrix operations
- **Memory Management**: Efficiently managing GPU VRAM

**Important Note:** In production, the first bottleneck usually isn't the transformer math—**it's the serving loop**.

---

## Agents and LLMs

**Agents** are autonomous systems that use LLMs as their reasoning engine to accomplish tasks. They can:
- Break down complex tasks into steps
- Use tools and APIs
- Maintain memory and context
- Make decisions and plan actions
- Interact with external systems

### Agent Architecture with LLM Inference

```
User Request
    ↓
Agent Controller
    ↓
LLM Inference Server (Reasoning)
    ↓
Tool Execution (APIs, DBs, RAG)
    ↓
Result Aggregation
    ↓
Response to User
```

### How Agents Use Inference

1. **Planning**: Agent uses LLM inference to decompose tasks
2. **Tool Selection**: Inference determines which tools to use
3. **Execution**: Agent calls external APIs or systems
4. **Reflection**: LLM analyzes results and plans next steps
5. **Iteration**: Process repeats until task completion

---

## Retrieval-Augmented Generation (RAG)

**RAG combines LLM inference with external knowledge retrieval** to enhance accuracy and reduce hallucinations.

### RAG Architecture

```
User Query
    ↓
Query Embedding (Encoder Model)
    ↓
Vector Database Search
    ↓
Retrieved Documents (Top-K)
    ↓
Context + Query → LLM Inference
    ↓
Grounded Response
```

### How RAG Works with Inference

1. **Query Processing**: User query is embedded into a vector
2. **Similarity Search**: Vector database finds relevant documents
3. **Context Injection**: Retrieved documents are added to the prompt
4. **Inference**: LLM generates response grounded in retrieved context
5. **Response**: Output is factually grounded and citation-ready

### Benefits of RAG

- Reduces hallucinations
- Provides up-to-date information
- Enables domain-specific knowledge
- Traceable and verifiable outputs
- No model retraining required

---

## Vector Databases

**Vector databases** store and retrieve high-dimensional embeddings efficiently, enabling semantic search for RAG systems.

### Popular Vector Databases

| Database | Key Features | Best For |
|----------|-------------|----------|
| **Pinecone** | Fully managed, high performance | Production RAG systems |
| **Weaviate** | Open-source, hybrid search | Scalable semantic search |
| **Chroma** | Lightweight, Python-native | Development and prototyping |
| **Milvus** | Distributed, highly scalable | Enterprise applications |
| **Qdrant** | Rust-based, fast filtering | High-performance retrieval |
| **FAISS** | Meta's library, in-memory | Research and experimentation |

### Vector Database Operations

1. **Embedding Storage**: Store document embeddings with metadata
2. **Similarity Search**: Find nearest neighbors using cosine/dot product
3. **Filtering**: Apply metadata filters to narrow search
4. **Hybrid Search**: Combine semantic and keyword search
5. **Indexing**: Use approximate nearest neighbor (ANN) algorithms

### Integration with Inference

Vector databases integrate with LLM inference servers to provide:
- Fast semantic retrieval (< 100ms)
- Scalable storage (millions to billions of vectors)
- Real-time updates
- Multi-modal search (text, images, audio)

---

## Challenges in LLM Inference

### 1. High Latency

LLMs process user prompts sequentially, predicting one token at a time. This step-by-step approach can result in delays, especially for complex queries or lengthy responses. **Latency is particularly problematic for real-time applications**, such as chatbots and virtual assistants, where users expect instantaneous feedback.

### 2. Computational Intensity

LLMs like GPT-4 and PaLM 2 boast billions of parameters, making inference computationally expensive. Every request requires significant processing power, leading to **high operational costs**, especially at scale. For businesses deploying LLMs in customer-facing applications, these costs can quickly become prohibitive.

### 3. Memory Constraints

Inference requires storing and accessing vast amounts of model parameters and intermediate states. Devices with limited memory—like edge devices—often struggle to handle large models, resulting in **bottlenecks or failure to process tasks efficiently**.

### 4. Token Limits

Many LLMs have limitations on the maximum number of tokens they can process in a single input. Long prompts may exceed these limits, requiring techniques like **truncation or windowing**, which can affect the model's understanding of the context and potentially degrade performance.

**Example:** In a translation tool, a long input text might need to be truncated, potentially losing crucial information and leading to less accurate translations.

### 5. Accuracy and Hallucinations

While LLMs are capable of generating sophisticated and contextually relevant outputs, they can also produce **hallucinations**—responses that are factually incorrect or nonsensical. This is a critical issue in domains like healthcare, law, or finance, where accuracy is paramount.

### 6. Scalability

Handling thousands or millions of concurrent inference requests while maintaining performance is a significant challenge. Applications that rely on LLMs must efficiently distribute workloads to **avoid bottlenecks and degraded user experiences**.

### 7. Multi-Cloud Deployment

Deploying AI models across multi-cloud environments presents a range of challenges, from ensuring consistent performance to managing complex infrastructure. Factors like **model size, high user volume, and latency** can all limit performance.

---

## Inference Optimization Techniques

**What is inference optimization?**

Inference optimization is a set of techniques to make LLM inference faster, cheaper, and more efficient. It's about reducing latency, improving throughput, and lowering hardware costs without hurting model quality.

### Common Optimization Strategies

- **Continuous batching**: Dynamically grouping requests for better GPU utilization
- **KV cache management**: Reusing or offloading attention caches to handle long prompts efficiently
- **Speculative decoding**: Using a smaller draft model to speed up token generation
- **Quantization**: Running models in lower precision (e.g., INT8, FP8) to save memory and compute
- **Prefix caching**: Caching common prompt segments to reduce redundant computation
- **Multi-GPU distribution/Parallelism**: Splitting LLMs across multiple GPUs for larger context windows

---

## Model Optimization

Optimizing the structure and behavior of LLMs can significantly improve inference efficiency without sacrificing performance.

### Key Techniques

#### Pruning
**Structured pruning** removes entire channels/heads, enabling speedups. By removing less significant model parameters, pruning reduces the size of the model, making it faster and more efficient.

- Removes redundant or less important weights
- Reduces model size by 30-50%
- Maintains accuracy with careful pruning strategies

#### Quantization
Lowering the numerical precision of model parameters (e.g., using 8-bit integers instead of 32-bit floating-point numbers) **reduces computational overhead**.

**Reduce precision to speed up compute and cut memory footprint.**

**Methods:**
- **Post-training dynamic quantization** (fastest to try)
- **Post-training static quantization** (requires calibration)
- **Quantization-aware training** (best accuracy retention)

**LLM-Specific Methods:**
- **AWQ** (Activation-aware Weight Quantization)
- **GPTQ** (Gradient-based Post-Training Quantization)
- **SmoothQuant**: Balances activation and weight quantization
- **LLM.int8()**: Mixed-precision 8-bit inference

**Example:** ONNX Runtime static quantization

#### Knowledge Distillation
Training a smaller model (a "student") to mimic the behavior of a larger, more complex model (a "teacher") enables compact models suitable for inference.

**Distillation** involves using a larger LLM to train a smaller one. The end result of this process is a **smaller model with similar inference capabilities** to the larger one.

---

## Inference Techniques

Innovative inference methods improve throughput and efficiency.

### KV Caching

**KV Cache (Key-Value Caching)** is all about speeding up inference. KV Cache only shows up at inference time, when the weights are locked in.

Transformer models compute self-attention across all previous tokens at each step. **KV caching stores these computations**, so the model doesn't have to recompute them every time a new token is generated.

**Key-value (KV) caching is a popular transformer-specific optimization technique** that makes LLM inference more computationally efficient. It allows for the fact that each new token is reliant on the key and tensor values of those that preceded it.

By **caching the key and tensor values in GPU memory**, KV caching eliminates the need to recompute many of the previous tensors as the model generates each new token.

**This technique stores intermediate computation results during token generation**, reducing redundancy and speeding up subsequent predictions.

**Benefits:**
- Reduces redundant computation
- Speeds up sequential token generation
- Essential for long-form generation
- Trades memory for speed

### Batching

**Grouping multiple inference requests for simultaneous processing** optimizes hardware utilization and reduces per-request latency.

**Request batching is an easy way to improve throughput**, making LLM applications faster and more responsive. When user requests are loaded in batches rather than one at a time, the model parameters don't need to be loaded as often.

#### Continuous (In-Flight) Batching

But collecting the maximum number of inputs before processing them can increase latency. **Continuous, or in-flight batching** can help compensate for this by evicting finished sequences from the batch, allowing a new request to replace it.

**In-flight batching significantly improves GPU utilization**, reducing the amount of time it takes the LLM application to provide a complete response to the user.

**Trade-off:** Larger batches improve throughput but can increase tail latency.

### Speculative Decoding

A smaller, faster model generates preliminary predictions, which the main LLM verifies, accelerating the overall process.

**Speculative inference** accelerates LLM inference through the use of a smaller, less resource-intensive draft model to generate speculative tokens. If the speculative tokens match those generated by the verification model, they're accepted. If not, they're discarded and the process begins again.

**How it works:**
1. Draft model generates multiple candidate tokens
2. Main model verifies all candidates in parallel
3. Accepted tokens are kept, rejected tokens are discarded
4. Process repeats until completion

**Benefits:**
- 2-3x speedup for large models
- No quality degradation
- Works best with related draft/target models

---

## Attention Mechanisms

You've heard about **"Attention is all you need"** already. **Attention is the most time-hungry part of the entire decoding pipeline. It scales quadratically with the number of tokens.**

The attention mechanism in transformers computes relationships between all tokens in a sequence, resulting in O(n²) complexity where n is the sequence length.

### Attention Optimization

**Attention mechanisms to reduce the computational cost associated with long prompts:**

#### Sparse Attention
**Focusing attention on a subset of the input tokens instead of the entire sequence.**

- Only computes attention for selected token pairs
- Reduces complexity from O(n²) to O(n√n) or O(n log n)
- Examples: Longformer, BigBird

#### Linearized Attention
**Approximating the attention mechanism with linear complexity.**

- Uses kernel tricks to avoid explicit attention matrix computation
- Achieves O(n) complexity
- Examples: Linear Transformer, Performer

#### Flash Attention
**Optimizing attention computation for faster execution on GPUs.**

- IO-aware algorithm that minimizes memory reads/writes
- Fuses operations to reduce kernel launches
- 2-4x faster than standard attention
- Enables longer context windows
- Flash Attention 2 brings additional 2x speedup

**Key Innovation:** Restructures attention computation to work with GPU memory hierarchy efficiently.

---

## Inference Performance Metrics

There are several ways to measure and evaluate LLM inference. As generative large language models become more important in enterprise applications, **establishing reliable performance metrics is vital** to improving their performance and better understanding their capabilities and limitations.

### Latency

**Latency measures the total length of time it takes the LLM to generate a response to a user's prompt.** The faster the model, the lower the latency. This LLM inference metric is especially important for **real-time applications** such as customer service chatbots, language translation, and retail or content recommender systems.

Latency is measured in two parts:

#### Time to First Token (TTFT)
TTFT is **the amount of time a user needs to wait before receiving a response to their input**. This is critical for user experience in interactive applications.

- Measures prefill phase performance
- Typically 50-500ms for optimized systems
- Affected by prompt length and batch size

#### Time Per Output Token (TPOT)
TPOT measures **the time needed to generate an output token for every user currently querying the system**.

- Measures decode phase efficiency
- Typically 10-50ms per token
- Determines streaming speed

**Taken together**, these two metrics account for the total time needed to generate a complete response.

### Throughput

**Throughput refers to the number of requests that can be processed or output generated within a certain period of time.** This can be measured in two ways:

#### Requests Per Second
A metric useful for evaluating concurrency and system capacity.

#### Tokens Per Second
This metric tracks **how many tokens per second an inference server can generate across all users and requests**. It is the more popular method for measuring throughput because it isn't dependent on the length of the model input or output.

**Target Performance:**
- Small models (7B): 100-500 tokens/sec per GPU
- Medium models (13B-30B): 50-200 tokens/sec per GPU
- Large models (70B+): 20-100 tokens/sec per GPU

---

## Model Parallelization

**Distributing an LLM across large clusters of GPUs enables organizations to run larger, more efficient models** that can handle increasingly larger batches of inputs.

Parallelization works by **partitioning the model, spreading its compute and memory requirements across multiple GPUs or instances**.

### Types of Parallelism

#### Tensor Parallelism
- Splits individual layers across multiple GPUs
- Each GPU computes a portion of matrix multiplications
- Requires high-bandwidth GPU interconnect (NVLink)
- Best for single-node multi-GPU setups

#### Pipeline Parallelism
- Splits model layers across GPUs
- Each GPU handles different layers
- Enables model scaling across nodes
- Requires careful batch management to avoid bubbles

#### Data Parallelism
- Replicates model across GPUs
- Each GPU processes different batch samples
- Simplest to implement
- Only helps with throughput, not memory

### Multi-GPU Distribution

**Splitting LLMs across multiple GPUs for larger context windows** and improved throughput.

**Benefits:**
- Handle models larger than single GPU memory
- Process longer context windows
- Increase throughput with larger batches
- Enable faster inference for large models

---

## Serving-Side Optimizations

### Batching and Dynamic Batching

**Batching increases GPU utilization** by combining multiple requests.

**Trade-off:** Larger batches improve throughput but can increase tail latency.

**Strategies:**
- **Static batching**: Fixed batch size, simple implementation
- **Dynamic batching**: Variable batch sizes, better resource utilization
- **Continuous batching**: In-flight request management, optimal for streaming

---

## Inference Serving Frameworks

Following are some of the **inference servers that are for serving LLMs specifically**.

### vLLM

**Repository:** https://github.com/vllm-project/vllm

Developed by researchers at UC Berkeley, **vLLM focuses heavily on maximizing throughput**.

**Key Features:**
- PagedAttention for efficient KV cache management
- Continuous batching for high throughput
- Optimized CUDA kernels
- Support for popular models (Llama, Mistral, GPT, etc.)
- Easy integration with OpenAI-compatible API

**Best For:**
- High-throughput production deployments
- Serving multiple concurrent users
- Cost-effective inference at scale

### Text Generation Inference (TGI)

**Repository:** https://github.com/huggingface/text-generation-inference

Developed and maintained by Hugging Face, **TGI is designed as a production-ready solution for deploying Transformer models**, including large language models.

**Key Features:**
- Built-in support for Hugging Face models
- Tensor parallelism for large models
- Flash Attention integration
- Token streaming support
- Safetensors weight loading
- Watermarking and safety features

**Best For:**
- Hugging Face ecosystem users
- Enterprise deployments
- Models requiring safety features

### OpenLLM

**Repository:** https://github.com/bentoml/OpenLLM

**Key Features:**
- Model-agnostic framework
- Built on BentoML for production deployment
- Support for multiple backends
- RESTful and gRPC APIs
- Easy containerization

**Best For:**
- Flexible deployment scenarios
- Multi-model serving
- Custom model architectures

### Other Notable Frameworks

| Framework | Key Strength | Use Case |
|-----------|--------------|----------|
| **NVIDIA Triton** | Multi-framework support, GPU optimization | Enterprise multi-model serving |
| **TensorRT-LLM** | Highest performance on NVIDIA GPUs | Low-latency production inference |
| **Ray Serve** | Distributed serving, autoscaling | Large-scale deployments |
| **Ollama** | Easy local deployment | Development and testing |
| **LocalAI** | OpenAI-compatible API, privacy-focused | On-premise deployments |

---

## Open-Source Inference Engines for Self-Hosted Deployment

Self-hosting large language models provides complete control over model weights, data sovereignty, and infrastructure configuration. However, it requires deliberate selection and application of appropriate optimization techniques to achieve competitive performance. When deploying open-source or custom models, the choice of inference engine significantly determines achievable throughput, latency, and resource utilization. Applying the right optimization techniques enables practitioners to adapt inference systems to specific use cases—from high-throughput batch processing and structured generation pipelines to low-latency interactive applications and resource-constrained edge deployments.

This section provides a comprehensive survey of the principal open-source inference engines, examining their design principles, core optimizations, hardware support, and suitability for different deployment contexts.

---

### vLLM: High-Throughput Memory-Efficient Engine

**Repository:** https://github.com/vllm-project/vllm
**Website:** https://vllm.ai/

vLLM is a high-throughput and memory-efficient inference and serving engine for large language models, originally developed at UC Berkeley's Sky Computing Lab and now maintained by a community of over 2,000 contributors. It has become one of the most widely adopted LLM serving frameworks in production environments.

**PagedAttention**

The foundational contribution of vLLM is PagedAttention, a memory management algorithm that treats the KV cache analogously to how operating systems manage virtual memory through paging. Rather than allocating a large contiguous block of GPU memory for each sequence's KV cache, PagedAttention partitions the cache into smaller fixed-size blocks (pages) that may be allocated non-contiguously. This approach substantially reduces memory fragmentation, enabling significantly higher concurrency within the same GPU memory budget.

**Key Capabilities:**

- State-of-the-art serving throughput through PagedAttention and continuous batching
- Quantization support: FP8, MXFP8/MXFP4, NVFP4, INT8, INT4, GPTQ, AWQ, GGUF, and additional formats
- Optimized attention kernels including FlashAttention, FlashInfer, and Triton-based implementations
- Speculative decoding (n-gram, suffix, EAGLE, DFlash variants) for accelerated token generation
- Disaggregated prefill and decode for pipeline parallelism optimization
- Tensor, pipeline, data, expert, and context parallelism for distributed inference
- OpenAI-compatible API server with Anthropic Messages API and gRPC support
- Multi-LoRA batching for serving multiple fine-tuned model variants simultaneously
- Support for over 200 Hugging Face model architectures including decoder-only LLMs, mixture-of-experts models, multimodal models, embedding models, and reward models

**Hardware Support:** NVIDIA CUDA GPUs, AMD ROCm GPUs, Intel XPU, x86 and ARM CPUs, Google TPUs, Huawei Ascend NPUs, Apple Silicon, and additional targets through plugin providers.

---

### llama.cpp: C/C++ Implementation for Edge and Consumer Hardware

**Repository:** https://github.com/ggml-org/llama.cpp

llama.cpp is a self-contained LLM inference implementation written entirely in C/C++, with the primary objective of enabling high-performance inference with minimal setup across a wide range of hardware—from consumer-grade laptops and Apple Silicon to cloud servers and embedded systems. It requires no external deep learning framework dependencies, making it exceptionally portable across platforms.

**Design Philosophy**

The project adheres to a philosophy of minimal dependency and maximum hardware accessibility:

- Plain C/C++ implementation without external framework dependencies
- Apple Silicon as a first-class deployment target, optimized via ARM NEON, Accelerate, and Metal frameworks
- AVX, AVX2, AVX512, and AMX support for x86 architectures
- Integer quantization at 1.5-bit through 8-bit precision levels for reduced memory footprint and accelerated inference
- Custom CUDA kernels for NVIDIA GPU acceleration, with AMD GPU support via HIP and Moore Threads GPU support via MUSA
- Vulkan and SYCL backend support for additional hardware compatibility
- CPU and GPU hybrid inference, enabling partial acceleration for models that exceed available VRAM

**GGUF Model Format**

Models in llama.cpp are stored in the GGUF (GGML Universal File) format, a binary specification for quantized model weights and metadata. GGUF supports a wide range of quantization levels and enables efficient memory-mapped loading. Models in other formats, such as Hugging Face safetensors, can be converted to GGUF using the provided Python conversion tools. The Hugging Face platform hosts a large collection of GGUF models and provides online conversion tooling.

**Supported Backends**

| Backend | Target Hardware |
|---------|----------------|
| Metal | Apple Silicon |
| CUDA | NVIDIA GPU |
| HIP | AMD GPU |
| SYCL | Intel and NVIDIA GPU |
| Vulkan | General GPU |
| OpenCL | Adreno GPU |
| CANN | Huawei Ascend NPU |
| BLAS/BLIS | General CPU |
| Hexagon | Qualcomm Snapdragon |
| WebGPU | All platforms (in development) |

**Server and Web Interface**

llama.cpp includes `llama-server`, a lightweight OpenAI API-compatible HTTP server (default port 8080) supporting multiple concurrent users, parallel decoding, speculative decoding, embedding serving, and reranking. The server provides a built-in web interface for interactive chat and model management. Additional utilities include `llama-cli` for interactive inference, `llama-bench` for performance benchmarking, and `llama-perplexity` for quality evaluation.

#### GGML: The Underlying Tensor Library

**Repository:** https://github.com/ggml-org/ggml

GGML is the tensor library for machine learning that serves as the computational foundation for llama.cpp and related projects including whisper.cpp. The library provides:

- Low-level, cross-platform implementation with no external dependencies
- Integer quantization support for memory and compute efficiency
- Broad hardware support through multiple computational backends
- Automatic differentiation for gradient computation
- ADAM and L-BFGS optimizers
- Zero memory allocations at runtime for deterministic performance characteristics

GGML defines the GGUF file format specification, which has become a widely adopted standard for distributing quantized LLMs. The format is supported by numerous downstream inference systems and model hosting platforms.

---

### SGLang: Structured Generation and High-Performance LLM Serving

**Repository:** https://github.com/sgl-project/sglang
**Website:** https://www.sglang.io/

SGLang is a high-performance serving framework for large language models and multimodal models, maintained by the LMSYS organization. It is designed for production-grade inference at scales ranging from a single GPU to large distributed clusters, with particular emphasis on structured generation and advanced KV cache management.

**RadixAttention**

SGLang introduces RadixAttention, a prefix caching mechanism that organizes KV cache entries in a radix tree data structure. This approach enables efficient reuse of shared prefixes across different requests, substantially reducing redundant computation for workloads sharing common prompt prefixes such as system prompts or few-shot examples.

**Key Capabilities:**

- RadixAttention for prefix caching and efficient KV cache reuse
- Zero-overhead CPU scheduler minimizing scheduling latency
- Prefill-decode disaggregation for large-scale deployment pipelines
- Speculative decoding support
- Continuous batching and paged attention
- Tensor, pipeline, expert, and data parallelism
- Grammar-constrained structured output generation via xgrammar
- Chunked prefill for long-context efficiency
- Quantization: FP4, FP8, INT4, AWQ, GPTQ
- Multi-LoRA batching
- OpenAI-compatible API

**Model and Hardware Support**

SGLang supports language models (Llama, Qwen, DeepSeek, GLM, Gemma, Mistral, and others), multimodal models, and diffusion models. Hardware targets include NVIDIA GPUs (GB200, B300, H100, A100), AMD GPUs (MI300, MI355), Intel Xeon CPUs, Google TPUs, and Huawei Ascend NPUs.

**Deployment at Scale**

SGLang has been adopted at large scale across industry, generating trillions of tokens per day in production environments. Reported deployments span over 400,000 GPUs worldwide across organizations including xAI, NVIDIA, AMD, Intel, LinkedIn, Oracle Cloud, Google Cloud, and Microsoft Azure. SGLang also serves as the rollout backend for training frontier models through integrations with reinforcement learning frameworks including verl and AReaL.

---

### NVIDIA Triton Inference Server

**Repository:** https://github.com/triton-inference-server/server

Triton Inference Server, developed by NVIDIA, is a production-grade open-source serving solution supporting diverse AI models across multiple deep learning and machine learning frameworks. It is designed for deployment across cloud, data center, edge, and embedded environments.

**Key Capabilities:**

- Multi-framework backend support: TensorRT, PyTorch, ONNX Runtime, OpenVINO, Python, RAPIDS FIL, and others
- Concurrent model execution, allowing multiple models to serve requests simultaneously
- Dynamic batching, grouping requests arriving within a configurable window for efficient GPU utilization
- Sequence batching and implicit state management for stateful models
- Model ensemble pipelines and Business Logic Scripting (BLS) for custom pre/post-processing
- HTTP/REST and gRPC inference protocols based on the KServe community standard
- GPU utilization metrics, server throughput, and latency monitoring
- C API and Java API for in-process edge deployment scenarios
- Support for NVIDIA GPUs, x86 and ARM CPUs, and AWS Inferentia

Triton is particularly suited for enterprise environments managing heterogeneous model portfolios across frameworks, multi-stage inference pipelines combining multiple models, and scenarios requiring robust model versioning and concurrent serving.

---

### Text Generation Inference: Hugging Face Ecosystem

**Repository:** https://github.com/huggingface/text-generation-inference

Text Generation Inference (TGI), developed and maintained by Hugging Face, is a high-performance toolkit for deploying transformer-based language models. TGI provides a production-ready server with continuous batching, token streaming, and hardware-optimized kernels.

TGI was developed with a focus on transformer model architectures as defined by the Hugging Face transformers library. In the current ecosystem, Hugging Face acknowledges that downstream inference engines—specifically vLLM, SGLang, llama.cpp, and MLX—have adopted and extended many of TGI's foundational approaches, and these are recommended for production deployments requiring maximum performance and ecosystem flexibility. TGI remains actively maintained and widely deployed, particularly within the Hugging Face model ecosystem, and continues to offer production-grade features including quantization, tensor parallelism, Flash Attention, and safety watermarking.

---

### ONNX Runtime

**Repository:** https://github.com/microsoft/onnxruntime  
**Website:** https://onnxruntime.ai/

ONNX Runtime, developed by Microsoft, is a cross-platform, high-performance inference and training accelerator for machine learning models. It supports models from deep learning frameworks including PyTorch and TensorFlow/Keras, as well as classical machine learning libraries. ONNX Runtime applies graph optimizations and hardware accelerator integrations to maximize inference performance across diverse deployment targets.

**Key Characteristics:**

- Cross-platform support: Linux, Windows, macOS, iOS, Android, and web browsers
- Multi-language APIs: Python, C#, JavaScript, Java, C++, Rust, and others
- Hardware execution providers: CUDA, DirectML, OpenVINO, TensorRT, CoreML, and more
- Graph-level optimizations: operator fusion, constant folding, and redundant node elimination
- Quantization support for reduced precision inference
- Generative AI and LLM support via the onnxruntime-genai extension
- Production deployment in Microsoft products including Windows, Office, Azure Cognitive Services, and Bing

ONNX Runtime is particularly well-suited for cross-framework interoperability requirements, edge and mobile deployments requiring a compact runtime, and production workloads within the Microsoft Azure ecosystem.

---

### DeepSpeed Model Implementations for Inference (MII)

**Repository:** https://github.com/deepspeedai/DeepSpeed-MII

DeepSpeed-MII is an open-source Python library developed by the DeepSpeed team at Microsoft, designed to provide high-throughput, low-latency LLM inference. Built on DeepSpeed-Inference, it applies automatic optimization strategies based on model architecture, model size, batch size, and available hardware resources.

**Key Technologies:**

- **Blocked KV Caching**: Manages KV cache in fixed-size blocks to reduce fragmentation and improve memory efficiency
- **Continuous Batching**: Processes requests at the iteration level for improved GPU utilization
- **Dynamic SplitFuse**: A scheduling strategy that fuses short prompts and splits long prompts, balancing compute and memory pressure within heterogeneous batches
- **High-Performance CUDA Kernels**: Custom kernels for matrix operations and attention computation
- **Tensor Parallelism**: Automatic multi-GPU distribution for large models
- **Load-Balanced Model Replicas**: Distributes inference load across multiple model instances

MII supports both non-persistent pipelines for exploratory use and persistent deployments for production applications, with RESTful API and gRPC endpoints.

---

### LMDeploy: Compressing, Deploying, and Serving LLMs

**Repository:** https://github.com/InternLM/lmdeploy

LMDeploy is a comprehensive toolkit for compressing, deploying, and serving large language models, developed by the MMRazor and MMDeploy teams at Shanghai AI Laboratory. It provides an end-to-end pipeline from model quantization through deployment and serving.

**Core Capabilities:**

- **Efficient Inference**: Delivers up to 1.8x higher request throughput than comparable systems through persistent batching, blocked KV cache, dynamic split-and-fuse scheduling, tensor parallelism, and high-performance CUDA kernels
- **Effective Quantization**: Supports weight-only and KV quantization; 4-bit quantized inference reported at 2.4x higher performance than FP16 equivalents
- **Request Distribution**: Facilitates multi-model service deployment across multiple compute nodes
- **Compatibility**: Simultaneous support for KV cache quantization, AWQ, and automatic prefix caching

LMDeploy provides two inference backends:

- **TurboMind**: A high-performance C++ inference engine designed for maximum optimization in production workloads, with efficient support for grouped query attention (GQA) and multi-query attention (MQA)
- **PyTorch Engine**: A Python-based engine that reduces development barriers and supports rapid model integration

**Supported Models:** Llama (all variants through Llama 3.2), Qwen (through Qwen3-MoE), InternLM, Mistral, GLM, Baichuan, Code Llama, and numerous vision-language models.

---

### Ollama: Simplified Local Deployment

Ollama is a framework that substantially simplifies the process of running quantized LLMs on local hardware. It builds on llama.cpp as its underlying inference engine, providing a unified command-line interface and REST API for downloading, managing, and executing models in GGUF format. Ollama handles hardware detection, GPU configuration, and model management automatically.

**Key Characteristics:**

- Single-command model download and execution
- Automatic hardware detection and configuration (CPU, GPU, Apple Silicon)
- OpenAI-compatible REST API
- Integrated model library with numerous quantized model variants
- Cross-platform support: Linux, macOS, and Windows

Ollama is best suited for development, prototyping, personal research, and local experimentation rather than high-concurrency production deployments.

---

### Sampling Strategies and Temperature

At each decode step, the model produces a probability distribution over its entire vocabulary via a softmax function applied to raw output scores (logits). A temperature parameter is applied to the logits before softmax normalization to control the sharpness of this distribution:

- **Temperature below 1.0**: Concentrates probability mass on fewer tokens, producing more deterministic and focused outputs
- **Temperature above 1.0**: Distributes probability more broadly across tokens, producing more varied and exploratory outputs
- **Temperature of 1.0**: Preserves the model's default distribution without scaling

Following temperature scaling, a sampling strategy determines how the next token is selected:

- **Greedy decoding**: Always selects the highest-probability token. Deterministic but susceptible to repetitive output patterns and sub-optimal long-range predictions
- **Top-k sampling**: Restricts candidate tokens to the k highest-probability entries, then samples from this set, preventing selection of very low-probability tokens
- **Top-p (nucleus) sampling**: Dynamically selects the smallest set of tokens whose cumulative probability reaches or exceeds a threshold p, then samples from this set
- **Top-k combined with Top-p**: Frequently applied in production systems; Top-k first removes extreme low-probability outliers, and Top-p subsequently refines the candidate pool by cumulative probability mass

The choice of decoding strategy and temperature values directly affects output quality, diversity, and determinism, and is a configurable parameter in all major inference engines.

---

### Context Window

The context window defines the maximum number of tokens an LLM can process within a single inference pass, encompassing both the input prompt tokens and the generated output tokens. A longer context window increases the model's ability to maintain coherent conversation history, process long documents, or incorporate extensive retrieved context in retrieval-augmented generation systems.

However, the quadratic scaling of the standard attention mechanism with sequence length means that larger context windows impose significantly higher memory and computational requirements. Extended context support is addressed through several techniques in modern inference engines:

- **Chunked prefill**: Processes long prompts in segments to manage peak memory pressure
- **PagedAttention** and **RadixAttention**: Manage KV cache memory efficiently for long-context sequences
- **Flash Attention**: Reduces memory requirements through IO-aware tiling of attention computation
- **RoPE (Rotary Position Embedding) scaling**: Extends the effective positional encoding range beyond the model's original training context length

---

### Optimization Strategies for Self-Hosted Models

When self-hosting open-source or custom models, selecting and applying the appropriate optimization techniques is critical to meeting specific performance objectives. The following table summarizes the principal techniques and their applicability across inference engines:

| Optimization Technique | Primary Benefit | Applicable Engines |
|------------------------|-----------------|-------------------|
| Quantization (INT4/INT8/FP8) | Reduced memory, faster compute | vLLM, llama.cpp, SGLang, LMDeploy, TGI |
| PagedAttention | KV cache memory efficiency | vLLM |
| RadixAttention | Prefix caching via radix tree | SGLang |
| Continuous Batching | Higher GPU utilization | vLLM, SGLang, TGI, LMDeploy, DeepSpeed-MII |
| Speculative Decoding | Faster token generation | vLLM, SGLang, llama.cpp |
| Flash Attention | Memory-efficient attention computation | vLLM, SGLang, TGI |
| Tensor Parallelism | Multi-GPU large model support | vLLM, SGLang, LMDeploy, TGI |
| GGUF Quantization | Consumer and edge hardware deployment | llama.cpp, Ollama |
| Dynamic SplitFuse | Mixed-length batch scheduling | DeepSpeed-MII |
| AWQ/GPTQ | Accurate post-training weight quantization | vLLM, SGLang, LMDeploy |
| Prefix Caching | Shared prompt reuse across requests | vLLM, SGLang, LMDeploy |

**Selecting Optimizations by Use Case:**

- For interactive, low-latency applications such as chatbots and assistants: minimize Time to First Token (TTFT) through prefix caching, chunked prefill, and PagedAttention or RadixAttention
- For high-throughput batch workloads: maximize tokens per second via continuous batching, larger effective batch sizes, and quantization
- For consumer or edge hardware: apply GGUF quantization at 4-bit precision via llama.cpp and leverage CPU and GPU hybrid inference
- For structured generation requirements such as JSON, code, or constrained output schemas: use SGLang with grammar-constrained decoding
- For multi-framework or multi-model serving environments: deploy NVIDIA Triton Inference Server
- For cross-platform or mobile inference: use ONNX Runtime with hardware-specific execution providers

---

### Comparative Overview of Open-Source Inference Engines

| Framework | Implementation | Core Optimization | Primary Use Case | Hardware |
|-----------|---------------|-------------------|-----------------|----------|
| vLLM | Python/CUDA | PagedAttention, continuous batching | High-throughput production serving | NVIDIA, AMD, TPU, CPU |
| llama.cpp | C/C++ | GGUF quantization, CPU+GPU hybrid | Local, edge, consumer hardware | All platforms |
| SGLang | Python/CUDA | RadixAttention, structured generation | Structured generation, large-scale | NVIDIA, AMD, TPU |
| Triton Inference Server | C++/Python | Multi-framework, dynamic batching | Enterprise multi-model serving | NVIDIA, CPU |
| TGI | Rust/Python | Flash Attention, token streaming | Hugging Face ecosystem | NVIDIA |
| ONNX Runtime | C++ | Graph optimization, cross-platform | Cross-platform, edge, mobile | All platforms |
| DeepSpeed-MII | Python | Dynamic SplitFuse, blocked KV cache | DeepSpeed ecosystem | NVIDIA |
| LMDeploy | Python/C++/CUDA | TurboMind engine, AWQ | InternLM/Qwen families | NVIDIA |
| OpenLLM | Python | BentoML integration, vLLM backend | Cloud-managed self-hosting | NVIDIA |
| Ollama | Go | llama.cpp backend, ease of use | Development, local experimentation | All platforms |

---

## Choosing the Right Inference for Production

### Factors to Consider

#### 1. Latency Requirements
- **Real-time chatbots**: < 100ms TTFT, < 20ms TPOT
- **Document generation**: < 500ms TTFT acceptable
- **Batch processing**: Latency less critical

#### 2. Throughput Needs
- **High traffic**: vLLM, TGI with continuous batching
- **Moderate traffic**: Standard serving frameworks
- **Low traffic**: Simplified deployment (Ollama, LocalAI)

#### 3. Model Size
- **< 7B parameters**: Single GPU sufficient
- **7B-30B**: Multi-GPU or quantization
- **> 30B**: Tensor parallelism required

#### 4. Cost Constraints
- **Cloud**: Use managed services (Vertex AI, SageMaker)
- **On-premise**: vLLM or TGI with careful optimization
- **Hybrid**: Load balancing across environments

#### 5. Security and Privacy
- **Sensitive data**: On-premise deployment
- **Public data**: Cloud-based inference acceptable
- **Compliance**: Ensure framework supports audit trails

### Decision Matrix

```
High Throughput + Low Latency → vLLM with Flash Attention
Enterprise + Hugging Face Models → TGI
Multi-Model Serving → NVIDIA Triton
Development/Testing → Ollama or LocalAI
Custom Requirements → OpenLLM
Maximum Performance → TensorRT-LLM
```

### Best Practices

1. **Start Simple**: Begin with basic deployment, optimize as needed
2. **Profile Early**: Measure latency and throughput from the start
3. **Monitor Continuously**: Track metrics in production
4. **Plan for Scale**: Design with growth in mind
5. **Test Thoroughly**: Validate under realistic load conditions
6. **Optimize Iteratively**: Apply optimizations based on bottlenecks

---

## Flask vs FastAPI: Choosing Your Server Framework

This project includes both **Flask** and **FastAPI** implementations of the inference server to demonstrate different approaches.

### Flask Server

**File:** `sources/inference_server.py` (Port 5000)

**Pros:**
- Simple and beginner-friendly
- Minimal boilerplate code
- Widely used and well-documented
- Easy to understand for learning
- Established ecosystem

**Cons:**
- Synchronous by default (blocks on I/O)
- Lower performance under high load
- Manual request validation
- No automatic API documentation
- Limited concurrency without additional setup

**Best For:**
- Learning and education
- Simple prototypes
- Low-traffic applications
- Teams familiar with Flask

### FastAPI Server

**File:** `sources/inference_server_fastapi.py` (Port 8000)

**Pros:**
- **Native async/await** support for better concurrency
- **2-3x faster** than Flask in benchmarks
- **Automatic API documentation** (Swagger UI at `/docs`)
- **Type validation** with Pydantic models
- **Modern Python 3.7+** typing support
- **Production-ready** - used by vLLM, TGI

**Cons:**
- Slightly steeper learning curve
- Requires understanding of async programming
- More dependencies (though still lightweight)

**Best For:**
- Production deployments
- High-concurrency applications
- API-first development
- Teams building scalable systems

### Performance Comparison

| Metric | Flask | FastAPI | Winner |
|--------|-------|---------|--------|
| **Requests/sec** | ~1,000 | ~2,500-3,000 | FastAPI |
| **Async Support** | Limited | Native | FastAPI |
| **Concurrent Requests** | Sequential | Parallel | FastAPI |
| **Type Validation** | Manual | Automatic | FastAPI |
| **API Docs** | Manual | Automatic | FastAPI |
| **Learning Curve** | Easy | Moderate | Flask |
| **Code Simplicity** | Very Simple | Simple | Flask |

### Recommendation

- **Use Flask** for learning, prototypes, or simple applications
- **Use FastAPI** for production, high-traffic systems, or when you need best performance

Both implementations in this project demonstrate the same concepts, so you can compare and choose based on your needs!

---

## Project Structure

```
📦 INFERENCE/
├── 📄 README.md                         # This document
├── 📄 .gitignore                        # Git ignore configuration
├── 📄 requirements.txt                  # Python dependencies
├── 📄 setup.sh                          # Virtual environment setup script
├── 📂 sources/
│   ├── 📄 inference_server.py           # Flask-based inference server (port 5000)
│   ├── 📄 inference_server_fastapi.py   # FastAPI-based inference server (port 8000)
│   ├── 📄 client_example.py             # Client examples for Flask server
│   ├── 📄 client_example_fastapi.py     # Client examples for FastAPI server
│   ├── 📄 rag_example.py                # RAG implementation example
│   └── 📄 vector_db_example.py          # Vector database integration
├── 📂 venv/                             # Virtual environment (not in Git)
└── 📂 models/                           # Model storage (not in Git)
```

---

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip package manager
- 8GB+ RAM (16GB+ recommended)
- GPU with CUDA support (optional but recommended for large models)

### Step 1: Clone or Navigate to the Project

```bash
cd LARGE-LANGUAGE-MODELS/INFERENCE
```

### Step 2: Create Virtual Environment

Run the provided setup script:

```bash
bash setup.sh
```

Or manually:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Verify Installation

```bash
# Activate virtual environment if not already activated
source venv/bin/activate

# Check installed packages
pip list
```

### Step 4: Start the Inference Server

**Option A: Flask Server (Beginner-Friendly)**

```bash
# Activate virtual environment
source venv/bin/activate

# Run the Flask inference server
python sources/inference_server.py
```

The server will start on `http://localhost:5000`

**Option B: FastAPI Server (Production-Ready, Recommended)**

```bash
# Activate virtual environment
source venv/bin/activate

# Run the FastAPI inference server
python sources/inference_server_fastapi.py
```

The server will start on `http://localhost:8000`
- **Interactive API Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)

**FastAPI Advantages:**
- **2-3x faster** than Flask with native async support
- **Automatic documentation** with interactive Swagger UI
- **Type validation** with Pydantic models
- **Better concurrency** for handling multiple requests
- **Production-ready** - used by vLLM, TGI, and other frameworks

### Step 5: Test with cURL

**For Flask Server (port 5000):**

#### Simple Inference Request

```bash
curl -X POST http://localhost:5000/api/v1/inference \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is artificial intelligence?",
    "max_tokens": 100,
    "temperature": 0.7
  }'
```

#### Health Check

```bash
curl http://localhost:5000/health
```

**For FastAPI Server (port 8000):**

#### Simple Inference Request

```bash
curl -X POST http://localhost:8000/api/v1/inference \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is artificial intelligence?",
    "max_tokens": 100,
    "temperature": 0.7
  }'
```

#### Health Check

```bash
curl http://localhost:8000/health
```

#### Interactive API Documentation

**Best way to test FastAPI:** Visit http://localhost:8000/docs in your browser for a fully interactive Swagger UI where you can test all endpoints with a visual interface!

### Step 6: Run Client Examples

**For Flask Server:**

```bash
# Activate virtual environment
source venv/bin/activate

# Run Flask client examples
python sources/client_example.py
```

**For FastAPI Server:**

```bash
# Activate virtual environment
source venv/bin/activate

# Run FastAPI client examples
python sources/client_example_fastapi.py
```

### Step 7: Test RAG Integration (Optional)

```bash
# Run RAG example
python sources/rag_example.py
```

### Step 8: Vector Database Example (Optional)

```bash
# Run vector database example
python sources/vector_db_example.py
```

---

## Example Use Case

### Scenario: Customer Support Chatbot

**Requirements:**
- Real-time response (< 200ms latency)
- Handle 1000 concurrent users
- Accurate, context-aware responses
- Grounded in company documentation

**Solution Architecture:**

```
Customer Query
    ↓
[Load Balancer]
    ↓
[Flask REST API]
    ↓
[Query Router]
    ├─→ [Vector Database] (Retrieve relevant docs)
    └─→ [vLLM Inference Server] (Generate response)
         ↓
[Response Aggregator]
    ↓
[Customer Interface]
```

**Implementation Steps:**

1. **Document Ingestion**
   - Convert company docs to embeddings
   - Store in vector database (Pinecone/Chroma)

2. **Query Processing**
   - Embed user query
   - Retrieve top-3 relevant documents

3. **Context Injection**
   - Combine query + retrieved docs
   - Format as prompt for LLM

4. **Inference**
   - Send to vLLM server
   - Use continuous batching for efficiency
   - Apply KV caching for multi-turn conversations

5. **Response Delivery**
   - Stream tokens to user
   - Include citations from retrieved docs
   - Log interaction for analytics

**Performance Results:**
- TTFT: 120ms
- TPOT: 15ms
- Throughput: 2500 tokens/sec
- Cost: $0.002 per query

---

## References

### Official Documentation

- **LLM Fundamentals** - Microsoft Agent Framework
  https://learn.microsoft.com/en-us/agent-framework/journey/llm-fundamentals

- **What is AI Inference?** - Google Cloud
  https://cloud.google.com/discover/what-is-ai-inference

- **Transformer Architecture** - "Attention is All You Need"
  https://arxiv.org/abs/1706.03762

- **vLLM Documentation**
  https://docs.vllm.ai/

- **Hugging Face TGI**
  https://huggingface.co/docs/text-generation-inference/

- **NVIDIA Triton Inference Server**
  https://github.com/triton-inference-server/server

### Research Papers

- **Flash Attention**
  https://arxiv.org/abs/2205.14135

- **Speculative Decoding**
  https://arxiv.org/abs/2211.17192

- **KV Cache Optimization**
  https://arxiv.org/abs/2309.17453

- **RAG (Retrieval-Augmented Generation)**
  https://arxiv.org/abs/2005.11401

### Vector Databases

- **Pinecone**
  https://www.pinecone.io/

- **Weaviate**
  https://weaviate.io/

- **Chroma**
  https://www.trychroma.com/

- **Milvus**
  https://milvus.io/

- **Qdrant**
  https://qdrant.tech/

- **FAISS**
  https://github.com/facebookresearch/faiss

### Optimization Techniques

- **Quantization: GPTQ**
  https://github.com/IST-DASLab/gptq

- **Quantization: AWQ**
  https://github.com/mit-han-lab/llm-awq

- **Model Compression Survey**
  https://arxiv.org/abs/2308.07633

### Production Deployment

- **LLM Inference in Production**
  https://www.databricks.com/blog/llm-inference-performance-engineering-best-practices

- **Scaling LLM Applications**
  https://www.anyscale.com/blog/a-comprehensive-guide-for-building-rag-based-llm-applications

- **Cost Optimization for LLM Inference**
  https://aws.amazon.com/blogs/machine-learning/optimize-llm-inference-costs/

### Tools and Frameworks

- **LangChain** (Agent Framework)
  https://www.langchain.com/

- **LlamaIndex** (RAG Framework)
  https://www.llamaindex.ai/

- **OpenAI API Documentation**
  https://platform.openai.com/docs/

- **Ray Serve** (Scalable Serving)
  https://docs.ray.io/en/latest/serve/

### Open-Source Inference Engines

- **vLLM**
  https://github.com/vllm-project/vllm

- **vLLM Website**
  https://vllm.ai/

- **llama.cpp**
  https://github.com/ggml-org/llama.cpp

- **ggml**
  https://github.com/ggml-org/ggml

- **SGLang**
  https://github.com/sgl-project/sglang

- **SGLang Website**
  https://www.sglang.io/

- **NVIDIA Triton Inference Server**
  https://github.com/triton-inference-server/server

- **ONNX Runtime**
  https://github.com/microsoft/onnxruntime

- **ONNX Runtime Website**
  https://onnxruntime.ai/

- **DeepSpeed-MII**
  https://github.com/deepspeedai/DeepSpeed-MII

- **LMDeploy**
  https://github.com/InternLM/lmdeploy

- **OpenLLM**
  https://github.com/bentoml/OpenLLM

- **What is LLM Inference? Challenges and Solutions** - Hugging Face Blog
  https://huggingface.co/blog/Kseniase/inference

---

## Summary

- **What LLM inference is** and how it differs from training
- **How inference works** through prefill and decode phases
- **Inference server architecture** and request flow
- **Agents and RAG** integration with LLM inference
- **Vector databases** for semantic search
- **Challenges** in production LLM deployment
- **Optimization techniques** including quantization, KV caching, and attention mechanisms
- **Performance metrics** for measuring inference quality
- **Inference frameworks** like vLLM, TGI, and Triton
- **Open-source inference engines** including llama.cpp, SGLang, ONNX Runtime, DeepSpeed-MII, and LMDeploy
- **Sampling strategies** and temperature control for output generation
- **Context window** management and extended context techniques
- **Optimization strategies** mapped to specific use cases for self-hosted deployments
- **Production deployment** strategies and best practices
- **Hands-on examples** with working code and API tests

With this knowledge and the provided examples, you're ready to deploy production ready LLM inference systems.

---

**Last Updated:** May 2, 2026

**License:** MIT
