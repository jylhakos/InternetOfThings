# BERT ML pipeline with Kubeflow

A document for building, deploying, and running BERT fine-tuning pipelines using Kubeflow on local Linux environments and Amazon AWS or Google GCP.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Local Development Setup](#local-development-setup)
4. [Kubeflow Pipeline Components](#kubeflow-pipeline-components)
5. [Local Kubeflow Setup](#local-kubeflow-setup)
6. [AWS Deployment](#aws-deployment)
7. [Pipeline Execution](#pipeline-execution)
8. [API Gateway and Load Balancing](#api-gateway-and-load-balancing)
9. [Monitoring and Logging](#monitoring-and-logging)
10. [Troubleshooting](#troubleshooting)
11. [Kubeflow on Google GCP](#kubeflow-on-google-gcp)

## Overview

This project implements a complete ML pipeline for BERT model fine-tuning with the following stages:

1. **Data Preprocessing** - Text data preparation and tokenization
2. **Model Fine-tuning** - BERT model training on custom dataset
3. **Model Evaluation** - Performance metrics and validation
4. **Model Deployment** - Containerized model serving
5. **Inference API** - FastAPI endpoint for real-time predictions

## Prerequisites

### System requirements
- **OS**: Linux/Debian (Ubuntu 20.04+ recommended)
- **RAM**: Minimum 8GB (16GB+ recommended for GPU training)
- **Storage**: 20GB+ free space
- **Python**: 3.8+
- **Docker**: 20.10+
- **kubectl**: 1.20+

### Required tools

#### 1. Install Docker
```bash
# Remove old versions
sudo apt-get remove docker docker-engine docker.io containerd runc

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### 2. Install kubectl
```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

#### 3. Install AWS CLI
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

#### 4. Install Terraform (for Infrastructure as Code)
```bash
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform
```

## Local development

### 1. Create Python Virtual Environment

```bash
# Clone the repository
git clone <your-repository-url>
cd "Artificial Intelligence/PIPELINE/Kubeflow"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
pip install -r requirements-api.txt

# Install additional Kubeflow SDK
pip install kfp==1.8.22 kubernetes==24.2.0
```

### 2. Environment configuration

Create `.env` file for local development:
```bash
cat > .env << EOF
# Model Configuration
MODEL_NAME=bert-base-uncased
MAX_LENGTH=128
BATCH_SIZE=16
LEARNING_RATE=2e-5
NUM_EPOCHS=3

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# AWS Configuration (for deployment)
AWS_REGION=us-west-2
AWS_ACCOUNT_ID=your-account-id
ECR_REPOSITORY=bert-pipeline
EKS_CLUSTER_NAME=kubeflow-cluster

# Kubeflow Configuration
KUBEFLOW_NAMESPACE=kubeflow
PIPELINE_NAME=bert-training-pipeline
EOF
```

### 3. Test local environment

```bash
# Test BERT fine-tuning locally
python src/bert_fine_tuning.py

# Test API locally
python api.py

# Test in another terminal
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"text": "This is a great product!", "return_confidence": true}'
```

## 🔧 Kubeflow pipeline components

### Pipeline architecture

The pipeline consists of four main components:

1. **Data Component** - Data preprocessing and validation
2. **Training Component** - BERT model fine-tuning
3. **Evaluation Component** - Model performance assessment
4. **Deployment Component** - Model serving setup

##  Local Kubeflow setup

### 1. Install Minikube (for local Kubernetes)

```bash
# Install Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --disk-size=20g --driver=docker

# Enable necessary addons
minikube addons enable ingress
minikube addons enable dashboard
```

### 2. Install Kubeflow pipelines standalone

```bash
# Download Kubeflow Pipelines manifests
export PIPELINE_VERSION=1.8.5
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=$PIPELINE_VERSION"
kubectl wait --for condition=established --timeout=60s crd/applications.app.k8s.io
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/dev?ref=$PIPELINE_VERSION"

# Wait for deployment
kubectl wait --for=condition=available --timeout=600s deployment/ml-pipeline-ui -n kubeflow

# Port forward to access UI
kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80 &
```

### 3. Access Kubeflow dashboard

Open your browser and navigate to: `http://localhost:8080`

## ☁️ Amazon AWS deployment

### 1. Configure Amazon AWS credentials

```bash
# Configure AWS CLI
aws configure
# Enter your AWS Access Key ID, Secret Access Key, Region, and Output format

# Verify configuration
aws sts get-caller-identity
```

### 2. Create Amazon EKS cluster using Terraform

Create `terraform/main.tf`:

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "kubeflow-cluster"
}

# VPC for EKS
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  
  name = "${var.cluster_name}-vpc"
  cidr = "10.0.0.0/16"
  
  azs             = ["${var.aws_region}a", "${var.aws_region}b", "${var.aws_region}c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  
  enable_nat_gateway = true
  enable_vpn_gateway = true
  
  tags = {
    Terraform = "true"
    Environment = "dev"
  }
}

# EKS Cluster
module "eks" {
  source = "terraform-aws-modules/eks/aws"
  
  cluster_name    = var.cluster_name
  cluster_version = "1.27"
  
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets
  
  eks_managed_node_groups = {
    main = {
      desired_capacity = 2
      max_capacity     = 4
      min_capacity     = 1
      
      instance_types = ["m5.large"]
      
      k8s_labels = {
        Environment = "dev"
        Application = "kubeflow"
      }
    }
  }
}

# ECR Repository for Docker images
resource "aws_ecr_repository" "bert_pipeline" {
  name                 = "bert-pipeline"
  image_tag_mutability = "MUTABLE"
  
  image_scanning_configuration {
    scan_on_push = true
  }
}

# Output values
output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks.cluster_endpoint
}

output "cluster_security_group_id" {
  description = "Security group ids attached to the cluster control plane"
  value       = module.eks.cluster_security_group_id
}

output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.bert_pipeline.repository_url
}
```

Deploy infrastructure:

```bash
# Initialize and apply Terraform
cd terraform
terraform init
terraform plan
terraform apply

# Update kubeconfig
aws eks update-kubeconfig --region us-west-2 --name kubeflow-cluster
```

### 3. Install Kubeflow on Amazon EKS

```bash
# Clone Kubeflow manifests
git clone https://github.com/awslabs/kubeflow-manifests.git
cd kubeflow-manifests

# Install Kubeflow (choose one option)

# Option 1: Full Kubeflow deployment
make deploy-kubeflow INSTALLATION_OPTION=kustomize DEPLOYMENT_OPTION=vanilla

# Option 2: Standalone Pipelines only
make deploy-kubeflow-pipelines INSTALLATION_OPTION=kustomize
```

### 4. Configure AWS Load Balancer

Create `aws-load-balancer.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: kubeflow-gateway-nlb
  namespace: istio-system
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
    service.beta.kubernetes.io/aws-load-balancer-scheme: "internet-facing"
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8080
    protocol: TCP
    name: http
  selector:
    istio: ingressgateway
```

Apply the configuration:
```bash
kubectl apply -f aws-load-balancer.yaml
```

## Pipeline execution

### 1. Build and Push Docker Images

```bash
# Login to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-west-2.amazonaws.com

# Build and push training image
docker build -t bert-training -f Dockerfile.training .
docker tag bert-training:latest <account-id>.dkr.ecr.us-west-2.amazonaws.com/bert-pipeline:training
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/bert-pipeline:training

# Build and push serving image
docker build -t bert-serving -f Dockerfile .
docker tag bert-serving:latest <account-id>.dkr.ecr.us-west-2.amazonaws.com/bert-pipeline:serving
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/bert-pipeline:serving
```

### 2. Create and run pipeline

```bash
# Compile and run the pipeline
python pipeline/bert_pipeline.py

# Monitor pipeline execution
kubectl get pods -n kubeflow
kubectl logs -f <pipeline-pod-name> -n kubeflow
```

## 🌐 API Gateway and AWS Load Balancing

### 1. AWS API Gateway Setup

Create `api-gateway.tf`:

```hcl
# API Gateway
resource "aws_api_gateway_rest_api" "bert_api" {
  name        = "bert-inference-api"
  description = "API Gateway for BERT model inference"
}

# API Gateway VPC Link
resource "aws_api_gateway_vpc_link" "bert_vpc_link" {
  name        = "bert-vpc-link"
  target_arns = [aws_lb.bert_nlb.arn]
}

# Network Load Balancer
resource "aws_lb" "bert_nlb" {
  name               = "bert-nlb"
  internal           = false
  load_balancer_type = "network"
  subnets            = module.vpc.public_subnets

  enable_deletion_protection = false

  tags = {
    Environment = "production"
  }
}
```

### 2. Local iptables configuration

Create `scripts/setup-iptables.sh`:

```bash
#!/bin/bash
# Local iptables configuration for development

# Allow incoming traffic on port 8000 (FastAPI)
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT

# Allow incoming traffic on port 8080 (Kubeflow UI)
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT

# Allow Docker bridge network
sudo iptables -A INPUT -i docker0 -j ACCEPT
sudo iptables -A FORWARD -i docker0 -o docker0 -j ACCEPT

# Save iptables rules
sudo iptables-save > /etc/iptables/rules.v4

echo "iptables rules configured successfully"
```

## Monitoring and logging

### 1. Set up Prometheus and Grafana

```bash
# Add Helm repositories
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace

# Install Grafana
helm install grafana grafana/grafana -n monitoring
```

### 2. Configure CloudWatch (Amazon AWS)

```bash
# Install CloudWatch agent
kubectl apply -f https://raw.githubusercontent.com/aws-samples/amazon-cloudwatch-container-insights/latest/k8s-deployment-manifest-templates/deployment-mode/daemonset/container-insights-monitoring/cloudwatch-namespace.yaml

kubectl apply -f https://raw.githubusercontent.com/aws-samples/amazon-cloudwatch-container-insights/latest/k8s-deployment-manifest-templates/deployment-mode/daemonset/container-insights-monitoring/cwagent/cwagent-configmap.yaml

kubectl apply -f https://raw.githubusercontent.com/aws-samples/amazon-cloudwatch-container-insights/latest/k8s-deployment-manifest-templates/deployment-mode/daemonset/container-insights-monitoring/cwagent/cwagent-daemonset.yaml
```

## Troubleshooting

### Issues

#### 1. Kubeflow installation
```bash
# Check pod status
kubectl get pods -n kubeflow

# Check logs
kubectl logs -n kubeflow deployment/ml-pipeline-ui

# Restart failed pods
kubectl delete pod <pod-name> -n kubeflow
```

#### 2. Amazon EKS connection
```bash
# Update kubeconfig
aws eks update-kubeconfig --region us-west-2 --name kubeflow-cluster

# Verify connection
kubectl get nodes
```

#### 3. Docker build
```bash
# Clear Docker cache
docker system prune -a

# Check available space
df -h
```

#### 4. GPU support (if available)
```bash
# Install NVIDIA device plugin
kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.12.0/nvidia-device-plugin.yml

# Verify GPU nodes
kubectl get nodes "-o=custom-columns=NAME:.metadata.name,GPU:.status.allocatable.nvidia\.com/gpu"
```

## Usage

### 1. Run training pipeline locally
```bash
python src/bert_fine_tuning.py --data-path data/ --output-dir models/ --epochs 3
```

### 2. Test API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Single prediction
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"text": "This product is amazing!", "return_confidence": true}'

# Batch prediction
curl -X POST "http://localhost:8000/predict/batch" \
     -H "Content-Type: application/json" \
     -d '{"texts": ["Great service!", "Poor quality"], "return_confidence": true}'
```

### 3. Monitor pipeline in Kubeflow UI
1. Open Kubeflow UI: `http://localhost:8080` (local) or Load Balancer URL (AWS)
2. Navigate to "Pipelines" section
3. Upload and run `bert_pipeline.py`
4. Monitor execution in "Runs" section

## Kubeflow on Google GCP

Building a BERT machine learning (ML) pipeline with Kubeflow on Google Cloud Platform (GCP) involves leveraging Kubeflow pipelines within Vertex AI pipelines to orchestrate the various stages of your machine learning (ML) workflow.

**Steps**

*Project Setup on Google GCP*

Validate that you have an active Google GCP project with permissions (e.g., Owner).

Create a Google Cloud Storage bucket for storing pipeline artifacts and data.

*Kubeflow pipelines environment*

Utilize Vertex AI Pipelines, which is the managed service for running Kubeflow Pipelines on Google GCP. This abstracts away the underlying Kubernetes infrastructure management.

Alternatively, you can manually deploy Kubeflow on a Google Kubernetes Engine (GKE) cluster, but Vertex AI Pipelines is generally recommended for ease of use and scalability.

*Pipeline definition with Kubeflow Pipelines SDK*

Define your ML pipeline using the Kubeflow Pipelines SDK (KFP SDK), preferably v2 or later for compatibility with Vertex AI Pipelines.

Break down your BERT workflow into distinct components (e.g., data preprocessing, model training, model evaluation, model deployment).

*Custom Components*

For specific BERT-related tasks (e.g., fine-tuning, specific data formats), you will likely need to create custom components using Python functions or containerized applications.

*Google Cloud pipeline components*

Leverage pre-built Google Cloud pipeline components for interacting with other Vertex AI services, such as Vertex AI Datasets, Model Registry, and Endpoints, for tasks like data loading, model management, and online predictions.

*BERT model integration*

Training

Within your training component, implement the BERT model training logic using frameworks like TensorFlow or PyTorch. This might involve loading pre-trained BERT models, fine-tuning them on your specific dataset, and saving the trained model artifacts.

Data Handling

Use appropriate libraries and techniques to handle the text data required for BERT, including tokenization and formatting.

*Orchestration*

Automate the entire BERT machine learning (ML) lifecycle from data ingestion to model deployment.

*Artifact and Metadata management*

Vertex AI Pipelines integrates with Vertex ML Metadata, automatically tracking artifacts (e.g., datasets, models, metrics) and lineage across pipeline runs.

This provides visibility into your experiments and helps manage different versions of your BERT models.

*Deployment and Serving (Optional)*

If you need to serve your trained BERT model for online predictions, integrate components for deploying the model to a Vertex AI Endpoint using services like TorchServe or KFServing.


## References

- [Kubeflow on AWS](https://awslabs.github.io/kubeflow-manifests/)
- [Install Kubeflow Pipelines](https://docs.aws.amazon.com/sagemaker/latest/dg/kubernetes-sagemaker-components-install.html)
- [Amazon Elastic Kubernetes Service](https://docs.aws.amazon.com/whitepapers/latest/overview-deployment-options/amazon-elastic-kubernetes-service.html)
- [AWS EKS Documentation](https://docs.aws.amazon.com/eks/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Kubeflow Pipelines SDK](https://kubeflow-pipelines.readthedocs.io/en/latest/)
- [Build a pipeline](https://cloud.google.com/vertex-ai/docs/pipelines/build-pipeline)

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
