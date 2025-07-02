#!/bin/bash

# Variables
AWS_REGION="us-west-2"
ECR_REPOSITORY="myapp"
IMAGE_TAG="latest"

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# ECR repository URL
ECR_REPOSITORY_URL="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}"

# Login to ECR
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPOSITORY_URL}

# Build the image
docker build -t ${ECR_REPOSITORY}:${IMAGE_TAG} .

# Tag the image
docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${ECR_REPOSITORY_URL}:${IMAGE_TAG}

# Push to ECR
docker push ${ECR_REPOSITORY_URL}:${IMAGE_TAG}

echo "Image pushed successfully to ${ECR_REPOSITORY_URL}:${IMAGE_TAG}"