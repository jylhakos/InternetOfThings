#!/bin/bash

# Microservices Application Deployment Script
# This script deploys the complete microservices application to AWS

set -e  # Exit on any error

# Configuration
ENVIRONMENT_NAME="microservices"
AWS_REGION="us-east-1"
AWS_PROFILE="default"  # Change to your AWS profile

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        error "AWS CLI is not installed. Please install it first."
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install it first."
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        error "Node.js is not installed. Please install it first."
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        error "npm is not installed. Please install it first."
    fi
    
    log "All prerequisites are satisfied."
}

# Build and push Docker images
build_and_push_images() {
    log "Building and pushing Docker images..."
    
    # Get AWS account ID
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --profile $AWS_PROFILE --query Account --output text)
    ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
    
    # Create ECR repositories if they don't exist
    for service in auth-service user-service api-gateway; do
        aws ecr describe-repositories --profile $AWS_PROFILE --region $AWS_REGION --repository-names "microservices/${service}" 2>/dev/null || \
        aws ecr create-repository --profile $AWS_PROFILE --region $AWS_REGION --repository-name "microservices/${service}"
    done
    
    # Login to ECR
    aws ecr get-login-password --profile $AWS_PROFILE --region $AWS_REGION | \
        docker login --username AWS --password-stdin $ECR_REGISTRY
    
    # Build and push images
    for service in auth-service user-service api-gateway; do
        log "Building ${service}..."
        docker build -t "microservices/${service}:latest" "./backend/${service}"
        docker tag "microservices/${service}:latest" "${ECR_REGISTRY}/microservices/${service}:latest"
        docker push "${ECR_REGISTRY}/microservices/${service}:latest"
    done
    
    log "Docker images built and pushed successfully."
}

# Deploy CloudFormation stacks
deploy_infrastructure() {
    log "Deploying infrastructure..."
    
    # Note: AWS CLI automatically uploads local template files to S3
    # when using --template-file. No manual S3 upload required.
    
    # Deploy network stack
    log "Deploying network infrastructure..."
    aws cloudformation deploy \
        --profile $AWS_PROFILE \
        --region $AWS_REGION \
        --template-file infrastructure/01-network.yaml \
        --stack-name "${ENVIRONMENT_NAME}-network" \
        --parameter-overrides EnvironmentName=$ENVIRONMENT_NAME \
        --capabilities CAPABILITY_NAMED_IAM \
        --no-fail-on-empty-changeset
    
    # Deploy database stack
    log "Deploying database infrastructure..."
    aws cloudformation deploy \
        --profile $AWS_PROFILE \
        --region $AWS_REGION \
        --template-file infrastructure/02-database.yaml \
        --stack-name "${ENVIRONMENT_NAME}-database" \
        --parameter-overrides EnvironmentName=$ENVIRONMENT_NAME \
        --capabilities CAPABILITY_NAMED_IAM \
        --no-fail-on-empty-changeset
    
    # Create JWT secret
    create_jwt_secret
    
    # Deploy ECS stack
    log "Deploying ECS infrastructure..."
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --profile $AWS_PROFILE --query Account --output text)
    ECR_REPOSITORY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/microservices"
    
    aws cloudformation deploy \
        --profile $AWS_PROFILE \
        --region $AWS_REGION \
        --template-file infrastructure/03-ecs.yaml \
        --stack-name "${ENVIRONMENT_NAME}-ecs" \
        --parameter-overrides \
            EnvironmentName=$ENVIRONMENT_NAME \
            ECRRepository=$ECR_REPOSITORY \
            ImageTag=latest \
        --capabilities CAPABILITY_NAMED_IAM \
        --no-fail-on-empty-changeset
    
    # Deploy frontend stack
    log "Deploying frontend infrastructure..."
    aws cloudformation deploy \
        --profile $AWS_PROFILE \
        --region $AWS_REGION \
        --template-file infrastructure/04-frontend.yaml \
        --stack-name "${ENVIRONMENT_NAME}-frontend" \
        --parameter-overrides EnvironmentName=$ENVIRONMENT_NAME \
        --capabilities CAPABILITY_NAMED_IAM \
        --no-fail-on-empty-changeset
    
    log "Infrastructure deployed successfully."
}

# Create JWT secret
create_jwt_secret() {
    log "Creating JWT secret..."
    
    # Generate a random JWT secret
    JWT_SECRET=$(openssl rand -base64 32)
    
    # Check if secret exists
    if aws secretsmanager describe-secret --profile $AWS_PROFILE --region $AWS_REGION --secret-id "${ENVIRONMENT_NAME}/jwt-secret" 2>/dev/null; then
        log "JWT secret already exists, updating..."
        aws secretsmanager update-secret \
            --profile $AWS_PROFILE \
            --region $AWS_REGION \
            --secret-id "${ENVIRONMENT_NAME}/jwt-secret" \
            --secret-string "{\"jwt_secret\":\"$JWT_SECRET\"}"
    else
        log "Creating new JWT secret..."
        aws secretsmanager create-secret \
            --profile $AWS_PROFILE \
            --region $AWS_REGION \
            --name "${ENVIRONMENT_NAME}/jwt-secret" \
            --description "JWT secret for microservices application" \
            --secret-string "{\"jwt_secret\":\"$JWT_SECRET\"}"
    fi
}

# Build and deploy frontend
deploy_frontend() {
    log "Building and deploying frontend..."
    
    # Get CloudFront distribution ID and S3 bucket name
    BUCKET_NAME=$(aws cloudformation describe-stacks \
        --profile $AWS_PROFILE \
        --region $AWS_REGION \
        --stack-name "${ENVIRONMENT_NAME}-frontend" \
        --query "Stacks[0].Outputs[?OutputKey=='FrontendBucket'].OutputValue" \
        --output text)
    
    DISTRIBUTION_ID=$(aws cloudformation describe-stacks \
        --profile $AWS_PROFILE \
        --region $AWS_REGION \
        --stack-name "${ENVIRONMENT_NAME}-frontend" \
        --query "Stacks[0].Outputs[?OutputKey=='CloudFrontDistribution'].OutputValue" \
        --output text)
    
    # Get API Gateway URL
    API_URL=$(aws cloudformation describe-stacks \
        --profile $AWS_PROFILE \
        --region $AWS_REGION \
        --stack-name "${ENVIRONMENT_NAME}-ecs" \
        --query "Stacks[0].Outputs[?OutputKey=='LoadBalancerURL'].OutputValue" \
        --output text)
    
    # Build frontend
    cd frontend
    npm install
    NEXT_PUBLIC_API_URL=$API_URL npm run build
    
    # Upload to S3
    aws s3 sync out/ s3://$BUCKET_NAME --profile $AWS_PROFILE --region $AWS_REGION --delete
    
    # Invalidate CloudFront cache
    aws cloudfront create-invalidation \
        --profile $AWS_PROFILE \
        --distribution-id $DISTRIBUTION_ID \
        --paths "/*"
    
    cd ..
    log "Frontend deployed successfully."
}

# Get deployment information
get_deployment_info() {
    log "Getting deployment information..."
    
    # Get website URL
    WEBSITE_URL=$(aws cloudformation describe-stacks \
        --profile $AWS_PROFILE \
        --region $AWS_REGION \
        --stack-name "${ENVIRONMENT_NAME}-frontend" \
        --query "Stacks[0].Outputs[?OutputKey=='WebsiteURL'].OutputValue" \
        --output text)
    
    # Get API URL
    API_URL=$(aws cloudformation describe-stacks \
        --profile $AWS_PROFILE \
        --region $AWS_REGION \
        --stack-name "${ENVIRONMENT_NAME}-ecs" \
        --query "Stacks[0].Outputs[?OutputKey=='LoadBalancerURL'].OutputValue" \
        --output text)
    
    echo -e "\n${GREEN}=== Deployment Complete ===${NC}"
    echo -e "${BLUE}Website URL:${NC} $WEBSITE_URL"
    echo -e "${BLUE}API URL:${NC} $API_URL"
    echo -e "${BLUE}Environment:${NC} $ENVIRONMENT_NAME"
    echo -e "${BLUE}Region:${NC} $AWS_REGION"
    echo ""
    echo -e "${YELLOW}Note: It may take a few minutes for all services to be fully available.${NC}"
}

# Main deployment function
main() {
    log "Starting deployment of microservices application..."
    
    check_prerequisites
    build_and_push_images
    deploy_infrastructure
    deploy_frontend
    get_deployment_info
    
    log "Deployment completed successfully!"
}

# Parse command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "destroy")
        log "Destroying infrastructure..."
        for stack in "${ENVIRONMENT_NAME}-frontend" "${ENVIRONMENT_NAME}-ecs" "${ENVIRONMENT_NAME}-database" "${ENVIRONMENT_NAME}-network"; do
            log "Deleting stack: $stack"
            aws cloudformation delete-stack --profile $AWS_PROFILE --region $AWS_REGION --stack-name $stack
        done
        log "Infrastructure destruction initiated."
        ;;
    "status")
        log "Getting stack status..."
        for stack in "${ENVIRONMENT_NAME}-network" "${ENVIRONMENT_NAME}-database" "${ENVIRONMENT_NAME}-ecs" "${ENVIRONMENT_NAME}-frontend"; do
            STATUS=$(aws cloudformation describe-stacks --profile $AWS_PROFILE --region $AWS_REGION --stack-name $stack --query "Stacks[0].StackStatus" --output text 2>/dev/null || echo "NOT_FOUND")
            echo -e "${BLUE}$stack:${NC} $STATUS"
        done
        ;;
    *)
        echo "Usage: $0 [deploy|destroy|status]"
        echo "  deploy  - Deploy the complete application"
        echo "  destroy - Destroy all infrastructure"
        echo "  status  - Show stack status"
        exit 1
        ;;
esac
