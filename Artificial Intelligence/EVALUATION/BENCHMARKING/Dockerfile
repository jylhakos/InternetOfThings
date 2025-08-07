FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger'); nltk.download('wordnet')"

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p results data models

# Set environment variables
ENV TOKENIZERS_PARALLELISM=false
ENV HF_HOME=/app/.cache/huggingface
ENV PYTHONPATH=/app

# Expose port for Jupyter notebook
EXPOSE 8888

# Create entrypoint script
RUN echo '#!/bin/bash\n\
if [ "$1" = "notebook" ]; then\n\
    exec jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token="" --NotebookApp.password=""\n\
elif [ "$1" = "benchmark" ]; then\n\
    exec python benchmark_runner.py\n\
else\n\
    exec "$@"\n\
fi' > /entrypoint.sh && chmod +x /entrypoint.sh

# Default command
ENTRYPOINT ["/entrypoint.sh"]
CMD ["notebook"]
