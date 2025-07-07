from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI
import uvicorn
from typing import Optional, List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Ollama FastAPI Server",
    description="FastAPI server that interfaces with Ollama LLM models using OpenAI-compatible API",
    version="1.0.0"
)

# Add CORS middleware to allow browser requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response validation
class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the message sender (user, assistant, system)")
    content: str = Field(..., description="Content of the message")

class PromptTemplate(BaseModel):
    """Template for structuring prompts with system instructions"""
    name: str = Field(..., description="Name of the template")
    system_prompt: str = Field(..., description="System instructions for the LLM")
    user_template: str = Field(default="{question}", description="Template for user input with placeholders")
    description: str = Field(default="", description="Description of what this template does")

class ChatRequest(BaseModel):
    question: str = Field(..., description="The question to ask the LLM")
    model: str = Field(default="llama3", description="The Ollama model to use")
    system_prompt: Optional[str] = Field(default=None, description="Custom system prompt for this request")
    template_name: Optional[str] = Field(default=None, description="Name of predefined template to use")
    max_tokens: Optional[int] = Field(default=500, description="Maximum tokens in response")
    temperature: Optional[float] = Field(default=0.7, description="Sampling temperature")
    stream: bool = Field(default=False, description="Whether to stream the response")

class TemplatedChatRequest(BaseModel):
    question: str = Field(..., description="The question to ask the LLM")
    template_name: str = Field(..., description="Name of the template to use")
    model: str = Field(default="llama3", description="The Ollama model to use")
    template_variables: Optional[Dict[str, str]] = Field(default={}, description="Variables to substitute in template")
    max_tokens: Optional[int] = Field(default=500, description="Maximum tokens in response")
    temperature: Optional[float] = Field(default=0.7, description="Sampling temperature")

class ChatResponse(BaseModel):
    answer: str = Field(..., description="The LLM's response to the question")
    model: str = Field(..., description="The model used for the response")
    system_prompt_used: Optional[str] = Field(default=None, description="The system prompt that was used")
    template_used: Optional[str] = Field(default=None, description="The template name that was used")
    usage: Optional[Dict[str, Any]] = Field(default=None, description="Token usage information")

class HealthResponse(BaseModel):
    status: str
    message: str
    ollama_connected: bool

# Predefined prompt templates
PROMPT_TEMPLATES = {
    "general": PromptTemplate(
        name="general",
        system_prompt="You are a helpful, knowledgeable, and friendly AI assistant. Provide clear, accurate, and concise responses to user questions.",
        user_template="{question}",
        description="General purpose assistant for any topic"
    ),
    "code_helper": PromptTemplate(
        name="code_helper",
        system_prompt="You are an expert programmer and coding assistant. Help users with programming questions, code review, debugging, and best practices. Provide code examples when helpful and explain your reasoning.",
        user_template="Programming question: {question}",
        description="Specialized assistant for programming and software development"
    ),
    "technical_writer": PromptTemplate(
        name="technical_writer",
        system_prompt="You are a technical writer who excels at explaining complex concepts clearly and concisely. Break down technical topics into easy-to-understand explanations with examples when appropriate.",
        user_template="Please explain: {question}",
        description="Assistant for technical explanations and documentation"
    ),
    "data_analyst": PromptTemplate(
        name="data_analyst",
        system_prompt="You are a data analyst and scientist. Help users understand data concepts, statistical methods, and provide insights on data-related questions. Use examples and clear explanations.",
        user_template="Data analysis question: {question}",
        description="Specialized assistant for data analysis and statistics"
    ),
    "creative_writer": PromptTemplate(
        name="creative_writer",
        system_prompt="You are a creative writing assistant. Help users with storytelling, creative writing techniques, character development, and narrative structure. Be imaginative and inspiring.",
        user_template="Creative writing request: {question}",
        description="Assistant for creative writing and storytelling"
    ),
    "teacher": PromptTemplate(
        name="teacher",
        system_prompt="You are an experienced teacher who excels at explaining concepts step-by-step. Break down complex topics into digestible parts, use analogies when helpful, and encourage learning.",
        user_template="Please teach me about: {question}",
        description="Educational assistant for learning and teaching"
    ),
    "business_advisor": PromptTemplate(
        name="business_advisor",
        system_prompt="You are a business consultant with expertise in strategy, operations, and management. Provide practical business advice and insights based on best practices and proven methodologies.",
        user_template="Business question: {question}",
        description="Assistant for business strategy and management advice"
    ),
    "researcher": PromptTemplate(
        name="researcher",
        system_prompt="You are a thorough researcher who provides well-researched, factual information. Cite sources when possible, present multiple perspectives on topics, and maintain objectivity.",
        user_template="Research topic: {question}",
        description="Assistant for research and fact-finding"
    )
}

def get_template(template_name: str) -> Optional[PromptTemplate]:
    """Get a template by name"""
    return PROMPT_TEMPLATES.get(template_name)

def format_prompt_with_template(template: PromptTemplate, question: str, variables: Dict[str, str] = None) -> List[Dict[str, str]]:
    """Format a question using a prompt template"""
    if variables is None:
        variables = {}
    
    # Add the question to variables
    variables["question"] = question
    
    # Format the user message using the template
    try:
        user_content = template.user_template.format(**variables)
    except KeyError as e:
        raise ValueError(f"Missing variable for template: {e}")
    
    # Return the formatted messages
    return [
        {"role": "system", "content": template.system_prompt},
        {"role": "user", "content": user_content}
    ]

# Initialize OpenAI client pointing to Ollama
# Ollama provides OpenAI-compatible API endpoints
client = OpenAI(
    base_url="http://localhost:11434/v1",  # Ollama's OpenAI-compatible endpoint
    api_key="not-needed"  # Ollama doesn't require API key
)

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with basic information"""
    return {
        "message": "Ollama FastAPI Server",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint to verify Ollama connection"""
    try:
        # Test connection to Ollama by listing models
        models = client.models.list()
        return HealthResponse(
            status="healthy",
            message="FastAPI server and Ollama are running",
            ollama_connected=True
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            message=f"Cannot connect to Ollama: {str(e)}",
            ollama_connected=False
        )

@app.get("/models")
async def list_models():
    """List available models from Ollama"""
    try:
        models = client.models.list()
        return {
            "models": [model.id for model in models.data],
            "count": len(models.data)
        }
    except Exception as e:
        logger.error(f"Failed to list models: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get models: {str(e)}")

@app.get("/templates")
async def list_templates():
    """List all available prompt templates"""
    return {
        "templates": {name: {"name": template.name, "description": template.description} 
                     for name, template in PROMPT_TEMPLATES.items()},
        "count": len(PROMPT_TEMPLATES)
    }

@app.get("/templates/{template_name}")
async def get_template_details(template_name: str):
    """Get detailed information about a specific template"""
    template = get_template(template_name)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")
    
    return {
        "name": template.name,
        "description": template.description,
        "system_prompt": template.system_prompt,
        "user_template": template.user_template
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_with_llm(request: ChatRequest):
    """
    Main endpoint to chat with the LLM model via Ollama
    
    This endpoint accepts a question and returns an answer from the specified LLM model.
    Supports custom system prompts and predefined templates.
    """
    try:
        logger.info(f"Received chat request for model: {request.model}")
        logger.info(f"Question: {request.question}")
        
        # Determine which system prompt and message structure to use
        messages = []
        system_prompt_used = None
        template_used = None
        
        if request.template_name:
            # Use predefined template
            template = get_template(request.template_name)
            if not template:
                raise HTTPException(status_code=404, detail=f"Template '{request.template_name}' not found")
            
            messages = format_prompt_with_template(template, request.question)
            system_prompt_used = template.system_prompt
            template_used = request.template_name
            logger.info(f"Using template: {request.template_name}")
            
        elif request.system_prompt:
            # Use custom system prompt
            messages = [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.question}
            ]
            system_prompt_used = request.system_prompt
            logger.info("Using custom system prompt")
            
        else:
            # No system prompt, just user question
            messages = [
                {"role": "user", "content": request.question}
            ]
            logger.info("Using simple user question without system prompt")
        
        # Call Ollama via OpenAI-compatible API
        response = client.chat.completions.create(
            model=request.model,
            messages=messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=request.stream
        )
        
        # Extract the answer from the response
        answer = response.choices[0].message.content
        
        # Prepare usage information if available
        usage_info = None
        if hasattr(response, 'usage') and response.usage:
            usage_info = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        
        logger.info(f"Generated response with {len(answer)} characters")
        
        return ChatResponse(
            answer=answer,
            model=request.model,
            system_prompt_used=system_prompt_used,
            template_used=template_used,
            usage=usage_info
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to get response from LLM: {str(e)}"
        )

@app.post("/chat/messages", response_model=ChatResponse)
async def chat_with_messages(request: Dict[str, Any]):
    """
    Advanced chat endpoint that accepts a list of messages for conversation context
    
    Expected format:
    {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "What is Python?"}
        ],
        "model": "llama3",
        "max_tokens": 500,
        "temperature": 0.7
    }
    """
    try:
        messages = request.get("messages", [])
        model = request.get("model", "llama3")
        max_tokens = request.get("max_tokens", 500)
        temperature = request.get("temperature", 0.7)
        
        if not messages:
            raise HTTPException(status_code=400, detail="Messages list cannot be empty")
        
        logger.info(f"Received conversation request with {len(messages)} messages")
        
        # Call Ollama via OpenAI-compatible API
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Extract the answer from the response
        answer = response.choices[0].message.content
        
        # Prepare usage information if available
        usage_info = None
        if hasattr(response, 'usage') and response.usage:
            usage_info = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        
        return ChatResponse(
            answer=answer,
            model=model,
            usage=usage_info
        )
        
    except Exception as e:
        logger.error(f"Error in chat/messages endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get response from LLM: {str(e)}"
        )

@app.post("/chat/template", response_model=ChatResponse)
async def chat_with_template(request: TemplatedChatRequest):
    """
    Chat endpoint that uses predefined prompt templates
    
    This endpoint uses predefined templates to structure the conversation
    with appropriate system prompts and user message formatting.
    """
    try:
        # Get the template
        template = get_template(request.template_name)
        if not template:
            raise HTTPException(status_code=404, detail=f"Template '{request.template_name}' not found")
        
        logger.info(f"Using template '{request.template_name}' for model: {request.model}")
        logger.info(f"Question: {request.question}")
        
        # Format the prompt using the template
        messages = format_prompt_with_template(
            template, 
            request.question, 
            request.template_variables
        )
        
        # Call Ollama via OpenAI-compatible API
        response = client.chat.completions.create(
            model=request.model,
            messages=messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        # Extract the answer from the response
        answer = response.choices[0].message.content
        
        # Prepare usage information if available
        usage_info = None
        if hasattr(response, 'usage') and response.usage:
            usage_info = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        
        logger.info(f"Generated response with {len(answer)} characters using template '{request.template_name}'")
        
        return ChatResponse(
            answer=answer,
            model=request.model,
            system_prompt_used=template.system_prompt,
            template_used=request.template_name,
            usage=usage_info
        )
        
    except ValueError as e:
        logger.error(f"Template formatting error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in template chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to get response from LLM: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
