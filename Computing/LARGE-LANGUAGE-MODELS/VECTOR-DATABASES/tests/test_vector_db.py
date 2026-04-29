"""
Vector database service tests
"""
import pytest
from app.services.vector_db import VectorDBService
from app.services.embedding import EmbeddingService
from app.config import settings


@pytest.fixture
def embedding_service():
    """Create embedding service fixture"""
    return EmbeddingService()


@pytest.fixture
def vector_db_service():
    """Create vector DB service fixture"""
    return VectorDBService()


def test_embedding_generation(embedding_service):
    """Test embedding generation"""
    text = "This is a test sentence"
    embedding = embedding_service.generate_embedding(text)
    
    assert isinstance(embedding, list)
    assert len(embedding) > 0
    assert all(isinstance(x, float) for x in embedding)
    assert len(embedding) == embedding_service.get_dimension()


def test_batch_embedding_generation(embedding_service):
    """Test batch embedding generation"""
    texts = [
        "First sentence",
        "Second sentence",
        "Third sentence"
    ]
    
    embeddings = embedding_service.generate_embeddings(texts)
    
    assert len(embeddings) == len(texts)
    assert all(len(emb) == embedding_service.get_dimension() for emb in embeddings)


def test_vector_db_add_and_search(vector_db_service, embedding_service):
    """Test adding documents and searching"""
    # Prepare test data
    texts = [
        "Vector databases are great for similarity search",
        "Machine learning models use embeddings",
        "Python is a popular programming language"
    ]
    
    embeddings = embedding_service.generate_embeddings(texts)
    ids = [f"test_{i}" for i in range(len(texts))]
    metadatas = [{"index": i} for i in range(len(texts))]
    
    # Add documents
    vector_db_service.add_documents(
        collection="test",
        ids=ids,
        embeddings=embeddings,
        texts=texts,
        metadatas=metadatas
    )
    
    # Search
    query = "database search"
    query_embedding = embedding_service.generate_embedding(query)
    results = vector_db_service.search("test", query_embedding, top_k=2)
    
    assert len(results) <= 2
    assert all("id" in r for r in results)
    assert all("score" in r for r in results)
    assert all("text" in r for r in results)


def test_vector_db_status(vector_db_service):
    """Test getting vector DB status"""
    status = vector_db_service.get_status()
    
    assert "status" in status
    assert "database" in status
    assert status["status"] == "connected"
