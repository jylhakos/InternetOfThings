"""
LangGraph Agent Evaluation with Langfuse Tracing

This script demonstrates how to create a LangGraph agent with full observability
using Langfuse for tracing, evaluation, and monitoring.

Based on: https://langfuse.com/guides/cookbook/example_langgraph_agents
"""

import os
from typing import TypedDict, Annotated, Sequence
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import Tool
from langchain_core.messages import BaseMessage, HumanMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolInvocation, ToolExecutor

from langfuse.decorators import observe, langfuse_context
from langfuse.callback import CallbackHandler

# Load environment variables
load_dotenv()


# Define sample tools for the agent
def search_tool(query: str) -> str:
    """Simulates a search tool that retrieves information."""
    # In production, this would call an actual search API
    search_results = {
        "What is the capital of France?": "Paris is the capital of France.",
        "Who wrote Romeo and Juliet?": "William Shakespeare wrote Romeo and Juliet.",
        "What is the speed of light?": "The speed of light is approximately 299,792,458 meters per second.",
    }
    return search_results.get(query, f"No results found for: {query}")


def calculator_tool(expression: str) -> str:
    """Simulates a calculator tool that evaluates mathematical expressions."""
    try:
        # WARNING: In production, use a safe eval alternative
        result = eval(expression)
        return f"The result of {expression} is {result}"
    except Exception as e:
        return f"Error calculating {expression}: {str(e)}"


# Define tools for LangChain
tools = [
    Tool(
        name="Search",
        func=search_tool,
        description="Useful for searching for factual information. Input should be a search query."
    ),
    Tool(
        name="Calculator",
        func=calculator_tool,
        description="Useful for mathematical calculations. Input should be a mathematical expression."
    )
]


# Define the agent state
class AgentState(TypedDict):
    messages: Sequence[BaseMessage]
    next_action: str


@observe(name="create_research_agent")
def create_agent():
    """Create a LangGraph agent with tools."""
    
    # Initialize LLM
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        streaming=False
    )
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful AI assistant. Use the available tools to answer questions.
        
Available tools:
- Search: For finding factual information
- Calculator: For mathematical calculations

Think step by step and use tools when necessary."""),
        MessagesPlaceholder(variable_name="messages"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create agent
    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    return agent_executor


@observe(name="run_agent")
def run_agent_with_tracing(query: str, session_id: str = None):
    """
    Run the agent with full Langfuse tracing.
    
    Args:
        query: The user's question
        session_id: Optional session ID for grouping related traces
    
    Returns:
        Agent response and trace information
    """
    
    # Initialize Langfuse callback handler
    langfuse_handler = CallbackHandler(
        session_id=session_id,
        tags=["langgraph-agent", "evaluation"]
    )
    
    # Create agent
    agent = create_agent()
    
    # Run agent with tracing
    try:
        response = agent.invoke(
            {"input": query},
            config={"callbacks": [langfuse_handler]}
        )
        
        # Get trace information
        trace_id = langfuse_context.get_current_trace_id()
        
        print(f"✓ Agent executed successfully")
        print(f"✓ Trace ID: {trace_id}")
        print(f"✓ Response: {response['output']}")
        
        return {
            "query": query,
            "response": response["output"],
            "trace_id": trace_id,
            "intermediate_steps": response.get("intermediate_steps", [])
        }
        
    except Exception as e:
        print(f"✗ Error running agent: {str(e)}")
        raise


@observe(name="batch_evaluation")
def evaluate_agent_on_dataset(test_cases: list, dataset_name: str = "agent_eval"):
    """
    Evaluate agent on multiple test cases and log to Langfuse.
    
    Args:
        test_cases: List of dicts with 'input' and 'expected_output' keys
        dataset_name: Name of the evaluation dataset
    
    Returns:
        Evaluation results
    """
    
    results = []
    
    for idx, test_case in enumerate(test_cases):
        print(f"\n{'='*60}")
        print(f"Test Case {idx + 1}/{len(test_cases)}")
        print(f"{'='*60}")
        print(f"Input: {test_case['input']}")
        print(f"Expected: {test_case.get('expected_output', 'N/A')}")
        
        # Run agent
        result = run_agent_with_tracing(
            query=test_case["input"],
            session_id=f"{dataset_name}_run_{idx}"
        )
        
        # Calculate simple accuracy (exact match or semantic similarity in production)
        actual_output = result["response"]
        expected_output = test_case.get("expected_output", "")
        
        # Simple match check (in production, use semantic similarity)
        is_correct = expected_output.lower() in actual_output.lower() if expected_output else None
        
        results.append({
            "test_case_id": idx,
            "input": test_case["input"],
            "expected": expected_output,
            "actual": actual_output,
            "correct": is_correct,
            "trace_id": result["trace_id"]
        })
        
        print(f"Actual: {actual_output}")
        print(f"Match: {is_correct}")
    
    return results


def main():
    """Main execution function."""
    
    print("="*60)
    print("LangGraph Agent Evaluation with Langfuse")
    print("="*60)
    
    # Example 1: Single query with tracing
    print("\n--- Example 1: Single Query ---")
    result = run_agent_with_tracing(
        query="What is the capital of France?",
        session_id="demo_session"
    )
    
    # Example 2: Batch evaluation on test cases
    print("\n--- Example 2: Batch Evaluation ---")
    
    test_cases = [
        {
            "input": "What is the capital of France?",
            "expected_output": "Paris"
        },
        {
            "input": "Who wrote Romeo and Juliet?",
            "expected_output": "Shakespeare"
        },
        {
            "input": "What is 25 * 4?",
            "expected_output": "100"
        },
        {
            "input": "What is the speed of light?",
            "expected_output": "299,792,458 meters per second"
        }
    ]
    
    evaluation_results = evaluate_agent_on_dataset(
        test_cases=test_cases,
        dataset_name="demo_evaluation"
    )
    
    # Print summary
    print("\n" + "="*60)
    print("Evaluation Summary")
    print("="*60)
    
    correct_count = sum(1 for r in evaluation_results if r["correct"])
    total_count = len(evaluation_results)
    accuracy = correct_count / total_count if total_count > 0 else 0
    
    print(f"Total Test Cases: {total_count}")
    print(f"Correct: {correct_count}")
    print(f"Accuracy: {accuracy:.2%}")
    
    print("\n✓ All evaluations complete!")
    print("✓ View detailed traces in Langfuse dashboard")
    print(f"✓ Dashboard: {os.getenv('LANGFUSE_HOST', 'http://localhost:3000')}")


if __name__ == "__main__":
    # Check required environment variables
    required_vars = ["OPENAI_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"✗ Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("✗ Please create a .env file with the required variables")
        exit(1)
    
    main()
