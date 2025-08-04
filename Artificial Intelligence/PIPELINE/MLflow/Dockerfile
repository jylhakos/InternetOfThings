# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/models /app/output /app/logs /app/powerbi_output

# Copy Fish.csv to data directory if it exists
RUN if [ -f "Dataset/Fish.csv" ]; then cp Dataset/Fish.csv data/; fi

# Set permissions
RUN chmod +x setup.sh activate_env.sh

# Expose ports for Jupyter and potential web services
EXPOSE 8888 8000 5000

# Set default command
CMD ["python", "scikit-learn/fish_predictive_model.py"]

# Optional: Use this for Jupyter notebook
# CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
