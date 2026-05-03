# AI/Agents/ML Pipeline

This repository contains machine learning pipelines built with different orchestration tools: **Apache Airflow**, **Dagster**, **Kubeflow**, and **MLflow**. Each implementation demonstrates best practices for building, deploying, and managing AI workflows on both local environments and Amazon AWS cloud infrastructure.

## Introduction

Pipeline tools like Apache Airflow and Dagster adapt the pre-training of Large Language Models (LLMs) on the cloud by orchestrating complex, distributed, and long-running workflows across ephemeral cloud infrastructure. They act as the "glue" between data ingestion, data preprocessing, model training on GPU clusters, and model artifact management. While Airflow is "task-centric" and often used for scheduling batch jobs, Dagster is "asset-centric," providing better visibility into data lineage and training artifacts (e.g., tokenized datasets, checkpoints).

Dagster is popular for LLM development due to its "asset-based" model, which allows engineers to treat trained models as data assets, improving reproducibility. Airflow remains a strong standard for organizations needing to merge traditional ETL workflows with new AI training pipelines due to its mature, expansive ecosystem.

### 1. Cloud Native Orchestration & Scaling

▸ **Resource allocation**: Both tools leverage Kubernetes, enabling them to spin up large GPU clusters (like AWS EC2, GCP Compute Engine) only when needed, and shutting them down to save costs.

▸ **Cloud integrations**: They natively integrate with cloud storage (S3, GCS) for storing terabytes of pre-training data and model checkpoints, and with training services like Databricks, AWS SageMaker, or Ray.

### 2. Managing Pre-Training Complexity

▸ **Data preprocessing pipelines**: They manage heavy ETL processes (e.g., using Spark or Ray) to clean, filter, and tokenize massive datasets (Common Crawl, Wikipedia) before training begins.

▸ **Asset lineage (Dagster)**: Dagster tracks the "software-defined assets" (raw data → clean data → tokenized data → trained model). If a dataset changes, Dagster knows exactly which models need retraining.

### LLM Pre-Training Workflow

▪ **Ingestion**: Airflow/Dagster triggers Spark jobs to collect data from web scrapes.
▪ **Transformation**: Data is cleaned, deduplicated, and converted to parquet files.
▪ **Tokenization**: Large datasets are tokenized using Spark/Ray, storing output on S3.
▪ **Training**: The orchestrator launches a Kubernetes pod or interacts with SageMaker to start the multi-node GPU pre-training job.
▪ **Monitoring**: The tool tracks the job status and logs artifacts (loss, learning rate) via integration with MLflow or Weights & Biases.
▪ **Cleanup**: Setup and teardown tasks release the GPU instances after training.

### References

- [Apache Airflow](https://airflow.apache.org/) - Official Airflow documentation
- [Dagster](https://dagster.io/) - Official Dagster documentation
- [AWS SageMaker](https://aws.amazon.com/sagemaker/) - Managed ML service for training and deployment
- [Ray on AWS](https://aws.amazon.com/blogs/opensource/scaling-ai-and-machine-learning-workloads-with-ray-on-aws/) - Scaling AI workloads with Ray
- [LLM experimentation at scale using SageMaker Pipelines and MLflow](https://aws.amazon.com/blogs/machine-learning/llm-experimentation-at-scale-using-amazon-sagemaker-pipelines-and-mlflow/)
- [Weights & Biases](https://wandb.ai/site) - Experiment tracking and model monitoring
- [MLflow](https://mlflow.org/) - Open-source ML lifecycle management
- [LLM training pipelines with Langchain, Airbyte, and Dagster](https://dagster.io/blog/training-llms) - Tutorial on combining LangChain, Airbyte, and Dagster to build maintainable and scalable pipelines for training LLMs: data ingestion via Airbyte, asset orchestration in Dagster, embedding generation, and a retrieval QA application with LangChain
- [ML Pipelines: 5 Components and 5 Critical Best Practices](https://dagster.io/learn/ml) - A guide covering what ML pipelines are, their key components (data ingestion, preprocessing, feature engineering, model training, evaluation, deployment), sequential vs. parallel processing, common challenges, and best practices for orchestrating ML pipelines with Dagster

## 📁 Directory Structure

```
PIPELINE/
├── README.md                 # This file - overview of all pipeline implementations
├── Airflow/                  # Apache Airflow ML pipeline implementation
│   ├── dags/                 # Airflow DAG definitions
│   │   ├── bert_fine_tuning_dag.py
│   │   └── enhanced_bert_fine_tuning_dag.py
│   ├── src/                  # Source code for ML tasks
│   │   ├── bert_fine_tuning.py
│   │   ├── data_wrangling.py
│   │   └── enhanced_bert_training.py
│   ├── config/               # Configuration files
│   ├── data/                 # Training datasets
│   ├── docker-compose.yml    # Local Airflow deployment
│   ├── terraform/            # AWS MWAA infrastructure
│   └── api.py               # FastAPI deployment endpoint
├── Dagster/                  # Dagster ML pipeline implementation
│   ├── dagster_project/      # Main Dagster project
│   ├── src/                  # Pipeline assets and resources
│   ├── aws_config/           # AWS deployment configurations
│   ├── dagster.yaml         # Dagster workspace configuration
│   ├── docker-compose.yml    # Local Dagster deployment
│   └── ARCHITECTURE.md       # Detailed architecture documentation
├── Kubeflow/                 # Kubeflow ML pipeline implementation
│   ├── pipeline/             # Kubeflow pipeline definitions
│   ├── src/                  # ML components and models
│   ├── cloudformation/       # AWS EKS infrastructure
│   ├── terraform/            # Terraform deployment scripts
│   ├── docker-compose.yml    # Local development environment
│   └── Makefile             # Build and deployment automation
└── MLflow/                   # MLflow ML pipeline implementation
    ├── Dataset/              # Fish weight prediction dataset
    ├── notebooks/            # Jupyter notebooks for exploration
    ├── scikit-learn/         # Scikit-learn model implementations
    ├── MLproject            # MLflow project configuration
    ├── conda.yaml           # Conda environment specification
    ├── train.py             # Model training script
    ├── evaluate.py          # Model evaluation script
    └── serve_api.py         # Model serving API
```

## 🔧 Pipeline Implementations

### 🌪️ Apache Airflow
**Focus**: Workflow orchestration and scheduling for BERT model fine-tuning

- **Use Case**: BERT fine-tuning pipeline with automated scheduling, monitoring, and AWS SageMaker integration
- **Key Features**:
  - DAG-based workflow orchestration
  - Integration with AWS MWAA (Managed Workflows for Apache Airflow)
  - Docker containerization support
  - Error handling and retries
  - Model deployment to SageMaker endpoints
- **Best For**: Complex, time-based scheduling requirements and enterprise-grade workflow management
- **AWS Integration**: MWAA, SageMaker, S3, IAM, CloudWatch

### ⚡ Dagster
**Focus**: Asset-centric ML pipeline with strong data lineage and observability

- **Use Case**: BERT training pipeline with emphasis on data assets and lineage tracking
- **Key Features**:
  - Asset-based pipeline definition
  - Built-in data quality checks
  - Rich UI for pipeline monitoring
  - Integration with AWS services
  - Testing framework
- **Best For**: Data-centric workflows requiring strong observability and data lineage
- **AWS Integration**: ECS, S3, SageMaker, EMR, Lambda

### ☸️ Kubeflow
**Focus**: Kubernetes-native ML pipelines with scalable model training and deployment

- **Use Case**: BERT ML pipeline with Kubernetes orchestration for scalability
- **Key Features**:
  - Kubernetes-native pipeline components
  - Distributed training capabilities
  - Model serving with KFServing
  - Integration with cloud ML services
  - Container-based execution
- **Best For**: Cloud-native ML workflows requiring high scalability and Kubernetes expertise
- **AWS Integration**: EKS, SageMaker, S3, ECR, Load Balancers

### 🐟 MLflow
**Focus**: End-to-end ML lifecycle management with experiment tracking and model registry

- **Use Case**: Fish weight prediction with an experiment tracking and model management
- **Key Features**:
  - Experiment tracking and metrics logging
  - Model registry and versioning
  - Multiple algorithm comparison (Linear, Ridge, Lasso, Random Forest)
  - REST API for model serving
  - Integration with various ML frameworks
- **Best For**: Research-oriented workflows requiring extensive experiment tracking and model comparison
- **AWS Integration**: SageMaker, S3, EC2, Model Registry

## Machine Learning (ML) Pipeline Architectures on Amazon AWS

### Apache Airflow on Amazon AWS
- **Orchestration**: AWS MWAA (Managed Workflows for Apache Airflow)
- **Training**: Amazon SageMaker training jobs
- **Storage**: S3 for data and model artifacts
- **Deployment**: SageMaker endpoints with API Gateway
- **Monitoring**: CloudWatch logs and metrics

### Dagster on Amazon AWS
- **Orchestration**: ECS Fargate for Dagster daemon and web server
- **Training**: SageMaker or EMR for distributed processing
- **Storage**: S3 for data lakes and model storage
- **Deployment**: Lambda functions for serverless inference
- **Monitoring**: CloudWatch and Dagster's built-in observability

### Kubeflow on Amazon AWS
- **Orchestration**: Amazon EKS (Elastic Kubernetes Service)
- **Training**: Distributed training across EKS nodes
- **Storage**: EFS for shared storage, S3 for data lakes
- **Deployment**: KFServing on EKS with Application Load Balancer
- **Monitoring**: Kubernetes metrics and CloudWatch Container Insights

### MLflow on Amazon AWS
- **Orchestration**: SageMaker Pipelines with MLflow tracking
- **Training**: SageMaker training jobs with MLflow logging
- **Storage**: S3 for artifacts, RDS for MLflow metadata
- **Deployment**: SageMaker endpoints registered in MLflow Model Registry
- **Monitoring**: MLflow UI with CloudWatch integration

## Choosing the right Pipeline

| Tool | Best For | Learning Curve | AWS Integration | Community |
|------|----------|---------------|-----------------|-----------|
| **Airflow** | Complex scheduling, enterprise workflows | Medium | Excellent (MWAA) | Large |
| **Dagster** | Data-centric pipelines, observability | Medium | Good | Growing |
| **Kubeflow** | Kubernetes-native, scalable ML | High | Good (EKS) | Active |
| **MLflow** | Experiment tracking, model lifecycle | Low | Excellent | Large |


Choose the pipeline that best fits your use case and explore the respective folder for detailed setup instructions.

##  Comparison: ML Pipeline Tools on Amazon AWS

### Apache Airflow + AWS
- **Orchestration**: AWS MWAA provides fully managed Apache Airflow
- **Strengths**: Mature ecosystem, extensive AWS integration, enterprise-ready
- **Use Cases**: Complex workflows, time-based scheduling, enterprise ML pipelines
- **AWS Services**: MWAA, SageMaker, S3, Lambda, EMR, Redshift

### Dagster + AWS 
- **Orchestration**: Asset-centric pipeline orchestration with strong data lineage
- **Strengths**: Modern data pipeline design, built-in testing, excellent observability
- **Use Cases**: Data-centric ML workflows, feature engineering, data quality monitoring
- **AWS Services**: ECS, SageMaker, S3, EMR, Lambda, Redshift

### Kubeflow + AWS
- **Orchestration**: Kubernetes-native ML pipelines on Amazon EKS
- **Strengths**: Cloud-native, highly scalable, container-based execution
- **Use Cases**: Large-scale distributed training, microservices architecture, multi-cloud deployments
- **AWS Services**: EKS, SageMaker, S3, ECR, EFS, Application Load Balancer

### MLflow + AWS
- **Orchestration**: Experiment tracking and model lifecycle management
- **Strengths**: Simple setup, excellent for experimentation, model registry integration
- **Use Cases**: Research workflows, model comparison, experiment tracking, A/B testing
- **AWS Services**: SageMaker (managed MLflow), S3, EC2, RDS, Model Registry

### Ray + AWS
- **Orchestration**: Distributed computing framework for scaling Python and AI workloads
- **Strengths**: High-performance distributed computing, unified API for data/ML/serving
- **Use Cases**: Large-scale data processing, distributed ML training, hyperparameter tuning
- **AWS Services**: EC2, EMR, SageMaker, S3, Ray on SageMaker Hyperpod

## Integration

### Multi-Tool Approaches
- **Ray + MLflow**: Use Ray for distributed training with MLflow for experiment tracking
- **Airflow + MLflow**: Orchestrate MLflow experiments using Airflow DAGs  
- **Kubeflow + MLflow**: Deploy MLflow tracking server on Kubernetes for experiment management
- **Dagster + Ray**: Use Dagster for data pipeline orchestration with Ray for compute-intensive tasks

### Amazon AWS specific patterns
- **SageMaker Integration**: All tools can integrate with SageMaker for managed training and deployment
- **S3 Data Lakes**: Centralized data storage accessible by all pipeline tools
- **IAM Security**: Unified access control across all AWS services
- **CloudWatch Monitoring**: Consistent logging and monitoring across all implementations

## Decision Matrix

| Requirement | Airflow | Dagster | Kubeflow | MLflow | Ray |
|-------------|---------|---------|----------|--------|-----|
| **Ease of Setup** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Scalability** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **AWS Integration** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Data Lineage** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Experiment Tracking** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Production Ready** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Learning Curve** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Community Support** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

## 🤖 AI Agents in ML Pipelines

AI agents represent autonomous systems capable of perceiving their environment, making decisions, and taking actions to achieve specific goals. Integrating AI agents into ML pipelines enables intelligent automation, adaptive workflows, and continuous improvement through feedback loops.

### Agent Development Lifecycle

#### 1. Development Stage
During development, the focus is on rapid iteration, debugging, and establishing a baseline for expected behavior.

**Key Practices:**
- **Tracing**: Implement tracing using SDKs (LangChain, LlamaIndex, OpenAI Agents SDK) or AI proxies to log every step of the agent's decision process:
  - User inputs and prompts
  - Tool calls and function invocations
  - Retrieved context and knowledge base queries
  - Model outputs and reasoning chains
  - Final responses and actions
  
- **Operational Metrics Tracking**: Monitor basic metrics to identify inefficiencies early:
  - Latency per agent request
  - Token usage and API call volumes
  - Tool execution times
  - Memory and compute utilization
  
- **Playground Environment**: Use interactive development environments (e.g., Braintrust, Maxim AI) to:
  - Test prompt variations side-by-side
  - Compare model outputs against test data
  - Debug complex, non-deterministic behaviors
  - Create a "flight recorder" for debugging

**Tools:**
- **LangGraph** (LangChain): Stateful, multi-agent, cyclic, graph-based workflows
- **AutoGen** (Microsoft): Specialized agents for multi-agent conversations
- **CrewAI**: Role-playing, structured agent teams with task coordination
- **Julep**: Agents with long-term memory and complex planning
- **Mastra**: TypeScript-first framework with RAG, memory, and tool-calling
- **Browser Use**: Open-source library for web browser interactions

#### 2. Evaluation Stage
The evaluation stage ensures agents meet predefined quality and safety standards before deployment.

**Key Practices:**
- **Automated Evaluation Suites**: Integrate automated evaluations into CI/CD pipelines:
  - Deterministic checks for objective metrics (e.g., correct JSON output, API response format)
  - "LLM-as-a-judge" systems for subjective qualities (tone, helpfulness, coherence)
  
- **Define Success Criteria**: Establish clear performance thresholds:
  - **Task Success Rate**: Percentage of successfully completed tasks
  - **Hallucination Rate**: Factual correctness and grounding in provided context
  - **Tool Use Accuracy**: Correct tool selection and parameter usage
  - **Safety Metrics**: Toxicity detection, PII handling, bias assessment
  - **Cost Efficiency**: Token usage per task, API call optimization
  
- **Human-in-the-Loop (HITL)**: Use human reviewers for:
  - Nuanced edge cases requiring judgment
  - Calibrating automated evaluators
  - Capturing human feedback into test datasets
  
- **Red Teaming**: Proactively simulate adversarial attacks:
  - Prompt injection attempts
  - Jailbreak scenarios
  - Data exfiltration risks
  - Potential misuse patterns

**Tools:**
- **Ragas**: Specialized evaluation for RAG-based systems
- **Arize Phoenix**: Open-source tracing and evaluation for LLM applications
- **Promptfoo**: Testing and evaluating prompts locally
- **Langfuse**: Tracking, debugging, and analytics for agentic pipelines

#### 3. Deployment Stage
Once in production, monitoring shifts to real-world performance, reliability, and identifying new edge cases.

**Key Practices:**
- **Continuous Monitoring and Alerting**: Track live traffic with real-time dashboards:
  - Performance degradation detection
  - Cost spike alerts
  - Error rate monitoring
  - SLA compliance tracking
  
- **Progressive Rollouts**: Deploy new agent versions gradually:
  - **Canary Releases**: Route small percentage of traffic to new version
  - **Shadow Mode**: Run new agent alongside old, compare outputs without impacting users
  - **A/B Testing**: Compare agent variants on production traffic
  
- **User Feedback Collection**: Implement explicit feedback mechanisms:
  - Thumbs up/down buttons
  - Rating scales
  - Free-form feedback forms
  - Session replay and analysis
  
- **Feedback Loop**: Systematically use production data to improve:
  - Enrich offline test datasets with failure cases
  - Identify unaddressed edge cases
  - Inform next development iteration
  - Create continuous improvement cycle

**Tools:**
- **Braintrust**: Evaluation-driven development with CI/CD and production monitoring
- **Fiddler**: Enterprise governance and compliance features
- **Langfuse**: Open-source tracing, prompt management, cost tracking
- **Galileo**: Real-time, low-cost safety checks and failure detection
- **Arize**: ML observability platform for production monitoring

### Deployment Options

#### Local Deployment
**Docker Compose**:
```yaml
services:
  agent-orchestrator:
    image: langgraph/langgraph-api
    environment:
      - TRACKING_URI=http://mlflow:5000
    ports:
      - "8080:8080"
  
  mlflow:
    image: ghcr.io/mlflow/mlflow
    ports:
      - "5000:5000"
    volumes:
      - mlflow-artifacts:/mlflow
```

**Kubernetes (Minikube/Kind)**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-agent
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: agent
        image: my-agent:latest
        env:
        - name: MLFLOW_TRACKING_URI
          value: "http://mlflow-service:5000"
```

#### Cloud Deployment (AWS)

**Airflow + Agents**:
- Use AWS MWAA to orchestrate agent execution workflows
- Deploy agents as containerized tasks on ECS/Fargate
- Track agent performance with MLflow on SageMaker
- Store agent artifacts in S3

**Kubeflow + Agents**:
- Deploy Kubeflow on Amazon EKS
- Run agent pipelines as Kubeflow components
- Use KServe for serving agent endpoints
- Integrate with SageMaker for model hosting

**MLflow + Agents**:
- Deploy MLflow tracking server on EC2 or ECS
- Use MLflow GenAI capabilities for agent tracking
- Register agent models in MLflow Model Registry
- Deploy agents via SageMaker endpoints

### How to Monitor AI Agent Pipeline Progress?

Monitoring AI agent pipeline progress requires an observability strategy that captures data throughout the agent's lifecycle and a robust evaluation framework to assess performance, quality, and cost.

#### Development Stage Monitoring
**Tracing and Debugging:**
```python
# Example: LangChain with MLflow tracing
import mlflow
from langchain.callbacks import MlflowCallbackHandler

mlflow.set_tracking_uri("http://mlflow-server:5000")
mlflow_handler = MlflowCallbackHandler()

# Your agent code with automatic tracing
agent.run("Task description", callbacks=[mlflow_handler])
```

**Key Metrics to Track:**
- Prompt tokens, completion tokens, total tokens
- Latency per agent step
- Tool call counts and execution times
- Cache hit rates
- Error rates by type

#### Evaluation Stage Monitoring
**CI/CD Integration:**
```python
# Example: Automated evaluation in CI/CD
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy

# Run evaluation suite
results = evaluate(
    dataset=test_dataset,
    metrics=[faithfulness, answer_relevancy],
    llm=evaluation_llm
)

# Fail pipeline if below threshold
assert results["faithfulness"] > 0.8
```

**Metrics Dashboard:**
- Task success rate trends
- Hallucination rate over test sets
- Tool accuracy by tool type
- Safety violations count
- Cost per evaluation run

#### Production Stage Monitoring
**Real-Time Observability:**
```python
# Example: Production monitoring with Langfuse
from langfuse import Langfuse

langfuse = Langfuse(
    public_key="pk-...",
    secret_key="sk-..."
)

# Trace production requests
with langfuse.trace(name="agent_request") as trace:
    response = agent.run(user_input)
    trace.update(
        output=response,
        metadata={"user_id": user_id}
    )
```

**Production Metrics:**
- Request volume and latency (p50, p95, p99)
- Error rate and error types
- Cost per request (tokens, API calls)
- User satisfaction scores
- SLA compliance (uptime, response time)

**Alerting Configuration:**
- Error rate > 5% in 5-minute window
- Latency > 10 seconds for p95
- Cost spike > 2x baseline
- Hallucination rate increase detected

### Integration: AI Agents with Pipeline Tools

#### Airflow + AI Agents

**Architecture:**
- Airflow DAGs orchestrate agent execution workflows
- Agents run as containerized tasks
- MLflow tracks agent experiments
- Results stored in S3

**Implementation:**
```python
# airflow/dags/agent_pipeline_dag.py
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
import mlflow

default_args = {
    'owner': 'mlops-team',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'retries': 2,
}

dag = DAG(
    'ai_agent_pipeline',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
)

# Task 1: Run AI agent
run_agent = DockerOperator(
    task_id='run_ai_agent',
    image='my-agent:latest',
    environment={
        'MLFLOW_TRACKING_URI': 'http://mlflow:5000',
        'AGENT_CONFIG': '/config/agent_config.json'
    },
    dag=dag
)

# Task 2: Evaluate agent performance
def evaluate_agent(**context):
    mlflow.set_tracking_uri('http://mlflow:5000')
    run_id = context['ti'].xcom_pull(task_ids='run_ai_agent')
    # Evaluation logic here
    pass

evaluate = PythonOperator(
    task_id='evaluate_agent',
    python_callable=evaluate_agent,
    dag=dag
)

run_agent >> evaluate
```

**AWS Deployment:**
1. Deploy MWAA with VPC access to MLflow
2. Configure ECS tasks for containerized agents
3. Set up S3 for agent artifacts and logs
4. Use CloudWatch for monitoring and alerting

#### Kubeflow + AI Agents

**Architecture:**
- Kubeflow Pipelines define agent workflows
- Components run as Kubernetes pods
- MLflow tracks experiments via sidecar
- KServe deploys agent endpoints

**Implementation:**
```python
# kubeflow/pipeline/agent_pipeline.py
from kfp import dsl
from kfp.components import create_component_from_func

@create_component_from_func
def train_agent(config_path: str, mlflow_uri: str) -> str:
    import mlflow
    from my_agent import AgentTrainer
    
    mlflow.set_tracking_uri(mlflow_uri)
    
    with mlflow.start_run() as run:
        trainer = AgentTrainer(config_path)
        model = trainer.train()
        
        mlflow.log_params(trainer.config)
        mlflow.log_metrics(trainer.metrics)
        mlflow.log_model(model, "agent_model")
        
        return run.info.run_id

@create_component_from_func
def deploy_agent(run_id: str, mlflow_uri: str):
    import mlflow
    mlflow.set_tracking_uri(mlflow_uri)
    
    # Register model
    model_uri = f"runs:/{run_id}/agent_model"
    mlflow.register_model(model_uri, "production_agent")

@dsl.pipeline(
    name='AI Agent Pipeline',
    description='Train, evaluate, and deploy AI agent'
)
def agent_pipeline(config_path: str, mlflow_uri: str):
    train_task = train_agent(config_path, mlflow_uri)
    deploy_task = deploy_agent(train_task.output, mlflow_uri)

if __name__ == '__main__':
    import kfp
    kfp.compiler.Compiler().compile(agent_pipeline, 'agent_pipeline.yaml')
```

**AWS Deployment:**
1. Install Kubeflow on Amazon EKS
2. Deploy MLflow tracking server as Kubernetes service
3. Configure EFS for shared storage
4. Use Application Load Balancer for external access
5. Integrate with SageMaker for model hosting

#### MLflow + AI Agents

**Architecture:**
- MLflow tracks agent experiments and versions
- MLflow GenAI API logs LLM interactions
- Model Registry stores agent artifacts
- Deployment via MLflow or SageMaker

**Implementation:**
```python
# src/agent_with_mlflow.py
import mlflow
from mlflow.models import infer_signature
from langchain.agents import AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent

# Enable MLflow autologging for LangChain
mlflow.langchain.autolog()

mlflow.set_tracking_uri("http://mlflow-server:5000")
mlflow.set_experiment("ai-agent-development")

with mlflow.start_run(run_name="agent_v1") as run:
    # Configure agent
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    tools = [search_tool, calculator_tool, database_tool]
    
    agent = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools)
    
    # Log configuration
    mlflow.log_params({
        "model": "gpt-4",
        "temperature": 0,
        "num_tools": len(tools),
        "max_iterations": 10
    })
    
    # Test agent
    test_cases = load_test_cases()
    results = []
    
    for test in test_cases:
        response = agent_executor.invoke({"input": test["query"]})
        results.append(response)
        
        # Log individual test metrics
        mlflow.log_metrics({
            f"test_{test['id']}_success": int(response["success"]),
            f"test_{test['id']}_latency": response["latency"]
        })
    
    # Log aggregated metrics
    mlflow.log_metrics({
        "success_rate": sum(r["success"] for r in results) / len(results),
        "avg_latency": sum(r["latency"] for r in results) / len(results),
        "total_cost": sum(r["cost"] for r in results)
    })
    
    # Log model
    signature = infer_signature(test_cases[0]["query"], results[0])
    mlflow.langchain.log_model(
        agent_executor,
        "agent_model",
        signature=signature,
        registered_model_name="customer_support_agent"
    )
    
    print(f"Agent logged to MLflow run: {run.info.run_id}")
```

**AWS Deployment:**
1. Deploy MLflow on EC2/ECS with RDS backend
2. Configure S3 for artifact storage
3. Use MLflow GenAI features for LLM tracking
4. Deploy to SageMaker endpoints from Model Registry

**MLflow GenAI Capabilities:**
- Automatic logging of LLM calls
- Prompt template versioning
- Token usage tracking
- Retrieval context logging
- Agent trajectory visualization

### Integration Steps Summary

**1. Set up Infrastructure:**
```bash
# Deploy Kubernetes cluster
eksctl create cluster --name ml-pipeline-cluster

# Install Kubeflow
kustomize build kubeflow/manifests | kubectl apply -f -

# Deploy MLflow
kubectl apply -f mlflow-deployment.yaml

# Install Airflow (AWS MWAA alternative)
helm install airflow apache-airflow/airflow
```

**2. Configure MLflow Tracking:**
```python
# All pipeline components point to central MLflow server
import os
os.environ['MLFLOW_TRACKING_URI'] = 'http://mlflow-service:5000'
```

**3. Create Agent Pipeline:**
- Define workflow in Airflow DAG / Kubeflow Pipeline
- Implement agent training/evaluation components
- Use MLflow for experiment tracking
- Log all metrics and artifacts

**4. Deploy and Monitor:**
- Progressive rollout with canary deployments
- Set up monitoring dashboards (Grafana + Prometheus)
- Configure alerting rules
- Collect user feedback

### Tool Selection Guide

**Choose LangGraph or AutoGen when:**
- Complex, multi-step reasoning required
- Multiple agents need to collaborate
- Cyclic workflows and state management needed

**Choose CrewAI when:**
- Role-based agent teams
- Structured task delegation
- Simpler, more opinionated setup preferred

**Choose Mastra when:**
- TypeScript/JavaScript environment
- RAG and memory are core requirements
- Web-based deployments

**For Evaluation:**
- **Ragas**: RAG-heavy agent systems
- **Arize Phoenix**: General LLM application tracing
- **Promptfoo**: Local prompt testing and optimization
- **Langfuse**: Production observability and analytics

**For Integration:**
- **Airflow**: Complex scheduling, enterprise workflows
- **Kubeflow**: Kubernetes-native, high scalability
- **MLflow**: Experiment tracking, model lifecycle management

## References

### Documentation - Pipeline Orchestration
- [Apache Airflow](https://airflow.apache.org/) - Official Airflow documentation
- [Dagster](https://dagster.io/) - Official Dagster documentation  
- [Kubeflow](https://kubeflow.org/) - Official Kubeflow documentation
- [MLflow](https://mlflow.org/) - Official MLflow documentation
- [MLflow GenAI](https://mlflow.org/docs/latest/genai/) - MLflow for Generative AI and LLM tracking
- [Ray](https://ray.io/) - Official Ray documentation

### Documentation - AI Agent Frameworks
- [LangGraph](https://langchain-ai.github.io/langgraph/) - Build stateful, multi-agent applications
- [LangChain](https://python.langchain.com/) - Framework for developing LLM applications
- [AutoGen](https://microsoft.github.io/autogen/) - Microsoft's multi-agent conversation framework
- [CrewAI](https://docs.crewai.com/) - Framework for orchestrating role-playing AI agents
- [Julep](https://github.com/julep-ai/julep) - Platform for creating AI agents with memory
- [Mastra](https://mastra.ai/) - TypeScript framework for building AI agents
- [Browser Use](https://github.com/browser-use/browser-use) - Library for browser-controlling agents

### Documentation - Agent Evaluation & Observability
- [Ragas](https://docs.ragas.io/) - Evaluation framework for RAG systems
- [Arize Phoenix](https://docs.arize.com/phoenix/) - Open-source LLM observability
- [Promptfoo](https://promptfoo.dev/) - Test and evaluate LLM prompts
- [Langfuse](https://langfuse.com/docs/) - Open-source LLM engineering platform
- [Braintrust](https://braintrustdata.com/) - Evaluation and observability for AI
- [Fiddler](https://www.fiddler.ai/) - Enterprise AI observability platform
- [Galileo](https://www.rungalileo.io/) - Real-time LLM safety and quality monitoring

### Amazon AWS Services
- [Amazon SageMaker](https://aws.amazon.com/sagemaker/) - Fully managed ML service
- [Amazon Bedrock](https://aws.amazon.com/bedrock/) - Managed foundation models service
- [AWS MWAA](https://aws.amazon.com/managed-workflows-for-apache-airflow/) - Managed Airflow
- [Amazon EKS](https://aws.amazon.com/eks/) - Managed Kubernetes service
- [AWS Lambda](https://aws.amazon.com/lambda/) - Serverless compute service
- [Amazon ECS](https://aws.amazon.com/ecs/) - Container orchestration service
- [Amazon S3](https://aws.amazon.com/s3/) - Object storage service
- [Amazon RDS](https://aws.amazon.com/rds/) - Managed relational database service

### Blog Posts & Tutorials - ML Pipelines
- [Scaling AI and Machine Learning Workloads with Ray on AWS](https://aws.amazon.com/blogs/opensource/scaling-ai-and-machine-learning-workloads-with-ray-on-aws/)
- [LLM experimentation at scale using Amazon SageMaker Pipelines and MLflow](https://aws.amazon.com/blogs/machine-learning/llm-experimentation-at-scale-using-amazon-sagemaker-pipelines-and-mlflow/)
- [Building ML Pipelines with Kubeflow on Amazon EKS](https://aws.amazon.com/blogs/opensource/kubeflow-amazon-eks/)
- [Orchestrating Analytics Jobs on Amazon EMR with Apache Airflow](https://aws.amazon.com/blogs/big-data/orchestrating-analytics-jobs-on-amazon-emr-with-apache-airflow/)

### Blog Posts & Tutorials - AI Agents
- [Building Production-Ready AI Agents](https://www.anthropic.com/index/building-production-ready-ai-agents) - Anthropic's guide to agent development
- [Evaluating and Monitoring AI Agents](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-monitor-ai-agents) - Microsoft Azure documentation
- [Best Practices for LLM Observability](https://medium.com/@langfuse/best-practices-for-llm-observability) - LLM monitoring strategies
- [AI Agent Architecture Patterns](https://aws.amazon.com/blogs/machine-learning/ai-agent-architecture-patterns/) - AWS ML blog on agent design

### Additional Resources
- [Airflow AI SDK](https://airflow.apache.org/docs/apache-airflow/stable/ai-sdk.html) - AI agent integration with Airflow
- [KServe](https://kserve.github.io/website/) - Kubernetes model serving
- [Hugging Face](https://huggingface.co/) - Model hub and deployment platform
- [OpenAI Agents SDK](https://platform.openai.com/docs/agents) - OpenAI's agent development kit
- [INS Forge](https://github.com/intentional-ai/ins-forge) - Open-source semantic layer for agents
