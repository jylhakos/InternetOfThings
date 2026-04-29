# Multi-stage Dockerfile for Dagster BERT Pipeline
# Stage 1: Base image with system dependencies
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    git \
    procps \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Dependencies installation
FROM base as dependencies

WORKDIR /app

# Copy requirements files
COPY requirements-dagster.txt requirements.txt requirements-api.txt ./

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements-dagster.txt && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-api.txt

# Stage 3: Application
FROM dependencies as application

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/dagster_home \
    /app/data/training \
    /app/models/bert_fine_tuned \
    /app/results/evaluation \
    /app/deployed_models/bert_classifier \
    /app/logs

# Create workspace.yaml for Dagster
RUN echo "load_from:" > /app/workspace.yaml && \
    echo "  - python_module:" >> /app/workspace.yaml && \
    echo "      module_name: dagster_project" >> /app/workspace.yaml && \
    echo "      working_directory: /app" >> /app/workspace.yaml

# Copy Dagster configuration if exists
COPY dagster.yaml /app/dagster_home/dagster.yaml

# Create non-root user for security
RUN groupadd -r dagster && \
    useradd -r -g dagster -u 1000 -m -d /home/dagster dagster && \
    chown -R dagster:dagster /app

# Switch to non-root user
USER dagster

# Set environment variables
ENV DAGSTER_HOME=/app/dagster_home \
    PYTHONPATH=/app

# Expose ports
EXPOSE 3000 8000

# Health check for Dagster webserver
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:3000/server_info || exit 1

# Default command (can be overridden)
CMD ["dagster", "dev", "-h", "0.0.0.0", "-p", "3000", "-w", "/app/workspace.yaml"]

# Stage 4: Production API image
FROM application as api

# Expose API port
EXPOSE 8000

# Health check for API
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# API command
CMD ["python", "api.py"]
