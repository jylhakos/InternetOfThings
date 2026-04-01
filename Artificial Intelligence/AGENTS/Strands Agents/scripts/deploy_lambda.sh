#!/bin/bash

# Strands Agents - Deployment Script for AWS Lambda

set -e

echo "========================================="
echo "Deploying Strands Agent to AWS Lambda"
echo "========================================="

# Check if AWS SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo "Error: AWS SAM CLI is not installed."
    echo "Please install it from: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html"
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "Error: AWS credentials are not configured."
    echo "Please run: aws configure"
    exit 1
fi

cd deployment/lambda

echo "Building SAM application..."
sam build

echo "Deploying to AWS..."
sam deploy --guided

echo ""
echo "========================================="
echo "✓ Deployment completed!"
echo "========================================="
echo ""
echo "Check the outputs above for your API endpoint."
echo "Test your agent with:"
echo "curl -X POST <API_ENDPOINT> -H 'Content-Type: application/json' -d '{\"query\": \"What is the weather in Seattle?\"}'"
echo ""
