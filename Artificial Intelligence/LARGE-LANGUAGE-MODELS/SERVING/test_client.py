#!/usr/bin/env python3
"""
Simple test client for the Ollama FastAPI server
"""

import requests
import json
import sys
from typing import Dict, Any

def test_health(base_url: str = "http://localhost:8000") -> bool:
    """Test server health"""
    try:
        response = requests.get(f"{base_url}/health")
        data = response.json()
        print(f"Health Status: {data['status']}")
        print(f"Message: {data['message']}")
        print(f"Ollama Connected: {data['ollama_connected']}")
        return data['ollama_connected']
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_models(base_url: str = "http://localhost:8000") -> None:
    """List available models"""
    try:
        response = requests.get(f"{base_url}/models")
        data = response.json()
        print(f"Available models ({data['count']}):")
        for model in data['models']:
            print(f"  - {model}")
    except Exception as e:
        print(f"❌ Failed to get models: {e}")

def test_chat(question: str, model: str = "llama3", base_url: str = "http://localhost:8000") -> None:
    """Test chat endpoint"""
    try:
        payload = {
            "question": question,
            "model": model,
            "max_tokens": 200,
            "temperature": 0.7
        }
        
        print(f"\n🤖 Asking {model}: {question}")
        print("Waiting for response...")
        
        response = requests.post(f"{base_url}/chat", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Response from {data['model']}:")
            print(f"Answer: {data['answer']}")
            if data.get('usage'):
                print(f"Tokens used: {data['usage']}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Chat test failed: {e}")

def test_templates(base_url: str = "http://localhost:8000") -> None:
    """Test template endpoints"""
    try:
        print(f"\n📋 Testing template endpoints...")
        
        # List templates
        response = requests.get(f"{base_url}/templates")
        if response.status_code == 200:
            data = response.json()
            print(f"Available templates ({data['count']}):")
            for name, info in data['templates'].items():
                print(f"  - {name}: {info['description']}")
        else:
            print(f"❌ Failed to list templates: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Template list test failed: {e}")

def test_template_chat(question: str, template_name: str, model: str = "llama3", base_url: str = "http://localhost:8000") -> None:
    """Test templated chat endpoint"""
    try:
        payload = {
            "question": question,
            "template_name": template_name,
            "model": model,
            "max_tokens": 200,
            "temperature": 0.7
        }
        
        print(f"\n🎯 Testing template '{template_name}' with {model}")
        print(f"Question: {question}")
        print("Waiting for response...")
        
        response = requests.post(f"{base_url}/chat/template", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Template response from {data['model']}:")
            print(f"Template used: {data['template_used']}")
            print(f"System prompt: {data['system_prompt_used'][:50]}...")
            print(f"Answer: {data['answer']}")
            if data.get('usage'):
                print(f"Tokens used: {data['usage']}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Template chat test failed: {e}")

def test_custom_system_prompt(question: str, system_prompt: str, model: str = "llama3", base_url: str = "http://localhost:8000") -> None:
    """Test custom system prompt"""
    try:
        payload = {
            "question": question,
            "system_prompt": system_prompt,
            "model": model,
            "max_tokens": 200,
            "temperature": 0.7
        }
        
        print(f"\n🎯 Testing custom system prompt with {model}")
        print(f"System prompt: {system_prompt}")
        print(f"Question: {question}")
        print("Waiting for response...")
        
        response = requests.post(f"{base_url}/chat", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Custom prompt response from {data['model']}:")
            print(f"System prompt used: {data['system_prompt_used'][:50]}...")
            print(f"Answer: {data['answer']}")
            if data.get('usage'):
                print(f"Tokens used: {data['usage']}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Custom prompt test failed: {e}")

def main():
    base_url = "http://localhost:8000"
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    print("🧪 Testing Ollama FastAPI Server")
    print("=" * 40)
    
    # Test health
    print("\n1. Testing Health Endpoint")
    healthy = test_health(base_url)
    
    if not healthy:
        print("❌ Server is not healthy. Please check Ollama and FastAPI server.")
        return
    
    # Test models
    print("\n2. Testing Models Endpoint")
    test_models(base_url)
    
    # Test simple chat
    print("\n3. Testing Simple Chat Endpoint")
    test_chat("What is 2+2?", "llama3", base_url)
    
    # Test templates
    print("\n4. Testing Template Endpoints")
    test_templates(base_url)
    
    # Test template chat
    print("\n5. Testing Templated Chat Endpoint")
    test_template_chat("Explain what Python is", "teacher", "llama3", base_url)
    
    # Test custom system prompt
    print("\n6. Testing Custom System Prompt")
    test_custom_system_prompt(
        "What is machine learning?", 
        "You are a technical expert who explains complex topics simply and clearly.", 
        "llama3", 
        base_url
    )
    
    print("\n✅ All tests completed!")
    print(f"\nYou can also open the web client at: {base_url}")
    print("Or serve the client.html file and access it in your browser.")

if __name__ == "__main__":
    main()
