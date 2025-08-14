#!/bin/bash

# Flutter SPA AWS Deployment Script
# This script deploys the Flutter SPA and backend to AWS using various AWS services

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STACK_NAME="flutter-spa-infrastructure"
REGION=${AWS_DEFAULT_REGION:-us-east-1}
ENVIRONMENT=${ENVIRONMENT:-production}
APP_NAME="flutter-spa"

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install it first."
        exit 1
    fi
    
    # Check Flutter
    if ! command -v flutter &> /dev/null; then
        print_error "Flutter is not installed. Please install it first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials are not configured. Please run 'aws configure'."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Create S3 bucket for static assets
create_s3_bucket() {
    print_status "Creating S3 bucket for static assets..."
    
    BUCKET_NAME="${APP_NAME}-assets-$(date +%s)"
    
    # Create bucket
    aws s3 mb s3://${BUCKET_NAME} --region ${REGION}
    
    # Configure bucket for website hosting
    aws s3 website s3://${BUCKET_NAME} \
        --index-document index.html \
        --error-document error.html
    
    # Set bucket policy for public read
    cat > bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::${BUCKET_NAME}/*"
        }
    ]
}
EOF
    
    aws s3api put-bucket-policy \
        --bucket ${BUCKET_NAME} \
        --policy file://bucket-policy.json
    
    rm bucket-policy.json
    
    print_success "S3 bucket created: ${BUCKET_NAME}"
    echo "BUCKET_NAME=${BUCKET_NAME}" >> .env.deployment
}

# Create ECR repositories
create_ecr_repositories() {
    print_status "Creating ECR repositories..."
    
    # Create backend repository
    aws ecr create-repository \
        --repository-name ${APP_NAME}/backend \
        --region ${REGION} || true
    
    # Create frontend repository
    aws ecr create-repository \
        --repository-name ${APP_NAME}/frontend \
        --region ${REGION} || true
    
    print_success "ECR repositories created"
}

# Build and push Docker images
build_and_push_images() {
    print_status "Building and pushing Docker images..."
    
    # Get ECR login token
    aws ecr get-login-password --region ${REGION} | \
        docker login --username AWS --password-stdin \
        $(aws sts get-caller-identity --query Account --output text).dkr.ecr.${REGION}.amazonaws.com
    
    # Build and push backend image
    print_status "Building backend image..."
    docker build -t ${APP_NAME}/backend ./backend
    docker tag ${APP_NAME}/backend:latest \
        $(aws sts get-caller-identity --query Account --output text).dkr.ecr.${REGION}.amazonaws.com/${APP_NAME}/backend:latest
    docker push $(aws sts get-caller-identity --query Account --output text).dkr.ecr.${REGION}.amazonaws.com/${APP_NAME}/backend:latest
    
    # Build and push frontend image
    print_status "Building frontend image..."
    docker build -t ${APP_NAME}/frontend .
    docker tag ${APP_NAME}/frontend:latest \
        $(aws sts get-caller-identity --query Account --output text).dkr.ecr.${REGION}.amazonaws.com/${APP_NAME}/frontend:latest
    docker push $(aws sts get-caller-identity --query Account --output text).dkr.ecr.${REGION}.amazonaws.com/${APP_NAME}/frontend:latest
    
    print_success "Docker images built and pushed"
}

# Deploy infrastructure with CloudFormation
deploy_infrastructure() {
    print_status "Deploying infrastructure with CloudFormation..."
    
    aws cloudformation deploy \
        --template-file infrastructure/cloudformation/template.yaml \
        --stack-name ${STACK_NAME} \
        --parameter-overrides \
            Environment=${ENVIRONMENT} \
            AppName=${APP_NAME} \
        --capabilities CAPABILITY_IAM \
        --region ${REGION}
    
    print_success "Infrastructure deployed"
}

# Deploy with AWS Amplify
deploy_amplify() {
    print_status "Setting up AWS Amplify..."
    
    # Initialize Amplify if not already done
    if [ ! -d "./amplify" ]; then
        print_status "Initializing Amplify..."
        amplify init --yes
    fi
    
    # Add hosting
    amplify add hosting
    
    # Deploy
    amplify publish
    
    print_success "Amplify deployment completed"
}

# Create ECS cluster and services
deploy_ecs() {
    print_status "Deploying to ECS..."
    
    # Create cluster
    aws ecs create-cluster --cluster-name ${APP_NAME}-cluster
    
    # Register task definitions
    aws ecs register-task-definition \
        --cli-input-json file://infrastructure/ecs/task-definition-backend.json
    
    aws ecs register-task-definition \
        --cli-input-json file://infrastructure/ecs/task-definition-frontend.json
    
    # Create services
    aws ecs create-service \
        --cluster ${APP_NAME}-cluster \
        --service-name ${APP_NAME}-backend \
        --task-definition ${APP_NAME}-backend:1 \
        --desired-count 2
    
    aws ecs create-service \
        --cluster ${APP_NAME}-cluster \
        --service-name ${APP_NAME}-frontend \
        --task-definition ${APP_NAME}-frontend:1 \
        --desired-count 2
    
    print_success "ECS services deployed"
}

# Set up API Gateway
setup_api_gateway() {
    print_status "Setting up API Gateway..."
    
    # Create REST API
    API_ID=$(aws apigateway create-rest-api \
        --name ${APP_NAME}-api \
        --query 'id' \
        --output text)
    
    # Get root resource ID
    ROOT_ID=$(aws apigateway get-resources \
        --rest-api-id ${API_ID} \
        --query 'items[0].id' \
        --output text)
    
    # Create proxy resource
    PROXY_ID=$(aws apigateway create-resource \
        --rest-api-id ${API_ID} \
        --parent-id ${ROOT_ID} \
        --path-part '{proxy+}' \
        --query 'id' \
        --output text)
    
    # Add ANY method to proxy resource
    aws apigateway put-method \
        --rest-api-id ${API_ID} \
        --resource-id ${PROXY_ID} \
        --http-method ANY \
        --authorization-type NONE
    
    # Deploy API
    aws apigateway create-deployment \
        --rest-api-id ${API_ID} \
        --stage-name prod
    
    print_success "API Gateway set up: https://${API_ID}.execute-api.${REGION}.amazonaws.com/prod"
}

# Set up monitoring
setup_monitoring() {
    print_status "Setting up monitoring..."
    
    # Create CloudWatch dashboard
    aws cloudwatch put-dashboard \
        --dashboard-name ${APP_NAME}-dashboard \
        --dashboard-body file://infrastructure/monitoring/dashboard.json
    
    # Create alarms
    aws cloudwatch put-metric-alarm \
        --alarm-name ${APP_NAME}-high-cpu \
        --alarm-description "High CPU utilization" \
        --actions-enabled \
        --alarm-actions arn:aws:sns:${REGION}:$(aws sts get-caller-identity --query Account --output text):${APP_NAME}-alerts \
        --metric-name CPUUtilization \
        --namespace AWS/ECS \
        --statistic Average \
        --period 300 \
        --threshold 80 \
        --comparison-operator GreaterThanThreshold \
        --evaluation-periods 2
    
    print_success "Monitoring set up"
}

# Clean up temporary files
cleanup() {
    print_status "Cleaning up temporary files..."
    rm -f .env.deployment
    docker system prune -f
    print_success "Cleanup completed"
}

# Main deployment function
deploy() {
    print_status "Starting deployment of Flutter SPA to AWS..."
    
    case ${1:-full} in
        "check")
            check_prerequisites
            ;;
        "build")
            check_prerequisites
            build_and_push_images
            ;;
        "infrastructure")
            check_prerequisites
            deploy_infrastructure
            ;;
        "amplify")
            check_prerequisites
            deploy_amplify
            ;;
        "ecs")
            check_prerequisites
            create_ecr_repositories
            build_and_push_images
            deploy_ecs
            ;;
        "api")
            check_prerequisites
            setup_api_gateway
            ;;
        "monitoring")
            check_prerequisites
            setup_monitoring
            ;;
        "full")
            check_prerequisites
            create_s3_bucket
            create_ecr_repositories
            build_and_push_images
            deploy_infrastructure
            setup_api_gateway
            setup_monitoring
            cleanup
            ;;
        *)
            echo "Usage: $0 {check|build|infrastructure|amplify|ecs|api|monitoring|full}"
            echo "  check         - Check prerequisites"
            echo "  build         - Build and push Docker images"
            echo "  infrastructure - Deploy infrastructure"
            echo "  amplify       - Deploy with Amplify"
            echo "  ecs          - Deploy with ECS"
            echo "  api          - Set up API Gateway"
            echo "  monitoring   - Set up monitoring"
            echo "  full         - Full deployment (default)"
            exit 1
            ;;
    esac
    
    print_success "Deployment completed successfully!"
}

# Handle script termination
trap cleanup EXIT

# Run deployment
deploy $1
