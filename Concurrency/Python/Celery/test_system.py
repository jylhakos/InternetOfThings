#!/usr/bin/env python3
"""
Test script for LLM FastAPI + Celery + LangChain.js system
"""

import requests
import time
import json
import sys
from typing import Dict, Any

class LLMSystemTester:
    def __init__(self, fastapi_url="http://localhost:8000", langchain_url="http://localhost:3000"):
        self.fastapi_url = fastapi_url
        self.langchain_url = langchain_url
        self.test_results = []

    def log_test(self, test_name: str, success: bool, message: str, details: Dict = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {}
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        
        if details and not success:
            print(f"   Details: {json.dumps(details, indent=2)}")

    def test_service_health(self, url: str, service_name: str) -> bool:
        """Test if a service is healthy"""
        try:
            response = requests.get(f"{url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test(f"{service_name} Health", True, f"Service is healthy", data)
                return True
            else:
                self.log_test(f"{service_name} Health", False, f"Health check failed with status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_test(f"{service_name} Health", False, f"Connection failed: {str(e)}")
            return False

    def test_fastapi_endpoints(self) -> bool:
        """Test FastAPI endpoints"""
        try:
            # Test root endpoint
            response = requests.get(self.fastapi_url, timeout=10)
            if response.status_code == 200:
                self.log_test("FastAPI Root", True, "Root endpoint accessible")
            else:
                self.log_test("FastAPI Root", False, f"Root endpoint returned {response.status_code}")
                return False

            # Test models endpoint
            response = requests.get(f"{self.fastapi_url}/models", timeout=10)
            if response.status_code == 200:
                models = response.json()
                self.log_test("FastAPI Models", True, f"Models endpoint working", {"models": models})
            else:
                self.log_test("FastAPI Models", False, f"Models endpoint failed: {response.status_code}")

            return True
        except requests.exceptions.RequestException as e:
            self.log_test("FastAPI Endpoints", False, f"Request failed: {str(e)}")
            return False

    def test_langchain_service(self) -> bool:
        """Test LangChain.js service"""
        try:
            # Test root endpoint
            response = requests.get(self.langchain_url, timeout=10)
            if response.status_code == 200:
                self.log_test("LangChain Root", True, "LangChain service accessible")
            else:
                self.log_test("LangChain Root", False, f"Service returned {response.status_code}")
                return False

            # Test models endpoint
            response = requests.get(f"{self.langchain_url}/models", timeout=10)
            if response.status_code == 200:
                models = response.json()
                self.log_test("LangChain Models", True, "Models endpoint working", {"models_count": len(models.get('models', []))})
            else:
                self.log_test("LangChain Models", False, f"Models endpoint failed: {response.status_code}")

            return True
        except requests.exceptions.RequestException as e:
            self.log_test("LangChain Service", False, f"Request failed: {str(e)}")
            return False

    def test_direct_llm_generation(self) -> bool:
        """Test direct LLM generation through LangChain service"""
        try:
            payload = {
                "prompt": "Say hello in exactly 5 words.",
                "temperature": 0.1,
                "max_tokens": 20
            }

            response = requests.post(
                f"{self.langchain_url}/generate",
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.log_test("Direct LLM Generation", True, "LLM generated response successfully", {
                        "response_length": len(result.get('response', '')),
                        "processing_time": result.get('processing_time', 0),
                        "tokens_used": result.get('tokens_used', 0)
                    })
                    return True
                else:
                    self.log_test("Direct LLM Generation", False, f"LLM generation failed: {result.get('error')}")
                    return False
            else:
                self.log_test("Direct LLM Generation", False, f"Request failed with status {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            self.log_test("Direct LLM Generation", False, f"Request failed: {str(e)}")
            return False

    def test_full_system_workflow(self) -> bool:
        """Test the complete workflow: FastAPI -> Celery -> LangChain -> Ollama"""
        try:
            # Submit chat request
            chat_payload = {
                "prompt": "What is 2+2? Answer with just the number.",
                "temperature": 0.1,
                "max_tokens": 10
            }

            print("🔄 Submitting chat request...")
            response = requests.post(
                f"{self.fastapi_url}/chat",
                json=chat_payload,
                timeout=10
            )

            if response.status_code != 200:
                self.log_test("Full System Workflow", False, f"Chat submission failed: {response.status_code}")
                return False

            result = response.json()
            task_id = result.get('task_id')

            if not task_id:
                self.log_test("Full System Workflow", False, "No task ID returned")
                return False

            self.log_test("Task Submission", True, f"Task submitted successfully", {"task_id": task_id})

            # Poll for result
            print(f"📊 Polling for task result (ID: {task_id})...")
            max_wait_time = 120  # 2 minutes
            poll_interval = 2
            elapsed_time = 0

            while elapsed_time < max_wait_time:
                time.sleep(poll_interval)
                elapsed_time += poll_interval

                response = requests.get(f"{self.fastapi_url}/task/{task_id}", timeout=10)
                
                if response.status_code != 200:
                    self.log_test("Full System Workflow", False, f"Task status check failed: {response.status_code}")
                    return False

                task_result = response.json()
                status = task_result.get('status')

                print(f"⏳ Task status: {status} (elapsed: {elapsed_time}s)")

                if status == 'SUCCESS':
                    result_data = task_result.get('result', {})
                    if result_data.get('success'):
                        self.log_test("Full System Workflow", True, "Complete workflow successful!", {
                            "total_time": elapsed_time,
                            "llm_response": result_data.get('response', ''),
                            "processing_time": result_data.get('processing_time', 0),
                            "tokens_used": result_data.get('tokens_used', 0)
                        })
                        return True
                    else:
                        self.log_test("Full System Workflow", False, f"Task completed but LLM failed: {result_data.get('error')}")
                        return False

                elif status == 'FAILURE':
                    error = task_result.get('error', 'Unknown error')
                    self.log_test("Full System Workflow", False, f"Task failed: {error}")
                    return False

            # Timeout
            self.log_test("Full System Workflow", False, f"Task timeout after {max_wait_time}s")
            return False

        except requests.exceptions.RequestException as e:
            self.log_test("Full System Workflow", False, f"Request failed: {str(e)}")
            return False

    def test_openai_compatibility(self) -> bool:
        """Test OpenAI-compatible endpoint"""
        try:
            payload = {
                "model": "llama3.1",
                "messages": [
                    {"role": "user", "content": "Say 'test successful' exactly."}
                ],
                "temperature": 0.1,
                "max_tokens": 10
            }

            response = requests.post(
                f"{self.langchain_url}/v1/chat/completions",
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    message = result['choices'][0]['message']['content']
                    self.log_test("OpenAI Compatibility", True, "OpenAI-compatible endpoint working", {
                        "response": message,
                        "usage": result.get('usage', {})
                    })
                    return True
                else:
                    self.log_test("OpenAI Compatibility", False, "Invalid response format")
                    return False
            else:
                self.log_test("OpenAI Compatibility", False, f"Request failed: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            self.log_test("OpenAI Compatibility", False, f"Request failed: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Starting LLM System Tests...")
        print("=" * 60)

        # Test individual services
        fastapi_healthy = self.test_service_health(self.fastapi_url, "FastAPI")
        langchain_healthy = self.test_service_health(self.langchain_url, "LangChain")

        if not fastapi_healthy or not langchain_healthy:
            print("\n❌ Basic health checks failed. Please ensure all services are running.")
            return False

        # Test endpoints
        self.test_fastapi_endpoints()
        self.test_langchain_service()

        # Test LLM functionality
        if self.test_direct_llm_generation():
            # Only test full workflow if direct generation works
            self.test_full_system_workflow()

        # Test OpenAI compatibility
        self.test_openai_compatibility()

        # Summary
        print("\n" + "=" * 60)
        print("📊 Test Summary:")
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")

        if passed == total:
            print("\n🎉 All tests passed! System is working correctly.")
            return True
        else:
            print("\n⚠️  Some tests failed. Check the details above.")
            return False

    def print_test_results(self):
        """Print detailed test results"""
        print("\n" + "=" * 60)
        print("📋 Detailed Test Results:")
        
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"\n{status} {result['test']}")
            print(f"   Message: {result['message']}")
            if result['details']:
                print(f"   Details: {json.dumps(result['details'], indent=4)}")

def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test LLM System")
    parser.add_argument("--fastapi-url", default="http://localhost:8000", help="FastAPI URL")
    parser.add_argument("--langchain-url", default="http://localhost:3000", help="LangChain service URL")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    tester = LLMSystemTester(args.fastapi_url, args.langchain_url)
    
    try:
        success = tester.run_all_tests()
        
        if args.verbose:
            tester.print_test_results()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test runner error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
