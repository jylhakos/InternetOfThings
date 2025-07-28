"""
FastAPI server for Redis Queue with LangChain and Ollama integration.
This server provides RESTful endpoints for asynchronous LLM processing.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from redis import Redis
from rq import Queue
from rq.job import Job
import uuid
import os
import time
import asyncio
from dotenv import load_dotenv
from typing import Optional, List, Union, Dict, Any
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Redis Queue with LangChain and Ollama",
    description="RESTful API for asynchronous LLM processing using RQ, FastAPI, and Ollama",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
try:
    redis_conn = Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        db=int(os.getenv('REDIS_DB', 0))
    )
    # Test Redis connection
    redis_conn.ping()
    logger.info("Successfully connected to Redis")
except Exception as e:
    logger.error(f"Failed to connect to Redis: {e}")
    raise

# Initialize RQ queue
q = Queue(connection=redis_conn)

# Pydantic models
class QuestionRequest(BaseModel):
    question: str
    model: Optional[str] = "llama3.2:1b"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 500

# New chat request model
class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = "llama3.2:1b"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 500
    system_prompt: Optional[str] = None

class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str

# New task response model
class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

class ResultResponse(BaseModel):
    job_id: str
    status: str
    result: Optional[str] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None
    message: Optional[str] = None

# New task result model  
class TaskResultResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[str] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None
    message: Optional[str] = None

# OpenAI-compatible models
class OpenAIMessage(BaseModel):
    role: str  # "system", "user", "assistant"
    content: str

class OpenAIChatCompletionRequest(BaseModel):
    model: str
    messages: List[OpenAIMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 500
    top_p: Optional[float] = 1.0
    frequency_penalty: Optional[float] = 0.0
    presence_penalty: Optional[float] = 0.0
    stream: Optional[bool] = False

class OpenAICompletionRequest(BaseModel):
    model: str
    prompt: Union[str, List[str]]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 500
    top_p: Optional[float] = 1.0
    frequency_penalty: Optional[float] = 0.0
    presence_penalty: Optional[float] = 0.0
    stream: Optional[bool] = False

class OpenAIChoice(BaseModel):
    index: int
    message: Optional[OpenAIMessage] = None
    text: Optional[str] = None
    finish_reason: str = "stop"

class OpenAIUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class OpenAIChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[OpenAIChoice]
    usage: OpenAIUsage

class OpenAICompletionResponse(BaseModel):
    id: str
    object: str = "text_completion"
    created: int
    model: str
    choices: List[OpenAIChoice]
    usage: OpenAIUsage

class OpenAIModel(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str = "redis-queue-system"

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Redis Queue with LangChain and Ollama API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "POST /chat",
            "task_status": "GET /task/{task_id}",
            "health": "GET /health",
            "models": "GET /models",
            "openai_chat": "POST /v1/chat/completions",
            "legacy_generate": "POST /generate_async/",
            "legacy_result": "GET /get_result/{job_id}"
        }
    }

@app.get("/health")
async def health_check():
    """System health check endpoint."""
    try:
        # Check Redis connection
        redis_conn.ping()
        redis_status = "healthy"
    except Exception:
        redis_status = "unhealthy"
    
    return {
        "status": "healthy" if redis_status == "healthy" else "unhealthy",
        "service": "Redis Queue LLM API",
        "version": "1.0.0",
        "redis": redis_status,
        "queue_size": len(q),
        "timestamp": time.time()
    }

@app.get("/models")
async def list_available_models():
    """Get available models endpoint."""
    try:
        models = [
            {
                "id": "llama3.2:1b",
                "name": "Llama 3.2 1B",
                "description": "Fast, lightweight model for quick responses",
                "parameters": "1B",
                "recommended_use": "Chat, Q&A, lightweight tasks"
            },
            {
                "id": "llama3.2:3b",
                "name": "Llama 3.2 3B", 
                "description": "Balanced model for general use",
                "parameters": "3B",
                "recommended_use": "General tasks, balanced performance"
            },
            {
                "id": "llama3.1:8b",
                "name": "Llama 3.1 8B",
                "description": "Advanced model for complex tasks",
                "parameters": "8B",
                "recommended_use": "Complex reasoning, detailed responses"
            },
            {
                "id": "codellama:7b",
                "name": "Code Llama 7B",
                "description": "Specialized model for code generation and analysis",
                "parameters": "7B",
                "recommended_use": "Code generation, programming assistance"
            },
            {
                "id": "mistral:7b",
                "name": "Mistral 7B",
                "description": "High-performance general-purpose model",
                "parameters": "7B",
                "recommended_use": "General tasks, high quality responses"
            }
        ]
        
        return {
            "models": models,
            "default_model": "llama3.2:1b",
            "total_models": len(models)
        }
    except Exception as e:
        logger.error(f"Error retrieving models: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving models: {str(e)}")

@app.post("/generate_async/", response_model=JobResponse)
async def generate_async(request: QuestionRequest):
    """
    Enqueue a job for asynchronous LLM processing.
    
    Args:
        request: QuestionRequest containing the question and optional parameters
        
    Returns:
        JobResponse with job_id and status
    """
    try:
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Prepare job data
        job_data = {
            "question": request.question,
            "model": request.model,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "job_id": job_id
        }
        
        # Enqueue the job
        job = q.enqueue(
            'worker.process_ollama_request',
            job_data,
            job_id=job_id,
            timeout='5m'  # 5-minute timeout
        )
        
        logger.info(f"Enqueued job {job_id} with question: {request.question[:50]}...")
        
        return JobResponse(
            job_id=job_id,
            status="queued",
            message="Your request is being processed. Use the job_id to check status and retrieve results."
        )
        
    except Exception as e:
        logger.error(f"Error enqueuing job: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to enqueue job: {str(e)}")

@app.post("/chat", response_model=TaskResponse)
async def submit_chat_request(request: ChatRequest):
    """
    Submit a chat request for asynchronous processing.
    
    Args:
        request: ChatRequest containing the message and optional parameters
        
    Returns:
        TaskResponse with task_id and status
    """
    try:
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Prepare job data with system prompt if provided
        question = request.message
        if request.system_prompt:
            question = f"System: {request.system_prompt}\n\nUser: {request.message}\n\nAssistant:"
        
        job_data = {
            "question": question,
            "model": request.model,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "job_id": task_id,
            "system_prompt": request.system_prompt
        }
        
        # Enqueue the job
        job = q.enqueue(
            'worker.process_ollama_request',
            job_data,
            job_id=task_id,
            timeout='5m'  # 5-minute timeout
        )
        
        logger.info(f"Enqueued chat task {task_id} with message: {request.message[:50]}...")
        
        return TaskResponse(
            task_id=task_id,
            status="queued",
            message="Your chat request is being processed. Use the task_id to check status and retrieve results."
        )
        
    except Exception as e:
        logger.error(f"Error enqueuing chat task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to enqueue chat task: {str(e)}")

@app.get("/get_result/{job_id}", response_model=ResultResponse)
async def get_result(job_id: str):
    """
    Retrieve the result of a processed job.
    
    Args:
        job_id: The unique identifier for the job
        
    Returns:
        ResultResponse with job status and result if completed
    """
    try:
        # Get job from Redis
        job = Job.fetch(job_id, connection=redis_conn)
        
        if job.is_finished:
            result = job.result
            return ResultResponse(
                job_id=job_id,
                status="finished",
                result=result.get("response") if isinstance(result, dict) else str(result),
                processing_time=result.get("processing_time") if isinstance(result, dict) else None
            )
        elif job.is_failed:
            return ResultResponse(
                job_id=job_id,
                status="failed",
                error=str(job.exc_info) if job.exc_info else "Job failed with unknown error"
            )
        elif job.is_started:
            return ResultResponse(
                job_id=job_id,
                status="started",
                message="Job is currently being processed"
            )
        else:  # queued
            return ResultResponse(
                job_id=job_id,
                status="queued",
                message="Job is waiting in queue"
            )
            
    except Exception as e:
        logger.error(f"Error retrieving job {job_id}: {e}")
        raise HTTPException(status_code=404, detail=f"Job not found or error retrieving job: {str(e)}")

@app.get("/task/{task_id}", response_model=TaskResultResponse)
async def get_task_status(task_id: str):
    """
    Check the status and result of a chat task.
    
    Args:
        task_id: The unique identifier for the task
        
    Returns:
        TaskResultResponse with task status and result if completed
    """
    try:
        # Get job from Redis using task_id
        job = Job.fetch(task_id, connection=redis_conn)
        
        if job.is_finished:
            result = job.result
            return TaskResultResponse(
                task_id=task_id,
                status="completed",
                result=result.get("response") if isinstance(result, dict) else str(result),
                processing_time=result.get("processing_time") if isinstance(result, dict) else None
            )
        elif job.is_failed:
            return TaskResultResponse(
                task_id=task_id,
                status="failed",
                error=str(job.exc_info) if job.exc_info else "Task failed with unknown error"
            )
        elif job.is_started:
            return TaskResultResponse(
                task_id=task_id,
                status="processing",
                message="Task is currently being processed"
            )
        else:  # queued
            return TaskResultResponse(
                task_id=task_id,
                status="queued",
                message="Task is waiting in queue"
            )
            
    except Exception as e:
        logger.error(f"Error retrieving task {task_id}: {e}")
        raise HTTPException(status_code=404, detail=f"Task not found or error retrieving task: {str(e)}")

@app.get("/job_status/{job_id}")
async def get_job_status(job_id: str):
    """
    Get current status of a job without full result details.
    
    Args:
        job_id: The unique identifier for the job
        
    Returns:
        Basic job status information
    """
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        
        status_info = {
            "job_id": job_id,
            "status": job.get_status(),
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "ended_at": job.ended_at.isoformat() if job.ended_at else None,
        }
        
        if job.is_started:
            status_info["progress"] = "Processing with Ollama..."
        elif job.is_queued:
            status_info["progress"] = f"Position in queue: {q.get_job_ids().index(job_id) + 1}"
        
        return status_info
        
    except Exception as e:
        logger.error(f"Error getting status for job {job_id}: {e}")
        raise HTTPException(status_code=404, detail=f"Job not found: {str(e)}")

@app.delete("/cancel_job/{job_id}")
async def cancel_job(job_id: str):
    """
    Cancel a queued or running job.
    
    Args:
        job_id: The unique identifier for the job
        
    Returns:
        Cancellation status
    """
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        
        if job.is_finished or job.is_failed:
            return {"job_id": job_id, "message": "Job already completed, cannot cancel"}
        
        job.cancel()
        return {"job_id": job_id, "message": "Job cancelled successfully"}
        
    except Exception as e:
        logger.error(f"Error cancelling job {job_id}: {e}")
        raise HTTPException(status_code=404, detail=f"Job not found or error cancelling: {str(e)}")

@app.get("/queue_info")
async def get_queue_info():
    """Get information about the current queue status."""
    try:
        return {
            "queue_length": len(q),
            "failed_jobs": len(q.failed_job_registry),
            "finished_jobs": len(q.finished_job_registry),
            "started_jobs": len(q.started_job_registry),
            "job_ids": q.get_job_ids()[:10]  # Show first 10 job IDs
        }
    except Exception as e:
        logger.error(f"Error getting queue info: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving queue information: {str(e)}")

# Helper functions for OpenAI compatibility
def verify_api_key(authorization: Optional[str] = Header(None)):
    """Simple API key verification for OpenAI compatibility."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    # Extract token from "Bearer <token>" format
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    # For demo purposes, accept any non-empty token
    token = authorization[7:]  # Remove "Bearer " prefix
    if not token or token.strip() == "":
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return token

def estimate_tokens(text: str) -> int:
    """Simple token estimation (roughly 4 characters per token)."""
    return len(text) // 4

def convert_messages_to_prompt(messages: List[OpenAIMessage]) -> str:
    """Convert OpenAI chat messages to a single prompt."""
    prompt_parts = []
    
    for message in messages:
        role = message.role
        content = message.content
        
        if role == "system":
            prompt_parts.append(f"System: {content}")
        elif role == "user":
            prompt_parts.append(f"User: {content}")
        elif role == "assistant":
            prompt_parts.append(f"Assistant: {content}")
    
    # Add a final prompt for the assistant to respond
    prompt_parts.append("Assistant:")
    
    return "\n\n".join(prompt_parts)

async def wait_for_job_completion(job_id: str, timeout: int = 300) -> Dict[str, Any]:
    """Wait for a job to complete and return the result."""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            job = Job.fetch(job_id, connection=redis_conn)
            
            if job.is_finished:
                result = job.result
                if isinstance(result, dict):
                    return {
                        "success": True,
                        "response": result.get("response", ""),
                        "processing_time": result.get("processing_time", 0)
                    }
                else:
                    return {
                        "success": True,
                        "response": str(result),
                        "processing_time": time.time() - start_time
                    }
            elif job.is_failed:
                return {
                    "success": False,
                    "error": str(job.exc_info) if job.exc_info else "Job failed"
                }
            
            # Wait a bit before checking again
            await asyncio.sleep(1)
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error checking job status: {str(e)}"
            }
    
    return {
        "success": False,
        "error": "Job timed out"
    }

# OpenAI-compatible API endpoints
@app.get("/v1/models")
async def list_models(authorization: Optional[str] = Header(None)):
    """List available models (OpenAI-compatible)."""
    verify_api_key(authorization)
    
    models = [
        OpenAIModel(
            id="llama3.2:1b",
            created=int(time.time()),
            owned_by="ollama"
        ),
        OpenAIModel(
            id="llama3.2:3b",
            created=int(time.time()),
            owned_by="ollama"
        ),
        OpenAIModel(
            id="llama3.1:8b",
            created=int(time.time()),
            owned_by="ollama"
        ),
        OpenAIModel(
            id="codellama:7b",
            created=int(time.time()),
            owned_by="ollama"
        ),
        OpenAIModel(
            id="mistral:7b",
            created=int(time.time()),
            owned_by="ollama"
        )
    ]
    
    return {
        "object": "list",
        "data": models
    }

@app.post("/v1/chat/completions", response_model=OpenAIChatCompletionResponse)
async def create_chat_completion(
    request: OpenAIChatCompletionRequest,
    authorization: Optional[str] = Header(None)
):
    """Create a chat completion (OpenAI-compatible)."""
    verify_api_key(authorization)
    
    try:
        # Convert messages to a single prompt
        prompt = convert_messages_to_prompt(request.messages)
        
        # Create job data
        job_data = {
            "question": prompt,
            "model": request.model,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "job_id": str(uuid.uuid4())
        }
        
        # Enqueue the job
        job = q.enqueue(
            'worker.process_ollama_request',
            job_data,
            job_id=job_data["job_id"],
            timeout='5m'
        )
        
        logger.info(f"Enqueued OpenAI-compatible job {job_data['job_id']}")
        
        # Wait for the job to complete
        result = await wait_for_job_completion(job_data["job_id"])
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Estimate token usage
        prompt_tokens = estimate_tokens(prompt)
        completion_tokens = estimate_tokens(result["response"])
        total_tokens = prompt_tokens + completion_tokens
        
        # Create OpenAI-compatible response
        response = OpenAIChatCompletionResponse(
            id=f"chatcmpl-{uuid.uuid4().hex[:8]}",
            created=int(time.time()),
            model=request.model,
            choices=[
                OpenAIChoice(
                    index=0,
                    message=OpenAIMessage(
                        role="assistant",
                        content=result["response"]
                    ),
                    finish_reason="stop"
                )
            ],
            usage=OpenAIUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens
            )
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in chat completion: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/completions", response_model=OpenAICompletionResponse)
async def create_completion(
    request: OpenAICompletionRequest,
    authorization: Optional[str] = Header(None)
):
    """Create a text completion (OpenAI-compatible)."""
    verify_api_key(authorization)
    
    try:
        # Handle both string and list prompts
        if isinstance(request.prompt, list):
            prompt = " ".join(request.prompt)
        else:
            prompt = request.prompt
        
        # Create job data
        job_data = {
            "question": prompt,
            "model": request.model,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "job_id": str(uuid.uuid4())
        }
        
        # Enqueue the job
        job = q.enqueue(
            'worker.process_ollama_request',
            job_data,
            job_id=job_data["job_id"],
            timeout='5m'
        )
        
        logger.info(f"Enqueued OpenAI-compatible completion job {job_data['job_id']}")
        
        # Wait for the job to complete
        result = await wait_for_job_completion(job_data["job_id"])
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Estimate token usage
        prompt_tokens = estimate_tokens(prompt)
        completion_tokens = estimate_tokens(result["response"])
        total_tokens = prompt_tokens + completion_tokens
        
        # Create OpenAI-compatible response
        response = OpenAICompletionResponse(
            id=f"cmpl-{uuid.uuid4().hex[:8]}",
            created=int(time.time()),
            model=request.model,
            choices=[
                OpenAIChoice(
                    index=0,
                    text=result["response"],
                    finish_reason="stop"
                )
            ],
            usage=OpenAIUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens
            )
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in completion: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=os.getenv('FASTAPI_HOST', '0.0.0.0'), 
        port=int(os.getenv('FASTAPI_PORT', 8000))
    )
