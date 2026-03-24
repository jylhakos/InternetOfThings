"""
AWS Lambda Handler for LLM Inference
This example demonstrates how to use AWS Lambda for LLM-related tasks
Note: Lambda has limitations for large model inference (15min timeout, 10GB memory max)
Best used for: orchestration, preprocessing, postprocessing, routing
"""

import json
import os
import boto3
from typing import Dict, Any

# Initialize AWS clients
sagemaker_runtime = boto3.client('sagemaker-runtime')
bedrock_runtime = boto3.client('bedrock-runtime')

# Environment variables
SAGEMAKER_ENDPOINT = os.environ.get('SAGEMAKER_ENDPOINT_NAME', '')
USE_BEDROCK = os.environ.get('USE_BEDROCK', 'false').lower() == 'true'


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler function
    
    Args:
        event: Lambda event containing the request
        context: Lambda context object
        
    Returns:
        Response dictionary with status code and body
    """
    try:
        # Parse request body
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event
        
        prompt = body.get('prompt', '')
        max_tokens = body.get('max_tokens', 100)
        temperature = body.get('temperature', 0.7)
        
        if not prompt:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Prompt is required'})
            }
        
        # Choose inference method based on configuration
        if USE_BEDROCK:
            response_text = invoke_bedrock(prompt, max_tokens, temperature)
        elif SAGEMAKER_ENDPOINT:
            response_text = invoke_sagemaker(prompt, max_tokens, temperature)
        else:
            response_text = "No inference endpoint configured"
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'response': response_text,
                'model': 'bedrock' if USE_BEDROCK else 'sagemaker'
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }


def invoke_bedrock(prompt: str, max_tokens: int, temperature: float) -> str:
    """
    Invoke Amazon Bedrock for inference
    
    Args:
        prompt: Input prompt
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        
    Returns:
        Generated text response
    """
    try:
        # Use Claude 3 on Bedrock
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": temperature
        })
        
        response = bedrock_runtime.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=body
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
        
    except Exception as e:
        print(f"Bedrock error: {str(e)}")
        raise


def invoke_sagemaker(prompt: str, max_tokens: int, temperature: float) -> str:
    """
    Invoke SageMaker endpoint for inference
    
    Args:
        prompt: Input prompt
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        
    Returns:
        Generated text response
    """
    try:
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "top_p": 0.9
            }
        }
        
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=SAGEMAKER_ENDPOINT,
            ContentType='application/json',
            Body=json.dumps(payload)
        )
        
        result = json.loads(response['Body'].read().decode())
        
        # Handle different response formats
        if isinstance(result, list) and len(result) > 0:
            return result[0].get('generated_text', '')
        elif isinstance(result, dict):
            return result.get('generated_text', result.get('output', ''))
        else:
            return str(result)
            
    except Exception as e:
        print(f"SageMaker error: {str(e)}")
        raise


def preprocess_text(text: str) -> str:
    """
    Preprocess input text
    
    Args:
        text: Raw input text
        
    Returns:
        Processed text
    """
    # Add your preprocessing logic here
    text = text.strip()
    return text


def postprocess_text(text: str) -> str:
    """
    Postprocess output text
    
    Args:
        text: Raw output text
        
    Returns:
        Processed text
    """
    # Add your postprocessing logic here
    text = text.strip()
    return text
