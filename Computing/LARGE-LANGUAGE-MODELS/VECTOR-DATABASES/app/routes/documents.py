"""
Document ingestion endpoints
"""
from fastapi import APIRouter, HTTPException
import logging
import uuid

from app.models import DocumentIngest, DocumentResponse
from app.main import get_vector_db_service, get_embedding_service
from app.utils.chunking import chunk_text

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/ingest", response_model=DocumentResponse)
async def ingest_document(doc: DocumentIngest):
    """
    Ingest a document into the vector database
    
    This endpoint:
    1. Chunks the document text
    2. Generates embeddings for each chunk
    3. Stores chunks in the vector database
    """
    try:
        vector_db = get_vector_db_service()
        embedding_service = get_embedding_service()
        
        if not vector_db or not embedding_service:
            raise HTTPException(status_code=503, detail="Services not initialized")
        
        # Chunk the text
        chunks = chunk_text(doc.text)
        logger.info(f"Split document into {len(chunks)} chunks")
        
        # Generate embeddings
        embeddings = embedding_service.generate_embeddings(chunks)
        
        # Generate IDs for chunks
        doc_id = str(uuid.uuid4())
        chunk_ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        
        # Prepare metadata
        metadatas = [
            {**doc.metadata, 'chunk_index': i, 'parent_id': doc_id}
            for i in range(len(chunks))
        ]
        
        # Store in vector database
        vector_db.add_documents(
            collection="default",
            ids=chunk_ids,
            embeddings=embeddings,
            texts=chunks,
            metadatas=metadatas
        )
        
        return DocumentResponse(
            id=doc_id,
            status="ingested",
            chunks=len(chunks),
            message=f"Successfully ingested {len(chunks)} chunks"
        )
        
    except Exception as e:
        logger.error(f"Error ingesting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk-ingest")
async def bulk_ingest(documents: list[DocumentIngest]):
    """
    Ingest multiple documents at once
    """
    try:
        results = []
        for doc in documents:
            result = await ingest_document(doc)
            results.append(result)
        
        return {
            "status": "success",
            "documents_ingested": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in bulk ingest: {e}")
        raise HTTPException(status_code=500, detail=str(e))
