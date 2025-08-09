#!/usr/bin/env python3
"""
Test script for the RNN + Transformer Language Model API.
This script demonstrates how to interact with the Flask API using cURL commands and Python requests.
"""

import requests
import json
import time
import sys
import subprocess


def print_curl_command(method, url, data=None, headers=None):
    """Print equivalent cURL command for the request."""
    curl_cmd = f"curl -X {method}"
    
    if headers:
        for key, value in headers.items():
            curl_cmd += f" -H '{key}: {value}'"
    
    if data:
        curl_cmd += f" -d '{json.dumps(data)}'"
    
    curl_cmd += f" {url}"
    
    print(f"Equivalent cURL command:")
    print(f"{curl_cmd}")
    print()


def test_api_endpoint(base_url="http://localhost:5000"):
    """Test all API endpoints."""
    
    print("=" * 80)
    print("TESTING RNN + TRANSFORMER LANGUAGE MODEL API")
    print("=" * 80)
    
    headers = {'Content-Type': 'application/json'}
    
    # Test 1: Health Check
    print("\n1. Testing Health Check Endpoint")
    print("-" * 40)
    url = f"{base_url}/health"
    print_curl_command("GET", url)
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    # Test 2: List Models
    print("\n2. Testing List Models Endpoint")
    print("-" * 40)
    url = f"{base_url}/models"
    print_curl_command("GET", url)
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        models_data = response.json()
        print(f"Response: {json.dumps(models_data, indent=2)}")
        available_models = models_data.get('available_models', [])
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    if not available_models:
        print("⚠️  No models available. Please train models first using 'python train.py'")
        return False
    
    # Test 3: Home/Info Endpoint
    print("\n3. Testing Home/Info Endpoint")
    print("-" * 40)
    url = f"{base_url}/"
    print_curl_command("GET", url)
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Text Generation
    print("\n4. Testing Text Generation")
    print("-" * 40)
    
    test_prompts = [
        "The future of artificial intelligence",
        "Machine learning has revolutionized",
        "Deep neural networks can",
        ""  # Empty prompt test
    ]
    
    for model_type in available_models:
        print(f"\n4.{available_models.index(model_type) + 1} Testing {model_type.upper()} model")
        print(f"Model: {model_type}")
        
        for i, prompt in enumerate(test_prompts[:2]):  # Test first 2 prompts
            print(f"\nPrompt {i+1}: '{prompt}'")
            
            url = f"{base_url}/generate"
            data = {
                "model_type": model_type,
                "prompt": prompt,
                "max_length": 50,
                "temperature": 0.8,
                "top_k": 50
            }
            
            print_curl_command("POST", url, data, headers)
            
            try:
                response = requests.post(url, json=data, headers=headers, timeout=30)
                print(f"Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"Generated Text: {result['generated_text']}")
                    print(f"Model Used: {result['model_type']}")
                else:
                    print(f"Error Response: {response.json()}")
                    
            except Exception as e:
                print(f"Error: {e}")
    
    # Test 5: Model Comparison
    print("\n5. Testing Model Comparison")
    print("-" * 40)
    
    url = f"{base_url}/compare"
    data = {
        "prompt": "Artificial intelligence will",
        "max_length": 30,
        "temperature": 0.8,
        "top_k": 50
    }
    
    print_curl_command("POST", url, data, headers)
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=60)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Prompt: {result['prompt']}")
            print("Comparison Results:")
            for model, text in result['results'].items():
                print(f"  {model.upper()}: {text}")
        else:
            print(f"Error Response: {response.json()}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 6: Error Handling
    print("\n6. Testing Error Handling")
    print("-" * 40)
    
    # Test with invalid model
    url = f"{base_url}/generate"
    data = {
        "model_type": "invalid_model",
        "prompt": "test",
        "max_length": 10
    }
    
    print("Testing invalid model type:")
    print_curl_command("POST", url, data, headers)
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Error Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    return True


def generate_curl_examples():
    """Generate example cURL commands for documentation."""
    
    print("\n" + "=" * 80)
    print("CURL COMMAND EXAMPLES FOR API TESTING")
    print("=" * 80)
    
    base_url = "http://localhost:5000"
    
    examples = [
        {
            "title": "1. Health Check",
            "command": f'curl -X GET {base_url}/health'
        },
        {
            "title": "2. List Available Models",
            "command": f'curl -X GET {base_url}/models'
        },
        {
            "title": "3. Generate Text with Hybrid Model",
            "command": f'''curl -X POST {base_url}/generate \\
  -H "Content-Type: application/json" \\
  -d '{{"model_type": "hybrid", "prompt": "The future of AI", "max_length": 50}}\''''
        },
        {
            "title": "4. Generate Text with Transformer",
            "command": f'''curl -X POST {base_url}/generate \\
  -H "Content-Type: application/json" \\
  -d '{{"model_type": "transformer", "prompt": "Deep learning", "max_length": 30}}\''''
        },
        {
            "title": "5. Generate Text with RNN",
            "command": f'''curl -X POST {base_url}/generate \\
  -H "Content-Type: application/json" \\
  -d '{{"model_type": "rnn", "prompt": "Neural networks", "max_length": 40}}\''''
        },
        {
            "title": "6. Compare All Models",
            "command": f'''curl -X POST {base_url}/compare \\
  -H "Content-Type: application/json" \\
  -d '{{"prompt": "Machine learning is", "max_length": 25}}\''''
        },
        {
            "title": "7. Generate with Custom Parameters",
            "command": f'''curl -X POST {base_url}/generate \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model_type": "hybrid",
    "prompt": "Transformers have revolutionized",
    "max_length": 60,
    "temperature": 0.9,
    "top_k": 40
  }}\''''
        }
    ]
    
    for example in examples:
        print(f"\n{example['title']}:")
        print(f"{example['command']}")
    
    print(f"\n{'='*80}")
    print("SAVE THESE COMMANDS TO TEST THE API MANUALLY")
    print(f"{'='*80}")


def test_with_curl():
    """Test API using actual cURL commands."""
    
    print("\n" + "=" * 80)
    print("TESTING WITH ACTUAL CURL COMMANDS")
    print("=" * 80)
    
    base_url = "http://localhost:5000"
    
    # Simple health check with cURL
    print("\n1. Testing health check with cURL:")
    try:
        result = subprocess.run(['curl', '-s', f'{base_url}/health'], 
                              capture_output=True, text=True, timeout=10)
        print(f"cURL output: {result.stdout}")
        if result.stderr:
            print(f"cURL error: {result.stderr}")
    except Exception as e:
        print(f"cURL test failed: {e}")
    
    # Test text generation with cURL
    print("\n2. Testing text generation with cURL:")
    curl_cmd = [
        'curl', '-s', '-X', 'POST',
        f'{base_url}/generate',
        '-H', 'Content-Type: application/json',
        '-d', '{"model_type": "hybrid", "prompt": "AI will", "max_length": 20}'
    ]
    
    try:
        result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=30)
        print(f"cURL output: {result.stdout}")
        if result.stderr:
            print(f"cURL error: {result.stderr}")
    except Exception as e:
        print(f"cURL test failed: {e}")


def check_api_server():
    """Check if API server is running."""
    base_url = "http://localhost:5000"
    
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def main():
    """Main function to run API tests."""
    
    print("RNN + Transformer Language Model API Tester")
    print("=" * 60)
    
    # Check if server is running
    if not check_api_server():
        print("❌ API server is not running!")
        print("\nTo start the server, run:")
        print("  python api.py")
        print("\nMake sure you have trained models first:")
        print("  python train.py")
        return
    
    print("✅ API server is running")
    
    # Run tests
    try:
        success = test_api_endpoint()
        
        if success:
            print("\n✅ All API tests completed successfully!")
        else:
            print("\n❌ Some tests failed. Check the output above.")
        
        # Generate cURL examples
        generate_curl_examples()
        
        # Test with actual cURL (if available)
        if input("\nTest with actual cURL commands? (y/N): ").lower().startswith('y'):
            test_with_curl()
        
    except KeyboardInterrupt:
        print("\n\nTesting interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
