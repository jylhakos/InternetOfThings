"""
FastAPI main application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.routes import documents, search, agent
from app.services.vector_db import VectorDBService
from app.services.embedding import EmbeddingService
from app.services.llm import LLMService
from app.models import HealthResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global service instances
vector_db_service = None
embedding_service = None
llm_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the application"""
    global vector_db_service, embedding_service, llm_service
    
    logger.info("Starting up Vector Database API...")
    
    # Initialize services
    try:
        embedding_service = EmbeddingService()
        logger.info(f"Initialized embedding service with model: {settings.embedding_model}")
        
        vector_db_service = VectorDBService()
        logger.info(f"Initialized vector database: {settings.vector_db_type}")
        
        llm_service = LLMService()
        logger.info(f"Initialized LLM service: {settings.llm_provider}")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("Shutting down...")
    if vector_db_service:
        vector_db_service.close()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Vector Database API for AI Agents with RAG capabilities",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(search.router, prefix="/api", tags=["Search"])
app.include_router(agent.router, prefix="/api/agent", tags=["AI Agent"])


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Vector Database API",
        "version": settings.app_version,
        "docs": "/docs",
        "status": "online"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    vector_db_status = "connected" if vector_db_service else "unavailable"
    llm_status = "available" if llm_service else "unavailable"
    
    return HealthResponse(
        status="healthy" if vector_db_service and llm_service else "degraded",
        vector_db=vector_db_status,
        llm=llm_status
    )


# Make services available to routes
def get_vector_db_service() -> VectorDBService:
    """Get vector database service instance"""
    return vector_db_service


def get_embedding_service() -> EmbeddingService:
    """Get embedding service instance"""
    return embedding_service


def get_llm_service() -> LLMService:
    """Get LLM service instance"""
    return llm_service


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
