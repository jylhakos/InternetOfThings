FROM python:3.11-slim

# Set working directory
WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p data/secure_docs data/malicious_docs logs

# Set environment variables
ENV PYTHONPATH=/workspace
ENV PYTHONUNBUFFERED=1

# Expose port for API (if needed)
EXPOSE 8000

# Default command
CMD ["/bin/bash"]
