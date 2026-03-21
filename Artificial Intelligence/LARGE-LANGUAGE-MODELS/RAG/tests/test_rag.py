"""
Unit tests for RAG pipeline components.

These tests verify document loading, indexing, and query functionality.
Run with: pytest tests/test_rag.py -v
"""

import pytest
from pathlib import Path
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader


class TestDocumentLoading:
    """Test document loading functionality."""
    
    def test_data_directory_exists(self, data_dir):
        """Test that the data directory exists."""
        assert Path(data_dir).exists(), f"Data directory not found: {data_dir}"
    
    def test_load_documents_success(self, data_dir):
        """Test that documents can be loaded successfully."""
        documents = SimpleDirectoryReader(data_dir).load_data()
        
        assert len(documents) > 0, "No documents were loaded"
        assert hasattr(documents[0], 'text'), "Document missing 'text' attribute"
        assert hasattr(documents[0], 'metadata'), "Document missing 'metadata' attribute"
    
    def test_document_content_not_empty(self, sample_documents):
        """Test that loaded documents have content."""
        for doc in sample_documents:
            assert len(doc.text) > 0, "Document has empty text"
            assert isinstance(doc.text, str), "Document text is not a string"


class TestIndexCreation:
    """Test vector index creation."""
    
    def test_create_index_from_documents(self, sample_documents):
        """Test that a vector index can be created from documents."""
        index = VectorStoreIndex.from_documents(sample_documents)
        
        assert index is not None, "Index creation returned None"
        assert hasattr(index, 'as_query_engine'), "Index missing query engine method"
    
    def test_index_has_storage_context(self, sample_documents):
        """Test that the index has a storage context."""
        index = VectorStoreIndex.from_documents(sample_documents)
        
        assert hasattr(index, 'storage_context'), "Index missing storage context"
        assert index.storage_context is not None


class TestQueryEngine:
    """Test query engine functionality."""
    
    @pytest.fixture
    def query_engine(self, sample_documents):
        """Create a query engine for testing."""
        index = VectorStoreIndex.from_documents(sample_documents)
        return index.as_query_engine()
    
    def test_query_engine_creation(self, query_engine):
        """Test that query engine can be created."""
        assert query_engine is not None
        assert hasattr(query_engine, 'query'), "Query engine missing 'query' method"
    
    def test_basic_query(self, query_engine):
        """Test a basic query returns a response."""
        response = query_engine.query("What is LlamaIndex?")
        
        assert response is not None, "Query returned None"
        assert len(str(response)) > 0, "Response is empty"
        assert hasattr(response, 'response'), "Response missing 'response' attribute"
    
    def test_query_with_different_inputs(self, query_engine):
        """Test queries with various inputs."""
        queries = [
            "What is RAG?",
            "How does LlamaIndex work?",
            "What are agents?",
        ]
        
        for query in queries:
            response = query_engine.query(query)
            assert response is not None, f"Query '{query}' returned None"
            assert len(str(response)) > 0, f"Query '{query}' returned empty response"


class TestRAGPipeline:
    """Test the complete RAG pipeline."""
    
    def test_end_to_end_rag(self, data_dir):
        """Test complete RAG pipeline from loading to querying."""
        # Load documents
        documents = SimpleDirectoryReader(data_dir).load_data()
        assert len(documents) > 0
        
        # Create index
        index = VectorStoreIndex.from_documents(documents)
        assert index is not None
        
        # Create query engine
        query_engine = index.as_query_engine()
        assert query_engine is not None
        
        # Execute query
        response = query_engine.query("What is the main topic of these documents?")
        assert response is not None
        assert len(str(response)) > 0


@pytest.mark.integration
class TestRAGModule:
    """Integration tests for the rag_pipeline module."""
    
    def test_load_documents_function(self, data_dir):
        """Test the load_documents function from rag_pipeline."""
        from src.rag_pipeline import load_documents
        
        documents = load_documents(data_dir)
        assert len(documents) > 0
    
    def test_create_vector_index_function(self, sample_documents, mock_openai_api_key):
        """Test the create_vector_index function."""
        from src.rag_pipeline import create_vector_index
        
        # This test may fail without valid API key
        pytest.skip("Requires valid OpenAI API key")
        
        index = create_vector_index(sample_documents)
        assert index is not None
    
    def test_create_rag_query_engine_function(self, data_dir, mock_openai_api_key):
        """Test the create_rag_query_engine function."""
        from src.rag_pipeline import create_rag_query_engine
        
        # This test may fail without valid API key
        pytest.skip("Requires valid OpenAI API key")
        
        query_engine = create_rag_query_engine(data_dir)
        assert query_engine is not None


if __name__ == "__main__":
    # Run tests with: python -m pytest tests/test_rag.py -v
    pytest.main([__file__, "-v"])
