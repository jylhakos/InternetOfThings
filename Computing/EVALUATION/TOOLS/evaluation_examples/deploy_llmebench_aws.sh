#!/bin/bash
# AWS LLMeBench Deployment Script
# Deploy standardized BERT benchmarking to AWS Batch

# 1. Create ECR repository for custom image
aws ecr create-repository --repository-name bert-llmebench

# 2. Create Dockerfile for LLMeBench
cat > Dockerfile.llmebench << 'EOF'
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y git

# Clone and install LLMeBench
RUN git clone https://github.com/qcri/LLMeBench.git
WORKDIR /app/LLMeBench
RUN pip install -r requirements.txt
RUN pip install -e .

# Install additional dependencies
RUN pip install torch transformers

# Copy evaluation scripts
COPY evaluation_examples/ /app/evaluation_examples/

ENTRYPOINT ["python", "/app/evaluation_examples/llmebench_example.py"]
EOF

# 3. Build and push image
$(aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com)
docker build -t bert-llmebench -f Dockerfile.llmebench .
docker tag bert-llmebench:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/bert-llmebench:latest
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/bert-llmebench:latest

# 4. Create Batch job definition
aws batch register-job-definition \
    --job-definition-name bert-llmebench-job \
    --type container \
    --container-properties '{
        "image": "YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/bert-llmebench:latest",
        "vcpus": 4,
        "memory": 8192,
        "jobRoleArn": "arn:aws:iam::YOUR_ACCOUNT:role/BatchJobRole"
    }'

# 5. Submit benchmark job
aws batch submit-job \
    --job-name bert-benchmark-$(date +%Y%m%d-%H%M%S) \
    --job-queue default-queue \
    --job-definition bert-llmebench-job

echo "✅ LLMeBench AWS Batch job submitted"
echo "📊 Monitor: aws batch describe-jobs --jobs JOB_ID"
