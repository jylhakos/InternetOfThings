"""
Configuration settings for the application
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "Vector Database API"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # Vector Database
    vector_db_type: str = "chroma"  # Options: chroma, qdrant, weaviate, milvus
    chroma_persist_directory: str = "./chroma_data"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None
    weaviate_url: str = "http://localhost:8080"
    milvus_host: str = "localhost"
    milvus_port: int = 19530
    
    # Embedding Model
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    
    # LLM / Inference Server
    llm_provider: str = "ollama"  # Options: ollama, huggingface, replicate
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"
    huggingface_api_key: Optional[str] = None
    replicate_api_key: Optional[str] = None
    
    # RAG Settings
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k_results: int = 5
    similarity_threshold: float = 0.7
    
    # Agent Settings
    agent_max_iterations: int = 5
    agent_memory_enabled: bool = True
    agent_session_ttl: int = 3600  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
