"""
Google Cloud Functions for LLM Inference
This example demonstrates how to use GCP Cloud Functions for LLM-related tasks
Note: Cloud Functions Gen 2 supports longer timeouts and more memory
Best used for: orchestration, preprocessing, postprocessing, routing
"""

import functions_framework
import json
import os
from typing import Dict, Any
from flask import Request, jsonify
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
PROJECT_ID = os.environ.get('GCP_PROJECT', '')
VERTEX_AI_LOCATION = os.environ.get('VERTEX_AI_LOCATION', 'us-central1')
VERTEX_AI_ENDPOINT = os.environ.get('VERTEX_AI_ENDPOINT', '')
USE_VERTEX_AI = os.environ.get('USE_VERTEX_AI', 'true').lower() == 'true'


@functions_framework.http
def inference(request: Request):
    """
    HTTP Cloud Function for LLM inference
    
    Args:
        request: Flask request object
        
    Returns:
        JSON response with generated text
    """
    # Set CORS headers
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    # Set CORS headers for main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    
    try:
        # Parse request
        request_json = request.get_json(silent=True)
        
        if not request_json:
            return (jsonify({'error': 'Request body must be JSON'}), 400, headers)
        
        prompt = request_json.get('prompt', '')
        max_tokens = request_json.get('max_tokens', 100)
        temperature = request_json.get('temperature', 0.7)
        model_name = request_json.get('model', 'gemini-pro')
        
        if not prompt:
            return (jsonify({'error': 'Prompt is required'}), 400, headers)
        
        # Choose inference method
        if USE_VERTEX_AI:
            response_text = invoke_vertex_ai(prompt, max_tokens, temperature, model_name)
            model_type = 'vertex_ai'
        elif VERTEX_AI_ENDPOINT:
            response_text = invoke_vertex_ai_endpoint(prompt, max_tokens, temperature)
            model_type = 'vertex_ai_endpoint'
        else:
            return (jsonify({'error': 'No inference endpoint configured'}), 500, headers)
        
        response_data = {
            'response': response_text,
            'model': model_type
        }
        
        return (jsonify(response_data), 200, headers)
        
    except Exception as e:
        logger.error(f'Error processing request: {str(e)}', exc_info=True)
        return (jsonify({'error': str(e)}), 500, headers)


@functions_framework.http
def health(request: Request):
    """
    Health check endpoint
    
    Args:
        request: Flask request object
        
    Returns:
        JSON response with health status
    """
    headers = {'Access-Control-Allow-Origin': '*'}
    
    health_status = {
        'status': 'healthy',
        'vertex_ai_configured': USE_VERTEX_AI,
        'custom_endpoint_configured': bool(VERTEX_AI_ENDPOINT)
    }
    
    return (jsonify(health_status), 200, headers)


def invoke_vertex_ai(prompt: str, max_tokens: int, temperature: float, model_name: str) -> str:
    """
    Invoke Vertex AI (Gemini or PaLM) for inference
    
    Args:
        prompt: Input prompt
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        model_name: Model to use (gemini-pro, text-bison, etc.)
        
    Returns:
        Generated text response
    """
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel, GenerationConfig
        
        # Initialize Vertex AI
        vertexai.init(project=PROJECT_ID, location=VERTEX_AI_LOCATION)
        
        # Configure generation
        generation_config = GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
            top_p=0.9
        )
        
        # Initialize model
        model = GenerativeModel(model_name)
        
        # Generate response
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        return response.text
        
    except Exception as e:
        logger.error(f'Vertex AI error: {str(e)}', exc_info=True)
        raise


def invoke_vertex_ai_endpoint(prompt: str, max_tokens: int, temperature: float) -> str:
    """
    Invoke custom Vertex AI endpoint for inference
    
    Args:
        prompt: Input prompt
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        
    Returns:
        Generated text response
    """
    try:
        from google.cloud import aiplatform
        
        # Initialize AI Platform
        aiplatform.init(project=PROJECT_ID, location=VERTEX_AI_LOCATION)
        
        # Get endpoint
        endpoint = aiplatform.Endpoint(VERTEX_AI_ENDPOINT)
        
        # Prepare instances
        instances = [
            {
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
        ]
        
        # Make prediction
        response = endpoint.predict(instances=instances)
        
        # Parse response
        predictions = response.predictions
        if predictions and len(predictions) > 0:
            prediction = predictions[0]
            if isinstance(prediction, str):
                return prediction
            elif isinstance(prediction, dict):
                return prediction.get('generated_text', prediction.get('output', ''))
        
        return str(predictions)
        
    except Exception as e:
        logger.error(f'Vertex AI endpoint error: {str(e)}', exc_info=True)
        raise


@functions_framework.http
def batch_inference(request: Request):
    """
    Batch inference endpoint for multiple prompts
    
    Args:
        request: Flask request object
        
    Returns:
        JSON response with list of generated texts
    """
    headers = {'Access-Control-Allow-Origin': '*'}
    
    try:
        request_json = request.get_json(silent=True)
        
        if not request_json:
            return (jsonify({'error': 'Request body must be JSON'}), 400, headers)
        
        prompts = request_json.get('prompts', [])
        max_tokens = request_json.get('max_tokens', 100)
        temperature = request_json.get('temperature', 0.7)
        model_name = request_json.get('model', 'gemini-pro')
        
        if not prompts or not isinstance(prompts, list):
            return (jsonify({'error': 'Prompts list is required'}), 400, headers)
        
        results = []
        for prompt in prompts:
            try:
                response_text = invoke_vertex_ai(prompt, max_tokens, temperature, model_name)
                results.append({'prompt': prompt, 'response': response_text})
            except Exception as e:
                results.append({'prompt': prompt, 'error': str(e)})
        
        return (jsonify({'results': results}), 200, headers)
        
    except Exception as e:
        logger.error(f'Batch processing error: {str(e)}', exc_info=True)
        return (jsonify({'error': str(e)}), 500, headers)


def preprocess_text(text: str) -> str:
    """
    Preprocess input text
    
    Args:
        text: Raw input text
        
    Returns:
        Processed text
    """
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
    text = text.strip()
    return text
