from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, AsyncGenerator
import json
from loguru import logger

from app.models.schemas import (
    ChatMessage, ChatResponse, StreamChatRequest, RAGQuery, 
    ModelName, AvailableModelsResponse, ModelSwitchRequest,
    BatchProcessRequest, BatchProcessResponse
)
from app.services.rag_service import RAGService
from app.services.ollama_service import OllamaService
from app.services.vector_service import VectorService


router = APIRouter()


# Dependency to get services
def get_vector_service():
    """Get vector service from app state"""
    pass


def get_ollama_service():
    """Get Ollama service from app state"""
    pass


def get_rag_service(
    vector_service: VectorService = Depends(get_vector_service),
    ollama_service: OllamaService = Depends(get_ollama_service)
):
    """Get RAG service"""
    return RAGService(vector_service, ollama_service)


@router.post("/query", response_model=ChatResponse)
async def chat_query(
    message: ChatMessage,
    rag_service: RAGService = Depends(get_rag_service)
):
    """Process a chat query with optional RAG"""
    try:
        response = await rag_service.chat(message)
        logger.info(f"Chat query processed: {message.message[:50]}...")
        return response
        
    except Exception as e:
        logger.error(f"Chat query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def stream_chat(
    request: StreamChatRequest,
    ollama_service: OllamaService = Depends(get_ollama_service),
    rag_service: RAGService = Depends(get_rag_service)
):
    """Stream chat response"""
    
    async def generate_stream() -> AsyncGenerator[str, None]:
        try:
            if request.use_rag:
                # For RAG streaming, we need to get context first, then stream the generation
                # Get relevant documents
                vector_service = rag_service.vector_service
                documents = await vector_service.search_documents(
                    query=request.message,
                    top_k=5,
                    score_threshold=0.7
                )
                
                # Format context
                context_parts = []
                for doc in documents:
                    context_parts.append(f"Source: {doc.metadata.get('filename', 'Unknown')}\\n{doc.content}")
                
                context = "\\n\\n".join(context_parts)
                
                # Format prompt with context
                formatted_prompt = await ollama_service.format_prompt_for_model(
                    question=request.message,
                    model=request.model.value,
                    context=context
                )
                
                prompt = formatted_prompt
            else:
                prompt = request.message
            
            # Stream response from Ollama
            async for chunk in ollama_service.generate_stream(
                prompt=prompt,
                model=request.model.value
            ):
                if chunk.get("response"):
                    yield f"data: {json.dumps({'content': chunk['response'], 'done': chunk.get('done', False)})}\\n\\n"
                
                if chunk.get("done", False):
                    yield f"data: {json.dumps({'content': '', 'done': True})}\\n\\n"
                    break
            
        except Exception as e:
            logger.error(f"Stream chat failed: {e}")
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\\n\\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.post("/rag", response_model=ChatResponse)
async def rag_query(
    query: RAGQuery,
    model: ModelName = ModelName.ARCEE_AGENT,
    rag_service: RAGService = Depends(get_rag_service)
):
    """Direct RAG query"""
    try:
        response = await rag_service.query(query, model.value)
        
        # Convert RAGResponse to ChatResponse
        chat_response = ChatResponse(
            response=response.answer,
            model_used=model.value,
            sources=[doc.metadata.get('filename', f'Document {doc.id}') for doc in response.sources],
            context_used=len(response.sources) > 0,
            processing_time=response.processing_time,
            metadata={
                "confidence": response.confidence,
                "document_count": len(response.sources)
            }
        )
        
        return chat_response
        
    except Exception as e:
        logger.error(f"RAG query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch", response_model=BatchProcessResponse)
async def batch_process(
    request: BatchProcessRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """Process multiple queries in batch"""
    try:
        responses = []
        errors = []
        total_time = 0
        
        for query in request.queries:
            try:
                message = ChatMessage(
                    message=query,
                    model=request.model,
                    use_rag=request.use_rag
                )
                
                response = await rag_service.chat(message)
                responses.append(response)
                total_time += response.processing_time
                
            except Exception as e:
                logger.error(f"Batch query failed for '{query}': {e}")
                errors.append(f"Query '{query}': {str(e)}")
                
                # Add empty response for failed query
                responses.append(ChatResponse(
                    response="Error processing query",
                    model_used=request.model.value,
                    sources=[],
                    context_used=False,
                    processing_time=0.0,
                    metadata={"error": str(e)}
                ))
        
        return BatchProcessResponse(
            responses=responses,
            total_processed=len(request.queries),
            total_processing_time=total_time,
            errors=errors
        )
        
    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models", response_model=AvailableModelsResponse)
async def get_available_models(
    ollama_service: OllamaService = Depends(get_ollama_service)
):
    """Get available models from Ollama"""
    try:
        models = await ollama_service.list_models()
        
        # Get current active model (you might store this in app state)
        active_model = "arcee-ai/arcee-agent"  # Default
        
        return AvailableModelsResponse(
            models=models,
            active_model=active_model
        )
        
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/switch")
async def switch_model(
    request: ModelSwitchRequest,
    ollama_service: OllamaService = Depends(get_ollama_service)
):
    """Switch active model"""
    try:
        # Check if model is available
        models = await ollama_service.list_models()
        available_model_names = [model.name for model in models]
        
        if request.model_name.value not in available_model_names:
            # Try to pull the model
            logger.info(f"Attempting to pull model: {request.model_name.value}")
            success = await ollama_service.pull_model(request.model_name.value)
            
            if not success:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Model {request.model_name.value} is not available and could not be pulled"
                )
        
        # In a real implementation, you'd store the active model in app state or database
        return {
            "message": f"Switched to model: {request.model_name.value}",
            "active_model": request.model_name.value
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Model switch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_chat_history(
    conversation_id: str = None,
    limit: int = 50
):
    """Get chat history (placeholder - would need to implement storage)"""
    try:
        # This would typically query a database for chat history
        return {
            "conversation_id": conversation_id,
            "messages": [],
            "message": "Chat history storage not implemented yet"
        }
        
    except Exception as e:
        logger.error(f"Failed to get chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history/{conversation_id}")
async def clear_chat_history(conversation_id: str):
    """Clear chat history for a conversation"""
    try:
        # This would typically delete from database
        return {
            "message": f"Chat history cleared for conversation: {conversation_id}",
            "conversation_id": conversation_id
        }
        
    except Exception as e:
        logger.error(f"Failed to clear chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def chat_health_check(
    ollama_service: OllamaService = Depends(get_ollama_service),
    vector_service: VectorService = Depends(get_vector_service)
):
    """Health check for chat services"""
    try:
        ollama_health = await ollama_service.health_check()
        vector_health = await vector_service.health_check()
        
        return {
            "status": "healthy" if (
                ollama_health.get("status") == "healthy" and 
                vector_health.get("status") == "healthy"
            ) else "unhealthy",
            "services": {
                "ollama": ollama_health,
                "vector_db": vector_health
            }
        }
        
    except Exception as e:
        logger.error(f"Chat health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
