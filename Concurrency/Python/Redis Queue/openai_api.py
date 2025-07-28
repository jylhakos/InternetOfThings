"""
OpenAI-compatible API endpoints for Open WebUI integration.
These endpoints provide compatibility with OpenAI's API format.
"""

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import time
import uuid
import json
import asyncio
from datetime import datetime

# These will be imported when the router is included in main.py
# from main import q, redis_conn, logger
# from rq.job import Job

router = APIRouter(prefix="/v1")

# OpenAI-compatible models
class OpenAIModel(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str = "redis-queue-system"

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

def verify_api_key(authorization: Optional[str] = Header(None)):
    """Simple API key verification for OpenAI compatibility."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    # Extract token from "Bearer <token>" format
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    # For demo purposes, accept any non-empty token
    # In production, implement proper API key validation
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

@router.get("/models")
async def list_models(api_key: str = Header(None, alias="Authorization")):
    """List available models (OpenAI-compatible)."""
    verify_api_key(api_key)
    
    # Define available models
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

@router.post("/chat/completions")
async def create_chat_completion(
    request: OpenAIChatCompletionRequest,
    api_key: str = Header(None, alias="Authorization")
):
    """Create a chat completion (OpenAI-compatible)."""
    verify_api_key(api_key)
    
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

@router.post("/completions")
async def create_completion(
    request: OpenAICompletionRequest,
    api_key: str = Header(None, alias="Authorization")
):
    """Create a text completion (OpenAI-compatible)."""
    verify_api_key(api_key)
    
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

# Add error handling for unsupported endpoints
@router.get("/engines")
async def list_engines():
    """Legacy engines endpoint redirect."""
    return {"error": "This endpoint is deprecated. Use /v1/models instead."}

@router.post("/embeddings")
async def create_embeddings():
    """Embeddings endpoint (not implemented)."""
    raise HTTPException(
        status_code=501, 
        detail="Embeddings endpoint not implemented in this system"
    )
