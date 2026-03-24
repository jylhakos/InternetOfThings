#!/bin/bash

# Production-ready AWS deployment with ECS and Load Balancer
# This script sets up a more robust production environment

set -e

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
CLUSTER_NAME="llm-chat-cluster"
SERVICE_NAME="llm-chat-service"
TASK_FAMILY="llm-chat-task"
ECR_REPO_NAME="llm-chat-service"
VPC_NAME="llm-chat-vpc"
SUBNETS_COUNT=2

echo "🚀 Deploying LLM Chat Service to AWS ECS (Production)"

# Check prerequisites
command -v aws >/dev/null 2>&1 || { echo "❌ AWS CLI required"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ Docker required"; exit 1; }

# Build and push Docker image
echo "🐳 Building Docker image..."

# Create Dockerfile
cat > ../Dockerfile << 'EOF'
FROM openjdk:17-jdk-slim

# Install curl and other utilities
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Maven files
COPY pom.xml .
COPY src ./src

# Install Maven
RUN apt-get update && apt-get install -y maven && rm -rf /var/lib/apt/lists/*

# Build application
RUN mvn clean package -DskipTests

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8080/api/v1/chat/health || exit 1

# Run application
CMD ["java", "-jar", "target/llm-chat-service-1.0.0.jar"]
EOF

# Build Docker image
docker build -t $ECR_REPO_NAME ../

# Create ECR repository
echo "📦 Setting up ECR repository..."
aws ecr describe-repositories --repository-names $ECR_REPO_NAME --region $AWS_REGION >/dev/null 2>&1 || \
aws ecr create-repository --repository-name $ECR_REPO_NAME --region $AWS_REGION

# Get ECR login
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com

# Tag and push image
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest"
docker tag $ECR_REPO_NAME:latest $ECR_URI
docker push $ECR_URI

echo "✅ Docker image pushed to ECR: $ECR_URI"

# Create ECS cluster
echo "🏗️  Creating ECS cluster..."
aws ecs describe-clusters --clusters $CLUSTER_NAME --region $AWS_REGION >/dev/null 2>&1 || \
aws ecs create-cluster --cluster-name $CLUSTER_NAME --region $AWS_REGION

# Create IAM role for ECS tasks
echo "🔐 Setting up IAM roles..."
cat > task-role-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

aws iam create-role --role-name ecsTaskRole --assume-role-policy-document file://task-role-policy.json 2>/dev/null || true
aws iam attach-role-policy --role-name ecsTaskRole --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

# Create task definition
echo "📋 Creating ECS task definition..."
cat > task-definition.json << EOF
{
  "family": "$TASK_FAMILY",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "executionRoleArn": "arn:aws:iam::$ACCOUNT_ID:role/ecsTaskRole",
  "taskRoleArn": "arn:aws:iam::$ACCOUNT_ID:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "ollama",
      "image": "ollama/ollama:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 11434,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "OLLAMA_HOST",
          "value": "0.0.0.0"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/$TASK_FAMILY",
          "awslogs-region": "$AWS_REGION",
          "awslogs-stream-prefix": "ollama"
        }
      }
    },
    {
      "name": "llm-chat-service",
      "image": "$ECR_URI",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "SPRING_AI_OLLAMA_BASE_URL",
          "value": "http://localhost:11434"
        }
      ],
      "dependsOn": [
        {
          "containerName": "ollama",
          "condition": "START"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/$TASK_FAMILY",
          "awslogs-region": "$AWS_REGION",
          "awslogs-stream-prefix": "app"
        }
      }
    }
  ]
}
EOF

# Create CloudWatch log group
aws logs create-log-group --log-group-name "/ecs/$TASK_FAMILY" --region $AWS_REGION 2>/dev/null || true

# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json --region $AWS_REGION

# Get default VPC and subnets
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query 'Vpcs[0].VpcId' --output text --region $AWS_REGION)
SUBNETS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query 'Subnets[0:2].SubnetId' --output text --region $AWS_REGION)
SUBNET_IDS=($(echo $SUBNETS | tr '\t' ' '))

# Create security group for ECS
SECURITY_GROUP_ID=$(aws ec2 create-security-group \
    --group-name "$SERVICE_NAME-sg" \
    --description "Security group for $SERVICE_NAME" \
    --vpc-id "$VPC_ID" \
    --region $AWS_REGION \
    --query 'GroupId' --output text 2>/dev/null) || \
aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=$SERVICE_NAME-sg" \
    --query 'SecurityGroups[0].GroupId' --output text --region $AWS_REGION

# Add security group rules
aws ec2 authorize-security-group-ingress \
    --group-id "$SECURITY_GROUP_ID" \
    --protocol tcp \
    --port 8080 \
    --cidr 0.0.0.0/0 \
    --region $AWS_REGION 2>/dev/null || true

# Create ECS service
echo "🚀 Creating ECS service..."
cat > service-definition.json << EOF
{
  "serviceName": "$SERVICE_NAME",
  "cluster": "$CLUSTER_NAME",
  "taskDefinition": "$TASK_FAMILY",
  "desiredCount": 1,
  "launchType": "FARGATE",
  "networkConfiguration": {
    "awsvpcConfiguration": {
      "subnets": ["${SUBNET_IDS[0]}", "${SUBNET_IDS[1]}"],
      "securityGroups": ["$SECURITY_GROUP_ID"],
      "assignPublicIp": "ENABLED"
    }
  }
}
EOF

aws ecs create-service --cli-input-json file://service-definition.json --region $AWS_REGION

echo "⏳ Waiting for service to be stable..."
aws ecs wait services-stable --cluster $CLUSTER_NAME --services $SERVICE_NAME --region $AWS_REGION

# Get service endpoint
TASK_ARN=$(aws ecs list-tasks --cluster $CLUSTER_NAME --service-name $SERVICE_NAME --region $AWS_REGION --query 'taskArns[0]' --output text)
PUBLIC_IP=$(aws ecs describe-tasks --cluster $CLUSTER_NAME --tasks $TASK_ARN --region $AWS_REGION --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' --output text | xargs -I {} aws ec2 describe-network-interfaces --network-interface-ids {} --query 'NetworkInterfaces[0].Association.PublicIp' --output text --region $AWS_REGION)

echo "✅ ECS Deployment Complete!"
echo ""
echo "🎯 Service Details:"
echo "Cluster: $CLUSTER_NAME"
echo "Service: $SERVICE_NAME"
echo "Public IP: $PUBLIC_IP"
echo "Application URL: http://$PUBLIC_IP:8080"
echo ""
echo "📊 Monitoring:"
echo "ECS Console: https://console.aws.amazon.com/ecs/home?region=$AWS_REGION#/clusters/$CLUSTER_NAME/services"
echo "CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/home?region=$AWS_REGION#logStream:group=/ecs/$TASK_FAMILY"
echo ""
echo "🗑️  Cleanup:"
echo "aws ecs delete-service --cluster $CLUSTER_NAME --service $SERVICE_NAME --force --region $AWS_REGION"
echo "aws ecs delete-cluster --cluster $CLUSTER_NAME --region $AWS_REGION"

# Cleanup temp files
rm -f task-definition.json service-definition.json task-role-policy.json ../Dockerfile
