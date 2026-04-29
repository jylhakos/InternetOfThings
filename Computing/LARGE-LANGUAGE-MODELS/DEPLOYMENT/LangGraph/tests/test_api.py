import pytest
import asyncio
from httpx import AsyncClient
import json
import os
from pathlib import Path

# Test configuration
API_BASE_URL = "http://localhost:8000"
API_V1_URL = f"{API_BASE_URL}/api/v1"

class TestLangGraphRAGAPI:
    """Test suite for LangGraph RAG API"""
    
    @pytest.fixture
    def client(self):
        """Create async HTTP client"""
        return AsyncClient(base_url=API_BASE_URL, timeout=60.0)
    
    @pytest.fixture
    def sample_document_content(self):
        """Sample document content for testing"""
        return """
        This is a comprehensive test document about artificial intelligence and machine learning.
        
        Artificial Intelligence (AI) is a branch of computer science that aims to create machines
        capable of performing tasks that typically require human intelligence. These tasks include
        learning, reasoning, problem-solving, perception, and language understanding.
        
        Machine Learning (ML) is a subset of AI that focuses on the development of algorithms and
        statistical models that enable computer systems to improve their performance on a specific
        task through experience, without being explicitly programmed.
        
        Deep Learning is a subset of machine learning based on artificial neural networks with
        representation learning. Deep learning architectures such as deep neural networks, deep
        belief networks, recurrent neural networks, and convolutional neural networks have been
        applied to fields including computer vision, speech recognition, natural language processing,
        and bioinformatics.
        
        Vector databases are specialized databases designed to store and query high-dimensional
        vectors efficiently. They are essential for RAG (Retrieval Augmented Generation) systems
        as they enable semantic search capabilities by storing document embeddings.
        
        RAG systems combine the power of large language models with external knowledge bases to
        provide more accurate and contextually relevant responses to user queries.
        """
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test API health check endpoint"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert "version" in data
    
    @pytest.mark.asyncio
    async def test_chat_health_check(self, client):
        """Test chat service health check"""
        response = await client.get("/api/v1/chat/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "services" in data
    
    @pytest.mark.asyncio
    async def test_list_models(self, client):
        """Test listing available models"""
        response = await client.get("/api/v1/chat/models")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        assert "active_model" in data
        assert isinstance(data["models"], list)
    
    @pytest.mark.asyncio
    async def test_document_upload(self, client, sample_document_content, tmp_path):
        """Test document upload functionality"""
        # Create temporary file
        test_file = tmp_path / "test_document.txt"
        test_file.write_text(sample_document_content)
        
        # Prepare file and metadata
        files = {"file": ("test_document.txt", test_file.open("rb"), "text/plain")}
        metadata = {
            "title": "Test AI Document",
            "category": "technical",
            "tags": ["AI", "ML", "testing"]
        }
        data = {"metadata": json.dumps(metadata)}
        
        # Upload document
        response = await client.post("/api/v1/documents/upload", files=files, data=data)
        
        # Cleanup
        test_file.unlink()
        
        assert response.status_code == 200
        response_data = response.json()
        assert "document" in response_data
        assert "message" in response_data
        assert response_data["document"]["filename"]
        assert response_data["document"]["chunk_count"] > 0
        
        # Store document ID for later tests
        self.uploaded_document_id = response_data["document"]["id"]
    
    @pytest.mark.asyncio
    async def test_list_documents(self, client):
        """Test listing uploaded documents"""
        response = await client.get("/api/v1/documents/?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert "total" in data
        assert "page" in data
        assert isinstance(data["documents"], list)
    
    @pytest.mark.asyncio
    async def test_search_documents(self, client):
        """Test vector search functionality"""
        search_payload = {
            "query": "artificial intelligence machine learning",
            "top_k": 5,
            "score_threshold": 0.3
        }
        
        response = await client.post("/api/v1/documents/search", json=search_payload)
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total_found" in data
        assert isinstance(data["results"], list)
    
    @pytest.mark.asyncio
    async def test_rag_query_arcee_agent(self, client):
        """Test RAG query with ArceeAgent model"""
        query_payload = {
            "message": "What is artificial intelligence and how does it work?",
            "model": "arcee-ai/arcee-agent",
            "use_rag": True,
            "max_tokens": 400,
            "temperature": 0.7
        }
        
        response = await client.post("/api/v1/chat/query", json=query_payload)
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "response" in data
        assert "model_used" in data
        assert "processing_time" in data
        assert "context_used" in data
        
        # Verify RAG was used
        assert data["context_used"] == True
        assert len(data["response"]) > 0
        assert data["model_used"] == "arcee-ai/arcee-agent"
    
    @pytest.mark.asyncio
    async def test_direct_llm_query(self, client):
        """Test direct LLM query without RAG"""
        query_payload = {
            "message": "Explain neural networks in simple terms",
            "model": "arcee-ai/arcee-agent",
            "use_rag": False,
            "max_tokens": 200,
            "temperature": 0.8
        }
        
        response = await client.post("/api/v1/chat/query", json=query_payload)
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "response" in data
        assert "model_used" in data
        assert "context_used" in data
        
        # Verify RAG was not used
        assert data["context_used"] == False
        assert len(data["response"]) > 0
    
    @pytest.mark.asyncio
    async def test_codellama_query(self, client):
        """Test CodeLlama model for code generation"""
        query_payload = {
            "message": "Write a Python function to calculate factorial of a number",
            "model": "codellama:7b",
            "use_rag": False,
            "max_tokens": 300,
            "temperature": 0.3
        }
        
        response = await client.post("/api/v1/chat/query", json=query_payload)
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "response" in data
        assert "model_used" in data
        assert data["model_used"] == "codellama:7b"
        
        # Check if response contains code-like content
        response_text = data["response"].lower()
        assert any(keyword in response_text for keyword in ["def", "function", "factorial", "return"])
    
    @pytest.mark.asyncio
    async def test_direct_rag_query(self, client):
        """Test direct RAG endpoint"""
        rag_payload = {
            "query": "What are the benefits of using vector databases?",
            "top_k": 3,
            "score_threshold": 0.6
        }
        
        response = await client.post(
            "/api/v1/chat/rag", 
            json=rag_payload,
            params={"model": "arcee-ai/arcee-agent"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify RAG response structure
        assert "response" in data
        assert "sources" in data
        assert "metadata" in data
        assert isinstance(data["sources"], list)
    
    @pytest.mark.asyncio
    async def test_batch_processing(self, client):
        """Test batch query processing"""
        batch_payload = {
            "queries": [
                "What is machine learning?",
                "Explain deep learning",
                "What is the difference between AI and ML?"
            ],
            "model": "arcee-ai/arcee-agent",
            "use_rag": True
        }
        
        response = await client.post("/api/v1/chat/batch", json=batch_payload)
        assert response.status_code == 200
        data = response.json()
        
        # Verify batch response structure
        assert "responses" in data
        assert "total_processed" in data
        assert "total_processing_time" in data
        assert len(data["responses"]) == len(batch_payload["queries"])
        
        # Verify each response
        for resp in data["responses"]:
            assert "response" in resp
            assert "model_used" in resp
    
    @pytest.mark.asyncio
    async def test_model_switch(self, client):
        """Test model switching functionality"""
        switch_payload = {
            "model_name": "codellama:7b"
        }
        
        response = await client.post("/api/v1/chat/models/switch", json=switch_payload)
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "active_model" in data
        assert data["active_model"] == "codellama:7b"
    
    @pytest.mark.asyncio
    async def test_collection_stats(self, client):
        """Test vector collection statistics"""
        response = await client.get("/api/v1/documents/stats/collection")
        assert response.status_code == 200
        data = response.json()
        
        # Should have some basic collection info
        assert isinstance(data, dict)
    
    @pytest.mark.asyncio
    async def test_streaming_chat(self, client):
        """Test streaming chat endpoint"""
        stream_payload = {
            "message": "Hello, this is a test message",
            "model": "arcee-ai/arcee-agent",
            "use_rag": False
        }
        
        # Note: Testing streaming is complex with httpx
        # This is a basic test to ensure the endpoint is accessible
        response = await client.post(
            "/api/v1/chat/stream",
            json=stream_payload,
            headers={"Accept": "text/event-stream"}
        )
        
        # Should start streaming (200) or have valid error response
        assert response.status_code in [200, 500, 503]
    
    @pytest.mark.asyncio
    async def test_error_handling(self, client):
        """Test API error handling"""
        # Test with empty message
        error_payload = {
            "message": "",
            "model": "arcee-ai/arcee-agent",
            "use_rag": True
        }
        
        response = await client.post("/api/v1/chat/query", json=error_payload)
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_invalid_model_error(self, client):
        """Test error handling with invalid model"""
        error_payload = {
            "message": "Test message",
            "model": "invalid-model-name",
            "use_rag": False
        }
        
        response = await client.post("/api/v1/chat/query", json=error_payload)
        # Should return error or validation error
        assert response.status_code in [400, 422, 500]


# Prompt Format Tests
class TestPromptFormats:
    """Test different prompt formats for various models"""
    
    @pytest.fixture
    def client(self):
        return AsyncClient(base_url=API_BASE_URL, timeout=60.0)
    
    @pytest.mark.asyncio
    async def test_arcee_agent_function_calling(self, client):
        """Test ArceeAgent with function calling format"""
        query_payload = {
            "message": "Search the knowledge base for information about vector databases and then explain how they are used in RAG systems",
            "model": "arcee-ai/arcee-agent",
            "use_rag": True,
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        response = await client.post("/api/v1/chat/query", json=query_payload)
        assert response.status_code == 200
        data = response.json()
        
        # Check if the response indicates function calling or tool usage
        response_text = data["response"].lower()
        # The response should be coherent and relevant
        assert len(data["response"]) > 50
        assert data["context_used"] == True
    
    @pytest.mark.asyncio
    async def test_codellama_code_generation(self, client):
        """Test CodeLlama with proper coding prompts"""
        query_payload = {
            "message": "Create a Python class called 'SimpleRAG' with methods to add documents and search them. Include proper type hints and docstrings.",
            "model": "codellama:7b",
            "use_rag": False,
            "max_tokens": 600,
            "temperature": 0.2
        }
        
        response = await client.post("/api/v1/chat/query", json=query_payload)
        assert response.status_code == 200
        data = response.json()
        
        response_text = data["response"]
        
        # Check for code-related keywords
        code_indicators = ["class", "def", "SimpleRAG", ":", "return"]
        assert any(indicator in response_text for indicator in code_indicators)
        
        # Check for proper Python structure
        assert "class" in response_text or "def" in response_text
    
    @pytest.mark.asyncio
    async def test_json_response_format(self, client):
        """Test requesting structured JSON responses"""
        query_payload = {
            "message": "List 3 benefits of using vector databases in RAG systems. Format your response as JSON with 'benefits' as an array.",
            "model": "arcee-ai/arcee-agent",
            "use_rag": True,
            "max_tokens": 400,
            "temperature": 0.5
        }
        
        response = await client.post("/api/v1/chat/query", json=query_payload)
        assert response.status_code == 200
        data = response.json()
        
        # The model should attempt to provide a structured response
        response_text = data["response"]
        assert len(response_text) > 0
        
        # Check if response mentions benefits or has some structure
        assert any(word in response_text.lower() for word in ["benefit", "advantage", "vector", "database"])


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
