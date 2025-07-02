#!/bin/bash

# Initialize Terraform
terraform init

# Plan the deployment
terraform plan -var="db_password=your_secure_password"

# Apply the configuration
terraform apply -var="db_password=your_secure_password" -auto-approve

# Get outputs
echo "Load Balancer DNS: $(terraform output -raw load_balancer_dns)"
echo "ECR Repository URL: $(terraform output -raw ecr_repository_url)"