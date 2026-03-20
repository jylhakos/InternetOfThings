"""
LLM service for inference
"""
import logging
import requests
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

from app.config import settings

logger = logging.getLogger(__name__)


class LLMBackend(ABC):
    """Abstract base class for LLM backends"""
    
    @abstractmethod
    def generate(self, prompt: str, context: Optional[List[str]] = None) -> str:
        """Generate response from LLM"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if LLM is available"""
        pass


class OllamaBackend(LLMBackend):
    """Ollama backend for local LLM inference"""
    
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        logger.info(f"Initialized Ollama backend with model: {self.model}")
    
    def generate(self, prompt: str, context: Optional[List[str]] = None) -> str:
        """Generate response using Ollama"""
        # Build full prompt with context if provided
        full_prompt = prompt
        if context:
            context_text = "\n\n".join([f"Context {i+1}:\n{ctx}" for i, ctx in enumerate(context)])
            full_prompt = f"{context_text}\n\nQuestion: {prompt}\n\nAnswer:"
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False
                },
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API error: {e}")
            return f"Error: Unable to generate response. {str(e)}"
    
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False


class MockLLMBackend(LLMBackend):
    """Mock LLM backend for testing"""
    
    def __init__(self):
        logger.info("Initialized Mock LLM backend")
    
    def generate(self, prompt: str, context: Optional[List[str]] = None) -> str:
        """Generate mock response"""
        if context:
            return f"Based on the provided context, here's my response to: {prompt}"
        return f"Mock response to: {prompt}"
    
    def is_available(self) -> bool:
        """Always available"""
        return True


class LLMService:
    """Main LLM service"""
    
    def __init__(self):
        """Initialize LLM backend"""
        self.backend = self._create_backend()
    
    def _create_backend(self) -> LLMBackend:
        """Create appropriate backend based on config"""
        if settings.llm_provider == "ollama":
            backend = OllamaBackend()
            # Fall back to mock if Ollama is not available
            if not backend.is_available():
                logger.warning("Ollama not available, using mock backend")
                return MockLLMBackend()
            return backend
        else:
            logger.warning(f"Unsupported LLM provider '{settings.llm_provider}', using mock")
            return MockLLMBackend()
    
    def generate_response(self, prompt: str, context: Optional[List[str]] = None) -> str:
        """
        Generate response from LLM
        
        Args:
            prompt: User query
            context: Optional list of context strings for RAG
            
        Returns:
            Generated response
        """
        return self.backend.generate(prompt, context)
    
    def is_available(self) -> bool:
        """Check if LLM is available"""
        return self.backend.is_available()
    
    def get_model_name(self) -> str:
        """Get model name"""
        if isinstance(self.backend, OllamaBackend):
            return settings.ollama_model
        return "mock"
