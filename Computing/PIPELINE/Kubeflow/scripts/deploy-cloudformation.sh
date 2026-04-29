#!/bin/bash

# CloudFormation deployment script for BERT Kubeflow pipeline

set -e

# Configuration
STACK_NAME="bert-kubeflow-stack"
TEMPLATE_FILE="cloudformation/kubeflow-stack.yaml"
REGION="us-west-2"
CLUSTER_NAME="kubeflow-cluster"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check AWS CLI
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI not found. Please install it first."
        exit 1
    fi
    
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Run 'aws configure' first."
        exit 1
    fi
}

# Deploy stack
deploy_stack() {
    log_info "Deploying CloudFormation stack: $STACK_NAME"
    
    aws cloudformation deploy \
        --template-file "$TEMPLATE_FILE" \
        --stack-name "$STACK_NAME" \
        --parameter-overrides \
            ClusterName="$CLUSTER_NAME" \
            NodeInstanceType=m5.large \
            DesiredCapacity=2 \
            MaxCapacity=4 \
            MinCapacity=1 \
        --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
        --region "$REGION" \
        --tags \
            Project=bert-kubeflow \
            Environment=dev
    
    log_success "Stack deployment completed"
}

# Get stack outputs
get_outputs() {
    log_info "Getting stack outputs..."
    
    aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs' \
        --output table
}

# Update kubeconfig
update_kubeconfig() {
    log_info "Updating kubeconfig..."
    
    aws eks update-kubeconfig \
        --region "$REGION" \
        --name "$CLUSTER_NAME"
    
    log_success "kubeconfig updated"
}

# Delete stack
delete_stack() {
    log_warning "Deleting CloudFormation stack: $STACK_NAME"
    
    read -p "Are you sure you want to delete the stack? (y/N): " confirm
    if [[ $confirm == "y" || $confirm == "Y" ]]; then
        aws cloudformation delete-stack \
            --stack-name "$STACK_NAME" \
            --region "$REGION"
        
        log_info "Waiting for stack deletion to complete..."
        aws cloudformation wait stack-delete-complete \
            --stack-name "$STACK_NAME" \
            --region "$REGION"
        
        log_success "Stack deleted successfully"
    else
        log_info "Stack deletion cancelled"
    fi
}

# Check stack status
check_status() {
    log_info "Checking stack status..."
    
    aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].{StackName:StackName,Status:StackStatus,CreationTime:CreationTime}' \
        --output table
}

# Main function
main() {
    check_aws_cli
    
    case "${1:-deploy}" in
        "deploy")
            deploy_stack
            get_outputs
            update_kubeconfig
            ;;
        "delete")
            delete_stack
            ;;
        "status")
            check_status
            ;;
        "outputs")
            get_outputs
            ;;
        "kubeconfig")
            update_kubeconfig
            ;;
        "help"|"-h"|"--help")
            echo "Usage: $0 [deploy|delete|status|outputs|kubeconfig|help]"
            echo ""
            echo "Commands:"
            echo "  deploy      Deploy the CloudFormation stack (default)"
            echo "  delete      Delete the CloudFormation stack"
            echo "  status      Check stack status"
            echo "  outputs     Show stack outputs"
            echo "  kubeconfig  Update kubeconfig for EKS cluster"
            echo "  help        Show this help message"
            ;;
        *)
            log_error "Unknown command: $1"
            echo "Run '$0 help' for usage information"
            exit 1
            ;;
    esac
}

main "$@"
