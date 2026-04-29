#!/bin/bash

# AWS SageMaker MLflow Deployment Script
# This script deploys the Fish Weight Prediction model to Amazon SageMaker

set -e

echo "☁️ Deploying Fish Weight Prediction Model to AWS SageMaker"
echo "==========================================================="

# Check AWS CLI installation
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install AWS CLI first."
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

# Set variables
REGION=${AWS_REGION:-us-east-1}
BUCKET_NAME=${S3_BUCKET:-fish-weight-mlflow-$(date +%s)}
ROLE_NAME=${SAGEMAKER_ROLE:-FishWeightSageMakerRole}
MODEL_NAME=fish-weight-predictor
ENDPOINT_NAME=fish-weight-endpoint

echo "🔧 Configuration:"
echo "  Region: $REGION"
echo "  S3 Bucket: $BUCKET_NAME"
echo "  SageMaker Role: $ROLE_NAME"
echo "  Model Name: $MODEL_NAME"
echo "  Endpoint Name: $ENDPOINT_NAME"

# Create S3 bucket if it doesn't exist
echo "📦 Creating S3 bucket..."
aws s3 mb s3://$BUCKET_NAME --region $REGION 2>/dev/null || echo "Bucket already exists or creation failed"

# Create IAM role for SageMaker if it doesn't exist
echo "🔐 Creating SageMaker IAM role..."
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "sagemaker.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create role (ignore error if it already exists)
aws iam create-role --role-name $ROLE_NAME --assume-role-policy-document file://trust-policy.json 2>/dev/null || echo "Role already exists"

# Attach necessary policies
aws iam attach-role-policy --role-name $ROLE_NAME --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess 2>/dev/null || true
aws iam attach-role-policy --role-name $ROLE_NAME --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess 2>/dev/null || true

# Get role ARN
ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)
echo "✅ SageMaker Role ARN: $ROLE_ARN"

# Package model for SageMaker
echo "📦 Packaging model for SageMaker..."
mkdir -p sagemaker_deployment/code

# Create inference script for SageMaker
cat > sagemaker_deployment/code/inference.py << EOF
import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import os
import json

def model_fn(model_dir):
    """Load model from S3"""
    model = joblib.load(os.path.join(model_dir, 'model.pkl'))
    
    # Setup label encoder with default species
    label_encoder = LabelEncoder()
    label_encoder.classes_ = np.array(['Bream', 'Roach', 'Whitefish', 'Parkki', 'Perch', 'Pike', 'Smelt'])
    
    return {'model': model, 'label_encoder': label_encoder}

def input_fn(request_body, content_type='application/json'):
    """Parse input data"""
    if content_type == 'application/json':
        input_data = json.loads(request_body)
        return input_data
    else:
        raise ValueError(f"Unsupported content type: {content_type}")

def predict_fn(input_data, model_dict):
    """Make predictions"""
    model = model_dict['model']
    label_encoder = model_dict['label_encoder']
    
    # Convert to DataFrame
    df = pd.DataFrame([input_data])
    
    # Feature engineering
    df['Length_avg'] = (df['Length1'] + df['Length2'] + df['Length3']) / 3
    df['Volume_proxy'] = df['Length_avg'] * df['Height'] * df['Width']
    df['Length_diff'] = df['Length3'] - df['Length1']
    df['Aspect_ratio'] = df['Length_avg'] / df['Height']
    df['Body_index'] = df['Height'] / df['Width']
    
    # Encode species
    try:
        df['Species_encoded'] = label_encoder.transform(df['Species'])
    except ValueError:
        df['Species_encoded'] = 0  # Default for unknown species
    
    # Select features
    feature_columns = ['Length1', 'Length2', 'Length3', 'Height', 'Width', 
                      'Length_avg', 'Volume_proxy', 'Length_diff', 'Aspect_ratio', 
                      'Body_index', 'Species_encoded']
    
    X = df[feature_columns]
    
    # Make prediction
    prediction = model.predict(X)[0]
    
    return {'predicted_weight': float(prediction)}

def output_fn(prediction, accept='application/json'):
    """Format output"""
    if accept == 'application/json':
        return json.dumps(prediction), accept
    else:
        raise ValueError(f"Unsupported accept type: {accept}")
EOF

# Create requirements file for SageMaker
cat > sagemaker_deployment/requirements.txt << EOF
scikit-learn>=1.3.0
pandas>=2.0.0
numpy>=1.24.0
joblib>=1.3.0
EOF

# Copy model file
if [ -f "models/best_fish_weight_model.pkl" ]; then
    cp models/best_fish_weight_model.pkl sagemaker_deployment/model.pkl
    echo "✅ Model copied for deployment"
else
    echo "❌ Model file not found. Please train the model first."
    exit 1
fi

# Create model tar file
echo "📦 Creating model tar file..."
cd sagemaker_deployment
tar -czf model.tar.gz model.pkl code/ requirements.txt
cd ..

# Upload model to S3
echo "☁️ Uploading model to S3..."
aws s3 cp sagemaker_deployment/model.tar.gz s3://$BUCKET_NAME/model.tar.gz

# Create SageMaker model
echo "🤖 Creating SageMaker model..."
cat > create_model.json << EOF
{
    "ModelName": "$MODEL_NAME",
    "PrimaryContainer": {
        "Image": "763104351884.dkr.ecr.$REGION.amazonaws.com/sklearn-inference:1.0-1-cpu-py3",
        "ModelDataUrl": "s3://$BUCKET_NAME/model.tar.gz"
    },
    "ExecutionRoleArn": "$ROLE_ARN"
}
EOF

aws sagemaker create-model --cli-input-json file://create_model.json --region $REGION 2>/dev/null || echo "Model already exists"

# Create endpoint configuration
echo "🔧 Creating endpoint configuration..."
cat > create_endpoint_config.json << EOF
{
    "EndpointConfigName": "$MODEL_NAME-config",
    "ProductionVariants": [
        {
            "VariantName": "primary",
            "ModelName": "$MODEL_NAME",
            "InitialInstanceCount": 1,
            "InstanceType": "ml.t2.medium",
            "InitialVariantWeight": 1
        }
    ]
}
EOF

aws sagemaker create-endpoint-config --cli-input-json file://create_endpoint_config.json --region $REGION 2>/dev/null || echo "Endpoint config already exists"

# Create endpoint
echo "🚀 Creating SageMaker endpoint..."
cat > create_endpoint.json << EOF
{
    "EndpointName": "$ENDPOINT_NAME",
    "EndpointConfigName": "$MODEL_NAME-config"
}
EOF

aws sagemaker create-endpoint --cli-input-json file://create_endpoint.json --region $REGION 2>/dev/null || echo "Endpoint already exists"

# Wait for endpoint to be in service
echo "⏳ Waiting for endpoint to be in service (this may take several minutes)..."
aws sagemaker wait endpoint-in-service --endpoint-name $ENDPOINT_NAME --region $REGION

echo "✅ Endpoint is now in service!"

# Create test script for the endpoint
cat > test_sagemaker_endpoint.py << EOF
#!/usr/bin/env python3
"""Test script for SageMaker endpoint"""

import boto3
import json

def test_endpoint():
    # Initialize SageMaker runtime client
    runtime = boto3.client('sagemaker-runtime', region_name='$REGION')
    
    # Test data
    test_data = {
        'Species': 'Bream',
        'Length1': 23.2,
        'Length2': 25.4,
        'Length3': 30.0,
        'Height': 11.52,
        'Width': 4.02
    }
    
    # Invoke endpoint
    response = runtime.invoke_endpoint(
        EndpointName='$ENDPOINT_NAME',
        ContentType='application/json',
        Body=json.dumps(test_data)
    )
    
    # Parse response
    result = json.loads(response['Body'].read().decode())
    print(f"Prediction result: {result}")

if __name__ == "__main__":
    test_endpoint()
EOF

chmod +x test_sagemaker_endpoint.py

# Create cleanup script
cat > cleanup_aws_resources.sh << EOF
#!/bin/bash
# Cleanup AWS resources

echo "🧹 Cleaning up AWS resources..."

# Delete endpoint
aws sagemaker delete-endpoint --endpoint-name $ENDPOINT_NAME --region $REGION 2>/dev/null || true

# Delete endpoint configuration
aws sagemaker delete-endpoint-config --endpoint-config-name $MODEL_NAME-config --region $REGION 2>/dev/null || true

# Delete model
aws sagemaker delete-model --model-name $MODEL_NAME --region $REGION 2>/dev/null || true

# Delete S3 bucket contents and bucket
aws s3 rm s3://$BUCKET_NAME --recursive 2>/dev/null || true
aws s3 rb s3://$BUCKET_NAME 2>/dev/null || true

echo "✅ Cleanup completed!"
EOF

chmod +x cleanup_aws_resources.sh

# Clean up temporary files
rm -f trust-policy.json create_model.json create_endpoint_config.json create_endpoint.json

echo ""
echo "🎉 AWS SageMaker deployment completed!"
echo "======================================"
echo ""
echo "📊 Endpoint Information:"
echo "  Endpoint Name: $ENDPOINT_NAME"
echo "  Region: $REGION"
echo "  Status: In Service"
echo ""
echo "🧪 Testing:"
echo "  python test_sagemaker_endpoint.py"
echo ""
echo "🔗 Useful AWS CLI commands:"
echo "  aws sagemaker describe-endpoint --endpoint-name $ENDPOINT_NAME --region $REGION"
echo "  aws sagemaker list-endpoints --region $REGION"
echo ""
echo "🧹 Cleanup (when done):"
echo "  ./cleanup_aws_resources.sh"
echo ""
echo "💰 Cost Note: Remember that SageMaker endpoints incur charges while running."
echo "   Delete the endpoint when not in use to avoid unnecessary costs."
