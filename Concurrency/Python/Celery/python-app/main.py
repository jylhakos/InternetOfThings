from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import uvicorn
import logging
from datetime import datetime

from celery_app import celery_app
from tasks import process_llm_request, health_check_langchain_service, get_available_models
from config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="LLM Processing API",
    description="FastAPI server with Celery for asynchronous LLM processing using LangChain.js and Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response validation
class ChatRequest(BaseModel):
    prompt: str = Field(..., description="The input prompt for the LLM")
    model: Optional[str] = Field(None, description="Model name to use")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Temperature for response generation")
    max_tokens: int = Field(1000, ge=1, le=4000, description="Maximum number of tokens in response")

class ChatResponse(BaseModel):
    task_id: str = Field(..., description="Task ID for tracking the request")
    status: str = Field(..., description="Current status of the task")
    message: str = Field(..., description="Status message")

class TaskStatusResponse(BaseModel):
    task_id: str = Field(..., description="Task ID")
    status: str = Field(..., description="Current status")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result if completed")
    error: Optional[str] = Field(None, description="Error message if failed")
    meta: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Health status")
    timestamp: str = Field(..., description="Current timestamp")
    services: Dict[str, Any] = Field(..., description="Status of dependent services")

@app.post("/chat", response_model=ChatResponse)
async def create_chat_request(request: ChatRequest):
    """
    Submit a chat request for asynchronous processing
    
    This endpoint accepts a chat prompt and delegates the LLM processing
    to a Celery worker. Returns immediately with a task ID that can be
    used to check the status and retrieve results.
    """
    try:
        # Submit task to Celery
        task = process_llm_request.delay(
            prompt=request.prompt,
            model_name=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        logger.info(f"Chat request submitted with task ID: {task.id}")
        
        return ChatResponse(
            task_id=task.id,
            status="PENDING",
            message="Request submitted for processing"
        )
        
    except Exception as e:
        logger.error(f"Error submitting chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to submit request: {str(e)}")

@app.get("/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Get the status and result of a specific task
    
    Use this endpoint to check the progress of a chat request
    and retrieve the result once processing is complete.
    """
    try:
        # Get task result from Celery
        task_result = celery_app.AsyncResult(task_id)
        
        if task_result.state == 'PENDING':
            response = TaskStatusResponse(
                task_id=task_id,
                status='PENDING',
                meta={'message': 'Task is waiting to be processed'}
            )
        elif task_result.state == 'PROCESSING':
            response = TaskStatusResponse(
                task_id=task_id,
                status='PROCESSING',
                meta=task_result.info
            )
        elif task_result.state == 'SUCCESS':
            response = TaskStatusResponse(
                task_id=task_id,
                status='SUCCESS',
                result=task_result.result
            )
        elif task_result.state == 'FAILURE':
            response = TaskStatusResponse(
                task_id=task_id,
                status='FAILURE',
                error=str(task_result.info),
                meta={'message': 'Task failed during processing'}
            )
        else:
            response = TaskStatusResponse(
                task_id=task_id,
                status=task_result.state,
                meta=task_result.info if hasattr(task_result, 'info') else {}
            )
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting task status for {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns the health status of the API and its dependent services
    """
    try:
        # Check Celery connection
        celery_status = "healthy"
        try:
            # Try to get Celery stats
            inspect = celery_app.control.inspect()
            active_tasks = inspect.active()
            if active_tasks is None:
                celery_status = "unhealthy - no workers available"
        except Exception:
            celery_status = "unhealthy - connection failed"
        
        # Check LangChain service (async task)
        langchain_task = health_check_langchain_service.delay()
        langchain_result = langchain_task.get(timeout=10)
        langchain_status = "healthy" if langchain_result.get('success') else f"unhealthy - {langchain_result.get('error')}"
        
        overall_status = "healthy" if celery_status == "healthy" and langchain_status == "healthy" else "degraded"
        
        return HealthResponse(
            status=overall_status,
            timestamp=datetime.utcnow().isoformat(),
            services={
                "celery": celery_status,
                "langchain_service": langchain_status,
                "redis": "healthy" if celery_status == "healthy" else "unknown"
            }
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.utcnow().isoformat(),
            services={
                "celery": "unknown",
                "langchain_service": "unknown",
                "redis": "unknown",
                "error": str(e)
            }
        )

@app.get("/models")
async def get_models():
    """
    Get available LLM models
    
    Returns a list of available models from the LangChain service
    """
    try:
        # Get models from LangChain service (async task)
        models_task = get_available_models.delay()
        result = models_task.get(timeout=10)
        
        if result.get('success'):
            return {
                "models": result.get('models', []),
                "default_model": result.get('default_model'),
                "status": "success"
            }
        else:
            raise HTTPException(status_code=503, detail=f"Failed to get models: {result.get('error')}")
            
    except Exception as e:
        logger.error(f"Error getting models: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve models: {str(e)}")

@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": "LLM Processing API with FastAPI and Celery",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "POST /chat": "Submit chat request",
            "GET /task/{task_id}": "Get task status",
            "GET /models": "Get available models",
            "GET /health": "Health check"
        }
    }

# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
