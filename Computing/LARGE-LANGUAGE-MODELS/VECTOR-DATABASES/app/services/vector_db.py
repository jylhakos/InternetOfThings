"""
Vector database service supporting multiple backends
"""
import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import uuid

from app.config import settings

logger = logging.getLogger(__name__)


class VectorDBBackend(ABC):
    """Abstract base class for vector database backends"""
    
    @abstractmethod
    def create_collection(self, name: str, dimension: int):
        """Create a collection"""
        pass
    
    @abstractmethod
    def add_documents(self, collection: str, ids: List[str], embeddings: List[List[float]], 
                     texts: List[str], metadatas: List[Dict[str, Any]]):
        """Add documents to collection"""
        pass
    
    @abstractmethod
    def search(self, collection: str, query_embedding: List[float], top_k: int, 
               filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get database status"""
        pass
    
    @abstractmethod
    def close(self):
        """Close connection"""
        pass


class ChromaBackend(VectorDBBackend):
    """ChromaDB backend implementation"""
    
    def __init__(self):
        import chromadb
        from chromadb.config import Settings as ChromaSettings
        
        self.client = chromadb.Client(ChromaSettings(
            persist_directory=settings.chroma_persist_directory,
            anonymized_telemetry=False
        ))
        logger.info("Initialized ChromaDB backend")
    
    def create_collection(self, name: str, dimension: int):
        """Create or get collection"""
        try:
            self.client.get_or_create_collection(name=name)
            logger.info(f"Created/got collection: {name}")
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            raise
    
    def add_documents(self, collection: str, ids: List[str], embeddings: List[List[float]], 
                     texts: List[str], metadatas: List[Dict[str, Any]]):
        """Add documents to collection"""
        coll = self.client.get_collection(name=collection)
        coll.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        logger.info(f"Added {len(ids)} documents to {collection}")
    
    def search(self, collection: str, query_embedding: List[float], top_k: int, 
               filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        coll = self.client.get_collection(name=collection)
        results = coll.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter
        )
        
        # Format results
        formatted_results = []
        if results['ids'] and results['ids'][0]:
            for i, doc_id in enumerate(results['ids'][0]):
                formatted_results.append({
                    'id': doc_id,
                    'score': 1.0 - results['distances'][0][i] if results.get('distances') else 0.0,
                    'text': results['documents'][0][i] if results.get('documents') else '',
                    'metadata': results['metadatas'][0][i] if results.get('metadatas') else {}
                })
        
        return formatted_results
    
    def get_status(self) -> Dict[str, Any]:
        """Get database status"""
        collections = self.client.list_collections()
        total_vectors = sum(coll.count() for coll in collections)
        return {
            'status': 'connected',
            'database': 'chroma',
            'collections': len(collections),
            'total_vectors': total_vectors
        }
    
    def close(self):
        """Close connection"""
        logger.info("Closing ChromaDB connection")


class QdrantBackend(VectorDBBackend):
    """Qdrant backend implementation"""
    
    def __init__(self):
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams
        
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key
        )
        self.Distance = Distance
        self.VectorParams = VectorParams
        logger.info("Initialized Qdrant backend")
    
    def create_collection(self, name: str, dimension: int):
        """Create collection"""
        from qdrant_client.models import Distance, VectorParams
        
        try:
            self.client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(size=dimension, distance=Distance.COSINE)
            )
            logger.info(f"Created collection: {name}")
        except Exception as e:
            logger.warning(f"Collection may already exist: {e}")
    
    def add_documents(self, collection: str, ids: List[str], embeddings: List[List[float]], 
                     texts: List[str], metadatas: List[Dict[str, Any]]):
        """Add documents to collection"""
        from qdrant_client.models import PointStruct
        
        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={'text': text, **metadata}
            )
            for embedding, text, metadata in zip(embeddings, texts, metadatas)
        ]
        
        self.client.upsert(collection_name=collection, points=points)
        logger.info(f"Added {len(points)} documents to {collection}")
    
    def search(self, collection: str, query_embedding: List[float], top_k: int, 
               filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        results = self.client.search(
            collection_name=collection,
            query_vector=query_embedding,
            limit=top_k
        )
        
        formatted_results = [
            {
                'id': str(result.id),
                'score': result.score,
                'text': result.payload.get('text', ''),
                'metadata': {k: v for k, v in result.payload.items() if k != 'text'}
            }
            for result in results
        ]
        
        return formatted_results
    
    def get_status(self) -> Dict[str, Any]:
        """Get database status"""
        collections = self.client.get_collections()
        return {
            'status': 'connected',
            'database': 'qdrant',
            'collections': len(collections.collections),
            'total_vectors': sum(self.client.count(c.name).count for c in collections.collections)
        }
    
    def close(self):
        """Close connection"""
        logger.info("Closing Qdrant connection")


class VectorDBService:
    """Main vector database service"""
    
    def __init__(self):
        """Initialize vector database backend"""
        self.backend = self._create_backend()
        self.backend.create_collection("default", settings.embedding_dimension)
    
    def _create_backend(self) -> VectorDBBackend:
        """Create appropriate backend based on config"""
        if settings.vector_db_type == "chroma":
            return ChromaBackend()
        elif settings.vector_db_type == "qdrant":
            return QdrantBackend()
        else:
            raise ValueError(f"Unsupported vector database: {settings.vector_db_type}")
    
    def add_documents(self, collection: str, ids: List[str], embeddings: List[List[float]], 
                     texts: List[str], metadatas: List[Dict[str, Any]]):
        """Add documents to collection"""
        self.backend.add_documents(collection, ids, embeddings, texts, metadatas)
    
    def search(self, collection: str, query_embedding: List[float], top_k: int, 
               filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        return self.backend.search(collection, query_embedding, top_k, filter)
    
    def get_status(self) -> Dict[str, Any]:
        """Get database status"""
        return self.backend.get_status()
    
    def close(self):
        """Close connection"""
        self.backend.close()
