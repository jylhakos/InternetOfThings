#!/bin/bash

set -e

echo "Automation script for a Go web application deployment to EKS."

# Variables
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export AWS_REGION="us-west-2"
export IMAGE_NAME="go-k8s-app"
export CLUSTER_NAME="go-app-cluster"

# Build and push Docker image
echo "Building and pushing Docker image."
./build-and-push.sh

# Update deployment manifest with correct image URI
sed -i "s/YOUR_AWS_ACCOUNT_ID/$AWS_ACCOUNT_ID/g" deployment.yaml

# Create EKS cluster if it doesn't exist
if ! eksctl get cluster --name $CLUSTER_NAME --region $AWS_REGION > /dev/null 2>&1; then
    echo "Creating EKS cluster..."
    eksctl create cluster -f cluster-config.yaml
fi

# Update kubeconfig
aws eks update-kubeconfig --region $AWS_REGION --name $CLUSTER_NAME

# Install AWS Load Balancer controller
echo "Installing AWS Load Balancer Controller..."
./install-alb-controller.sh

# Deploy application
echo "Deploying application..."
kubectl apply -f deployment.yaml
kubectl apply -f ingress.yaml
kubectl apply -f hpa.yaml

# Wait for deployment
echo "Waiting for deployment to be ready."
kubectl wait --for=condition=available --timeout=300s deployment/go-app-deployment

# Get application URL
echo "Deployment completed."

kubectl get ingress go-app-ingress -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'

echo "  Use kubectl commands:"
echo "  kubectl get pods"
echo "  kubectl logs -l app=go-app"
echo "  kubectl describe service go-app-service"
echo "  kubectl get hpa"