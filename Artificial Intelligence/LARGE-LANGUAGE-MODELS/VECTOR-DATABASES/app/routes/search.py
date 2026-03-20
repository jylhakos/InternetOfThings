"""
Search endpoints for vector database
"""
from fastapi import APIRouter, HTTPException
import logging
import time

from app.models import (
    SearchRequest, SearchResponse, SearchResult,
    EmbeddingRequest, EmbeddingResponse, VectorDBStatus
)
from app.main import get_vector_db_service, get_embedding_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def vector_search(request: SearchRequest):
    """
    Perform vector similarity search
    
    This endpoint:
    1. Converts query to embedding
    2. Searches vector database for similar documents
    3. Returns ranked results
    """
    try:
        vector_db = get_vector_db_service()
        embedding_service = get_embedding_service()
        
        if not vector_db or not embedding_service:
            raise HTTPException(status_code=503, detail="Services not initialized")
        
        start_time = time.time()
        
        # Generate query embedding
        query_embedding = embedding_service.generate_embedding(request.query)
        
        # Search vector database
        results = vector_db.search(
            collection=request.collection,
            query_embedding=query_embedding,
            top_k=request.top_k,
            filter=request.filter
        )
        
        query_time_ms = (time.time() - start_time) * 1000
        
        # Format results
        search_results = [
            SearchResult(
                id=r['id'],
                score=r['score'],
                text=r['text'],
                metadata=r['metadata']
            )
            for r in results
        ]
        
        return SearchResponse(
            results=search_results,
            query_time_ms=round(query_time_ms, 2),
            total_results=len(search_results)
        )
        
    except Exception as e:
        logger.error(f"Error in vector search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/embeddings/generate", response_model=EmbeddingResponse)
async def generate_embedding(request: EmbeddingRequest):
    """
    Generate embedding for text
    """
    try:
        embedding_service = get_embedding_service()
        
        if not embedding_service:
            raise HTTPException(status_code=503, detail="Embedding service not initialized")
        
        embedding = embedding_service.generate_embedding(request.text)
        
        return EmbeddingResponse(
            text=request.text,
            embedding=embedding,
            dimensions=len(embedding),
            model=embedding_service.get_model_name()
        )
        
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vector-db/status", response_model=VectorDBStatus)
async def get_vector_db_status():
    """
    Get vector database status and statistics
    """
    try:
        vector_db = get_vector_db_service()
        
        if not vector_db:
            raise HTTPException(status_code=503, detail="Vector database not initialized")
        
        status = vector_db.get_status()
        
        return VectorDBStatus(**status)
        
    except Exception as e:
        logger.error(f"Error getting vector DB status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
