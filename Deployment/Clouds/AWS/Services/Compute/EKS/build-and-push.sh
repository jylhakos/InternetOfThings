#!/bin/bash

# Set variables
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION="us-west-2"  # Change to your preferred region
IMAGE_NAME="go-k8s-app"
IMAGE_TAG="latest"

# Create ECR repository if it doesn't exist
aws ecr describe-repositories --repository-names $IMAGE_NAME --region $AWS_REGION || \
aws ecr create-repository --repository-name $IMAGE_NAME --region $AWS_REGION

# Get login token and login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build Docker image
docker build -t $IMAGE_NAME:$IMAGE_TAG .

# Tag for ECR
docker tag $IMAGE_NAME:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$IMAGE_NAME:$IMAGE_TAG

# Push to ECR
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$IMAGE_NAME:$IMAGE_TAG

echo "Image pushed to: $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$IMAGE_NAME:$IMAGE_TAG"