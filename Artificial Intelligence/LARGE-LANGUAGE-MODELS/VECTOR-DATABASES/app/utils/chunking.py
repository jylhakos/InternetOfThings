"""
Text chunking utilities for document processing
"""
from typing import List
import logging

from app.config import settings
from app.utils.tokenizer import get_tokenizer, estimate_tokens

logger = logging.getLogger(__name__)


def chunk_text(
    text: str,
    chunk_size: int = None,
    chunk_overlap: int = None,
    separator: str = "\n\n"
) -> List[str]:
    """
    Split text into chunks with overlap
    
    This is essential for storing documents in vector databases because:
    1. Embedding models have token limits (e.g., 512 tokens)
    2. Smaller chunks provide more precise retrieval
    3. Overlap preserves context across chunk boundaries
    
    Args:
        text: Input text to chunk
        chunk_size: Maximum tokens per chunk (default from config)
        chunk_overlap: Number of tokens to overlap (default from config)
        separator: Paragraph/section separator
        
    Returns:
        List of text chunks
    """
    if chunk_size is None:
        chunk_size = settings.chunk_size
    
    if chunk_overlap is None:
        chunk_overlap = settings.chunk_overlap
    
    # First try to split by separator (paragraphs)
    sections = text.split(separator)
    
    chunks = []
    current_chunk = []
    current_size = 0
    
    tokenizer = get_tokenizer()
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
        
        section_tokens = tokenizer.count_tokens(section)
        
        # If section itself is too large, split it further
        if section_tokens > chunk_size:
            # Split by sentences
            sentences = split_into_sentences(section)
            for sentence in sentences:
                sentence_tokens = tokenizer.count_tokens(sentence)
                
                if current_size + sentence_tokens > chunk_size and current_chunk:
                    # Save current chunk
                    chunks.append(' '.join(current_chunk))
                    
                    # Start new chunk with overlap
                    overlap_text = get_overlap_text(current_chunk, chunk_overlap, tokenizer)
                    current_chunk = [overlap_text, sentence] if overlap_text else [sentence]
                    current_size = tokenizer.count_tokens(' '.join(current_chunk))
                else:
                    current_chunk.append(sentence)
                    current_size += sentence_tokens
        else:
            # Section fits within chunk size
            if current_size + section_tokens > chunk_size and current_chunk:
                # Save current chunk
                chunks.append(' '.join(current_chunk))
                
                # Start new chunk with overlap
                overlap_text = get_overlap_text(current_chunk, chunk_overlap, tokenizer)
                current_chunk = [overlap_text, section] if overlap_text else [section]
                current_size = tokenizer.count_tokens(' '.join(current_chunk))
            else:
                current_chunk.append(section)
                current_size += section_tokens
    
    # Add remaining chunk
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    logger.info(f"Split text into {len(chunks)} chunks (size: {chunk_size}, overlap: {chunk_overlap})")
    
    return chunks


def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences
    
    Simple implementation using common sentence delimiters
    
    Args:
        text: Input text
        
    Returns:
        List of sentences
    """
    # Simple sentence splitting
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def get_overlap_text(chunk: List[str], overlap_tokens: int, tokenizer) -> str:
    """
    Get overlap text from end of chunk
    
    Args:
        chunk: Current chunk as list of strings
        overlap_tokens: Number of tokens to overlap
        tokenizer: Tokenizer instance
        
    Returns:
        Overlap text
    """
    if not chunk or overlap_tokens <= 0:
        return ""
    
    # Take text from end of chunk
    full_text = ' '.join(chunk)
    tokens = tokenizer.tokenize(full_text)
    
    if len(tokens) <= overlap_tokens:
        return full_text
    
    # Take last N tokens
    overlap_tokens_list = tokens[-overlap_tokens:]
    return ' '.join(overlap_tokens_list)


def chunk_documents(documents: List[str], chunk_size: int = None, chunk_overlap: int = None) -> List[str]:
    """
    Chunk multiple documents
    
    Args:
        documents: List of documents
        chunk_size: Maximum tokens per chunk
        chunk_overlap: Number of tokens to overlap
        
    Returns:
        List of all chunks from all documents
    """
    all_chunks = []
    
    for doc in documents:
        chunks = chunk_text(doc, chunk_size, chunk_overlap)
        all_chunks.extend(chunks)
    
    logger.info(f"Chunked {len(documents)} documents into {len(all_chunks)} chunks")
    
    return all_chunks


def chunk_with_metadata(
    text: str,
    metadata: dict,
    chunk_size: int = None,
    chunk_overlap: int = None
) -> List[dict]:
    """
    Chunk text and attach metadata to each chunk
    
    Args:
        text: Input text
        metadata: Metadata to attach
        chunk_size: Maximum tokens per chunk
        chunk_overlap: Number of tokens to overlap
        
    Returns:
        List of dictionaries with 'text' and 'metadata'
    """
    chunks = chunk_text(text, chunk_size, chunk_overlap)
    
    result = []
    for i, chunk in enumerate(chunks):
        chunk_metadata = {
            **metadata,
            'chunk_index': i,
            'total_chunks': len(chunks)
        }
        result.append({
            'text': chunk,
            'metadata': chunk_metadata
        })
    
    return result
