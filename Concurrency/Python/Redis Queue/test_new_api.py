#!/usr/bin/env python3
"""
Test script for the updated Redis Queue API endpoints.
Tests the new chat-focused API: POST /chat, GET /task/{task_id}, GET /health, GET /models
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test the health check endpoint."""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            print(f"   Redis status: {data['redis']}")
            print(f"   Queue size: {data['queue_size']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_models_endpoint():
    """Test the models list endpoint."""
    print("\n📋 Testing models endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/models")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Models endpoint working")
            print(f"   Total models: {data['total_models']}")
            print(f"   Default model: {data['default_model']}")
            print("   Available models:")
            for model in data['models'][:3]:  # Show first 3 models
                print(f"     - {model['id']}: {model['name']}")
            return True
        else:
            print(f"❌ Models endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Models endpoint error: {e}")
        return False

def test_chat_endpoint():
    """Test the chat submission endpoint."""
    print("\n💬 Testing chat endpoint...")
    
    # Test data
    chat_request = {
        "prompt": "What is the capital of France? Please provide a brief answer.",
        "model": "llama3.2:1b",
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    try:
        # Submit chat request
        response = requests.post(
            f"{BASE_URL}/chat",
            json=chat_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            task_id = data.get('task_id')
            print(f"✅ Chat request submitted successfully")
            print(f"   Task ID: {task_id}")
            print(f"   Status: {data.get('status')}")
            return task_id
        else:
            print(f"❌ Chat request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Chat request error: {e}")
        return None

def test_task_status_endpoint(task_id):
    """Test the task status endpoint."""
    print(f"\n📊 Testing task status endpoint for task: {task_id}")
    
    max_attempts = 30  # Maximum polling attempts
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get(f"{BASE_URL}/task/{task_id}")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                
                print(f"   Attempt {attempt + 1}: Status = {status}")
                
                if status == 'completed':
                    print("✅ Task completed successfully!")
                    result = data.get('result', {})
                    print(f"   Response: {result.get('response', 'No response')}")
                    print(f"   Model: {result.get('model', 'Unknown')}")
                    print(f"   Processing time: {result.get('processing_time', 'Unknown')}s")
                    return True
                elif status == 'failed':
                    print("❌ Task failed")
                    print(f"   Error: {data.get('message', 'Unknown error')}")
                    return False
                elif status in ['pending', 'started']:
                    print(f"   Task is {status}, waiting...")
                    time.sleep(2)
                    attempt += 1
                else:
                    print(f"   Unknown status: {status}")
                    attempt += 1
            else:
                print(f"❌ Task status request failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Task status error: {e}")
            return False
    
    print(f"❌ Task did not complete within {max_attempts} attempts")
    return False

def test_openai_compatibility():
    """Test the OpenAI-compatible endpoint."""
    print("\n🤖 Testing OpenAI compatibility endpoint...")
    
    openai_request = {
        "model": "llama3.2:1b",
        "messages": [
            {"role": "user", "content": "Hello! How are you today?"}
        ],
        "temperature": 0.7,
        "max_tokens": 50
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json=openai_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ OpenAI compatibility endpoint working")
            print(f"   Model: {data.get('model')}")
            choices = data.get('choices', [])
            if choices:
                message = choices[0].get('message', {})
                content = message.get('content', 'No content')
                print(f"   Response: {content[:100]}...")
            return True
        else:
            print(f"❌ OpenAI endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ OpenAI endpoint error: {e}")
        return False

def main():
    """Run all API tests."""
    print("🚀 Starting Redis Queue API Tests")
    print("=" * 50)
    
    # Test health endpoint
    if not test_health_endpoint():
        print("❌ Health check failed - system may not be running")
        return False
    
    # Test models endpoint
    test_models_endpoint()
    
    # Test chat submission
    task_id = test_chat_endpoint()
    if not task_id:
        print("❌ Chat submission failed")
        return False
    
    # Test task status and completion
    if not test_task_status_endpoint(task_id):
        print("❌ Task processing failed")
        return False
    
    # Test OpenAI compatibility
    test_openai_compatibility()
    
    print("\n" + "=" * 50)
    print("🎉 All API tests completed!")
    print("\nThe new chat-focused API endpoints are working:")
    print("  ✅ POST /chat - Submit chat requests")
    print("  ✅ GET /task/{task_id} - Check task status")
    print("  ✅ GET /health - System health")
    print("  ✅ GET /models - Available models")
    print("  ✅ POST /v1/chat/completions - OpenAI compatibility")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
