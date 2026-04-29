"""
Embedding generation service using sentence-transformers
"""
from sentence_transformers import SentenceTransformer
from typing import List, Union
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings"""
    
    def __init__(self):
        """Initialize the embedding model"""
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        self.model = SentenceTransformer(settings.embedding_model)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Embedding dimension: {self.dimension}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text
            
        Returns:
            List of floats representing the embedding
        """
        embedding = self.model.encode(text, convert_to_tensor=False)
        return embedding.tolist()
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embeddings
        """
        embeddings = self.model.encode(texts, convert_to_tensor=False)
        return [emb.tolist() for emb in embeddings]
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        return self.dimension
    
    def get_model_name(self) -> str:
        """Get model name"""
        return settings.embedding_model
