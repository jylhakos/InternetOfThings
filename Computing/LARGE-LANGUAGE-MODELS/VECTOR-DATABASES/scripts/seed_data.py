"""
Seed sample data into the vector database
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.vector_db import VectorDBService
from app.services.embedding import EmbeddingService
import uuid

def seed_data():
    """Seed sample documents into vector database"""
    
    print("Seeding sample data...")
    
    # Initialize services
    embedding_service = EmbeddingService()
    vector_db = VectorDBService()
    
    # Sample documents about vector databases
    documents = [
        {
            "text": "Vector databases are specialized databases designed to store and query high-dimensional vectors efficiently. They are essential for machine learning and AI applications.",
            "metadata": {"topic": "introduction", "source": "seed"}
        },
        {
            "text": "ChromaDB is an open-source embedding database that makes it easy to build LLM applications. It's designed for simplicity and ease of use.",
            "metadata": {"topic": "chroma", "source": "seed"}
        },
        {
            "text": "Qdrant is a vector search engine written in Rust. It offers high performance and supports advanced filtering capabilities.",
            "metadata": {"topic": "qdrant", "source": "seed"}
        },
        {
            "text": "Weaviate is an open-source vector database that supports both vector and hybrid search. It has built-in support for various ML models.",
            "metadata": {"topic": "weaviate", "source": "seed"}
        },
        {
            "text": "Milvus is a cloud-native vector database built for massive-scale vector similarity search. It can handle billions of vectors.",
            "metadata": {"topic": "milvus", "source": "seed"}
        },
        {
            "text": "RAG (Retrieval Augmented Generation) combines retrieval from vector databases with LLM generation to provide more accurate and contextual responses.",
            "metadata": {"topic": "rag", "source": "seed"}
        },
        {
            "text": "Embeddings are dense vector representations of data that capture semantic meaning. They enable similarity search in high-dimensional space.",
            "metadata": {"topic": "embeddings", "source": "seed"}
        },
        {
            "text": "AI agents use vector databases as long-term memory to store and retrieve information across different sessions.",
            "metadata": {"topic": "ai-agents", "source": "seed"}
        },
        {
            "text": "Semantic search uses vector embeddings to find results based on meaning rather than exact keyword matches.",
            "metadata": {"topic": "semantic-search", "source": "seed"}
        },
        {
            "text": "FastAPI is a modern Python web framework perfect for building API services with automatic documentation and validation.",
            "metadata": {"topic": "fastapi", "source": "seed"}
        }
    ]
    
    # Generate embeddings
    texts = [doc["text"] for doc in documents]
    metadatas = [doc["metadata"] for doc in documents]
    
    print(f"Generating embeddings for {len(texts)} documents...")
    embeddings = embedding_service.generate_embeddings(texts)
    
    # Generate IDs
    ids = [f"seed_{uuid.uuid4()}" for _ in texts]
    
    # Add to vector database
    print("Adding documents to vector database...")
    vector_db.add_documents(
        collection="default",
        ids=ids,
        embeddings=embeddings,
        texts=texts,
        metadatas=metadatas
    )
    
    print(f"✓ Successfully seeded {len(documents)} documents!")
    
    # Test search
    print("\nTesting search...")
    query = "What are vector databases?"
    query_embedding = embedding_service.generate_embedding(query)
    results = vector_db.search("default", query_embedding, top_k=3)
    
    print(f"\nQuery: '{query}'")
    print(f"Found {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Score: {result['score']:.3f}")
        print(f"   Text: {result['text'][:100]}...")
        print(f"   Topic: {result['metadata'].get('topic', 'N/A')}")
    
    print("\n✓ Seeding complete!")


if __name__ == "__main__":
    seed_data()
