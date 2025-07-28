#!/usr/bin/env python3
"""
Open WebUI Test Cases and Integration Examples
This script provides comprehensive test cases for Open WebUI integration
with the Redis Queue + FastAPI + LangChain + Ollama system.
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List
import uuid

class OpenWebUITestSuite:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.openai_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer sk-dummy-key-for-redis-queue-system"
        }
    
    def test_openai_models_endpoint(self) -> Dict[str, Any]:
        """Test the OpenAI-compatible models endpoint."""
        print("🔍 Testing OpenAI Models Endpoint...")
        
        try:
            response = requests.get(
                f"{self.base_url}/v1/models",
                headers=self.openai_headers
            )
            response.raise_for_status()
            data = response.json()
            
            print(f"✅ Models endpoint working")
            print(f"   Available models: {len(data.get('data', []))}")
            for model in data.get('data', [])[:3]:
                print(f"   - {model.get('id', 'Unknown')}")
            
            return {"success": True, "data": data}
            
        except Exception as e:
            print(f"❌ Models endpoint failed: {e}")
            return {"success": False, "error": str(e)}
    
    def test_openai_chat_completions(self) -> Dict[str, Any]:
        """Test the OpenAI-compatible chat completions endpoint."""
        print("\n🔍 Testing OpenAI Chat Completions...")
        
        test_cases = [
            {
                "name": "Simple Question",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "What is the capital of France?"}
                ],
                "expected_keywords": ["Paris", "France", "capital"]
            },
            {
                "name": "Technical Question",
                "messages": [
                    {"role": "system", "content": "You are a technical expert."},
                    {"role": "user", "content": "Explain Redis in one sentence."}
                ],
                "expected_keywords": ["Redis", "database", "memory", "cache"]
            },
            {
                "name": "Creative Request",
                "messages": [
                    {"role": "system", "content": "You are a creative writer."},
                    {"role": "user", "content": "Write a haiku about coding."}
                ],
                "expected_keywords": ["code", "coding", "program"]
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            print(f"\n   Testing: {test_case['name']}")
            
            payload = {
                "model": "llama3.2:1b",
                "messages": test_case["messages"],
                "temperature": 0.7,
                "max_tokens": 200
            }
            
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=self.openai_headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                processing_time = time.time() - start_time
                
                # Extract response content
                choices = data.get("choices", [])
                if choices:
                    content = choices[0].get("message", {}).get("content", "")
                    print(f"   ✅ Response received ({processing_time:.2f}s)")
                    print(f"      Content: {content[:100]}...")
                    
                    # Check for expected keywords
                    found_keywords = [kw for kw in test_case["expected_keywords"] 
                                    if kw.lower() in content.lower()]
                    if found_keywords:
                        print(f"      Keywords found: {found_keywords}")
                    
                    results.append({
                        "test": test_case["name"],
                        "success": True,
                        "response": content,
                        "processing_time": processing_time,
                        "keywords_found": found_keywords
                    })
                else:
                    print(f"   ❌ No response content")
                    results.append({
                        "test": test_case["name"],
                        "success": False,
                        "error": "No response content"
                    })
                    
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                results.append({
                    "test": test_case["name"],
                    "success": False,
                    "error": str(e)
                })
        
        return {"results": results}
    
    def test_openai_completions(self) -> Dict[str, Any]:
        """Test the OpenAI-compatible completions endpoint."""
        print("\n🔍 Testing OpenAI Completions...")
        
        test_prompts = [
            "The capital of France is",
            "Redis is a",
            "Machine learning is"
        ]
        
        results = []
        
        for prompt in test_prompts:
            print(f"\n   Testing prompt: '{prompt}'")
            
            payload = {
                "model": "llama3.2:1b",
                "prompt": prompt,
                "temperature": 0.7,
                "max_tokens": 100
            }
            
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/v1/completions",
                    headers=self.openai_headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                processing_time = time.time() - start_time
                
                choices = data.get("choices", [])
                if choices:
                    text = choices[0].get("text", "")
                    print(f"   ✅ Completion received ({processing_time:.2f}s)")
                    print(f"      Text: {text[:80]}...")
                    
                    results.append({
                        "prompt": prompt,
                        "success": True,
                        "completion": text,
                        "processing_time": processing_time
                    })
                else:
                    print(f"   ❌ No completion text")
                    results.append({
                        "prompt": prompt,
                        "success": False,
                        "error": "No completion text"
                    })
                    
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                results.append({
                    "prompt": prompt,
                    "success": False,
                    "error": str(e)
                })
        
        return {"results": results}
    
    def test_concurrent_requests(self, num_requests: int = 3) -> Dict[str, Any]:
        """Test concurrent requests to simulate multiple Open WebUI users."""
        print(f"\n🔍 Testing {num_requests} Concurrent Requests...")
        
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def make_request(request_id: int):
            payload = {
                "model": "llama3.2:1b",
                "messages": [
                    {"role": "user", "content": f"This is concurrent request #{request_id}. Please respond with the request number."}
                ],
                "temperature": 0.7,
                "max_tokens": 100
            }
            
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=self.openai_headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                processing_time = time.time() - start_time
                
                results_queue.put({
                    "request_id": request_id,
                    "success": True,
                    "processing_time": processing_time,
                    "response": data.get("choices", [{}])[0].get("message", {}).get("content", "")
                })
                
            except Exception as e:
                results_queue.put({
                    "request_id": request_id,
                    "success": False,
                    "error": str(e)
                })
        
        # Start concurrent requests
        threads = []
        start_time = time.time()
        
        for i in range(num_requests):
            thread = threading.Thread(target=make_request, args=(i + 1,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Collect results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]
        
        print(f"   ✅ Completed {len(successful)}/{num_requests} requests")
        print(f"   ❌ Failed {len(failed)} requests")
        print(f"   ⏱️  Total time: {total_time:.2f}s")
        
        if successful:
            avg_time = sum(r["processing_time"] for r in successful) / len(successful)
            print(f"   📊 Average processing time: {avg_time:.2f}s")
        
        return {
            "total_requests": num_requests,
            "successful": len(successful),
            "failed": len(failed),
            "total_time": total_time,
            "average_processing_time": avg_time if successful else 0,
            "results": results
        }
    
    def demonstrate_prompt_templates(self):
        """Demonstrate different prompt templates that work well with Open WebUI."""
        print("\n📋 Prompt Template Demonstrations for Open WebUI")
        print("=" * 60)
        
        templates = {
            "Technical Expert": {
                "system": "You are a senior software engineer and technical expert. Provide detailed, accurate technical explanations with examples and best practices.",
                "user_prompt": "Explain microservices architecture",
                "description": "Best for technical documentation, coding questions, architecture discussions"
            },
            "Creative Writer": {
                "system": "You are a creative writer with a vivid imagination. Write engaging, descriptive content with rich storytelling elements.",
                "user_prompt": "Write a story about a robot discovering art",
                "description": "Best for creative writing, storytelling, content creation"
            },
            "Business Analyst": {
                "system": "You are a business analyst and consultant. Provide strategic insights, market analysis, and actionable business recommendations.",
                "user_prompt": "Analyze the impact of AI on small businesses",
                "description": "Best for business strategy, market analysis, planning"
            },
            "Friendly Tutor": {
                "system": "You are a patient, encouraging tutor who explains complex topics in simple terms with examples and analogies.",
                "user_prompt": "Explain quantum computing to a beginner",
                "description": "Best for education, learning, explanations"
            },
            "Code Reviewer": {
                "system": "You are an experienced code reviewer. Analyze code for best practices, potential issues, and suggest improvements.",
                "user_prompt": "Review this Python function for calculating factorial",
                "description": "Best for code review, programming help, debugging"
            }
        }
        
        for template_name, template_info in templates.items():
            print(f"\n🎯 {template_name}")
            print(f"   Description: {template_info['description']}")
            print(f"   System Prompt: {template_info['system']}")
            print(f"   Example User Input: {template_info['user_prompt']}")
            print(f"   Open WebUI Usage:")
            print(f"     1. Set System Prompt: {template_info['system']}")
            print(f"     2. Ask: {template_info['user_prompt']}")
    
    def run_comprehensive_test(self):
        """Run all test cases for Open WebUI integration."""
        print("🚀 Redis Queue + Open WebUI Integration Test Suite")
        print("=" * 60)
        
        # Test OpenAI endpoints
        models_result = self.test_openai_models_endpoint()
        chat_result = self.test_openai_chat_completions()
        completion_result = self.test_openai_completions()
        concurrent_result = self.test_concurrent_requests(3)
        
        # Show prompt templates
        self.demonstrate_prompt_templates()
        
        # Summary
        print(f"\n📊 Test Summary")
        print("=" * 30)
        print(f"✅ Models Endpoint: {'PASS' if models_result['success'] else 'FAIL'}")
        
        chat_success = sum(1 for r in chat_result['results'] if r['success'])
        chat_total = len(chat_result['results'])
        print(f"✅ Chat Completions: {chat_success}/{chat_total} PASS")
        
        completion_success = sum(1 for r in completion_result['results'] if r['success'])
        completion_total = len(completion_result['results'])
        print(f"✅ Completions: {completion_success}/{completion_total} PASS")
        
        print(f"✅ Concurrent Requests: {concurrent_result['successful']}/{concurrent_result['total_requests']} PASS")
        
        print(f"\n🌐 Open WebUI Access:")
        print(f"   URL: http://localhost:3001")
        print(f"   API Base URL: {self.base_url}/v1")
        print(f"   API Key: sk-dummy-key-for-redis-queue-system")

def show_curl_examples():
    """Show equivalent cURL commands for Open WebUI test cases."""
    print("\n🔧 Equivalent cURL Commands")
    print("=" * 40)
    
    examples = [
        {
            "name": "List Models",
            "curl": """curl -X GET "http://localhost:8000/v1/models" \\
  -H "Authorization: Bearer sk-dummy-key-for-redis-queue-system" \\
  -H "Content-Type: application/json" """
        },
        {
            "name": "Chat Completion",
            "curl": """curl -X POST "http://localhost:8000/v1/chat/completions" \\
  -H "Authorization: Bearer sk-dummy-key-for-redis-queue-system" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "llama3.2:1b",
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful assistant."
      },
      {
        "role": "user",
        "content": "What is the capital of France?"
      }
    ],
    "temperature": 0.7,
    "max_tokens": 500
  }'"""
        },
        {
            "name": "Text Completion",
            "curl": """curl -X POST "http://localhost:8000/v1/completions" \\
  -H "Authorization: Bearer sk-dummy-key-for-redis-queue-system" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "llama3.2:1b",
    "prompt": "The capital of France is",
    "temperature": 0.7,
    "max_tokens": 100
  }'"""
        }
    ]
    
    for example in examples:
        print(f"\n📝 {example['name']}:")
        print(example['curl'])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "curl":
            show_curl_examples()
        elif sys.argv[1] == "templates":
            suite = OpenWebUITestSuite()
            suite.demonstrate_prompt_templates()
        elif sys.argv[1] == "models":
            suite = OpenWebUITestSuite()
            suite.test_openai_models_endpoint()
        else:
            print("Usage: python open_webui_tests.py [curl|templates|models]")
    else:
        # Run comprehensive test
        suite = OpenWebUITestSuite()
        
        print("🔍 Checking if services are running...")
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                suite.run_comprehensive_test()
            else:
                print("❌ FastAPI server is not healthy")
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to FastAPI server at http://localhost:8000")
            print("Please start the system first: ./start.sh start")
        except Exception as e:
            print(f"❌ Error: {e}")
