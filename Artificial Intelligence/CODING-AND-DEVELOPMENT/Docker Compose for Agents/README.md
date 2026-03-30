# Compose for Agents

A tutorial for software developers to set up and utilize Docker Compose for AI agents with Python virtual environments in VS Code.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [SQL Agent Example](#sql-agent-example)
- [Running the Project](#running-the-project)
- [Project Structure](#project-structure)
- [Architecture Overview](#architecture-overview)
- [Cleanup](#cleanup)
- [References](#references)
- [Quick Start Commands Reference](#quick-start-commands-reference)

## Overview

This document describes the process of building and running AI agents with Docker Compose, including a reference implementation of a SQL Agent built with LangGraph that translates natural language queries into SQL.

**Key Features:**

- Zero-config setup with Docker Compose
- Local LLM inference using Docker Model Runner (no internet/API keys required)
- PostgreSQL database with pre-seeded Chinook database
- Python virtual environment for local development
- LangGraph-based AI agent with MCP (Model Context Protocol)

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker Desktop** 4.43.0+ or **Docker Engine** with Docker Compose 2.38.1+
  - [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
  - [Install Docker Engine](https://docs.docker.com/engine/)
- **Python** 3.12 or higher
- **VS Code** with Python extension
- **GPU support** (recommended for local model inference)
  - MacBook with GPU
  - Linux/Windows with NVIDIA GPU and drivers
  - Or use [Docker Offload](https://www.docker.com/products/docker-offload/)
- **Git** for cloning repositories

### VS Code Integration

1. Open Command Palette: `Ctrl+Shift+P` (or `Cmd+Shift+P`)
2. Select: `Python: Select Interpreter`
3. Choose: `./venv/bin/python`

**Or use VS Code Tasks:**

- Press `Ctrl+Shift+B` (or `Cmd+Shift+B`)
- Select task: "Docker Compose Up"

### Docker Model Runner Requirements

If using Docker Desktop on Windows or Docker Engine on Linux, ensure:

- GPU support is enabled
- [Docker Model Runner requirements](https://docs.docker.com/ai/model-runner/) are met
- Necessary GPU drivers are installed

## Environment Setup

### Step 1: Create Python Virtual Environment

Open VS Code terminal and create a virtual environment:

```bash
# Navigate to project directory
cd "/home/laptop/EXERCISES/IOT/InternetOfThings/Artificial Intelligence/CODING-AND-DEVELOPMENT/Compose for Agents"

# Create virtual environment
python3 -m venv venv

# Activate virtual environment (Linux/Mac)
source venv/bin/activate

# On Windows, use:
# venv\Scripts\activate
```

### Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install uv
uv sync

# 3. Download database (if needed)
wget https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite -O Chinook.db

# 4. Start services
docker compose up
```

### Configuration Files

#### **.gitignore** (Git Ignore Rules)

- Python cache files
- Virtual environments
- Secrets and keys
- IDE configurations

#### **.dockerignore** (Docker Ignore Rules)

- Development files exclusion
- Build optimization

#### **.vscode/settings.json** (VS Code Settings)

- Python interpreter path
- Auto-activation of virtual environment
- Docker Compose integration
- Formatting and linting

#### **.vscode/tasks.json** (VS Code Tasks)

- Setup virtual environment task
- Docker Compose up/down tasks
- Log viewing tasks
- Database download task

### Step 2: Activate Virtual Environment in VS Code

1. Open VS Code Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`)
2. Type: `Python: Select Interpreter`
3. Select the interpreter from `./venv/bin/python`

Or, VS Code should automatically detect and prompt you to use the virtual environment.

### Step 3: Install Python Dependencies

With the virtual environment activated:

```bash
# Install uv (fast Python package manager)
pip install uv

# Install project dependencies
uv sync
```

### Step 4: Verify Docker Installation

```bash
# Check Docker version
docker --version

# Check Docker Compose version
docker compose version

# Verify Docker is running
docker ps
```

### Core Files

#### **agent.py** (SQL Agent Implementation)

- LangGraph-based AI agent
- MCP (Model Context Protocol) integration
- Natural language to SQL query conversion
- Chinook database exploration

#### **compose.yaml** (Docker Compose Configuration)

- PostgreSQL database service
- SQLite importer service
- LangGraph agent service
- MCP Gateway service
- Docker Model Runner for local LLM

#### **Dockerfile** (Multi-stage Build)

- Base Python 3.12 image
- UV package manager for fast dependency installation
- Separate stages for importer and agent

#### **pyproject.toml** (Python Dependencies)

- LangChain and LangGraph
- MCP adapters
- PostgreSQL driver
- UV configuration

#### **importer.py** (Database Migration)

- SQLite to PostgreSQL data migration
- Automatic schema conversion
- Bulk data import using pgcopy

## SQL Agent Example

### What Does It Do?

This project demonstrates a **zero-config AI agent** that uses [LangGraph](https://github.com/langchain-ai/langgraph) to answer natural language questions by querying a SQL database.

The agent explores the **Chinook database** - a digital media store with information about:

- Artists and Albums
- Media Tracks
- Invoices and Sales
- Customers

**Example Questions:**

- "Who was the best-selling sales agent in 2010?"
- "List the top 3 albums by sales."
- "How many customers are from Brazil?"

### Architecture Components

1. **LangGraph Agent** (`agent.py`) - Transforms natural language into SQL queries
2. **PostgreSQL Database** - Runtime database populated from SQLite
3. **MCP Gateway** - Model Context Protocol server for database access
4. **Docker Model Runner** - Local LLM inference (llama3.2)
5. **SQLite Importer** - Imports Chinook.db to PostgreSQL

### Key Files

- `agent.py` - LangGraph agent logic with MCP tools integration
- `compose.yaml` - Docker Compose orchestration
- `Dockerfile` - Multi-stage build for importer and agent
- `pyproject.toml` - Python dependencies
- `importer.py` - SQLite to PostgreSQL data migration
- `Chinook.db` - Example database (downloadable)

## Running the Project

### Option 1: Using Docker Compose (Recommended)

This is the simplest method - everything runs in containers:

```bash
# Activate virtual environment first (for Docker commands)
source venv/bin/activate

# Download the Chinook database (if not present)
wget https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite -O Chinook.db

# Start all services
docker compose up

# Or run in detached mode
docker compose up -d

# View logs
docker compose logs -f agent
```

The agent will:

1. Start PostgreSQL database
2. Import Chinook.db data
3. Launch MCP Gateway and Model Runner
4. Answer the default question: "Who was the best-selling sales agent in 2010?"

### Option 2: Using OpenAI API

If you prefer using OpenAI instead of local inference:

```bash
# Create API key file
echo "sk-your-openai-api-key" > secret.openai-api-key

# Start with OpenAI configuration
docker compose down -v
docker compose -f compose.yaml -f compose.openai.yaml up
```

### Customizing the Question

Edit the `QUESTION` environment variable in `compose.yaml`:

```yaml
agent:
  environment:
    - QUESTION=List the top 5 best-selling artists.
```

### Using Your Own Database

Replace `Chinook.db` with your own SQLite file:

```yaml
importer:
  volumes:
    - ./your-database.db:/app/Chinook.db
```

## Project Structure

```
Compose for Agents/
├── agent.py                 # LangGraph agent implementation
├── compose.yaml            # Docker Compose configuration
├── Dockerfile              # Multi-stage Docker build
├── pyproject.toml          # Python dependencies
├── importer.py             # SQLite to PostgreSQL importer
├── Chinook.db              # Example database
├── venv/                   # Python virtual environment
└── README.md               # This file
```

## Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                    Docker Compose                        │
│                                                          │
│  ┌──────────────┐      ┌─────────────────┐               │
│  │   Agent      │─────▶│  MCP Gateway    │               │
│  │ (LangGraph)  │      │  (SSE Server)   │               │
│  └──────────────┘      └─────────────────┘               │
│         │                       │                        │
│         │                       │                        │
│         ▼                       ▼                        │
│  ┌──────────────┐      ┌─────────────────┐               │
│  │ Model Runner │      │   PostgreSQL    │               │
│  │ (llama3.2)   │      │   Database      │               │
│  └──────────────┘      └─────────────────┘               │
│                                ▲                         │
│                                │                         │
│                        ┌───────────────┐                 │
│                        │   Importer    │                 │
│                        │ (SQLite→PG)   │                 │
│                        └───────────────┘                 │
└──────────────────────────────────────────────────────────┘
```

**Workflow:**

1. User question is sent to LangGraph agent
2. Agent uses MCP tools to query PostgreSQL
3. Model Runner provides LLM inference
4. Agent returns natural language answer

## Cleanup

To stop all services and remove containers/volumes:

```bash
# Stop and remove everything
docker compose down -v

# Remove unused Docker resources
docker system prune -a
```

## References

### Official Documentation

- **Docker Compose for Agents**: [https://github.com/docker/compose-for-agents/tree/main](https://github.com/docker/compose-for-agents/tree/main)
- **LangGraph SQL Agent Example**: [https://github.com/docker/compose-for-agents/tree/main/langgraph](https://github.com/docker/compose-for-agents/tree/main/langgraph)
- **Agent Source Code**: [https://github.com/docker/compose-for-agents/blob/main/langgraph/agent.py](https://github.com/docker/compose-for-agents/blob/main/langgraph/agent.py)
- **Docker Compose Configuration**: [https://github.com/docker/compose-for-agents/blob/main/langgraph/compose.yaml](https://github.com/docker/compose-for-agents/blob/main/langgraph/compose.yaml)

### Related Projects

- **LangGraph**: [https://github.com/langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)
- **Docker Model Runner**: [https://docs.docker.com/ai/model-runner/](https://docs.docker.com/ai/model-runner/)
- **MCP Protocol**: [https://github.com/docker/mcp-gateway](https://github.com/docker/mcp-gateway)
- **Chinook Database**: [https://github.com/lerocha/chinook-database](https://github.com/lerocha/chinook-database)

### Additional Resources

- **Docker Desktop**: [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
- **Docker Compose Documentation**: [https://docs.docker.com/compose/](https://docs.docker.com/compose/)
- **Python Virtual Environments**: [https://docs.python.org/3/library/venv.html](https://docs.python.org/3/library/venv.html)
- **VS Code Python**: [https://code.visualstudio.com/docs/python/python-tutorial](https://code.visualstudio.com/docs/python/python-tutorial)

---

## Quick Start Commands Reference

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install uv
uv sync

# Download database
wget https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite -O Chinook.db

# Run
docker compose up

# Cleanup
docker compose down -v
```

---

**Note**: This project uses Docker Model Runner for local LLM inference by default. No internet connection or external API keys are required for the default setup. The agent runs completely offline with local models.
