# Makefile for BERT Kubeflow Pipeline

.PHONY: help setup clean build deploy test local-train local-api docker-build docker-run

# Variables
PYTHON := python3
PIP := pip3
VENV := bert-kubeflow-env
CLUSTER_NAME := kubeflow-cluster
AWS_REGION := us-west-2

# Default target
help:
	@echo "🤖 BERT Kubeflow Pipeline - Available Targets:"
	@echo ""
	@echo "Setup & Environment:"
	@echo "  setup          - Full environment setup"
	@echo "  setup-python   - Setup Python environment only"
	@echo "  setup-aws      - Setup AWS configuration"
	@echo "  setup-local    - Setup local Kubeflow"
	@echo "  clean          - Clean up environment"
	@echo ""
	@echo "Development:"
	@echo "  local-train    - Run BERT training locally"
	@echo "  local-api      - Start FastAPI server locally"
	@echo "  test           - Run tests"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build   - Build Docker images"
	@echo "  docker-run     - Run serving container"
	@echo "  docker-push    - Push images to ECR"
	@echo ""
	@echo "Kubeflow:"
	@echo "  compile-pipeline - Compile Kubeflow pipeline"
	@echo "  deploy-k8s     - Deploy to Kubernetes"
	@echo "  deploy-aws     - Full AWS deployment"
	@echo ""
	@echo "Infrastructure:"
	@echo "  terraform-init - Initialize Terraform"
	@echo "  terraform-plan - Plan Terraform deployment"
	@echo "  terraform-apply - Apply Terraform configuration"
	@echo "  cloudformation - Deploy with CloudFormation"
	@echo ""

# Setup targets
setup:
	@echo "🚀 Setting up complete environment..."
	./scripts/setup.sh

setup-python:
	@echo "🐍 Setting up Python environment..."
	./scripts/setup.sh python

setup-aws:
	@echo "☁️ Setting up AWS configuration..."
	./scripts/setup.sh aws

setup-local:
	@echo "🏠 Setting up local Kubeflow..."
	./scripts/setup.sh local

clean:
	@echo "🧹 Cleaning up environment..."
	rm -rf $(VENV)
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf *.egg-info
	docker system prune -f

# Development targets
local-train:
	@echo "🎯 Running BERT training locally..."
	$(PYTHON) src/bert_fine_tuning.py

local-api:
	@echo "🌐 Starting FastAPI server..."
	$(PYTHON) api.py

test:
	@echo "🧪 Running tests..."
	$(PYTHON) -m pytest tests/ -v

# Docker targets
docker-build:
	@echo "🐳 Building Docker images..."
	docker build -t bert-serving .
	docker build -t bert-training -f Dockerfile.training .

docker-run:
	@echo "🐳 Running serving container..."
	docker run -p 8000:8000 bert-serving

docker-push:
	@echo "🐳 Pushing images to ECR..."
	./scripts/deploy.sh push

# Kubeflow targets
compile-pipeline:
	@echo "⚙️ Compiling Kubeflow pipeline..."
	$(PYTHON) pipeline/bert_pipeline.py

deploy-k8s:
	@echo "☸️ Deploying to Kubernetes..."
	./scripts/deploy.sh deploy

deploy-aws:
	@echo "☁️ Full AWS deployment..."
	./scripts/deploy.sh

# Infrastructure targets
terraform-init:
	@echo "🏗️ Initializing Terraform..."
	cd terraform && terraform init

terraform-plan:
	@echo "📋 Planning Terraform deployment..."
	cd terraform && terraform plan -var="cluster_name=$(CLUSTER_NAME)" -var="aws_region=$(AWS_REGION)"

terraform-apply:
	@echo "🚀 Applying Terraform configuration..."
	cd terraform && terraform apply -var="cluster_name=$(CLUSTER_NAME)" -var="aws_region=$(AWS_REGION)" -auto-approve

cloudformation:
	@echo "📚 Deploying with CloudFormation..."
	./scripts/deploy-cloudformation.sh deploy

# Utility targets
logs:
	@echo "📄 Showing Kubeflow logs..."
	kubectl logs -n kubeflow -l app=ml-pipeline-ui --tail=100

status:
	@echo "📊 Checking deployment status..."
	kubectl get pods -n kubeflow
	kubectl get svc -n kubeflow

port-forward:
	@echo "🔗 Setting up port forwarding..."
	@echo "Kubeflow UI will be available at http://localhost:8080"
	kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80

# Installation targets for dependencies
install-deps:
	@echo "📦 Installing system dependencies..."
	sudo apt-get update
	sudo apt-get install -y docker.io kubectl

install-tools:
	@echo "🛠️ Installing additional tools..."
	# Install Minikube
	curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
	sudo install minikube-linux-amd64 /usr/local/bin/minikube
	rm minikube-linux-amd64
	# Install Helm
	curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Environment info
env-info:
	@echo "🔍 Environment Information:"
	@echo "Python: $(shell python3 --version)"
	@echo "Docker: $(shell docker --version)"
	@echo "kubectl: $(shell kubectl version --client --short 2>/dev/null || echo 'Not installed')"
	@echo "AWS CLI: $(shell aws --version 2>/dev/null || echo 'Not installed')"
	@echo "Terraform: $(shell terraform --version 2>/dev/null || echo 'Not installed')"
