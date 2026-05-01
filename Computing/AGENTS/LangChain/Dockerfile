# ============================================================
# Dockerfile — LangChain AI Agent (FastAPI)
# ============================================================
# This image runs the FastAPI server that exposes the LangChain
# agent as a REST API. It connects to an external Ollama container
# (or OpenAI cloud API) as the LLM backend.
#
# Build:
#   docker build -t langchain-agent .
#
# Run standalone (connect to host Ollama):
#   docker run -d \
#     -p 8000:8000 \
#     -e LLM_PROVIDER=ollama \
#     -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
#     -e OLLAMA_MODEL=llama3.2 \
#     --name langchain-agent \
#     langchain-agent
#
# Run with docker-compose (recommended):
#   docker compose up
# ============================================================

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed by some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (Docker layer cache optimisation)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application source code
# (excludes paths listed in .dockerignore)
COPY agent.py .
COPY server.py .

# Copy environment template (actual .env is supplied at runtime)
COPY .env.example .

# Expose FastAPI port
EXPOSE 8000

# Health check — polls the FastAPI health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the FastAPI server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
