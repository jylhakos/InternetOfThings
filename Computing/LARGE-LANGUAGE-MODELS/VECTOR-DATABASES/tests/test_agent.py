"""
AI Agent service tests
"""
import pytest
from app.services.agent import AgentService, AgentMemory
from app.services.vector_db import VectorDBService
from app.services.embedding import EmbeddingService
from app.services.llm import LLMService


@pytest.fixture
def agent_service():
    """Create agent service fixture"""
    vector_db = VectorDBService()
    embedding = EmbeddingService()
    llm = LLMService()
    return AgentService(vector_db, embedding, llm)


def test_agent_memory():
    """Test agent memory functionality"""
    memory = AgentMemory()
    session_id = "test_session"
    
    # Create session
    memory.create_session(session_id)
    assert session_id in memory.sessions
    
    # Add messages
    memory.add_message(session_id, "user", "Hello")
    memory.add_message(session_id, "assistant", "Hi there!")
    
    # Retrieve history
    history = memory.get_session_history(session_id)
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"


def test_agent_query_without_rag(agent_service):
    """Test agent query without RAG"""
    result = agent_service.query(
        query="What is 2+2?",
        use_rag=False
    )
    
    assert "query" in result
    assert "response" in result
    assert "sources" in result
    assert len(result["sources"]) == 0
    assert result["context_retrieved"] is False


def test_agent_query_with_rag(agent_service):
    """Test agent query with RAG"""
    # First upload some knowledge
    documents = [
        {"text": "The capital of France is Paris"},
        {"text": "Python was created by Guido van Rossum"}
    ]
    
    agent_service.upload_knowledge(documents, collection="default")
    
    # Query with RAG
    result = agent_service.query(
        query="What is the capital of France?",
        use_rag=True,
        top_k=2,
        collection="default"
    )
    
    assert "query" in result
    assert "response" in result
    assert "sources" in result


def test_agent_chat(agent_service):
    """Test agent chat functionality"""
    session_id = "test_chat_session"
    
    # First message
    result1 = agent_service.chat(
        message="Hello, I'm testing the chat",
        session_id=session_id
    )
    
    assert "response" in result1
    assert result1["session_id"] == session_id
    
    # Second message
    result2 = agent_service.chat(
        message="Can you remember our conversation?",
        session_id=session_id
    )
    
    assert "response" in result2
    assert result2["context_retrieved"] is True


def test_knowledge_upload(agent_service):
    """Test knowledge base upload"""
    documents = [
        {"text": "FastAPI is a modern web framework", "metadata": {"topic": "web"}},
        {"text": "Vector databases store embeddings", "metadata": {"topic": "database"}}
    ]
    
    result = agent_service.upload_knowledge(documents, collection="test_knowledge")
    
    assert result["status"] == "success"
    assert result["documents_added"] == 2
    assert result["collection"] == "test_knowledge"
