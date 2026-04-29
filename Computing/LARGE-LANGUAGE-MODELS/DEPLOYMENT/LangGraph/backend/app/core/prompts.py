"""
Prompt templates for different LLM models
"""

from typing import Dict, Any
from enum import Enum


class ModelType(str, Enum):
    ARCEE_AGENT = "arcee-agent"
    CODELLAMA = "codellama"
    DEFAULT = "default"


class PromptTemplates:
    """Collection of prompt templates for different models"""
    
    # ArceeAgent specific prompts (using ChatML format)
    ARCEE_AGENT_SYSTEM = """<|im_start|>system
You are a helpful AI assistant specialized in function calling and tool usage. You excel at retrieving information from documents and providing accurate, well-structured answers based on the provided context.

Available tools:
- search_documents: Search for relevant information in the knowledge base
- web_search: Search the internet for additional information if needed

When using tools, format your calls using XML-like tags:
<tool_call>
<name>search_documents</name>
<parameters>
<query>your search query here</query>
</parameters>
</tool_call>

Guidelines:
1. Always use the provided context documents first
2. Provide accurate and relevant information
3. If information is not available in the context, clearly state this
4. Format responses in a clear, structured manner
5. Include source references when possible
<|im_end|>"""

    ARCEE_AGENT_USER = """<|im_start|>user
Question: {question}

Context Documents:
{context}

Please provide a comprehensive answer based on the context provided.
<|im_end|>

<|im_start|>assistant"""

    # CodeLlama specific prompts
    CODELLAMA_SYSTEM = """# System Prompt
You are CodeLlama, an expert coding assistant. You excel at:
- Writing clean, efficient code
- Explaining programming concepts
- Debugging and troubleshooting
- Code reviews and optimization
- Multiple programming languages

Guidelines:
1. Provide clear explanations with code examples
2. Use proper syntax highlighting
3. Include comments in code when helpful
4. Suggest best practices
5. Offer alternative solutions when appropriate"""

    CODELLAMA_USER = """# Programming Question
{question}

## Context
{context}

## Instructions
Provide a comprehensive answer with:
- Clear explanation of the solution
- Working code examples
- Best practices and considerations
- Comments explaining key concepts

## Response:"""

    # Default/Generic prompts
    DEFAULT_SYSTEM = """You are a helpful AI assistant. You provide accurate, informative responses based on the given context. Always be honest about what you know and don't know."""

    DEFAULT_USER = """Question: {question}

Context: {context}

Please provide a helpful and accurate response."""

    # RAG-specific prompts
    RAG_QUERY_PROMPT = """Based on the following context documents, please answer the user's question. If the answer cannot be found in the context, please say so clearly.

Context:
{context}

Question: {question}

Answer:"""

    RAG_DOCUMENT_GRADER_PROMPT = """You are a grader assessing relevance of retrieved documents to a user question.
    
Retrieved document:
{document}

User question: {question}

Rate the relevance of the document to the question on a scale of 1-5 (1 = not relevant, 5 = highly relevant).
Provide just the number."""

    HALLUCINATION_GRADER_PROMPT = """You are a grader assessing whether an answer is grounded in a set of retrieved facts.
    
Retrieved facts:
{documents}

Answer: {generation}

Is the answer grounded in the retrieved facts? Answer with 'yes' or 'no'."""

    @classmethod
    def get_system_prompt(cls, model_type: ModelType) -> str:
        """Get system prompt for specific model type"""
        if model_type == ModelType.ARCEE_AGENT:
            return cls.ARCEE_AGENT_SYSTEM
        elif model_type == ModelType.CODELLAMA:
            return cls.CODELLAMA_SYSTEM
        else:
            return cls.DEFAULT_SYSTEM
    
    @classmethod
    def get_user_prompt(cls, model_type: ModelType) -> str:
        """Get user prompt template for specific model type"""
        if model_type == ModelType.ARCEE_AGENT:
            return cls.ARCEE_AGENT_USER
        elif model_type == ModelType.CODELLAMA:
            return cls.CODELLAMA_USER
        else:
            return cls.DEFAULT_USER
    
    @classmethod
    def format_prompt(
        cls, 
        model_type: ModelType, 
        question: str, 
        context: str = "", 
        **kwargs
    ) -> str:
        """Format complete prompt for specific model"""
        system_prompt = cls.get_system_prompt(model_type)
        user_prompt = cls.get_user_prompt(model_type)
        
        # Format the user prompt with provided variables
        formatted_user = user_prompt.format(
            question=question,
            context=context,
            **kwargs
        )
        
        # Combine system and user prompts
        if model_type == ModelType.ARCEE_AGENT:
            return system_prompt + "\n\n" + formatted_user
        else:
            return system_prompt + "\n\n" + formatted_user


def get_model_type_from_name(model_name: str) -> ModelType:
    """Determine model type from model name"""
    model_name_lower = model_name.lower()
    
    if "arcee" in model_name_lower:
        return ModelType.ARCEE_AGENT
    elif "codellama" in model_name_lower or "code-llama" in model_name_lower:
        return ModelType.CODELLAMA
    else:
        return ModelType.DEFAULT


# Response format schemas
RESPONSE_FORMAT_JSON = {
    "type": "json_object",
    "schema": {
        "type": "object",
        "properties": {
            "answer": {
                "type": "string",
                "description": "The main answer to the question"
            },
            "sources": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of source documents used"
            },
            "confidence": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "Confidence score for the answer"
            },
            "reasoning": {
                "type": "string",
                "description": "Explanation of how the answer was derived"
            }
        },
        "required": ["answer"]
    }
}
