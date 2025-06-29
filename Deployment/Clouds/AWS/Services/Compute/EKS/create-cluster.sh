#!/bin/bash

# Create EKS cluster
eksctl create cluster -f cluster-config.yaml

# Update kubeconfig
aws eks update-kubeconfig --region us-west-2 --name go-app-cluster

# Verify cluster connection
kubectl get nodes