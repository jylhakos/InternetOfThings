"""
RAG Pipeline Module

This module handles document loading, indexing, and query engine creation
for Retrieval-Augmented Generation with LlamaIndex.
"""

import os
from pathlib import Path
from typing import Optional, List

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Settings,
    StorageContext,
)
from llama_index.core.tools import QueryEngineTool
from llama_index.llms.openai import OpenAI


def load_documents(data_dir: str = "./data") -> List:
    """
    Load documents from a directory.
    
    Args:
        data_dir (str): Path to directory containing documents
        
    Returns:
        List: Loaded documents
        
    Raises:
        FileNotFoundError: If data directory doesn't exist
        ValueError: If no documents found in directory
    """
    data_path = Path(data_dir)
    
    if not data_path.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")
    
    documents = SimpleDirectoryReader(data_dir).load_data()
    
    if not documents:
        raise ValueError(f"No documents found in {data_dir}")
    
    print(f"Loaded {len(documents)} documents from {data_dir}")
    return documents


def create_vector_index(documents: List, llm_model: str = "gpt-4o") -> VectorStoreIndex:
    """
    Create a vector index from documents.
    
    Args:
        documents (List): List of documents to index
        llm_model (str): LLM model to use (default: gpt-4o)
        
    Returns:
        VectorStoreIndex: Created vector index
    """
    # Configure LLM settings
    Settings.llm = OpenAI(model=llm_model, temperature=0)
    
    # Create vector index
    index = VectorStoreIndex.from_documents(documents)
    
    print(f"Created vector index with {len(documents)} documents")
    return index


def create_rag_query_engine(data_dir: str = "./data", llm_model: str = "gpt-4o"):
    """
    Create a complete RAG query engine from documents.
    
    Args:
        data_dir (str): Path to directory containing documents
        llm_model (str): LLM model to use
        
    Returns:
        Query engine for RAG queries
    """
    documents = load_documents(data_dir)
    index = create_vector_index(documents, llm_model)
    query_engine = index.as_query_engine()
    
    return query_engine


def create_rag_tool(
    data_dir: str = "./data",
    tool_name: str = "knowledge_base",
    tool_description: str = "Useful for answering questions about LlamaIndex documentation and RAG concepts.",
    llm_model: str = "gpt-4o"
) -> QueryEngineTool:
    """
    Create a RAG tool that can be used by LlamaIndex agents.
    
    Args:
        data_dir (str): Path to directory containing documents
        tool_name (str): Name of the tool
        tool_description (str): Description of what the tool does
        llm_model (str): LLM model to use
        
    Returns:
        QueryEngineTool: A tool wrapping the RAG query engine
    """
    query_engine = create_rag_query_engine(data_dir, llm_model)
    
    rag_tool = QueryEngineTool.from_defaults(
        query_engine=query_engine,
        name=tool_name,
        description=tool_description
    )
    
    print(f"Created RAG tool: {tool_name}")
    return rag_tool


def setup_chromadb_storage(collection_name: str = "rag_documents"):
    """
    Setup ChromaDB for persistent vector storage.
    
    Args:
        collection_name (str): Name of the Chroma collection
        
    Returns:
        tuple: (chroma_client, vector_store, storage_context)
        
    Note:
        Requires ChromaDB server running on localhost:8000
        Start with: docker run -p 8000:8000 chromadb/chroma
    """
    try:
        import chromadb
        from llama_index.vector_stores.chroma import ChromaVectorStore
        
        # Connect to Chroma server
        chroma_client = chromadb.HttpClient(host="localhost", port=8000)
        
        # Get or create collection
        chroma_collection = chroma_client.get_or_create_collection(collection_name)
        
        # Create vector store
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        
        # Create storage context
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        print(f"Connected to ChromaDB collection: {collection_name}")
        return chroma_client, vector_store, storage_context
        
    except Exception as e:
        print(f"Error connecting to ChromaDB: {e}")
        print("Make sure ChromaDB is running: docker run -p 8000:8000 chromadb/chroma")
        raise


def create_persistent_index(documents: List, collection_name: str = "rag_documents"):
    """
    Create a vector index with persistent ChromaDB storage.
    
    Args:
        documents (List): Documents to index
        collection_name (str): ChromaDB collection name
        
    Returns:
        VectorStoreIndex: Index with persistent storage
    """
    _, _, storage_context = setup_chromadb_storage(collection_name)
    
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context
    )
    
    print(f"Created persistent index in ChromaDB: {collection_name}")
    return index


if __name__ == "__main__":
    # Test the RAG pipeline
    from dotenv import load_dotenv
    load_dotenv()
    
    print("Testing RAG pipeline...")
    
    # Create query engine
    query_engine = create_rag_query_engine()
    
    # Test query
    response = query_engine.query("What is LlamaIndex?")
    print(f"\nQuery: What is LlamaIndex?")
    print(f"Response: {response}")
