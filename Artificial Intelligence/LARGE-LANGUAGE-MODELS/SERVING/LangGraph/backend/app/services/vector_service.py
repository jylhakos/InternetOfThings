from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
from loguru import logger
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

from app.core.config import settings
from app.models.schemas import DocumentChunk, VectorSearchRequest, VectorSearchResponse


class VectorService:
    """Service for vector database operations using Qdrant"""
    
    def __init__(self):
        self.client: Optional[QdrantClient] = None
        self.embedding_model: Optional[SentenceTransformer] = None
        self.collection_name = settings.COLLECTION_NAME
        self.vector_size = settings.VECTOR_SIZE
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def initialize(self):
        """Initialize Qdrant client and embedding model"""
        try:
            # Initialize Qdrant client
            self.client = QdrantClient(
                url=settings.QDRANT_URL,
                timeout=60
            )
            
            # Initialize embedding model
            await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._load_embedding_model
            )
            
            # Create collection if it doesn't exist
            await self.create_collection()
            
            logger.info("Vector service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector service: {e}")
            raise
    
    def _load_embedding_model(self):
        """Load embedding model (runs in thread pool)"""
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        logger.info(f"Loaded embedding model: {settings.EMBEDDING_MODEL}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if vector service is healthy"""
        try:
            if not self.client:
                return {"status": "unhealthy", "error": "Client not initialized"}
            
            # Check if collection exists and get info
            collection_info = self.client.get_collection(self.collection_name)
            
            return {
                "status": "healthy",
                "collection": self.collection_name,
                "points_count": collection_info.points_count,
                "vectors_count": collection_info.vectors_count,
                "embedding_model": settings.EMBEDDING_MODEL
            }
        except Exception as e:
            logger.error(f"Vector service health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    async def create_collection(self):
        """Create vector collection if it doesn't exist"""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.collection_name}")
            else:
                logger.info(f"Collection already exists: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            raise
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for text list"""
        if not self.embedding_model:
            raise Exception("Embedding model not initialized")
        
        try:
            embeddings = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self.embedding_model.encode,
                texts
            )
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    async def add_documents(
        self, 
        documents: List[DocumentChunk]
    ) -> bool:
        """Add documents to vector database"""
        try:
            if not documents:
                return True
            
            # Extract text content for embedding
            texts = [doc.content for doc in documents]
            
            # Generate embeddings
            embeddings = await self.generate_embeddings(texts)
            
            # Create points for Qdrant
            points = []
            for doc, embedding in zip(documents, embeddings):
                point = PointStruct(
                    id=doc.id if doc.id else str(uuid.uuid4()),
                    vector=embedding,
                    payload={
                        "content": doc.content,
                        "metadata": doc.metadata
                    }
                )
                points.append(point)
            
            # Upsert points to collection
            operation_info = self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"Added {len(points)} documents to vector database")
            return operation_info.status == models.UpdateStatus.COMPLETED
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return False
    
    async def search_documents(
        self, 
        query: str, 
        top_k: int = 5, 
        score_threshold: float = 0.7
    ) -> List[DocumentChunk]:
        """Search for similar documents"""
        start_time = time.time()
        
        try:
            # Generate query embedding
            query_embedding = await self.generate_embeddings([query])
            
            # Search in Qdrant
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding[0],
                limit=top_k,
                score_threshold=score_threshold,
                with_payload=True,
                with_vectors=False
            )
            
            # Convert results to DocumentChunk objects
            documents = []
            for result in search_results:
                chunk = DocumentChunk(
                    id=str(result.id),
                    content=result.payload["content"],
                    metadata=result.payload["metadata"],
                    score=result.score
                )
                documents.append(chunk)
            
            search_time = time.time() - start_time
            logger.info(f"Found {len(documents)} documents in {search_time:.3f}s")
            
            return documents
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document from vector database"""
        try:
            operation_info = self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=[document_id]
                )
            )
            
            logger.info(f"Deleted document: {document_id}")
            return operation_info.status == models.UpdateStatus.COMPLETED
            
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            return False
    
    async def delete_collection(self) -> bool:
        """Delete the entire collection"""
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            return False
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            
            return {
                "collection_name": self.collection_name,
                "points_count": collection_info.points_count,
                "vectors_count": collection_info.vectors_count,
                "segments_count": collection_info.segments_count,
                "config": {
                    "vector_size": self.vector_size,
                    "distance": "cosine"
                }
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {}
    
    async def vector_search(self, request: VectorSearchRequest) -> VectorSearchResponse:
        """Perform vector search with detailed response"""
        start_time = time.time()
        
        try:
            documents = await self.search_documents(
                query=request.query,
                top_k=request.top_k,
                score_threshold=request.score_threshold
            )
            
            search_time = time.time() - start_time
            
            return VectorSearchResponse(
                results=documents,
                total_found=len(documents),
                search_time=search_time
            )
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return VectorSearchResponse(
                results=[],
                total_found=0,
                search_time=0.0
            )
    
    async def similarity_search_with_metadata(
        self,
        query: str,
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[DocumentChunk]:
        """Search with metadata filtering"""
        try:
            query_embedding = await self.generate_embeddings([query])
            
            # Build filter if provided
            must_conditions = []
            if metadata_filter:
                for key, value in metadata_filter.items():
                    must_conditions.append(
                        models.FieldCondition(
                            key=f"metadata.{key}",
                            match=models.MatchValue(value=value)
                        )
                    )
            
            search_filter = None
            if must_conditions:
                search_filter = models.Filter(
                    must=must_conditions
                )
            
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding[0],
                query_filter=search_filter,
                limit=top_k,
                with_payload=True,
                with_vectors=False
            )
            
            documents = []
            for result in search_results:
                chunk = DocumentChunk(
                    id=str(result.id),
                    content=result.payload["content"],
                    metadata=result.payload["metadata"],
                    score=result.score
                )
                documents.append(chunk)
            
            return documents
            
        except Exception as e:
            logger.error(f"Filtered search failed: {e}")
            return []
    
    def __del__(self):
        """Cleanup executor on deletion"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
