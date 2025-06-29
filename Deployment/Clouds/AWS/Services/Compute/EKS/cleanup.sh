#!/bin/bash

echo "🧹 Cleaning up resources..."

# Delete Kubernetes resources
kubectl delete -f hpa.yaml
kubectl delete -f ingress.yaml
kubectl delete -f deployment.yaml

# Delete EKS cluster
eksctl delete cluster --name go-app-cluster --region us-west-2

# Delete ECR repository (optional)
aws ecr delete-repository --repository-name go-k8s-app --region us-west-2 --force

echo "✅ Cleanup complete!"