#!/bin/bash

# AWS Deployment Script for LLM Inference Server
# This script deploys the LLM Inference Server to AWS using CDK

set -e

echo "🚀 Starting AWS deployment for LLM Inference Server..."

# Check prerequisites
command -v aws >/dev/null 2>&1 || { echo "❌ AWS CLI is required but not installed. Aborting." >&2; exit 1; }
command -v cdk >/dev/null 2>&1 || { echo "❌ CDK CLI is required but not installed. Aborting." >&2; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting." >&2; exit 1; }

# Configuration
AWS_REGION=${AWS_REGION:-us-east-1}
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPOSITORY_NAME="llm-inference-server"
IMAGE_TAG=${IMAGE_TAG:-latest}

echo "📋 Configuration:"
echo "  AWS Region: $AWS_REGION"
echo "  AWS Account: $AWS_ACCOUNT_ID"
echo "  ECR Repository: $ECR_REPOSITORY_NAME"
echo "  Image Tag: $IMAGE_TAG"

# Create ECR repository if it doesn't exist
echo "📦 Setting up ECR repository..."
aws ecr describe-repositories --repository-names $ECR_REPOSITORY_NAME --region $AWS_REGION >/dev/null 2>&1 || {
    echo "Creating ECR repository: $ECR_REPOSITORY_NAME"
    aws ecr create-repository --repository-name $ECR_REPOSITORY_NAME --region $AWS_REGION
}

# Get ECR login token
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build Docker image
echo "🏗️ Building Docker image..."
docker build -t $ECR_REPOSITORY_NAME:$IMAGE_TAG .

# Tag image for ECR
echo "🏷️ Tagging image for ECR..."
docker tag $ECR_REPOSITORY_NAME:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:$IMAGE_TAG

# Push image to ECR
echo "📤 Pushing image to ECR..."
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:$IMAGE_TAG

# Create or update secrets in AWS Secrets Manager
echo "🔑 Setting up secrets..."
SECRET_NAME="llm-inference-secrets"

# Check if secret exists
if aws secretsmanager describe-secret --secret-id $SECRET_NAME --region $AWS_REGION >/dev/null 2>&1; then
    echo "Secret $SECRET_NAME already exists"
else
    echo "Creating secret $SECRET_NAME"
    
    # Generate a random JWT secret if not provided
    JWT_SECRET=${JWT_SECRET:-$(openssl rand -base64 32)}
    
    SECRET_VALUE=$(cat <<EOF
{
  "JWT_SECRET": "$JWT_SECRET",
  "OPENAI_API_KEY": "${OPENAI_API_KEY:-}",
  "HUGGINGFACE_API_KEY": "${HUGGINGFACE_API_KEY:-}"
}
EOF
)
    
    aws secretsmanager create-secret \
        --name $SECRET_NAME \
        --description "Secrets for LLM Inference Server" \
        --secret-string "$SECRET_VALUE" \
        --region $AWS_REGION
fi

# Deploy CDK stack
echo "☁️ Deploying CDK stack..."
cd cdk

# Install CDK dependencies
npm install

# Bootstrap CDK if needed
echo "🥾 Bootstrapping CDK (if needed)..."
cdk bootstrap aws://$AWS_ACCOUNT_ID/$AWS_REGION

# Deploy the stack
echo "🚀 Deploying infrastructure..."
cdk deploy --require-approval never

echo "✅ Deployment completed successfully!"

# Get the service URL
STACK_OUTPUT=$(aws cloudformation describe-stacks --stack-name LLMInferenceServerStack --region $AWS_REGION --query 'Stacks[0].Outputs')
SERVICE_URL=$(echo $STACK_OUTPUT | jq -r '.[] | select(.OutputKey=="ServiceURL") | .OutputValue')

echo ""
echo "🎉 LLM Inference Server deployed successfully!"
echo "🌐 Service URL: $SERVICE_URL"
echo "📊 Health Check: $SERVICE_URL/api/health"
echo "📖 API Documentation: $SERVICE_URL/"
echo ""
echo "Next steps:"
echo "1. Update your secrets in AWS Secrets Manager if needed"
echo "2. Configure your domain name and SSL certificate"
echo "3. Test the API endpoints"
echo "4. Set up monitoring and alerting"
echo ""
echo "To update the deployment:"
echo "  IMAGE_TAG=v2 ./scripts/deploy-aws.sh"
echo ""
echo "To destroy the deployment:"
echo "  cd cdk && cdk destroy"
