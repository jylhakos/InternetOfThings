# Example Python Client for Spring AI RAG Demo

import requests
import json
from typing import Optional, Dict, Any

class SpringAIChatClient:
    """
    Python client for interacting with Spring AI RAG API
    """
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.chat_url = f"{base_url}/api/chat"
    
    def ask_simple(self, question: str) -> Dict[str, Any]:
        """
        Ask a simple question using default RAG settings
        
        Args:
            question: The question to ask
            
        Returns:
            Response dictionary with answer, sources, etc.
        """
        response = requests.post(
            f"{self.chat_url}/ask",
            params={"question": question}
        )
        response.raise_for_status()
        return response.json()
    
    def ask_advanced(
        self,
        question: str,
        include_context: bool = True,
        similarity_threshold: float = 0.7,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Ask a question with advanced RAG parameters
        
        Args:
            question: The question to ask
            include_context: Whether to use RAG (True) or direct query (False)
            similarity_threshold: Minimum similarity score (0.0-1.0)
            top_k: Number of documents to retrieve
            
        Returns:
            Response dictionary with answer, sources, response time, etc.
        """
        payload = {
            "question": question,
            "includeContext": include_context,
            "similarityThreshold": similarity_threshold,
            "topK": top_k
        }
        
        response = requests.post(
            self.chat_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> str:
        """Check if the service is running"""
        response = requests.get(f"{self.chat_url}/health")
        response.raise_for_status()
        return response.text


def main():
    # Create client
    client = SpringAIChatClient()
    
    # Health check
    print("Health Check:")
    print(client.health_check())
    print("\n" + "="*60 + "\n")
    
    # Example 1: Simple question
    print("Example 1: Simple Question")
    result = client.ask_simple("What is Spring AI?")
    print(f"Question: What is Spring AI?")
    print(f"Answer: {result['answer']}")
    print(f"Response Time: {result['responseTimeMs']}ms")
    print(f"Model: {result['model']}")
    print("\n" + "="*60 + "\n")
    
    # Example 2: Advanced query
    print("Example 2: Advanced Query with Parameters")
    result = client.ask_advanced(
        question="How does Retrieval Augmented Generation work?",
        similarity_threshold=0.8,
        top_k=3
    )
    print(f"Question: How does Retrieval Augmented Generation work?")
    print(f"Answer: {result['answer']}")
    print(f"Sources: {result['sources']}")
    print(f"Response Time: {result['responseTimeMs']}ms")
    print("\n" + "="*60 + "\n")
    
    # Example 3: High precision query
    print("Example 3: High Precision Query")
    result = client.ask_advanced(
        question="What is the ChatClient API?",
        similarity_threshold=0.9,
        top_k=2
    )
    print(f"Question: What is the ChatClient API?")
    print(f"Answer: {result['answer'][:200]}...")  # Truncate for display
    print(f"Sources: {result['sources']}")
    print("\n" + "="*60 + "\n")
    
    # Example 4: Direct query without RAG
    print("Example 4: Direct Query (No RAG)")
    result = client.ask_advanced(
        question="What is 5 + 3?",
        include_context=False
    )
    print(f"Question: What is 5 + 3?")
    print(f"Answer: {result['answer']}")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not connect to Spring AI service")
        print(f"Make sure the application is running on http://localhost:8080")
        print(f"Details: {e}")
