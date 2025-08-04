#!/bin/bash
# AWS Setup and Deployment Script for Dagster BERT Pipeline

set -euo pipefail

# Configuration
REGION=${AWS_DEFAULT_REGION:-us-east-1}
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO_NAME="dagster-bert-pipeline"
STACK_NAME="dagster-bert-pipeline"
CLUSTER_NAME="dagster-bert-pipeline"

echo "=== Dagster BERT Pipeline AWS Deployment ==="
echo "Region: $REGION"
echo "Account ID: $ACCOUNT_ID"
echo "ECR Repository: $ECR_REPO_NAME"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if AWS CLI is configured
check_aws_config() {
    log_info "Checking AWS CLI configuration..."
    
    if ! aws sts get-caller-identity > /dev/null 2>&1; then
        log_error "AWS CLI not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    log_info "AWS CLI configured successfully"
}

# Function to create ECR repository
create_ecr_repo() {
    log_info "Creating ECR repository..."
    
    if aws ecr describe-repositories --repository-names $ECR_REPO_NAME --region $REGION > /dev/null 2>&1; then
        log_warn "ECR repository $ECR_REPO_NAME already exists"
    else
        aws ecr create-repository \
            --repository-name $ECR_REPO_NAME \
            --region $REGION \
            --image-scanning-configuration scanOnPush=true
        log_info "ECR repository created: $ECR_REPO_NAME"
    fi
}

# Function to build and push Docker image
build_and_push_image() {
    log_info "Building and pushing Docker image..."
    
    # Login to ECR
    aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com
    
    # Build image
    docker build -t $ECR_REPO_NAME .
    
    # Tag image
    docker tag $ECR_REPO_NAME:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPO_NAME:latest
    
    # Push image
    docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPO_NAME:latest
    
    log_info "Docker image pushed successfully"
}

# Function to deploy CloudFormation stack
deploy_infrastructure() {
    log_info "Deploying infrastructure with CloudFormation..."
    
    # Get default VPC and subnets
    VPC_ID=$(aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query "Vpcs[0].VpcId" --output text --region $REGION)
    SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query "Subnets[0:2].SubnetId" --output text --region $REGION | tr '\t' ',')
    
    if [ "$VPC_ID" == "None" ] || [ -z "$SUBNET_IDS" ]; then
        log_error "Could not find default VPC or subnets. Please specify VPC and subnet IDs."
        exit 1
    fi
    
    log_info "Using VPC: $VPC_ID"
    log_info "Using Subnets: $SUBNET_IDS"
    
    # Deploy CloudFormation stack
    aws cloudformation deploy \
        --template-file aws_config/cloudformation-template.yaml \
        --stack-name $STACK_NAME \
        --parameter-overrides \
            VpcId=$VPC_ID \
            SubnetIds=$SUBNET_IDS \
            ECRRepository=$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPO_NAME \
        --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
        --region $REGION
    
    log_info "Infrastructure deployed successfully"
}

# Function to register ECS task definition
register_task_definition() {
    log_info "Registering ECS task definition..."
    
    # Update task definition with actual values
    sed -e "s/ACCOUNT_ID/$ACCOUNT_ID/g" \
        -e "s/REGION/$REGION/g" \
        aws_config/ecs-task-definition.json > /tmp/ecs-task-definition.json
    
    aws ecs register-task-definition \
        --cli-input-json file:///tmp/ecs-task-definition.json \
        --region $REGION
    
    log_info "ECS task definition registered"
}

# Function to create ECS service
create_ecs_service() {
    log_info "Creating ECS service..."
    
    # Get subnet and security group from CloudFormation outputs
    SUBNET_1=$(echo $SUBNET_IDS | cut -d',' -f1)
    SECURITY_GROUP=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query "Stacks[0].Outputs[?OutputKey=='DagsterECSSecurityGroup'].OutputValue" \
        --output text)
    
    # Create service
    aws ecs create-service \
        --cluster $CLUSTER_NAME \
        --service-name dagster-bert-service \
        --task-definition dagster-bert-pipeline:1 \
        --desired-count 1 \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_1],securityGroups=[$SECURITY_GROUP],assignPublicIp=ENABLED}" \
        --region $REGION
    
    log_info "ECS service created"
}

# Function to setup environment variables
setup_environment() {
    log_info "Setting up environment variables..."
    
    # Export environment variables for Dagster
    export DAGSTER_ECS_CLUSTER=$CLUSTER_NAME
    export DAGSTER_S3_BUCKET="dagster-bert-pipeline-$ACCOUNT_ID-$REGION"
    export AWS_DEFAULT_REGION=$REGION
    
    # Create .env file for local development
    cat > .env << EOF
# AWS Configuration
AWS_DEFAULT_REGION=$REGION
AWS_ACCOUNT_ID=$ACCOUNT_ID

# Dagster Configuration
DAGSTER_ECS_CLUSTER=$CLUSTER_NAME
DAGSTER_S3_BUCKET=dagster-bert-pipeline-$ACCOUNT_ID-$REGION
DAGSTER_HOME=./dagster_home

# Database Configuration (will be populated from Secrets Manager)
DAGSTER_PG_USERNAME=dagster
DAGSTER_PG_HOST=
DAGSTER_PG_DB=dagster
DAGSTER_PG_PASSWORD=

# ECR Configuration
ECR_REPOSITORY=$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPO_NAME
EOF
    
    log_info "Environment variables configured"
}

# Function to verify deployment
verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check if ECS service is running
    SERVICE_STATUS=$(aws ecs describe-services \
        --cluster $CLUSTER_NAME \
        --services dagster-bert-service \
        --region $REGION \
        --query "services[0].status" \
        --output text)
    
    if [ "$SERVICE_STATUS" == "ACTIVE" ]; then
        log_info "ECS service is active"
    else
        log_warn "ECS service status: $SERVICE_STATUS"
    fi
    
    # Get load balancer URL (if available)
    ALB_DNS=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query "Stacks[0].Outputs[?OutputKey=='LoadBalancerDNS'].OutputValue" \
        --output text 2>/dev/null || echo "Not available")
    
    if [ "$ALB_DNS" != "Not available" ] && [ "$ALB_DNS" != "None" ]; then
        log_info "Application Load Balancer: http://$ALB_DNS"
    fi
    
    log_info "Deployment verification completed"
}

# Main execution
main() {
    case "${1:-all}" in
        "check")
            check_aws_config
            ;;
        "ecr")
            check_aws_config
            create_ecr_repo
            ;;
        "build")
            check_aws_config
            create_ecr_repo
            build_and_push_image
            ;;
        "infra")
            check_aws_config
            deploy_infrastructure
            ;;
        "ecs")
            check_aws_config
            register_task_definition
            create_ecs_service
            ;;
        "env")
            setup_environment
            ;;
        "verify")
            verify_deployment
            ;;
        "all")
            check_aws_config
            create_ecr_repo
            build_and_push_image
            deploy_infrastructure
            register_task_definition
            create_ecs_service
            setup_environment
            verify_deployment
            ;;
        "clean")
            log_warn "Cleaning up AWS resources..."
            aws ecs delete-service --cluster $CLUSTER_NAME --service dagster-bert-service --force --region $REGION || true
            aws cloudformation delete-stack --stack-name $STACK_NAME --region $REGION || true
            aws ecr delete-repository --repository-name $ECR_REPO_NAME --force --region $REGION || true
            log_info "Cleanup completed"
            ;;
        *)
            echo "Usage: $0 {check|ecr|build|infra|ecs|env|verify|all|clean}"
            echo ""
            echo "Commands:"
            echo "  check  - Check AWS CLI configuration"
            echo "  ecr    - Create ECR repository"
            echo "  build  - Build and push Docker image"
            echo "  infra  - Deploy infrastructure"
            echo "  ecs    - Register task definition and create service"
            echo "  env    - Setup environment variables"
            echo "  verify - Verify deployment"
            echo "  all    - Run complete deployment"
            echo "  clean  - Clean up all AWS resources"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
