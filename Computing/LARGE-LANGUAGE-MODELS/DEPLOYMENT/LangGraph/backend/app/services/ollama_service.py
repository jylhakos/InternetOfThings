import httpx
import json
from typing import Dict, Any, List, Optional, AsyncGenerator
from loguru import logger
import time

from app.core.config import settings
from app.core.prompts import PromptTemplates, get_model_type_from_name
from app.models.schemas import ModelInfo


class OllamaService:
    """Service for interacting with Ollama LLM server"""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.timeout = httpx.Timeout(60.0, read=300.0)  # Extended read timeout for LLM responses
        
    async def health_check(self) -> Dict[str, Any]:
        """Check if Ollama server is healthy"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    return {"status": "healthy", "models": response.json()}
                else:
                    return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    async def list_models(self) -> List[ModelInfo]:
        """List available models from Ollama"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                
                models_data = response.json()
                models = []
                
                for model in models_data.get("models", []):
                    model_info = ModelInfo(
                        name=model["name"],
                        size=model.get("size"),
                        modified_at=model.get("modified_at"),
                        digest=model.get("digest"),
                        details=model.get("details", {})
                    )
                    models.append(model_info)
                
                return models
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    async def generate_response(
        self,
        prompt: str,
        model: str = settings.PRIMARY_MODEL,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response from Ollama model"""
        start_time = time.time()
        
        try:
            # Prepare request payload
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.9),
                    "top_k": kwargs.get("top_k", 40),
                    "num_ctx": kwargs.get("context_window", 4000),
                }
            }
            
            # Add max tokens if specified
            if "max_tokens" in kwargs:
                payload["options"]["num_predict"] = kwargs["max_tokens"]
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                processing_time = time.time() - start_time
                
                return {
                    "response": result.get("response", ""),
                    "model": result.get("model", model),
                    "processing_time": processing_time,
                    "context": result.get("context", []),
                    "done": result.get("done", True),
                    "total_duration": result.get("total_duration", 0),
                    "load_duration": result.get("load_duration", 0),
                    "prompt_eval_duration": result.get("prompt_eval_duration", 0),
                    "eval_duration": result.get("eval_duration", 0),
                    "eval_count": result.get("eval_count", 0),
                }
        except httpx.TimeoutException:
            logger.error("Ollama request timed out")
            raise Exception("Request timed out")
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise Exception(f"Request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise Exception(f"Generation failed: {str(e)}")
    
    async def generate_stream(
        self,
        prompt: str,
        model: str = settings.PRIMARY_MODEL,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate streaming response from Ollama model"""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.9),
                    "top_k": kwargs.get("top_k", 40),
                    "num_ctx": kwargs.get("context_window", 4000),
                }
            }
            
            if "max_tokens" in kwargs:
                payload["options"]["num_predict"] = kwargs["max_tokens"]
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/generate",
                    json=payload
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                chunk = json.loads(line)
                                yield chunk
                                
                                if chunk.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"Streaming generation failed: {e}")
            raise Exception(f"Streaming failed: {str(e)}")
    
    async def format_prompt_for_model(
        self,
        question: str,
        model: str,
        context: str = "",
        **kwargs
    ) -> str:
        """Format prompt according to model requirements"""
        model_type = get_model_type_from_name(model)
        return PromptTemplates.format_prompt(
            model_type=model_type,
            question=question,
            context=context,
            **kwargs
        )
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = settings.PRIMARY_MODEL,
        **kwargs
    ) -> Dict[str, Any]:
        """Chat completion using Ollama's chat endpoint"""
        start_time = time.time()
        
        try:
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.9),
                    "num_ctx": kwargs.get("context_window", 4000),
                }
            }
            
            if "max_tokens" in kwargs:
                payload["options"]["num_predict"] = kwargs["max_tokens"]
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                processing_time = time.time() - start_time
                
                return {
                    "message": result.get("message", {}),
                    "model": result.get("model", model),
                    "processing_time": processing_time,
                    "done": result.get("done", True),
                    "total_duration": result.get("total_duration", 0),
                    "load_duration": result.get("load_duration", 0),
                    "prompt_eval_duration": result.get("prompt_eval_duration", 0),
                    "eval_duration": result.get("eval_duration", 0),
                }
        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            raise Exception(f"Chat completion failed: {str(e)}")
    
    async def pull_model(self, model_name: str) -> bool:
        """Pull/download a model to Ollama"""
        try:
            payload = {"name": model_name, "stream": False}
            
            async with httpx.AsyncClient(timeout=httpx.Timeout(300.0)) as client:
                response = await client.post(
                    f"{self.base_url}/api/pull",
                    json=payload
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            return False
    
    async def delete_model(self, model_name: str) -> bool:
        """Delete a model from Ollama"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.delete(
                    f"{self.base_url}/api/delete",
                    json={"name": model_name}
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Failed to delete model {model_name}: {e}")
            return False
