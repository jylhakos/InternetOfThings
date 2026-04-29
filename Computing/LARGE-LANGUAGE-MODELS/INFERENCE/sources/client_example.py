#!/usr/bin/env python3
"""
LLM Inference Client Example: Demonstrates how to interact with the inference server using Python.
"""

import requests
import json
import time
from typing import Dict, Any, List


class InferenceClient:
    """Client for interacting with LLM Inference Server"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """Check server health"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get server metrics"""
        response = self.session.get(f"{self.base_url}/metrics")
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
        Send single inference request.
        
        Args:
            prompt: Input text prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 2.0)
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
        Send batch inference request.
        
        Args:
            prompts: List of input prompts
            max_tokens: Maximum tokens per prompt
            
        Returns:
            Batch response with all results
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
    
    def stream_inference(self, prompt: str, max_tokens: int = 100):
        """
        Stream inference tokens as they're generated.
        
        Args:
            prompt: Input text prompt
            max_tokens: Maximum tokens to generate
            
        Yields:
            Token data as it's generated
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
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    yield data
    
    def list_models(self) -> Dict[str, Any]:
        """List available models"""
        response = self.session.get(f"{self.base_url}/api/v1/models")
        response.raise_for_status()
        return response.json()


def print_section(title: str):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def example_health_check(client: InferenceClient):
    """Example: Health check"""
    print_section("Health Check")
    
    try:
        health = client.health_check()
        print(f"✓ Server Status: {health['status']}")
        print(f"✓ Service: {health['service']}")
        print(f"✓ Version: {health['version']}")
        print(f"✓ Timestamp: {health['timestamp']}")
    except Exception as e:
        print(f"✗ Error: {e}")


def example_single_inference(client: InferenceClient):
    """Example: Single inference request"""
    print_section("Single Inference Request")
    
    prompt = "Explain how Large Language Models work in simple terms."
    
    print(f"Prompt: {prompt}\n")
    print("Sending request...")
    
    try:
        start_time = time.time()
        response = client.inference(prompt, max_tokens=50, temperature=0.8)
        elapsed = (time.time() - start_time) * 1000
        
        print(f"\n✓ Request ID: {response['request_id']}")
        print(f"✓ Generated Text:\n  {response['generated_text']}\n")
        print(f"✓ Tokens Generated: {response['tokens_generated']}")
        print(f"✓ Total Latency: {response['latency_ms']:.2f}ms")
        print(f"✓ Time to First Token: {response['ttft_ms']:.2f}ms")
        print(f"✓ Time Per Output Token: {response['tpot_ms']:.2f}ms")
        print(f"✓ Client-side Latency: {elapsed:.2f}ms")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_batch_inference(client: InferenceClient):
    """Example: Batch inference request"""
    print_section("Batch Inference Request")
    
    prompts = [
        "What is machine learning?",
        "Explain neural networks.",
        "Define artificial intelligence.",
        "What are transformers in AI?"
    ]
    
    print(f"Sending {len(prompts)} prompts in batch:")
    for i, p in enumerate(prompts, 1):
        print(f"  {i}. {p}")
    
    print("\nProcessing...")
    
    try:
        start_time = time.time()
        response = client.batch_inference(prompts, max_tokens=30)
        elapsed = (time.time() - start_time) * 1000
        
        print(f"\n✓ Batch ID: {response['batch_id']}")
        print(f"✓ Total Requests: {response['total_requests']}")
        print(f"✓ Total Latency: {response['total_latency_ms']:.2f}ms")
        print(f"✓ Avg Latency per Request: {response['avg_latency_per_request_ms']:.2f}ms")
        print(f"✓ Client-side Latency: {elapsed:.2f}ms\n")
        
        print("Responses:")
        for i, resp in enumerate(response['responses'], 1):
            print(f"\n  {i}. Prompt: {resp['prompt']}")
            print(f"     Generated: {resp['generated_text'][:100]}...")
            print(f"     TTFT: {resp['ttft_ms']:.2f}ms, TPOT: {resp['tpot_ms']:.2f}ms")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_streaming_inference(client: InferenceClient):
    """Example: Streaming inference"""
    print_section("Streaming Inference")
    
    prompt = "Describe the process of LLM inference step by step."
    
    print(f"Prompt: {prompt}\n")
    print("Streaming tokens as they're generated:\n")
    
    try:
        token_count = 0
        start_time = time.time()
        
        for data in client.stream_inference(prompt, max_tokens=20):
            status = data.get('status')
            
            if status == 'started':
                print(f"  {data['token']} ", end='', flush=True)
            elif status == 'generating':
                token_count += 1
                print(f"{data['token']} ", end='', flush=True)
            elif status == 'completed':
                elapsed = (time.time() - start_time) * 1000
                print(f"\n\n✓ Streaming completed")
                print(f"✓ Tokens received: {token_count}")
                print(f"✓ Total time: {elapsed:.2f}ms")
            elif status == 'error':
                print(f"\n✗ Error: {data.get('error')}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")


def example_list_models(client: InferenceClient):
    """Example: List available models"""
    print_section("List Available Models")
    
    try:
        response = client.list_models()
        models = response['models']
        
        print(f"✓ Found {len(models)} models:\n")
        
        for model in models:
            print(f"  Model ID: {model['model_id']}")
            print(f"  Name: {model['name']}")
            print(f"  Parameters: {model['parameters']}")
            print(f"  Context Length: {model['context_length']} tokens")
            print(f"  Status: {model['status']}")
            print()
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_metrics(client: InferenceClient):
    """Example: Get server metrics"""
    print_section("Server Performance Metrics")
    
    try:
        metrics = client.get_metrics()
        
        print("✓ Performance Metrics:\n")
        print(f"  Total Requests: {metrics['total_requests']}")
        print(f"  Successful: {metrics['successful_requests']}")
        print(f"  Failed: {metrics['failed_requests']}")
        print(f"  Success Rate: {metrics['success_rate']}%")
        print(f"  Total Tokens Generated: {metrics['total_tokens_generated']}")
        print(f"  Average Tokens per Request: {metrics['average_tokens_per_request']}")
        print(f"  Average Latency: {metrics['average_latency_ms']:.2f}ms")
        print(f"  P95 Latency: {metrics['p95_latency_ms']:.2f}ms")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_error_handling(client: InferenceClient):
    """Example: Error handling"""
    print_section("Error Handling")
    
    # Test 1: Missing prompt
    print("Test 1: Missing prompt parameter")
    try:
        response = requests.post(
            f"{client.base_url}/api/v1/inference",
            json={"max_tokens": 100}
        )
        print(f"  Response: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test 2: Invalid batch request
    print("\nTest 2: Invalid batch request (empty prompts)")
    try:
        response = requests.post(
            f"{client.base_url}/api/v1/batch_inference",
            json={"prompts": []}
        )
        print(f"  Response: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"  Error: {e}")


def load_test(client: InferenceClient, num_requests: int = 10):
    """Example: Simple load test"""
    print_section(f"Load Test ({num_requests} requests)")
    
    prompt = "Test prompt for load testing."
    
    print(f"Sending {num_requests} concurrent-style requests...\n")
    
    latencies = []
    successes = 0
    failures = 0
    
    start_time = time.time()
    
    for i in range(num_requests):
        try:
            req_start = time.time()
            response = client.inference(prompt, max_tokens=20)
            req_latency = (time.time() - req_start) * 1000
            latencies.append(req_latency)
            successes += 1
            print(f"  Request {i+1}/{num_requests}: ✓ {req_latency:.2f}ms")
        except Exception as e:
            failures += 1
            print(f"  Request {i+1}/{num_requests}: ✗ {e}")
    
    total_time = (time.time() - start_time) * 1000
    
    print(f"\n✓ Load Test Results:")
    print(f"  Total Time: {total_time:.2f}ms")
    print(f"  Successful Requests: {successes}")
    print(f"  Failed Requests: {failures}")
    
    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        print(f"  Average Latency: {avg_latency:.2f}ms")
        print(f"  Min Latency: {min_latency:.2f}ms")
        print(f"  Max Latency: {max_latency:.2f}ms")
        print(f"  Throughput: {successes / (total_time / 1000):.2f} req/sec")


def main():
    """Run all examples"""
    print("\n" + "★" * 80)
    print("  LLM INFERENCE CLIENT - EXAMPLES")
    print("★" * 80)
    
    # Initialize client
    client = InferenceClient("http://localhost:5000")
    
    # Check if server is running
    try:
        client.health_check()
    except Exception as e:
        print("\n✗ Cannot connect to inference server!")
        print(f"  Error: {e}")
        print("\n  Please ensure the server is running:")
        print("    python sources/inference_server.py\n")
        return
    
    # Run examples
    example_health_check(client)
    example_list_models(client)
    example_single_inference(client)
    example_batch_inference(client)
    example_streaming_inference(client)
    example_error_handling(client)
    load_test(client, num_requests=5)
    example_metrics(client)
    
    print("\n" + "★" * 80)
    print("  All examples completed!")
    print("★" * 80 + "\n")


if __name__ == "__main__":
    main()
