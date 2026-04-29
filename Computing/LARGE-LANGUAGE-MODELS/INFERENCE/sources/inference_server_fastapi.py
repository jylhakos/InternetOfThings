#!/usr/bin/env python3
"""
LLM Inference Server: A FastAPI-based REST API server for Large Language Model inference.

This server demonstrates modern async patterns with:
- Async/await for concurrent request handling
- Pydantic models for request/response validation
- Automatic OpenAPI/Swagger documentation
- Server-Sent Events for streaming
- Better performance than Flask for production use

FastAPI advantages:
- Native async support for high concurrency
- Automatic API documentation (Swagger UI at /docs)
- Type safety with Pydantic validation
- Superior performance (2-3x faster than Flask)
- Modern Python 3.7+ typing support
"""

import time
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import deque
import threading

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Pydantic Models for Request/Response Validation
class InferenceRequest(BaseModel):
    """Request model for single inference"""
    prompt: str = Field(..., description="Input text prompt", min_length=1)
    max_tokens: int = Field(100, description="Maximum tokens to generate", ge=1, le=1000)
    temperature: float = Field(0.7, description="Sampling temperature", ge=0.0, le=2.0)
    top_p: float = Field(0.9, description="Nucleus sampling parameter", ge=0.0, le=1.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "What is the capital of France?",
                "max_tokens": 100,
                "temperature": 0.7,
                "top_p": 0.9
            }
        }


class BatchInferenceRequest(BaseModel):
    """Request model for batch inference"""
    prompts: List[str] = Field(..., description="List of input prompts", min_items=1)
    max_tokens: int = Field(100, description="Maximum tokens to generate per prompt", ge=1, le=1000)
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompts": [
                    "What is AI?",
                    "Explain machine learning",
                    "What are transformers?"
                ],
                "max_tokens": 100
            }
        }


class StreamInferenceRequest(BaseModel):
    """Request model for streaming inference"""
    prompt: str = Field(..., description="Input text prompt", min_length=1)
    max_tokens: int = Field(100, description="Maximum tokens to generate", ge=1, le=1000)


class InferenceResponse(BaseModel):
    """Response model for single inference"""
    request_id: str
    prompt: str
    generated_text: str
    tokens_generated: int
    latency_ms: float
    ttft_ms: float = Field(..., description="Time to First Token in milliseconds")
    tpot_ms: float = Field(..., description="Time Per Output Token in milliseconds")
    timestamp: str


class BatchResponse(BaseModel):
    """Response for a single item in batch"""
    request_id: str
    prompt: str
    generated_text: str
    tokens_generated: int
    ttft_ms: float
    tpot_ms: float


class BatchInferenceResponse(BaseModel):
    """Response model for batch inference"""
    batch_id: str
    total_requests: int
    total_latency_ms: float
    avg_latency_per_request_ms: float
    responses: List[BatchResponse]
    timestamp: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    timestamp: str
    version: str


class MetricsResponse(BaseModel):
    """Metrics response"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_tokens_generated: int
    average_latency_ms: float
    p95_latency_ms: float
    average_tokens_per_request: float
    success_rate: float


class ModelInfo(BaseModel):
    """Model information"""
    model_id: str
    name: str
    parameters: str
    context_length: int
    status: str


class ModelsResponse(BaseModel):
    """List of available models"""
    models: List[ModelInfo]


class InferenceMetrics:
    """Track inference performance metrics with thread-safe operations"""
    
    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_tokens_generated = 0
        self.total_latency_ms = 0.0
        self.request_latencies = deque(maxlen=100)  # Keep last 100
        self.lock = threading.Lock()
    
    def record_request(self, success: bool, tokens: int, latency_ms: float):
        """Record metrics for a request"""
        with self.lock:
            self.total_requests += 1
            if success:
                self.successful_requests += 1
                self.total_tokens_generated += tokens
                self.total_latency_ms += latency_ms
                self.request_latencies.append(latency_ms)
            else:
                self.failed_requests += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        with self.lock:
            avg_latency = (
                self.total_latency_ms / self.successful_requests 
                if self.successful_requests > 0 else 0
            )
            avg_tokens = (
                self.total_tokens_generated / self.successful_requests 
                if self.successful_requests > 0 else 0
            )
            
            # Calculate p95 latency
            p95_latency = 0.0
            if self.request_latencies:
                sorted_latencies = sorted(self.request_latencies)
                p95_index = int(len(sorted_latencies) * 0.95)
                p95_latency = sorted_latencies[p95_index]
            
            return {
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "failed_requests": self.failed_requests,
                "total_tokens_generated": self.total_tokens_generated,
                "average_latency_ms": round(avg_latency, 2),
                "p95_latency_ms": round(p95_latency, 2),
                "average_tokens_per_request": round(avg_tokens, 2),
                "success_rate": round(
                    (self.successful_requests / self.total_requests * 100) 
                    if self.total_requests > 0 else 0, 
                    2
                )
            }


class MockLLMEngine:
    """
    Mock LLM engine for demonstration purposes with async support.
    In production, this would interface with actual models via:
    - vLLM (has native async support)
    - Hugging Face Transformers
    - TensorRT-LLM
    - etc.
    """
    
    def __init__(self):
        self.kv_cache = {}  # Simulate KV cache
        logger.info("MockLLMEngine initialized (async version)")
    
    async def generate(
        self, 
        prompt: str, 
        max_tokens: int = 100, 
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> tuple[str, float, float]:
        """
        Simulate token generation with timing (async version).
        
        Returns:
            tuple: (generated_text, ttft_ms, tpot_ms)
        """
        # Simulate prefill phase (Time to First Token)
        prefill_time = 0.08 + len(prompt.split()) * 0.002  # 80ms base + 2ms per word
        await asyncio.sleep(prefill_time)
        ttft_ms = prefill_time * 1000
        
        # Simulate decode phase (Time Per Output Token)
        tokens_to_generate = min(max_tokens, 150)  # Cap for demo
        decode_time_per_token = 0.015  # 15ms per token
        
        generated_tokens = []
        
        # Simulate token-by-token generation (async)
        for i in range(tokens_to_generate):
            await asyncio.sleep(decode_time_per_token)
            # Generate mock token (in reality, this would be model inference)
            generated_tokens.append(f"token_{i}")
        
        # Create a mock response
        generated_text = f"This is a simulated response to: '{prompt[:50]}...' "
        generated_text += f"Generated {tokens_to_generate} tokens with temperature={temperature}, top_p={top_p}. "
        generated_text += "In production, this would be actual LLM-generated content from FastAPI async server."
        
        tpot_ms = decode_time_per_token * 1000
        
        return generated_text, ttft_ms, tpot_ms
    
    async def batch_generate(
        self, 
        prompts: List[str], 
        max_tokens: int = 100
    ) -> List[tuple[str, float, float]]:
        """
        Simulate batch inference with concurrent processing.
        FastAPI's async allows true concurrent processing of multiple requests.
        """
        # Simulate batch processing overhead
        batch_overhead = 0.05  # 50ms overhead for batch setup
        await asyncio.sleep(batch_overhead)
        
        # Process all prompts concurrently (this is where FastAPI shines!)
        tasks = [self.generate(prompt, max_tokens) for prompt in prompts]
        results = await asyncio.gather(*tasks)
        
        return results


# Initialize FastAPI app
app = FastAPI(
    title="LLM Inference Server (FastAPI)",
    description="High-performance async inference server for Large Language Models",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc UI
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
llm_engine = MockLLMEngine()
metrics = InferenceMetrics()


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("FastAPI LLM Inference Server starting up...")
    logger.info("Interactive API docs available at: http://localhost:8000/docs")
    logger.info("Alternative docs available at: http://localhost:8000/redoc")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("FastAPI LLM Inference Server shutting down...")


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify server is running.
    
    Returns server status and basic information.
    """
    return HealthResponse(
        status="healthy",
        service="LLM Inference Server (FastAPI)",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )


@app.get("/metrics", response_model=MetricsResponse, tags=["Monitoring"])
async def get_metrics():
    """
    Get server performance metrics.
    
    Returns detailed performance statistics including:
    - Total requests processed
    - Success/failure rates
    - Latency statistics (average and P95)
    - Token generation metrics
    """
    return metrics.get_metrics()


@app.post("/api/v1/inference", response_model=InferenceResponse, tags=["Inference"])
async def inference(request: InferenceRequest):
    """
    Single inference request endpoint.
    
    Processes a single prompt and returns generated text with detailed metrics.
    
    **Example:**
    ```json
    {
        "prompt": "What is the capital of France?",
        "max_tokens": 100,
        "temperature": 0.7,
        "top_p": 0.9
    }
    ```
    """
    try:
        request_id = f"req_{int(time.time() * 1000)}"
        logger.info(f"Processing inference request: {request_id}")
        
        # Start timing
        start_time = time.time()
        
        # Generate response (async!)
        generated_text, ttft_ms, tpot_ms = await llm_engine.generate(
            request.prompt,
            request.max_tokens,
            request.temperature,
            request.top_p
        )
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        tokens_generated = request.max_tokens
        
        # Record metrics
        metrics.record_request(True, tokens_generated, latency_ms)
        
        # Create response
        response = InferenceResponse(
            request_id=request_id,
            prompt=request.prompt,
            generated_text=generated_text,
            tokens_generated=tokens_generated,
            latency_ms=round(latency_ms, 2),
            ttft_ms=round(ttft_ms, 2),
            tpot_ms=round(tpot_ms, 2),
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"Request {request_id} completed in {latency_ms:.2f}ms")
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        metrics.record_request(False, 0, 0)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/batch_inference", response_model=BatchInferenceResponse, tags=["Inference"])
async def batch_inference(request: BatchInferenceRequest):
    """
    Batch inference request endpoint.
    
    Processes multiple prompts concurrently (FastAPI async advantage!).
    
    **Example:**
    ```json
    {
        "prompts": [
            "What is AI?",
            "Explain machine learning",
            "What are transformers?"
        ],
        "max_tokens": 100
    }
    ```
    """
    try:
        logger.info(f"Processing batch inference: {len(request.prompts)} prompts")
        
        # Start timing
        start_time = time.time()
        
        # Generate batch responses (concurrent with asyncio.gather!)
        results = await llm_engine.batch_generate(request.prompts, request.max_tokens)
        
        # Calculate latency
        total_latency_ms = (time.time() - start_time) * 1000
        
        # Create responses
        responses = []
        for i, (prompt, (generated_text, ttft_ms, tpot_ms)) in enumerate(
            zip(request.prompts, results)
        ):
            batch_response = BatchResponse(
                request_id=f"batch_req_{int(time.time() * 1000)}_{i}",
                prompt=prompt,
                generated_text=generated_text,
                tokens_generated=request.max_tokens,
                ttft_ms=round(ttft_ms, 2),
                tpot_ms=round(tpot_ms, 2)
            )
            responses.append(batch_response)
            
            # Record metrics for each request
            metrics.record_request(
                True, 
                request.max_tokens, 
                ttft_ms + (tpot_ms * request.max_tokens)
            )
        
        logger.info(
            f"Batch request completed: {len(request.prompts)} prompts in {total_latency_ms:.2f}ms"
        )
        
        return BatchInferenceResponse(
            batch_id=f"batch_{int(time.time() * 1000)}",
            total_requests=len(request.prompts),
            total_latency_ms=round(total_latency_ms, 2),
            avg_latency_per_request_ms=round(total_latency_ms / len(request.prompts), 2),
            responses=responses,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error processing batch request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/stream_inference", tags=["Inference"])
async def stream_inference(request: StreamInferenceRequest):
    """
    Streaming inference endpoint (Server-Sent Events).
    
    Streams tokens as they are generated, providing real-time feedback.
    
    **Example:**
    ```json
    {
        "prompt": "Explain quantum computing",
        "max_tokens": 100
    }
    ```
    
    **Response Format:** Server-Sent Events (SSE)
    """
    async def generate_stream():
        """Async generator for streaming tokens"""
        try:
            # Simulate prefill
            await asyncio.sleep(0.08)
            
            # Send first token
            yield f"data: {json.dumps({'status': 'started', 'token': '[START]'})}\n\n"
            
            # Simulate token-by-token generation
            for i in range(min(request.max_tokens, 20)):  # Cap at 20 for demo
                await asyncio.sleep(0.015)  # 15ms per token
                token_data = {
                    "status": "generating",
                    "token": f"token_{i}",
                    "token_index": i
                }
                yield f"data: {json.dumps(token_data)}\n\n"
            
            # Send completion
            yield f"data: {json.dumps({'status': 'completed'})}\n\n"
            
        except Exception as e:
            error_data = {"status": "error", "error": str(e)}
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/api/v1/models", response_model=ModelsResponse, tags=["Models"])
async def list_models():
    """
    List available models.
    
    Returns information about all models that can be used for inference.
    """
    models = [
        ModelInfo(
            model_id="mock-llm-7b",
            name="Mock LLM 7B",
            parameters="7B",
            context_length=4096,
            status="loaded"
        ),
        ModelInfo(
            model_id="mock-llm-13b",
            name="Mock LLM 13B",
            parameters="13B",
            context_length=8192,
            status="available"
        ),
        ModelInfo(
            model_id="mock-llm-70b",
            name="Mock LLM 70B",
            parameters="70B",
            context_length=8192,
            status="available"
        )
    ]
    return ModelsResponse(models=models)


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "service": "LLM Inference Server (FastAPI)",
        "version": "1.0.0",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        },
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "inference": "/api/v1/inference",
            "batch_inference": "/api/v1/batch_inference",
            "stream_inference": "/api/v1/stream_inference",
            "models": "/api/v1/models"
        }
    }


if __name__ == '__main__':
    import uvicorn
    
    logger.info("Starting FastAPI LLM Inference Server...")
    logger.info("Server will be available at http://localhost:8000")
    logger.info("Interactive API documentation at http://localhost:8000/docs")
    logger.info("\nAvailable endpoints:")
    logger.info("  - GET  /              (API information)")
    logger.info("  - GET  /health        (Health check)")
    logger.info("  - GET  /metrics       (Performance metrics)")
    logger.info("  - GET  /docs          (Swagger UI)")
    logger.info("  - GET  /redoc         (ReDoc documentation)")
    logger.info("  - POST /api/v1/inference         (Single inference)")
    logger.info("  - POST /api/v1/batch_inference   (Batch inference)")
    logger.info("  - POST /api/v1/stream_inference  (Streaming inference)")
    logger.info("  - GET  /api/v1/models            (List models)")
    
    # Run with uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )
