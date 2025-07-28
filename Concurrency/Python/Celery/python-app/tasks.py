import requests
import json
import logging
from typing import Dict, Any, Optional
from celery_app import celery_app
from config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def process_llm_request(self, prompt: str, model_name: str = None, temperature: float = 0.7, max_tokens: int = 1000) -> Dict[str, Any]:
    """
    Celery task to process LLM requests through LangChain.js service
    
    Args:
        prompt: The input prompt for the LLM
        model_name: Name of the model to use (optional)
        temperature: Temperature for response generation
        max_tokens: Maximum number of tokens in response
    
    Returns:
        Dictionary containing the LLM response and metadata
    """
    try:
        # Update task state to indicate processing has started
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Sending request to LangChain service...'}
        )
        
        # Prepare request payload
        payload = {
            'prompt': prompt,
            'model': model_name or settings.OLLAMA_MODEL,
            'temperature': temperature,
            'max_tokens': max_tokens
        }
        
        # Make request to LangChain.js service
        response = requests.post(
            f"{settings.LANGCHAIN_SERVICE_URL}/generate",
            json=payload,
            timeout=settings.CELERY_TASK_TIMEOUT - 30  # Leave buffer for task timeout
        )
        
        response.raise_for_status()
        result = response.json()
        
        # Update task state with completion
        self.update_state(
            state='SUCCESS',
            meta={'status': 'LLM processing completed successfully'}
        )
        
        return {
            'success': True,
            'response': result.get('response', ''),
            'model': result.get('model', model_name),
            'tokens_used': result.get('tokens_used', 0),
            'processing_time': result.get('processing_time', 0),
            'timestamp': result.get('timestamp', '')
        }
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout error for task {self.request.id}")
        self.update_state(
            state='FAILURE',
            meta={'error': 'Request timeout - LLM processing took too long'}
        )
        raise
        
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error for task {self.request.id}")
        self.update_state(
            state='FAILURE',
            meta={'error': 'Failed to connect to LangChain service'}
        )
        raise
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error for task {self.request.id}: {str(e)}")
        self.update_state(
            state='FAILURE',
            meta={'error': f'Request failed: {str(e)}'}
        )
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error for task {self.request.id}: {str(e)}")
        self.update_state(
            state='FAILURE',
            meta={'error': f'Unexpected error: {str(e)}'}
        )
        raise

@celery_app.task
def health_check_langchain_service() -> Dict[str, Any]:
    """
    Health check task for LangChain.js service
    
    Returns:
        Dictionary containing health status
    """
    try:
        response = requests.get(
            f"{settings.LANGCHAIN_SERVICE_URL}/health",
            timeout=10
        )
        response.raise_for_status()
        
        return {
            'success': True,
            'status': 'healthy',
            'service': 'langchain',
            'response_time': response.elapsed.total_seconds()
        }
        
    except Exception as e:
        return {
            'success': False,
            'status': 'unhealthy',
            'service': 'langchain',
            'error': str(e)
        }

@celery_app.task
def get_available_models() -> Dict[str, Any]:
    """
    Get available models from LangChain.js service
    
    Returns:
        Dictionary containing available models
    """
    try:
        response = requests.get(
            f"{settings.LANGCHAIN_SERVICE_URL}/models",
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        
        return {
            'success': True,
            'models': result.get('models', []),
            'default_model': settings.OLLAMA_MODEL
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'models': []
        }
