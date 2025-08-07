# Open Source Tools For Evaluating Large Language Models (LLMs)

This document presents how to evaluate LLM models like BERT model.

## 🛠️ Open Source LLM Evaluation Tools (2025)

The LLM evaluation has evolved with open-source tools designed specifically for model assessment. This project integrates several evaluation frameworks to provide multi-dimensional analysis of language model performance.

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

| **Use Case** | **Recommended Tool** | **Why** |
|--------------|---------------------|---------|
| **Production Testing** | DeepEval | Metrics, production-ready |
| **Creative Content** | G-Eval | Human-like evaluation via LLM judges |
| **Multi-lingual** | LLMeBench | Specialized for cross-language evaluation |
| **RAG Applications** | Ragas | RAG-specific metrics and optimization |
| **Academic Research** | LM Evaluation Harness | Standardized benchmarks |
| **LangChain Apps** | LangSmith | Native integration, observability |

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

> 📖 **For detailed API documentation, examples, and troubleshooting, see the auto-generated docs at [http://localhost:8000/docs](http://localhost:8000/docs) when the server is running**

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

### Traditional Training and Evaluation Metrics

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

### Model Performance Evaluation

#### 1. **Validation split**
- Split data into training (80%), validation (10%), test (10%)
- Use validation set to tune hyperparameters
- Use test set for final performance evaluation

#### 2. **Cross validation**
- K-fold cross-validation for robust performance estimates
- Helps detect overfitting and ensures generalization

#### 3. **Confusion matrix**
- Visualize classification performance across all classes
- Identify which classes are being confused

#### 4. **Classification report**
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

#### Manual Setup
```bash
# Activate virtual environment
source bert_env/bin/activate

# Install evaluation tools
pip install -r requirements-evaluation.txt

# Verify installation
python src/test_environment.py
```

### Available Evaluation Tools

#### 1. **DeepEval Framework**
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

#### 2. **BERTScore Integration**
[Documentation: BERTScore](https://spotintelligence.com/2024/08/20/bertscore/)

Semantic similarity evaluation using BERT embeddings:
```python
from bert_score import BERTScorer
scorer = BERTScorer(lang="en", rescale_with_baseline=True)
P, R, F1 = scorer.score(predictions, references)
```

#### 3. **G-Eval Implementation**
[Paper: G-Eval NLG Evaluation](https://github.com/nlpyang/geval)

LLM-as-a-judge evaluation with chain-of-thoughts:
```bash
# Set OpenAI API key for G-Eval
export OPENAI_API_KEY="your-api-key"

# Run G-Eval
python src/geval_integration.py
```

#### 4. **ROUGE and BLEU Metrics**
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

#### Evaluation Features
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

#### Optimizers (2025)

The choice of optimizer significantly impacts BERT fine-tuning performance. Here are the **optimizer options** available in your environment.

##### **Available Optimizers**
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

##### **Optimizer Comparison Table**
| Optimizer | Memory Usage | Stability | Performance | Best For |
|-----------|-------------|-----------|-------------|----------|
| **AdamW** | Medium | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | General BERT fine-tuning |
| **Adafactor** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | Large models, memory constraints |
| **RAdam** | Medium | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Self-correcting, no warmup needed |
| **Adamax** | Medium | ⭐⭐⭐ | ⭐⭐⭐ | Sparse gradients, unstable data |

##### **Usage Recommendations**

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

**🔬 Research/Stability**: Use `RAdam` for self-correcting behavior
```python
from torch.optim import RAdam

optimizer = RAdam(model.parameters(), lr=2e-5, weight_decay=0.01)
# No manual warmup needed - RAdam handles it internally
```

##### **Modern Fine-tuning Template**
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

### **Core Documentation**
- **API Documentation**: [Auto-generated Swagger UI](http://localhost:8000/docs) (when server is running)
- **Installation Guide**: [evaluation_examples/installation_guide.md](./evaluation_examples/installation_guide.md)
- **Comprehensive Demo**: [evaluation_examples/comprehensive_demo.py](./evaluation_examples/comprehensive_demo.py)
- **Integration Tests**: [evaluation_examples/integration_test.py](./evaluation_examples/integration_test.py)

### **LLM Evaluation Tools (2025)**

#### **1. DeepEval - Production LLM Testing**
- **Repository**: [confident-ai/deepeval](https://github.com/confident-ai/deepeval)
- **Documentation**: [deepeval.com/docs/metrics-llm-evals](https://deepeval.com/docs/metrics-llm-evals)
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
- **ROUGE**: [github.com/google-research/google-research/tree/master/rouge](https://github.com/google-research/google-research/tree/master/rouge)
- **BLEU**: [github.com/mjpost/sacrebleu](https://github.com/mjpost/sacrebleu)
- **METEOR**: [aclweb.org/anthology/W05-0909](https://aclweb.org/anthology/W05-0909.pdf)

### **Core Technologies**
- **BERT Paper**: [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- **BERT**: [BERT: Pre-training of Deep Bidirectional Transformers](https://arxiv.org/abs/1810.04805)
- **Transformers**: [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- **Hugging Face**: [huggingface.co](https://huggingface.co/)
- **PyTorch**: [pytorch.org](https://pytorch.org/)

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
