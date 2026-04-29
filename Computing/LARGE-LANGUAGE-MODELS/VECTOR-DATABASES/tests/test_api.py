"""
API endpoint tests
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["status"] == "online"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "vector_db" in data
    assert "llm" in data


def test_ingest_document():
    """Test document ingestion"""
    document = {
        "text": "This is a test document about vector databases. They are useful for similarity search.",
        "metadata": {
            "source": "test",
            "category": "documentation"
        }
    }
    
    response = client.post("/api/documents/ingest", json=document)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["status"] == "ingested"
    assert data["chunks"] > 0


def test_vector_search():
    """Test vector search"""
    # First ingest a document
    document = {
        "text": "Vector databases enable semantic search using embeddings.",
        "metadata": {"source": "test"}
    }
    client.post("/api/documents/ingest", json=document)
    
    # Then search
    search_request = {
        "query": "What are vector databases?",
        "top_k": 5
    }
    
    response = client.post("/api/search", json=search_request)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "query_time_ms" in data


def test_embedding_generation():
    """Test embedding generation"""
    request = {
        "text": "Generate embedding for this text"
    }
    
    response = client.post("/api/embeddings/generate", json=request)
    assert response.status_code == 200
    data = response.json()
    assert "embedding" in data
    assert "dimensions" in data
    assert len(data["embedding"]) == data["dimensions"]


def test_agent_query():
    """Test AI agent query"""
    # Ingest some knowledge first
    document = {
        "text": "FastAPI is a modern Python web framework for building APIs.",
        "metadata": {"topic": "fastapi"}
    }
    client.post("/api/documents/ingest", json=document)
    
    # Query the agent
    query_request = {
        "query": "What is FastAPI?",
        "use_rag": True,
        "top_k": 3
    }
    
    response = client.post("/api/agent/query", json=query_request)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "sources" in data
    assert "model" in data


def test_agent_chat():
    """Test agent chat with session"""
    message1 = {
        "message": "My name is Alice",
        "session_id": "test_session_123"
    }
    
    response1 = client.post("/api/agent/chat", json=message1)
    assert response1.status_code == 200
    
    # Second message in same session
    message2 = {
        "message": "What is my name?",
        "session_id": "test_session_123"
    }
    
    response2 = client.post("/api/agent/chat", json=message2)
    assert response2.status_code == 200
    data = response2.json()
    assert "response" in data
    assert data["session_id"] == "test_session_123"


def test_knowledge_upload():
    """Test knowledge base upload"""
    knowledge = {
        "documents": [
            {"text": "Python is a programming language"},
            {"text": "JavaScript is used for web development"}
        ],
        "collection": "test_collection"
    }
    
    response = client.post("/api/agent/knowledge", json=knowledge)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["documents_added"] == 2
