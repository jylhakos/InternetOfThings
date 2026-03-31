#!/bin/bash

# Strands Agents - Deployment Script for AWS Fargate

set -e

echo "========================================="
echo "Deploying Strands Agent to AWS Fargate"
echo "========================================="

# Configuration variables
AWS_REGION=${AWS_REGION:-us-west-2}
ECR_REPO_NAME="strands-agent"
STACK_NAME="strands-agent-fargate"

echo "Region: $AWS_REGION"
echo "ECR Repository: $ECR_REPO_NAME"
echo "Stack Name: $STACK_NAME"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "Error: AWS CLI is not installed."
    exit 1
fi

# Get AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "AWS Account ID: $AWS_ACCOUNT_ID"

# Create ECR repository if it doesn't exist
echo "Creating ECR repository..."
aws ecr describe-repositories --repository-names $ECR_REPO_NAME --region $AWS_REGION 2>/dev/null || \
    aws ecr create-repository --repository-name $ECR_REPO_NAME --region $AWS_REGION

# Login to ECR
echo "Logging in to ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build Docker image
echo "Building Docker image..."
cd deployment/fargate
docker build -t $ECR_REPO_NAME .

# Tag and push image
IMAGE_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest"
echo "Tagging image as $IMAGE_URI..."
docker tag $ECR_REPO_NAME:latest $IMAGE_URI

echo "Pushing image to ECR..."
docker push $IMAGE_URI

# Deploy CloudFormation stack
echo "Deploying CloudFormation stack..."
cd ../..
aws cloudformation deploy \
    --template-file deployment/fargate/cloudformation.yaml \
    --stack-name $STACK_NAME \
    --parameter-overrides ImageUri=$IMAGE_URI \
    --capabilities CAPABILITY_IAM \
    --region $AWS_REGION

echo ""
echo "========================================="
echo "✓ Deployment completed!"
echo "========================================="
echo ""
echo "Getting load balancer URL..."
aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerUrl`].OutputValue' \
    --output text \
    --region $AWS_REGION

echo ""
