"""
Text tokenization utilities
"""
from typing import List
import logging

logger = logging.getLogger(__name__)


class SimpleTokenizer:
    """
    Simple tokenizer for text processing
    
    This is a basic word-level tokenizer. For production use,
    consider using transformers tokenizers like:
    - transformers.AutoTokenizer
    - tiktoken (for OpenAI models)
    - sentencepiece
    """
    
    def __init__(self):
        self.name = "simple_tokenizer"
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        # Simple whitespace tokenization
        tokens = text.split()
        return tokens
    
    def count_tokens(self, text: str) -> int:
        """
        Count number of tokens in text
        
        Args:
            text: Input text
            
        Returns:
            Number of tokens
        """
        return len(self.tokenize(text))
    
    def encode(self, text: str) -> List[int]:
        """
        Encode text to token IDs (simple implementation)
        
        Args:
            text: Input text
            
        Returns:
            List of token IDs (here just using hash values)
        """
        tokens = self.tokenize(text)
        # Simple encoding using hash (not suitable for production)
        return [hash(token) % 50000 for token in tokens]
    
    def decode(self, token_ids: List[int]) -> str:
        """
        Decode token IDs back to text
        
        Note: This simple implementation cannot decode properly
        """
        return f"<decoded_{len(token_ids)}_tokens>"


def get_tokenizer(model_name: str = "simple"):
    """
    Get tokenizer instance
    
    Args:
        model_name: Name of the tokenizer model
        
    Returns:
        Tokenizer instance
    """
    if model_name == "simple":
        return SimpleTokenizer()
    else:
        logger.warning(f"Unknown tokenizer '{model_name}', using simple tokenizer")
        return SimpleTokenizer()


def estimate_tokens(text: str) -> int:
    """
    Estimate number of tokens in text
    
    Quick estimation: ~4 characters per token on average
    
    Args:
        text: Input text
        
    Returns:
        Estimated token count
    """
    return len(text) // 4


def truncate_text(text: str, max_tokens: int, tokenizer=None) -> str:
    """
    Truncate text to maximum number of tokens
    
    Args:
        text: Input text
        max_tokens: Maximum number of tokens
        tokenizer: Optional tokenizer instance
        
    Returns:
        Truncated text
    """
    if tokenizer is None:
        tokenizer = SimpleTokenizer()
    
    tokens = tokenizer.tokenize(text)
    
    if len(tokens) <= max_tokens:
        return text
    
    # Truncate tokens
    truncated_tokens = tokens[:max_tokens]
    return ' '.join(truncated_tokens) + '...'
