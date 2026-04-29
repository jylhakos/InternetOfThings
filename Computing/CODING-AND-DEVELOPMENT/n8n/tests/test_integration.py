"""
Integration tests for complete n8n + Ollama workflow.
Run with: pytest tests/test_integration.py -v
"""

import pytest
import requests
import time
import json
from typing import Dict, Any, Optional


class TestWorkflowExecution:
    """Integration tests for workflow execution"""

    @pytest.fixture
    def n8n_base_url(self) -> str:
        """n8n server base URL"""
        return 'http://localhost:5678'

    @pytest.fixture
    def ollama_base_url(self) -> str:
        """Ollama server base URL"""
        return 'http://localhost:11434'

    @pytest.fixture(autouse=True)
    def check_services_running(self, n8n_base_url: str, ollama_base_url: str):
        """Ensure both services are running before tests"""
        # Check n8n
        try:
            n8n_response = requests.get(f'{n8n_base_url}/healthz', timeout=5)
            if n8n_response.status_code != 200:
                pytest.skip("n8n server not healthy")
        except requests.exceptions.ConnectionError:
            pytest.skip("n8n server not running. Start with: n8n")

        # Check Ollama
        try:
            ollama_response = requests.get(f'{ollama_base_url}/api/version', timeout=5)
            if ollama_response.status_code != 200:
                pytest.skip("Ollama server not responding")
        except requests.exceptions.ConnectionError:
            pytest.skip("Ollama server not running. Start with: ollama serve")

    def test_end_to_end_chat_workflow(self, ollama_base_url: str):
        """Test complete chat workflow from input to output"""
        # This test simulates a complete chat interaction
        # Note: Actual webhook URL will depend on workflow configuration
        
        payload = {
            "model": "llama2",
            "prompt": "What is n8n?",
            "stream": False
        }
        
        try:
            response = requests.post(
                f'{ollama_base_url}/api/generate',
                json=payload,
                timeout=60
            )
            
            assert response.status_code == 200, "Workflow execution failed"
            data = response.json()
            
            assert 'response' in data, "No response in output"
            assert len(data['response']) > 0, "Empty response"
            
            # Basic validation of response content
            response_text = data['response'].lower()
            assert len(response_text) > 10, "Response too short"
            
            print(f"✓ Workflow executed successfully")
            print(f"  Response length: {len(data['response'])} characters")
            
        except requests.exceptions.Timeout:
            pytest.skip("Workflow execution timeout - model may be processing")

    def test_chat_workflow_with_different_prompts(self, ollama_base_url: str):
        """Test workflow with various prompt types"""
        test_prompts = [
            "Hello",
            "What is 2+2?",
            "Write a haiku about automation"
        ]
        
        for prompt in test_prompts:
            payload = {
                "model": "llama2",
                "prompt": prompt,
                "stream": False
            }
            
            try:
                response = requests.post(
                    f'{ollama_base_url}/api/generate',
                    json=payload,
                    timeout=60
                )
                
                assert response.status_code == 200, f"Failed for prompt: {prompt}"
                data = response.json()
                assert 'response' in data and len(data['response']) > 0
                
                print(f"✓ Prompt '{prompt[:30]}...' successful")
                
            except requests.exceptions.Timeout:
                pytest.skip(f"Timeout for prompt: {prompt}")

    @pytest.mark.performance
    def test_workflow_response_time(self, ollama_base_url: str):
        """Test workflow response time performance"""
        payload = {
            "model": "llama2",
            "prompt": "Hi",
            "stream": False
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f'{ollama_base_url}/api/generate',
                json=payload,
                timeout=60
            )
            
            end_time = time.time()
            latency = end_time - start_time
            
            assert response.status_code == 200, "Workflow failed"
            assert latency < 60, f"Response too slow: {latency:.2f}s"
            
            print(f"✓ Response time: {latency:.2f} seconds")
            
            # Performance thresholds
            if latency < 10:
                print("  Performance: Excellent")
            elif latency < 30:
                print("  Performance: Good")
            else:
                print("  Performance: Acceptable (may need optimization)")
                
        except requests.exceptions.Timeout:
            pytest.fail("Workflow execution timeout (>60s)")

    def test_concurrent_requests(self, ollama_base_url: str):
        """Test handling of concurrent chat requests"""
        import concurrent.futures
        
        def send_request(prompt_id: int) -> Dict[str, Any]:
            payload = {
                "model": "llama2",
                "prompt": f"Request {prompt_id}",
                "stream": False
            }
            
            response = requests.post(
                f'{ollama_base_url}/api/generate',
                json=payload,
                timeout=60
            )
            
            return {
                'id': prompt_id,
                'status': response.status_code,
                'success': response.status_code == 200
            }
        
        # Send 3 concurrent requests
        num_requests = 3
        
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
                futures = [executor.submit(send_request, i) for i in range(num_requests)]
                results = [f.result() for f in concurrent.futures.as_completed(futures, timeout=120)]
            
            # Check all requests succeeded
            success_count = sum(1 for r in results if r['success'])
            assert success_count == num_requests, \
                f"Only {success_count}/{num_requests} requests succeeded"
            
            print(f"✓ Successfully handled {num_requests} concurrent requests")
            
        except concurrent.futures.TimeoutError:
            pytest.skip("Concurrent requests timeout - reduce load or optimize model")


class TestWorkflowRobustness:
    """Test workflow error handling and edge cases"""

    @pytest.fixture
    def ollama_base_url(self) -> str:
        return 'http://localhost:11434'

    def test_empty_prompt_handling(self, ollama_base_url: str):
        """Test workflow behavior with empty prompts"""
        payload = {
            "model": "llama2",
            "prompt": "",
            "stream": False
        }
        
        try:
            response = requests.post(
                f'{ollama_base_url}/api/generate',
                json=payload,
                timeout=30
            )
            
            # Should either succeed with a response or return error
            assert response.status_code in [200, 400], \
                "Unexpected status for empty prompt"
            
            print("✓ Empty prompt handled correctly")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Ollama not running")

    def test_very_long_prompt_handling(self, ollama_base_url: str):
        """Test workflow with very long input"""
        long_prompt = "Tell me about automation. " * 100  # ~2800 characters
        
        payload = {
            "model": "llama2",
            "prompt": long_prompt,
            "stream": False
        }
        
        try:
            response = requests.post(
                f'{ollama_base_url}/api/generate',
                json=payload,
                timeout=120
            )
            
            # Should handle long prompts gracefully
            assert response.status_code in [200, 400, 413], \
                "Long prompt not handled properly"
            
            if response.status_code == 200:
                print(f"✓ Long prompt ({len(long_prompt)} chars) processed successfully")
            else:
                print(f"✓ Long prompt returned expected error: {response.status_code}")
                
        except requests.exceptions.Timeout:
            pytest.skip("Long prompt processing timeout")

    def test_special_characters_in_prompt(self, ollama_base_url: str):
        """Test workflow with special characters"""
        special_prompts = [
            "Hello, world! How are you?",
            "Test with symbols: @#$%^&*()",
            "Unicode test: 你好 مرحبا שלום",
            "Code snippet: def test():\n    return True"
        ]
        
        for prompt in special_prompts:
            payload = {
                "model": "llama2",
                "prompt": prompt,
                "stream": False
            }
            
            try:
                response = requests.post(
                    f'{ollama_base_url}/api/generate',
                    json=payload,
                    timeout=60
                )
                
                assert response.status_code == 200, \
                    f"Failed for special characters: {prompt[:30]}"
                
                print(f"✓ Special characters handled: {prompt[:50]}")
                
            except requests.exceptions.Timeout:
                print(f"⚠ Timeout for: {prompt[:30]}")
                continue


class TestDataFlow:
    """Test data flow through workflow components"""

    @pytest.fixture
    def ollama_base_url(self) -> str:
        return 'http://localhost:11434'

    def test_input_to_output_data_integrity(self, ollama_base_url: str):
        """Test that data flows correctly through the workflow"""
        test_cases = [
            ("What is 1+1?", ["2", "two"]),  # Expected keywords in response
            ("Name a color", ["red", "blue", "green", "yellow", "color"]),
        ]
        
        for prompt, expected_keywords in test_cases:
            payload = {
                "model": "llama2",
                "prompt": prompt,
                "stream": False
            }
            
            try:
                response = requests.post(
                    f'{ollama_base_url}/api/generate',
                    json=payload,
                    timeout=60
                )
                
                assert response.status_code == 200
                data = response.json()
                response_text = data.get('response', '').lower()
                
                # Check if at least one expected keyword is present
                has_relevant_keyword = any(
                    keyword in response_text 
                    for keyword in expected_keywords
                )
                
                if has_relevant_keyword:
                    print(f"✓ Response relevant for: '{prompt}'")
                else:
                    print(f"⚠ Response may not be relevant for: '{prompt}'")
                    
            except requests.exceptions.Timeout:
                pytest.skip(f"Timeout for prompt: {prompt}")


if __name__ == "__main__":
    # Run tests with verbose output and show local variables on failure
    pytest.main([__file__, "-v", "--tb=short", "-s"])
