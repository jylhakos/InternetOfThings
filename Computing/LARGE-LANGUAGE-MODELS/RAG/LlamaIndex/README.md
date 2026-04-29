# AI Agents with LlamaIndex

This folder contains examples and implementations of AI agents built with LlamaIndex, focusing on Retrieval-Augmented Generation (RAG) capabilities.

## Table of Contents

- [Overview](#overview)
- [What is LlamaIndex?](#what-is-llamaindex)
- [AI Agents with RAG](#ai-agents-with-rag)
- [Architecture](#architecture)
- [Implementation Examples](#implementation-examples)
- [Advanced Features](#advanced-features)
- [References](#references)

## Overview

This directory demonstrates how to build intelligent AI agents that combine:
- **Retrieval-Augmented Generation (RAG)**: Access to a knowledge base through vector search
- **External Tools**: Integration with APIs (e.g., weather, databases)
- **Reasoning**: LLM-powered decision-making to choose appropriate tools

## What is LlamaIndex?

**LlamaIndex** is an industry-standard framework for building Retrieval-Augmented Generation (RAG) applications. It is specialized in:

### Core Capabilities

1. **Data Ingestion**
   - Load data from 100+ sources (PDFs, databases, APIs, web pages)
   - Parse structured and unstructured data
   - Handle multiple document formats

2. **Indexing**
   - Create vector embeddings for semantic search
   - Support for multiple index types (vector, keyword, knowledge graph)
   - Efficient storage and retrieval structures

3. **Retrieval**
   - Semantic search using embeddings
   - Hybrid search (combining vector and keyword search)
   - Top-K retrieval with relevance scoring

4. **Query Engines**
   - Combine retrieval with LLM generation
   - Context-aware response synthesis
   - Multi-step reasoning over documents

### Why LlamaIndex for RAG?

- **Simplicity**: Create sophisticated RAG pipelines in just a few lines of code
- **Private Data**: Easily connect proprietary data to LLMs
- **Flexibility**: Support for multiple LLMs, embedding models, and vector stores
- **Production-Ready**: Battle-tested in enterprise applications

## AI Agents with RAG

AI agents in LlamaIndex are autonomous systems that can:
1. **Understand user queries** through natural language processing
2. **Reason about which tool to use** (RAG knowledge base vs. external APIs)
3. **Execute actions** by calling appropriate tools
4. **Generate responses** by synthesizing information from multiple sources

### Agent Types

LlamaIndex supports several agent architectures:

#### ReActAgent (Reasoning + Acting)
- Uses chain-of-thought reasoning
- Decides tool usage step-by-step
- Transparent thought process

```python
from llama_index.core.agent import ReActAgent

agent = ReActAgent.from_tools(
    [rag_tool, weather_tool, calculator_tool],
    llm=llm,
    verbose=True
)
```

#### OpenAIAgent
- Leverages OpenAI's function calling
- Efficient tool selection
- Optimized for OpenAI models

```python
from llama_index.agent.openai import OpenAIAgent

agent = OpenAIAgent.from_tools(
    tools=[rag_tool, weather_tool],
    llm=OpenAI(model="gpt-4")
)
```

## Architecture

### High-Level Flow

```
User Query → Agent → Tool Selection → Tool Execution → Response Generation
                ↓
         [RAG Tool, Weather Tool, Custom Tools]
                ↓
    [Vector DB, APIs, Functions]
```

### RAG Component Architecture

```
Documents → Embedding Model → Vector Store
                                    ↓
User Query → Embedding → Similarity Search → Top-K Documents
                                                    ↓
                              LLM (with context) → Response
```

## Implementation Examples

### Example 1: Basic RAG Agent

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import QueryEngineTool
from llama_index.llms.openai import OpenAI

# Load and index documents
documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

# Create RAG tool
rag_tool = QueryEngineTool.from_defaults(
    query_engine=query_engine,
    name="knowledge_base",
    description="Useful for questions about company documentation"
)

# Create agent
agent = ReActAgent.from_tools(
    [rag_tool],
    llm=OpenAI(model="gpt-4"),
    verbose=True
)

# Query the agent
response = agent.chat("What is our company's return policy?")
print(response)
```

### Example 2: Multi-Tool Agent (RAG + External API)

```python
import requests
from llama_index.core.tools import FunctionTool

# Define weather tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    
    if data.get("cod") == 200:
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        return f"{city}: {temp}°C, {desc}"
    return f"Could not get weather for {city}"

weather_tool = FunctionTool.from_defaults(fn=get_weather)

# Create multi-tool agent
agent = ReActAgent.from_tools(
    [rag_tool, weather_tool],
    llm=OpenAI(model="gpt-4"),
    verbose=True
)

# The agent chooses the right tool
print(agent.chat("What's the weather in Paris?"))  # Uses weather_tool
print(agent.chat("What is LlamaIndex?"))           # Uses rag_tool
```

### Example 3: Agent with Custom Tool

```python
def calculate_mortgage(principal: float, rate: float, years: int) -> str:
    """Calculate monthly mortgage payment."""
    monthly_rate = rate / 100 / 12
    num_payments = years * 12
    payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / \
              ((1 + monthly_rate)**num_payments - 1)
    return f"Monthly payment: ${payment:.2f}"

mortgage_tool = FunctionTool.from_defaults(fn=calculate_mortgage)

agent = ReActAgent.from_tools(
    [rag_tool, mortgage_tool],
    llm=OpenAI(model="gpt-4"),
    verbose=True
)

response = agent.chat("Calculate mortgage for $300,000 at 4.5% for 30 years")
```

## Advanced Features

### 1. Persistent Vector Storage

Use Chroma or other vector databases for persistence:

```python
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex, StorageContext

# Connect to Chroma
chroma_client = chromadb.HttpClient(host="localhost", port=8000)
chroma_collection = chroma_client.get_or_create_collection("company_docs")

vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Create or load index
index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context
)
```

### 2. Custom Retrieval Strategies

```python
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine

# Configure retriever
retriever = VectorIndexRetriever(
    index=index,
    similarity_top_k=5,  # Return top 5 documents
)

# Create custom query engine
query_engine = RetrieverQueryEngine(retriever=retriever)
```

### 3. Response Synthesis Modes

```python
# Different synthesis strategies
query_engine = index.as_query_engine(
    response_mode="tree_summarize"  # Options: refine, compact, tree_summarize
)
```

### 4. Streaming Responses

```python
# Stream agent responses
response = agent.stream_chat("Explain LlamaIndex RAG architecture")
for token in response.response_gen:
    print(token, end="")
```

### 5. Agent Memory

```python
from llama_index.core.memory import ChatMemoryBuffer

memory = ChatMemoryBuffer.from_defaults(token_limit=3000)

agent = ReActAgent.from_tools(
    [rag_tool, weather_tool],
    llm=llm,
    memory=memory,
    verbose=True
)

# Agent remembers conversation history
agent.chat("What's the weather in Tokyo?")
agent.chat("What about yesterday?")  # References previous query
```

### 6. Evaluation and Monitoring

```python
from deepeval.integrations.llama_index import DeepEvalAnswerRelevancyEvaluator

evaluator = DeepEvalAnswerRelevancyEvaluator()

# Evaluate response quality
user_input = "What is LlamaIndex?"
response = agent.chat(user_input)

evaluation = evaluator.evaluate_response(
    query=user_input,
    response=response
)

print(f"Relevancy Score: {evaluation.score}")
```

## References

### Official Documentation
- [LlamaIndex GitHub](https://github.com/run-llama/llama_index)
- [LlamaIndex Docs](https://developers.llamaindex.ai/)
- [Agent Guide](https://developers.llamaindex.ai/python/framework/module_guides/deploying/agents/)
- [RAG Quickstart](https://developers.llamaindex.ai/python/framework/tutorials/quickstart/)

### Integration Guides
- [Vector Store Integrations](https://developers.llamaindex.ai/python/framework/module_guides/storing/vector_stores/)
- [LLM Integrations](https://developers.llamaindex.ai/python/framework/module_guides/models/llms/)
- [DeepEval Integration](https://developers.llamaindex.ai/python/framework/community/integrations/deepeval/)

### Tutorials
- [Building Production RAG](https://developers.llamaindex.ai/python/framework/guides/rag/)
- [Multi-Modal RAG](https://developers.llamaindex.ai/python/framework/guides/multimodal/)
- [Agent Examples](https://developers.llamaindex.ai/python/framework/examples/agent/)

### Community
- [Discord Community](https://discord.gg/llamaindex)
- [Twitter/X](https://twitter.com/llama_index)

---

**Parent Documentation**: See [RAG folder README](../README.md) for setup instructions and environment configuration.