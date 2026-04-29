#!/usr/bin/env python3
"""
FastAPI LLM Inference Client Examples

This script demonstrates how to interact with the FastAPI-based inference server.
It shows various client patterns including:
- Single inference requests
- Batch inference
- Streaming inference with Server-Sent Events
- Error handling
- Performance measurement

Run the FastAPI server first:
    python sources/inference_server_fastapi.py

Or with uvicorn:
    uvicorn sources.inference_server_fastapi:app --reload --port 8000
"""

import requests
import json
import time
from typing import List, Dict, Any


class FastAPIInferenceClient:
    """Client for interacting with FastAPI LLM Inference Server"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the client.
        
        Args:
            base_url: Base URL of the FastAPI inference server
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def health_check(self) -> Dict[str, Any]:
        """Check if the server is healthy"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get server performance metrics"""
        response = self.session.get(f"{self.base_url}/metrics")
        response.raise_for_status()
        return response.json()
    
    def list_models(self) -> Dict[str, Any]:
        """List available models"""
        response = self.session.get(f"{self.base_url}/api/v1/models")
        response.raise_for_status()
        return response.json()
    
    def inference(
        self,
        prompt: str,
        max_tokens: int = 100,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> Dict[str, Any]:
        """
        Send a single inference request.
        
        Args:
            prompt: Input text prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
        
        Returns:
            Response dictionary with generated text and metrics
        """
        payload = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p
        }
        
        response = self.session.post(
            f"{self.base_url}/api/v1/inference",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def batch_inference(
        self,
        prompts: List[str],
        max_tokens: int = 100
    ) -> Dict[str, Any]:
        """
        Send a batch inference request.
        
        Args:
            prompts: List of input prompts
            max_tokens: Maximum tokens to generate per prompt
        
        Returns:
            Response dictionary with all results and metrics
        """
        payload = {
            "prompts": prompts,
            "max_tokens": max_tokens
        }
        
        response = self.session.post(
            f"{self.base_url}/api/v1/batch_inference",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def stream_inference(
        self,
        prompt: str,
        max_tokens: int = 100
    ):
        """
        Send a streaming inference request (Server-Sent Events).
        
        Args:
            prompt: Input text prompt
            max_tokens: Maximum tokens to generate
        
        Yields:
            Streaming events as they arrive
        """
        payload = {
            "prompt": prompt,
            "max_tokens": max_tokens
        }
        
        response = self.session.post(
            f"{self.base_url}/api/v1/stream_inference",
            json=payload,
            stream=True
        )
        response.raise_for_status()
        
        # Parse Server-Sent Events
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data = json.loads(line_str[6:])
                    yield data


# Example Functions

def example_health_check():
    """Example: Check server health"""
    print("\n" + "="*60)
    print("Example 1: Health Check")
    print("="*60)
    
    client = FastAPIInferenceClient()
    
    try:
        health = client.health_check()
        print(f"✓ Server Status: {health['status']}")
        print(f"  Service: {health['service']}")
        print(f"  Version: {health['version']}")
        print(f"  Timestamp: {health['timestamp']}")
    except requests.exceptions.ConnectionError:
        print("✗ Error: Cannot connect to server. Make sure it's running on port 8000")
        print("  Start with: python sources/inference_server_fastapi.py")
    except Exception as e:
        print(f"✗ Error: {e}")


def example_single_inference():
    """Example: Single inference request"""
    print("\n" + "="*60)
    print("Example 2: Single Inference Request")
    print("="*60)
    
    client = FastAPIInferenceClient()
    
    prompt = "What are the key differences between Flask and FastAPI?"
    print(f"Prompt: {prompt}")
    print("\nSending request...")
    
    try:
        start_time = time.time()
        response = client.inference(
            prompt=prompt,
            max_tokens=100,
            temperature=0.7
        )
        elapsed = (time.time() - start_time) * 1000
        
        print(f"\n✓ Request completed in {elapsed:.2f}ms")
        print(f"  Request ID: {response['request_id']}")
        print(f"  Generated Text: {response['generated_text'][:100]}...")
        print(f"  Tokens Generated: {response['tokens_generated']}")
        print(f"  Time to First Token: {response['ttft_ms']:.2f}ms")
        print(f"  Time per Output Token: {response['tpot_ms']:.2f}ms")
        print(f"  Total Latency: {response['latency_ms']:.2f}ms")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_batch_inference():
    """Example: Batch inference request"""
    print("\n" + "="*60)
    print("Example 3: Batch Inference Request")
    print("="*60)
    
    client = FastAPIInferenceClient()
    
    prompts = [
        "What is async programming?",
        "Explain FastAPI advantages",
        "What is Server-Sent Events?",
        "How does Pydantic work?"
    ]
    
    print(f"Processing {len(prompts)} prompts:")
    for i, p in enumerate(prompts, 1):
        print(f"  {i}. {p}")
    
    print("\nSending batch request...")
    
    try:
        start_time = time.time()
        response = client.batch_inference(prompts=prompts, max_tokens=50)
        elapsed = (time.time() - start_time) * 1000
        
        print(f"\n✓ Batch request completed in {elapsed:.2f}ms")
        print(f"  Batch ID: {response['batch_id']}")
        print(f"  Total Requests: {response['total_requests']}")
        print(f"  Total Latency: {response['total_latency_ms']:.2f}ms")
        print(f"  Avg Latency per Request: {response['avg_latency_per_request_ms']:.2f}ms")
        
        print("\n  Individual Results:")
        for i, result in enumerate(response['responses'], 1):
            print(f"    {i}. TTFT: {result['ttft_ms']:.2f}ms, "
                  f"TPOT: {result['tpot_ms']:.2f}ms, "
                  f"Tokens: {result['tokens_generated']}")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_streaming_inference():
    """Example: Streaming inference with Server-Sent Events"""
    print("\n" + "="*60)
    print("Example 4: Streaming Inference")
    print("="*60)
    
    client = FastAPIInferenceClient()
    
    prompt = "Explain the benefits of async/await in Python"
    print(f"Prompt: {prompt}")
    print("\nStreaming tokens...\n")
    
    try:
        token_count = 0
        start_time = time.time()
        first_token_time = None
        
        for event in client.stream_inference(prompt=prompt, max_tokens=20):
            if event['status'] == 'started':
                print(f"[{event['status'].upper()}] Received first token")
                first_token_time = time.time()
            elif event['status'] == 'generating':
                token_count += 1
                print(f"  Token {event['token_index']}: {event['token']}")
            elif event['status'] == 'completed':
                elapsed = (time.time() - start_time) * 1000
                ttft = (first_token_time - start_time) * 1000 if first_token_time else 0
                print(f"\n[{event['status'].upper()}]")
                print(f"  Total tokens: {token_count}")
                print(f"  Time to first token: {ttft:.2f}ms")
                print(f"  Total time: {elapsed:.2f}ms")
            elif event['status'] == 'error':
                print(f"✗ Error during streaming: {event['error']}")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_list_models():
    """Example: List available models"""
    print("\n" + "="*60)
    print("Example 5: List Available Models")
    print("="*60)
    
    client = FastAPIInferenceClient()
    
    try:
        response = client.list_models()
        models = response['models']
        
        print(f"Available Models: {len(models)}\n")
        for i, model in enumerate(models, 1):
            print(f"{i}. {model['name']} ({model['model_id']})")
            print(f"   Parameters: {model['parameters']}")
            print(f"   Context Length: {model['context_length']:,} tokens")
            print(f"   Status: {model['status']}")
            print()
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_metrics():
    """Example: Get server metrics"""
    print("\n" + "="*60)
    print("Example 6: Server Metrics")
    print("="*60)
    
    client = FastAPIInferenceClient()
    
    try:
        metrics = client.get_metrics()
        
        print("Server Performance Metrics:\n")
        print(f"  Total Requests: {metrics['total_requests']}")
        print(f"  Successful: {metrics['successful_requests']}")
        print(f"  Failed: {metrics['failed_requests']}")
        print(f"  Success Rate: {metrics['success_rate']}%")
        print(f"\n  Total Tokens Generated: {metrics['total_tokens_generated']}")
        print(f"  Avg Tokens/Request: {metrics['average_tokens_per_request']:.2f}")
        print(f"\n  Average Latency: {metrics['average_latency_ms']:.2f}ms")
        print(f"  P95 Latency: {metrics['p95_latency_ms']:.2f}ms")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_load_test():
    """Example: Simple load test"""
    print("\n" + "="*60)
    print("Example 7: Load Test")
    print("="*60)
    
    client = FastAPIInferenceClient()
    
    num_requests = 10
    print(f"Sending {num_requests} concurrent-style requests...")
    print("(Note: Using requests library, not truly concurrent)")
    print("For true concurrency, use asyncio with httpx")
    
    prompts = [f"Test prompt number {i+1}" for i in range(num_requests)]
    
    try:
        start_time = time.time()
        
        # Send requests sequentially (for true concurrency, use asyncio)
        responses = []
        for i, prompt in enumerate(prompts, 1):
            response = client.inference(prompt=prompt, max_tokens=50)
            responses.append(response)
            print(f"  Request {i}/{num_requests} completed")
        
        elapsed = time.time() - start_time
        
        print(f"\n✓ Load test completed")
        print(f"  Total time: {elapsed:.2f}s")
        print(f"  Requests: {num_requests}")
        print(f"  Avg time per request: {(elapsed/num_requests):.3f}s")
        print(f"  Throughput: {num_requests/elapsed:.2f} req/s")
        
        # Calculate token stats
        total_tokens = sum(r['tokens_generated'] for r in responses)
        print(f"  Total tokens: {total_tokens}")
        print(f"  Tokens per second: {total_tokens/elapsed:.2f}")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_error_handling():
    """Example: Error handling and validation"""
    print("\n" + "="*60)
    print("Example 8: Error Handling")
    print("="*60)
    
    client = FastAPIInferenceClient()
    
    print("Testing error scenarios:\n")
    
    # Test 1: Empty prompt
    print("1. Empty prompt (should fail with validation error)")
    try:
        response = client.inference(prompt="", max_tokens=50)
        print("   ✗ Unexpected: Request succeeded")
    except requests.exceptions.HTTPError as e:
        print(f"   ✓ Expected error: {e.response.status_code} - Validation failed")
    
    # Test 2: Invalid max_tokens
    print("\n2. Invalid max_tokens = 0 (should fail with validation error)")
    try:
        response = client.inference(prompt="Test", max_tokens=0)
        print("   ✗ Unexpected: Request succeeded")
    except requests.exceptions.HTTPError as e:
        print(f"   ✓ Expected error: {e.response.status_code} - Validation failed")
    
    # Test 3: Invalid temperature
    print("\n3. Invalid temperature = 3.0 (should fail with validation error)")
    try:
        response = client.inference(prompt="Test", temperature=3.0)
        print("   ✗ Unexpected: Request succeeded")
    except requests.exceptions.HTTPError as e:
        print(f"   ✓ Expected error: {e.response.status_code} - Validation failed")
    
    print("\n✓ FastAPI's Pydantic validation caught all invalid inputs!")
    print("  This is automatic - no manual validation code needed")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("FastAPI LLM Inference Client Examples")
    print("="*60)
    print("\nMake sure the FastAPI server is running:")
    print("  python sources/inference_server_fastapi.py")
    print("\nAPI Documentation available at:")
    print("  http://localhost:8000/docs (Swagger UI)")
    print("  http://localhost:8000/redoc (ReDoc)")
    
    # Run examples
    example_health_check()
    example_single_inference()
    example_batch_inference()
    example_streaming_inference()
    example_list_models()
    example_metrics()
    example_load_test()
    example_error_handling()
    
    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60)
    print("\nNext steps:")
    print("  - Visit http://localhost:8000/docs for interactive API testing")
    print("  - Check metrics at http://localhost:8000/metrics")
    print("  - Compare performance with Flask version (port 5000)")


if __name__ == '__main__':
    main()
