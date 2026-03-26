"""
Prompt Template Example with LangChain and Ollama

This example demonstrates how to:
1. Define a flexible prompt template with input variables.
2. Load an open-source model using the Ollama integration.
3. Combine them into a simple chain and invoke it.

Prerequisites:
- Install required packages: pip install langchain langchain-community
- Install Ollama: https://ollama.ai
- Pull a model: ollama pull llama2
"""

from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


def simple_translation_example():
    """
    Example 1: Simple Translation with Prompt Template
    
    This demonstrates the basic usage of prompt templates with LangChain.
    """
    print("=" * 60)
    print("Example 1: Simple Translation")
    print("=" * 60)
    
    # 1. Define the Prompt Template
    # A prompt template allows for dynamic content based on input variables.
    prompt_template_str = """
You are a helpful assistant that translates English to French.
Translate the following English phrase to French:
{phrase}
"""
    
    # Create a PromptTemplate instance, which automatically detects the variable "phrase".
    prompt = PromptTemplate.from_template(prompt_template_str)
    
    # 2. Load the Open Source Model
    # This uses the Ollama integration to run an open-source model (e.g., "llama2") locally.
    # Ensure you have the model pulled locally using `ollama pull llama2`.
    llm = Ollama(model="llama2")
    
    # 3. Create a Chain
    # Chains connect components (prompts, models, parsers) to form an application.
    # The LangChain Expression Language (LCEL) uses the pipe operator `|` for this.
    chain = prompt | llm | StrOutputParser()
    
    # 4. Invoke the Chain
    # Pass a dictionary with the input variable(s) to the invoke method.
    input_data = {"phrase": "Hello, world!"}
    response = chain.invoke(input_data)
    
    print(f"English Phrase: {input_data['phrase']}")
    print(f"French Translation: {response}")
    print()


def data_analyst_example():
    """
    Example 2: Data Analyst Prompt with Constraints
    
    This demonstrates a more complex prompt with role, task, and constraints.
    """
    print("=" * 60)
    print("Example 2: Data Analyst Summary")
    print("=" * 60)
    
    # Define a structured prompt template with role, task, and constraints
    prompt_template = """
System/Role: You are an expert data analyst.

Task: Summarize the main findings from the text provided below.

Constraints:
- Use bullet points.
- Maximum 5 bullets.
- Focus on key insights.

Text: \"\"\"
{text}
\"\"\"

Summary:
"""
    
    prompt = PromptTemplate.from_template(prompt_template)
    llm = Ollama(model="llama2")
    chain = prompt | llm | StrOutputParser()
    
    # Sample data
    sample_text = """
    In Q4 2023, the company saw a 25% increase in revenue compared to Q3.
    Customer acquisition costs decreased by 15%, while customer retention 
    improved to 92%. The new product line launched in October contributed 
    $2M in sales. Operating expenses remained stable at $5M per quarter.
    The marketing team's new campaign resulted in a 40% increase in website traffic.
    """
    
    response = chain.invoke({"text": sample_text})
    
    print("Input Text:")
    print(sample_text)
    print("\nAI-Generated Summary:")
    print(response)
    print()


def few_shot_sentiment_example():
    """
    Example 3: Few-Shot Sentiment Analysis
    
    This demonstrates few-shot learning where we provide examples to guide the model.
    """
    print("=" * 60)
    print("Example 3: Few-Shot Sentiment Analysis")
    print("=" * 60)
    
    # Few-shot prompt with examples
    prompt_template = """
Classify the sentiment of the following reviews as Positive, Negative, or Neutral.

Examples:
Review: "The product exceeded my expectations!"
Sentiment: Positive

Review: "Terrible quality, broke after one day."
Sentiment: Negative

Review: "The service was okay, nothing special."
Sentiment: Neutral

Now classify this review:
Review: {review}
Sentiment:
"""
    
    prompt = PromptTemplate.from_template(prompt_template)
    llm = Ollama(model="llama2")
    chain = prompt | llm | StrOutputParser()
    
    # Test reviews
    test_reviews = [
        "Absolutely love this! Best purchase ever!",
        "Don't waste your money on this.",
        "It works as described. Nothing more, nothing less."
    ]
    
    for review in test_reviews:
        response = chain.invoke({"review": review})
        print(f"Review: {review}")
        print(f"Sentiment: {response.strip()}")
        print()


def chain_of_thought_example():
    """
    Example 4: Chain-of-Thought Reasoning
    
    This demonstrates using chain-of-thought prompting for better reasoning.
    """
    print("=" * 60)
    print("Example 4: Chain-of-Thought Reasoning")
    print("=" * 60)
    
    prompt_template = """
You are a math tutor. Solve the following problem step-by-step.

Problem: {problem}

Let's think step-by-step:
"""
    
    prompt = PromptTemplate.from_template(prompt_template)
    llm = Ollama(model="llama2")
    chain = prompt | llm | StrOutputParser()
    
    problem = "If a store sells 45 items per day and operates 6 days a week, how many items does it sell in 4 weeks?"
    
    response = chain.invoke({"problem": problem})
    
    print(f"Problem: {problem}")
    print(f"\nSolution:\n{response}")
    print()


def code_generation_example():
    """
    Example 5: Code Generation with Specific Requirements
    
    This demonstrates using prompts for code generation.
    """
    print("=" * 60)
    print("Example 5: Code Generation")
    print("=" * 60)
    
    prompt_template = """
You are an expert Python developer.

Task: Write a Python function with the following specifications:

Requirements:
{requirements}

Provide only the function code with docstring. Do not include explanations.

Function:
"""
    
    prompt = PromptTemplate.from_template(prompt_template)
    llm = Ollama(model="llama2")
    chain = prompt | llm | StrOutputParser()
    
    requirements = """
- Function name: calculate_average
- Takes a list of numbers as input
- Returns the average of those numbers
- Handles empty lists by returning 0
- Include type hints
"""
    
    response = chain.invoke({"requirements": requirements})
    
    print("Requirements:")
    print(requirements)
    print("\nGenerated Code:")
    print(response)
    print()


def main():
    """
    Main function to run all examples.
    
    Note: Make sure you have Ollama installed and the llama2 model pulled:
    - Install Ollama: https://ollama.ai
    - Pull model: ollama pull llama2
    """
    print("\n" + "=" * 60)
    print("PROMPT ENGINEERING WITH LANGCHAIN AND OLLAMA")
    print("=" * 60 + "\n")
    
    try:
        # Run all examples
        simple_translation_example()
        data_analyst_example()
        few_shot_sentiment_example()
        chain_of_thought_example()
        code_generation_example()
        
        print("=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure Ollama is installed: https://ollama.ai")
        print("2. Pull the llama2 model: ollama pull llama2")
        print("3. Ensure Ollama service is running")
        print("4. Install required packages: pip install langchain langchain-community")


if __name__ == "__main__":
    main()
