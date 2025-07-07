#!/usr/bin/env python3
"""
Example usage of the Ollama FastAPI server with prompt templates
"""

import requests
import json

# Server configuration
BASE_URL = "http://localhost:8000"

def example_simple_chat():
    """Example of simple chat without system prompt"""
    print("🔹 Simple Chat Example")
    print("-" * 30)
    
    payload = {
        "question": "What is Python programming?",
        "model": "llama3",
        "temperature": 0.7
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Answer: {data['answer'][:200]}...")
    else:
        print(f"Error: {response.status_code}")

def example_custom_system_prompt():
    """Example using custom system prompt"""
    print("\n🔹 Custom System Prompt Example")
    print("-" * 30)
    
    payload = {
        "question": "Explain quantum computing",
        "system_prompt": "You are a physics professor who explains complex topics using simple analogies and examples that a high school student can understand.",
        "model": "llama3",
        "temperature": 0.7,
        "max_tokens": 300
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"System Prompt Used: {data['system_prompt_used'][:60]}...")
        print(f"Answer: {data['answer'][:200]}...")
    else:
        print(f"Error: {response.status_code}")

def example_predefined_template():
    """Example using predefined template"""
    print("\n🔹 Predefined Template Example")
    print("-" * 30)
    
    # First, let's see available templates
    templates_response = requests.get(f"{BASE_URL}/templates")
    if templates_response.status_code == 200:
        templates = templates_response.json()
        print("Available templates:")
        for name, info in templates['templates'].items():
            print(f"  - {name}: {info['description']}")
    
    # Use the code_helper template
    payload = {
        "question": "How do I create a REST API in Python?",
        "template_name": "code_helper",
        "model": "llama3",
        "temperature": 0.7,
        "max_tokens": 400
    }
    
    response = requests.post(f"{BASE_URL}/chat/template", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nTemplate Used: {data['template_used']}")
        print(f"Answer: {data['answer'][:200]}...")
    else:
        print(f"Error: {response.status_code}")

def example_teacher_template():
    """Example using teacher template for educational content"""
    print("\n🔹 Teacher Template Example")
    print("-" * 30)
    
    payload = {
        "question": "machine learning algorithms",
        "template_name": "teacher",
        "model": "llama3",
        "temperature": 0.6,
        "max_tokens": 350
    }
    
    response = requests.post(f"{BASE_URL}/chat/template", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Template Used: {data['template_used']}")
        print(f"Answer: {data['answer'][:200]}...")
    else:
        print(f"Error: {response.status_code}")

def example_creative_writer_template():
    """Example using creative writer template"""
    print("\n🔹 Creative Writer Template Example")
    print("-" * 30)
    
    payload = {
        "question": "Write a short story about a robot learning to paint",
        "template_name": "creative_writer",
        "model": "llama3",
        "temperature": 0.9,  # Higher temperature for creativity
        "max_tokens": 400
    }
    
    response = requests.post(f"{BASE_URL}/chat/template", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Template Used: {data['template_used']}")
        print(f"Story: {data['answer'][:300]}...")
    else:
        print(f"Error: {response.status_code}")

def example_business_advisor_template():
    """Example using business advisor template"""
    print("\n🔹 Business Advisor Template Example")
    print("-" * 30)
    
    payload = {
        "question": "How can a small startup improve customer retention?",
        "template_name": "business_advisor",
        "model": "llama3",
        "temperature": 0.7,
        "max_tokens": 350
    }
    
    response = requests.post(f"{BASE_URL}/chat/template", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Template Used: {data['template_used']}")
        print(f"Advice: {data['answer'][:200]}...")
    else:
        print(f"Error: {response.status_code}")

def example_compare_responses():
    """Compare responses with and without templates"""
    print("\n🔹 Comparison: With vs Without Template")
    print("-" * 30)
    
    question = "Explain neural networks"
    
    # Without template
    print("Without template:")
    payload1 = {
        "question": question,
        "model": "llama3",
        "temperature": 0.7,
        "max_tokens": 200
    }
    
    response1 = requests.post(f"{BASE_URL}/chat", json=payload1)
    if response1.status_code == 200:
        data1 = response1.json()
        print(f"Response: {data1['answer'][:150]}...")
    
    # With teacher template
    print("\nWith teacher template:")
    payload2 = {
        "question": question,
        "template_name": "teacher",
        "model": "llama3",
        "temperature": 0.7,
        "max_tokens": 200
    }
    
    response2 = requests.post(f"{BASE_URL}/chat/template", json=payload2)
    if response2.status_code == 200:
        data2 = response2.json()
        print(f"Response: {data2['answer'][:150]}...")

def main():
    print("🦙 Ollama FastAPI Server - Prompt Template Examples")
    print("=" * 60)
    
    # Check if server is running
    try:
        health_response = requests.get(f"{BASE_URL}/health")
        if health_response.status_code != 200:
            print("❌ Server is not running. Please start the FastAPI server first.")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please start the FastAPI server first.")
        print("Run: python main.py")
        return
    
    print("✅ Server is running. Running examples...\n")
    
    # Run examples
    example_simple_chat()
    example_custom_system_prompt()
    example_predefined_template()
    example_teacher_template()
    example_creative_writer_template()
    example_business_advisor_template()
    example_compare_responses()
    
    print("\n" + "=" * 60)
    print("✅ All examples completed!")
    print(f"🌐 Open the web client: {BASE_URL}")
    print("📚 API docs: {}/docs".format(BASE_URL))

if __name__ == "__main__":
    main()
