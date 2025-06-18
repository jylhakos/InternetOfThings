#!/bin/bash

# Deployment script for Go Fargate application
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_requirements() {
    print_status "Checking requirements..."
    
    command -v aws >/dev/null 2>&1 || { print_error "AWS CLI is required but not installed. Aborting."; exit 1; }
    command -v docker >/dev/null 2>&1 || { print_error "Docker is required but not installed. Aborting."; exit 1; }
    command -v terraform >/dev/null 2>&1 || { print_error "Terraform is required but not installed. Aborting."; exit 1; }
    
    print_status "All requirements satisfied."
}

# Initialize Terraform
init_terraform() {
    print_status "Initializing Terraform..."
    cd terraform
    terraform init
    cd ..
}

# Deploy infrastructure
deploy_infrastructure() {
    print_status "Deploying infrastructure with Terraform..."
    cd terraform
    
    # Check if terraform.tfvars exists
    if [ ! -f "terraform.tfvars" ]; then
        print_error "terraform.tfvars not found. Please copy terraform.tfvars.example to terraform.tfvars and configure it."
        exit 1
    fi
    
    terraform plan -out=tfplan
    terraform apply tfplan
    cd ..
}

# Build and push Docker image
build_and_push_image() {
    print_status "Building and pushing Docker image..."
    
    # Get values from Terraform outputs
    cd terraform
    AWS_REGION=$(terraform output -raw aws_region 2>/dev/null || echo "us-east-1")
    ECR_REPO_URL=$(terraform output -raw ecr_repository_url)
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    cd ..
    
    # Login to ECR
    print_status "Logging in to ECR..."
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO_URL
    
    # Build image
    print_status "Building Docker image..."
    docker build -t go-fargate-app .
    
    # Tag image
    print_status "Tagging image..."
    docker tag go-fargate-app:latest $ECR_REPO_URL:latest
    
    # Push image
    print_status "Pushing image to ECR..."
    docker push $ECR_REPO_URL:latest
}

# Update ECS service
update_ecs_service() {
    print_status "Updating ECS service..."
    cd terraform
    
    ECS_CLUSTER=$(terraform output -raw ecs_cluster_name)
    ECS_SERVICE=$(terraform output -raw ecs_service_name)
    AWS_REGION=$(terraform output -raw aws_region 2>/dev/null || echo "us-east-1")
    
    # Force new deployment
    aws ecs update-service \
        --cluster $ECS_CLUSTER \
        --service $ECS_SERVICE \
        --force-new-deployment \
        --region $AWS_REGION
    
    print_status "Waiting for service to stabilize..."
    aws ecs wait services-stable \
        --cluster $ECS_CLUSTER \
        --services $ECS_SERVICE \
        --region $AWS_REGION
    
    cd ..
}

# Show deployment status
show_status() {
    print_status "Deployment completed successfully!"
    
    cd terraform
    APPLICATION_URL=$(terraform output -raw application_url)
    ALB_DNS=$(terraform output -raw alb_dns_name)
    cd ..
    
    echo ""
    echo "Application Details:"
    echo "==================="
    echo "Application URL: $APPLICATION_URL"
    echo "Load Balancer DNS: $ALB_DNS"
    echo ""
    echo "You can monitor your application using:"
    echo "- AWS Console -> ECS"
    echo "- AWS Console -> CloudWatch"
    echo "- Application logs in CloudWatch Logs"
}

# Main deployment function
main() {
    print_status "Starting deployment of Go Fargate application..."
    
    check_requirements
    init_terraform
    deploy_infrastructure
    build_and_push_image
    update_ecs_service
    show_status
    
    print_status "Deployment completed successfully!"
}

# Show usage
usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  deploy     Deploy the complete infrastructure and application"
    echo "  image      Build and push Docker image only"
    echo "  terraform  Deploy infrastructure only"
    echo "  update     Update ECS service only"
    echo "  destroy    Destroy all infrastructure"
    echo "  status     Show current deployment status"
    echo ""
}

# Handle command line arguments
case "${1:-deploy}" in
    deploy)
        main
        ;;
    image)
        check_requirements
        build_and_push_image
        ;;
    terraform)
        check_requirements
        init_terraform
        deploy_infrastructure
        ;;
    update)
        check_requirements
        update_ecs_service
        ;;
    destroy)
        print_warning "This will destroy all infrastructure. Are you sure? (y/N)"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            cd terraform
            terraform destroy
            cd ..
        else
            print_status "Destroy cancelled."
        fi
        ;;
    status)
        show_status
        ;;
    *)
        usage
        exit 1
        ;;
esac
