# Evaluation and metrics of models

### BERT:
- **Bidirectional**: Unlike traditional models that read text from left to right, BERT reads text in both directions simultaneously
- **Pre-trained**: Trained on massive text datasets using self-supervised learning
- **Context-aware**: Understands word meaning based on surrounding context
- **Transfer Learning**: Can be fine-tuned for specific tasks with minimal additional training

## How does the BERT model work for text classification?

### 1. **Text Classification process**
1. **Input Tokenization**: Text is converted to token IDs using WordPiece tokenization
2. **Embedding**: Tokens are converted to dense vector representations
3. **Transformer Layers**: 12 layers (BERT-base) or 24 layers (BERT-large) process the embeddings
4. **[CLS] Token**: Special classification token whose final representation is used for classification
5. **Classification Head**: A simple linear layer maps BERT output to class probabilities

### 2. **Fine-tuning process**
Fine-tuning adapts the pre-trained BERT model to specific classification tasks:
- **Transfer Learning**: Start with pre-trained BERT weights
- **Task specific layer**: Add a classification head for your specific number of classes
- **End-to-end training**: Update all model parameters using labeled data from your domain
- **Lower Learning Rate**: Use smaller learning rates (2e-5) to preserve pre-trained knowledge

## How fine-tuning works?

### Supervised learning approach
Text classification uses **supervised learning**:
1. **Labeled dataset**: Collection of texts with their corresponding category labels
2. **Training**: Algorithm learns patterns from labeled examples
3. **Validation**: Model performance is evaluated on unseen data
4. **Inference**: Trained model predicts categories for new text

### Pre-trained model
- **Training time**: Start with language understanding already learned
- **Performance**: Leverages patterns from massive text corpora
- **Less data required**: Fine-tuning needs fewer labeled examples than training from scratch
- **Hugging Face Hub**: Easy access to pre-trained models

## Step-by-step

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

> **For detailed API documentation, examples, and troubleshooting, see [DOCUMENTATION.md](./DOCUMENTATION.md)**

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

### Docker deployment (Options)

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


#### **Performance optimization**
```bash
# Use multi-stage builds
# Enable Docker BuildKit
DOCKER_BUILDKIT=1 docker build -t bert-classifier .

# Use .dockerignore to exclude unnecessary files
# Optimize layer caching by copying requirements first
```

## Challenges in Evaluating LLMs

### **Limitations of Existing Metrics**
Many evaluation metrics fail to capture nuanced aspects of language, such as:
- **Context understanding**: Traditional metrics may not assess how well models understand implicit meanings
- **Semantic coherence**: Lexical overlap metrics can miss semantic consistency
- **Cultural sensitivity**: Bias detection requires specialized evaluation frameworks
- **Domain adaptation**: Generic metrics may not reflect performance in specific domains

### **Complexity of Language Understanding**
The intricate nature of human language makes it challenging to develop comprehensive assessment metrics:
- **Ambiguity**: Natural language contains inherent ambiguities that are difficult to measure
- **Contextual dependencies**: Long-range dependencies in text require sophisticated evaluation
- **Subjective quality**: Aspects like style, tone, and appropriateness are subjective
- **Multilingual considerations**: Cross-lingual evaluation introduces additional complexity

### **Human Evaluation Challenges**
While human evaluation is considered the gold standard, it has limitations:
- **Scalability**: Human evaluation is expensive and time-consuming
- **Consistency**: Inter-annotator agreement can be low for subjective tasks
- **Bias**: Human evaluators may introduce their own biases
- **Expertise requirements**: Some tasks require domain-specific knowledge

## Benchmark Tasks for LLM Comparison

When comparing different Large Language Models (LLMs), it is essential to adopt a systematic approach using standardized benchmarks:

### **Common Benchmark Tasks**
- **Sentiment Analysis**: Assess emotional tone understanding
- **Text Summarization**: Evaluate ability to generate concise summaries
- **Question Answering**: Test comprehension and reasoning capabilities
- **Natural Language Inference**: Measure logical reasoning skills
- **Machine Translation**: Evaluate cross-lingual capabilities

### **Benchmark Datasets**
- **GLUE/SuperGLUE**: General language understanding benchmarks
- **SQuAD**: Reading comprehension dataset
- **WMT**: Machine translation benchmarks
- **BLEU/ROUGE**: Text generation evaluation
- **HellaSwag**: Commonsense reasoning

## Conclusions

In this evaluation and metrics guide, we explored the comprehensive practices and metrics used to evaluate Large Language Models (LLMs) and fine-tuned BERT models. 

### **Takeaways**

1. **Multi-faceted Evaluation**: Effective LLM evaluation requires combining multiple metrics rather than relying on a single measure. Different metrics capture different aspects of model performance.

2. **Task-Specific Metrics**: The choice of evaluation metrics should align with the specific task and application requirements. What works for text classification may not be suitable for text generation.

3. **Automated vs. Human Evaluation**: While automated metrics provide scalable and consistent evaluation, human evaluation remains crucial for assessing subjective qualities and edge cases.

4. **Continuous Monitoring**: Model evaluation should be an ongoing process, especially in production environments where data distribution may shift over time.

5. **Bias and Fairness**: Modern LLM evaluation must include assessments of bias, fairness, and ethical considerations to ensure responsible AI deployment.

### **Best Practices for LLM Evaluation**

- **Establish baseline models** for comparison
- **Use multiple evaluation metrics** to capture different aspects of performance
- **Include domain-specific test cases** relevant to your application
- **Monitor both automated metrics and human feedback**
- **Regularly update evaluation datasets** to reflect real-world scenarios
- **Document evaluation methodology** for reproducibility

### **Directions**

The field of LLM evaluation continues to evolve with:
- **Emerging metrics** that better capture semantic understanding
- **Automated human-aligned evaluation** using AI judges
- **Real-time evaluation frameworks** for production systems
- **Cross-modal evaluation** for multimodal language models

As LLMs become more sophisticated, evaluation methodologies must also advance to ensure we can effectively measure and improve model performance across diverse applications and use cases.

## What are LLM Evaluation Metrics?

LLM evaluation metrics are quantitative and qualitative measures used to assess the performance, accuracy, and quality of Large Language Models. These metrics help developers understand how well their models perform on specific tasks and guide improvements during fine-tuning.

### Why do we need LLM evaluation metrics?

Evaluating LLMs is essential to ensure models are reliable, accurate, and safe before deploying applications in production. Without proper evaluation:
- Models may produce inaccurate or biased outputs
- Performance degradation may go unnoticed
- Business objectives may not be met
- User trust and safety could be compromised

### Categories of LLM Evaluation Metrics

When evaluating LLMs, it's helpful to consider different categories of metrics:

#### **Automatic Metrics**
Quantitative scores computed by algorithms or models. These require no human in the loop and often compare the LLM output against a reference or use an intrinsic measure.

**Examples**: perplexity, BLEU/ROUGE scores, BERTScore, MAUVE, exact match accuracy.

#### **Human-Aligned Metrics**
Qualitative judgments reflecting human preferences or values. These include clarity, coherence, helpfulness, harmlessness, etc., and are often obtained via human raters or learned proxies (like another LLM "judge").

**Examples**: toxicity level, factuality/faithfulness, helpfulness ratings.

### LLM Evaluation Metric Categories

#### 1. **Language Modeling Metrics (Statistical)**
These measure how well a model predicts text, typically at the token or sequence level.
- **Perplexity (PPL)**: Measures how well a probability distribution predicts a sample
- **Cross-entropy loss**: Quantifies the difference between predicted and actual distributions

#### 2. **Lexical Overlap Metrics**
Compare n-grams or word overlaps between generated text and reference.
- **BLEU (Bilingual Evaluation Understudy)**: Measures n-gram overlap with brevity penalty
- **ROUGE (Recall-Oriented Understudy for Gisting Evaluation)**: Focuses on recall in text summarization
- **METEOR**: Considers word-level matching including synonyms and paraphrases
- **CIDEr**: Consensus-based metric for image captioning

#### 3. **Embedding-Based Metrics**
Leverage semantic embeddings to measure similarity rather than exact overlap.
- **BERTScore**: Uses BERT embeddings to measure semantic similarity
- **MoverScore**: Earth Mover's Distance on contextualized embeddings

#### 4. **Learned Metrics**
Neural models fine-tuned on human judgments to directly predict quality scores.
- **BLEURT**: BERT-based metric trained on human ratings
- **COMET**: Cross-lingual metric trained on human assessments

#### 5. **Diversity Metrics**
Track repetitiveness or variety in generated text.
- **Distinct-n**: Measures uniqueness of n-grams in generated text
- **Self-BLEU**: Measures diversity by computing BLEU scores within generated samples

#### 6. **Task/Domain-Specific Metrics**
Designed to capture factual consistency or semantic relations.
- **Exact Match (EM)**: Binary metric for exact answer matching
- **F1 Score**: Harmonic mean of precision and recall
- **Accuracy**: Percentage of correct predictions
- **Q²**: Question-answering evaluation metric
- **SPICE**: Semantic evaluation for image captioning

#### 7. **Human Evaluation**
The "gold standard" for evaluating coherence, style, correctness, and nuanced aspects.

## Metrics for LLM Accuracy

### Task-Specific Accuracy Metrics

#### **Exact Match (EM)**
A simple metric that checks how often the model's predicted answer matches the reference answer exactly. Commonly used for question-answering tasks.

#### **F1 Score**
More flexible than EM, measures the overlap between predicted and reference answers. Especially useful when there are multiple valid answers.

#### **Accuracy**
The percentage of correct answers over the total number of questions asked. Straightforward but can be limiting for complex tasks with multiple possible answers.

### Statistical Accuracy Metrics

#### **Perplexity**
Perplexity is a key metric used to evaluate language models by measuring how well a model predicts a sequence of words. It is defined as the exponential of the average negative log-likelihood. **Lower perplexity indicates better performance**.

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model = AutoModelForCausalLM.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained("gpt2")
text = "Hello, how are you?"
enc = tokenizer(text, return_tensors="pt")
with torch.no_grad():
    # Compute negative log-likelihood loss
    loss = model(**enc, labels=enc["input_ids"]).loss
    perplexity = torch.exp(loss)
print(f"Perplexity: {perplexity.item():.2f}")
```

#### **Cross-entropy Loss**
Widely used to assess the dissimilarity between predicted probability distribution and actual distribution of words. Minimizing cross-entropy loss helps models make more accurate predictions.

### Semantic Similarity Metrics

#### **Cosine Similarity**
Compares predicted answer embeddings with reference answer embeddings. Higher similarity indicates better performance.

#### **BERTScore**
BERTScore is an evaluation metric tool that uses BERT embeddings to measure semantic similarity between generated and reference texts, offering a nuanced assessment of text quality.

```python
# Install bert_score library
# !pip install bert_score

from bert_score import score

candidates = ["The cat sits on the mat"]
references = ["A feline rests upon a rug"]
P, R, F1 = score(candidates, references, lang="en", verbose=True)
print(f"BERTScore F1: {F1[0]:.4f}")
```

### Lexical Similarity Metrics

#### **BLEU Score**
BLEU (Bilingual Evaluation Understudy) evaluates machine-generated text quality by comparing overlapping n-grams with reference texts.

**How BLEU works:**
- **N-gram Overlap**: Calculates proportion of overlapping n-grams (1-grams, 2-grams, 3-grams, 4-grams)
- **Precision**: Fraction of overlapping n-grams between machine output and reference
- **Brevity Penalty (BP)**: Prevents overly short sentences that might have high precision but low quality

#### **ROUGE Score**
ROUGE (Recall-Oriented Understudy for Gisting Evaluation) primarily evaluates text summaries by focusing on recall.

**Main ROUGE metrics:**
- **ROUGE-N**: Measures n-gram overlap between reference and generated text
- **ROUGE-1**: Evaluates overlap of single words (unigrams)
- **ROUGE-2**: Measures overlap of bigrams (two consecutive words)
- **ROUGE-L**: Focuses on longest common subsequence (LCS)
- **ROUGE-W**: Weights longer continuous matches higher
- **ROUGE-S**: Skip-bigram metric for non-consecutive bigrams

### Model-Based Scores

#### **BLEURT**
BLEURT (Bilingual Evaluation Understudy with Representations from Transformers) uses pre-trained models like BERT to score LLM outputs against expected outputs.

### Bias and Fairness Metrics

#### **Bias Metrics**
Quantify biases in machine learning models, measuring how predictions differ across groups based on sensitive attributes (race, gender, age).

#### **Fairness Metrics**
Evaluate how fairly models treat different groups, ensuring equitable outcomes across diverse populations.

## Testing fine-tuning success

### 1. **Training metrics**
- **Loss Reduction**: Training loss should decrease over epochs
- **Convergence**: Loss should stabilize (not oscillate wildly)
- **No Overfitting**: Validation loss shouldn't increase while training loss decreases

### 2. **Evaluation metrics**
- **Accuracy**: Percentage of correctly classified samples
- **Precision**: True positives / (True positives + False positives)
- **Recall**: True positives / (True positives + False negatives)  
- **F1-Score**: Harmonic mean of precision and recall

### 3. **Test cases**
```python
# Example test cases
test_cases = [
    ("I love this product!", 1),      # Positive
    ("This is terrible quality", 0),   # Negative
    ("Average experience", ???),       # Neutral - check model confidence
]
```

## Model performance evaluation

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

## References

### **Core Documentation**
- **DOCUMENTATION.md**: [Complete API Reference and Usage Guide](./DOCUMENTATION.md)

### **Research Papers**
- **BERT Paper**: [BERT: Pre-training of Deep Bidirectional Transformers](https://arxiv.org/abs/1810.04805)
- **Attention Mechanism**: [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- **BERTScore**: [BERTScore: Evaluating Text Generation with BERT](https://arxiv.org/abs/1904.09675)

### **Evaluation Metrics and Fine-tuning**
- **AWS SageMaker**: [Metrics for fine-tuning large language models in Autopilot](https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-llms-finetuning-metrics.html)
- **Hugging Face PEFT**: [PEFT methods to fine-tune LLM models](https://huggingface.co/blog/samuellimabraz/peft-methods)
- **LLM Evaluation**: [Let's talk about LLM evaluation](https://huggingface.co/blog/clefourrier/llm-evaluation)
- **Comprehensive Guide**: [LLM evaluation metrics - A comprehensive guide](https://wandb.ai/onlineinference/genai-research/reports/LLM-evaluation-metrics-A-comprehensive-guide-for-large-language-models--VmlldzoxMjU5ODA4NA)
- **BERTScore Deep Dive**: [Understanding BERTScore](https://spotintelligence.com/2024/08/20/bertscore/)

### **Technical Resources**
- **Hugging Face Hub**: [https://huggingface.co/](https://huggingface.co/)
- **PyTorch**: [https://pytorch.org/](https://pytorch.org/)
- **Text Classification with BERT**: [https://www.sabrepc.com/blog/Deep-Learning-and-AI/text-classification-with-bert](https://www.sabrepc.com/blog/Deep-Learning-and-AI/text-classification-with-bert)

### **Evaluation Tools and Libraries**
- **Evaluation Metrics for ML and AI Models**: [GitHub Repository](https://github.com/xbeat/Machine-Learning/blob/main/Evaluation%20Metrics%20for%20ML%20and%20AI%20Models%20in%20Python.md)
- **BERT Score Library**: `pip install bert_score`
- **Scikit-learn Metrics**: [Classification Metrics Documentation](https://scikit-learn.org/stable/modules/model_evaluation.html)
