import asyncio
from typing import Dict, Any, List, Optional, TypedDict
from loguru import logger
import time

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.core.config import settings
from app.core.prompts import PromptTemplates, get_model_type_from_name
from app.models.schemas import RAGQuery, RAGResponse, DocumentChunk, ChatMessage, ChatResponse
from app.services.vector_service import VectorService
from app.services.ollama_service import OllamaService


class RAGState(TypedDict):
    """State for RAG workflow"""
    question: str
    documents: List[DocumentChunk]
    context: str
    answer: str
    model: str
    needs_web_search: bool
    confidence_score: float
    sources: List[str]
    processing_steps: List[str]


class RAGService:
    """RAG service using LangGraph for orchestration"""
    
    def __init__(self, vector_service: VectorService, ollama_service: OllamaService):
        self.vector_service = vector_service
        self.ollama_service = ollama_service
        self.workflow = self._create_rag_workflow()
        self.memory = MemorySaver()
    
    def _create_rag_workflow(self) -> StateGraph:
        """Create LangGraph workflow for RAG"""
        workflow = StateGraph(RAGState)
        
        # Add nodes
        workflow.add_node("retriever", self._retrieve_documents)
        workflow.add_node("document_grader", self._grade_documents)
        workflow.add_node("generator", self._generate_answer)
        workflow.add_node("hallucination_grader", self._grade_hallucination)
        workflow.add_node("answer_grader", self._grade_answer)
        workflow.add_node("web_search", self._web_search_fallback)
        
        # Set entry point
        workflow.set_entry_point("retriever")
        
        # Add edges
        workflow.add_edge("retriever", "document_grader")
        
        # Conditional routing after document grading
        workflow.add_conditional_edges(
            "document_grader",
            self._decide_to_generate,
            {
                "generate": "generator",
                "web_search": "web_search",
            }
        )
        
        # From web search back to generator
        workflow.add_edge("web_search", "generator")
        
        # From generator to hallucination grader
        workflow.add_edge("generator", "hallucination_grader")
        
        # Conditional routing after hallucination check
        workflow.add_conditional_edges(
            "hallucination_grader",
            self._decide_to_finish,
            {
                "useful": "answer_grader",
                "not_useful": "web_search",
            }
        )
        
        # From answer grader to end or back to generator
        workflow.add_conditional_edges(
            "answer_grader",
            self._grade_generation_v_documents_and_question,
            {
                "useful": END,
                "not_useful": "web_search",
            }
        )
        
        return workflow.compile(checkpointer=self.memory)
    
    async def _retrieve_documents(self, state: RAGState) -> RAGState:
        """Retrieve relevant documents from vector store"""
        logger.info(f"Retrieving documents for: {state['question']}")
        
        try:
            documents = await self.vector_service.search_documents(
                query=state["question"],
                top_k=5,
                score_threshold=0.7
            )
            
            state["documents"] = documents
            state["processing_steps"].append(f"Retrieved {len(documents)} documents")
            
            logger.info(f"Retrieved {len(documents)} documents")
            return state
            
        except Exception as e:
            logger.error(f"Document retrieval failed: {e}")
            state["documents"] = []
            state["processing_steps"].append("Document retrieval failed")
            return state
    
    async def _grade_documents(self, state: RAGState) -> RAGState:
        """Grade relevance of retrieved documents"""
        logger.info("Grading document relevance")
        
        try:
            relevant_docs = []
            
            for doc in state["documents"]:
                # Use LLM to grade document relevance
                prompt = PromptTemplates.RAG_DOCUMENT_GRADER_PROMPT.format(
                    document=doc.content[:500],  # Limit content for grading
                    question=state["question"]
                )
                
                response = await self.ollama_service.generate_response(
                    prompt=prompt,
                    model=state["model"],
                    max_tokens=50,
                    temperature=0.1
                )
                
                try:
                    score = float(response["response"].strip())
                    if score >= 3:  # Keep documents with score 3 or higher
                        doc.score = score
                        relevant_docs.append(doc)
                except ValueError:
                    # If we can't parse the score, keep the document
                    relevant_docs.append(doc)
            
            state["documents"] = relevant_docs
            state["processing_steps"].append(f"Filtered to {len(relevant_docs)} relevant documents")
            
            logger.info(f"Kept {len(relevant_docs)} relevant documents")
            return state
            
        except Exception as e:
            logger.error(f"Document grading failed: {e}")
            state["processing_steps"].append("Document grading failed, using all documents")
            return state
    
    async def _generate_answer(self, state: RAGState) -> RAGState:
        """Generate answer using retrieved documents"""
        logger.info("Generating answer")
        
        try:
            # Prepare context from documents
            context_parts = []
            sources = []
            
            for doc in state["documents"]:
                context_parts.append(f"Source: {doc.metadata.get('filename', 'Unknown')}\n{doc.content}")
                sources.append(doc.metadata.get('filename', f"Document {doc.id}"))
            
            context = "\n\n".join(context_parts)
            state["context"] = context
            state["sources"] = sources
            
            # Format prompt for specific model
            formatted_prompt = await self.ollama_service.format_prompt_for_model(
                question=state["question"],
                model=state["model"],
                context=context
            )
            
            # Generate response
            response = await self.ollama_service.generate_response(
                prompt=formatted_prompt,
                model=state["model"],
                max_tokens=500,
                temperature=0.7
            )
            
            state["answer"] = response["response"]
            state["processing_steps"].append("Generated answer from context")
            
            logger.info("Answer generated successfully")
            return state
            
        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            state["answer"] = "I apologize, but I encountered an error while generating the answer."
            state["processing_steps"].append("Answer generation failed")
            return state
    
    async def _grade_hallucination(self, state: RAGState) -> RAGState:
        """Check if answer is grounded in retrieved documents"""
        logger.info("Checking for hallucinations")
        
        try:
            if not state["documents"]:
                state["confidence_score"] = 0.5
                return state
            
            # Use LLM to grade hallucination
            docs_content = "\n".join([doc.content for doc in state["documents"]])
            prompt = PromptTemplates.HALLUCINATION_GRADER_PROMPT.format(
                documents=docs_content,
                generation=state["answer"]
            )
            
            response = await self.ollama_service.generate_response(
                prompt=prompt,
                model=state["model"],
                max_tokens=10,
                temperature=0.1
            )
            
            is_grounded = "yes" in response["response"].lower()
            state["confidence_score"] = 0.8 if is_grounded else 0.4
            state["processing_steps"].append(f"Hallucination check: {'passed' if is_grounded else 'failed'}")
            
            logger.info(f"Hallucination check: {'passed' if is_grounded else 'failed'}")
            return state
            
        except Exception as e:
            logger.error(f"Hallucination grading failed: {e}")
            state["confidence_score"] = 0.5
            state["processing_steps"].append("Hallucination check failed")
            return state
    
    async def _grade_answer(self, state: RAGState) -> RAGState:
        """Grade the quality of the answer"""
        logger.info("Grading answer quality")
        
        # Simple heuristic grading for now
        answer_length = len(state["answer"])
        has_sources = len(state["sources"]) > 0
        
        if answer_length > 50 and has_sources:
            quality_score = 0.8
        elif answer_length > 20:
            quality_score = 0.6
        else:
            quality_score = 0.3
        
        # Combine with confidence score
        state["confidence_score"] = (state["confidence_score"] + quality_score) / 2
        state["processing_steps"].append(f"Answer quality score: {quality_score}")
        
        return state
    
    async def _web_search_fallback(self, state: RAGState) -> RAGState:
        """Fallback to web search (placeholder for now)"""
        logger.info("Web search fallback triggered")
        
        # For now, just generate a response indicating we need more information
        state["answer"] = "I don't have enough information in my knowledge base to answer this question comprehensively. You may need to provide more specific documents or context."
        state["confidence_score"] = 0.3
        state["processing_steps"].append("Used web search fallback (placeholder)")
        
        return state
    
    def _decide_to_generate(self, state: RAGState) -> str:
        """Decide whether to generate answer or search web"""
        if len(state["documents"]) > 0:
            return "generate"
        else:
            return "web_search"
    
    def _decide_to_finish(self, state: RAGState) -> str:
        """Decide whether answer is useful or needs improvement"""
        if state["confidence_score"] > 0.6:
            return "useful"
        else:
            return "not_useful"
    
    def _grade_generation_v_documents_and_question(self, state: RAGState) -> str:
        """Final grading of answer quality"""
        if state["confidence_score"] > 0.7:
            return "useful"
        else:
            return "not_useful"
    
    async def query(self, request: RAGQuery, model: str = None) -> RAGResponse:
        """Process RAG query using the workflow"""
        start_time = time.time()
        
        try:
            # Initialize state
            initial_state = RAGState(
                question=request.query,
                documents=[],
                context="",
                answer="",
                model=model or settings.PRIMARY_MODEL,
                needs_web_search=False,
                confidence_score=0.0,
                sources=[],
                processing_steps=[]
            )
            
            # Run the workflow
            final_state = await self.workflow.ainvoke(
                initial_state,
                config={"configurable": {"thread_id": "rag_session"}}
            )
            
            processing_time = time.time() - start_time
            
            # Create response
            response = RAGResponse(
                answer=final_state["answer"],
                sources=final_state["documents"],
                query=request.query,
                confidence=final_state["confidence_score"],
                processing_time=processing_time
            )
            
            logger.info(f"RAG query completed in {processing_time:.3f}s")
            return response
            
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            processing_time = time.time() - start_time
            
            return RAGResponse(
                answer="I apologize, but I encountered an error while processing your question.",
                sources=[],
                query=request.query,
                confidence=0.0,
                processing_time=processing_time
            )
    
    async def chat(self, message: ChatMessage) -> ChatResponse:
        """Process chat message using RAG"""
        start_time = time.time()
        
        try:
            if message.use_rag:
                # Use full RAG workflow
                rag_query = RAGQuery(
                    query=message.message,
                    top_k=5,
                    score_threshold=0.7
                )
                
                rag_response = await self.query(rag_query, message.model.value)
                
                return ChatResponse(
                    response=rag_response.answer,
                    model_used=message.model.value,
                    sources=[doc.metadata.get('filename', f'Document {doc.id}') for doc in rag_response.sources],
                    context_used=len(rag_response.sources) > 0,
                    processing_time=rag_response.processing_time,
                    metadata={
                        "confidence": rag_response.confidence,
                        "document_count": len(rag_response.sources)
                    }
                )
            else:
                # Direct LLM query without RAG
                response = await self.ollama_service.generate_response(
                    prompt=message.message,
                    model=message.model.value,
                    max_tokens=message.max_tokens,
                    temperature=message.temperature,
                    top_p=message.top_p
                )
                
                processing_time = time.time() - start_time
                
                return ChatResponse(
                    response=response["response"],
                    model_used=message.model.value,
                    sources=[],
                    context_used=False,
                    processing_time=processing_time,
                    metadata={
                        "confidence": 1.0,
                        "document_count": 0
                    }
                )
                
        except Exception as e:
            logger.error(f"Chat processing failed: {e}")
            processing_time = time.time() - start_time
            
            return ChatResponse(
                response="I apologize, but I encountered an error while processing your message.",
                model_used=message.model.value,
                sources=[],
                context_used=False,
                processing_time=processing_time,
                metadata={"error": str(e)}
            )
