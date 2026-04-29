"""
AI Agent service with memory and RAG capabilities
"""
import logging
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime, timedelta

from app.config import settings

logger = logging.getLogger(__name__)


class AgentMemory:
    """Simple in-memory storage for agent sessions"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def create_session(self, session_id: str):
        """Create a new session"""
        self.sessions[session_id] = {
            'messages': [],
            'created_at': datetime.now(),
            'last_activity': datetime.now()
        }
        logger.info(f"Created session: {session_id}")
    
    def add_message(self, session_id: str, role: str, content: str):
        """Add message to session"""
        if session_id not in self.sessions:
            self.create_session(session_id)
        
        self.sessions[session_id]['messages'].append({
            'role': role,
            'content': content,
            'timestamp': datetime.now()
        })
        self.sessions[session_id]['last_activity'] = datetime.now()
    
    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get session history"""
        if session_id not in self.sessions:
            return []
        return self.sessions[session_id]['messages']
    
    def cleanup_old_sessions(self):
        """Remove sessions older than TTL"""
        now = datetime.now()
        ttl = timedelta(seconds=settings.agent_session_ttl)
        
        expired = [
            sid for sid, session in self.sessions.items()
            if now - session['last_activity'] > ttl
        ]
        
        for sid in expired:
            del self.sessions[sid]
            logger.info(f"Cleaned up expired session: {sid}")


class AgentService:
    """AI Agent service with RAG and memory"""
    
    def __init__(self, vector_db_service, embedding_service, llm_service):
        """
        Initialize agent service
        
        Args:
            vector_db_service: Vector database service for RAG
            embedding_service: Embedding service
            llm_service: LLM service
        """
        self.vector_db = vector_db_service
        self.embedding = embedding_service
        self.llm = llm_service
        self.memory = AgentMemory() if settings.agent_memory_enabled else None
        logger.info("Initialized AI Agent service")
    
    def query(self, query: str, use_rag: bool = True, top_k: int = 3, 
              collection: str = "default", session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process agent query with optional RAG
        
        Args:
            query: User query
            use_rag: Whether to use RAG
            top_k: Number of documents to retrieve
            collection: Collection name
            session_id: Optional session ID for memory
            
        Returns:
            Response dictionary
        """
        sources = []
        context = None
        
        # RAG: Retrieve relevant context
        if use_rag:
            try:
                query_embedding = self.embedding.generate_embedding(query)
                results = self.vector_db.search(collection, query_embedding, top_k)
                
                if results:
                    context = [r['text'] for r in results]
                    sources = [{'id': r['id'], 'score': r['score']} for r in results]
                    logger.info(f"Retrieved {len(results)} documents for RAG")
            except Exception as e:
                logger.error(f"RAG retrieval failed: {e}")
        
        # Add session context if available
        if session_id and self.memory:
            history = self.memory.get_session_history(session_id)
            if history:
                # Add recent history to context
                recent_history = history[-3:]  # Last 3 messages
                history_context = "\n".join([
                    f"{msg['role']}: {msg['content']}" 
                    for msg in recent_history
                ])
                if context:
                    context.append(f"Previous conversation:\n{history_context}")
                else:
                    context = [f"Previous conversation:\n{history_context}"]
        
        # Generate response
        response = self.llm.generate_response(query, context)
        
        # Store in memory
        if session_id and self.memory:
            self.memory.add_message(session_id, "user", query)
            self.memory.add_message(session_id, "assistant", response)
        
        return {
            'query': query,
            'response': response,
            'sources': sources,
            'model': self.llm.get_model_name(),
            'session_id': session_id,
            'context_retrieved': len(sources) > 0 if use_rag else False
        }
    
    def chat(self, message: str, session_id: str) -> Dict[str, Any]:
        """
        Chat with agent using session memory
        
        Args:
            message: User message
            session_id: Session ID
            
        Returns:
            Response dictionary
        """
        # Ensure session exists
        if self.memory and session_id not in self.memory.sessions:
            self.memory.create_session(session_id)
        
        # Get session history for context
        context = []
        if self.memory:
            history = self.memory.get_session_history(session_id)
            if history:
                recent = history[-5:]  # Last 5 messages
                context_text = "\n".join([
                    f"{msg['role']}: {msg['content']}" 
                    for msg in recent
                ])
                context = [f"Conversation history:\n{context_text}"]
        
        # Generate response
        response = self.llm.generate_response(message, context)
        
        # Store in memory
        if self.memory:
            self.memory.add_message(session_id, "user", message)
            self.memory.add_message(session_id, "assistant", response)
        
        return {
            'response': response,
            'session_id': session_id,
            'context_retrieved': len(context) > 0
        }
    
    def upload_knowledge(self, documents: List[Dict[str, str]], collection: str = "default"):
        """
        Upload documents to knowledge base
        
        Args:
            documents: List of documents with 'text' and optional 'metadata'
            collection: Collection name
        """
        texts = [doc['text'] for doc in documents]
        metadatas = [doc.get('metadata', {}) for doc in documents]
        
        # Generate embeddings
        embeddings = self.embedding.generate_embeddings(texts)
        
        # Generate IDs
        ids = [str(uuid.uuid4()) for _ in texts]
        
        # Store in vector database
        self.vector_db.add_documents(collection, ids, embeddings, texts, metadatas)
        
        logger.info(f"Uploaded {len(documents)} documents to {collection}")
        
        return {
            'status': 'success',
            'documents_added': len(documents),
            'collection': collection
        }
