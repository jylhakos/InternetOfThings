#!/usr/bin/env python3
"""
Prompt Templates Example for the Redis Queue + LangChain + Ollama system.
This script demonstrates how prompt templates work and can be tested.
"""

import requests
import json
import time
from typing import Dict, Any

class PromptTemplateDemo:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        
    def test_template_types(self):
        """Test different prompt template types."""
        
        # Test questions for different template types
        test_cases = [
            {
                "question": "What is machine learning?",
                "template_type": "default",
                "description": "Default conversational template"
            },
            {
                "question": "What is machine learning?",
                "template_type": "technical",
                "description": "Technical expert template"
            },
            {
                "question": "Write a story about a robot learning to paint",
                "template_type": "creative",
                "description": "Creative assistant template"
            },
            {
                "question": "How are you doing today?",
                "template_type": "chat",
                "description": "Friendly chat template"
            }
        ]
        
        print("Prompt Templates Demonstration")
        print("=" * 50)
        print("\nThis demo shows how different prompt templates affect LLM responses")
        print("to the same or similar questions.\n")
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. Testing: {test_case['description']}")
            print(f"   Question: {test_case['question']}")
            print(f"   Template: {test_case['template_type']}")
            print("-" * 40)
            
            # Submit the question
            result = self.submit_and_wait(
                test_case['question'], 
                template_type=test_case['template_type']
            )
            
            if result.get('status') == 'finished':
                response = result.get('result', 'No response')
                print(f"   Response: {response[:200]}...")
                if len(response) > 200:
                    print("   [Response truncated]")
                print(f"   Processing time: {result.get('processing_time', 0):.2f}s")
            else:
                print(f"   Error: {result.get('error', 'Unknown error')}")
    
    def submit_and_wait(self, question: str, template_type: str = "default", max_wait: int = 60) -> Dict[str, Any]:
        """Submit a question and wait for the result."""
        
        # Note: This is a conceptual example. The actual template_type parameter
        # would need to be supported in the FastAPI endpoint and passed through
        # to the LangChain.js service.
        
        payload = {
            "question": question,
            "model": "llama3.2:1b",
            "temperature": 0.7,
            "max_tokens": 500,
            # "template_type": template_type  # This would be added to the API
        }
        
        try:
            # Submit question
            response = requests.post(f"{self.base_url}/generate_async/", json=payload)
            response.raise_for_status()
            job_data = response.json()
            job_id = job_data.get("job_id")
            
            # Wait for result
            start_time = time.time()
            while time.time() - start_time < max_wait:
                result_response = requests.get(f"{self.base_url}/get_result/{job_id}")
                result_response.raise_for_status()
                result = result_response.json()
                
                status = result.get("status")
                if status in ["finished", "failed"]:
                    return result
                
                time.sleep(2)
            
            return {"error": "Timeout waiting for result"}
            
        except Exception as e:
            return {"error": str(e)}

def show_template_explanations():
    """Show explanations of different prompt templates."""
    
    templates_info = {
        "default": {
            "description": "A general-purpose conversational template",
            "use_case": "Standard Q&A, general information requests",
            "template": "You are a helpful assistant. Answer the following question accurately and concisely:\n\nQuestion: {question}\n\nAnswer:"
        },
        "chat": {
            "description": "A friendly, conversational template for chat interactions",
            "use_case": "Casual conversations, friendly interactions",
            "template": "You are a helpful AI assistant in a chat conversation. Provide a friendly and informative response to the user's message.\n\nUser: {question}\n\nAssistant:"
        },
        "technical": {
            "description": "A template for detailed technical explanations",
            "use_case": "Programming questions, technical documentation, scientific explanations",
            "template": "You are a technical expert. Provide a detailed and accurate technical response to the following question:\n\nQuestion: {question}\n\nTechnical Response:"
        },
        "creative": {
            "description": "A template for creative and imaginative responses",
            "use_case": "Creative writing, storytelling, artistic prompts",
            "template": "You are a creative assistant. Provide an imaginative and engaging response to the following prompt:\n\nPrompt: {question}\n\nCreative Response:"
        }
    }
    
    print("Prompt Templates Explanation")
    print("=" * 40)
    print("\nPrompt templates provide pre-defined structures for creating consistent")
    print("prompts that are sent to LLMs. They help shape the AI's behavior and")
    print("response style based on the context and purpose of the interaction.\n")
    
    for template_name, info in templates_info.items():
        print(f"📋 {template_name.upper()} TEMPLATE")
        print(f"   Description: {info['description']}")
        print(f"   Use Case: {info['use_case']}")
        print(f"   Template Structure:")
        print(f"   ```")
        for line in info['template'].split('\n'):
            print(f"   {line}")
        print(f"   ```\n")
    
    print("🔧 How Prompt Templates Work:")
    print("1. The template defines the structure and context for the AI")
    print("2. The user's question is inserted into the {question} placeholder")
    print("3. The complete prompt is sent to the LLM (e.g., Llama)")
    print("4. The LLM generates a response following the template's guidance")
    print("\n💡 Benefits:")
    print("- Consistent response formatting")
    print("- Context-appropriate behavior")
    print("- Better control over AI personality")
    print("- Improved response quality for specific use cases")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "explain":
        show_template_explanations()
    else:
        demo = PromptTemplateDemo()
        
        print("Note: This demo requires the full system to be running.")
        print("Start the system with: ./start.sh")
        print("\nFor template explanations, run: python prompt_templates_example.py explain\n")
        
        try:
            # Check if system is running
            health_response = requests.get("http://localhost:8000/health", timeout=5)
            if health_response.status_code == 200:
                demo.test_template_types()
            else:
                print("❌ System is not healthy. Please check your setup.")
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to the FastAPI server.")
            print("Please start the system first: ./start.sh")
        except Exception as e:
            print(f"❌ Error: {e}")
