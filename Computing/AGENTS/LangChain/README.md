# How to build AI Agents with LangChain?

This repository contains code for building AI agents using LangChain, a framework for developing
applications powered by large language models. The agent supports **local inference via Ollama**
(free, no API key required) as well as the OpenAI cloud API.

---

## Table of Contents

- [Overview](#overview)
- [What's Included](#whats-included)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
  - [Step 1: Set Up Virtual Environment (VS Code)](#step-1-set-up-virtual-environment-vs-code)
  - [Step 2: Install Dependencies](#step-2-install-dependencies)
  - [Step 3: Configure Environment](#step-3-configure-environment)
  - [Step 4: Run the Demo](#step-4-run-the-demo)
- [Local Deployment with Ollama](#local-deployment-with-ollama)
  - [Why Use Ollama?](#why-use-ollama)
  - [Install Ollama on Linux (Native)](#install-ollama-on-linux-native)
  - [Step 1: Start the Ollama Container (Docker)](#step-1-start-the-ollama-container-docker)
  - [Step 2: Pull a Model](#step-2-pull-a-model)
  - [Step 3: Configure the Agent](#step-3-configure-the-agent)
  - [Available Open-Source Models](#available-open-source-models)
  - [Using GGUF Models from Hugging Face](#using-gguf-models-from-hugging-face)
  - [Running Hugging Face Models with Testcontainers](#running-hugging-face-models-with-testcontainers)
- [Ollama Architecture: How It Works Under the Hood](#ollama-architecture-how-it-works-under-the-hood)
  - [The llama.cpp Inference Engine](#the-llamacpp-inference-engine)
  - [Go Wrapper and Cgo Integration](#go-wrapper-and-cgo-integration)
  - [Model Management and GGUF Format](#model-management-and-gguf-format)
- [Using llama.cpp Directly](#using-llamacpp-directly)
  - [Build from Source on Linux](#build-from-source-on-linux)
  - [Run with Docker](#run-with-docker)
  - [Run Inference with llama-cli](#run-inference-with-llama-cli)
  - [Launch an OpenAI-Compatible Server](#launch-an-openai-compatible-server)
- [OpenAI-Compatible API Interface](#openai-compatible-api-interface)
  - [Chat Completions API](#chat-completions-api)
  - [Using Local Models via OpenAI-Compatible Endpoints](#using-local-models-via-openai-compatible-endpoints)
- [Open WebUI: Browser Interface for Local LLMs](#open-webui-browser-interface-for-local-llms)
  - [Install Open WebUI with Docker](#install-open-webui-with-docker)
  - [Install Open WebUI on Linux (Native)](#install-open-webui-on-linux-native)
  - [Connect Open WebUI to llama.cpp Server](#connect-open-webui-to-llamacpp-server)
  - [Use Open WebUI as a Chat Front-End for This Project](#use-open-webui-as-a-chat-front-end-for-this-project)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Deployment with Docker](#deployment-with-docker)
  - [Option A: Docker Compose (Agent + Ollama)](#option-a-docker-compose-agent--ollama)
  - [Option B: Standalone Dockerfile](#option-b-standalone-dockerfile)
- [FastAPI Server](#fastapi-server)
- [Customization](#customization)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [References](#references)

---

## Overview

LangChain is an enterprise-grade framework that provides:
- **Ecosystem**: Integrations with various LLMs, vector stores, and tools
- **Agent Capabilities**: Build autonomous agents that can reason and use tools
- **Chain Composition**: Combine multiple components into sophisticated pipelines
- **Memory Management**: Maintain conversation context and state
- **Observability**: Built-in tracing and monitoring with LangSmith

---

## What's Included

- **agent.py**: Complete AI agent demo with tools (weather and calculator), supports Ollama + OpenAI
- **server.py**: FastAPI server to deploy the agent as a REST API
- **test_setup.py**: Verification script for imports, structure, and Ollama connectivity
- **docker-compose.yml**: One-command local deployment of agent + Ollama
- **Dockerfile**: Container image for the FastAPI server
- **.env.example**: Template for environment variables
- **requirements.txt**: Python dependencies list

---

## Prerequisites

- Python 3.9 or later (Python 3.12 recommended)
- [Docker](https://docs.docker.com/get-docker/) (for Ollama local inference)
- VS Code (recommended) with the Python extension
- OpenAI API key *(only required if using `LLM_PROVIDER=openai`)*

---

## Setup Instructions

### Step 1: Set Up Virtual Environment (VS Code)

#### Terminal setup

1. **Navigate to this directory**:
   ```bash
   cd "/path/to/AGENTS/LangChain"
   ```

2. **Create a virtual environment**:
   ```bash
   python3.12 -m venv venv
   ```

3. **Activate the virtual environment**:
   - **Linux / macOS**:
     ```bash
     source venv/bin/activate
     ```
   - **Windows**:
     ```cmd
     venv\Scripts\activate
     ```

#### Activate in VS Code

1. Open the Command Palette: `Ctrl+Shift+P` (Linux/Windows) or `Cmd+Shift+P` (macOS)
2. Type **Python: Select Interpreter** and press Enter
3. Choose the interpreter inside `venv/` — it will show as:
   ```
   Python 3.12.x ('venv': venv)  ./venv/bin/python
   ```
4. Open a **New Terminal** in VS Code (`Ctrl+` `` ` ``). It will automatically activate
   the venv and you will see `(venv)` at the start of the prompt.

### Step 2: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- `langchain` — Core LangChain framework
- `langchain-core` — Foundational abstractions
- `langchain-ollama` — Ollama integration for local inference
- `langchain-openai` — OpenAI integration
- `python-dotenv` — Environment variable management
- `fastapi` — Web framework for the REST API server
- `uvicorn` — ASGI server for FastAPI
- `httpx` / `requests` — HTTP clients

### Step 3: Configure Environment

1. **Copy the example environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env`** — for Ollama (default, no API key needed):
   ```env
   LLM_PROVIDER="ollama"
   OLLAMA_BASE_URL="http://localhost:11434"
   OLLAMA_MODEL="llama3.2"
   ```

   Or for OpenAI:
   ```env
   LLM_PROVIDER="openai"
   OPENAI_API_KEY="sk-your-actual-api-key-here"
   OPENAI_MODEL="gpt-3.5-turbo"
   ```

3. **`.env` is excluded from Git** (see `.gitignore`)

### Step 4: Run the Demo

#### Option A: Run the Standalone Agent

```bash
python agent.py
```

#### Option B: Run the FastAPI Server

```bash
python server.py
```

Then access:
- **API Docs**: http://localhost:8000/docs
- **Query endpoint**: POST to http://localhost:8000/query

Example API request:
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the weather in Tokyo?"}'
```

---

## Local Deployment with Ollama

### Why Use Ollama?

[Ollama](https://ollama.com/) is based on **llama.cpp** and lets you interact with LLMs directly
through your computer — completely offline, with no API costs. It exposes a local REST API on
port `11434` that LangChain connects to seamlessly.

Benefits:
- **Free** — no usage fees, no API key required
- **Private** — data never leaves your machine
- **Offline** — works without an internet connection after model download
- **Fast** — GPU acceleration supported (NVIDIA, Apple Silicon)

### Install Ollama on Linux (Native)

If you prefer to run Ollama directly on your Linux system without Docker, use the official
install script:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

The installer downloads the `ollama` binary to `/usr/local/bin` and registers a `systemd`
service that starts automatically on boot.

Verify the installation:

```bash
ollama --version
systemctl status ollama
```

The service listens on `http://localhost:11434` by default. Pull and run a model immediately:

```bash
ollama pull llama3.2
ollama run llama3.2
```

Manage the service:

```bash
sudo systemctl stop ollama
sudo systemctl restart ollama
sudo systemctl disable ollama    # prevent autostart on boot
```

To uninstall Ollama completely:

```bash
sudo systemctl stop ollama
sudo systemctl disable ollama
sudo rm /etc/systemd/system/ollama.service
sudo rm $(which ollama)
sudo rm -rf /usr/share/ollama ~/.ollama
```

### Step 1: Start the Ollama Container (Docker)

Run the official Ollama Docker image. This creates a persistent volume so downloaded models
survive container restarts:

```bash
docker run -d \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  ollama/ollama
```

Verify it is running:
```bash
docker ps --filter name=ollama
curl http://localhost:11434/api/tags
```

#### GPU Acceleration (NVIDIA)

To enable NVIDIA GPU acceleration, install the
[NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
and add the `--gpus` flag:

```bash
docker run -d \
  --gpus all \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  ollama/ollama
```

### Step 2: Pull a Model

Pull a lightweight model that supports tool use (recommended for LangChain agents):

```bash
# Recommended — Llama 3.2 3B (good tool use, 2.0 GB)
docker exec -it ollama ollama pull llama3.2

# Or pull directly by running it (pulls automatically if not present)
docker exec -it ollama ollama run llama3.2
```

List downloaded models:
```bash
docker exec -it ollama ollama list
```

### Step 3: Configure the Agent

Edit your `.env` file:
```env
LLM_PROVIDER="ollama"
OLLAMA_BASE_URL="http://localhost:11434"
OLLAMA_MODEL="llama3.2"
```

Then run:
```bash
python agent.py
```

---

### Available Open-Source Models

All models below run entirely on your machine via Ollama. Sizes are approximate download sizes.
Models marked with "tool use" work best with LangChain agents that need to call functions/tools.

| Model | Size | Strengths | Tool Use | Pull Command |
|-------|------|-----------|----------|--------------|
| `llama3.2:1b` | 1.3 GB | Ultra-fast, low memory | Limited | `ollama pull llama3.2:1b` |
| `llama3.2` (3B) | 2.0 GB | Balanced, good agent use | **Yes** | `ollama pull llama3.2` |
| `llama3.1:8b` | 4.9 GB | High quality, excellent tool use | **Yes** | `ollama pull llama3.1:8b` |
| `phi3:mini` | 2.2 GB | Microsoft, efficient reasoning | Good | `ollama pull phi3:mini` |
| `phi3.5:mini` | 2.2 GB | Updated Phi-3.5, improved reasoning | Good | `ollama pull phi3.5:mini` |
| `gemma2:2b` | 1.6 GB | Google, fast & efficient | Limited | `ollama pull gemma2:2b` |
| `gemma2:9b` | 5.4 GB | Google, very capable | **Yes** | `ollama pull gemma2:9b` |
| `qwen2.5:3b` | 2.0 GB | Alibaba, strong instruction following | **Yes** | `ollama pull qwen2.5:3b` |
| `qwen2.5:7b` | 4.7 GB | Alibaba, excellent tool use | **Yes** | `ollama pull qwen2.5:7b` |
| `mistral` (7B) | 4.1 GB | Great for instruction following | **Yes** | `ollama pull mistral` |
| `mistral-nemo` | 7.1 GB | Updated Mistral with tool use | **Yes** | `ollama pull mistral-nemo` |
| `tinyllama` | 638 MB | Minimum footprint (limited) | No | `ollama pull tinyllama` |
| `deepseek-r1:1.5b` | 1.1 GB | Reasoning-focused model | Limited | `ollama pull deepseek-r1:1.5b` |

**Recommended for this project (LangChain tool-calling agents):**
- **`llama3.2`** (default) — best balance of size and tool-use capability
- **`qwen2.5:3b`** — excellent alternative, very capable for its size
- **`mistral`** — highest quality at 7B if you have the disk space

To switch model, update `OLLAMA_MODEL` in your `.env` file.

---

### Using GGUF Models from Hugging Face

Ollama supports pulling **GGUF models** directly from the
[Hugging Face Hub](https://huggingface.co/models). This gives you access to thousands of
quantized community models.

#### Option A: Pull directly from Hugging Face (recommended)

Find a model on [Hugging Face](https://huggingface.co/models) that offers GGUF files.
On the model page, open the **Use this model** dropdown and choose **Ollama** — this shows
the exact pull command. Or run:

```bash
# General format:
docker exec -it ollama ollama run hf.co/USERNAME/REPOSITORY:QUANTIZATION

# Examples:
docker exec -it ollama ollama run hf.co/bartowski/Llama-3.2-3B-Instruct-GGUF:Q4_K_M
docker exec -it ollama ollama run hf.co/microsoft/Phi-3-mini-4k-instruct-gguf:Q4_K_M
```

Quantization tags (trade-off between quality and size):
- `Q4_K_M` — recommended, good quality at ~4 bits per weight
- `Q5_K_M` — slightly better quality, slightly larger
- `Q8_0` — near original quality, largest file size
- `Q2_K` — smallest, noticeable quality loss

#### Option B: Import a locally downloaded GGUF file

If you already have a `.gguf` file on your machine:

1. **Download the GGUF file** from the **Files and versions** tab of a Hugging Face model page.

2. **Create a `Modelfile`** in the same folder as the `.gguf` file:
   ```dockerfile
   FROM ./your-model-filename.gguf
   ```

3. **Copy the files into the running Ollama container**:
   ```bash
   docker cp ./your-model-filename.gguf ollama:/your-model-filename.gguf
   docker cp ./Modelfile ollama:/Modelfile
   ```

4. **Register and run the model**:
   ```bash
   docker exec -it ollama ollama create my-custom-model -f /Modelfile
   docker exec -it ollama ollama run my-custom-model
   ```

5. **Update `.env`** to use your custom model name:
   ```env
   OLLAMA_MODEL="my-custom-model"
   ```

**Requirements:**
- Models must be in **GGUF format**.
- If only PyTorch (`.pt`, `.bin`) or Safetensors (`.safetensors`) are available,
  convert them first using [llama.cpp](https://github.com/ggml-org/llama.cpp)
  (`convert_hf_to_gguf.py` script).

---

### Running Hugging Face Models with Testcontainers

[Testcontainers](https://testcontainers.com/) is a library that starts Docker containers
programmatically from code. Combined with Ollama, it enables reproducible LLM inference
environments without requiring a pre-installed Ollama service on the host.

This approach is described in the Docker blog post
[How to Run Hugging Face Models Programmatically Using Ollama and Testcontainers](https://www.docker.com/blog/how-to-run-hugging-face-models-programmatically-using-ollama-and-testcontainers/).

#### How It Works

1. Your script or test starts an Ollama container automatically via the Testcontainers API.
2. A Hugging Face GGUF model is pulled into the container at runtime.
3. Inference is performed against the containerized Ollama endpoint.
4. The container is stopped and removed automatically when the code block exits.

This makes LLM inference fully portable — no pre-installed Ollama, no manual model
management required on the test machine or CI/CD runner.

#### Python Example

Install the required packages:

```bash
pip install testcontainers[ollama] ollama
```

```python
from testcontainers.ollama import OllamaContainer

# Start an Ollama container and pull a Hugging Face GGUF model
with OllamaContainer() as ollama:
    ollama.pull_model("hf.co/bartowski/Llama-3.2-3B-Instruct-GGUF:Q4_K_M")

    base_url = ollama.get_endpoint()
    print(f"Ollama running at: {base_url}")

    # Connect LangChain to the containerized Ollama instance
    from langchain_ollama import ChatOllama
    llm = ChatOllama(
        model="hf.co/bartowski/Llama-3.2-3B-Instruct-GGUF:Q4_K_M",
        base_url=base_url
    )
    response = llm.invoke("What is the capital of France?")
    print(response.content)
# Container is stopped and removed automatically here
```

#### Use Cases

- **CI/CD pipelines**: Spin up models in automated tests without a persistent Ollama install.
- **Reproducible demos**: Scripts that self-provision the entire inference environment.
- **Isolation**: Each run starts with a clean container, preventing state leaks between tests.

---

## Ollama Architecture: How It Works Under the Hood

Ollama is a high-level wrapper and management tool built on top of
[llama.cpp](https://github.com/ggml-org/llama.cpp). It acts as a Go-based server that
orchestrates the underlying C++ inference engine, abstracting away model packaging, hardware
acceleration configuration, and API serving.

### The llama.cpp Inference Engine

[llama.cpp](https://github.com/ggml-org/llama.cpp) is a C/C++ library that provides highly
optimized LLM inference across platforms (Linux, macOS, Windows) for both CPUs and GPUs.
Ollama delegates all text generation to llama.cpp:

- **GGUF Format**: Ollama exclusively uses GGUF (GGML Unified Format) models — the standard
  developed by the llama.cpp project. A GGUF file packages model weights, vocabulary,
  metadata, and chat templates into a single self-contained file for efficient local execution.
- **Quantization**: GGUF files are typically quantized to reduce memory footprint while
  preserving most model quality. Common quantization levels:
  - `Q2_K` — smallest file, noticeable quality loss
  - `Q4_K_M` — recommended balance of quality and size (~4 bits per weight)
  - `Q5_K_M` — slightly better quality, slightly larger
  - `Q8_0` — near-original quality, largest file size
- **Hardware Acceleration**: llama.cpp compiles with support for:
  - CPU: AVX, AVX2, AVX-512 SIMD instructions
  - NVIDIA GPU: CUDA
  - AMD GPU: ROCm / HIP
  - Apple Silicon: Metal (MPS)

### Go Wrapper and Cgo Integration

Ollama is implemented as a Go application that wraps llama.cpp:

- **Backend service**: Ollama runs `ollama_llama_server`, a Go service that manages the
  llama.cpp process lifecycle and handles concurrent requests from multiple clients.
- **Cgo calls**: Ollama uses [Cgo](https://pkg.go.dev/cmd/cgo) to call directly into the
  llama.cpp C library for low-level operations such as `llama_model_load()` and
  `llama_model_quantize()`.
- **REST API**: Ollama exposes a REST API on port `11434` that is compatible with the
  OpenAI Chat Completions interface (see
  [OpenAI-Compatible API Interface](#openai-compatible-api-interface)).
- **Concurrency**: The Go layer manages multiple simultaneous client connections and queues
  inference requests to the single-instance llama.cpp engine.

### Model Management and GGUF Format

When you run `ollama pull <model>`:

1. Ollama downloads the GGUF file from the Ollama model registry or Hugging Face Hub.
2. Ollama creates a **Modelfile** — a configuration record that packages the system prompt,
   chat template, context window size, and inference parameters alongside the GGUF weights.
3. When a request arrives, Ollama reads the Modelfile and passes its configuration with the
   prompt to llama.cpp, which performs the actual token generation.
4. Models are stored in `~/.ollama/models/` (Linux/macOS) and persist across container
   restarts when a Docker volume is mounted at `/root/.ollama`.

This design means you do not need to configure llama.cpp manually — Ollama handles all
configuration automatically based on each model's Modelfile.

---

## Using llama.cpp Directly

[llama.cpp](https://github.com/ggml-org/llama.cpp) is the inference engine that Ollama is
built on. Using it directly gives you granular control over threading, GPU layer offloading,
quantization, and context size that Ollama abstracts away.

### Build from Source on Linux

**Prerequisites**: `git`, `cmake` (3.14+), and `gcc` or `clang`.

```bash
# Clone the repository
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp

# Build with make (CPU only)
make -j$(nproc)

# Build with CUDA support for NVIDIA GPUs
make LLAMA_CUDA=1 -j$(nproc)

# Alternative: CMake build
mkdir build && cd build
cmake .. -DGGML_CUDA=ON    # remove -DGGML_CUDA=ON for CPU-only
cmake --build . --config Release -j$(nproc)
```

After a `make` build, executables (`llama-cli`, `llama-server`) are in the project root.
After a CMake build, they are in `build/bin/`.

Download a GGUF model:

```bash
mkdir -p models

# Example: Llama 3.2 3B Q4_K_M quantization (~2 GB)
wget -O models/llama-3.2-3b-q4.gguf \
  "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf"
```

### Run with Docker

The official llama.cpp Docker image is published at `ghcr.io/ggml-org/llama.cpp`:

```bash
# CPU inference
docker run --rm -v $(pwd)/models:/models \
  ghcr.io/ggml-org/llama.cpp:latest \
  -m /models/llama-3.2-3b-q4.gguf \
  -p "What is the capital of France?" \
  -n 128

# NVIDIA GPU inference
docker run --rm --gpus all -v $(pwd)/models:/models \
  ghcr.io/ggml-org/llama.cpp:full-cuda \
  -m /models/llama-3.2-3b-q4.gguf \
  -p "What is the capital of France?" \
  -ngl 99 -n 128
```

Run the OpenAI-compatible server in Docker:

```bash
docker run --rm -p 8080:8080 -v $(pwd)/models:/models \
  ghcr.io/ggml-org/llama.cpp:server \
  --host 0.0.0.0 --port 8080 \
  -m /models/llama-3.2-3b-q4.gguf
```

### Run Inference with llama-cli

Basic prompt inference:

```bash
# Use a local GGUF file
./llama-cli -m models/llama-3.2-3b-q4.gguf -p "What is the capital of France?"

# Download and run a model directly from Hugging Face
./llama-cli -hf ggml-org/gemma-3-1b-it-GGUF
```

Key parameters:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `-m` | Path to GGUF model file | `-m models/llama-3.2-3b.gguf` |
| `-p` | Prompt text | `-p "Explain quantum computing"` |
| `-ngl` | GPU layers to offload (use 99 for all) | `-ngl 99` |
| `-t` | CPU threads (match physical core count) | `-t 8` |
| `-c` | Context window size in tokens | `-c 8192` |
| `-n` | Number of tokens to generate | `-n 256` |
| `--temp` | Sampling temperature (0 = deterministic) | `--temp 0.1` |
| `-hf` | Download and run directly from Hugging Face | `-hf ggml-org/gemma-3-1b-it-GGUF` |
| `-i` | Interactive (chat) mode | `-i` |

Examples:

```bash
# CPU-only inference, 8 threads, 4096 context window
./llama-cli -m models/llama-3.2-3b-q4.gguf -p "Explain LLMs." -t 8 -c 4096

# GPU-accelerated inference (offload all layers to NVIDIA GPU)
./llama-cli -m models/llama-3.2-3b-q4.gguf -p "Explain LLMs." -ngl 99 -c 4096

# Interactive chat mode
./llama-cli -m models/llama-3.2-3b-q4.gguf -i --chat-template llama3
```

### Launch an OpenAI-Compatible Server

`llama-server` exposes a REST API on `/v1/chat/completions` that is fully compatible with
the OpenAI SDK, LangChain, and any other OpenAI-compatible client:

```bash
# Start server on port 8080 (CPU only)
./llama-server -m models/llama-3.2-3b-q4.gguf --host 0.0.0.0 --port 8080

# Start server with NVIDIA GPU offloading
./llama-server -m models/llama-3.2-3b-q4.gguf --host 0.0.0.0 --port 8080 -ngl 99

# Download a Hugging Face model and start the server in one command
./llama-server -hf ggml-org/gemma-3-1b-it-GGUF
```

Connect LangChain to the llama.cpp server:

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    base_url="http://localhost:8080/v1",
    api_key="not-needed",       # llama-server does not require authentication
    model="local-model"
)
```

---

## OpenAI-Compatible API Interface

The OpenAI Chat Completions API has become the de facto standard interface for LLM inference.
Both Ollama and llama.cpp implement this same REST interface, which means the same client
code can target cloud models (OpenAI) or local models (Ollama, llama.cpp) by changing only
the `base_url`.

### Chat Completions API

The primary inference endpoint is `POST /v1/chat/completions`. It accepts a list of messages
with `system`, `user`, and `assistant` roles and returns a generated response.

**Key OpenAI API endpoints:**

| Endpoint | Purpose |
|----------|---------|
| `POST /v1/chat/completions` | Standard chat inference — the primary endpoint for most LLM tasks |
| `POST /v1/responses` | Newer OpenAI-native endpoint with built-in tools (web search, code interpreter) |
| `POST /v1/batches` | Asynchronous batch processing for high-volume tasks (50% cost discount) |
| `POST /v1/embeddings` | Convert text to numerical vectors for semantic search or recommendations |

**Python example using the OpenAI SDK (cloud):**

```python
from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY")

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user",   "content": "Explain LLM inference."}
    ]
)
print(response.choices[0].message.content)
```

### Using Local Models via OpenAI-Compatible Endpoints

Ollama and llama.cpp both expose `/v1/chat/completions`. Point the client to a local server
by setting `base_url`.

**Connect to Ollama (port 11434):**

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"        # Ollama does not validate the key value
)
response = client.chat.completions.create(
    model="llama3.2",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user",   "content": "What is the capital of France?"}
    ]
)
print(response.choices[0].message.content)
```

**Connect to llama.cpp server (port 8080):**

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8080/v1",
    api_key="not-needed"    # llama-server does not require authentication
)
response = client.chat.completions.create(
    model="local-model",
    messages=[{"role": "user", "content": "What is the capital of France?"}]
)
print(response.choices[0].message.content)
```

**Using LangChain with any OpenAI-compatible server:**

Use `ChatOpenAI` with `base_url` to connect LangChain to Ollama or llama.cpp without
changing any agent or tool code:

```python
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a given city name."""
    return f"It is sunny in {city}!"

# Point to Ollama
llm = ChatOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    model="llama3.2"
)

# Or point to llama.cpp server:
# llm = ChatOpenAI(base_url="http://localhost:8080/v1", api_key="none", model="local-model")

agent = create_react_agent(llm, [get_weather])
result = agent.invoke({"messages": [("human", "What is the weather in Paris?")]})
print(result["messages"][-1].content)
```

---

## Open WebUI: Browser Interface for Local LLMs

[Open WebUI](https://github.com/open-webui/open-webui) is a self-hosted, offline-capable web
interface for interacting with large language models. It provides a ChatGPT-style chat UI
that connects directly to Ollama or any OpenAI-compatible API endpoint, with no data sent to
external services.

Key capabilities:
- Full-featured chat interface with conversation history and model switching
- Supports Ollama natively and any OpenAI-compatible API (llama.cpp, LiteLLM, etc.)
- Multi-user support with role-based access control
- RAG (Retrieval-Augmented Generation) with document uploads
- Image generation, web browsing, and code execution tools (optional)
- Model management — pull, delete, and inspect Ollama models from the UI

### Install Open WebUI with Docker

The fastest way to run Open WebUI alongside an existing Ollama instance:

```bash
# Connect to Ollama running on the host machine
docker run -d \
  -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main
```

Open the interface at http://localhost:3000.

If Ollama is also running in Docker (e.g. via `docker-compose.yml`), link both containers
on the same network instead:

```bash
docker network create llm-net

docker run -d \
  --network llm-net \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  ollama/ollama

docker run -d \
  --network llm-net \
  -p 3000:8080 \
  -e OLLAMA_BASE_URL=http://ollama:11434 \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main
```

To enable NVIDIA GPU passthrough for the Ollama container in the same setup:

```bash
docker run -d \
  --network llm-net \
  --gpus all \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  ollama/ollama
```

### Install Open WebUI on Linux (Native)

Open WebUI is a Python/Node.js application and can run directly without Docker:

```bash
# Prerequisites: Python 3.11+ and Node.js 20+
pip install open-webui

# Start the server (connects to Ollama at localhost:11434 by default)
open-webui serve
```

The web interface is then available at http://localhost:8080.

To change the Ollama endpoint or bind to a different port:

```bash
OLLAMA_BASE_URL=http://localhost:11434 open-webui serve --port 3000
```

### Connect Open WebUI to llama.cpp Server

Open WebUI treats any OpenAI-compatible endpoint as a backend. To connect it to a running
`llama-server` instance:

1. Start the llama.cpp server (see [Launch an OpenAI-Compatible Server](#launch-an-openai-compatible-server)).
2. In Open WebUI, go to **Settings > Connections > OpenAI API**.
3. Set the API Base URL to `http://localhost:8080/v1` and the API key to any non-empty string.
4. Save and refresh — the connected models will appear in the model selector.

This allows you to use Open WebUI's full chat interface backed by llama.cpp inference,
without Ollama.

### Use Open WebUI as a Chat Front-End for This Project

Open WebUI can serve as a browser-based alternative to the FastAPI server included in this
project. Both use Ollama as the inference backend — the difference is the interface:

| Interface | Access | Best For |
|-----------|--------|----------|
| **Open WebUI** | http://localhost:3000 | Interactive chat, model exploration, multi-user |
| **FastAPI server** (`server.py`) | http://localhost:8000 | Programmatic API access, LangChain agent with tools |
| **agent.py** (terminal) | Terminal | Development, debugging agent reasoning |

Both can run simultaneously without conflict — they connect to the same Ollama service on
port 11434 independently.

Quick combined startup:

```bash
# Terminal 1: Start Ollama
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
docker exec -it ollama ollama pull llama3.2

# Terminal 2: Start Open WebUI
docker run -d \
  -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  -v open-webui:/app/backend/data \
  --name open-webui \
  ghcr.io/open-webui/open-webui:main

# Terminal 3: Start the LangChain FastAPI agent
source venv/bin/activate
python server.py
```

---

## Project Structure

```
LangChain/
▸ agent.py              # AI agent — tools, LLM init (Ollama/OpenAI), interactive loop
▸ server.py             # FastAPI REST API server for the agent
▸ test_setup.py         # Verification script (imports, structure, Ollama ping)
▸ run.sh                # Quick-start shell script
▸ requirements.txt      # Python dependencies
▸ Dockerfile            # Container image for the FastAPI server
▸ docker-compose.yml    # Compose file: FastAPI agent + Ollama service
▸ .env.example          # Environment variables template
▸ .env                  # Your local config (git-ignored)
▸ .gitignore            # Excludes venv, .env, model files, binaries
▸ .dockerignore         # Excludes build-time unnecessary files
▸ README.md             # This file
◈ venv/                 # Virtual environment (git-ignored, created locally)
```

---

## How It Works

### Agent Architecture

1. **Tools**: Functions the agent can call autonomously:
   - `GetWeather` — retrieves weather information for cities
   - `Calculator` — evaluates mathematical expressions

2. **Language Model**: Ollama (local) or OpenAI (cloud), selected by `LLM_PROVIDER` env var

3. **Agent Type**: `ZERO_SHOT_REACT_DESCRIPTION`

   - **ZERO_SHOT**: No examples needed — the agent figures out tool usage from descriptions alone
   - **REACT**: Alternates between **Reasoning** (Thought) and **Acting** (Action/Observation)
   - **DESCRIPTION**: Tool descriptions guide which tool to use

4. **Execution Flow**:
   ```
   User Query → Agent Reasoning → Tool Selection → Tool Execution → Response
   ```

### The ReAct Cycle in Action

When you run the agent with `verbose=True`:

```
User: "What's the weather in San Francisco?"

Thought: I need to use the GetWeather tool to find the weather information.
Action: GetWeather
Action Input: "San Francisco"
Observation: It's foggy and cool, 15°C

Thought: I now know the final answer.
Final Answer: The weather in San Francisco is foggy and cool, 15°C.
```

Each cycle:
1. **Thought** — agent reasons about what to do
2. **Action** — selects a tool
3. **Action Input** — passes input to the tool
4. **Observation** — reads the tool result
5. **Repeat or Finish** — loops until the answer is complete

### Other Agent Types in LangChain

| Agent Type | Best For | Notes |
|------------|----------|-------|
| `ZERO_SHOT_REACT_DESCRIPTION` | General purpose, basic tool use | Default, recommended |
| `CONVERSATIONAL_REACT_DESCRIPTION` | Chatbots with memory | Requires memory setup |
| `REACT_DOCSTORE` | Document search and QA | Specific to doc search |
| `SELF_ASK_WITH_SEARCH` | Research and fact-finding | Requires search tool |
| `STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION` | Complex structured inputs | More complex setup |

### Key Components

```python
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama   # local inference
# from langchain_openai import ChatOpenAI  # cloud inference

# 1. Define tools using the @tool decorator
@tool
def get_weather(city: str) -> str:
    """Get the current weather for a given city name."""
    return f"It is sunny in {city}!"

# 2. Initialize LLM (Ollama)
llm = ChatOllama(model="llama3.2", base_url="http://localhost:11434", temperature=0)

# 3. Create agent with LangGraph
agent_executor = create_react_agent(llm, [get_weather])

# 4. Invoke the agent
result = agent_executor.invoke({"messages": [("human", "What's the weather in Tokyo?")]})
print(result["messages"][-1].content)
```

---

## Deployment with Docker

### Option A: Docker Compose (Agent + Ollama)

The `docker-compose.yml` starts both the FastAPI agent and Ollama in one command:

```bash
# Build and start both services
docker compose up -d

# Pull a model into the Ollama service
docker compose exec ollama ollama pull llama3.2

# Check logs
docker compose logs -f langchain-agent
docker compose logs -f ollama

# Stop
docker compose down
```

After startup, the API is available at http://localhost:8000.

### Option B: Standalone Dockerfile

Build and run just the FastAPI agent container, connecting to an existing Ollama instance:

```bash
# Build the image
docker build -t langchain-agent .

# Run, pointing to host Ollama
docker run -d \
  -p 8000:8000 \
  -e LLM_PROVIDER=ollama \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  -e OLLAMA_MODEL=llama3.2 \
  --name langchain-agent \
  langchain-agent

# Or run with OpenAI
docker run -d \
  -p 8000:8000 \
  -e LLM_PROVIDER=openai \
  -e OPENAI_API_KEY=sk-your-key \
  -e OPENAI_MODEL=gpt-3.5-turbo \
  --name langchain-agent \
  langchain-agent
```

---

## FastAPI Server

The `server.py` file provides a production-ready REST API.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Health check — shows provider and status |
| `POST` | `/query` | Send a question to the agent |
| `GET` | `/tools` | List available agent tools |
| `GET` | `/docs` | Interactive Swagger UI documentation |
| `GET` | `/redoc` | ReDoc documentation |

### Run locally (venv)

```bash
# With uvicorn directly
uvicorn server:app --reload --host 0.0.0.0 --port 8000

# Or via the module
python server.py
```

### Run in production

```bash
pip install gunicorn
gunicorn server:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## Customization

### Adding New Tools

```python
from langchain_core.tools import tool

@tool
def my_custom_tool(input: str) -> str:
    """Describe when to use this tool and what it does."""
    return result

tools.append(my_custom_tool)
```

### Changing the LLM Provider

Edit `.env`:
```env
# Use Ollama (local, free)
LLM_PROVIDER="ollama"
OLLAMA_MODEL="mistral"

# Use OpenAI (cloud)
LLM_PROVIDER="openai"
OPENAI_API_KEY="sk-..."
OPENAI_MODEL="gpt-3.5-turbo"
```

### Using a Different LangChain LLM Class

```python
# Anthropic Claude
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-3-haiku-20240307")

# Google Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(model="gemini-pro")
```

---

## Testing

The `test_setup.py` script verifies imports, agent structure, environment config, and
optionally pings the Ollama server:

```bash
# Activate venv first
source venv/bin/activate

# Run all checks
python test_setup.py
```

Expected output with Ollama running:
```
============================================================
LangChain Setup Verification
============================================================
Testing imports...
✓ python-dotenv
✓ langchain.agents
✓ langchain_core.tools
✓ langchain_ollama (local inference)
✓ langchain_openai (cloud inference)
✓ fastapi
✓ uvicorn

Testing agent structure...
✓ Tool creation works
✓ AgentType.ZERO_SHOT_REACT_DESCRIPTION = zero-shot-react-description

Checking environment...
✓ .env file exists
✓ .env.example exists
✓ LLM_PROVIDER = ollama
✓ OLLAMA_BASE_URL = http://localhost:11434
✓ OLLAMA_MODEL = llama3.2

Checking Ollama connectivity...
✓ Ollama server reachable at http://localhost:11434
  Available models: llama3.2:latest
✓ Model 'llama3.2' is available
```

---

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'langchain_ollama'`
**Solution**: Install the Ollama integration:
```bash
pip install langchain-ollama
```

### Issue: Ollama not reachable / connection refused
**Solution**: Start the Ollama container:
```bash
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```
If the container exists but is stopped: `docker start ollama`

### Issue: Model not found in Ollama
**Solution**: Pull the model first:
```bash
docker exec -it ollama ollama pull llama3.2
```

### Issue: Agent gives unexpected or poor responses with small models
**Solution**:
- Try a larger model (`qwen2.5:7b`, `mistral`, `llama3.1:8b`)
- Enable `verbose=True` to see the agent's reasoning
- Improve tool descriptions to be more explicit

### Issue: `OPENAI_API_KEY not found`
**Solution**: Either set `LLM_PROVIDER=ollama` in `.env`, or add a valid OpenAI key.

### Issue: Import errors
**Solution**: Ensure the virtual environment is activated (`source venv/bin/activate`) and
dependencies are installed (`pip install -r requirements.txt`).

---

## References

- **LangChain Documentation**: https://python.langchain.com/docs/
- **LangChain Integrations**: https://docs.langchain.com/oss/python/integrations/providers/overview
- **LangChain GitHub**: https://github.com/langchain-ai/langchain
- **LangChain Ollama Integration**: https://python.langchain.com/docs/integrations/llms/ollama/
- **LangSmith (Observability)**: https://smith.langchain.com/
- **Ollama Official Site**: https://ollama.com/
- **Ollama Docker Hub**: https://hub.docker.com/r/ollama/ollama
- **Ollama GitHub**: https://github.com/ollama/ollama
- **Ollama Model Library**: https://ollama.com/library
- **Hugging Face Model Hub**: https://huggingface.co/models
- **Using Ollama with GGUF Models on Hugging Face**: https://huggingface.co/docs/hub/ollama
- **llama.cpp GitHub**: https://github.com/ggml-org/llama.cpp
- **llama.cpp Docker Image**: https://github.com/ggml-org/llama.cpp/pkgs/container/llama.cpp
- **How to Run Hugging Face Models with Ollama and Testcontainers**: https://www.docker.com/blog/how-to-run-hugging-face-models-programmatically-using-ollama-and-testcontainers/
- **Testcontainers for Python**: https://testcontainers-python.readthedocs.io/
- **OpenAI API Reference**: https://platform.openai.com/docs/
- **Open WebUI GitHub**: https://github.com/open-webui/open-webui
- **Open WebUI Documentation**: https://docs.openwebui.com/
- **Ollama Documentation**: https://docs.ollama.com/

---

## License

MIT
