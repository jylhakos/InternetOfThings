from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
from contextlib import asynccontextmanager
from loguru import logger

from app.routers import documents, chat
from app.core.config import settings
from app.services.vector_service import VectorService
from app.services.ollama_service import OllamaService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting FastAPI RAG application...")
    
    # Initialize services
    try:
        vector_service = VectorService()
        await vector_service.initialize()
        app.state.vector_service = vector_service
        logger.info("Vector service initialized")
        
        ollama_service = OllamaService()
        await ollama_service.health_check()
        app.state.ollama_service = ollama_service
        logger.info("Ollama service connected")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI RAG application...")


app = FastAPI(
    title="LangGraph RAG System",
    description="A comprehensive RAG system with LangGraph, Ollama, and Qdrant",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
os.makedirs("uploads", exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "LangGraph RAG System API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check vector service
        vector_service = app.state.vector_service
        vector_status = await vector_service.health_check()
        
        # Check Ollama service
        ollama_service = app.state.ollama_service
        ollama_status = await ollama_service.health_check()
        
        return {
            "status": "healthy",
            "services": {
                "vector_db": vector_status,
                "ollama": ollama_status
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.FASTAPI_HOST,
        port=settings.FASTAPI_PORT,
        reload=True
    )
