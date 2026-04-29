from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
import json
from loguru import logger

from app.models.schemas import (
    DocumentResponse, DocumentListResponse, DocumentMetadata,
    Document, ErrorResponse
)
from app.services.document_service import DocumentService
from app.services.vector_service import VectorService


router = APIRouter()


# Dependency to get services
def get_vector_service():
    """Get vector service from app state"""
    # This will be injected by FastAPI from app.state
    pass


def get_document_service(vector_service: VectorService = Depends(get_vector_service)):
    """Get document service"""
    return DocumentService(vector_service)


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None),
    document_service: DocumentService = Depends(get_document_service)
):
    """Upload and process a document"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file selected")
        
        if file.size and file.size > 50 * 1024 * 1024:  # 50MB limit
            raise HTTPException(status_code=400, detail="File too large (max 50MB)")
        
        # Parse metadata if provided
        doc_metadata = None
        if metadata:
            try:
                metadata_dict = json.loads(metadata)
                doc_metadata = DocumentMetadata(**metadata_dict)
            except (json.JSONDecodeError, ValueError) as e:
                raise HTTPException(status_code=400, detail=f"Invalid metadata format: {str(e)}")
        
        # Read file content
        file_content = await file.read()
        
        # Process document
        result = await document_service.process_document(
            filename=file.filename,
            file_content=file_content,
            content_type=file.content_type or "application/octet-stream",
            metadata=doc_metadata
        )
        
        logger.info(f"Document uploaded successfully: {file.filename}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    page: int = 1,
    page_size: int = 20,
    category: Optional[str] = None,
    document_service: DocumentService = Depends(get_document_service)
):
    """List uploaded documents with pagination"""
    try:
        # For now, return uploaded files info
        # In a production system, you'd store document metadata in a database
        files = await document_service.list_uploaded_files()
        
        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_files = files[start_idx:end_idx]
        
        # Convert to Document objects (simplified for demo)
        documents = []
        for file_info in paginated_files:
            doc = Document(
                id=file_info["filename"].split(".")[0],  # Simple ID from filename
                filename=file_info["filename"],
                file_type=file_info["filename"].split(".")[-1] if "." in file_info["filename"] else "unknown",
                file_size=file_info["size"],
                content_preview="",  # Would need to read file for preview
                metadata=DocumentMetadata(
                    title=file_info["filename"],
                    created_at=file_info["created"]
                ),
                chunk_count=0,  # Would need to query vector DB for actual count
                created_at=file_info["created"],
                updated_at=file_info["modified"]
            )
            documents.append(doc)
        
        return DocumentListResponse(
            documents=documents,
            total=len(files),
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service)
):
    """Delete a document and its chunks"""
    try:
        success = await document_service.delete_document(document_id)
        
        if success:
            return {"message": f"Document {document_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Document not found or deletion failed")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service)
):
    """Get document information"""
    try:
        # Get document info (this would normally query a database)
        doc_info = await document_service.get_document_info(document_id)
        
        if not doc_info or not doc_info.get("exists", False):
            raise HTTPException(status_code=404, detail="Document not found")
        
        return doc_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}/chunks")
async def get_document_chunks(
    document_id: str,
    vector_service: VectorService = Depends(get_vector_service)
):
    """Get all chunks for a document"""
    try:
        chunks = await vector_service.get_document_chunks(document_id)
        
        return {
            "document_id": document_id,
            "chunks": chunks,
            "total_chunks": len(chunks)
        }
        
    except Exception as e:
        logger.error(f"Failed to get chunks for document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_documents(
    request: VectorSearchRequest,
    vector_service: VectorService = Depends(get_vector_service)
):
    """Search documents using vector similarity"""
    try:
        response = await vector_service.search_with_filters(request)
        return response
        
    except Exception as e:
        logger.error(f"Document search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/collection")
async def get_collection_stats(
    vector_service: VectorService = Depends(get_vector_service)
):
    """Get vector collection statistics"""
    try:
        stats = await vector_service.get_collection_info()
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get collection stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
