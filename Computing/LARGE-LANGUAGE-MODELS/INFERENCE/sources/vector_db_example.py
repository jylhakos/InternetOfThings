#!/usr/bin/env python3
"""
Vector Database Example
Demonstrates vector database operations for LLM applications.
"""

import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import time


@dataclass
class VectorRecord:
    """Represents a vector record in the database"""
    id: str
    vector: np.ndarray
    metadata: Dict[str, Any]
    created_at: float = field(default_factory=time.time)


class SimpleVectorDB:
    """
    Simple vector database implementation for demonstration.
    
    In production, use:
    - Pinecone: https://www.pinecone.io/
    - Weaviate: https://weaviate.io/
    - Chroma: https://www.trychroma.com/
    - Milvus: https://milvus.io/
    - Qdrant: https://qdrant.tech/
    - FAISS: https://github.com/facebookresearch/faiss
    """
    
    def __init__(self, dimension: int = 384, index_type: str = "flat"):
        """
        Initialize vector database.
        
        Args:
            dimension: Vector dimensionality
            index_type: Index type ('flat', 'hnsw', 'ivf') - only 'flat' implemented
        """
        self.dimension = dimension
        self.index_type = index_type
        self.records: List[VectorRecord] = []
        self.id_to_index: Dict[str, int] = {}
        
        print(f"✓ Initialized VectorDB (dim={dimension}, index={index_type})")
    
    def insert(
        self, 
        id: str, 
        vector: np.ndarray, 
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Insert a vector into the database.
        
        Args:
            id: Unique identifier
            vector: Vector embedding
            metadata: Associated metadata
            
        Returns:
            Success status
        """
        if len(vector) != self.dimension:
            raise ValueError(
                f"Vector dimension {len(vector)} doesn't match DB dimension {self.dimension}"
            )
        
        # Check if ID already exists
        if id in self.id_to_index:
            raise ValueError(f"Record with ID '{id}' already exists")
        
        # Create record
        record = VectorRecord(
            id=id,
            vector=vector,
            metadata=metadata or {}
        )
        
        # Add to storage
        self.id_to_index[id] = len(self.records)
        self.records.append(record)
        
        return True
    
    def insert_many(self, records: List[tuple]) -> int:
        """
        Batch insert multiple vectors.
        
        Args:
            records: List of (id, vector, metadata) tuples
            
        Returns:
            Number of records inserted
        """
        inserted = 0
        for id, vector, metadata in records:
            try:
                self.insert(id, vector, metadata)
                inserted += 1
            except ValueError as e:
                print(f"  ⚠ Skipped {id}: {e}")
        
        return inserted
    
    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 10,
        filter_fn: Optional[callable] = None
    ) -> List[tuple[str, float, Dict[str, Any]]]:
        """
        Search for similar vectors using cosine similarity.
        
        Args:
            query_vector: Query embedding
            top_k: Number of results
            filter_fn: Optional filter function on metadata
            
        Returns:
            List of (id, score, metadata) tuples
        """
        if len(query_vector) != self.dimension:
            raise ValueError("Query vector dimension mismatch")
        
        # Normalize query vector
        query_norm = query_vector / (np.linalg.norm(query_vector) + 1e-8)
        
        results = []
        
        for record in self.records:
            # Apply filter if provided
            if filter_fn and not filter_fn(record.metadata):
                continue
            
            # Compute cosine similarity
            vector_norm = record.vector / (np.linalg.norm(record.vector) + 1e-8)
            similarity = float(np.dot(query_norm, vector_norm))
            
            results.append((record.id, similarity, record.metadata))
        
        # Sort by similarity (descending)
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:top_k]
    
    def get(self, id: str) -> Optional[VectorRecord]:
        """Get record by ID"""
        idx = self.id_to_index.get(id)
        if idx is not None:
            return self.records[idx]
        return None
    
    def delete(self, id: str) -> bool:
        """Delete record by ID"""
        idx = self.id_to_index.get(id)
        if idx is None:
            return False
        
        # Remove from index
        del self.id_to_index[id]
        
        # Mark as deleted (in production, you'd rebuild index)
        self.records[idx] = None
        
        return True
    
    def update_metadata(self, id: str, metadata: Dict[str, Any]) -> bool:
        """Update metadata for a record"""
        record = self.get(id)
        if record:
            record.metadata.update(metadata)
            return True
        return False
    
    def stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        active_records = sum(1 for r in self.records if r is not None)
        
        return {
            "total_records": len(self.records),
            "active_records": active_records,
            "deleted_records": len(self.records) - active_records,
            "dimension": self.dimension,
            "index_type": self.index_type
        }


def generate_random_embedding(dimension: int = 384, seed: Optional[int] = None) -> np.ndarray:
    """Generate a random normalized embedding"""
    if seed is not None:
        np.random.seed(seed)
    vector = np.random.randn(dimension)
    return vector / np.linalg.norm(vector)


def example_basic_operations():
    """Example: Basic CRUD operations"""
    print("\n" + "=" * 80)
    print("  BASIC VECTOR DATABASE OPERATIONS")
    print("=" * 80 + "\n")
    
    # Initialize DB
    db = SimpleVectorDB(dimension=384)
    
    # 1. Insert single record
    print("1. Inserting single record...")
    vector1 = generate_random_embedding(384, seed=42)
    db.insert("doc_1", vector1, {"title": "Introduction to AI", "category": "AI"})
    print("   ✓ Inserted doc_1\n")
    
    # 2. Batch insert
    print("2. Batch inserting records...")
    records = [
        ("doc_2", generate_random_embedding(384, seed=43), {"title": "Machine Learning Basics", "category": "ML"}),
        ("doc_3", generate_random_embedding(384, seed=44), {"title": "Deep Learning Guide", "category": "DL"}),
        ("doc_4", generate_random_embedding(384, seed=45), {"title": "Natural Language Processing", "category": "NLP"}),
    ]
    inserted = db.insert_many(records)
    print(f"   ✓ Inserted {inserted} records\n")
    
    # 3. Get record
    print("3. Retrieving record...")
    record = db.get("doc_2")
    if record:
        print(f"   ✓ Found: {record.metadata['title']}")
        print(f"     Vector shape: {record.vector.shape}")
        print(f"     Created at: {time.ctime(record.created_at)}\n")
    
    # 4. Update metadata
    print("4. Updating metadata...")
    db.update_metadata("doc_1", {"views": 100, "updated": True})
    updated_record = db.get("doc_1")
    print(f"   ✓ Updated metadata: {updated_record.metadata}\n")
    
    # 5. Database stats
    print("5. Database statistics:")
    stats = db.stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")


def example_similarity_search():
    """Example: Similarity search"""
    print("\n" + "=" * 80)
    print("  SIMILARITY SEARCH")
    print("=" * 80 + "\n")
    
    db = SimpleVectorDB(dimension=384)
    
    # Insert documents about different topics
    print("Inserting documents...\n")
    documents = [
        ("ai_1", 100, {"title": "Introduction to AI", "category": "AI", "year": 2023}),
        ("ai_2", 101, {"title": "AI Applications", "category": "AI", "year": 2024}),
        ("ml_1", 200, {"title": "Machine Learning Fundamentals", "category": "ML", "year": 2023}),
        ("ml_2", 201, {"title": "Advanced ML Techniques", "category": "ML", "year": 2024}),
        ("dl_1", 300, {"title": "Deep Learning with PyTorch", "category": "DL", "year": 2023}),
        ("nl_1", 400, {"title": "NLP with Transformers", "category": "NLP", "year": 2024}),
    ]
    
    for doc_id, seed, metadata in documents:
        vector = generate_random_embedding(384, seed=seed)
        db.insert(doc_id, vector, metadata)
        print(f"  ✓ {metadata['title']}")
    
    # Search with query
    print("\n" + "─" * 80)
    print("Query: 'artificial intelligence concepts'")
    print("─" * 80 + "\n")
    
    query_vector = generate_random_embedding(384, seed=100)
    results = db.search(query_vector, top_k=3)
    
    print("Top 3 Results:\n")
    for i, (doc_id, score, metadata) in enumerate(results, 1):
        print(f"  {i}. {metadata['title']}")
        print(f"     ID: {doc_id}")
        print(f"     Similarity: {score:.4f}")
        print(f"     Category: {metadata['category']}")
        print(f"     Year: {metadata['year']}\n")


def example_filtered_search():
    """Example: Filtered similarity search"""
    print("\n" + "=" * 80)
    print("  FILTERED SIMILARITY SEARCH")
    print("=" * 80 + "\n")
    
    db = SimpleVectorDB(dimension=384)
    
    # Insert documents
    documents = [
        ("tech_1", 500, {"topic": "AI", "language": "Python", "level": "beginner"}),
        ("tech_2", 501, {"topic": "AI", "language": "JavaScript", "level": "intermediate"}),
        ("tech_3", 502, {"topic": "Web", "language": "Python", "level": "advanced"}),
        ("tech_4", 503, {"topic": "AI", "language": "Python", "level": "advanced"}),
        ("tech_5", 504, {"topic": "Mobile", "language": "Swift", "level": "beginner"}),
    ]
    
    for doc_id, seed, metadata in documents:
        vector = generate_random_embedding(384, seed=seed)
        db.insert(doc_id, vector, metadata)
    
    # Search with filter
    print("Query: 'machine learning tutorials'")
    print("Filter: topic='AI' AND language='Python'\n")
    
    query_vector = generate_random_embedding(384, seed=600)
    
    # Define filter function
    def filter_fn(metadata):
        return metadata.get("topic") == "AI" and metadata.get("language") == "Python"
    
    results = db.search(query_vector, top_k=5, filter_fn=filter_fn)
    
    print(f"Found {len(results)} matching results:\n")
    for i, (doc_id, score, metadata) in enumerate(results, 1):
        print(f"  {i}. {doc_id}")
        print(f"     Similarity: {score:.4f}")
        print(f"     Metadata: {metadata}\n")


def example_hybrid_search():
    """Example: Hybrid search (semantic + metadata)"""
    print("\n" + "=" * 80)
    print("  HYBRID SEARCH (Semantic + Metadata)")
    print("=" * 80 + "\n")
    
    db = SimpleVectorDB(dimension=384)
    
    # Insert blog posts
    print("Inserting blog posts...\n")
    posts = [
        ("post_1", 700, {"title": "Getting Started with AI", "tags": ["AI", "beginner"], "upvotes": 150}),
        ("post_2", 701, {"title": "Advanced Neural Networks", "tags": ["AI", "advanced"], "upvotes": 200}),
        ("post_3", 702, {"title": "Web Development Tips", "tags": ["Web", "tips"], "upvotes": 50}),
        ("post_4", 703, {"title": "AI in Production", "tags": ["AI", "production"], "upvotes": 300}),
        ("post_5", 704, {"title": "Beginner's Guide to Python", "tags": ["Python", "beginner"], "upvotes": 100}),
    ]
    
    for post_id, seed, metadata in posts:
        vector = generate_random_embedding(384, seed=seed)
        db.insert(post_id, vector, metadata)
    
    # Hybrid search: semantic similarity + metadata boost
    print("Query: 'artificial intelligence tutorials'")
    print("Boost: Posts with upvotes > 100\n")
    
    query_vector = generate_random_embedding(384, seed=800)
    
    # Get initial results
    results = db.search(query_vector, top_k=5)
    
    # Apply metadata-based re-ranking
    reranked_results = []
    for doc_id, score, metadata in results:
        # Boost score based on upvotes
        upvotes = metadata.get("upvotes", 0)
        boost = 1.0 + (upvotes / 1000.0)  # Up to 20% boost for 200 upvotes
        boosted_score = score * boost
        
        reranked_results.append((doc_id, score, boosted_score, metadata))
    
    # Sort by boosted score
    reranked_results.sort(key=lambda x: x[2], reverse=True)
    
    print("Results (with metadata boosting):\n")
    for i, (doc_id, orig_score, boosted_score, metadata) in enumerate(reranked_results, 1):
        print(f"  {i}. {metadata['title']}")
        print(f"     Original Score: {orig_score:.4f}")
        print(f"     Boosted Score: {boosted_score:.4f}")
        print(f"     Upvotes: {metadata['upvotes']}")
        print(f"     Tags: {metadata['tags']}\n")


def example_performance_benchmark():
    """Example: Performance benchmarking"""
    print("\n" + "=" * 80)
    print("  PERFORMANCE BENCHMARK")
    print("=" * 80 + "\n")
    
    dimensions = [128, 384, 768]
    num_records = 1000
    num_queries = 10
    
    for dim in dimensions:
        print(f"Dimension: {dim}")
        print("─" * 40)
        
        # Initialize DB
        db = SimpleVectorDB(dimension=dim)
        
        # Benchmark insertion
        start_time = time.time()
        records = [
            (f"doc_{i}", generate_random_embedding(dim, seed=i), {"index": i})
            for i in range(num_records)
        ]
        db.insert_many(records)
        insert_time = time.time() - start_time
        
        print(f"  Insertion: {num_records} records in {insert_time:.3f}s")
        print(f"  Rate: {num_records/insert_time:.0f} insertions/sec")
        
        # Benchmark search
        start_time = time.time()
        for i in range(num_queries):
            query_vector = generate_random_embedding(dim, seed=1000+i)
            db.search(query_vector, top_k=10)
        search_time = time.time() - start_time
        
        print(f"  Search: {num_queries} queries in {search_time:.3f}s")
        print(f"  Rate: {num_queries/search_time:.1f} queries/sec")
        print(f"  Avg latency: {(search_time/num_queries)*1000:.1f}ms\n")


def example_vector_db_comparison():
    """Example: Compare different vector DB features"""
    print("\n" + "=" * 80)
    print("  VECTOR DATABASE COMPARISON")
    print("=" * 80 + "\n")
    
    comparison = {
        "Pinecone": {
            "Type": "Managed Cloud",
            "Open Source": "No",
            "Scalability": "Excellent",
            "Ease of Use": "Very Easy",
            "Performance": "Excellent",
            "Best For": "Production apps, high scale"
        },
        "Weaviate": {
            "Type": "Self-hosted/Cloud",
            "Open Source": "Yes",
            "Scalability": "Excellent",
            "Ease of Use": "Moderate",
            "Performance": "Excellent",
            "Best For": "Hybrid search, semantic apps"
        },
        "Chroma": {
            "Type": "Embedded/Self-hosted",
            "Open Source": "Yes",
            "Scalability": "Good",
            "Ease of Use": "Very Easy",
            "Performance": "Good",
            "Best For": "Development, prototypes"
        },
        "Milvus": {
            "Type": "Self-hosted/Cloud",
            "Open Source": "Yes",
            "Scalability": "Excellent",
            "Ease of Use": "Moderate",
            "Performance": "Excellent",
            "Best For": "Large-scale deployments"
        },
        "Qdrant": {
            "Type": "Self-hosted/Cloud",
            "Open Source": "Yes",
            "Scalability": "Excellent",
            "Ease of Use": "Easy",
            "Performance": "Excellent",
            "Best For": "High-performance retrieval"
        },
        "FAISS": {
            "Type": "Library",
            "Open Source": "Yes",
            "Scalability": "Good",
            "Ease of Use": "Moderate",
            "Performance": "Excellent",
            "Best For": "Research, custom solutions"
        }
    }
    
    for db_name, features in comparison.items():
        print(f"📦 {db_name}")
        for feature, value in features.items():
            print(f"   {feature:15s}: {value}")
        print()


def main():
    """Run all vector database examples"""
    print("\n" + "★" * 80)
    print("  VECTOR DATABASE EXAMPLES")
    print("★" * 80)
    
    example_basic_operations()
    example_similarity_search()
    example_filtered_search()
    example_hybrid_search()
    example_performance_benchmark()
    example_vector_db_comparison()
    
    print("\n" + "★" * 80)
    print("  All vector database examples completed!")
    print("★" * 80 + "\n")
    
    print("💡 Production Recommendations:")
    print("  1. For prototyping: Use Chroma (easy setup)")
    print("  2. For production: Use Pinecone (managed, scalable)")
    print("  3. For hybrid search: Use Weaviate (semantic + keyword)")
    print("  4. For high performance: Use Qdrant (fast, efficient)")
    print("  5. For research: Use FAISS (flexible, powerful)")
    print()


if __name__ == "__main__":
    main()
