#!/bin/bash

# BERT Kubeflow Pipeline Setup Script
# This script sets up the complete environment for BERT fine-tuning with Kubeflow

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_NAME="bert-kubeflow-env"
CLUSTER_NAME="kubeflow-cluster"
AWS_REGION="us-west-2"

# Functions
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

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 is not installed or not in PATH"
        return 1
    fi
    return 0
}

# Main setup function
main() {
    log_info "Starting BERT Kubeflow Pipeline Setup..."
    
    # Check prerequisites
    log_info "Checking prerequisites..."
    
    required_commands=("python3" "pip3" "docker" "kubectl" "aws" "terraform")
    for cmd in "${required_commands[@]}"; do
        if ! check_command "$cmd"; then
            log_error "Please install $cmd before continuing"
            exit 1
        fi
    done
    
    log_success "All required commands are available"
    
    # Setup Python virtual environment
    setup_python_environment
    
    # Setup Docker
    setup_docker
    
    # Setup AWS
    setup_aws
    
    # Setup local Kubeflow (optional)
    read -p "Do you want to setup local Kubeflow with Minikube? (y/N): " setup_local
    if [[ $setup_local == "y" || $setup_local == "Y" ]]; then
        setup_local_kubeflow
    fi
    
    # Setup AWS infrastructure
    read -p "Do you want to deploy AWS infrastructure with Terraform? (y/N): " deploy_aws
    if [[ $deploy_aws == "y" || $deploy_aws == "Y" ]]; then
        setup_aws_infrastructure
    fi
    
    # Final instructions
    show_final_instructions
    
    log_success "Setup completed successfully!"
}

setup_python_environment() {
    log_info "Setting up Python virtual environment..."
    
    cd "$PROJECT_ROOT"
    
    # Create virtual environment
    if [ ! -d "$VENV_NAME" ]; then
        python3 -m venv "$VENV_NAME"
        log_success "Virtual environment created: $VENV_NAME"
    else
        log_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source "$VENV_NAME/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        log_success "Installed requirements.txt"
    fi
    
    if [ -f "requirements-api.txt" ]; then
        pip install -r requirements-api.txt
        log_success "Installed requirements-api.txt"
    fi
    
    # Install Kubeflow SDK
    pip install kfp==1.8.22 kubernetes==24.2.0
    log_success "Installed Kubeflow SDK"
    
    # Create activation script
    cat > activate.sh << 'EOF'
#!/bin/bash
source bert-kubeflow-env/bin/activate
echo "Python virtual environment activated"
echo "Available commands:"
echo "  python src/bert_fine_tuning.py  - Run local training"
echo "  python api.py                   - Start API server"
echo "  python pipeline/bert_pipeline.py - Compile Kubeflow pipeline"
EOF
    chmod +x activate.sh
    
    log_success "Python environment setup completed"
}

setup_docker() {
    log_info "Configuring Docker..."
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Add user to docker group if not already
    if ! groups "$USER" | grep -q docker; then
        log_warning "Adding $USER to docker group. You may need to log out and back in."
        sudo usermod -aG docker "$USER"
    fi
    
    # Build local images
    log_info "Building Docker images..."
    
    # Build training image
    docker build -t bert-training -f Dockerfile.training . || {
        log_warning "Dockerfile.training not found, creating one..."
        create_training_dockerfile
        docker build -t bert-training -f Dockerfile.training .
    }
    
    # Build serving image
    docker build -t bert-serving .
    
    log_success "Docker setup completed"
}

create_training_dockerfile() {
    cat > Dockerfile.training << 'EOF'
# Training Dockerfile for BERT fine-tuning
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY data/ ./data/ 2>/dev/null || true

# Set environment variables
ENV PYTHONPATH=/app
ENV TRANSFORMERS_CACHE=/app/cache

# Create directories
RUN mkdir -p /app/models /app/cache /app/data

# Default command
CMD ["python", "src/bert_fine_tuning.py"]
EOF
}

setup_aws() {
    log_info "Setting up AWS configuration..."
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_warning "AWS credentials not configured"
        log_info "Please run: aws configure"
        log_info "Or set environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY"
        
        read -p "Configure AWS now? (y/N): " configure_aws
        if [[ $configure_aws == "y" || $configure_aws == "Y" ]]; then
            aws configure
        else
            log_warning "Skipping AWS setup. Configure manually later."
            return
        fi
    fi
    
    # Get AWS account info
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    log_info "AWS Account ID: $AWS_ACCOUNT_ID"
    
    # Create ECR repository if it doesn't exist
    if ! aws ecr describe-repositories --repository-names bert-pipeline --region "$AWS_REGION" &> /dev/null; then
        log_info "Creating ECR repository..."
        aws ecr create-repository \
            --repository-name bert-pipeline \
            --region "$AWS_REGION" \
            --image-scanning-configuration scanOnPush=true
        log_success "ECR repository created"
    else
        log_info "ECR repository already exists"
    fi
    
    # Update environment file
    update_env_file
    
    log_success "AWS setup completed"
}

setup_local_kubeflow() {
    log_info "Setting up local Kubeflow with Minikube..."
    
    # Check if Minikube is installed
    if ! check_command "minikube"; then
        log_info "Installing Minikube..."
        curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
        sudo install minikube-linux-amd64 /usr/local/bin/minikube
        rm minikube-linux-amd64
    fi
    
    # Start Minikube
    log_info "Starting Minikube..."
    minikube start --cpus=4 --memory=8192 --disk-size=20g --driver=docker
    
    # Enable addons
    minikube addons enable ingress
    minikube addons enable dashboard
    
    # Install Kubeflow Pipelines
    log_info "Installing Kubeflow Pipelines..."
    export PIPELINE_VERSION=1.8.5
    kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=$PIPELINE_VERSION"
    kubectl wait --for condition=established --timeout=60s crd/applications.app.k8s.io
    kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/dev?ref=$PIPELINE_VERSION"
    
    # Wait for deployment
    log_info "Waiting for Kubeflow Pipelines to be ready..."
    kubectl wait --for=condition=available --timeout=600s deployment/ml-pipeline-ui -n kubeflow
    
    # Create port-forward script
    cat > start-kubeflow-ui.sh << 'EOF'
#!/bin/bash
echo "Starting Kubeflow UI port-forward..."
echo "Access Kubeflow at: http://localhost:8080"
kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80
EOF
    chmod +x start-kubeflow-ui.sh
    
    log_success "Local Kubeflow setup completed"
    log_info "Run './start-kubeflow-ui.sh' to access Kubeflow UI"
}

setup_aws_infrastructure() {
    log_info "Setting up AWS infrastructure with Terraform..."
    
    cd "$PROJECT_ROOT/terraform"
    
    # Initialize Terraform
    terraform init
    
    # Plan deployment
    log_info "Planning Terraform deployment..."
    terraform plan -var="cluster_name=$CLUSTER_NAME" -var="aws_region=$AWS_REGION"
    
    # Apply deployment
    read -p "Apply Terraform configuration? (y/N): " apply_terraform
    if [[ $apply_terraform == "y" || $apply_terraform == "Y" ]]; then
        terraform apply -var="cluster_name=$CLUSTER_NAME" -var="aws_region=$AWS_REGION" -auto-approve
        
        # Update kubeconfig
        aws eks update-kubeconfig --region "$AWS_REGION" --name "$CLUSTER_NAME"
        
        # Install Kubeflow on EKS
        install_kubeflow_aws
        
        log_success "AWS infrastructure deployed"
    else
        log_info "Skipping Terraform apply"
    fi
    
    cd "$PROJECT_ROOT"
}

install_kubeflow_aws() {
    log_info "Installing Kubeflow on AWS EKS..."
    
    # Clone Kubeflow manifests
    if [ ! -d "kubeflow-manifests" ]; then
        git clone https://github.com/awslabs/kubeflow-manifests.git
    fi
    
    cd kubeflow-manifests
    
    # Install Kubeflow Pipelines standalone
    log_info "Installing Kubeflow Pipelines..."
    make deploy-kubeflow-pipelines INSTALLATION_OPTION=kustomize
    
    # Wait for deployment
    kubectl wait --for=condition=available --timeout=600s deployment/ml-pipeline-ui -n kubeflow
    
    cd "$PROJECT_ROOT"
    log_success "Kubeflow installed on AWS"
}

update_env_file() {
    local env_file="$PROJECT_ROOT/.env"
    
    cat > "$env_file" << EOF
# Model Configuration
MODEL_NAME=bert-base-uncased
MAX_LENGTH=128
BATCH_SIZE=16
LEARNING_RATE=2e-5
NUM_EPOCHS=3

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# AWS Configuration
AWS_REGION=$AWS_REGION
AWS_ACCOUNT_ID=$AWS_ACCOUNT_ID
ECR_REPOSITORY=bert-pipeline
EKS_CLUSTER_NAME=$CLUSTER_NAME

# Kubeflow Configuration
KUBEFLOW_NAMESPACE=kubeflow
PIPELINE_NAME=bert-training-pipeline

# Docker Configuration
DOCKER_REGISTRY=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
EOF
    
    log_success "Environment file updated: $env_file"
}

setup_iptables() {
    log_info "Configuring iptables for local development..."
    
    # Allow incoming traffic on required ports
    sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT  # FastAPI
    sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT  # Kubeflow UI
    sudo iptables -A INPUT -p tcp --dport 3000 -j ACCEPT  # Additional services
    
    # Allow Docker bridge network
    sudo iptables -A INPUT -i docker0 -j ACCEPT
    sudo iptables -A FORWARD -i docker0 -o docker0 -j ACCEPT
    
    # Save iptables rules
    sudo mkdir -p /etc/iptables
    sudo iptables-save | sudo tee /etc/iptables/rules.v4 > /dev/null
    
    log_success "iptables configured"
}

show_final_instructions() {
    log_info "Setup completed! Here's what you can do next:"
    
    echo ""
    echo "🔧 DEVELOPMENT COMMANDS:"
    echo "  source activate.sh                    # Activate Python environment"
    echo "  python src/bert_fine_tuning.py       # Run local training"
    echo "  python api.py                        # Start API server"
    echo "  python pipeline/bert_pipeline.py     # Compile Kubeflow pipeline"
    echo ""
    echo "🐳 DOCKER COMMANDS:"
    echo "  docker run -p 8000:8000 bert-serving # Run serving container"
    echo "  docker run bert-training              # Run training container"
    echo ""
    echo "☁️  AWS COMMANDS:"
    echo "  aws eks update-kubeconfig --region $AWS_REGION --name $CLUSTER_NAME"
    echo "  kubectl get pods -n kubeflow"
    echo ""
    echo "🚀 KUBEFLOW ACCESS:"
    echo "  Local:  ./start-kubeflow-ui.sh       # Port-forward to localhost:8080"
    echo "  AWS:    kubectl port-forward -n istio-system svc/istio-ingressgateway 8080:80"
    echo ""
    echo "📚 NEXT STEPS:"
    echo "  1. Activate Python environment: source activate.sh"
    echo "  2. Test local training: python src/bert_fine_tuning.py"
    echo "  3. Compile pipeline: python pipeline/bert_pipeline.py"
    echo "  4. Upload pipeline to Kubeflow UI"
    echo ""
}

# Script options
case "${1:-}" in
    "python")
        setup_python_environment
        ;;
    "docker")
        setup_docker
        ;;
    "aws")
        setup_aws
        ;;
    "local")
        setup_local_kubeflow
        ;;
    "terraform")
        setup_aws_infrastructure
        ;;
    "iptables")
        setup_iptables
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [python|docker|aws|local|terraform|iptables|help]"
        echo ""
        echo "Options:"
        echo "  python     Setup Python virtual environment only"
        echo "  docker     Setup Docker only"
        echo "  aws        Setup AWS configuration only"
        echo "  local      Setup local Kubeflow only"
        echo "  terraform  Deploy AWS infrastructure only"
        echo "  iptables   Configure iptables only"
        echo "  help       Show this help message"
        echo ""
        echo "Run without arguments for interactive setup"
        ;;
    *)
        main
        ;;
esac
