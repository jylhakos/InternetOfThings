"""
Pydantic models for request and response schemas
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class DocumentIngest(BaseModel):
    """Request model for document ingestion"""
    text: str = Field(..., description="Text content to ingest")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Document metadata")


class DocumentResponse(BaseModel):
    """Response model for document operations"""
    id: str
    status: str
    chunks: int
    message: Optional[str] = None


class SearchRequest(BaseModel):
    """Request model for vector search"""
    query: str = Field(..., description="Search query text")
    top_k: int = Field(default=5, ge=1, le=50, description="Number of results to return")
    filter: Optional[Dict[str, Any]] = Field(default=None, description="Metadata filters")
    collection: Optional[str] = Field(default="default", description="Collection name")


class SearchResult(BaseModel):
    """Single search result"""
    id: str
    score: float
    text: str
    metadata: Dict[str, Any]


class SearchResponse(BaseModel):
    """Response model for search operations"""
    results: List[SearchResult]
    query_time_ms: float
    total_results: int


class EmbeddingRequest(BaseModel):
    """Request model for embedding generation"""
    text: str = Field(..., description="Text to generate embeddings for")


class EmbeddingResponse(BaseModel):
    """Response model for embedding generation"""
    text: str
    embedding: List[float]
    dimensions: int
    model: str


class AgentQueryRequest(BaseModel):
    """Request model for AI agent queries"""
    query: str = Field(..., description="User query")
    use_rag: bool = Field(default=True, description="Whether to use RAG")
    top_k: int = Field(default=3, ge=1, le=10)
    session_id: Optional[str] = Field(default=None, description="Session ID for context")
    collection: Optional[str] = Field(default="default")
    agent_mode: Optional[str] = Field(default="default", description="Agent mode: default, research, chat")


class AgentQueryResponse(BaseModel):
    """Response model for AI agent queries"""
    query: str
    response: str
    sources: List[Dict[str, Any]]
    model: str
    session_id: Optional[str] = None
    context_retrieved: bool = False


class ChatMessage(BaseModel):
    """Request model for chat messages"""
    message: str = Field(..., description="User message")
    session_id: str = Field(..., description="Session ID")


class ChatResponse(BaseModel):
    """Response model for chat"""
    response: str
    session_id: str
    context_retrieved: bool
    timestamp: datetime = Field(default_factory=datetime.now)


class KnowledgeUpload(BaseModel):
    """Request model for uploading knowledge base"""
    documents: List[Dict[str, str]]
    collection: str = Field(default="default")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    vector_db: str
    llm: str
    timestamp: datetime = Field(default_factory=datetime.now)


class VectorDBStatus(BaseModel):
    """Vector database status"""
    status: str
    database: str
    collections: int
    total_vectors: int
