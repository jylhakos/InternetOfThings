"""
AI Agent with RAG and External Tools

This module creates an intelligent agent that combines:
- RAG (Retrieval-Augmented Generation) for knowledge base queries
- Weather API for real-time weather information
- ReAct reasoning to decide which tool to use
"""

import os
from typing import List, Optional
from dotenv import load_dotenv

from llama_index.core.agent import ReActAgent
from llama_index.core.tools import BaseTool
from llama_index.llms.openai import OpenAI

from weather_tool import create_weather_tool
from rag_pipeline import create_rag_tool


class RAGAgent:
    """
    An intelligent agent that combines RAG with external tools.
    
    The agent uses reasoning to decide whether to:
    - Query the internal knowledge base (RAG)
    - Call external APIs (e.g., weather)
    - Use other custom tools
    """
    
    def __init__(
        self,
        data_dir: str = "./data",
        llm_model: str = "gpt-4o",
        verbose: bool = True,
        additional_tools: Optional[List[BaseTool]] = None
    ):
        """
        Initialize the RAG agent.
        
        Args:
            data_dir (str): Directory containing knowledge base documents
            llm_model (str): LLM model to use (e.g., gpt-4o, gpt-3.5-turbo)
            verbose (bool): Whether to print agent's thought process
            additional_tools (List[BaseTool], optional): Additional tools for the agent
        """
        # Load environment variables
        load_dotenv()
        
        # Verify API keys
        self._verify_api_keys()
        
        # Initialize LLM
        self.llm = OpenAI(model=llm_model, temperature=0)
        self.verbose = verbose
        
        # Create tools
        print("Initializing agent tools...")
        self.tools = []
        
        # Add RAG tool
        try:
            rag_tool = create_rag_tool(
                data_dir=data_dir,
                tool_name="knowledge_base",
                tool_description=(
                    "Useful for answering questions about LlamaIndex, RAG concepts, "
                    "AI agents, and information from the internal knowledge base."
                ),
                llm_model=llm_model
            )
            self.tools.append(rag_tool)
        except Exception as e:
            print(f"Warning: Could not create RAG tool: {e}")
        
        # Add weather tool
        try:
            weather_tool = create_weather_tool()
            self.tools.append(weather_tool)
        except Exception as e:
            print(f"Warning: Could not create weather tool: {e}")
        
        # Add additional tools
        if additional_tools:
            self.tools.extend(additional_tools)
        
        # Create agent
        if not self.tools:
            raise ValueError("No tools available for the agent!")
        
        print(f"Created agent with {len(self.tools)} tools")
        self.agent = ReActAgent.from_tools(
            self.tools,
            llm=self.llm,
            verbose=self.verbose
        )
    
    def _verify_api_keys(self):
        """Verify that required API keys are set."""
        if not os.getenv("OPENAI_API_KEY"):
            print("Warning: OPENAI_API_KEY not found in environment")
        
        if not os.getenv("OPENWEATHER_API_KEY"):
            print("Warning: OPENWEATHER_API_KEY not found (weather tool may not work)")
    
    def chat(self, message: str) -> str:
        """
        Send a message to the agent and get a response.
        
        Args:
            message (str): User's question or request
            
        Returns:
            str: Agent's response
        """
        response = self.agent.chat(message)
        return str(response)
    
    def stream_chat(self, message: str):
        """
        Send a message and stream the response.
        
        Args:
            message (str): User's question or request
            
        Yields:
            str: Response tokens as they are generated
        """
        response = self.agent.stream_chat(message)
        for token in response.response_gen:
            yield token
    
    def reset(self):
        """Reset the agent's conversation memory."""
        self.agent.reset()


def main():
    """
    Example usage of the RAG agent.
    Demonstrates how the agent chooses between different tools.
    """
    print("=" * 80)
    print("RAG AGENT WITH MULTIPLE TOOLS")
    print("=" * 80)
    
    # Create agent
    agent = RAGAgent(
        data_dir="./data",
        llm_model="gpt-4o",
        verbose=True
    )
    
    # Example queries
    queries = [
        "What is LlamaIndex?",
        "What's the weather like in Tokyo?",
        "How does RAG work?",
        "What's the current weather in Paris?",
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'=' * 80}")
        print(f"QUERY {i}: {query}")
        print(f"{'=' * 80}")
        
        try:
            response = agent.chat(query)
            print(f"\nFINAL RESPONSE:\n{response}\n")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
