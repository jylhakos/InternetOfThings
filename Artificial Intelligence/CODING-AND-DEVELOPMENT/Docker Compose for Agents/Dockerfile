FROM python:3.12-slim AS base

WORKDIR /app

# Install uv for fast Python package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Importer stage - for importing SQLite to PostgreSQL
FROM base AS importer

RUN uv add pgcopy

COPY importer.py ./

CMD ["uv", "run", "importer.py"]

# Agent stage - for running the LangGraph agent
FROM base AS agent

COPY agent.py ./

CMD ["uv", "run", "agent.py"]
