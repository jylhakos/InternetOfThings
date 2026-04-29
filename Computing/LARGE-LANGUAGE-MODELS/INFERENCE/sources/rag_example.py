#!/usr/bin/env python3
"""
RAG (Retrieval-Augmented Generation) Example
Demonstrates how to implement RAG with LLM inference.
"""

import numpy as np
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import json


@dataclass
class Document:
    """Represents a document in the knowledge base"""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: np.ndarray = None


class SimpleEmbeddingModel:
    """
    Simple embedding model for demonstration.
    In production, use:
    - sentence-transformers
    - OpenAI embeddings
    - Cohere embeddings
    """
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
    
    def embed(self, text: str) -> np.ndarray:
        """
        Generate embedding for text.
        In production, this would use an actual embedding model.
        """
        # Simple hash-based embedding for demo
        np.random.seed(hash(text) % (2**32))
        embedding = np.random.randn(self.dimension)
        # Normalize
        embedding = embedding / np.linalg.norm(embedding)
        return embedding
    
    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for multiple texts"""
        return [self.embed(text) for text in texts]


class VectorStore:
    """
    Simple in-memory vector store.
    In production, use:
    - Pinecone
    - Weaviate
    - Chroma
    - Milvus
    - Qdrant
    """
    
    def __init__(self, embedding_model: SimpleEmbeddingModel):
        self.embedding_model = embedding_model
        self.documents: List[Document] = []
    
    def add_document(self, doc_id: str, content: str, metadata: Dict[str, Any] = None):
        """Add a document to the vector store"""
        embedding = self.embedding_model.embed(content)
        doc = Document(
            id=doc_id,
            content=content,
            metadata=metadata or {},
            embedding=embedding
        )
        self.documents.append(doc)
    
    def add_documents(self, documents: List[Tuple[str, str, Dict[str, Any]]]):
        """Add multiple documents"""
        for doc_id, content, metadata in documents:
            self.add_document(doc_id, content, metadata)
    
    def similarity_search(
        self, 
        query: str, 
        top_k: int = 3,
        filter_metadata: Dict[str, Any] = None
    ) -> List[Tuple[Document, float]]:
        """
        Search for similar documents using cosine similarity.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of (Document, similarity_score) tuples
        """
        query_embedding = self.embedding_model.embed(query)
        
        # Calculate similarities
        results = []
        for doc in self.documents:
            # Apply metadata filter if provided
            if filter_metadata:
                if not all(
                    doc.metadata.get(k) == v 
                    for k, v in filter_metadata.items()
                ):
                    continue
            
            # Cosine similarity
            similarity = np.dot(query_embedding, doc.embedding)
            results.append((doc, float(similarity)))
        
        # Sort by similarity (descending)
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:top_k]


class RAGSystem:
    """
    RAG (Retrieval-Augmented Generation) System.
    Combines retrieval from vector store with LLM generation.
    """
    
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Document]:
        """Retrieve relevant documents for query"""
        results = self.vector_store.similarity_search(query, top_k=top_k)
        return [doc for doc, score in results]
    
    def create_prompt(self, query: str, documents: List[Document]) -> str:
        """
        Create augmented prompt with retrieved context.
        
        This is a key part of RAG - injecting relevant context into the prompt.
        """
        context = "\n\n".join([
            f"Document {i+1}:\n{doc.content}"
            for i, doc in enumerate(documents)
        ])
        
        prompt = f"""You are a helpful assistant. Answer the question based on the provided context.

Context:
{context}

Question: {query}

Answer: Let me answer based on the provided context."""
        
        return prompt
    
    def query(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Execute RAG query: retrieve + generate.
        
        Args:
            query: User question
            top_k: Number of documents to retrieve
            
        Returns:
            Dictionary with prompt, retrieved docs, and metadata
        """
        # 1. Retrieve relevant documents
        retrieved_docs = self.retrieve(query, top_k=top_k)
        
        # 2. Create augmented prompt
        augmented_prompt = self.create_prompt(query, retrieved_docs)
        
        # 3. Return prompt for LLM inference
        # In production, you would call the LLM here
        return {
            "query": query,
            "retrieved_documents": [
                {
                    "id": doc.id,
                    "content": doc.content,
                    "metadata": doc.metadata
                }
                for doc in retrieved_docs
            ],
            "augmented_prompt": augmented_prompt,
            "num_retrieved": len(retrieved_docs)
        }


def create_sample_knowledge_base() -> List[Tuple[str, str, Dict[str, Any]]]:
    """Create sample documents for demonstration"""
    documents = [
        (
            "doc_1",
            "Large Language Models (LLMs) are neural networks with billions of parameters. "
            "They are trained on vast amounts of text data to understand and generate human-like text. "
            "Popular examples include GPT-4, Claude, and Llama.",
            {"category": "AI", "topic": "LLMs", "date": "2024-01-01"}
        ),
        (
            "doc_2",
            "Inference in machine learning is the process of using a trained model to make predictions "
            "on new data. During inference, the model applies learned patterns to generate outputs. "
            "Inference is computationally cheaper than training but still requires significant resources for large models.",
            {"category": "AI", "topic": "Inference", "date": "2024-01-15"}
        ),
        (
            "doc_3",
            "Vector databases store high-dimensional embeddings for efficient similarity search. "
            "They use algorithms like approximate nearest neighbors (ANN) to quickly find similar vectors. "
            "Popular vector databases include Pinecone, Weaviate, and Chroma.",
            {"category": "AI", "topic": "Vector Databases", "date": "2024-02-01"}
        ),
        (
            "doc_4",
            "Retrieval-Augmented Generation (RAG) combines retrieval systems with language models. "
            "It first retrieves relevant documents from a knowledge base, then uses them as context "
            "for the LLM to generate accurate, grounded responses. This reduces hallucinations.",
            {"category": "AI", "topic": "RAG", "date": "2024-02-15"}
        ),
        (
            "doc_5",
            "Transformers are the architecture behind modern LLMs. They use self-attention mechanisms "
            "to process sequences of data in parallel. The attention mechanism allows the model to "
            "focus on relevant parts of the input when generating outputs.",
            {"category": "AI", "topic": "Transformers", "date": "2024-03-01"}
        ),
        (
            "doc_6",
            "GPU acceleration is crucial for LLM inference. GPUs excel at parallel matrix operations "
            "which are fundamental to neural network computations. NVIDIA GPUs with CUDA support "
            "are commonly used for deploying LLMs in production.",
            {"category": "Hardware", "topic": "GPUs", "date": "2024-03-10"}
        ),
        (
            "doc_7",
            "Quantization reduces model size by using lower precision numbers. For example, converting "
            "32-bit floats to 8-bit integers. This decreases memory usage and speeds up inference "
            "with minimal impact on model quality. Techniques like AWQ and GPTQ are popular for LLMs.",
            {"category": "AI", "topic": "Optimization", "date": "2024-03-15"}
        ),
    ]
    return documents


def example_basic_rag():
    """Example: Basic RAG workflow"""
    print("\n" + "=" * 80)
    print("  BASIC RAG EXAMPLE")
    print("=" * 80 + "\n")
    
    # 1. Initialize components
    print("1. Initializing RAG system...")
    embedding_model = SimpleEmbeddingModel(dimension=384)
    vector_store = VectorStore(embedding_model)
    rag_system = RAGSystem(vector_store)
    
    # 2. Load knowledge base
    print("2. Loading knowledge base...")
    documents = create_sample_knowledge_base()
    vector_store.add_documents(documents)
    print(f"   ✓ Loaded {len(documents)} documents\n")
    
    # 3. Execute RAG queries
    queries = [
        "What are Large Language Models?",
        "How does retrieval-augmented generation work?",
        "Explain quantization for neural networks",
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'─' * 80}")
        print(f"Query {i}: {query}")
        print('─' * 80)
        
        result = rag_system.query(query, top_k=2)
        
        print(f"\n✓ Retrieved {result['num_retrieved']} relevant documents:\n")
        
        for j, doc in enumerate(result['retrieved_documents'], 1):
            print(f"  Document {j} (ID: {doc['id']}):")
            print(f"    Content: {doc['content'][:150]}...")
            print(f"    Metadata: {doc['metadata']}\n")
        
        print(f"✓ Augmented Prompt (first 300 chars):")
        print(f"  {result['augmented_prompt'][:300]}...\n")


def example_filtered_search():
    """Example: Search with metadata filtering"""
    print("\n" + "=" * 80)
    print("  FILTERED SEARCH EXAMPLE")
    print("=" * 80 + "\n")
    
    # Initialize
    embedding_model = SimpleEmbeddingModel(dimension=384)
    vector_store = VectorStore(embedding_model)
    
    # Load documents
    documents = create_sample_knowledge_base()
    vector_store.add_documents(documents)
    
    # Search with filter
    query = "Tell me about AI technologies"
    print(f"Query: {query}")
    print(f"Filter: category='AI'\n")
    
    results = vector_store.similarity_search(
        query, 
        top_k=3,
        filter_metadata={"category": "AI"}
    )
    
    print(f"✓ Found {len(results)} documents:\n")
    
    for i, (doc, score) in enumerate(results, 1):
        print(f"  {i}. Document {doc.id} (similarity: {score:.4f})")
        print(f"     Topic: {doc.metadata.get('topic')}")
        print(f"     Content: {doc.content[:100]}...\n")


def example_rag_with_inference():
    """Example: RAG + Inference (simulated)"""
    print("\n" + "=" * 80)
    print("  RAG + INFERENCE EXAMPLE")
    print("=" * 80 + "\n")
    
    # Initialize RAG
    embedding_model = SimpleEmbeddingModel(dimension=384)
    vector_store = VectorStore(embedding_model)
    rag_system = RAGSystem(vector_store)
    
    # Load documents
    documents = create_sample_knowledge_base()
    vector_store.add_documents(documents)
    
    # User query
    query = "What is the benefit of using RAG with LLMs?"
    print(f"User Query: {query}\n")
    
    # RAG retrieval
    print("Step 1: Retrieving relevant context...")
    result = rag_system.query(query, top_k=2)
    
    print(f"✓ Retrieved {result['num_retrieved']} documents\n")
    
    # Simulated inference
    print("Step 2: Sending to LLM for inference...")
    print(f"✓ Augmented prompt prepared ({len(result['augmented_prompt'])} chars)\n")
    
    # Simulate LLM response
    print("Step 3: LLM generates response:\n")
    simulated_response = (
        "Based on the provided context, Retrieval-Augmented Generation (RAG) "
        "combines retrieval systems with language models to improve response accuracy. "
        "The main benefit is that RAG first retrieves relevant documents from a knowledge base, "
        "then uses them as context for the LLM to generate accurate, grounded responses. "
        "This significantly reduces hallucinations and ensures answers are based on factual information "
        "from the knowledge base rather than just the model's training data."
    )
    
    print(f"  {simulated_response}\n")
    
    print("✓ RAG workflow completed successfully!")
    print(f"  - Query processed")
    print(f"  - {result['num_retrieved']} documents retrieved")
    print(f"  - Context-aware response generated")


def example_similarity_scores():
    """Example: Understanding similarity scores"""
    print("\n" + "=" * 80)
    print("  SIMILARITY SCORES EXAMPLE")
    print("=" * 80 + "\n")
    
    embedding_model = SimpleEmbeddingModel(dimension=384)
    vector_store = VectorStore(embedding_model)
    
    # Load documents
    documents = create_sample_knowledge_base()
    vector_store.add_documents(documents)
    
    # Test different queries
    test_queries = [
        "What are neural networks?",
        "Explain transformer architecture",
        "How to optimize inference?",
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("Top 3 similar documents:\n")
        
        results = vector_store.similarity_search(query, top_k=3)
        
        for i, (doc, score) in enumerate(results, 1):
            print(f"  {i}. Score: {score:.4f} | Topic: {doc.metadata.get('topic', 'N/A')}")
            print(f"     {doc.content[:80]}...\n")


def main():
    """Run all RAG examples"""
    print("\n" + "★" * 80)
    print("  RAG (RETRIEVAL-AUGMENTED GENERATION) EXAMPLES")
    print("★" * 80)
    
    example_basic_rag()
    example_filtered_search()
    example_rag_with_inference()
    example_similarity_scores()
    
    print("\n" + "★" * 80)
    print("  All RAG examples completed!")
    print("★" * 80 + "\n")
    
    print("💡 Next Steps:")
    print("  1. Replace SimpleEmbeddingModel with sentence-transformers")
    print("  2. Use a real vector database (Pinecone, Chroma, etc.)")
    print("  3. Connect to actual LLM inference server")
    print("  4. Implement chunking for long documents")
    print("  5. Add hybrid search (semantic + keyword)")
    print()


if __name__ == "__main__":
    main()
