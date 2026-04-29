"""
AI Agent endpoints
"""
from fastapi import APIRouter, HTTPException
import logging

from app.models import (
    AgentQueryRequest, AgentQueryResponse,
    ChatMessage, ChatResponse, KnowledgeUpload
)
from app.main import get_vector_db_service, get_embedding_service, get_llm_service
from app.services.agent import AgentService

logger = logging.getLogger(__name__)
router = APIRouter()

# Global agent service instance
agent_service = None


def get_agent_service() -> AgentService:
    """Get or create agent service"""
    global agent_service
    
    if agent_service is None:
        vector_db = get_vector_db_service()
        embedding = get_embedding_service()
        llm = get_llm_service()
        
        if not all([vector_db, embedding, llm]):
            raise HTTPException(status_code=503, detail="Required services not initialized")
        
        agent_service = AgentService(vector_db, embedding, llm)
        logger.info("Initialized agent service")
    
    return agent_service


@router.post("/query", response_model=AgentQueryResponse)
async def agent_query(request: AgentQueryRequest):
    """
    Query the AI agent with optional RAG
    
    This endpoint:
    1. Optionally retrieves relevant context from vector DB (RAG)
    2. Generates response using LLM with context
    3. Returns response with sources
    """
    try:
        agent = get_agent_service()
        
        result = agent.query(
            query=request.query,
            use_rag=request.use_rag,
            top_k=request.top_k,
            collection=request.collection,
            session_id=request.session_id
        )
        
        return AgentQueryResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in agent query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=ChatResponse)
async def agent_chat(message: ChatMessage):
    """
    Chat with the agent using session memory
    
    Maintains conversation context across messages using session_id
    """
    try:
        agent = get_agent_service()
        
        result = agent.chat(
            message=message.message,
            session_id=message.session_id
        )
        
        return ChatResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in agent chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge")
async def upload_knowledge(upload: KnowledgeUpload):
    """
    Upload documents to agent's knowledge base
    
    Adds documents to vector database for RAG retrieval
    """
    try:
        agent = get_agent_service()
        
        result = agent.upload_knowledge(
            documents=upload.documents,
            collection=upload.collection
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error uploading knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))
