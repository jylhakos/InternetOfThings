#!/usr/bin/env python3
"""
LLM Inference Server: A Flask-based REST API server for Large Language Model inference.

This server demonstrates:
- Request handling and queuing
- Batch processing for efficiency
- KV cache simulation
- Performance metrics tracking
- Health checks and monitoring
"""

import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import deque
from dataclasses import dataclass, asdict
import threading

from flask import Flask, request, jsonify, Response
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class InferenceRequest:
    """Data class for inference requests"""
    prompt: str
    max_tokens: int = 100
    temperature: float = 0.7
    top_p: float = 0.9
    request_id: str = ""
    timestamp: float = 0.0


@dataclass
class InferenceResponse:
    """Data class for inference responses"""
    request_id: str
    prompt: str
    generated_text: str
    tokens_generated: int
    latency_ms: float
    ttft_ms: float  # Time to first token
    tpot_ms: float  # Time per output token
    timestamp: str


class InferenceMetrics:
    """Track inference performance metrics"""
    
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
    Mock LLM engine for demonstration purposes.
    In production, this would interface with actual models via:
    - vLLM
    - Hugging Face Transformers
    - TensorRT-LLM
    - etc.
    """
    
    def __init__(self):
        self.kv_cache = {}  # Simulate KV cache
        logger.info("MockLLMEngine initialized")
    
    def generate(
        self, 
        prompt: str, 
        max_tokens: int = 100, 
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> tuple[str, float, float]:
        """
        Simulate token generation with timing.
        
        Returns:
            tuple: (generated_text, ttft_ms, tpot_ms)
        """
        # Simulate prefill phase (Time to First Token)
        prefill_time = 0.08 + len(prompt.split()) * 0.002  # 80ms base + 2ms per word
        time.sleep(prefill_time)
        ttft_ms = prefill_time * 1000
        
        # Simulate decode phase (Time Per Output Token)
        tokens_to_generate = min(max_tokens, 150)  # Cap for demo
        decode_time_per_token = 0.015  # 15ms per token
        
        generated_tokens = []
        
        # Simulate token-by-token generation
        for i in range(tokens_to_generate):
            time.sleep(decode_time_per_token)
            # Generate mock token (in reality, this would be model inference)
            generated_tokens.append(f"token_{i}")
        
        # Create a mock response
        generated_text = f"This is a simulated response to: '{prompt[:50]}...' "
        generated_text += f"Generated {tokens_to_generate} tokens with temperature={temperature}, top_p={top_p}. "
        generated_text += "In production, this would be actual LLM-generated content."
        
        tpot_ms = decode_time_per_token * 1000
        
        return generated_text, ttft_ms, tpot_ms
    
    def batch_generate(
        self, 
        prompts: List[str], 
        max_tokens: int = 100
    ) -> List[tuple[str, float, float]]:
        """
        Simulate batch inference with continuous batching.
        In production, this would leverage GPU parallelism.
        """
        results = []
        
        # Simulate batch processing efficiency
        # Batching reduces overhead by processing multiple requests together
        batch_overhead = 0.05  # 50ms overhead for batch setup
        time.sleep(batch_overhead)
        
        for prompt in prompts:
            # In real batch processing, these would be parallelized
            result = self.generate(prompt, max_tokens)
            results.append(result)
        
        return results


# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Initialize components
llm_engine = MockLLMEngine()
metrics = InferenceMetrics()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "LLM Inference Server",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })


@app.route('/metrics', methods=['GET'])
def get_metrics():
    """Get server performance metrics"""
    return jsonify(metrics.get_metrics())


@app.route('/api/v1/inference', methods=['POST'])
def inference():
    """
    Single inference request endpoint.
    
    Request body:
    {
        "prompt": "Your input text",
        "max_tokens": 100,
        "temperature": 0.7,
        "top_p": 0.9
    }
    """
    try:
        # Parse request
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({"error": "Missing 'prompt' in request body"}), 400
        
        # Create inference request
        inf_request = InferenceRequest(
            prompt=data['prompt'],
            max_tokens=data.get('max_tokens', 100),
            temperature=data.get('temperature', 0.7),
            top_p=data.get('top_p', 0.9),
            request_id=f"req_{int(time.time() * 1000)}",
            timestamp=time.time()
        )
        
        logger.info(f"Processing inference request: {inf_request.request_id}")
        
        # Start timing
        start_time = time.time()
        
        # Generate response
        generated_text, ttft_ms, tpot_ms = llm_engine.generate(
            inf_request.prompt,
            inf_request.max_tokens,
            inf_request.temperature,
            inf_request.top_p
        )
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        tokens_generated = inf_request.max_tokens
        
        # Record metrics
        metrics.record_request(True, tokens_generated, latency_ms)
        
        # Create response
        response = InferenceResponse(
            request_id=inf_request.request_id,
            prompt=inf_request.prompt,
            generated_text=generated_text,
            tokens_generated=tokens_generated,
            latency_ms=round(latency_ms, 2),
            ttft_ms=round(ttft_ms, 2),
            tpot_ms=round(tpot_ms, 2),
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(
            f"Request {inf_request.request_id} completed in {latency_ms:.2f}ms"
        )
        
        return jsonify(asdict(response)), 200
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        metrics.record_request(False, 0, 0)
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/batch_inference', methods=['POST'])
def batch_inference():
    """
    Batch inference request endpoint.
    
    Request body:
    {
        "prompts": ["prompt1", "prompt2", ...],
        "max_tokens": 100
    }
    """
    try:
        # Parse request
        data = request.get_json()
        
        if not data or 'prompts' not in data:
            return jsonify({"error": "Missing 'prompts' in request body"}), 400
        
        prompts = data['prompts']
        max_tokens = data.get('max_tokens', 100)
        
        if not isinstance(prompts, list) or len(prompts) == 0:
            return jsonify({"error": "'prompts' must be a non-empty list"}), 400
        
        logger.info(f"Processing batch inference: {len(prompts)} prompts")
        
        # Start timing
        start_time = time.time()
        
        # Generate batch responses
        results = llm_engine.batch_generate(prompts, max_tokens)
        
        # Calculate latency
        total_latency_ms = (time.time() - start_time) * 1000
        
        # Create responses
        responses = []
        for i, (prompt, (generated_text, ttft_ms, tpot_ms)) in enumerate(
            zip(prompts, results)
        ):
            response = {
                "request_id": f"batch_req_{int(time.time() * 1000)}_{i}",
                "prompt": prompt,
                "generated_text": generated_text,
                "tokens_generated": max_tokens,
                "ttft_ms": round(ttft_ms, 2),
                "tpot_ms": round(tpot_ms, 2)
            }
            responses.append(response)
            
            # Record metrics for each request
            metrics.record_request(True, max_tokens, ttft_ms + (tpot_ms * max_tokens))
        
        logger.info(
            f"Batch request completed: {len(prompts)} prompts in {total_latency_ms:.2f}ms"
        )
        
        return jsonify({
            "batch_id": f"batch_{int(time.time() * 1000)}",
            "total_requests": len(prompts),
            "total_latency_ms": round(total_latency_ms, 2),
            "avg_latency_per_request_ms": round(total_latency_ms / len(prompts), 2),
            "responses": responses,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing batch request: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/stream_inference', methods=['POST'])
def stream_inference():
    """
    Streaming inference endpoint (Server-Sent Events).
    
    Request body:
    {
        "prompt": "Your input text",
        "max_tokens": 100
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({"error": "Missing 'prompt' in request body"}), 400
        
        prompt = data['prompt']
        max_tokens = data.get('max_tokens', 100)
        
        def generate_stream():
            """Generator for streaming tokens"""
            try:
                # Simulate prefill
                time.sleep(0.08)
                
                # Send first token
                yield f"data: {json.dumps({'status': 'started', 'token': '[START]'})}\n\n"
                
                # Simulate token-by-token generation
                for i in range(min(max_tokens, 20)):  # Cap at 20 for demo
                    time.sleep(0.015)  # 15ms per token
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
        
        return Response(
            generate_stream(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        logger.error(f"Error in streaming inference: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/models', methods=['GET'])
def list_models():
    """List available models"""
    models = [
        {
            "model_id": "mock-llm-7b",
            "name": "Mock LLM 7B",
            "parameters": "7B",
            "context_length": 4096,
            "status": "loaded"
        },
        {
            "model_id": "mock-llm-13b",
            "name": "Mock LLM 13B",
            "parameters": "13B",
            "context_length": 8192,
            "status": "available"
        }
    ]
    return jsonify({"models": models})


if __name__ == '__main__':
    logger.info("Starting LLM Inference Server...")
    logger.info("Server will be available at http://localhost:5000")
    logger.info("Available endpoints:")
    logger.info("  - GET  /health")
    logger.info("  - GET  /metrics")
    logger.info("  - POST /api/v1/inference")
    logger.info("  - POST /api/v1/batch_inference")
    logger.info("  - POST /api/v1/stream_inference")
    logger.info("  - GET  /api/v1/models")
    
    # Run server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
