"""
Azure Functions for LLM Inference
This example demonstrates how to use Azure Functions for LLM-related tasks
Note: Azure Functions has similar limitations as AWS Lambda
Best used for: orchestration, preprocessing, postprocessing, routing
"""

import azure.functions as func
import json
import logging
import os
from typing import Optional

# Initialize Azure Function App
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# Environment variables
AZURE_OPENAI_ENDPOINT = os.environ.get('AZURE_OPENAI_ENDPOINT', '')
AZURE_OPENAI_KEY = os.environ.get('AZURE_OPENAI_KEY', '')
AZURE_OPENAI_DEPLOYMENT = os.environ.get('AZURE_OPENAI_DEPLOYMENT', 'gpt-4')
AZURE_ML_ENDPOINT = os.environ.get('AZURE_ML_ENDPOINT', '')
AZURE_ML_KEY = os.environ.get('AZURE_ML_KEY', '')


@app.route(route="inference", methods=["POST"])
def inference(req: func.HttpRequest) -> func.HttpResponse:
    """
    Main inference endpoint
    
    Args:
        req: HTTP request object
        
    Returns:
        HTTP response with generated text
    """
    logging.info('Processing inference request')
    
    try:
        # Parse request body
        req_body = req.get_json()
        prompt = req_body.get('prompt', '')
        max_tokens = req_body.get('max_tokens', 100)
        temperature = req_body.get('temperature', 0.7)
        use_azure_ml = req_body.get('use_azure_ml', False)
        
        if not prompt:
            return func.HttpResponse(
                json.dumps({'error': 'Prompt is required'}),
                status_code=400,
                mimetype='application/json'
            )
        
        # Choose inference method
        if use_azure_ml and AZURE_ML_ENDPOINT:
            response_text = invoke_azure_ml(prompt, max_tokens, temperature)
            model_type = 'azure_ml'
        elif AZURE_OPENAI_ENDPOINT:
            response_text = invoke_azure_openai(prompt, max_tokens, temperature)
            model_type = 'azure_openai'
        else:
            return func.HttpResponse(
                json.dumps({'error': 'No inference endpoint configured'}),
                status_code=500,
                mimetype='application/json'
            )
        
        response = {
            'response': response_text,
            'model': model_type
        }
        
        return func.HttpResponse(
            json.dumps(response),
            status_code=200,
            mimetype='application/json',
            headers={'Access-Control-Allow-Origin': '*'}
        )
        
    except ValueError as e:
        logging.error(f'Invalid JSON in request: {str(e)}')
        return func.HttpResponse(
            json.dumps({'error': 'Invalid JSON in request body'}),
            status_code=400,
            mimetype='application/json'
        )
    except Exception as e:
        logging.error(f'Error processing request: {str(e)}')
        return func.HttpResponse(
            json.dumps({'error': str(e)}),
            status_code=500,
            mimetype='application/json'
        )


@app.route(route="health", methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """
    Health check endpoint
    
    Args:
        req: HTTP request object
        
    Returns:
        HTTP response with health status
    """
    logging.info('Health check requested')
    
    health_status = {
        'status': 'healthy',
        'azure_openai_configured': bool(AZURE_OPENAI_ENDPOINT),
        'azure_ml_configured': bool(AZURE_ML_ENDPOINT)
    }
    
    return func.HttpResponse(
        json.dumps(health_status),
        status_code=200,
        mimetype='application/json'
    )


def invoke_azure_openai(prompt: str, max_tokens: int, temperature: float) -> str:
    """
    Invoke Azure OpenAI Service
    
    Args:
        prompt: Input prompt
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        
    Returns:
        Generated text response
    """
    try:
        from openai import AzureOpenAI
        
        client = AzureOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_KEY,
            api_version="2024-02-15-preview"
        )
        
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logging.error(f'Azure OpenAI error: {str(e)}')
        raise


def invoke_azure_ml(prompt: str, max_tokens: int, temperature: float) -> str:
    """
    Invoke Azure ML endpoint
    
    Args:
        prompt: Input prompt
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        
    Returns:
        Generated text response
    """
    try:
        import requests
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {AZURE_ML_KEY}'
        }
        
        payload = {
            'input_data': {
                'input_string': [prompt],
                'parameters': {
                    'max_new_tokens': max_tokens,
                    'temperature': temperature,
                    'top_p': 0.9
                }
            }
        }
        
        response = requests.post(
            AZURE_ML_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=300
        )
        response.raise_for_status()
        
        result = response.json()
        
        # Handle different response formats
        if isinstance(result, list) and len(result) > 0:
            return result[0]
        elif isinstance(result, dict):
            return result.get('output', result.get('generated_text', ''))
        else:
            return str(result)
            
    except Exception as e:
        logging.error(f'Azure ML error: {str(e)}')
        raise


@app.route(route="batch", methods=["POST"])
def batch_inference(req: func.HttpRequest) -> func.HttpResponse:
    """
    Batch inference endpoint for multiple prompts
    
    Args:
        req: HTTP request object
        
    Returns:
        HTTP response with list of generated texts
    """
    logging.info('Processing batch inference request')
    
    try:
        req_body = req.get_json()
        prompts = req_body.get('prompts', [])
        max_tokens = req_body.get('max_tokens', 100)
        temperature = req_body.get('temperature', 0.7)
        
        if not prompts or not isinstance(prompts, list):
            return func.HttpResponse(
                json.dumps({'error': 'Prompts list is required'}),
                status_code=400,
                mimetype='application/json'
            )
        
        results = []
        for prompt in prompts:
            try:
                response_text = invoke_azure_openai(prompt, max_tokens, temperature)
                results.append({'prompt': prompt, 'response': response_text})
            except Exception as e:
                results.append({'prompt': prompt, 'error': str(e)})
        
        return func.HttpResponse(
            json.dumps({'results': results}),
            status_code=200,
            mimetype='application/json',
            headers={'Access-Control-Allow-Origin': '*'}
        )
        
    except Exception as e:
        logging.error(f'Batch processing error: {str(e)}')
        return func.HttpResponse(
            json.dumps({'error': str(e)}),
            status_code=500,
            mimetype='application/json'
        )
