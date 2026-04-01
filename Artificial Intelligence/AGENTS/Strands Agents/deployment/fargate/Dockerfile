FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY fargate_app.py .

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "fargate_app.py"]
