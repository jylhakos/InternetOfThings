# Open Source Tools For Evaluating Large Language Models and AI Agents

This document presents open-source tools and metrics to evaluate Large Language Models (LLMs), AI Agents, MCP Servers, and MCP Clients.

## Table of Contents

- [⚠️ Important: Virtual Environment Requirement](#️-important-virtual-environment-requirement)
- [AI Agent Evaluation vs. LLM Evaluation](#-ai-agent-evaluation-vs-llm-evaluation)
  - [Why Agent Evaluation Differs from LLM Evaluation](#why-agent-evaluation-differs-from-llm-evaluation)
  - [The Challenge: Non-Deterministic Systems](#the-challenge-non-deterministic-systems)
- [How to Evaluate AI Agents?](#-how-to-evaluate-ai-agents)
  - [Evaluation Strategies](#evaluation-strategies)
  - [Metrics to Track for AI Agents](#metrics-to-track-for-ai-agents)
- [Structure of an Evaluation](#-structure-of-an-evaluation)
  - [Core Evaluation Terminology](#core-evaluation-terminology)
  - [Agent Evaluation Grader Types](#agent-evaluation-grader-types)
- [🔧 How to Test and Measure Agentic AI Performance?](#-how-to-test-and-measure-agentic-ai-performance)
  - [Testing MCP Servers and MCP Clients](#testing-mcp-servers-and-mcp-clients)
- [🛠️ Open Source Evaluation Tools for Large Language Models (March - 2026)](#️-open-source-evaluation-tools-for-large-language-models-march---2026)
- [Agent Evaluation Tools (2026)](#-agent-evaluation-tools-2026)
  - [Commercial & Open-Source Agent Evaluation Platforms](#commercial--open-source-agent-evaluation-platforms)
  - [Open-Source Agent Evaluation Frameworks](#open-source-agent-evaluation-frameworks)
  - [Claude + LangChain Evaluation](#claude--langchain-evaluation)
  - [Agent Evaluation in 5 Steps](#agent-evaluation-in-5-steps)
- [What is BERT?](#what-is-bert)
- [How does the BERT model work for text classification?](#how-does-the-bert-model-work-for-text-classification)
- [Project](#project)
- [Setup](#setup)
- [FastAPI backend server](#fastapi-backend-server)
- [Docker deployment](#docker-deployment)
- [LLM Evaluation Metrics](#llm-evaluation-metrics)
- [Training and Evaluation Metrics](#training-and-evaluation-metrics)
- [Model Performance Evaluation](#model-performance-evaluation)
- [LLM Evaluation Tools Integration](#llm-evaluation-tools-integration)
- [Evaluation Tools](#evaluation-tools)
- [Optimizers (2026)](#optimizers-2026)
- [Model Prediction Testing](#model-prediction-testing)
- [Advanced topics](#advanced-topics)
- [References](#references)
- [Summary](#-summary)

---

## ⚠️ Important: Virtual Environment Requirement

**All operations in this TOOLS folder MUST be performed within an active virtual environment.** Before installing libraries, running scripts, or executing tools, always activate the virtual environment:

```bash
# Activate virtual environment
source bert_env/bin/activate

# Verify activation (you should see (bert_env) prefix in terminal)
which python
```

**Why Virtual Environment is Mandatory:**
- Isolates project dependencies from system Python
- Prevents version conflicts between packages
- Ensures reproducible development environment
- Required for proper package management and testing

**Never run installation or execution commands without activating the virtual environment first.**

## AI Agent Evaluation vs. LLM Evaluation

### Why Agent Evaluation Differs from LLM Evaluation

**Traditional LLM evaluation** focuses on text quality metrics like coherence, factual accuracy, and response relevance. These metrics assume the model's job ends when it generates text.

**Agent evaluation requires a fundamentally different approach** because agents don't just generate text. They:
- **Take actions** and invoke tools with specific parameters
- **Make sequential decisions** that build on previous steps
- **Must recover** when external APIs fail or return unexpected data
- **Maintain context** across multi-turn interactions
- **Control costs and latency** in production environments
- **Remain resilient** against adversarial inputs

#### Real-World Example

A customer support agent needs to look up order status, process refunds, and update customer records. Traditional LLM metrics tell you **nothing** about whether it:
- Called the right API endpoints
- Passed correct customer IDs
- Handled cases where refund requests exceeded policy limits
- Recovered from database connection failures

**Agent evaluation must assess:**
1.   Task completion success
2.   Tool invocation accuracy
3.   Reasoning quality across multi-step workflows
4.   Failure handling and recovery
5.   Cost and latency performance
6.   Long-term context maintenance

### The Challenge: Non-Deterministic Systems

Unlike traditional software, **agents and LLM applications are non-deterministic**: the same input can produce different outputs. Traditional LLM metrics, along with single-turn accuracy, do not adequately capture an agent's ability to:
- Plan effectively
- Recover from failures
- Maintain long-term context
- Control costs and latency
- Remain resilient against adversarial inputs

**The fundamental challenge:** Figuring out whether your agent actually works reliably in production.

## How to Evaluate AI Agents?

Evaluating and testing AI agents requires a **multi-layered approach** combining:
- **Automated metrics** (code-based graders)
- **LLM-as-a-judge** (model-based graders)
- **Human review** (human graders)

This approach assesses reasoning, tool use, and task success across all dimensions.

### Evaluation Strategies

#### 1. **Component vs. End-to-End Testing**
Test individual skills (e.g., tool selection, parameter generation) before testing the entire workflow.

```python
# Component testing
test_tool_selection()      # Does agent choose right tool?
test_parameter_generation() # Are parameters correct?
test_error_recovery()      # Does it handle API failures?

# End-to-end testing
test_complete_workflow()   # Does entire task succeed?
```

#### 2. **LLM-as-a-Judge**
Use a strong LLM (e.g., GPT-4, Claude) to evaluate the output of your agent based on specific rubrics:
- Checking for hallucinations
- Verifying proper formatting
- Assessing reasoning quality
- Validating adherence to guidelines

```python
# LLM-as-a-judge example
evaluator_prompt = """
Evaluate if this agent response:
1. Answered the question accurately
2. Used appropriate data from context
3. Avoided hallucinations
4. Followed safety guidelines

Agent response: {response}
Context: {context}
"""
```

#### 3. **Simulation and Datasets**
Create a dataset of user queries and expected behaviors to run offline, automated tests for regression.

```python
# Example test dataset
test_cases = [
    {
        "input": "Book a flight from NYC to LAX on Dec 25",
        "expected_tools": ["search_flights", "book_flight"],
        "expected_outcome": "flight_booked",
        "success_criteria": "reservation_exists_in_db"
    },
    # ... more test cases
]
```

#### 4. **Human-in-the-Loop (HITL)**
Use expert human review for qualitative aspects:
- Tone and empathy
- Safety and ethical considerations
- Complex judgment calls
- Edge cases and unusual scenarios

### Metrics to Track for AI Agents

#### 1. **Task Success Rate**
Percentage of goals successfully completed by the agent.

```python
task_success_rate = (successful_tasks / total_tasks) * 100
```

#### 2. **Tool Usage Quality**
Correctness of tool selection, parameter generation, and function calls.

```python
metrics = {
    "tool_selection_accuracy": 0.95,  # Right tool chosen
    "parameter_correctness": 0.92,     # Correct parameters
    "api_call_success": 0.88           # Successful execution
}
```

#### 3. **Trajectory Evaluation**
Assessing the reasoning steps and actions the agent took to reach the solution.

```python
# Trajectory quality metrics
trajectory_metrics = {
    "num_steps": 5,                    # Efficiency
    "reasoning_quality": "high",        # Decision quality
    "backtracking_count": 0,           # Error recovery
    "redundant_calls": 0                # Optimization
}
```

#### 4. **Faithfulness/Groundedness**
Ensuring the output is supported by the retrieved context, minimizing hallucinations.

```python
# Groundedness check
faithfulness_score = evaluate_claims(
    claims=agent_response,
    evidence=retrieved_context
)
```

#### 5. **Performance & Cost**
Tracking latency, token consumption, and cost per task.

```python
performance_metrics = {
    "avg_latency_ms": 1250,
    "tokens_per_task": 2500,
    "cost_per_task_usd": 0.025,
    "throughput_tasks_per_min": 48
}
```

## Structure of an Evaluation

An **evaluation ("eval")** is a test for an AI system: give an AI an input, then apply grading logic to its output to measure success.

### Core Evaluation Terminology

#### **Task** (a.k.a. problem or test case)
A single test with defined inputs and success criteria.

```python
task = {
    "id": "flight_booking_001",
    "input": "Book a flight from SFO to JFK",
    "tools": ["search_flights", "book_flight", "update_db"],
    "success_criteria": "reservation_exists AND confirmation_sent"
}
```

#### **Trial**
Each attempt at a task. Because model outputs vary between runs, we run **multiple trials** to produce more consistent results.

```python
# Run 5 trials per task for statistical significance
trials = [run_task(task) for _ in range(5)]
success_rate = sum(trial.success for trial in trials) / len(trials)
```

#### **Grader**
Logic that scores some aspect of the agent's performance. A task can have **multiple graders**, each containing multiple **assertions** (sometimes called checks).

```python
graders = {
    "code_based": check_reservation_in_db(),
    "model_based": llm_evaluates_response_quality(),
    "human": human_reviews_edge_cases()
}
```

#### **Transcript** (also called trace or trajectory)
The complete record of a trial, including:
- All outputs
- Tool calls
- Reasoning steps
- Intermediate results
- Any other interactions

For the Anthropic API, this is the **full messages array** at the end of an eval run - containing all the calls to the API and all of the returned responses during the evaluation.

```python
transcript = {
    "messages": [...],              # Full conversation
    "tool_calls": [...],            # All function invocations
    "reasoning_steps": [...],        # Agent's thinking
    "timestamps": [...]              # Timing information
}
```

#### **Outcome**
The **final state in the environment** at the end of the trial. A flight-booking agent might say "Your flight has been booked" at the end of the transcript, but the **outcome** is whether a reservation actually exists in the environment's SQL database.

```python
# Transcript vs Outcome
transcript_claim = "Flight booked successfully"
actual_outcome = database.query("SELECT * FROM reservations WHERE id=123")
# Outcome verification is critical!
```

#### **Evaluation Harness**
The infrastructure that runs evals end-to-end. It provides:
- Instructions and tools
- Runs tasks concurrently
- Records all the steps
- Grades outputs
- Aggregates results

```python
class EvaluationHarness:
    def run_evaluation(self, tasks, agent, graders):
        results = []
        for task in tasks:
            trials = self.run_trials(task, agent, num_trials=5)
            scores = self.apply_graders(trials, graders)
            results.append(self.aggregate_results(scores))
        return results
```

#### **Agent Harness** (or scaffold)
The system that enables a model to act as an agent: it processes inputs, orchestrates tool calls, and returns results. When we evaluate "an agent," we're evaluating **the harness and the model working together**.

```python
class AgentHarness:
    def __init__(self, model, tools):
        self.model = model
        self.tools = tools
    
    def execute_task(self, task_input):
        while not task_complete:
            response = self.model.generate(context)
            if response.requires_tool:
                result = self.tools.execute(response.tool_call)
                context.append(result)
        return final_result
```

### Agent Evaluation Grader Types

Agent evaluations typically combine **three types of graders**:

1. **Code-based graders**: Automated assertions on outcomes and transcripts
2. **Model-based graders**: LLM-as-a-judge evaluating quality
3. **Human graders**: Expert review for nuanced judgment

Each grader evaluates some portion of either the **transcript** or the **outcome**.

## How to Test and Measure Agentic AI Performance?

Testing agentic AI requires **defining what evaluation means** in an operational setting and which agent behaviors should be measured.

### What to Measure

| Dimension                    | Evaluation Method                                                |        Example Metrics                        |
|------------------------------|------------------------------------------------------------------|-----------------------------------------------|
| **Intelligence & Accuracy**  | Automated reasoning tests, LLM judges reviewing reasoning traces | Task success rate, reasoning quality score    |
| **User Experience**          | Human feedback, surveys, A/B testing                             | User satisfaction (NPS), task completion time |
| **Performance & Efficiency** | Real-time monitoring                                             | Latency (ms), token costs, throughput         |
| **Safety & Reliability**     | Adversarial testing, failure injection                           | Error recovery rate, hallucination frequency  |
| **Cost Optimization**        | Production metrics tracking                                      | Cost per task, token efficiency rate          |

### How to Measure Effectively

#### 1. **Intelligence and Accuracy**
```python
# Automated reasoning tests
def test_reasoning_quality(agent, test_cases):
    scores = []
    for case in test_cases:
        response = agent.execute(case.input)
        score = evaluate_reasoning_chain(response.trajectory)
        scores.append(score)
    return np.mean(scores)

# LLM-as-a-judge
def llm_judge_evaluation(agent_output, rubric):
    judge_prompt = f"""
    Evaluate this agent response against the rubric:
    {rubric}
    
    Agent output: {agent_output}
    """
    return llm.evaluate(judge_prompt)
```

#### 2. **Reference-Free vs Reference-Aware Evaluation**

**Reference-Free** (no gold standard needed):
- Helpfulness
- Clarity
- Relevance
- Safety

**Reference-Aware** (compared to gold answer):
- Correctness
- Completeness
- Factual accuracy

```python
# Reference-free
score = evaluate_helpfulness(response)

# Reference-aware
score = compare_to_gold_standard(response, reference_answer)
```

#### 3. **Real-Time Performance Monitoring**
```python
class AgentPerformanceMonitor:
    def track_metrics(self, task_execution):
        return {
            "latency_ms": task_execution.duration,
            "tokens_used": task_execution.token_count,
            "cost_usd": task_execution.token_count * price_per_token,
            "api_calls": len(task_execution.tool_calls),
            "success": task_execution.outcome == "success"
        }
```

### Testing MCP Servers and MCP Clients

**Model Context Protocol (MCP)** servers and clients require specialized testing approaches:

#### MCP Server Testing
```python
# Test MCP server capabilities
def test_mcp_server(server):
    # 1. Test tool registration
    assert server.list_tools() == expected_tools
    
    # 2. Test tool execution
    result = server.execute_tool("search", {"query": "test"})
    assert result.success
    
    # 3. Test error handling
    result = server.execute_tool("invalid_tool", {})
    assert result.error_code == "TOOL_NOT_FOUND"
    
    # 4. Test context management
    context = server.get_context()
    assert len(context.history) > 0
```

#### MCP Client Testing
```python
# Test MCP client integration
def test_mcp_client(client, mock_server):
    # 1. Test server connection
    assert client.connect(mock_server) == True
    
    # 2. Test tool discovery
    tools = client.discover_tools()
    assert len(tools) > 0
    
    # 3. Test tool invocation
    response = client.call_tool("search", {"query": "test"})
    assert response.status == "success"
    
    # 4. Test error propagation
    response = client.call_tool("failing_tool", {})
    assert client.handle_error(response.error)
```

## Open Source Evaluation Tools for Large Language Models (March - 2026)

Large Language Models (LLMs) evaluation has evolved with open-source tools designed specifically for model assessment. This project integrates several evaluation frameworks to provide multi-dimensional analysis of language model performance.

### **Evaluation Tools**

#### 1. **DeepEval** - LLM Testing Framework
- **Repository**: [confident-ai/deepeval](https://github.com/confident-ai/deepeval)
- **Documentation**: [deepeval.com/docs/metrics-llm-evals](https://deepeval.com/docs/metrics-llm-evals)
- **Description**: An open-source framework for testing LLM applications in production
- **Key Features**:
  - Scientifically tested evaluation metrics
  - Answer relevancy, faithfulness, contextual precision/recall
  - Hallucination detection and bias assessment
  - Real-time performance monitoring
  - Custom metric creation and A/B testing
- **Use Cases**: Production LLM testing, RAG evaluation, chatbot assessment
- **Installation**: `pip install deepeval`

#### 2. **G-Eval** - LLM-as-a-Judge Framework
- **Repository**: [nlpyang/geval](https://github.com/nlpyang/geval)
- **Description**: Chain-of-thought based evaluation using LLMs as judges
- **Key Features**:
  - Uses GPT-4 for human-like evaluation
  - Chain-of-thoughts reasoning for transparent scoring
  - Natural language generation evaluation
  - Creative content assessment
  - Correlation with human judgments
- **Use Cases**: Creative writing evaluation, summarization quality, dialogue assessment
- **Requirements**: OpenAI API key for GPT evaluation

#### 3. **LLMeBench** - Multi-Lingual Benchmarking
- **Repository**: [qcri/LLMeBench](https://github.com/qcri/LLMeBench)
- **Description**: Comprehensive benchmarking framework for LLMs across multiple languages
- **Key Features**:
  - Multi-lingual evaluation support
  - Standardized benchmarking protocols
  - Comparative analysis across models
  - Leaderboard integration
  - Performance tracking over time
- **Use Cases**: Model comparison, multi-lingual applications, research benchmarking
- **Strength**: Standardized evaluation protocols for fair model comparison

#### 4. **LangSmith** - Production LLM Observability
- **Repository**: [langchain-ai/langsmith-sdk](https://github.com/langchain-ai/langsmith-sdk)
- **Documentation**: [docs.smith.langchain.com](https://docs.smith.langchain.com/evaluation)
- **Website**: [langchain.com/langsmith](https://www.langchain.com/langsmith)
- **Description**: Advanced observability and evaluation platform for LangChain applications
- **Key Features**:
  - Real-time monitoring and debugging
  - Automatic evaluation metrics
  - Bias detection and safety evaluation
  - Performance analytics dashboard
  - Custom evaluator configuration
  - Dataset management and versioning
- **Evaluation Methods**:
  ```python
  # Synchronous evaluation
  results = client.evaluate(
      target_function,
      dataset=dataset,
      evaluators=evaluators
  )
  
  # Asynchronous evaluation
  results = await client.aevaluate(
      target_function,
      dataset=dataset,
      evaluators=evaluators
  )
  ```
- **Use Cases**: Production monitoring, LangChain app evaluation, enterprise deployments

#### 5. **Ragas** - RAG Application Evaluation
- **Repository**: [explodinggradients/ragas](https://github.com/explodinggradients/ragas)
- **Documentation**: [docs.ragas.io](https://docs.ragas.io/en/stable/)
- **Description**: Specialized toolkit for evaluating and optimizing RAG (Retrieval-Augmented Generation) applications
- **Key Features**:
  - RAG-specific metrics (context relevance, answer faithfulness)
  - Retrieval quality assessment
  - End-to-end RAG pipeline evaluation
  - Automated optimization suggestions
  - Integration with popular RAG frameworks
- **RAG Metrics**:
  - Context Relevance
  - Answer Faithfulness
  - Answer Relevancy
  - Context Precision/Recall
- **Use Cases**: RAG system optimization, document Q&A evaluation, knowledge base assessment

#### 6. **LM Evaluation Harness** - Academic Benchmarking
- **Repository**: [EleutherAI/lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness)
- **Description**: Unified framework for evaluating language models on academic benchmarks
- **Key Features**:
  - 200+ academic benchmarks and tasks
  - Standardized evaluation protocols
  - Research-grade reproducibility
  - Performance reporting
  - Model leaderboard integration
- **Use Cases**: Academic research, model comparison, benchmark evaluation
- **Strength**: Extensive benchmark coverage for research applications

### **Integrated Evaluation Pipeline**

Our project combines multiple tools for LLM assessment:

```python
# Multi-framework evaluation approach
evaluation_pipeline = {
    "traditional_metrics": ["accuracy", "f1", "precision", "recall"],
    "semantic_metrics": ["bertscore", "rouge", "bleu"],
    "llm_based_metrics": ["deepeval", "geval", "ragas"],
    "production_monitoring": ["langsmith"]
}
```

### **Tool Selection**

| **Use Case**            | **Recommended Tool**  | **Why**                                       |
|-------------------------|-----------------------|-----------------------------------------------|
| **Production Testing**  | DeepEval              | Metrics, production-ready                     |
| **Creative Content**    | G-Eval                | Human-like evaluation via LLM judges          |
| **Multi-lingual**       | LLMeBench             | Specialized for cross-language evaluation     |
| **RAG Applications**    | Ragas                 | RAG-specific metrics and optimization         |
| **Academic Research**   | LM Evaluation Harness | Standardized benchmarks                       |
| **LangChain Apps**      | LangSmith             | Native integration, observability             |

### **Getting Started**

```bash
# Install core evaluation tools
pip install deepeval ragas bert-score rouge-score sacrebleu

# Install optional tools (requires API keys)
pip install openai  # For G-Eval
pip install langsmith  # For LangSmith integration

# Set environment variables
export OPENAI_API_KEY="your-key"
export LANGCHAIN_API_KEY="your-key"
```

### **Integration**

 **DeepEval**: Integrated with custom metrics
 **BERTScore**: Semantic similarity evaluation
 **G-Eval**: LLM-as-judge implementation
 **ROUGE/BLEU**: Traditional text similarity
⚠️ **Ragas**: Available for RAG evaluation
⚠️ **LangSmith**: Optional enterprise integration
⚠️ **LM Evaluation Harness**: Academic benchmark support

These evaluation tools ensure multi-dimensional assessment of LLM performance across different domains and use cases.

##   Agent Evaluation Tools (2026)

Specialized tools for evaluating AI agents, which require testing beyond text generation to assess tool use, multi-step reasoning, and task completion.

### **Commercial & Open-Source Agent Evaluation Platforms**

#### 1. **LangSmith** (by LangChain) 
- **Best For**: Debugging and visualizing complex traces in agent workflows
- **Repository**: [langchain-ai/langsmith-sdk](https://github.com/langchain-ai/langsmith-sdk)
- **Documentation**: [docs.smith.langchain.com](https://docs.smith.langchain.com/evaluation)
- **Key Features**:
  - Real-time trace visualization
  - Agent workflow debugging
  - Tool call tracking and analysis
  - Automatic evaluation metrics
  - Dataset management and versioning
  - Integration with LangChain ecosystem
- **Use Cases**: LangChain agent development, complex workflow debugging, production monitoring
- **Installation**: `pip install langsmith`

#### 2. **Braintrust**
- **Best For**: Robust human-in-the-loop (HITL) evaluation and automated testing
- **Website**: [braintrustdata.com](https://www.braintrustdata.com)
- **Key Features**:
  - Human rater management
  - Automated testing pipelines
  - Comparative evaluations
  - Production monitoring
  - Team collaboration tools
- **Use Cases**: Enterprise agent evaluation, HITL workflows, quality assurance

#### 3. **Maxim AI**
- **Best For**: End-to-end evaluation, simulation, and regression testing
- **Website**: [getmaxim.ai](https://www.getmaxim.ai)
- **Key Features**:
  - Simulation environments
  - Regression test automation
  - Performance benchmarking
  - Cost tracking
  - Failure analysis
- **Use Cases**: Production readiness testing, continuous evaluation, cost optimization

#### 4. **DeepEval** (Open Source)
- **Best For**: Code-first framework for unit testing LLM apps (pytest-style)
- **Repository**: [confident-ai/deepeval](https://github.com/confident-ai/deepeval)
- **Documentation**: [docs.confident-ai.com](https://docs.confident-ai.com)
- **Key Features**:
  - Pytest integration
  - Agent-specific metrics
  - Tool usage evaluation
  - Trajectory analysis
  - Custom metric creation
- **Agent Metrics**:
  - Tool correctness
  - Task success rate
  - Reasoning quality
  - Hallucination detection
- **Installation**: `pip install deepeval`
- **Example**:
```python
import deepeval
from deepeval.test_case import LLMTestCase
from deepeval.metrics import ToolCorrectnessMetric

@deepeval.pytest_mark.agent
def test_agent_tool_usage():
    test_case = LLMTestCase(
        input="Book a flight from NYC to LA",
        expected_tools=["search_flights", "book_flight"],
        actual_output=agent_response
    )
    metric = ToolCorrectnessMetric(threshold=0.9)
    assert metric.measure(test_case)
```

#### 5. **Ragas** (Open Source)
- **Best For**: Evaluating retrieval-augmented generation (RAG) components in agents
- **Repository**: [explodinggradients/ragas](https://github.com/explodinggradients/ragas)
- **Documentation**: [docs.ragas.io](https://docs.ragas.io/en/stable/)
- **Key Features**:
  - RAG-specific metrics
  - Context relevance evaluation
  - Answer faithfulness
  - Retrieval quality assessment
  - End-to-end RAG pipeline evaluation
- **Use Cases**: Knowledge-based agents, document Q&A agents, RAG optimization
- **Installation**: `pip install ragas`

#### 6. **Arize Phoenix** (Open Source)
- **Best For**: Tracking agent performance, debugging, and observability
- **Repository**: [Arize-ai/phoenix](https://github.com/Arize-ai/phoenix)
- **Documentation**: [docs.arize.com/phoenix](https://docs.arize.com/phoenix)
- **Key Features**:
  - Open-source observability
  - Agent trace visualization
  - Performance tracking
  - Debugging tools
  - Embedding analysis
  - LLM evaluation metrics
- **Use Cases**: Production monitoring, debugging agent failures, performance optimization
- **Installation**: `pip install arize-phoenix`
- **Example**:
```python
import phoenix as px
from phoenix.trace import TraceDataset

# Launch Phoenix UI
session = px.launch_app()

# Track agent execution
with px.trace("agent_execution"):
    result = agent.execute(task)
```

#### 7. **Comet Opik** (Open Source)
- **Best For**: LLM evaluation and observability platform
- **Repository**: [comet-ml/opik](https://github.com/comet-ml/opik)
- **Documentation**: [comet.com/docs/opik](https://www.comet.com/docs/opik)
- **Key Features**:
  - Trace instrumentation
  - Tool use logging
  - RAG retrieval tracking
  - Evaluation metrics
  - Production monitoring
- **Use Cases**: Agent instrumentation, trace analysis, metric tracking
- **Installation**: `pip install opik`
- **Example**:
```python
from opik import track

@track()
def agent_task(input_text):
    # Automatically logs to Opik
    response = agent.execute(input_text)
    return response
```

### **Open-Source Agent Evaluation Frameworks**

#### **Arize Phoenix** - Comprehensive Observability
```python
# Install and setup
pip install arize-phoenix

# Usage example
import phoenix as px
from phoenix.trace import trace_function

# Start Phoenix UI
px.launch_app()

@trace_function
def complex_agent_workflow(query):
    # Phoenix automatically traces:
    # - LLM calls
    # - Tool invocations
    # - Retrieval operations
    # - Reasoning steps
    result = agent.run(query)
    return result
```

#### **LangSmith (Community)** - LangChain Integration
```python
# Install
pip install langsmith

# Setup
import os
os.environ["LANGCHAIN_API_KEY"] = "your-api-key"
os.environ["LANGCHAIN_TRACING_V2"] = "true"

# Automatic tracing for LangChain agents
from langchain.agents import create_agent
agent = create_agent(...)  # Automatically traced
```

#### **DeepEval** - Pytest-Style Testing
```python
# Install
pip install deepeval

# Create agent tests
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    AnswerRelevancyMetric,
    ToolCorrectnessMetric,
    FaithfulnessMetric
)

def test_customer_support_agent():
    test_case = LLMTestCase(
        input="Cancel my order #12345",
        expected_output="Order #12345 cancelled",
        actual_output=agent.run("Cancel my order #12345"),
        context=["Order #12345 exists", "User is authorized"]
    )
    
    assert_test(test_case, [
        AnswerRelevancyMetric(threshold=0.8),
        ToolCorrectnessMetric(threshold=0.9),
        FaithfulnessMetric(threshold=0.85)
    ])
```

#### **Ragas** - Experiments-First Workflow
```python
# Install
pip install ragas

# Create evaluation dataset
from ragas import evaluate
from ragas.metrics import (
    context_relevancy,
    answer_relevancy,
    faithfulness
)

dataset = {
    "question": ["What is the refund policy?"],
    "answer": [agent_response],
    "contexts": [retrieved_docs],
    "ground_truth": ["Refunds within 30 days"]
}

# Run evaluation
results = evaluate(
    dataset,
    metrics=[context_relevancy, answer_relevancy, faithfulness]
)
```

### **Claude + LangChain Evaluation**

Using Claude (Anthropic) with LangChain for agent evaluation:

```python
# LLM-as-a-judge with Claude
from langchain_anthropic import ChatAnthropic
from langchain.evaluation import load_evaluator

# Initialize Claude as judge
judge = ChatAnthropic(model="claude-3-5-sonnet-20241022")

# Create evaluator
evaluator = load_evaluator(
    "labeled_criteria",
    criteria="correctness",
    llm=judge
)

# Evaluate agent response
eval_result = evaluator.evaluate_strings(
    prediction=agent_output,
    reference=expected_output,
    input=user_query
)

print(f"Score: {eval_result['score']}")
print(f"Reasoning: {eval_result['reasoning']}")
```

#### Trace-Based Analysis
```python
# Analyze agent reasoning chain
from langchain.callbacks import LangChainTracer

tracer = LangChainTracer()
agent.run(query, callbacks=[tracer])

# Analyze trace
for run in tracer.runs:
    print(f"Action: {run.action}")
    print(f"Tool: {run.tool}")
    print(f"Result: {run.result}")
```

### **Agent Evaluation in 5 Steps** (Microsoft Copilot Studio)

Based on [Microsoft's agent evaluation framework](https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/how-to-evaluate-ai-agents/):

#### **Step 1: Define Success Criteria**
Establish what "good" looks like for your agent:
- Task completion metrics
- Quality thresholds
- Performance requirements
- Safety boundaries

```python
success_criteria = {
    "task_success_rate": 0.95,
    "avg_latency_ms": 2000,
    "hallucination_rate": 0.02,
    "user_satisfaction": 4.5  # out of 5
}
```

#### **Step 2: Create Test Datasets**
Build comprehensive test cases covering:
- Common scenarios
- Edge cases
- Failure modes
- Adversarial inputs

```python
test_dataset = [
    {"input": "...", "expected_outcome": "...", "category": "common"},
    {"input": "...", "expected_outcome": "...", "category": "edge_case"},
    {"input": "...", "expected_outcome": "...", "category": "adversarial"}
]
```

#### **Step 3: Implement Multi-Layered Evaluation**
Combine automated, LLM-based, and human evaluation:

```python
def evaluate_agent(test_case):
    # Layer 1: Automated checks
    automated_score = check_outcome(test_case)
    
    # Layer 2: LLM-as-a-judge
    llm_score = llm_judge.evaluate(test_case)
    
    # Layer 3: Human review (for flagged cases)
    if automated_score < 0.7 or llm_score < 0.7:
        human_score = request_human_review(test_case)
    
    return aggregate_scores(automated_score, llm_score, human_score)
```

#### **Step 4: Run Continuous Evaluation**
Monitor agent performance in production:

```python
# Production monitoring
class AgentMonitor:
    def __init__(self):
        self.metrics = defaultdict(list)
    
    def log_interaction(self, interaction):
        self.metrics['latency'].append(interaction.duration)
        self.metrics['success'].append(interaction.success)
        self.metrics['cost'].append(interaction.token_cost)
    
    def get_health_metrics(self):
        return {
            "success_rate": np.mean(self.metrics['success']),
            "avg_latency": np.mean(self.metrics['latency']),
            "total_cost": np.sum(self.metrics['cost'])
        }
```

#### **Step 5: Iterate and Improve**
Use evaluation insights to improve agent performance:
- Identify failure patterns
- Optimize prompts
- Fine-tune tool selection
- Update knowledge base
- Refine error handling

### **Agent Evaluation Best Practices**

1. **Test Incrementally**: Start with component testing, then integration, finally end-to-end
2. **Multiple Trials**: Run each test multiple times due to non-determinism
3. **Diverse Metrics**: Combine accuracy, latency, cost, and safety metrics
4. **Real-World Data**: Test with production-like scenarios
5. **Continuous Monitoring**: Evaluate in production, not just pre-deployment
6. **Human Oversight**: Include human review for critical applications

### **LangChain Evaluation Framework**

```python
# Automated test chains for reasoning quality
from langchain.evaluation import load_evaluator

# Create reasoning evaluator
reasoning_evaluator = load_evaluator("criteria", criteria="reasoning")

# Evaluate agent's reasoning
result = reasoning_evaluator.evaluate_strings(
    prediction=agent_output,
    input=user_query,
    criteria="The response demonstrates clear, logical reasoning"
)
```

**Example: LLM-as-a-Judge with Two Modes**

```python
# Mode 1: Reference-Free (helpfulness, clarity, relevance)
reference_free = load_evaluator(
    "criteria",
    criteria={
        "helpfulness": "Is the response helpful to the user?",
        "clarity": "Is the response clear and well-organized?",
        "relevance": "Does the response address the user's question?"
    }
)

score = reference_free.evaluate_strings(
    prediction=agent_response,
    input=user_query
)

# Mode 2: Reference-Aware (correctness vs gold answer)
reference_aware = load_evaluator(
    "labeled_criteria",
    criteria="correctness"
)

score = reference_aware.evaluate_strings(
    prediction=agent_response,
    reference=gold_standard_answer,
    input=user_query
)
```

**Running the Example** (requires Anthropic API key):
```bash
# Set API key
export ANTHROPIC_API_KEY="your-api-key"

# Install dependencies (in virtual environment!)
source bert_env/bin/activate
pip install langchain langchain-anthropic

# Run evaluation
python examples/langchain_claude_eval.py
```

### **Additional Agent Evaluation Tools**

- **Langfuse**: Open-source tracing and observability - [langfuse.com](https://langfuse.com/)
- **Arize AI**: ML + LLM observability platform - [arize.com](https://arize.com/)
- **Weights & Biases**: Experiment tracking for agents - [wandb.ai](https://wandb.ai/)
- **MLflow**: LLM evaluation framework - [mlflow.org/llm-evaluation](https://mlflow.org/llm-evaluation)

## What is BERT?

**BERT** (Bidirectional Encoder Representations from Transformers) is a natural language processing (NLP) model developed by Google. BERT uses a deep neural network architecture called a **Transformer** to interpret the context and meaning of words in text.

## How does the BERT model work for text classification?

### 1. **Architecture**
BERT is built on the **Transformer architecture**, which relies on:
- **Multi-Head Self-Attention**: Allows the model to focus on different parts of the input sequence simultaneously
- **Feed-Forward Neural Networks**: Process the attention outputs
- **Layer Normalization**: Stabilizes training
- **Positional Encodings**: Help the model understand word order

### 2. **Attention mechanism in Transformers**
The **attention mechanism** is the core innovation of Transformers:
- **Self-Attention**: Each word in the sequence attends to every other word, creating rich contextual representations
- **Multi-Head Attention**: Multiple attention mechanisms run in parallel, capturing different types of relationships
- **Query-Key-Value**: Each word is transformed into query (Q), key (K), and value (V) vectors
- **Attention Weights**: Computed as: `Attention(Q,K,V) = softmax(QK^T/√d_k)V`

### 3. **Text Classification process**
1. **Input Tokenization**: Text is converted to token IDs using WordPiece tokenization
2. **Embedding**: Tokens are converted to dense vector representations
3. **Transformer Layers**: 12 layers (BERT-base) or 24 layers (BERT-large) process the embeddings
4. **[CLS] Token**: Special classification token whose final representation is used for classification
5. **Classification Head**: A simple linear layer maps BERT output to class probabilities

### 4. **Fine-tuning process**
Fine-tuning adapts the pre-trained BERT model to specific classification tasks:
- **Transfer Learning**: Start with pre-trained BERT weights
- **Task specific layer**: Add a classification head for your specific number of classes
- **End-to-end training**: Update all model parameters using labeled data from your domain
- **Lower Learning Rate**: Use smaller learning rates (2e-5) to preserve pre-trained knowledge

## Project

```
EVALUATION/TOOLS/
├── README.md                 # This documentation
├── .gitignore               # Git ignore file for Python projects
├── .dockerignore            # Docker ignore patterns
├── requirements.txt         # Core dependencies
├── requirements-api.txt     # API-specific dependencies
├── requirements-evaluation.txt # Evaluation tools dependencies
├── bert_env/                # Virtual environment (excluded from git)
├── src/
│   ├── bert_fine_tuning.py  # Main BERT fine-tuning script
│   ├── minimal_bert.py      # Simplified BERT implementation
│   ├── bert_evaluation.py   # Evaluation with LLM metrics
│   ├── geval_integration.py # G-Eval LLM-as-a-judge implementation
│   ├── test_environment.py  # Environment verification script
│   └── test_evaluation_setup.py # Evaluation tools test
├── evaluation_examples/      # 🆕 LLM Evaluation Framework
│   ├── comprehensive_demo.py # Master demo showcasing all 5 frameworks
│   ├── integration_test.py  # Integration testing suite
│   ├── installation_guide.md # Installation instructions
│   ├── deepeval_example.py  # DeepEval production testing example
│   ├── geval_example.py     # G-Eval LLM-as-a-judge example
│   ├── llmebench_example.py # LLMeBench multi-lingual benchmarking
│   ├── langsmith_example.py # LangSmith observability platform
│   ├── ragas_example.py     # Ragas RAG evaluation toolkit
│   ├── deploy_deepeval_aws.sh   # AWS deployment for DeepEval
│   ├── deploy_geval_aws.sh      # AWS deployment for G-Eval
│   ├── deploy_llmebench_aws.sh  # AWS deployment for LLMeBench
│   ├── deploy_langsmith_aws.sh  # AWS deployment for LangSmith
│   ├── install_llmebench.sh     # LLMeBench installation script
│   └── *.json, *.txt        # Generated reports and results
├── api.py                   # FastAPI backend server
├── test_setup.py            # Environment verification script
├── test_model.py            # Model evaluation suite
├── test_api.sh              # API testing script with curl commands
├── examples.py              # Usage examples and guides
├── project_summary.py       # Project overview
├── demo_evaluation.py       # Basic evaluation tools demonstration
├── test_imports.py          # Import verification test
├── quick_bert_test.py       # Quick BERT setup verification
├── setup_evaluation.sh      # Automated evaluation setup script
├── test_evaluation_tools.py # Evaluation tools testing
├── simple_test.py           # Simple functionality test
├── status_report.py         # Project status generator
├── modern_optimizers_guide.py # Modern optimizers demonstration
├── optimizer_demo.py        # Optimizer comparison examples
├── optimizer_status_report.py # Optimizer performance reports
├── Dockerfile               # Docker container configuration
├── docker-compose.yml       # Docker Compose setup
├── docker_deploy.sh         # Docker deployment script
├── nginx.conf               # Nginx reverse proxy config
└── fine_tuned_bert/         # Saved model directory (created after training)
```

## Setup

### 1. Create Python virtual environment
```bash
python3 -m venv bert_env
source bert_env/bin/activate  # On Linux/Mac
```

### 2. Install dependencies
```bash
pip install torch transformers scikit-learn numpy pandas
```

### 3. Verify setup
```bash
python test_setup.py
```

### 4. Run fine-tuning
```bash
python src/bert_fine_tuning.py
```

### 5. Start FastAPI server
```bash
# Install API dependencies
pip install -r requirements-api.txt

# Start the API server
python api.py
# or using uvicorn directly
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### 6. Test API Endpoints
```bash
# Run comprehensive API tests
./test_api.sh

# Or test manually with curl
curl -X POST "http://localhost:8000/classify" \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this product!", "return_confidence": true}'
```

## FastAPI backend server

This project includes **FastAPI** backend that provides REST API endpoints for text classification using the fine-tuned BERT model.

> **For detailed API documentation, examples, and troubleshooting, see the auto-generated docs at [http://localhost:8000/docs](http://localhost:8000/docs) when the server is running**

### API
- **RESTful Endpoints**: Standard HTTP methods for text classification
- **Single & batch processing**: Classify one text or multiple texts at once
- **Confidence scores**: Optional confidence values for predictions
- **Health monitoring**: Health check and model status endpoints
- **Documentation**: Auto-generated API docs with Swagger UI
- **CORS**: Cross-Origin Resource Sharing enabled
- **Error handling**: Comprehensive error responses and logging
- **Performance metrics**: Processing time tracking

### API Endpoints

#### 1. **Root Endpoint**
```bash
GET /
# Returns basic API information
```

#### 2. **Health Check**
```bash
GET /health
# Returns API and model health status
curl http://localhost:8000/health
```

#### 3. **Model information**
```bash
GET /model/info
# Returns detailed model information
curl http://localhost:8000/model/info
```

#### 4. **Text Classification (Single)**
```bash
POST /classify
# Classify a single text
curl -X POST "http://localhost:8000/classify" \
  -H "Content-Type: application/json" \
  -d '{"text": "I absolutely love this product!", "return_confidence": true}'

# Response:
{
  "text": "I absolutely love this product!",
  "prediction": 1,
  "label": "positive",
  "confidence": 0.9876,
  "processing_time_ms": 45.23
}
```

#### 5. **Text Classification (Batch)**
```bash
POST /classify/batch
# Classify multiple texts at once
curl -X POST "http://localhost:8000/classify/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["Great product!", "Terrible service.", "It was okay."],
    "return_confidence": true
  }'

# Response:
{
  "results": [
    {
      "text": "Great product!",
      "prediction": 1,
      "label": "positive",
      "confidence": 0.9234,
      "processing_time_ms": 42.1
    },
    // ... more results
  ],
  "total_texts": 3,
  "total_processing_time_ms": 123.45
}
```

#### 6. **Classifications - Demo**
```bash
GET /classify/demo
# Returns sample classifications for testing
curl http://localhost:8000/classify/demo
```

### Documentation (API)

The FastAPI server automatically generates interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- Browse all available endpoints
- Test API calls directly in the browser
- View request/response schemas
- Download OpenAPI specifications

### Starting the API server

#### Method 1: Python execution
```bash
# Activate virtual environment
source bert_env/bin/activate

# Install API dependencies
pip install -r requirements-api.txt

# Start server
python api.py
```

#### Method 2: Using Uvicorn
```bash
# Development mode with auto-reload
uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# Production mode
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

### Testing the API

#### Automated testing
```bash
# Run comprehensive test suite
./test_api.sh
```

#### Manual testing
```bash
# Basic classification
curl -X POST "http://localhost:8000/classify" \
  -H "Content-Type: application/json" \
  -d '{"text": "This movie was fantastic!"}'

# With confidence scores
curl -X POST "http://localhost:8000/classify" \
  -H "Content-Type: application/json" \
  -d '{"text": "I hate this product.", "return_confidence": true}'

# Batch processing
curl -X POST "http://localhost:8000/classify/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["Amazing service!", "Poor quality.", "Average experience."],
    "return_confidence": true
  }'

# Health check
curl http://localhost:8000/health

# Model information
curl http://localhost:8000/model/info
```

## Docker deployment

The project includes complete **Docker** support for containerized deployment.

### Docker
- **Multi-stage Build**: Optimized container size
- **Security**: Non-root user execution
- **Health Checks**: Container health monitoring
- **Resource Limits**: Memory and CPU constraints
- **Environment Configuration**: Flexible deployment options
- **Nginx Integration**: Optional reverse proxy setup

### Start with Docker

#### 1. **Build and run with Docker**
```bash
# Build the Docker image
docker build -t bert-classifier .

# Run the container
docker run -p 8000:8000 bert-classifier

# Run with custom configuration
docker run -p 8000:8000 \
  -e LOG_LEVEL=debug \
  -v $(pwd)/fine_tuned_bert:/app/fine_tuned_bert:ro \
  bert-classifier
```

#### 2. **Using Docker Compose (Recommended)**
```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down

# Start with nginx (production)
docker-compose --profile production up -d
```

#### 3. **Production deployment**
```bash
# Build and run with nginx reverse proxy
docker-compose --profile production up -d

# Scale the API service
docker-compose up -d --scale bert-api=3
```

### Docker configuration

#### **Dockerfile**
The Dockerfile includes:
- Python 3.11 slim base image
- System dependencies installation
- Python package installation with caching
- Non-root user for security
- Health check configuration
- Optimized layer caching

#### **Docker Compose**
The docker-compose.yml provides:
- API service configuration
- Port mapping (8000:8000)
- Volume mounting for models
- Health checks
- Resource limits
- Optional nginx reverse proxy

#### **Environment variables**
```bash
# Available environment variables
LOG_LEVEL=info          # Logging level
PYTHONPATH=/app         # Python path
MODEL_PATH=/app/fine_tuned_bert  # Custom model path
```

### Docker deployment options

#### **Development**
```bash
# Basic development setup
docker-compose up -d
# Access API at http://localhost:8000
```

#### **Production with Load Balancer**
```bash
# Production setup with nginx
docker-compose --profile production up -d
# Access API through nginx at http://localhost:80
```

#### **Kubernetes deployment**
```yaml
# kubernetes-deployment.yaml (example)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bert-classifier
spec:
  replicas: 3
  selector:
    matchLabels:
      app: bert-classifier
  template:
    metadata:
      labels:
        app: bert-classifier
    spec:
      containers:
      - name: bert-classifier
        image: bert-classifier:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "2Gi"
            cpu: "500m"
          limits:
            memory: "4Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: bert-classifier-service
spec:
  selector:
    app: bert-classifier
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Container health monitoring

#### **Health Check Endpoint**
```bash
# Check container health
curl http://localhost:8000/health

# Docker health status
docker ps
# Look for "healthy" status
```

#### **Monitoring commands**
```bash
# View container logs
docker logs <container_id>

# Monitor resource usage
docker stats <container_id>

# Execute commands inside container
docker exec -it <container_id> /bin/bash
```

### Troubleshooting Docker

#### **Problems**
```bash
# Container not starting
docker logs <container_id>

# Port already in use
docker ps | grep 8000
sudo netstat -tulpn | grep 8000

# Model not loading
# Ensure fine_tuned_bert directory exists
ls -la fine_tuned_bert/

# Memory issues
# Increase Docker memory limits
# Or use smaller models like DistilBERT
```

#### **Performance optimization**
```bash
# Use multi-stage builds
# Enable Docker BuildKit
DOCKER_BUILDKIT=1 docker build -t bert-classifier .

# Use .dockerignore to exclude unnecessary files
# Optimize layer caching by copying requirements first
```

## LLM Evaluation Metrics

### Why Do We Need LLM Evaluation Metrics?

Evaluating Large Language Models (LLMs) is essential to ensure models are reliable, accurate, and safe before deploying applications in production. Metrics help quantify model performance, guide improvements, and ensure alignment with user and business requirements.

### Categories of LLM Evaluation Metrics

LLM evaluation metrics fall into several categories:

- **Language Modeling Metrics (Statistical):**
  Measure how well a model predicts text, typically at the token or sequence level.
  *Example:* Perplexity (PPL).

- **Lexical Overlap Metrics:**
  Compare n-grams or word overlaps between generated and reference texts.
  *Examples:* BLEU, ROUGE, METEOR, CIDEr.

- **Embedding-Based Metrics:**
  Use semantic embeddings (e.g., BERT) to measure similarity beyond exact word matches.
  *Examples:* BERTScore, MoverScore.

- **Learned Metrics:**
  Neural models fine-tuned on human judgments to predict quality scores.
  *Example:* BLEURT.

- **Task-Specific Metrics:**
  - **Exact Match (EM):** Checks if the predicted answer matches the reference exactly (common in QA tasks).
  - **F1 Score:** Measures overlap between predicted and reference answers.
  - **Accuracy:** Percentage of correct answers.

- **Semantic Similarity Metrics:**
  - **Cosine Similarity:** Compares embeddings of predicted and reference answers.
  - **BERTScore:** Uses BERT embeddings for nuanced semantic comparison.

### Metrics for LLM Accuracy

- **Perplexity:** Measures how well the model predicts the next word; lower is better.
- **Precision, Recall, F1 Score:** Standard metrics for classification and QA tasks.
- **Accuracy:** Fraction of correct predictions.
- **BLEU:** Evaluates n-gram overlap, mainly for translation and summarization.
- **ROUGE:** Focuses on recall, useful for summarization.
- **BERTScore:** Measures semantic similarity using BERT embeddings.

### Tools for Evaluating BERT Models

Several open-source frameworks can assist in evaluating BERT and other LLMs:

1. **DeepEval**
   [GitHub: confident-ai/deepeval](https://github.com/confident-ai/deepeval)
   Open-source LLM evaluation framework for testing and benchmarking LLM systems. Supports automatic and custom metrics.

2. **LLMeBench**
   [GitHub: qcri/LLMeBench](https://github.com/qcri/LLMeBench)
   Provides comparative analyses and benchmarking of LLM models according to industry standards.

3. **G-Eval**
   [GitHub: nlpyang/geval](https://github.com/nlpyang/geval)
   Framework for LLM-as-a-judge evaluation using chain-of-thoughts (CoT) and custom metrics.

4. **BERTScore**
   [Spotintelligence: BERTScore](https://spotintelligence.com/2024/08/20/bertscore/)
   Uses BERT embeddings to measure semantic similarity between generated and reference texts.

5. **BLEURT**
   Model-based metric using transformer representations for scoring LLM outputs.

## Training and Evaluation Metrics

#### 1. **Training metrics**
- **Loss Reduction**: Training loss should decrease over epochs
- **Convergence**: Loss should stabilize (not oscillate wildly)
- **No Overfitting**: Validation loss shouldn't increase while training loss decreases

#### 2. **Basic evaluation metrics**
- **Accuracy**: Percentage of correctly classified samples
- **Precision**: True positives / (True positives + False positives)
- **Recall**: True positives / (True positives + False negatives)
- **F1-Score**: Harmonic mean of precision and recall

#### 3. **Test cases**
```python
# Example test cases
test_cases = [
    ("I love this product!", 1),      # Positive
    ("This is terrible quality", 0),   # Negative
    ("Average experience", ???),       # Neutral - check model confidence
]
```

## Model Performance Evaluation

### 1. **Validation split**
- Split data into training (80%), validation (10%), test (10%)
- Use validation set to tune hyperparameters
- Use test set for final performance evaluation

### 2. **Cross validation**
- K-fold cross-validation for robust performance estimates
- Helps detect overfitting and ensures generalization

### 3. **Confusion matrix**
- Visualize classification performance across all classes
- Identify which classes are being confused

### 4. **Classification report**
```python
from sklearn.metrics import classification_report
print(classification_report(y_true, y_pred))
```

## LLM Evaluation Tools Integration

### Setup Evaluation Environment

#### Quick Setup
```bash
# Run the automated setup script
./setup_evaluation.sh
```

### Manual Setup
```bash
# Activate virtual environment
source bert_env/bin/activate

# Install evaluation tools
pip install -r requirements-evaluation.txt

# Verify installation
python src/test_environment.py
```

## Evaluation Tools

### 1. **DeepEval Framework**
[GitHub: confident-ai/deepeval](https://github.com/confident-ai/deepeval)

DeepEval provides comprehensive LLM evaluation metrics including:
- Answer Relevancy
- Faithfulness
- Contextual Precision/Recall
- Hallucination Detection
- Bias Assessment

```bash
# Install DeepEval
pip install deepeval

# Run evaluation
python src/bert_evaluation.py
```

### 2. **BERTScore Integration**
[Documentation: BERTScore](https://spotintelligence.com/2024/08/20/bertscore/)

Semantic similarity evaluation using BERT embeddings:
```python
from bert_score import BERTScorer
scorer = BERTScorer(lang="en", rescale_with_baseline=True)
P, R, F1 = scorer.score(predictions, references)
```

### 3. **G-Eval Implementation**
[Paper: G-Eval NLG Evaluation](https://github.com/nlpyang/geval)

LLM-as-a-judge evaluation with chain-of-thoughts:
```bash
# Set OpenAI API key for G-Eval
export OPENAI_API_KEY="your-api-key"

# Run G-Eval
python src/geval_integration.py
```

### 4. **ROUGE and BLEU Metrics**
Traditional text similarity metrics:
```python
# ROUGE scores
from rouge_score import rouge_scorer
scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'])

# BLEU scores
import sacrebleu
bleu = sacrebleu.corpus_bleu(predictions, references)
```

### Evaluation Pipeline

#### Run Evaluation
```bash
# Activate environment
source bert_env/bin/activate

# Run BERT fine-tuning (if not done already)
python src/bert_fine_tuning.py

# Run comprehensive evaluation
python src/bert_evaluation.py
```

### Evaluation Features
- **Traditional Metrics**: Accuracy, Precision, Recall, F1-Score
- **Semantic Metrics**: BERTScore, ROUGE, BLEU
- **LLM-based Metrics**: DeepEval suite, G-Eval
- **Visualization**: Automated plots and charts
- **Export**: JSON results and evaluation reports

#### Sample Evaluation Output
```json
{
  "traditional_metrics": {
    "accuracy": 0.857,
    "f1_score": 0.851,
    "precision": 0.863,
    "recall": 0.847
  },
  "bertscore": {
    "bertscore_f1": 0.832,
    "bertscore_precision": 0.828,
    "bertscore_recall": 0.836
  },
  "rouge": {
    "rouge1_fmeasure_mean": 0.745,
    "rouge2_fmeasure_mean": 0.623,
    "rougeL_fmeasure_mean": 0.712
  },
  "deepeval": {
    "answer_relevancy_mean": 4.2,
    "hallucination_mean": 1.8,
    "bias_mean": 2.1
  }
}
```

### Evaluation Practices

#### 1. **Multi-Metric Evaluation**
```python
# Use multiple metrics for comprehensive assessment
evaluator = BERTEvaluator(model_path="./fine_tuned_bert")
results = evaluator.evaluate_comprehensive(test_data)
```

#### 2. **Cross-Validation**
```python
# Implement k-fold cross-validation
from sklearn.model_selection import KFold
kfold = KFold(n_splits=5, shuffle=True, random_state=42)
```

#### 3. **Error Analysis**
```python
# Analyze prediction errors
confusion_matrix = results["traditional_metrics"]["confusion_matrix"]
# Identify misclassified samples for improvement
```

#### 4. **Confidence Calibration**
```python
# Assess model confidence appropriateness
avg_confidence = results["traditional_metrics"]["avg_confidence"]
# Check if confidence correlates with accuracy
```

### Integration with Production

#### Model Monitoring
```python
# Set up continuous evaluation
def monitor_model_performance(new_data):
    evaluator = BERTEvaluator(model_path="./fine_tuned_bert")
    results = evaluator.evaluate_traditional_metrics(
        new_data['texts'],
        new_data['labels']
    )
    return results
```

#### A/B Testing Framework
```python
# Compare model versions
def compare_models(model_a_path, model_b_path, test_data):
    evaluator_a = BERTEvaluator(model_a_path)
    evaluator_b = BERTEvaluator(model_b_path)
    
    results_a = evaluator_a.evaluate_comprehensive(test_data)
    results_b = evaluator_b.evaluate_comprehensive(test_data)
    
    return compare_results(results_a, results_b)
```

### Troubleshooting

#### Issues
```bash
# OpenAI API key for G-Eval
export OPENAI_API_KEY="your-key-here"

# Memory issues with large evaluations
# Reduce batch size or use CPU evaluation

# Missing model error
python src/bert_fine_tuning.py  # Train model first

# AdamW import error (FIXED)
# Issue: ImportError: cannot import name 'AdamW' from 'transformers'
# Solution: Use 'from torch.optim import AdamW' instead
# This has been fixed in the current bert_fine_tuning.py

# Test imports before running
python test_imports.py  # Verify all imports work
python quick_bert_test.py  # Quick BERT functionality test
```

## Optimizers (2026)

The choice of optimizer significantly impacts BERT fine-tuning performance. Here are the **optimizer options** available in your environment.

### **Available Optimizers**
```python
# 1. RECOMMENDED: torch.optim.AdamW (Default Choice)
from torch.optim import AdamW
optimizer = AdamW(model.parameters(), lr=2e-5, weight_decay=0.01)

# 2. MEMORY EFFICIENT: transformers.Adafactor
from transformers.optimization import Adafactor
optimizer = Adafactor(model.parameters(), scale_parameter=False,
                      relative_step=False, lr=1e-3)

# 3. SELF-CORRECTING: torch.optim.RAdam
from torch.optim import RAdam
optimizer = RAdam(model.parameters(), lr=2e-5, weight_decay=0.01)

# 4. SPARSE DATA: torch.optim.Adamax
from torch.optim import Adamax
optimizer = Adamax(model.parameters(), lr=2e-3, weight_decay=0.01)
```

### **Optimizer Comparison Table**
| Optimizer     | Memory Usage | Stability    | Performance | Best For                          |
|---------------|--------------|--------------|-------------|-----------------------------------|
| **AdamW**     | Medium       | ⭐⭐⭐⭐⭐   | ⭐⭐⭐⭐⭐ | General BERT fine-tuning          |
| **Adafactor** | High         | ⭐⭐⭐       | ⭐⭐⭐⭐   | Large models, memory constraints  |
| **RAdam**     | Medium       | ⭐⭐⭐⭐⭐   | ⭐⭐⭐⭐   | Self-correcting, no warmup needed |
| **Adamax**    | Medium       | ⭐⭐⭐       | ⭐⭐⭐     | Sparse gradients, unstable data   |

### **Usage Recommendations**

**Default Choice**: Use `torch.optim.AdamW`
```python
from torch.optim import AdamW
from transformers import get_linear_schedule_with_warmup

optimizer = AdamW(model.parameters(), lr=2e-5, weight_decay=0.01, eps=1e-8)
scheduler = get_linear_schedule_with_warmup(optimizer,
                                          num_warmup_steps=100,
                                          num_training_steps=1000)
```

**Memory Constrained**: Use `Adafactor` for large models
```python
from transformers.optimization import Adafactor

optimizer = Adafactor(model.parameters(),
                      scale_parameter=False,
                      relative_step=False,
                      warmup_init=False,
                      lr=1e-3)
```

**Research/Stability**: Use `RAdam` for self-correcting behavior
```python
from torch.optim import RAdam

optimizer = RAdam(model.parameters(), lr=2e-5, weight_decay=0.01)
# No manual warmup needed - RAdam handles it internally
```

### **Fine-tuning Template**
```python
def create_modern_optimizer(model, optimizer_type="adamw", lr=2e-5):
    """Create modern optimizer for BERT fine-tuning"""
    
    if optimizer_type == "adamw":
        from torch.optim import AdamW
        return AdamW(model.parameters(), lr=lr, weight_decay=0.01)
        
    elif optimizer_type == "adafactor":
        from transformers.optimization import Adafactor
        return Adafactor(model.parameters(), scale_parameter=False, 
                        relative_step=False, lr=lr)
                        
    elif optimizer_type == "radam":
        from torch.optim import RAdam
        return RAdam(model.parameters(), lr=lr, weight_decay=0.01)
        
    elif optimizer_type == "adamax":
        from torch.optim import Adamax
        return Adamax(model.parameters(), lr=lr*10, weight_decay=0.01)
        
    else:
        raise ValueError(f"Unknown optimizer: {optimizer_type}")

# Usage
optimizer = create_modern_optimizer(model, "adamw", lr=2e-5)
```

#### Performance Optimization
```bash
# Use GPU for faster evaluation
CUDA_VISIBLE_DEVICES=0 python src/bert_evaluation.py

# Parallel evaluation for large datasets
# Modify batch processing in evaluation script
```

### Quick Start

#### Demo (Recommended)
```bash
# Run complete evaluation framework demonstration
python evaluation_examples/comprehensive_demo.py

# Or run integration test to verify setup
python evaluation_examples/integration_test.py
```
This demo showcases all 5 evaluation frameworks and checks your environment setup.

#### 🛠️ **Individual Framework Examples**
```bash
# DeepEval - Production LLM Testing
python evaluation_examples/deepeval_example.py

# G-Eval - LLM-as-a-Judge Framework
python evaluation_examples/geval_example.py

# LLMeBench - Multi-lingual Benchmarking
python evaluation_examples/llmebench_example.py

# LangSmith - Production Observability
python evaluation_examples/langsmith_example.py

# Ragas - RAG Application Evaluation
python evaluation_examples/ragas_example.py
```

#### 📦 **Installation Guide**
See detailed instructions in `evaluation_examples/installation_guide.md` for:
- Framework-specific installation commands
- API key setup (OpenAI, LangChain)
- AWS deployment prerequisites
- Troubleshooting common issues

#### 1. **Environment Setup**
```bash
# Clone and navigate to project
cd "path/to/your/project"

# Create and activate virtual environment
python3 -m venv bert_env
source bert_env/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-evaluation.txt

# Test setup
python src/test_evaluation_setup.py
```

#### 2. **Run Demo Evaluation**
```bash
# Activate environment
source bert_env/bin/activate

# Run evaluation demo (works without trained model)
python demo_evaluation.py
```

#### 3. **Train and Evaluate BERT Model**
```bash
# Train BERT model
python src/bert_fine_tuning.py

# Run comprehensive evaluation
python src/bert_evaluation.py
```

#### 4. **Advanced Evaluation**
```bash
# G-Eval with OpenAI API
export OPENAI_API_KEY="your-api-key"
python src/geval_integration.py

# Install additional tools
pip install deepeval wandb
```

### Evaluation Results Example

The evaluation tools generate comprehensive reports like this:

```json
{
  "traditional_metrics": {
    "accuracy": 0.875,
    "f1_score": 0.871,
    "precision": 0.863,
    "recall": 0.880,
    "avg_confidence": 0.823
  },
  "bertscore": {
    "bertscore_f1": 0.832,
    "bertscore_precision": 0.828,
    "bertscore_recall": 0.836
  },
  "rouge": {
    "rouge1_f1": 0.475,
    "rouge2_f1": 0.294,
    "rougeL_f1": 0.475
  },
  "bleu": {
    "bleu_score": 15.2
  }
}
```

### Tools & Metrics Status

**Basic BERT Pipeline**: Fine-tuning script ready
**Traditional Metrics**: Accuracy, Precision, Recall, F1-Score
**Semantic Metrics**: BERTScore, ROUGE, BLEU integration
**Visualization**: Automated plotting and reporting
**G-Eval Integration**: LLM-as-a-judge evaluation
**DeepEval**: Optional (requires separate installation)
**LLMeBench**: Requires manual setup

The evaluation framework is ready-to-use and LLM model assessment uses industry-standard metrics.

## Model Prediction Testing

### 1. **Inference function**
```python
def predict_sentiment(text, model, tokenizer):
    inputs = tokenizer(text, return_tensors="pt", 
                      padding=True, truncation=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
        prediction = torch.argmax(outputs.logits, dim=-1)
    return prediction.item()
```

### 2. **Batch prediction**
- Process multiple texts efficiently
- Monitor prediction confidence scores
- Handle edge cases and out-of-domain text

### 3. **Model interpretability**
- Use attention visualization to understand model decisions
- Analyze which words contribute most to predictions
- Test with adversarial examples

## Advanced topics

### **Model variants**
- RoBERTa: Robustly Optimized BERT
- DistilBERT: Smaller, faster BERT
- ALBERT: A Lite BERT
- DeBERTa: Decoding-enhanced BERT

### **Production deployment**
- **Model quantization for faster inference**: Reduce model size and inference time
- **ONNX export for cross-platform deployment**: Convert to ONNX format for broader compatibility
- **API endpoints with FastAPI/Flask**: RESTful services for integration
- **Docker containerization**: Scalable deployment with container orchestration
- **Monitoring and logging in production**: Track performance and detect issues
- **Load balancing and auto-scaling**: Handle high traffic loads
- **Security considerations**: Authentication, rate limiting, and input validation

## References

### **AI Agent Evaluation Resources**

#### **Core Agent Evaluation Guides**
- **Anthropic: Demystifying Evals for AI Agents**: [anthropic.com/engineering/demystifying-evals-for-ai-agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
  - Comprehensive guide on agent evaluation strategies and best practices
- **Microsoft Copilot Studio: How to Evaluate AI Agents**: [microsoft.com/copilot/how-to-evaluate-ai-agents](https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/how-to-evaluate-ai-agents/)
  - Agent evaluation in 5 steps: define criteria, create datasets, implement evaluation, monitor, iterate
- **MLflow LLM Evaluation Guide**: [mlflow.org/llm-evaluation](https://mlflow.org/llm-evaluation)
  - LLM vs Agent evaluation differences and measurement frameworks
- **Fast.io: Best Tools for AI Agent Testing**: [fast.io/resources/best-tools-ai-agent-testing](https://fast.io/resources/best-tools-ai-agent-testing/)
  - Comprehensive comparison of agent testing tools

#### **Agent Evaluation Platforms (2026)**
- **Braintrust**: Human-in-the-loop evaluation platform - [braintrustdata.com](https://www.braintrustdata.com)
- **Maxim AI**: End-to-end evaluation and simulation - [getmaxim.ai](https://www.getmaxim.ai)
- **Langfuse**: Open-source tracing and observability - [langfuse.com](https://langfuse.com/)
- **Arize AI**: ML + LLM observability platform - [arize.com](https://arize.com/)
- **Weights & Biases**: Experiment tracking - [wandb.ai](https://wandb.ai/)

### **Core Documentation**
- **API Documentation**: [Auto-generated Swagger UI](http://localhost:8000/docs) (when server is running)
- **Installation Guide**: [evaluation_examples/installation_guide.md](./evaluation_examples/installation_guide.md)
- **Comprehensive Demo**: [evaluation_examples/comprehensive_demo.py](./evaluation_examples/comprehensive_demo.py)
- **Integration Tests**: [evaluation_examples/integration_test.py](./evaluation_examples/integration_test.py)

### **Open-Source Agent Evaluation Tools**

#### **1. Arize Phoenix - Agent Observability**
- **Repository**: [Arize-ai/phoenix](https://github.com/Arize-ai/phoenix)
- **Documentation**: [docs.arize.com/phoenix](https://docs.arize.com/phoenix)
- **Website**: [phoenix.arize.com](https://phoenix.arize.com/)
- **PyPI**: [pip install arize-phoenix](https://pypi.org/project/arize-phoenix/)
- **Features**: Agent trace visualization, performance tracking, debugging tools

#### **2. Comet Opik - LLM Evaluation Platform**
- **Repository**: [comet-ml/opik](https://github.com/comet-ml/opik)
- **Documentation**: [comet.com/docs/opik](https://www.comet.com/docs/opik)
- **Website**: [comet.com/opik](https://www.comet.com/site/products/opik/)
- **PyPI**: [pip install opik](https://pypi.org/project/opik/)
- **Features**: Trace instrumentation, tool use logging, evaluation metrics

### **LLM Evaluation Tools (2026)**

#### **1. DeepEval - Production LLM Testing**
- **Repository**: [confident-ai/deepeval](https://github.com/confident-ai/deepeval)
- **Documentation**: [deepeval.com/docs/metrics-llm-evals](https://deepeval.com/docs/metrics-llm-evals)
- **Documentation (Confident AI)**: [docs.confident-ai.com](https://docs.confident-ai.com)
- **PyPI**: [pip install deepeval](https://pypi.org/project/deepeval/)
- **Example**: [evaluation_examples/deepeval_example.py](./evaluation_examples/deepeval_example.py)

#### **2. G-Eval - LLM-as-a-Judge Framework**
- **Repository**: [nlpyang/geval](https://github.com/nlpyang/geval)
- **Paper**: [G-Eval: NLG Evaluation using GPT-4](https://arxiv.org/abs/2303.16634)
- **OpenAI API**: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Example**: [evaluation_examples/geval_example.py](./evaluation_examples/geval_example.py)

#### **3. LLMeBench - Multi-Lingual Benchmarking**
- **Repository**: [qcri/LLMeBench](https://github.com/qcri/LLMeBench)
- **Documentation**: [llmebench.qcri.org](https://llmebench.qcri.org)
- **Paper**: [LLMeBench: A Flexible Framework for Accelerating LLMs Benchmarking](https://arxiv.org/abs/2308.04945)
- **Example**: [evaluation_examples/llmebench_example.py](./evaluation_examples/llmebench_example.py)

#### **4. LangSmith - Production Observability**
- **Repository**: [langchain-ai/langsmith-sdk](https://github.com/langchain-ai/langsmith-sdk)
- **Documentation**: [docs.smith.langchain.com](https://docs.smith.langchain.com/evaluation)
- **Platform**: [smith.langchain.com](https://smith.langchain.com)
- **API Keys**: [langchain.com/langsmith](https://www.langchain.com/langsmith)
- **Example**: [evaluation_examples/langsmith_example.py](./evaluation_examples/langsmith_example.py)

#### **5. Ragas - RAG Application Evaluation**
- **Repository**: [explodinggradients/ragas](https://github.com/explodinggradients/ragas)
- **Documentation**: [docs.ragas.io](https://docs.ragas.io/en/stable/)
- **PyPI**: [pip install ragas](https://pypi.org/project/ragas/)
- **Example**: [evaluation_examples/ragas_example.py](./evaluation_examples/ragas_example.py)

#### **6. LM Evaluation Harness - Academic Benchmarking**
- **Repository**: [EleutherAI/lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness)
- **Documentation**: [github.com/EleutherAI/lm-evaluation-harness/tree/main/docs](https://github.com/EleutherAI/lm-evaluation-harness/tree/main/docs)
- **Leaderboard**: [huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard](https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard)

### **Traditional Evaluation Metrics**
- **BERTScore**: [huggingface.co/spaces/evaluate-metric/bertscore](https://huggingface.co/spaces/evaluate-metric/bertscore)
- **BERTScore Guide**: [spotintelligence.com/bertscore](https://spotintelligence.com/2024/08/20/bertscore/)
- **ROUGE**: [github.com/google-research/google-research/tree/master/rouge](https://github.com/google-research/google-research/tree/master/rouge)
- **BLEU**: [github.com/mjpost/sacrebleu](https://github.com/mjpost/sacrebleu)
- **METEOR**: [aclweb.org/anthology/W05-0909](https://aclweb.org/anthology/W05-0909.pdf)

### **Core Technologies**
- **BERT Paper**: [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- **BERT**: [BERT: Pre-training of Deep Bidirectional Transformers](https://arxiv.org/abs/1810.04805)
- **Transformers**: [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- **Hugging Face**: [huggingface.co](https://huggingface.co/)
- **PyTorch**: [pytorch.org](https://pytorch.org/)

### **LangChain Resources**
- **LangChain Documentation**: [python.langchain.com](https://python.langchain.com/docs/get_started/introduction)
- **LangChain Evaluation**: [python.langchain.com/docs/guides/evaluation](https://python.langchain.com/docs/guides/productionization/evaluation/)
- **LangChain Anthropic**: [python.langchain.com/docs/integrations/platforms/anthropic](https://python.langchain.com/docs/integrations/platforms/anthropic)

### **Anthropic (Claude) Resources** 
- **Anthropic API Documentation**: [docs.anthropic.com](https://docs.anthropic.com/)
- **Claude Models**: [docs.anthropic.com/claude/docs/models-overview](https://docs.anthropic.com/en/docs/about-claude/models)
- **Tool Use Guide**: [docs.anthropic.com/claude/docs/tool-use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)

### **Cloud Deployment**
- **AWS Lambda**: [docs.aws.amazon.com/lambda](https://docs.aws.amazon.com/lambda/)
- **AWS SageMaker**: [docs.aws.amazon.com/sagemaker](https://docs.aws.amazon.com/sagemaker/)
- **AWS ECS**: [docs.aws.amazon.com/ecs](https://docs.aws.amazon.com/ecs/)
- **Docker**: [docs.docker.com](https://docs.docker.com/)

### **Additional Resources**
- **FastAPI**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com/)
- **Text Classification with BERT**: [sabrepc.com/blog/Deep-Learning-and-AI/text-classification-with-bert](https://www.sabrepc.com/blog/Deep-Learning-and-AI/text-classification-with-bert)
- **Modern Optimizers Guide**: [modern_optimizers_guide.py](./modern_optimizers_guide.py)
- **LLM Evaluation Best Practices**: [arxiv.org/abs/2307.03109](https://arxiv.org/abs/2307.03109)

---

## Summary

This project provides evaluation tools for:
-   **Large Language Models (LLMs)**: Traditional metrics and semantic evaluation
-   **AI Agents**: Multi-layered evaluation with tool usage, reasoning, and task completion metrics
-   **MCP Servers & Clients**: Protocol testing and integration validation
-   **Production Deployment**: Docker, FastAPI, monitoring, and observability

**Key Takeaway**: Agent evaluation differs fundamentally from LLM evaluation because agents take actions, use tools, make sequential decisions, and must handle failures - requiring assessment beyond text quality to include task completion, tool correctness, and reasoning quality.

**Remember**: Always activate the virtual environment before running any commands!
