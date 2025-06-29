#!/bin/bash

# Apply Kubernetes manifests
kubectl apply -f deployment.yaml
kubectl apply -f ingress.yaml

# Check deployment status
kubectl get deployments
kubectl get pods
kubectl get services
kubectl get ingress

# Get ALB URL
echo "Application will be available at:"
kubectl get ingress go-app-ingress -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'