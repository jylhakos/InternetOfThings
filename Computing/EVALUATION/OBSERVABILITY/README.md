# AI Agent & LLM Observability

This repository explores observability tools, metrics, and best practices for Large Language Models (LLMs) and AI agents across local and cloud deployments.

---

## Table of Contents

1. [Introduction](#introduction)
2. [What is Observability?](#what-is-observability)
3. [What is AI Agent Observability?](#what-is-ai-agent-observability)
4. [Traditional Observability vs Agent Observability](#traditional-observability-vs-agent-observability)
5. [Components of AI Agent Observability](#components-of-ai-agent-observability)
6. [Aspects of Agent Observability](#aspects-of-agent-observability)
7. [Open Source Tools for AI Agent Observability](#open-source-tools-for-ai-agent-observability)
8. [Tool Comparison Table](#tool-comparison-table)
9. [How to Monitor AI Agent Performance](#how-to-monitor-ai-agent-performance)
10. [Evaluation Methods](#evaluation-methods)
    - [Phase 1: Manual Tracing](#phase-1--manual-tracing)
    - [Phase 2: Online Evaluation](#phase-2--online-evaluation)
    - [Phase 3: Offline Evaluation](#phase-3--offline-evaluation)
11. [Testing vs Evaluation](#testing-vs-evaluation)
12. [Azure Foundry Observability](#azure-foundry-observability)
13. [Setup Instructions](#setup-instructions)
    - [Local Linux Setup](#local-linux-setup)
    - [Cloud Provider Setup](#cloud-provider-setup)
14. [Practical Example: Agent Evaluation with LangGraph](#practical-example-agent-evaluation-with-langgraph)
15. [Running Tests in CI/CD](#running-tests-in-cicd)
16. [Project Structure](#project-structure)
17. [References](#references)

---

## Introduction

Observability is essential for understanding, debugging, and optimizing AI systems. As AI agents become more autonomous and complex, traditional monitoring approaches are insufficient. This guide covers modern observability practices, tools, and techniques specifically designed for LLMs and AI agents.

---

## What is Observability?

**AI observability** refers to the ability to monitor, understand, and troubleshoot AI systems throughout their lifecycle. It transforms AI from a "black box" into a transparent system by collecting and analyzing telemetry data—logs, traces, and metrics—to understand the internal reasoning, actions, and tool usage of autonomous systems.

Observability enables:
- Real-time monitoring of AI system behavior
- Debugging non-deterministic outputs
- Performance tracking and optimization
- Quality assurance and compliance
- Root cause analysis of failures

---

## What is AI Agent Observability?

**Agent observability** is the practice of achieving deep, actionable visibility into the internal workings, decisions, and outcomes of AI agents throughout their lifecycle—from development and testing to deployment and ongoing operation.

Key aspects include:

- **Continuous Monitoring**: Tracking agent actions, decisions, and interactions in real time to surface anomalies, unexpected behaviors, or performance drift
- **Tracing**: Capturing detailed execution flows, including how agents reason through tasks, select tools, and collaborate with other agents or services
- **Logging**: Recording agent decisions, tool calls, and internal state changes to support debugging and behavior analysis
- **Evaluation**: Systematically assessing agent outputs for quality, safety, compliance, and alignment with user intent
- **Governance**: Enforcing policies and standards to ensure agents operate ethically, safely, and in accordance with organizational and regulatory requirements

---

## Traditional Observability vs Agent Observability

### Traditional Observability

Traditional observability relies on three foundational pillars:
- **Metrics**: Quantitative measurements (CPU, memory, latency, throughput)
- **Logs**: Event records and system messages
- **Traces**: Request flow through distributed systems

These are well-suited for conventional software systems where the focus is on infrastructure health, latency, and throughput.

### Agent Observability

AI agents are **non-deterministic** and introduce new dimensions that require an advanced observability framework:

- **Autonomy**: Agents make independent decisions
- **Reasoning**: Multi-step thought processes and planning
- **Dynamic Decision Making**: Context-dependent behavior
- **Tool Usage**: Integration with external APIs and services
- **Prompt Sensitivity**: Output variance based on prompt engineering
- **Quality Metrics**: Accuracy, hallucinations, groundedness, relevance

Agent observability extends beyond traditional metrics to include behavioral, operational, and decisional insights.

---

## Components of AI Agent Observability

Agent observability covers three main areas:

### 1. Behavioral Observability
Tracking what actions the agent takes, in what order, and how often:
- Action sequences and decision trees
- Tool selection patterns
- Retry and error handling behaviors
- Multi-agent collaboration patterns

### 2. Operational Observability
Monitoring how well the agent performs:
- **Latency**: Response time for requests
- **Uptime**: System availability
- **Resource Usage**: Token consumption, API calls, compute costs
- **Error Rates**: Failed requests and exceptions
- **Throughput**: Requests processed per unit time

### 3. Decisional Observability
Providing insight into why the agent made certain choices:
- Reasoning chains and thought processes
- Data sources used for decisions
- Prompt interpretation and understanding
- Confidence scores and uncertainty metrics
- Explanation generation

---

## Aspects of Agent Observability

### 1. Tracing & Debugging
Visualizing multi-step agent actions to understand decision-making:
- End-to-end trace visualization
- Step-by-step execution flow
- Tool call sequences
- Intermediate reasoning steps
- Error propagation paths

### 2. Performance Metrics
Measuring operational efficiency:
- **Latency**: Time to first token, total response time
- **Cost per Request**: Token usage, API call costs
- **Accuracy**: Correctness of outputs
- **Success Rate**: Task completion percentage
- **Token Efficiency**: Output quality per token

### 3. Evaluation
Assessing prompt quality and model outputs:
- **Accuracy/Correctness**: Factual accuracy of responses
- **Hallucination Detection**: Identifying fabricated information
- **Groundedness**: Alignment with source documents (RAG)
- **Relevance**: Response appropriateness to query
- **Coherence**: Logical consistency and flow
- **Fluency**: Natural language quality
- **Safety**: Absence of harmful content

### 4. Prompt Management
Tracking changes in prompts to analyze their impact:
- Version control for prompts
- A/B testing different prompts
- Prompt performance analytics
- Template management
- Prompt optimization insights

---

## Open Source Tools for AI Agent Observability

### 1. **Langfuse** (MIT License)
An open-source LLM engineering platform that excels in tracing, prompt management, and metrics evaluation.

**Key Features**:
- Native integration with LangChain and LlamaIndex
- Tracing and observability
- Prompt versioning and management
- Dataset creation and experimentation
- LLM-as-a-Judge evaluators
- Self-hostable

**Use Case**: All-in-one platform for development, testing, and production monitoring

**Links**:
- Website: [https://langfuse.com/](https://langfuse.com/)
- GitHub: [https://github.com/langfuse/langfuse](https://github.com/langfuse/langfuse)

---

### 2. **Arize Phoenix** (Apache 2.0 / ELv2)
An open-source observability platform designed for tracing, evaluation, and prompt analysis.

**Key Features**:
- Local-first RAG observability
- Native integration with LlamaIndex and LangChain
- Real-time tracing
- Embedding analysis and visualization
- Drift detection

**Use Case**: Local development with strong RAG evaluation capabilities

**Links**:
- Website: [https://phoenix.arize.com/](https://phoenix.arize.com/)
- Docs: [https://docs.arize.com/phoenix](https://docs.arize.com/phoenix)

---

### 3. **Helicone** (Apache 2.0)
A proxy-based tool providing 1-line integration for monitoring, caching, and rate-limiting.

**Key Features**:
- Low-latency proxy architecture
- Minimal code changes required
- Request caching
- Rate limiting
- Cost tracking

**Use Case**: Quick integration with minimal overhead for production APIs

**Links**:
- Website: [https://www.helicone.ai/](https://www.helicone.ai/)

---

### 4. **Opik** (by Comet)
Open-source platform for evaluating, testing, and monitoring LLM applications and agents.

**Key Features**:
- Experiment tracking
- Prompt versioning
- Evaluation metrics
- Integration with Comet ML

**Use Case**: Teams already using Comet ML for ML experimentation

---

### 5. **Promptfoo** (MIT License)
Focused on testing and evaluating prompts and models through CLI.

**Key Features**:
- CLI-based prompt testing
- Automated prompt evaluation
- Regression testing
- Multiple model comparison

**Use Case**: Prompt quality assurance and continuous testing

**Links**:
- Website: [https://www.promptfoo.dev/](https://www.promptfoo.dev/)

---

### 6. **DeepEval** (MIT License)
An open-source framework designed to test and monitor RAG and AI agent performance.

**Key Features**:
- RAG-specific evaluation metrics
- Agent performance testing
- Automated testing framework
- G-Eval methodology

**Use Case**: RAG and agent testing

**Links**:
- GitHub: [https://github.com/confident-ai/deepeval](https://github.com/confident-ai/deepeval)

---

### 7. **AgentWatch**
A specialized, free, open-source tool for real-time monitoring and analysis of AI agent behaviors.

**Key Features**:
- Real-time agent monitoring
- Behavior pattern analysis
- Anomaly detection

**Use Case**: Specialized agent behavior monitoring

---

### 8. **OpenLLMetry** (Apache 2.0)
Built on OpenTelemetry, it enables tracing of agentic applications to monitor LLM interactions.

**Key Features**:
- OpenTelemetry standard compliance
- Distributed tracing
- Integration with existing observability stacks
- Vendor-neutral

**Use Case**: Organizations using OpenTelemetry infrastructure

**Links**:
- GitHub: [https://github.com/traceloop/openllmetry](https://github.com/traceloop/openllmetry)

---

### 9. **TruLens** (MIT License)
Observability and evaluation framework with RAG Triad metrics.

**Key Features**:
- RAG Triad evaluation (Context Relevance, Groundedness, Answer Relevance)
- Integration with LlamaIndex
- Custom feedback functions

**Use Case**: RAG application evaluation and optimization

**Links**:
- Website: [https://www.trulens.org/](https://www.trulens.org/)

---

### 10. **Lunary** (Apache 2.0)
Lightweight observability and prompt management platform.

**Key Features**:
- Observability for RAG pipelines
- Prompt management
- Chatbot analytics
- Freemium model

**Use Case**: Lightweight RAG and chatbot observability

**Links**:
- Website: [https://lunary.ai/](https://lunary.ai/)

---

### 11. **Hugging Face Observer**
An open-source Python SDK for lightweight AI observability, specifically for tracking Generative AI API interactions.

**Key Features**:
- Wrapper around LLM API calls
- Records input, output, latency, and model details
- OpenTelemetry integration
- Compatible with Hugging Face models

**Use Case**: Observability for Hugging Face inference endpoints

**Links**:
- Blog: [https://huggingface.co/blog/davidberenstein1957/observers-a-lightweight-sdk-for-ai-observability](https://huggingface.co/blog/davidberenstein1957/observers-a-lightweight-sdk-for-ai-observability)
- GitHub: [https://github.com/cfahlgren1/observers](https://github.com/cfahlgren1/observers)

---

## Tool Comparison Table

| Tool | Focus | Pricing | Open Source | Integration | Best For |
|------|-------|---------|-------------|-------------|----------|
| **Langfuse** | LLM Engineering Platform | Freemium (from $0/mo) | Yes (MIT) | Native | All-in-one observability, prompts, and evaluations |
| **Arize Phoenix** | AI Observability & Evaluation | Freemium (from $0/mo) | Yes (ELv2) | Native | Local-first RAG observability and evaluation |
| **Helicone** | LLM Observability & AI Gateway | Freemium (from $0/mo) | Yes (Apache-2.0) | Native | Low-latency proxy for observability and caching |
| **TruLens** | Observability & Evaluation | Free (Open Source) | Yes (MIT) | Community | RAG Triad evaluation metrics |
| **Lunary** | Observability & Prompt Management | Freemium (from $0/mo) | Yes (Apache-2.0) | Yes | Lightweight RAG pipeline and chatbot observability |
| **Portkey** | AI Gateway / LLM Routing | Freemium (from $49/mo) | Yes (MIT) | Native | Production gateway with routing and fallbacks |
| **LangSmith** | Debugging & Evals | Paid (from Langchain) | No | Native | An agent debugging and enterprise features |
| **Datadog LLM** | Unified Infrastructure & LLM | Paid (Datadog pricing) | No | Native | Unified infrastructure and LLM monitoring |

---

## How to Monitor AI Agent Performance

Monitoring AI agent performance requires tracking both technical metrics and the quality of outputs.

### Key Monitoring Techniques

#### 1. Traceability (End-to-End Traces)
Detailed, step-by-step logging of how an agent processes a request from start to finish:
- Initial user query
- Agent reasoning steps
- Tool selection and execution
- API calls and responses
- Intermediate outputs
- Final response generation

**Tools**: Langfuse, Arize Phoenix, LangSmith

#### 2. Quality Metrics (Accuracy/Hallucinations)
Measure if outputs are accurate, relevant, and helpful:
- **Accuracy**: Factual correctness
- **Hallucination Rate**: Frequency of fabricated information
- **Groundedness**: Alignment with source documents (RAG-specific)
- **Relevance**: Response appropriateness
- **Coherence**: Logical consistency

**Tools**: DeepEval, TruLens, LLM-as-a-Judge evaluators

#### 3. Tool/API Usage Efficiency
Monitoring which tools the agent uses and their effectiveness:
- Tool selection frequency
- Tool call success rate
- Tool latency and performance
- API error rates
- Retry patterns

#### 4. Success Rate
Tracking whether the agent completed its high-level objective:
- Task completion rate
- User satisfaction scores
- Goal achievement percentage
- Abandonment rate

**Reference**: [Microsoft AI Agents for Beginners - Production](https://microsoft.github.io/ai-agents-for-beginners/10-ai-agents-production/)

### Monitoring Approaches

#### Continuous Monitoring
Real-time tracking of agent actions using tools that integrate with AI frameworks:
- Live dashboards
- Alert systems
- Anomaly detection
- Real-time metrics

**Integration with**: LangChain, CrewAI, LlamaIndex

#### Online Evaluation
Evaluating the agent in a live environment to detect "model drift":
- Production traffic sampling
- Real-time quality scoring
- Automated flagging of issues
- Continuous feedback loops

#### Human-in-the-Loop (HITL)
Involving humans to review agent actions or flag errors:
- Manual review workflows
- Exception handling
- Quality assurance
- Training data collection

---

## Evaluation Methods

Observability gives us metrics, but **evaluation** is the process of analyzing that data and performing tests to determine how well an AI agent is performing and how it can be improved.

The evaluation process follows a natural progression as your application matures:

### Phase 1 — Manual Tracing

During early development, the most valuable activity is simply **inspecting traces** to understand your agent's reasoning.

**Activities**:
- Review individual request traces
- Understand agent decision-making
- Identify edge cases
- Debug reasoning errors

**Tools**: Langfuse Trace Inspector, LangSmith Trace Viewer

### Phase 2 — Online Evaluation

As you get your first users, implement **user feedback mechanisms** and **automated evaluators** to flag problematic traces in real-time.

**LLM-as-a-Judge** is a powerful way to automatically evaluate agent output:

```python
# Example: Using an LLM to judge response quality
def llm_as_judge(question, answer, context):
    prompt = f"""
    Evaluate the following answer to the question.
    
    Question: {question}
    Answer: {answer}
    Context: {context}
    
    Rate the answer on:
    1. Accuracy (0-100)
    2. Relevance (0-100)
    3. Groundedness (0-100)
    
    Provide scores in JSON format.
    """
    # Call LLM and parse response
    return scores
```

**Benefits**:
- Automated quality checks
- Real-time feedback
- Scales with production traffic
- Identifies drift and anomalies

### Phase 3 — Offline Evaluation

At scale, create **benchmark datasets** of inputs and expected outputs, then run automated experiments to test your agent before each release.

**Dataset Evaluation Process**:

1. **Create Benchmark Dataset**: Collect prompt and expected output pairs
2. **Run Agent on Dataset**: Process all test cases
3. **Compare Results**: Use scoring mechanisms to evaluate outputs
4. **Analyze Performance**: Identify regressions and improvements

**Example Workflow**:
```python
# Pseudocode for offline evaluation
dataset = load_benchmark_dataset()

for test_case in dataset:
    output = agent.run(test_case.input)
    score = evaluate(output, test_case.expected_output)
    results.append(score)

report = generate_evaluation_report(results)
```

**Benefits**:
- Prevents regressions before deployment
- Enables confident iteration
- Comparative analysis of model versions
- Reproducible testing

---

## Testing vs Evaluation

### Traditional Testing
**Testing** typically means running automated checks that produce **pass/fail** results.

Example:
```python
def test_addition():
    assert add(2, 3) == 5  # Deterministic, exact match
```

### LLM Testing Challenge
When you ask an LLM "What is the capital of France?", you might get:
- "Paris"
- "The capital is Paris"
- "Paris, France"
- A longer explanation

All are correct, but none match exactly. This **variability** doesn't mean we can't test LLM applications—it means we need **different testing strategies**.

### Evaluation-Based Testing
In LLM applications, you "test" your application by "evaluating" its outputs with **scoring functions**. A test passes if the evaluation score meets your threshold.

**Components**:
1. **Datasets**: Collections of input/output pairs that represent test cases
2. **Experiment Runners**: Execute your LLM application against the dataset
3. **Evaluators**: Score the outputs programmatically instead of checking exact matches

**Example**:
```python
def test_llm_response_quality():
    response = llm.generate("What is the capital of France?")
    score = semantic_similarity(response, "Paris")
    assert score > 0.8  # Pass if semantically similar
```

---

## Azure Foundry Observability

Microsoft Azure Foundry provides observability for generative AI applications.

**Reference**: [Observability in Generative AI - Azure Foundry](https://learn.microsoft.com/en-us/azure/foundry/concepts/observability)

### Evaluation in Azure Foundry

Evaluators measure the quality, safety, and reliability of AI responses throughout development.

**Built-in Evaluators**:
- **General-Purpose Quality**: Coherence, fluency, similarity
- **RAG-Specific Metrics**: Groundedness, relevance, context precision
- **Safety & Security**: Hate/unfairness, violence, self-harm, sexual content
- **Agent-Specific Metrics**: Tool call accuracy, task completion rate
- **Custom Evaluators**: Domain-specific requirements

### Monitoring in Azure Foundry

Production monitoring ensures deployed AI applications maintain quality and performance.

**Integration**: Azure Monitor Application Insights

**Real-Time Dashboards Track**:
- Operational metrics
- Token consumption
- Latency
- Error rates
- Quality scores

### AI Application Lifecycle Evaluation

#### 1. Base Model Selection
Select the right foundation model by comparing:
- Quality and task performance
- Ethical considerations
- Safety profiles
- Cost and latency tradeoffs

#### 2. Production Evaluation (Pre-Deployment)
Thorough testing before deployment:
- Evaluation datasets
- Edge case identification
- Robustness testing
- Key metrics validation (task adherence, groundedness, relevance, safety)

#### 3. Post-Deployment Monitoring
Continuous monitoring ensuring quality in real-world conditions:

- **Operational Metrics**: Regular measurement of key operational metrics
- **Continuous Evaluation**: Quality and safety evaluation at a sampled rate
- **Scheduled Evaluation**: Quality and safety evaluation using test datasets to detect drift

### Key Configuration Questions

| Question | Action |
|----------|--------|
| How to set up tracing? | Configure distributed tracing |
| What are you evaluating for? | Identify or build relevant evaluators |
| What data should you use? | Upload or generate relevant dataset |
| How did my model/AI application perform? | Analyze results |

---

## Setup Instructions

### Local Linux Setup

#### Prerequisites
- Linux operating system (Ubuntu 20.04+ recommended)
- Python 3.9 or higher
- Git

#### Step 1: Create Virtual Environment

```bash
# Navigate to OBSERVABILITY folder
cd EVALUATION/OBSERVABILITY

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

#### Step 2: Install Core Dependencies

```bash
# Install core observability libraries
pip install langfuse
pip install arize-phoenix
pip install openlit
pip install trulens-eval
pip install deepeval

# Install LLM frameworks
pip install langchain
pip install langgraph
pip install llama-index

# Install ML libraries
pip install torch
pip install transformers
pip install datasets

# Install utility libraries
pip install python-dotenv
pip install opentelemetry-api
pip install opentelemetry-sdk
```

#### Step 3: Install Langfuse (Self-Hosted)

**Option A: Using Docker Compose** (Recommended)

```bash
# Install Docker and Docker Compose if not already installed
sudo apt update
sudo apt install docker.io docker-compose

# Create directory for Langfuse
mkdir -p langfuse-local
cd langfuse-local

# Download docker-compose.yml
curl -o docker-compose.yml https://raw.githubusercontent.com/langfuse/langfuse/main/docker-compose.yml

# Start Langfuse
docker-compose up -d

# Access Langfuse at http://localhost:3000
```

**Option B: Install Langfuse Python SDK Only**

```bash
pip install langfuse
```

#### Step 4: Install Arize Phoenix (Local)

```bash
# Phoenix runs as a local server
pip install arize-phoenix

# Start Phoenix server
python -m phoenix.server.main serve

# Access Phoenix at http://localhost:6006
```

#### Step 5: Setup Helicone (Proxy-Based)

Helicone is primarily a cloud service, but you can use it with a proxy:

```bash
pip install helicone
```

Create `.env` file:
```bash
HELICONE_API_KEY=your_api_key_here
```

#### Step 6: Configure Environment Variables

Create a `.env` file in the OBSERVABILITY folder:

```bash
# LLM Provider API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
HUGGINGFACE_API_KEY=your_hf_key

# Langfuse Configuration
LANGFUSE_PUBLIC_KEY=your_public_key
LANGFUSE_SECRET_KEY=your_secret_key
LANGFUSE_HOST=http://localhost:3000

# Helicone Configuration
HELICONE_API_KEY=your_helicone_key

# Arize Configuration (if using cloud)
ARIZE_API_KEY=your_arize_key
ARIZE_SPACE_ID=your_space_id
```

#### Step 7: Verify Installation

```python
# test_installation.py
import langfuse
import phoenix
from langchain import LangChain
from opentelemetry import trace

print("All dependencies installed successfully!")
```

Run:
```bash
python test_installation.py
```

---

### Cloud Provider Setup

#### Google Cloud Platform (GCP)

##### 1. Setup Cloud Logging and Monitoring

```bash
# Install Google Cloud SDK
pip install google-cloud-logging
pip install google-cloud-monitoring

# Initialize GCP
gcloud init
gcloud auth application-default login
```

##### 2. Configure OpenTelemetry for GCP

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from google.cloud.trace.exporter import CloudTraceSpanExporter

# Setup tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Export to Google Cloud Trace
cloud_trace_exporter = CloudTraceSpanExporter()
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(cloud_trace_exporter)
)
```

##### 3. Deploy Langfuse on Google Cloud Run

```bash
# Build container
gcloud builds submit --tag gcr.io/PROJECT_ID/langfuse

# Deploy to Cloud Run
gcloud run deploy langfuse \
  --image gcr.io/PROJECT_ID/langfuse \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

#### Microsoft Azure

##### 1. Setup Application Insights

```bash
# Install Azure Monitor
pip install azure-monitor-opentelemetry
pip install opencensus-ext-azure

# Install Azure SDK
pip install azure-identity
pip install azure-mgmt-monitor
```

##### 2. Configure Application Insights for LLM Observability

```python
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

# Configure Azure Monitor
configure_azure_monitor(
    connection_string="InstrumentationKey=YOUR_KEY;IngestionEndpoint=https://REGION.in.applicationinsights.azure.com/"
)

tracer = trace.get_tracer(__name__)

# Trace LLM calls
with tracer.start_as_current_span("llm_call"):
    response = llm.generate(prompt)
```

##### 3. Use Azure Foundry Evaluation

Azure Foundry provides built-in evaluation capabilities:

```python
from azure.ai.evaluation import EvaluationClient

client = EvaluationClient(
    endpoint="https://YOUR_FOUNDRY.azure.com",
    credential=DefaultAzureCredential()
)

# Run evaluation
results = client.evaluate(
    model="your-model",
    dataset="your-dataset",
    evaluators=["groundedness", "relevance", "coherence"]
)
```

##### 4. Deploy Langfuse on Azure Container Apps

```bash
# Create container registry
az acr create --name langfuseregistry --resource-group myResourceGroup --sku Basic

# Build and push image
az acr build --registry langfuseregistry --image langfuse:latest .

# Deploy to Container Apps
az containerapp create \
  --name langfuse \
  --resource-group myResourceGroup \
  --image langfuseregistry.azurecr.io/langfuse:latest \
  --target-port 3000 \
  --ingress external
```

---

## Practical Example: Agent Evaluation with LangGraph

This example demonstrates how to monitor the internal steps (traces) of LangGraph agents and evaluate performance using Langfuse and Hugging Face Datasets.

**Reference**: [LangGraph Agent Observability with Langfuse](https://langfuse.com/guides/cookbook/example_langgraph_agents)

### Step-by-Step Implementation

#### Step 1: Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install required packages
pip install langfuse
pip install langgraph
pip install langchain
pip install langchain-openai
pip install datasets
pip install python-dotenv
```

#### Step 2: Setup Environment Variables

Create `.env` file:
```bash
OPENAI_API_KEY=your_openai_key
LANGFUSE_PUBLIC_KEY=your_public_key
LANGFUSE_SECRET_KEY=your_secret_key
LANGFUSE_HOST=http://localhost:3000  # or cloud URL
```

#### Step 3: Create Agent with LangGraph

See implementation in [sources/agent_evaluation.py](sources/agent_evaluation.py)

The agent performs the following:
1. Takes a user query
2. Uses tools (search, calculator)
3. Reasons through the problem
4. Returns a final answer

#### Step 4: Integrate Langfuse Tracing

Langfuse automatically traces LangGraph agents:

```python
from langfuse.decorators import observe
from langfuse.callback import CallbackHandler

# Initialize Langfuse callback
langfuse_handler = CallbackHandler()

# Run agent with tracing
response = agent.invoke(
    {"input": query},
    {"callbacks": [langfuse_handler]}
)
```

#### Step 5: Load Evaluation Dataset

Use Hugging Face Datasets:

```python
from datasets import load_dataset

# Load benchmark dataset
dataset = load_dataset("hotpot_qa", "distractor", split="validation[:10]")

# Convert to Langfuse dataset
for item in dataset:
    langfuse.create_dataset_item(
        dataset_name="hotpot_qa_eval",
        input=item["question"],
        expected_output=item["answer"]
    )
```

#### Step 6: Run Evaluation

```python
dataset = langfuse.get_dataset("hotpot_qa_eval")

for item in dataset.items:
    # Run agent
    response = agent.invoke(
        {"input": item.input},
        {"callbacks": [langfuse_handler]}
    )
    
    # Score response
    langfuse_handler.score(
        name="accuracy",
        value=calculate_accuracy(response, item.expected_output)
    )
```

#### Step 7: Analyze Results

View traces and evaluation results in Langfuse UI:
- Navigate to http://localhost:3000
- View traces for each agent execution
- Analyze performance metrics
- Compare different runs

---

## Running Tests in CI/CD

You can integrate observability and evaluation into your continuous integration pipeline.

### GitHub Actions Example

Create `.github/workflows/llm-tests.yml`:

```yaml
name: LLM Evaluation Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run evaluation tests
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        LANGFUSE_PUBLIC_KEY: ${{ secrets.LANGFUSE_PUBLIC_KEY }}
        LANGFUSE_SECRET_KEY: ${{ secrets.LANGFUSE_SECRET_KEY }}
      run: |
        python sources/run_evaluation.py
    
    - name: Check evaluation thresholds
      run: |
        python sources/check_thresholds.py --min-accuracy 0.8
```

### Using Remote Datasets with LLM-as-a-Judge

For more advanced testing, use remote datasets stored in Langfuse:

```python
from langfuse import Langfuse

langfuse = Langfuse()

# Fetch remote dataset
dataset = langfuse.get_dataset("production_eval_set")

# Run evaluation
for item in dataset.items:
    response = agent.run(item.input)
    
    # Use LLM-as-a-Judge
    score = llm_judge_evaluator(
        input=item.input,
        output=response,
        expected=item.expected_output
    )
    
    # Log result
    langfuse.score(
        trace_id=response.trace_id,
        name="llm_judge_score",
        value=score
    )
```

---

## Project Structure

```
OBSERVABILITY/
│
├── 📄 README.md                          # This file
├── 📄 .gitignore                         # Git ignore rules
├── 📄 .env                               # Environment variables (not in Git)
├── 📄 requirements.txt                   # Python dependencies
│
├── 📁 venv/                              # Virtual environment (excluded from Git)
│
├── 📁 sources/                           # Source code directory
│   ├── 📄 agent_evaluation.py            # LangGraph agent with Langfuse tracing
│   ├── 📄 run_evaluation.py              # Batch evaluation script
│   ├── 📄 check_thresholds.py            # Threshold validation for CI/CD
│   ├── 📄 llm_judge_evaluator.py         # LLM-as-a-Judge implementation
│   └── 📄 test_installation.py           # Verify dependencies
│
├── 📁 data/                              # Datasets for evaluation
│   ├── 📄 benchmark_dataset.json
│   └── 📄 test_cases.json
│
├── 📁 notebooks/                         # Jupyter notebooks for exploration
│   └── 📄 agent_analysis.ipynb
│
├── 📁 configs/                           # Configuration files
│   ├── 📄 langfuse_config.yaml
│   └── 📄 phoenix_config.yaml
│
├── 📁 results/                           # Evaluation results (excluded from Git)
│   └── 📄 evaluation_report.json
│
└── 📁 docker/                            # Docker configurations
    ├── 📄 Dockerfile
    └── 📄 docker-compose.yml
```

---

## References

### Observability Platforms

- **Langfuse**: [https://langfuse.com/](https://langfuse.com/)
  - GitHub: [https://github.com/langfuse/langfuse](https://github.com/langfuse/langfuse)
  - Docs: [https://langfuse.com/docs](https://langfuse.com/docs)
  - Self-Hosting: [https://langfuse.com/docs/deployment/self-host](https://langfuse.com/docs/deployment/self-host)

- **Arize Phoenix**: [https://phoenix.arize.com/](https://phoenix.arize.com/)
  - Docs: [https://docs.arize.com/phoenix](https://docs.arize.com/phoenix)

- **Helicone**: [https://www.helicone.ai/](https://www.helicone.ai/)
  - Docs: [https://docs.helicone.ai/](https://docs.helicone.ai/)

- **LangSmith**: [https://www.langchain.com/langsmith](https://www.langchain.com/langsmith)
  - Info: [https://info.langchain.com/AI-Observability](https://info.langchain.com/AI-Observability)

- **Datadog LLM Observability**: [https://www.datadoghq.com/product/llm-observability/](https://www.datadoghq.com/product/llm-observability/)

- **Lunary**: [https://lunary.ai/](https://lunary.ai/)

- **TruLens**: [https://www.trulens.org/](https://www.trulens.org/)

- **Portkey**: [https://portkey.ai/](https://portkey.ai/)

### Frameworks and SDKs

- **LangChain**: [https://www.langchain.com/](https://www.langchain.com/)
  - GitHub: [https://github.com/langchain-ai/langchain](https://github.com/langchain-ai/langchain)

- **LangGraph**: [https://langchain-ai.github.io/langgraph/](https://langchain-ai.github.io/langgraph/)

- **LlamaIndex**: [https://www.llamaindex.ai/](https://www.llamaindex.ai/)

- **Hugging Face Transformers**: [https://huggingface.co/transformers](https://huggingface.co/transformers)

- **Hugging Face Observer**: [https://github.com/cfahlgren1/observers](https://github.com/cfahlgren1/observers)
  - Blog: [https://huggingface.co/blog/davidberenstein1957/observers-a-lightweight-sdk-for-ai-observability](https://huggingface.co/blog/davidberenstein1957/observers-a-lightweight-sdk-for-ai-observability)

### Cloud Providers

- **Azure Foundry Observability**: [https://learn.microsoft.com/en-us/azure/foundry/concepts/observability](https://learn.microsoft.com/en-us/azure/foundry/concepts/observability)

- **Google Cloud Vertex AI**: [https://cloud.google.com/vertex-ai](https://cloud.google.com/vertex-ai)

### Guides and Tutorials

- **LangGraph Agent Evaluation with Langfuse**: [https://langfuse.com/guides/cookbook/example_langgraph_agents](https://langfuse.com/guides/cookbook/example_langgraph_agents)

- **Synthetic Dataset Generation**: [https://langfuse.com/guides/cookbook/example_synthetic_datasets](https://langfuse.com/guides/cookbook/example_synthetic_datasets)

- **Testing LLM Applications**: [https://langfuse.com/blog/2025-10-21-testing-llm-applications](https://langfuse.com/blog/2025-10-21-testing-llm-applications)

- **LLM Observability Tools Comparison**: [https://www.langchain.com/articles/llm-observability-tools](https://www.langchain.com/articles/llm-observability-tools)

- **Microsoft AI Agents for Beginners - Production**: [https://microsoft.github.io/ai-agents-for-beginners/10-ai-agents-production/](https://microsoft.github.io/ai-agents-for-beginners/10-ai-agents-production/)

- **Hugging Face Agents Course - Observability**: [https://huggingface.co/learn/agents-course/bonus-unit2/what-is-agent-observability-and-evaluation](https://huggingface.co/learn/agents-course/bonus-unit2/what-is-agent-observability-and-evaluation)

- **Monitor Hugging Face Models with Langfuse**: [https://github.com/langfuse/langfuse-docs/blob/main/cookbook/integration_huggingface_openai_sdk.ipynb](https://github.com/langfuse/langfuse-docs/blob/main/cookbook/integration_huggingface_openai_sdk.ipynb)

- **Ollama Observability Example**: [https://github.com/cfahlgren1/observers](https://github.com/cfahlgren1/observers)

### Open Source Communities

- **Hugging Face Hub**: [https://huggingface.co/](https://huggingface.co/)

- **OpenTelemetry**: [https://opentelemetry.io/](https://opentelemetry.io/)

- **OpenLLMetry**: [https://github.com/traceloop/openllmetry](https://github.com/traceloop/openllmetry)

---

## Summary

Observability is critical for understanding, debugging, and improving AI agents and LLM applications. Unlike traditional software, AI systems are non-deterministic and require specialized observability approaches that capture behavioral, operational, and decisional insights.

**Key Takeaways**:

1. **Observability gives us metrics**; evaluation is the process of analyzing that data to improve AI performance
2. **Two categories of evaluation**: Online (real-time) and Offline (benchmark datasets)
3. **Open-source tools** like Langfuse, Arize Phoenix, and Helicone provides observability without vendor lock-in
4. **Three-phase maturity model**: Manual tracing → Online evaluation → Offline evaluation
5. **Testing LLMs requires evaluation-based approaches** rather than exact-match assertions
6. **Cloud providers** like Azure and GCP offer integrated observability solutions
7. **Local deployment** is possible with Docker-based tools for full control

By implementing proper observability and evaluation practices, teams can build reliable, transparent, and continuously improving AI agents.

---

**Last Updated**: March 26, 2026
