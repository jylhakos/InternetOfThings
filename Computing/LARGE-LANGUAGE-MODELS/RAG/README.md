# Retrieval-Augmented Generation (RAG)

## Table of Contents

- [What is Retrieval Augmented Generation (RAG)?](#what-is-retrieval-augmented-generation-rag)
- [What is LlamaIndex?](#what-is-llamaindex)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Installation](#installation)
- [Creating AI Agents with RAG](#creating-ai-agents-with-rag)
- [Testing AI Agents](#testing-ai-agents)
- [RAG Evaluation](#rag-evaluation)
- [Running Local Infrastructure](#running-local-infrastructure)
- [References](#references)

## What is Retrieval Augmented Generation (RAG)?

**Retrieval Augmented Generation (RAG)** is a technique that enhances Large Language Models (LLMs) by providing them with relevant external information retrieved from a knowledge base. Instead of relying solely on the knowledge encoded in the model's parameters during training, RAG systems dynamically retrieve contextual information from external sources to generate more accurate, up-to-date, and factual responses.

A basic RAG setup includes:
- **Embedding Model**: Converts text into vector representations
- **Vector Database**: Stores and retrieves document embeddings efficiently
- **LLM**: Generates responses based on retrieved context

The vector database is used to find the top-K documents that match the query. The retrieved documents are then provided to the LLM as context to generate accurate answers.

An example agent prints its thought process and decides which tool (weather API or RAG knowledge base) is appropriate for each question before providing an answer.

## What is LlamaIndex?

**LlamaIndex** is an industry-standard framework for building Retrieval-Augmented Generation (RAG) applications. It simplifies data ingestion, indexing, and retrieval, allowing developers to create sophisticated RAG pipelines in few lines of code, making it ideal for connecting private data to LLMs.

LlamaIndex is specialized in:
- **Data Ingestion**: Loading data from various sources (PDFs, APIs, databases)
- **Indexing**: Creating efficient vector indices for semantic search
- **Retrieval**: Finding the most relevant documents for a given query
- **Query Engines**: Combining retrieval with LLM generation

## Project Structure

```
RAG/
├── README.md                  # This file - RAG overview and setup
├── .gitignore                 # Git ignore patterns
├── .env                       # Environment variables (API keys)
├── venv/                      # Python virtual environment
├── LlamaIndex/                # LlamaIndex-specific examples
│   └── README.md              # LlamaIndex detailed documentation
├── src/                       # Source code
│   ├── __init__.py
│   ├── agent.py               # AI agent implementation
│   ├── weather_tool.py        # Weather API tool
│   └── rag_pipeline.py        # RAG setup and indexing
├── tests/                     # Test files
│   ├── __init__.py
│   ├── test_agent.py          # Agent tests
│   └── test_rag.py            # RAG retrieval tests
└── data/                      # Knowledge base documents
    └── sample_data.txt        # Sample documents for RAG
```

## Prerequisites

- **Python 3.9+**: Ensure Python is installed on your system
- **Git**: For version control
- **Docker** (optional): For running local vector databases and LLM inference servers

To check your Python version:
```bash
python --version
```

## Environment Setup

### Step 1: Create Virtual Environment

A virtual environment isolates your project dependencies from the global Python installation.

```bash
# Navigate to the RAG directory
cd "LARGE-LANGUAGE-MODELS/RAG"

# Create a virtual environment named 'venv'
python -m venv venv
```

### Step 2: Activate Virtual Environment

**On Linux/macOS:**
```bash
source venv/bin/activate
```

**On Windows:**
```cmd
venv\Scripts\activate
```

After activation, your terminal prompt should show `(venv)` prefix.

### Step 3: Verify Activation

```bash
which python  # Should point to venv/bin/python
python --version
```

## Installation

### Install Core Dependencies

With the virtual environment activated, install the required packages:

```bash
# Upgrade pip
pip install --upgrade pip

# Install LlamaIndex and core dependencies
pip install llama-index llama-index-llms-openai python-dotenv requests

# Install testing framework
pip install pytest pytest-asyncio

# Install DeepEval for RAG evaluation
pip install deepeval

# Install vector database client (Chroma)
pip install chromadb

# Install additional utilities
pip install python-dotenv
```

### Create Requirements File

Save your dependencies for reproducibility:

```bash
pip freeze > requirements.txt
```

To install from requirements file later:
```bash
pip install -r requirements.txt
```

## Creating AI Agents with RAG

Building an AI agent with LlamaIndex that combines Retrieval-Augmented Generation (RAG) and an external weather forecast API involves creating an agent capable of using specific tools. The agent intelligently decides whether to use its internal knowledge base (RAG) or call the weather API based on the user's query.

### Setting Up API Keys

Create a `.env` file in the project root:

```env
# .env file
OPENAI_API_KEY="your_openai_api_key"
OPENWEATHER_API_KEY="your_openweathermap_api_key"
```

Never commit this file to version control!

### Defining the Weather Tool

Create a Python function that calls the OpenWeather API and define it as a LlamaIndex FunctionTool:

```python
import requests
import os
from llama_index.core.tools import FunctionTool

def get_weather(location: str) -> str:
    """Useful for getting the weather for a given location."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Weather API key not found."
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data.get("cod") == 200:
            weather_desc = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            return f"The weather in {location} is {weather_desc} with a temperature of {temp}°C."
        else:
            return f"Could not retrieve weather for {location}"
    except requests.exceptions.RequestException as e:
        return f"Error connecting to weather API: {e}"

# Wrap as LlamaIndex tool
weather_tool = FunctionTool.from_defaults(fn=get_weather)
```

### Setting Up the RAG Pipeline

Create a knowledge base for the agent:

```python
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import QueryEngineTool
from dotenv import load_dotenv

load_dotenv()

# Configure LLM
Settings.llm = OpenAI(model="gpt-4o", temperature=0)

# Load documents from data directory
documents = SimpleDirectoryReader("./data").load_data()

# Create vector index
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

# Wrap as tool for the agent
rag_tool = QueryEngineTool.from_defaults(
    query_engine=query_engine,
    name="DocumentationTool",
    description="Useful for answering questions about LlamaIndex documentation and internal knowledge."
)
```

### Creating the Agent

Combine the RAG tool and weather tool into a ReActAgent:

```python
from llama_index.core.agent import ReActAgent

# Initialize agent with both tools
agent = ReActAgent.from_tools(
    [weather_tool, rag_tool],
    llm=OpenAI(model="gpt-4o", temperature=0),
    verbose=True  # Shows agent's thought process
)

# Example usage
response_weather = agent.chat("What's the weather like in Tokyo?")
print(f"Agent Response: {response_weather}")

response_rag = agent.chat("What are the main features of LlamaIndex for RAG?")
print(f"Agent Response: {response_rag}")
```

### Is a Vector Database Needed?

**Yes**, a vector database is essential for the RAG component of this example. Here's why:

1. **Efficient Semantic Search**: Vector databases enable fast similarity search over embeddings
2. **Scalability**: Can handle millions of documents efficiently
3. **Persistence**: Store indexed documents for reuse across sessions
4. **Top-K Retrieval**: Quickly find the most relevant documents for a query

In the LlamaIndex example above, `VectorStoreIndex` creates an in-memory vector store by default. For production use, you would connect to a persistent vector database like Chroma, Weaviate, or Qdrant.

## Testing AI Agents

### How to Create AI Agent Tests?

Testing AI agents requires a different approach than traditional software testing due to the non-deterministic nature of LLMs.

### Why is Testing AI Agents with RAG Challenging?

Testing AI agents with Retrieval-Augmented Generation (RAG) presents unique challenges that differ fundamentally from traditional software testing:

#### 1. Non-Deterministic Outputs

Unlike traditional functions that return the same output for the same input, LLMs generate different responses each time, even with identical queries. This makes traditional assertion-based testing (`assert output == expected`) impossible.

**Challenge**: How do you verify correctness when there's no single "right answer"?

**Solution**: Use semantic similarity metrics and quality thresholds instead of exact matching.

#### 2. Multiple Components to Test

RAG systems have several interconnected components that must work together:
- **Document Retrieval**: Is the right context being retrieved?
- **Embedding Quality**: Are embeddings capturing semantic meaning?
- **LLM Generation**: Is the generated response accurate and relevant?
- **Tool Selection**: Does the agent choose the appropriate tool?

**Challenge**: A failure could occur in any component, making debugging complex.

**Solution**: Test each component independently and then test integration.

#### 3. Subjective Quality Measures

Traditional software has objective correctness (passes or fails), but RAG systems have subjective quality dimensions:
- Relevance: Does the answer address the question?
- Faithfulness: Is it true to the source documents?
- Coherence: Is it well-structured and readable?
- Completeness: Does it cover all important points?

**Challenge**: Quality is context-dependent and hard to measure objectively.

**Solution**: Use specialized evaluation metrics (Answer Relevancy, Faithfulness, Groundedness).

#### 4. Context-Dependent Correctness

The "correct" answer depends on:
- The retrieved documents (retrieval quality)
- The query phrasing
- The conversation history
- The domain and use case

**Challenge**: Same question, different contexts = different valid answers.

**Solution**: Test with diverse scenarios and use retrieval context as part of test cases.

#### 5. No Ground Truth

Unlike supervised ML where you have labeled data, RAG systems often operate on novel queries without predefined correct answers.

**Challenge**: What do you compare the output against?

**Solution**: Use reference-free metrics or manually curated test cases with human evaluation.

#### 6. Hallucination Risks

LLMs can generate plausible-sounding but factually incorrect information not present in the source documents.

**Challenge**: Detecting when the model "makes things up" requires verifying claims against source documents.

**Solution**: Use faithfulness and groundedness metrics to detect hallucinations.

#### 7. Emergent Behaviors

Agents can exhibit unexpected behaviors when combining multiple tools or reasoning through complex queries.

**Challenge**: Can't predict all possible agent behaviors in advance.

**Solution**: Use verbose mode to inspect reasoning, log tool usage, and test edge cases.

#### 8. Performance Variability

Response quality can vary based on:
- LLM model version updates
- Prompt engineering changes
- Vector database index changes
- Retrieved document quality

**Challenge**: Tests that pass today might fail tomorrow due to external changes.

**Solution**: Implement continuous evaluation and monitoring with baseline metrics.

### Why Traditional Unit Tests Aren't Enough

Traditional unit tests work well for deterministic logic:
```python
def add(a, b):
    return a + b

assert add(2, 3) == 5  # ✓ Works great
```

But RAG systems require different approaches:
```python
response = agent.chat("What is LlamaIndex?")
# Can't do: assert response == "LlamaIndex is..."  ✗ Fails due to variability
# Must do: assert relevancy_score(response) > 0.7  ✓ Checks quality instead
```

### The Solution: Specialized Evaluation Frameworks

This is why tools like **DeepEval** are essential for RAG testing. They provide:
- Metrics designed for LLM outputs (relevancy, faithfulness, groundedness)
- Integration with pytest for automated testing
- Threshold-based pass/fail criteria
- Context-aware evaluation

### Setting Up Test Framework

**Step 1: Create Test Directory Structure**

```bash
mkdir -p tests
touch tests/__init__.py
touch tests/test_agent.py
touch tests/test_rag.py
```

**Step 2: Install Testing Dependencies**

```bash
pip install pytest pytest-asyncio
```

### Writing Basic Tests

**tests/test_rag.py** - Basic retrieval test:

```python
import pytest
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex

def test_document_loading():
    """Test that documents can be loaded from data directory."""
    documents = SimpleDirectoryReader("./data").load_data()
    assert len(documents) > 0, "No documents loaded"
    assert hasattr(documents[0], 'text'), "Document missing text attribute"

def test_index_creation():
    """Test that vector index can be created."""
    documents = SimpleDirectoryReader("./data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    assert index is not None, "Index creation failed"

def test_query_engine():
    """Test basic query functionality."""
    documents = SimpleDirectoryReader("./data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    
    response = query_engine.query("What is LlamaIndex?")
    assert response is not None, "Query returned no response"
    assert len(str(response)) > 0, "Response is empty"
```

### Using Pytest Fixtures

Fixtures help mock components and create reusable test setups:

```python
import pytest
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

@pytest.fixture
def sample_index():
    """Fixture that creates a test index."""
    documents = SimpleDirectoryReader("./data").load_data()
    return VectorStoreIndex.from_documents(documents)

def test_with_fixture(sample_index):
    """Test using the fixture."""
    query_engine = sample_index.as_query_engine()
    response = query_engine.query("Test query")
    assert response is not None
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_rag.py

# Run specific test function
pytest tests/test_rag.py::test_document_loading

# Run with coverage report
pytest --cov=src tests/
```

### Pytest File Naming Conventions

- Test files: `test_*.py` or `*_test.py`
- Test functions: `def test_*()`
- Test classes: `class Test*`

Pytest automatically discovers tests following these conventions.

## RAG Evaluation

RAG systems require evaluation metrics beyond traditional unit tests because LLM outputs are non-deterministic. Evaluation frameworks assess the quality of generated answers and retrieved context.

### DeepEval Integration

**DeepEval** provides unit testing for AI agents and LLM-powered applications with pytest integration.

### Key Evaluation Metrics

1. **Answer Relevancy Metric**: Measures how relevant the answer is to the query
2. **Faithfulness Metric**: Checks if the answer is faithful to the retrieved context
3. **Groundedness Metric**: Verifies the answer is grounded in provided facts

### Types of Metrics Used in This Example

DeepEval provides several types of metrics to evaluate LlamaIndex RAG applications. This example demonstrates:

#### 1. Answer Relevancy Metric
- **Purpose**: Evaluates whether the generated answer directly addresses the user's query
- **How it works**: Compares the semantic similarity between the question and the answer
- **Use case**: Ensures the agent provides relevant responses and doesn't go off-topic
- **Threshold**: Typically set to 0.7 or higher for production systems

#### 2. Faithfulness Metric
- **Purpose**: Measures if the answer is faithful to the retrieved context (no hallucinations)
- **How it works**: Checks if claims in the answer can be traced back to the retrieved documents
- **Use case**: Prevents the LLM from making up information not present in the source documents
- **Critical for**: Ensuring factual accuracy in RAG applications

#### 3. Groundedness Metric (Contextual Relevancy)
- **Purpose**: Verifies that the answer is grounded in the provided facts and context
- **How it works**: Evaluates how well the retrieved context supports the generated answer
- **Use case**: Ensures the retrieval system fetched relevant documents
- **Helps identify**: Issues with document retrieval or embedding quality

#### Additional Metrics Available

While not shown in the basic example, DeepEval also supports:

- **Contextual Precision**: Measures if irrelevant context was retrieved
- **Contextual Recall**: Checks if all relevant information was retrieved
- **Hallucination Score**: Detects fabricated information
- **Toxicity**: Identifies harmful or inappropriate content
- **Bias**: Detects biased responses
- **RAGAS Metrics**: Research-grade RAG assessment metrics

#### Why These Metrics Matter

Traditional unit tests check if code functions correctly, but RAG systems require evaluation of:
- **Quality**: Is the answer good enough?
- **Relevance**: Does it answer the question?
- **Accuracy**: Is it factually correct based on source documents?
- **Consistency**: Does it perform well across different queries?

DeepEval integrates seamlessly with pytest, allowing you to set thresholds and automatically fail tests if quality drops below acceptable levels.

### Installation

```bash
pip install deepeval
```

### Example: Using DeepEval with LlamaIndex

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from deepeval.integrations.llama_index import DeepEvalAnswerRelevancyEvaluator

# Load and index documents
documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)
rag_application = index.as_query_engine()

# Query the RAG system
user_input = "What is LlamaIndex?"
response_object = rag_application.query(user_input)

# Evaluate the response
evaluator = DeepEvalAnswerRelevancyEvaluator()
evaluation_result = evaluator.evaluate_response(
    query=user_input,
    response=response_object
)

print(f"Relevancy Score: {evaluation_result.score}")
```

### Pytest with DeepEval

```python
import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

def test_answer_relevancy():
    """Test that RAG answers are relevant to queries."""
    answer_relevancy_metric = AnswerRelevancyMetric(threshold=0.7)
    
    test_case = LLMTestCase(
        input="What is LlamaIndex?",
        actual_output="LlamaIndex is a framework for building RAG applications.",
        retrieval_context=["LlamaIndex documentation about RAG frameworks"]
    )
    
    assert_test(test_case, [answer_relevancy_metric])
```

### DeepEval Usage: Standalone vs. Integrated with Pytest

The examples above demonstrate **two different approaches** for using DeepEval to evaluate RAG applications:

#### Approach 1: DeepEval Standalone

The first example shows DeepEval used independently:

```python
from deepeval.integrations.llama_index import DeepEvalAnswerRelevancyEvaluator

evaluator = DeepEvalAnswerRelevancyEvaluator()
evaluation_result = evaluator.evaluate_response(query=user_input, response=response_object)
print(f"Relevancy Score: {evaluation_result.score}")
```

**Use this approach for:**
- Quick one-off evaluations and debugging
- Interactive experimentation during development
- Manual quality checks of specific responses
- Ad-hoc testing in Jupyter notebooks or scripts

#### Approach 2: DeepEval Integrated with Pytest (Recommended)

The second example shows DeepEval integrated with pytest:

```python
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric

def test_answer_relevancy():
    answer_relevancy_metric = AnswerRelevancyMetric(threshold=0.7)
    test_case = LLMTestCase(input="...", actual_output="...", retrieval_context=["..."])
    assert_test(test_case, [answer_relevancy_metric])
```

**Use this approach for:**
- **Automated Testing**: Tests run automatically as part of your test suite
- **Pass/Fail Thresholds**: Tests fail if quality drops below acceptable levels
- **CI/CD Integration**: Integrate into continuous integration pipelines
- **Reproducibility**: Consistent evaluation across development cycles
- **Multiple Metrics**: Test multiple quality aspects in one test suite
- **Regression Detection**: Catch quality degradation early

#### Recommended Approach: Use Both Together

The most effective strategy combines both approaches:

1. **During Development**: Use standalone DeepEval for quick feedback and experimentation
2. **In Test Suite**: Use pytest integration for automated quality gates
3. **In Production Monitoring**: Use standalone DeepEval to log evaluation metrics

This dual approach ensures both development velocity and production quality assurance.

## Running Local Infrastructure

### Chroma Vector Database with Docker

Run Chroma locally for persistent vector storage:

```bash
# Pull Chroma image
docker pull chromadb/chroma

# Run Chroma container
docker run -p 8000:8000 chromadb/chroma

# Verify Chroma is running
curl http://localhost:8000/api/v1/heartbeat
```

### Connecting LlamaIndex to Chroma

```python
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex, StorageContext

# Connect to Chroma
chroma_client = chromadb.HttpClient(host="localhost", port=8000)
chroma_collection = chroma_client.create_collection("my_collection")

# Create vector store
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Create index with persistent storage
index = VectorStoreIndex.from_documents(
    documents, 
    storage_context=storage_context
)
```

### Local LLM Inference with Docker

Run quantized open-source models locally using Ollama:

```bash
# Pull Ollama image
docker pull ollama/ollama

# Run Ollama container
docker run -d -p 11434:11434 --name ollama ollama/ollama

# Pull a model (e.g., Llama 2)
docker exec -it ollama ollama pull llama2

# Test the model
curl http://localhost:11434/api/generate -d '{
  "model": "llama2",
  "prompt": "What is RAG?"
}'
```

### Using Ollama with LlamaIndex

```python
from llama_index.llms.ollama import Ollama

# Configure local LLM
llm = Ollama(model="llama2", request_timeout=120.0)

# Use in LlamaIndex
Settings.llm = llm
```

## References

### LlamaIndex Resources
- [LlamaIndex GitHub Repository](https://github.com/run-llama/llama_index)
- [LlamaIndex Documentation](https://developers.llamaindex.ai/)
- [Unit Testing LLMs/RAG With DeepEval](https://developers.llamaindex.ai/python/framework/community/integrations/deepeval/)
- [LlamaIndex RAG Guide](https://developers.llamaindex.ai/python/framework/tutorials/quickstart/)

### Testing & Evaluation
- [Pytest Documentation](https://docs.pytest.org/)
- [DeepEval GitHub Repository](https://github.com/confident-ai/deepeval)
- [DeepEval Documentation](https://docs.confident-ai.com/)
- [DeepEval Getting Started Guide](https://deepeval.com/docs/getting-started)
- [Pytest Fixtures Guide](https://docs.pytest.org/en/stable/fixture.html)

### Python Environment
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [pip Documentation](https://pip.pypa.io/en/stable/)

### Vector Databases
- [Chroma Documentation](https://docs.trychroma.com/)
- [Chroma Docker Hub](https://hub.docker.com/r/chromadb/chroma)

### Local LLM Inference
- [Ollama Documentation](https://ollama.ai/)
- [Ollama Docker Repository](https://hub.docker.com/r/ollama/ollama)

### APIs
- [OpenWeatherMap API](https://openweathermap.org/api)
- [OpenAI API Documentation](https://platform.openai.com/docs/)

---

**Next Steps**: Check the [LlamaIndex folder](./LlamaIndex/README.md) for detailed examples and implementations of AI agents with RAG.
