#!/usr/bin/env python3
"""
Test client for the Redis Queue + FastAPI + LangChain + Ollama system.
This script demonstrates how to interact with the API endpoints.
"""

import requests
import time
import json
import sys
from typing import Dict, Any

class RQTestClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        
    def health_check(self) -> Dict[str, Any]:
        """Check if the FastAPI server is healthy."""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.json()
        except Exception as e:
            return {"error": str(e), "status": "unhealthy"}
    
    def submit_question(self, question: str, model: str = "llama3.2:1b") -> Dict[str, Any]:
        """Submit a question for asynchronous processing."""
        payload = {
            "question": question,
            "model": model,
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        try:
            response = requests.post(f"{self.base_url}/generate_async/", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_result(self, job_id: str) -> Dict[str, Any]:
        """Get the result of a submitted job."""
        try:
            response = requests.get(f"{self.base_url}/get_result/{job_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get the status of a job."""
        try:
            response = requests.get(f"{self.base_url}/job_status/{job_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_queue_info(self) -> Dict[str, Any]:
        """Get information about the current queue."""
        try:
            response = requests.get(f"{self.base_url}/queue_info")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def wait_for_result(self, job_id: str, max_wait: int = 60, poll_interval: int = 2) -> Dict[str, Any]:
        """Wait for a job to complete and return the result."""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            result = self.get_result(job_id)
            
            if "error" in result:
                return result
            
            status = result.get("status")
            if status == "finished":
                return result
            elif status == "failed":
                return result
            
            print(f"Job {job_id} status: {status}")
            time.sleep(poll_interval)
        
        return {"error": "Timeout waiting for result", "job_id": job_id}

def run_interactive_test():
    """Run an interactive test session."""
    client = RQTestClient()
    
    print("Redis Queue + FastAPI + LangChain + Ollama Test Client")
    print("=" * 60)
    
    # Health check
    print("\n1. Checking server health...")
    health = client.health_check()
    print(f"Health: {json.dumps(health, indent=2)}")
    
    if health.get("status") != "healthy":
        print("⚠️  Server is not healthy. Please check your setup.")
        return
    
    # Queue info
    print("\n2. Checking queue status...")
    queue_info = client.get_queue_info()
    print(f"Queue Info: {json.dumps(queue_info, indent=2)}")
    
    # Interactive questions
    print("\n3. Interactive Q&A Session")
    print("Enter questions to send to the LLM (type 'quit' to exit):")
    
    while True:
        question = input("\nQuestion: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            break
        
        if not question:
            continue
        
        print(f"\n📤 Submitting question: {question}")
        
        # Submit question
        submission = client.submit_question(question)
        if "error" in submission:
            print(f"❌ Error submitting question: {submission['error']}")
            continue
        
        job_id = submission.get("job_id")
        print(f"✅ Job submitted with ID: {job_id}")
        
        # Wait for result
        print("⏳ Waiting for result...")
        result = client.wait_for_result(job_id, max_wait=120)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        elif result.get("status") == "finished":
            print(f"\n✅ Response: {result.get('result')}")
            if result.get('processing_time'):
                print(f"⏱️  Processing time: {result['processing_time']:.2f} seconds")
        elif result.get("status") == "failed":
            print(f"❌ Job failed: {result.get('error', 'Unknown error')}")

def run_batch_test():
    """Run a batch test with predefined questions."""
    client = RQTestClient()
    
    test_questions = [
        "What is the capital of France?",
        "Explain quantum computing in simple terms.",
        "Write a short poem about artificial intelligence.",
        "What are the benefits of renewable energy?",
        "How does photosynthesis work?"
    ]
    
    print("Running batch test with predefined questions...")
    print("=" * 50)
    
    job_ids = []
    
    # Submit all questions
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Submitting: {question}")
        result = client.submit_question(question)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            job_id = result["job_id"]
            job_ids.append((job_id, question))
            print(f"✅ Job ID: {job_id}")
    
    # Wait for all results
    print(f"\nWaiting for {len(job_ids)} jobs to complete...")
    
    for job_id, question in job_ids:
        print(f"\n📋 Waiting for: {question[:50]}...")
        result = client.wait_for_result(job_id, max_wait=120)
        
        if result.get("status") == "finished":
            print(f"✅ Response: {result.get('result')[:100]}...")
            print(f"⏱️  Time: {result.get('processing_time', 0):.2f}s")
        else:
            print(f"❌ Failed or timeout: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "batch":
            run_batch_test()
        elif sys.argv[1] == "health":
            client = RQTestClient()
            health = client.health_check()
            print(json.dumps(health, indent=2))
        else:
            print("Usage: python test_client.py [batch|health]")
            print("  batch: Run batch test with predefined questions")
            print("  health: Just check server health")
            print("  (no args): Run interactive test")
    else:
        run_interactive_test()
