#!/usr/bin/env python3
"""
Comprehensive cURL test cases and RESTful API validation for Open WebUI integration.
This script tests all API endpoints with equivalent cURL commands and validates responses.
"""

import requests
import json
import time
import subprocess
import sys
import os
from typing import Dict, Any, Optional

BASE_URL = "http://localhost:8000"
OPENAI_API_KEY = "dummy-key"  # For testing OpenAI compatibility

class APITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, message: str = "", curl_cmd: str = ""):
        """Log test results."""
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
        if message:
            print(f"   {message}")
        if curl_cmd:
            print(f"   cURL: {curl_cmd}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "curl": curl_cmd
        })
    
    def run_curl_command(self, curl_cmd: str) -> Dict[str, Any]:
        """Execute cURL command and return parsed response."""
        try:
            result = subprocess.run(curl_cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return {"success": True, "output": result.stdout, "error": None}
            else:
                return {"success": False, "output": result.stdout, "error": result.stderr}
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        print("\n🏥 Testing Health Endpoint")
        print("=" * 40)
        
        # Method 1: Using requests
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Health Check (requests)",
                    True,
                    f"Status: {data.get('status')}, Redis: {data.get('redis')}"
                )
            else:
                self.log_test("Health Check (requests)", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Health Check (requests)", False, str(e))
        
        # Method 2: Using cURL
        curl_cmd = f'curl -s "{self.base_url}/health"'
        result = self.run_curl_command(curl_cmd)
        
        if result["success"]:
            try:
                data = json.loads(result["output"])
                self.log_test(
                    "Health Check (cURL)",
                    True,
                    f"Status: {data.get('status')}",
                    curl_cmd
                )
            except json.JSONDecodeError:
                self.log_test("Health Check (cURL)", False, "Invalid JSON response", curl_cmd)
        else:
            self.log_test("Health Check (cURL)", False, result["error"], curl_cmd)
    
    def test_models_endpoint(self):
        """Test models list endpoint."""
        print("\n📋 Testing Models Endpoint")
        print("=" * 40)
        
        # Method 1: Using requests
        try:
            response = requests.get(f"{self.base_url}/models")
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Models List (requests)",
                    True,
                    f"Total models: {data.get('total_models')}, Default: {data.get('default_model')}"
                )
            else:
                self.log_test("Models List (requests)", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Models List (requests)", False, str(e))
        
        # Method 2: Using cURL
        curl_cmd = f'curl -s "{self.base_url}/models"'
        result = self.run_curl_command(curl_cmd)
        
        if result["success"]:
            try:
                data = json.loads(result["output"])
                self.log_test(
                    "Models List (cURL)",
                    True,
                    f"Found {len(data.get('models', []))} models",
                    curl_cmd
                )
            except json.JSONDecodeError:
                self.log_test("Models List (cURL)", False, "Invalid JSON response", curl_cmd)
        else:
            self.log_test("Models List (cURL)", False, result["error"], curl_cmd)
    
    def test_openai_models_endpoint(self):
        """Test OpenAI-compatible models endpoint."""
        print("\n🤖 Testing OpenAI Models Endpoint")
        print("=" * 40)
        
        # Method 1: Using requests
        try:
            response = requests.get(
                f"{self.base_url}/v1/models",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"}
            )
            if response.status_code == 200:
                data = response.json()
                models = data.get('data', [])
                self.log_test(
                    "OpenAI Models (requests)",
                    True,
                    f"Found {len(models)} OpenAI-compatible models"
                )
            else:
                self.log_test("OpenAI Models (requests)", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("OpenAI Models (requests)", False, str(e))
        
        # Method 2: Using cURL
        curl_cmd = f'curl -s -H "Authorization: Bearer {OPENAI_API_KEY}" "{self.base_url}/v1/models"'
        result = self.run_curl_command(curl_cmd)
        
        if result["success"]:
            try:
                data = json.loads(result["output"])
                models = data.get('data', [])
                self.log_test(
                    "OpenAI Models (cURL)",
                    True,
                    f"Retrieved {len(models)} models",
                    curl_cmd
                )
            except json.JSONDecodeError:
                self.log_test("OpenAI Models (cURL)", False, "Invalid JSON response", curl_cmd)
        else:
            self.log_test("OpenAI Models (cURL)", False, result["error"], curl_cmd)
    
    def test_chat_endpoint(self):
        """Test chat submission endpoint."""
        print("\n💬 Testing Chat Endpoint")
        print("=" * 40)
        
        chat_request = {
            "prompt": "What is the capital of France? Please provide a brief answer.",
            "model": "llama3.2:1b",
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        # Method 1: Using requests
        try:
            response = requests.post(
                f"{self.base_url}/chat",
                json=chat_request,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                data = response.json()
                task_id = data.get('task_id')
                self.log_test(
                    "Chat Submission (requests)",
                    True,
                    f"Task ID: {task_id[:8]}..., Status: {data.get('status')}"
                )
                return task_id
            else:
                self.log_test("Chat Submission (requests)", False, f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Chat Submission (requests)", False, str(e))
            return None
        
        # Method 2: Using cURL
        curl_data = json.dumps(chat_request)
        curl_cmd = f'''curl -s -X POST "{self.base_url}/chat" -H "Content-Type: application/json" -d '{curl_data}' '''
        result = self.run_curl_command(curl_cmd)
        
        if result["success"]:
            try:
                data = json.loads(result["output"])
                task_id = data.get('task_id')
                self.log_test(
                    "Chat Submission (cURL)",
                    True,
                    f"Task ID: {task_id[:8] if task_id else 'None'}...",
                    curl_cmd
                )
            except json.JSONDecodeError:
                self.log_test("Chat Submission (cURL)", False, "Invalid JSON response", curl_cmd)
        else:
            self.log_test("Chat Submission (cURL)", False, result["error"], curl_cmd)
    
    def test_openai_chat_completions(self):
        """Test OpenAI-compatible chat completions endpoint."""
        print("\n🗨️ Testing OpenAI Chat Completions")
        print("=" * 40)
        
        openai_request = {
            "model": "llama3.2:1b",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello! How are you today?"}
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }
        
        # Method 1: Using requests
        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json=openai_request,
                headers=self.headers
            )
            if response.status_code == 200:
                data = response.json()
                choices = data.get('choices', [])
                if choices:
                    content = choices[0].get('message', {}).get('content', '')
                    self.log_test(
                        "OpenAI Chat Completions (requests)",
                        True,
                        f"Response: {content[:50]}..."
                    )
                else:
                    self.log_test("OpenAI Chat Completions (requests)", False, "No choices in response")
            else:
                self.log_test("OpenAI Chat Completions (requests)", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("OpenAI Chat Completions (requests)", False, str(e))
        
        # Method 2: Using cURL
        curl_data = json.dumps(openai_request)
        curl_cmd = f'''curl -s -X POST "{self.base_url}/v1/chat/completions" -H "Content-Type: application/json" -H "Authorization: Bearer {OPENAI_API_KEY}" -d '{curl_data}' '''
        result = self.run_curl_command(curl_cmd)
        
        if result["success"]:
            try:
                data = json.loads(result["output"])
                choices = data.get('choices', [])
                if choices:
                    content = choices[0].get('message', {}).get('content', '')
                    self.log_test(
                        "OpenAI Chat Completions (cURL)",
                        True,
                        f"Response length: {len(content)} chars",
                        curl_cmd
                    )
                else:
                    self.log_test("OpenAI Chat Completions (cURL)", False, "No choices in response", curl_cmd)
            except json.JSONDecodeError:
                self.log_test("OpenAI Chat Completions (cURL)", False, "Invalid JSON response", curl_cmd)
        else:
            self.log_test("OpenAI Chat Completions (cURL)", False, result["error"], curl_cmd)
    
    def test_task_status_endpoint(self, task_id: str):
        """Test task status endpoint."""
        if not task_id:
            print("\n⚠️ Skipping task status test - no task ID available")
            return
        
        print(f"\n📊 Testing Task Status Endpoint")
        print("=" * 40)
        
        # Method 1: Using requests
        try:
            response = requests.get(f"{self.base_url}/task/{task_id}")
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                self.log_test(
                    "Task Status (requests)",
                    True,
                    f"Status: {status}"
                )
            else:
                self.log_test("Task Status (requests)", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Task Status (requests)", False, str(e))
        
        # Method 2: Using cURL
        curl_cmd = f'curl -s "{self.base_url}/task/{task_id}"'
        result = self.run_curl_command(curl_cmd)
        
        if result["success"]:
            try:
                data = json.loads(result["output"])
                status = data.get('status')
                self.log_test(
                    "Task Status (cURL)",
                    True,
                    f"Status: {status}",
                    curl_cmd
                )
            except json.JSONDecodeError:
                self.log_test("Task Status (cURL)", False, "Invalid JSON response", curl_cmd)
        else:
            self.log_test("Task Status (cURL)", False, result["error"], curl_cmd)
    
    def test_open_webui_compatibility(self):
        """Test Open WebUI specific compatibility requirements."""
        print("\n🌐 Testing Open WebUI Compatibility")
        print("=" * 40)
        
        # Test 1: CORS headers
        try:
            response = requests.options(f"{self.base_url}/v1/chat/completions")
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            
            if cors_headers['Access-Control-Allow-Origin']:
                self.log_test("CORS Configuration", True, "CORS headers present")
            else:
                self.log_test("CORS Configuration", False, "Missing CORS headers")
        except Exception as e:
            self.log_test("CORS Configuration", False, str(e))
        
        # Test 2: Required OpenAI endpoints exist
        required_endpoints = [
            ("/v1/models", "GET"),
            ("/v1/chat/completions", "POST"),
            ("/health", "GET")
        ]
        
        for endpoint, method in required_endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}")
                else:
                    response = requests.post(f"{self.base_url}{endpoint}", json={})
                
                # Accept any response that's not 404
                if response.status_code != 404:
                    self.log_test(f"Endpoint {method} {endpoint}", True, f"Available (HTTP {response.status_code})")
                else:
                    self.log_test(f"Endpoint {method} {endpoint}", False, "Not found (HTTP 404)")
            except Exception as e:
                self.log_test(f"Endpoint {method} {endpoint}", False, str(e))
    
    def generate_curl_examples(self):
        """Generate example cURL commands for documentation."""
        print("\n📖 cURL Examples for Open WebUI Integration")
        print("=" * 60)
        
        examples = [
            {
                "title": "Health Check",
                "description": "Check system status",
                "curl": f'curl -s "{BASE_URL}/health"'
            },
            {
                "title": "List Models (Standard)",
                "description": "Get available models",
                "curl": f'curl -s "{BASE_URL}/models"'
            },
            {
                "title": "List Models (OpenAI Format)",
                "description": "Get models in OpenAI format for Open WebUI",
                "curl": f'curl -s -H "Authorization: Bearer {OPENAI_API_KEY}" "{BASE_URL}/v1/models"'
            },
            {
                "title": "Chat Request",
                "description": "Submit async chat request",
                "curl": f'''curl -X POST "{BASE_URL}/chat" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "prompt": "What is artificial intelligence?",
    "model": "llama3.2:1b",
    "temperature": 0.7,
    "max_tokens": 200
  }}' '''
            },
            {
                "title": "OpenAI Chat Completions",
                "description": "OpenAI-compatible endpoint for Open WebUI",
                "curl": f'''curl -X POST "{BASE_URL}/v1/chat/completions" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer {OPENAI_API_KEY}" \\
  -d '{{
    "model": "llama3.2:1b",
    "messages": [
      {{"role": "system", "content": "You are a helpful assistant."}},
      {{"role": "user", "content": "Explain quantum computing in simple terms."}}
    ],
    "temperature": 0.7,
    "max_tokens": 300
  }}' '''
            },
            {
                "title": "Task Status Check",
                "description": "Check status of submitted task",
                "curl": f'curl -s "{BASE_URL}/task/YOUR_TASK_ID_HERE"'
            }
        ]
        
        for example in examples:
            print(f"\n### {example['title']}")
            print(f"**{example['description']}**")
            print("```bash")
            print(example['curl'])
            print("```")
    
    def run_all_tests(self):
        """Run comprehensive test suite."""
        print("🚀 Starting Comprehensive API Test Suite")
        print("=" * 60)
        print(f"Testing API at: {self.base_url}")
        print(f"OpenAI API Key: {OPENAI_API_KEY}")
        
        # Run tests
        self.test_health_endpoint()
        self.test_models_endpoint()
        self.test_openai_models_endpoint()
        task_id = self.test_chat_endpoint()
        self.test_openai_chat_completions()
        
        # Wait a bit for async task to potentially complete
        if task_id:
            print("\n⏳ Waiting 5 seconds for task processing...")
            time.sleep(5)
            self.test_task_status_endpoint(task_id)
        
        self.test_open_webui_compatibility()
        
        # Generate documentation
        self.generate_curl_examples()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n🌐 Open WebUI Integration Status:")
        openai_endpoints_working = any(
            result['success'] for result in self.test_results 
            if 'OpenAI' in result['test']
        )
        
        if openai_endpoints_working:
            print("✅ Ready for Open WebUI integration")
            print(f"   Configure Open WebUI with: {BASE_URL}/v1")
            print(f"   Use API key: {OPENAI_API_KEY}")
        else:
            print("❌ OpenAI compatibility issues detected")
            print("   Check FastAPI server and OpenAI endpoints")

def main():
    """Main test execution."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "examples":
            tester = APITester()
            tester.generate_curl_examples()
            return
        elif sys.argv[1] == "quick":
            tester = APITester()
            tester.test_health_endpoint()
            tester.test_openai_models_endpoint()
            tester.print_summary()
            return
    
    # Run full test suite
    tester = APITester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
