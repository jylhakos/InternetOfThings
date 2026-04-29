# Strands Agents

An open-source Python and TypeScript SDK for building autonomous, production-ready AI agents with a "model-first" approach.

![Strands Agents](https://img.shields.io/badge/Python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)
![AWS](https://img.shields.io/badge/AWS-Powered-orange.svg)

---

## Table of Contents

- [What are Strands Agents?](#what-are-strands-agents)
- [Core Concepts](#core-concepts)
- [Project Structure](#project-structure)
- [DevOps Setup Guide](#devops-setup-guide)
- [Running Examples](#running-examples)
- [Deployment](#deployment)
- [Monitoring and Observability](#monitoring-and-observability)
- [Testing Deployed Agents](#testing-deployed-agents)
- [Architecture](#architecture)
- [References](#references)

---

## What are Strands Agents?

**Strands Agents** is an open-source Python and TypeScript SDK launched by AWS for building autonomous, production-ready AI agents with a "model-first" approach. It simplifies creating intelligent agents by leveraging Large Language Models (LLMs) to reason through goals and interact with tools, reducing manual orchestration.

### Key Features

- **Model-First Approach**: Leverages state-of-the-art LLMs' native reasoning and tool-use capabilities
- **Simplified Development**: Build agents in just a few lines of code
- **Flexible Model Support**: Works with Amazon Bedrock, Anthropic, Ollama, Meta Llama, OpenAI (via LiteLLM), and custom providers
- **Production-Ready**: Designed for deployment at scale with built-in observability
- **Tool Ecosystem**: Access thousands of MCP servers and 20+ pre-built tools
- **Multi-Agent Orchestration**: Support for complex workflows, graphs, and swarms

### Why Strands Agents?

Unlike frameworks that require developers to define complex workflows, Strands embraces the capabilities of modern LLMs to:

- Plan and chain thoughts autonomously
- Select and execute tools intelligently
- Reflect on outcomes and adjust strategies
- Scale from simple to complex use cases
- Deploy seamlessly from local development to cloud production

Multiple teams at AWS use Strands for their AI agents in production, including **Amazon Q Developer**, **AWS Glue**, and **VPC Reachability Analyzer**.

---

## Core Concepts

The simplest definition of an agent is a combination of **three components**:

### A Model

Strands offers flexible model support:

- **Amazon Bedrock**: Any model that supports tool use and streaming ([supported models](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference-supported-models-features.html))
- **Anthropic API**: Claude model family
- **Meta Llama**: Via Llama API
- **Ollama**: For local development
- **OpenAI & Others**: Through LiteLLM
- **Custom Providers**: Define your own model integrations

### Tools

Tools enable agents to interact with the world:

- **Model Context Protocol (MCP) Servers**: Thousands of published tools
- **Pre-built Strands Tools**: 20+ ready-to-use tools for files, HTTP requests, AWS APIs
- **Custom Python Functions**: Use the `@tool` decorator to convert any function

Example pre-built tools:

- **Retrieve Tool**: Semantic search using Amazon Bedrock Knowledge Bases
- **Thinking Tool**: Deep analytical reasoning and self-reflection
- **Multi-Agent Tools**: Workflow, graph, and swarm orchestration

### A Prompt

Prompts define the agent's task:

- **User Prompt**: The specific task or question (e.g., "What's the weather in Seattle?")
- **System Prompt**: General instructions and desired behavior

### The Agentic Loop

An agent interacts with its model and tools in a loop until it completes the task provided by the prompt.

![Agentic Loop](https://d2908q01vomqb2.cloudfront.net/ca3512f4dfa95a03169c5a670a4c91a19b3077b4/2025/05/16/agentic-loop.png)

_Source: [AWS Open Source Blog - Introducing Strands Agents](https://aws.amazon.com/blogs/opensource/introducing-strands-agents-an-open-source-ai-agents-sdk/)_

**How it works:**

1. Strands invokes the LLM with the prompt and agent context
2. The LLM responds with natural language, plans steps, or selects tools
3. When tools are selected, Strands executes them and provides results back to the LLM
4. The loop continues until the task is complete

---

## Project Structure

```
Strands Agents/
├── README.md                      # Comprehensive documentation
├── QUICK_START.md                 # Quick setup guide
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore patterns
├── agentic-loop.png              # Architecture diagram
├── test_agent.py                  # Installation test script
│
├── venv/                          # Python virtual environment
│
├── examples/                      # Example agents
│   ├── weather_forecaster.py     # Weather API agent (HTTP tools)
│   └── naming_agent.py            # Project naming agent (MCP + GitHub)
│
├── deployment/                    # AWS deployment configurations
│   ├── lambda/                    # AWS Lambda deployment
│   │   ├── lambda_handler.py     # Lambda function handler
│   │   ├── template.yaml         # SAM template
│   │   └── Dockerfile            # Lambda container image
│   │
│   └── fargate/                   # AWS Fargate deployment
│       ├── fargate_app.py        # Flask web application
│       ├── Dockerfile            # Container image
│       └── cloudformation.yaml   # Infrastructure template
│
├── scripts/                       # Automation scripts
│   ├── setup_env.sh              # Virtual environment setup
│   ├── deploy_lambda.sh          # Lambda deployment script
│   └── deploy_fargate.sh         # Fargate deployment script
│
└── .vscode/                       # VS Code configuration
    └── settings.json             # Python interpreter settings
```

### Practical Example: Three Components in Code

```python
from strands import Agent
from strands_tools import http_request

# 1. MODEL: Using default Bedrock model (Anthropic Claude)
# The model is automatically configured based on your AWS credentials

# 2. TOOLS: HTTP request capability
tools = [http_request]

# 3. PROMPT: System instructions
system_prompt = """You are a weather assistant with HTTP capabilities.
You can retrieve and explain weather forecasts for US locations."""

# Create the agent with all three components
weather_agent = Agent(
    system_prompt=system_prompt,  # Component 3: Prompt
    tools=tools                     # Component 2: Tools
    # Model is implicit (Component 1)
)

# Use the agent
response = weather_agent("What's the weather like in Seattle?")
print(response)
```

---

## 🛠️ DevOps Setup Guide

### Prerequisites

- **Python**: 3.11 or higher
- **AWS Account**: For using Bedrock models and deployment
- **AWS CLI**: Configured with credentials
- **Git**: For cloning repositories
- **VS Code**: Recommended IDE (with Python extension)

### Step 1: Clone or Initialize Repository

```bash
# If cloning from a repository
git clone <repository-url>
cd "Strands Agents"

# Or initialize in current directory
# Already in project directory
```

### Step 2: Create Virtual Environment

**Important**: Always activate the virtual environment before installing packages or running code in VS Code.

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

**VS Code Integration**:

1. Open Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`)
2. Select **"Python: Select Interpreter"**
3. Choose the interpreter from `./venv/bin/python`

### Step 3: Install Dependencies

```bash
# Ensure virtual environment is activated (you should see (venv) in your prompt)
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure AWS Credentials

```bash
# Configure AWS CLI
aws configure
# Enter:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (e.g., us-west-2)
# - Output format (json)

# Verify credentials
aws sts get-caller-identity
```

### Step 5: Enable Bedrock Model Access

1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Navigate to **Model access**
3. Request access to **Anthropic Claude 3.7 Sonnet** (or your preferred model)
4. Wait for approval (usually instant for most models)

### Step 6: Set Environment Variables (Optional)

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
# For GitHub integration (naming agent):
export GITHUB_TOKEN=your_github_personal_access_token

# For Anthropic API (alternative to Bedrock):
export ANTHROPIC_API_KEY=your_api_key
```

### Setup Script

We provide a setup script that automates steps 2-3:

```bash
# Make script executable
chmod +x scripts/setup_env.sh

# Run setup
./scripts/setup_env.sh
```

### For Development

```bash
# 1. Set up environment
./scripts/setup_env.sh

# 2. Activate virtual environment
source venv/bin/activate

# 3. Configure AWS
aws configure

# 4. Test installation
python test_agent.py

# 5. Run examples
python examples/weather_forecaster.py
```

### For Deployment

```bash
# AWS Lambda
./scripts/deploy_lambda.sh

# AWS Fargate
./scripts/deploy_fargate.sh
```

### For VS Code

1. Open project: `code .`
2. Select Python interpreter: `./venv/bin/python`
3. Terminal will auto-activate virtual environment
4. Run files with F5 or the Run button

---

## Running Examples

### Example 1: Weather Forecaster Agent

Demonstrates HTTP tool usage with the National Weather Service API.

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Run the weather forecaster
python examples/weather_forecaster.py
```

**Sample interaction:**

```
Weather Forecaster Agent
==================================================
Ask me about weather conditions in the United States!
Examples:
  - What's the weather like in Seattle?
  - Will it rain tomorrow in Miami?
  - Compare temperature in New York and Chicago
==================================================

Your question: What's the weather like in Seattle?

Agent is processing your request...

Current weather in Seattle, WA:
Temperature: 52°F
Conditions: Partly Sunny
Wind: NW at 8 mph
...
```

### Example 2: Naming Agent

Demonstrates MCP integration and multi-step tool orchestration.

```bash
# Set GitHub token
export GITHUB_TOKEN=your_token

# Run the naming agent
python examples/naming_agent.py
```

**Requirements:**

- GitHub personal access token
- Bedrock model access (Claude 3.7 Sonnet)
- `uvx` installed for MCP server: `pip install uv`

### Example 3: Simple Agent (Inline)

Quick test of Strands functionality:

```python
# Create a file: test_agent.py
from strands import Agent

agent = Agent(
    system_prompt="You are a helpful assistant."
)

response = agent("Explain what Strands Agents is in one sentence.")
print(response)
```

Run it:

```bash
python test_agent.py
```

---

## Deployment

Strands Agents can be deployed in various production architectures. Below are reference implementations for AWS.

### Deployment Architecture Patterns

#### 1. Local Development

- Agent runs entirely in local environment
- Suitable for prototyping and testing
- Example: CLI tools, Jupyter notebooks

#### 2. Serverless API (AWS Lambda)

- Agent deployed as Lambda function
- API Gateway for HTTP access
- Auto-scaling, pay-per-use
- **Best for**: Event-driven workloads, low-traffic APIs

#### 3. Container-Based (AWS Fargate)

- Agent runs in Docker container
- Application Load Balancer for routing
- Persistent connections, predictable performance
- **Best for**: Production APIs, higher traffic

#### 4. Hybrid Architecture

- Agent in one environment, tools in another
- Separation of concerns
- Enhanced security
- **Best for**: Complex enterprise deployments

### Deployment Option 1: AWS Lambda

Deploy your agent as a serverless function.

**Tools Required:**

- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- Docker (for building Lambda layers)
- AWS CLI with configured credentials

**Quick Deploy:**

```bash
# Run automated deployment script
./scripts/deploy_lambda.sh

# Or manually:
cd deployment/lambda
sam build
sam deploy --guided
```

**What gets deployed:**

- Lambda function with Strands agent
- API Gateway endpoint
- IAM roles with Bedrock permissions
- CloudWatch logs

**Testing:**

```bash
# Get API endpoint from SAM outputs
curl -X POST https://<api-id>.execute-api.us-west-2.amazonaws.com/prod/agent \
  -H 'Content-Type: application/json' \
  -d '{"query": "What is the weather in Seattle?"}'
```

### Deployment Option 2: AWS Fargate

Deploy your agent in a containerized environment.

**Tools Required:**

- [AWS CLI](https://aws.amazon.com/cli/)
- [Docker](https://www.docker.com/get-started)
- AWS account with VPC configured

**Quick Deploy:**

```bash
# Run automated deployment script
./scripts/deploy_fargate.sh

# The script will:
# 1. Create ECR repository
# 2. Build and push Docker image
# 3. Deploy CloudFormation stack with:
#    - ECS Cluster
#    - Fargate Service
#    - Application Load Balancer
#    - Security Groups
```

**Manual Deployment:**

```bash
# 1. Build Docker image
cd deployment/fargate
docker build -t strands-agent .

# 2. Push to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-west-2.amazonaws.com
docker tag strands-agent:latest <account-id>.dkr.ecr.us-west-2.amazonaws.com/strands-agent:latest
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/strands-agent:latest

# 3. Deploy CloudFormation
aws cloudformation deploy \
  --template-file cloudformation.yaml \
  --stack-name strands-agent-fargate \
  --parameter-overrides ImageUri=<image-uri> \
  --capabilities CAPABILITY_IAM
```

### Deployment Option 3: Amazon EC2

For full control over the compute environment.

**Reference:** [Strands Agents EC2 Deployment Guide](https://strandsagents.com/0.1.x/user-guide/deploy/deploy_to_amazon_ec2/)

**Tools Required:**

- EC2 instance (t3.medium or larger recommended)
- Elastic IP or Load Balancer
- Security Groups configured

**Steps:**

1. Launch EC2 instance with Amazon Linux 2023
2. Install Python 3.11+
3. Clone repository and setup virtual environment
4. Configure systemd service
5. Set up Nginx as reverse proxy
6. Configure SSL/TLS with AWS Certificate Manager

### Deployment Option 4: Amazon Bedrock AgentCore

Purpose-built runtime for hosting Strands agents.

**Reference:** [Strands AgentCore Samples](https://github.com/strands-agents/samples/tree/main/python/02-deploy/03-agentcore)

**Benefits:**

- Managed infrastructure
- Built-in scaling
- Integrated with AWS services
- Simplified operations

---

## Monitoring and Observability

Strands Agents provides built-in observability features to track metrics, logs, and traces.

### How Monitoring Works

Strands uses **OpenTelemetry (OTEL)** to emit telemetry data compatible with various backends:

- **AWS CloudWatch**: Metrics and logs
- **AWS X-Ray**: Distributed tracing
- **Datadog**: Full-stack monitoring
- **Honeycomb**: Observability platform
- **Prometheus + Grafana**: Self-hosted metrics

### Enabling Observability

```python
from strands import Agent
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

# Configure OpenTelemetry
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Add span processor (example: console export)
span_processor = BatchSpanProcessor(ConsoleSpanExporter())
trace.get_tracer_provider().add_span_processor(span_processor)

# Create agent (automatically instrumented)
agent = Agent(
    system_prompt="You are a helpful assistant.",
    tools=[http_request]
)

# Use agent (traces automatically emitted)
with tracer.start_as_current_span("agent_execution"):
    response = agent("Your query here")
```

### Key Metrics to Monitor

1. **Agent Performance**
   - Response latency
   - Tool execution time
   - Model inference duration

2. **Success Metrics**
   - Task completion rate
   - Error rate
   - Tool call success rate

3. **Resource Utilization**
   - Memory usage
   - CPU utilization
   - API call volume (Bedrock)

4. **Cost Tracking**
   - Bedrock API costs
   - Lambda/Fargate costs
   - Data transfer costs

### CloudWatch Integration (Lambda)

Automatically enabled for Lambda deployments:

```bash
# View logs
aws logs tail /aws/lambda/strands-agent-lambda --follow

# Query metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=strands-agent-lambda \
  --start-time 2026-03-30T00:00:00Z \
  --end-time 2026-03-31T00:00:00Z \
  --period 3600 \
  --statistics Average,Maximum
```

### Distributed Tracing

Track requests across components:

```python
# The agent's trajectory is automatically traced
# View in AWS X-Ray or your OTEL backend

# Example span structure:
# - agent_execution
#   - model_invocation
#   - tool_selection
#   - tool_execution
#     - http_request
#   - model_invocation (with results)
```

---

## Testing Deployed Agents

### Testing AWS Lambda Deployment

#### 1. Test via API Gateway

```bash
# Get API endpoint from CloudFormation/SAM outputs
API_URL="https://<api-id>.execute-api.us-west-2.amazonaws.com/prod/agent"

# Test with curl
curl -X POST $API_URL \
  -H 'Content-Type: application/json' \
  -d '{"query": "What is the capital of France?"}'

# Expected response:
# {"response": "The capital of France is Paris.", "query": "What is the capital of France?"}
```

#### 2. Test via AWS CLI

```bash
# Invoke Lambda directly
aws lambda invoke \
  --function-name strands-agent-lambda \
  --payload '{"body": "{\"query\": \"Hello, agent!\"}"}' \
  response.json

# View response
cat response.json
```

#### 3. Load Testing

```bash
# Using Apache Bench
ab -n 100 -c 10 -p payload.json -T application/json $API_URL

# payload.json content:
# {"query": "Tell me a fun fact"}
```

### Testing AWS Fargate Deployment

#### 1. Get Load Balancer URL

```bash
# From CloudFormation outputs
aws cloudformation describe-stacks \
  --stack-name strands-agent-fargate \
  --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerUrl`].OutputValue' \
  --output text
```

#### 2. Health Check

```bash
LB_URL="http://<load-balancer-dns>"

# Test health endpoint
curl $LB_URL/health

# Expected: {"status": "healthy"}
```

#### 3. Agent Functionality Test

```bash
# Test agent endpoint
curl -X POST $LB_URL/agent \
  -H 'Content-Type: application/json' \
  -d '{"query": "Explain quantum computing in simple terms"}'
```

#### 4. Performance Testing

```bash
# Using hey (HTTP load generator)
hey -n 1000 -c 50 -m POST \
  -H "Content-Type: application/json" \
  -d '{"query": "What is AI?"}' \
  $LB_URL/agent
```

### Automated Testing Script

```bash
#!/bin/bash
# test_deployment.sh

ENDPOINT=$1

if [ -z "$ENDPOINT" ]; then
  echo "Usage: ./test_deployment.sh <api-url>"
  exit 1
fi

echo "Testing agent deployment at: $ENDPOINT"

# Test 1: Simple query
echo -e "\n1. Testing simple query..."
RESPONSE=$(curl -s -X POST $ENDPOINT \
  -H 'Content-Type: application/json' \
  -d '{"query": "Say hello"}')
echo "Response: $RESPONSE"

# Test 2: Tool usage (if weather agent)
echo -e "\n2. Testing tool usage..."
RESPONSE=$(curl -s -X POST $ENDPOINT \
  -H 'Content-Type: application/json' \
  -d '{"query": "What is the weather in Seattle?"}')
echo "Response: $RESPONSE"

# Test 3: Error handling
echo -e "\n3. Testing error handling..."
RESPONSE=$(curl -s -X POST $ENDPOINT \
  -H 'Content-Type: application/json' \
  -d '{}')
echo "Response: $RESPONSE"

echo -e "\n✅ Testing complete!"
```

### Verification Checklist

- Agent responds to simple queries
- Tool execution works correctly
- Error handling returns appropriate messages
- Response times are acceptable (<5s for simple queries)
- CloudWatch logs show agent activity
- No unauthorized access (security groups configured)
- Costs are within expected range

### Monitoring Deployment Health

```bash
# Lambda: Check recent errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/strands-agent-lambda \
  --filter-pattern "ERROR"

# Fargate: Check task status
aws ecs describe-tasks \
  --cluster strands-agent-cluster \
  --tasks $(aws ecs list-tasks --cluster strands-agent-cluster --query 'taskArns[0]' --output text)

# Check CloudWatch alarms
aws cloudwatch describe-alarms \
  --alarm-names strands-agent-errors
```

---

## Architecture

### Local Development Architecture

```
┌──────────────────────────────────────┐
│  Developer Environment               │
│                                      │
│  ┌────────────┐     ┌─────────────┐  │
│  │   Agent    │────▶│   Bedrock   │  │
│  │  (Strands) │◀────│   (Claude)  │  │
│  └────────────┘     └─────────────┘  │
│         │                            │
│         │                            │
│    ┌────▼─────┐                      │
│    │  Tools   │                      │
│    │  (MCP,   │                      │
│    │   HTTP)  │                      │
│    └──────────┘                      │
└──────────────────────────────────────┘
```

### Production Architecture (API Deployment)

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│  AWS Cloud                                  │
│                                             │
│  ┌──────────────┐      ┌─────────────────┐  │
│  │API Gateway/  │      │    Lambda or    │  │
│  │     ALB      │─────▶│    Fargate      │  │
│  └──────────────┘      │   ┌─────────┐   │  │
│                        │   │ Agent   │   │  │
│                        │   └────┬────┘   │  │
│                        └────────┼────────┘  │
│                                 │           │
│         ┌───────────────────────┼────────┐  │
│         ▼                       ▼        │  │
│  ┌─────────────┐         ┌──────────┐    │  │
│  │   Bedrock   │         │  Tools   │    │  │
│  │   Models    │         │  (MCP,   │    │  │
│  └─────────────┘         │  HTTP,   │    │  │
│                          │  AWS)    │    │  │
│                          └──────────┘    │  │
│                                          │  │
│  ┌─────────────────────────────────┐     │  │
│  │  Monitoring (CloudWatch/X-Ray)  │     │  │
│  └─────────────────────────────────┘     │  │
└──────────────────────────────────────────┘
```

### Multi-Agent Architecture

```
┌───────────────────────────────────────────┐
│  Orchestrator Agent                       │
│                                           │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐    │
│  │Agent 1  │  │Agent 2  │  │Agent 3  │    │
│  │(Research)  │(Analysis)  │(Report) │    │
│  └─────────┘  └─────────┘  └─────────┘    │
│       │             │             │       │
│       └─────────────┼─────────────┘       │
│                     ▼                     │
│            ┌────────────────┐             │
│            │ Shared Context │             │
│            └────────────────┘             │
└───────────────────────────────────────────┘
```

---

## References

### Documentation

- **Strands Agents Website**: https://strandsagents.com/
- **Python API Reference**: https://strandsagents.com/docs/api/python/
- **TypeScript API Reference**: https://strandsagents.com/docs/api/typescript/
- **User Guide**: https://strandsagents.com/docs/user-guide/quickstart/overview/
- **GitHub Repository (Docs)**: https://github.com/strands-agents/docs
- **GitHub Repository (Samples)**: https://github.com/strands-agents/samples

### Examples and Tutorials

- **Weather Forecaster Example**: https://strandsagents.com/docs/examples/python/weather_forecaster/
- **CLI Reference Agent**: https://strandsagents.com/docs/examples/python/cli-reference-agent/
- **All Examples**: https://strandsagents.com/docs/examples/

### Deployment Resources

- **Deployment Toolkit**: https://strandsagents.com/0.1.x/user-guide/deploy/operating-agents-in-production/
- **AWS Lambda Deployment**: https://strandsagents.com/0.1.x/user-guide/deploy/deploy_to_aws_lambda/
- **AWS Fargate Deployment**: https://strandsagents.com/0.1.x/user-guide/deploy/deploy_to_aws_fargate/
- **Amazon EC2 Deployment**: https://strandsagents.com/0.1.x/user-guide/deploy/deploy_to_amazon_ec2/
- **Deployment Samples (GitHub)**: https://github.com/strands-agents/samples/tree/main/python/02-deploy

### AWS and Model Context Protocol

- **AWS Open Source Blog**: https://aws.amazon.com/blogs/opensource/introducing-strands-agents-an-open-source-ai-agents-sdk/
- **Amazon Bedrock**: https://aws.amazon.com/bedrock/
- **Model Context Protocol (MCP)**: https://modelcontextprotocol.io/
- **MCP Examples**: https://modelcontextprotocol.io/examples
- **Strands MCP Server**: https://github.com/strands-agents/mcp-server/

### AWS

- **AWS SAM CLI**: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html
- **AWS Bedrock Model Access**: https://docs.aws.amazon.com/bedrock/latest/userguide/model-access-modify.html
- **Amazon Bedrock Knowledge Bases**: https://aws.amazon.com/bedrock/knowledge-bases/
- **AWS Lambda**: https://aws.amazon.com/lambda/
- **AWS Fargate**: https://aws.amazon.com/fargate/
- **Amazon EC2**: https://aws.amazon.com/ec2/

### Tools and Prerequisites

- **Python 3.11+**: https://www.python.org/downloads/
- **AWS CLI**: https://aws.amazon.com/cli/
- **Docker**: https://www.docker.com/get-started
- **VS Code**: https://code.visualstudio.com/
- **GitHub Personal Access Tokens**: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens

### Community and Support

- **GitHub Issues**: https://github.com/strands-agents/strands-agents/issues
- **Community Packages**: https://strandsagents.com/docs/community/community-packages/
- **Contributing Guide**: https://strandsagents.com/docs/contribute/

---

## License

This project follows the Apache License 2.0, the same as Strands Agents.

---

**Built using Strands Agents - An open-source AI agents SDK by AWS**
