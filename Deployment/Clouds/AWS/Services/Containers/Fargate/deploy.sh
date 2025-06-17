#!/bin/bash

# Build and push Docker image
APP_NAME="go-rest-api"
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Build Docker image
docker build -t $APP_NAME .

# Tag for ECR
docker tag $APP_NAME:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$APP_NAME:latest

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Push image
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$APP_NAME:latest

# Update ECS service to use new image
aws ecs update-service --cluster $APP_NAME --service $APP_NAME --force-new-deployment --region $AWS_REGION

echo "Deployment completed!"