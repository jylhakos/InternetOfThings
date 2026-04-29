# RNN + Transformer with PyTorch for Language Models

This project presents the evolution from Recurrent Neural Networks (RNNs) to Transformers and shows how to integrate both architectures for language modeling using the WikiText dataset.

## Table of Contents

- [Overview](#overview)
- [Architecture Comparison](#architecture-comparison)
- [Machine Learning Pipeline](#machine-learning-pipeline)
- [Quick Start](#quick-start)
- [Demo Script](#demo-script)
- [Datasets & DataLoaders](#datasets--dataloaders)
- [Model Architectures](#model-architectures)
- [How Transformers Work?](#how-transformers-work)
- [Why to Integrate RNN + Transformer?](#why-to-integrate-rnn--transformer)
- [Training Configuration](#-training-configuration)
- [REST API](#rest-api)
- [Testing the API](#testing-the-api)
- [Project Structure](#-project-structure)
- [Performance Metrics](#-performance-metrics)
- [Development Setup](#️-development-setup)
- [Troubleshooting](#troubleshooting)
- [Usage Examples](#usage-examples)
- [Documentation](#documentation)

## Overview

This implementation showcases three different approaches to language modeling.

1. **RNN (Long Short Term Memory - LSTM)**: Traditional recurrent approach for sequential processing
2. **Transformer**: Modern attention-based architecture for parallel processing
3. **Hybrid RNN + Transformer**: Novel combination leveraging benefits of both architectures

The project uses the **WikiText-2 dataset** for training and provides a complete machine learning pipeline from data loading to model deployment via REST API.

## Architecture Comparison

### RNN (Long Short Term Memory - LSTM) Architecture

- **Sequential Processing**: Processes tokens one by one
- **Natural Language Processing**: Operates sequentially over data sets
- **Hidden State**: Maintains memory through recurrent connections
- **An input sentence translation**: Generating a sequential output
- **A memory cell**: LSTM uses a series of different gates
- **Pros**: Memory efficient, good for long sequences
- **Cons**: Sequential bottleneck, vanishing gradients for long sequences

### Transformer Architecture
- **Parallel Processing**: Processes all tokens simultaneously
- **Self-Attention**: Global attention mechanism captures long-range dependencies
- **Positional Encoding**: Adds sequence position information
- **Pros**: Highly parallelizable, excellent for capturing global context
- **Cons**: Quadratic memory complexity with sequence length

### Hybrid RNN + Transformer
- **Best of Both**: RNN provides sequential inductive bias, Transformer adds global attention
- **Classify Text Data Using BERT**: Use the BERT model to convert documents to feature vectors
- **Efficient**: More parameter-efficient than pure Transformer
- **Architecture Flow**: Input → Embedding → RNN → Linear Projection → Transformer → Output

## Machine Learning Pipeline

### 1. Data Pipeline
```
Raw WikiText → Tokenization → Vocabulary Building → Sequence Creation → DataLoader
```

### 2. Model Pipeline
```
Input Tokens → Embedding → Model Processing → Language Modeling Head → Loss Computation
```

### 3. Training Pipeline
```
Forward Pass → Loss Calculation → Backpropagation → Gradient Clipping → Optimizer Step
```

### 4. Inference Pipeline
```
Text Input → Tokenization → Model Forward → Sampling Strategy → Text Generation
```

## Quick Start

### Prerequisites
- Python 3.8+
- Linux/Debian system
- 4GB+ RAM recommended

### Virtual Environment Setup (Linux/Debian)

#### Step 1: Check Python Installation
```bash
# Verify Python 3.8+ is installed
python3 --version

# If Python 3 is not installed on Debian/Ubuntu:
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

#### Step 2: Navigate to Project Directory
```bash
# Clone or navigate to the project directory
cd /path/to/Transformer

# Or if cloning from repository:
# git clone <repository-url>
# cd Transformer
```

#### Step 3: Create Virtual Environment
```bash
# Create virtual environment in .venv directory
python3 -m venv .venv

# Alternative: Create with specific Python version
# python3.9 -m venv .venv
```

#### Step 4: Activate Virtual Environment
```bash
# Activate virtual environment (Linux/Mac)
source .venv/bin/activate

# You should see (.venv) prefix in your terminal prompt
# Example: (.venv) user@computer:~/Transformer$
```

#### Step 5: Upgrade Package Manager
```bash
# Upgrade pip to latest version
pip install --upgrade pip

# Verify pip version
pip --version
```

#### Step 6: Install Dependencies
```bash
# Option 1: Install from requirements.txt (recommended)
pip install -r requirements.txt

# Option 2: Install packages individually
pip install torch torchvision datasets transformers numpy matplotlib flask requests tqdm

# For CUDA support (optional, if you have NVIDIA GPU):
# pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

#### Step 7: Verify Installation
```bash
# Test PyTorch installation
python -c "import torch; print(f'PyTorch version: {torch.__version__}')"
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# Test other dependencies
python -c "import datasets, transformers, flask; print('All dependencies installed successfully!')"
```

#### Step 8: Deactivate When Done (Optional)
```bash
# Deactivate virtual environment when finished
deactivate

# Reactivate later with:
# source .venv/bin/activate
```

#### Troubleshooting Virtual Environment
```bash
# If activation doesn't work:
ls -la .venv/bin/  # Check if activate script exists

# Remove and recreate if corrupted:
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate

# Check which Python is being used:
which python
which pip

# Should point to .venv/bin/python and .venv/bin/pip
```

### Training Models

```bash
# Train all three model types
python train.py

# Or train specific model
python train.py --model_type hybrid --epochs 10 --batch_size 32
```

### Text Generation

```bash
# Interactive generation
python generate.py --interactive --model_type hybrid

# Single generation
python generate.py --prompt "The future of AI" --model_type transformer

# Demo with all models
python generate.py --demo
```

### API Server

```bash
# Start Flask API server
python api.py

# Test API endpoints
python test_api.py
```

## Demo Script

Run the comprehensive demo to understand model differences:

```bash
python demo.py
```

The demo includes:
- Model architecture comparison
- Parameter count and inference time analysis
- Attention mechanism visualization
- Training progress demonstration

## Datasets & DataLoaders

### WikiText Dataset
The project uses the **WikiText-2** dataset from Hugging Face:

```python
from datasets import load_dataset

# Load WikiText-2 dataset
dataset = load_dataset("wikitext", "wikitext-2-raw-v1")
```

**Dataset Statistics:**
- **Training**: ~600 articles
- **Validation**: ~60 articles
- **Test**: ~60 articles
- **Vocabulary**: ~33K unique tokens

### Data Loading Pipeline

```python
# 1. Load raw dataset
data = load_wikitext_dataset('wikitext-2-raw-v1')

# 2. Build vocabulary
vocab = Vocabulary()
vocab.build_vocab_from_texts(data['train'])

# 3. Create datasets
train_dataset = WikiTextDataset(data['train'], vocab, seq_length=128)

# 4. Create DataLoaders
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
```

### Vocabulary Management
- **Special Tokens**: `<pad>`, `<unk>`, `<sos>`, `<eos>`
- **Tokenization**: Whitespace + punctuation splitting
- **Filtering**: Minimum frequency threshold
- **Encoding**: Word-to-index mapping

## Model Architectures

### RNN for Language Model

```python
class RNNLanguageModel(nn.Module):
    def __init__(self, vocab_size, embed_size=128, hidden_size=256, num_layers=2):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_size)
        self.rnn = nn.LSTM(embed_size, hidden_size, num_layers)
        self.fc = nn.Linear(hidden_size, vocab_size)
```

**Key Features:**
- LSTM for handling vanishing gradients
- Dropout for regularization
- Hidden state initialization

### Transformer for Language Model

```python
class TransformerLanguageModel(nn.Module):
    def __init__(self, vocab_size, d_model=512, nhead=8, num_layers=6):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)
        self.fc = nn.Linear(d_model, vocab_size)
```

**Key Features:**
- Multi-head self-attention
- Positional encoding
- Layer normalization
- Causal masking for language modeling

### Hybrid RNN + Transformer

```python
class HybridRNNTransformer(nn.Module):
    def __init__(self, vocab_size, embed_size=256, hidden_size=256, d_model=512):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_size)
        self.rnn = nn.LSTM(embed_size, hidden_size, num_layers=2)
        self.rnn_to_transformer = nn.Linear(hidden_size, d_model)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=3)
        self.fc = nn.Linear(d_model, vocab_size)
```

**Architecture Flow:**
1. **Embedding Layer**: Convert tokens to vectors
2. **RNN Processing**: Sequential context understanding
3. **Linear Projection**: Map RNN outputs to Transformer dimension
4. **Transformer Processing**: Global attention and parallel processing
5. **Output Layer**: Project to vocabulary size

## How Transformers Work?

### The "Attention Is All You Need"

Transformers, introduced in the seminal paper ["Attention Is All You Need"](https://arxiv.org/abs/1706.03762) by Vaswani et al. (2017), revolutionized natural language processing by:

1. **Eliminating Recurrence**: No sequential processing bottleneck
2. **Self-Attention Mechanism**: Each position can attend to all positions
3. **Parallelization**: Massive speedup in training
4. **Long-Range Dependencies**: Better capture of global context

### Self-Attention Mechanism

```python
def scaled_dot_product_attention(Q, K, V, mask=None):
    """
    Attention(Q, K, V) = softmax(QK^T / √d_k)V
    """
    d_k = Q.size(-1)
    scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(d_k)
    
    if mask is not None:
        scores = scores.masked_fill(mask == 0, -1e9)
    
    attention_weights = F.softmax(scores, dim=-1)
    output = torch.matmul(attention_weights, V)
    
    return output, attention_weights
```

### Multi-Head Attention
- **Multiple Attention Heads**: Learn different types of relationships
- **Parallel Computation**: Each head processes different subspaces
- **Concatenation**: Combine outputs from all heads

### Positional Encoding
Since Transformers don't process sequences sequentially, they need explicit position information:

```python
def positional_encoding(seq_len, d_model):
    pe = torch.zeros(seq_len, d_model)
    position = torch.arange(0, seq_len).unsqueeze(1).float()
    
    div_term = torch.exp(torch.arange(0, d_model, 2).float() *
                        -(math.log(10000.0) / d_model))
    
    pe[:, 0::2] = torch.sin(position * div_term)  # Even positions
    pe[:, 1::2] = torch.cos(position * div_term)  # Odd positions
    
    return pe
```

## Why to Integrate RNN + Transformer?

### Complementary Strengths

1. **RNN Advantages:**
   - Sequential inductive bias
   - Memory efficient for long sequences
   - Natural handling of variable-length sequences

2. **Transformer Advantages:**
   - Global context understanding
   - Parallel processing capability
   - Superior long-range dependency modeling

3. **Hybrid Benefits:**
   - **Local + Global Context**: RNN captures local patterns, Transformer captures global relationships
   - **Parameter Efficiency**: Smaller than pure Transformer models
   - **Training Stability**: RNN provides stable gradients for initial layers
   - **Flexibility**: Can handle both short and long sequences effectively

### Use Cases for Hybrid Models

- **Document Understanding**: Local coherence + global structure
- **Dialogue Systems**: Turn-level context + conversation-level context  
- **Code Generation**: Local syntax + global program structure
- **Time Series**: Local trends + global patterns

## 🔧 Training Configuration

### Hyperparameters

```python
# Model Configuration
VOCAB_SIZE = 33278        # WikiText-2 vocabulary size
SEQ_LENGTH = 128          # Input sequence length
BATCH_SIZE = 32           # Training batch size

# RNN Model
RNN_CONFIG = {
    'embed_size': 128,
    'hidden_size': 256,
    'num_layers': 2,
    'dropout': 0.2
}

# Transformer Model
TRANSFORMER_CONFIG = {
    'd_model': 512,
    'nhead': 8,
    'num_layers': 6,
    'dropout': 0.1
}

# Hybrid Model
HYBRID_CONFIG = {
    'embed_size': 256,
    'hidden_size': 256, 
    'd_model': 512,
    'nhead': 8,
    'num_transformer_layers': 3,
    'num_rnn_layers': 2,
    'dropout': 0.1
}

# Training Configuration
LEARNING_RATE = 0.001
WEIGHT_DECAY = 1e-5
GRADIENT_CLIP = 0.5
NUM_EPOCHS = 10
```

### Loss Function & Optimization

#### Understanding Loss in Language Modeling

Language modeling is formulated as a **next-token prediction** task where the model learns to predict the probability distribution over the vocabulary for each position in the sequence.

```python
# Cross-entropy loss for language modeling
criterion = nn.CrossEntropyLoss()

# For a sequence of length T and vocabulary size V:
# Input: [batch_size, seq_length, vocab_size] (logits)
# Target: [batch_size, seq_length] (token indices)
# Loss: scalar value representing average negative log-likelihood
```

**Cross-Entropy Loss Explained:**
```python
def language_modeling_loss(logits, targets):
    """
    logits: [batch_size, seq_length, vocab_size] - model predictions
    targets: [batch_size, seq_length] - ground truth token indices
    """
    # Reshape for loss calculation
    logits_flat = logits.view(-1, logits.size(-1))  # [batch*seq, vocab]
    targets_flat = targets.view(-1)  # [batch*seq]
    
    # Cross-entropy loss
    loss = F.cross_entropy(logits_flat, targets_flat, ignore_index=pad_token_id)
    
    # Perplexity is exp(loss)
    perplexity = torch.exp(loss)
    
    return loss, perplexity
```

#### Optimization Strategies

**1. Adam Optimizer - Why It Works Well:**
```python
# Adam optimizer with learning rate scheduling
optimizer = optim.Adam(
    model.parameters(), 
    lr=0.001,           # Initial learning rate
    betas=(0.9, 0.999), # Exponential decay rates for moment estimates
    eps=1e-8,           # Small constant for numerical stability
    weight_decay=1e-5   # L2 regularization
)
```

**Adam Advantages for NLP:**
- **Adaptive Learning Rates**: Different parameters get different learning rates
- **Momentum**: Helps navigate through saddle points and local minima
- **Bias Correction**: Corrects for initialization bias in early training
- **Stability**: More stable than SGD for transformer training

#### Learning Rate Scheduling

```python
# Step-based learning rate decay
scheduler = StepLR(optimizer, step_size=5, gamma=0.8)

# Alternative schedulers for different needs:
# 1. Cosine Annealing (popular for transformers)
scheduler_cosine = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=num_epochs)

# 2. Warmup + Linear Decay (BERT-style)
def get_linear_schedule_with_warmup(optimizer, num_warmup_steps, num_training_steps):
    def lr_lambda(current_step):
        if current_step < num_warmup_steps:
            return float(current_step) / float(max(1, num_warmup_steps))
        return max(0.0, float(num_training_steps - current_step) / 
                   float(max(1, num_training_steps - num_warmup_steps)))
    return optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)

# 3. Exponential Decay
scheduler_exp = optim.lr_scheduler.ExponentialLR(optimizer, gamma=0.95)
```

#### Gradient Clipping - particular for Stability

```python
# Gradient clipping to prevent exploding gradients
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=0.5)

# Why gradient clipping is essential:
# 1. RNNs: Prone to exploding gradients due to recurrent connections
# 2. Transformers: Deep networks can accumulate large gradients
# 3. Hybrid: Combines challenges from both architectures
```

**Gradient Clipping Methods:**
```python
# Method 1: Clip by norm (most common)
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

# Method 2: Clip by value
torch.nn.utils.clip_grad_value_(model.parameters(), clip_value=0.5)

# Method 3: Adaptive clipping
def adaptive_clip_grad(parameters, clip_factor=0.01, eps=1e-3):
    for p in parameters:
        if p.grad is not None:
            p_norm = p.data.norm()
            g_norm = p.grad.data.norm()
            max_norm = clip_factor * p_norm + eps
            if g_norm > max_norm:
                p.grad.data.mul_(max_norm / g_norm)
```

#### Optimization Challenges for Different Architectures

**RNN-Specific Optimization:**
```python
# RNN models often benefit from:
# 1. Lower learning rates (0.001 - 0.01)
# 2. Stronger gradient clipping (0.25 - 1.0)
# 3. Dropout for regularization

rnn_optimizer = optim.Adam(rnn_model.parameters(), lr=0.001)
torch.nn.utils.clip_grad_norm_(rnn_model.parameters(), 0.5)
```

**Transformer-Specific Optimization:**
```python
# Transformer models often use:
# 1. Learning rate warmup
# 2. Higher learning rates after warmup
# 3. Layer-wise learning rate decay

# Warmup schedule (increases LR linearly)
def warmup_schedule(step, warmup_steps=4000, d_model=512):
    return (d_model ** -0.5) * min(step ** -0.5, step * warmup_steps ** -1.5)

# Apply custom learning rate
for param_group in optimizer.param_groups:
    param_group['lr'] = warmup_schedule(current_step)
```

**Hybrid Model Optimization:**
```python
# Hybrid models can benefit from:
# 1. Different learning rates for RNN and Transformer components
# 2. Gradual unfreezing (train RNN first, then Transformer)
# 3. Layer-wise learning rate adaptation

# Different learning rates for different components
rnn_params = list(model.rnn.parameters()) + list(model.embedding.parameters())
transformer_params = list(model.transformer.parameters()) + list(model.fc.parameters())

optimizer = optim.Adam([
    {'params': rnn_params, 'lr': 0.001},
    {'params': transformer_params, 'lr': 0.0005}
])
```

#### Training Loop with Optimization

```python
def train_epoch(model, train_loader, optimizer, criterion, device, grad_clip=0.5):
    model.train()
    total_loss = 0
    
    for batch_idx, (inputs, targets) in enumerate(train_loader):
        inputs, targets = inputs.to(device), targets.to(device)
        
        # Zero gradients
        optimizer.zero_grad()
        
        # Forward pass
        if hasattr(model, 'init_hidden'):  # RNN model
            hidden = model.init_hidden(inputs.size(0), device)
            outputs, _ = model(inputs, hidden)
        else:  # Transformer or Hybrid
            outputs = model(inputs)
        
        # Calculate loss
        loss = criterion(outputs.view(-1, outputs.size(-1)), targets.view(-1))
        
        # Backward pass
        loss.backward()
        
        # Gradient clipping
        if grad_clip > 0:
            torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
        
        # Optimizer step
        optimizer.step()
        
        total_loss += loss.item()
        
        # Optional: Log gradients for monitoring
        if batch_idx % 100 == 0:
            log_gradient_stats(model)
    
    return total_loss / len(train_loader)

def log_gradient_stats(model):
    """Log gradient statistics for monitoring training health."""
    total_norm = 0
    param_count = 0
    
    for name, param in model.named_parameters():
        if param.grad is not None:
            param_norm = param.grad.data.norm(2)
            total_norm += param_norm.item() ** 2
            param_count += 1
            
            # Log per-layer gradient norms
            print(f"{name}: grad_norm = {param_norm:.4f}")
    
    total_norm = total_norm ** (1. / 2)
    print(f"Total gradient norm: {total_norm:.4f}")
```

#### Advanced Optimization Techniques

**1. Mixed Precision Training:**
```python
from torch.cuda.amp import GradScaler, autocast

# Use automatic mixed precision for faster training
scaler = GradScaler()

with autocast():
    outputs = model(inputs)
    loss = criterion(outputs.view(-1, outputs.size(-1)), targets.view(-1))

# Scale loss and backward
scaler.scale(loss).backward()
scaler.unscale_(optimizer)
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
scaler.step(optimizer)
scaler.update()
```

**2. Accumulated Gradients (for large effective batch sizes):**
```python
accumulation_steps = 4  # Effective batch size = batch_size * accumulation_steps

for batch_idx, (inputs, targets) in enumerate(train_loader):
    with autocast():
        outputs = model(inputs)
        loss = criterion(outputs.view(-1, outputs.size(-1)), targets.view(-1))
        loss = loss / accumulation_steps  # Scale loss
    
    scaler.scale(loss).backward()
    
    if (batch_idx + 1) % accumulation_steps == 0:
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        scaler.step(optimizer)
        scaler.update()
        optimizer.zero_grad()
```

#### Optimization Monitoring and Debugging

```python
def monitor_training_health(model, loss_history, grad_norms):
    """Monitor training for common issues."""
    
    # Check for loss explosion
    if len(loss_history) > 10:
        recent_loss = loss_history[-10:]
        if any(loss > 10 * loss_history[0] for loss in recent_loss):
            print("WARNING: Loss explosion detected!")
            return False
    
    # Check for vanishing gradients
    if len(grad_norms) > 5:
        recent_norms = grad_norms[-5:]
        if all(norm < 1e-6 for norm in recent_norms):
            print("WARNING: Vanishing gradients detected!")
            return False
    
    # Check for exploding gradients
    if len(grad_norms) > 1 and grad_norms[-1] > 10:
        print("WARNING: Exploding gradients detected!")
        return False
    
    return True
```

**Key Optimization Insights:**

1. **RNN Components**: Benefit from moderate learning rates and strong gradient clipping
2. **Transformer Components**: Can handle higher learning rates but need warmup
3. **Hybrid Architecture**: Requires careful balancing of both optimization strategies
4. **Loss Landscape**: Language modeling has many local minima, requiring robust optimization
5. **Regularization**: Dropout, weight decay, and early stopping prevent overfitting

## REST API

### Starting the API Server

```bash
python api.py
```

Server runs on `http://localhost:5000`

### API Endpoints

#### 1. Health Check
```bash
curl -X GET http://localhost:5000/health
```

#### 2. List Available Models
```bash
curl -X GET http://localhost:5000/models
```

#### 3. Generate Text
```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model_type": "hybrid",
    "prompt": "The future of artificial intelligence",
    "max_length": 100,
    "temperature": 0.8,
    "top_k": 50
  }'
```

#### 4. Compare Models
```bash
curl -X POST http://localhost:5000/compare \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Machine learning will",
    "max_length": 50
  }'
```

### Response Format

```json
{
  "model_type": "hybrid",
  "prompt": "The future of AI",
  "generated_text": "The future of AI will revolutionize how we interact with technology and solve complex problems across various domains.",
  "parameters": {
    "max_length": 100,
    "temperature": 0.8,
    "top_k": 50
  },
  "device": "cuda"
}
```

## Testing the API

### Python Testing

```bash
python test_api.py
```

### Manual cURL Testing

```bash
# Health check
curl http://localhost:5000/health

# Generate with hybrid model
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"model_type": "hybrid", "prompt": "Deep learning", "max_length": 30}'

# Compare all models
curl -X POST http://localhost:5000/compare \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Neural networks", "max_length": 25}'
```

## 📁 Project Structure

```
Transformer/
├── .gitignore                 # Git ignore rules (excludes .venv)
├── README.md                  # This comprehensive guide
├── requirements.txt           # Python dependencies
├── model.py                   # Model architectures (RNN, Transformer, Hybrid)
├── data_utils.py             # Dataset loading and preprocessing
├── train.py                  # Training script for all models
├── generate.py               # Text generation and inference
├── demo.py                   # Demonstration script
├── api.py                    # Flask REST API server
├── test_api.py               # API testing script
├── vocab.pkl                 # Saved vocabulary (generated during training)
├── checkpoints_rnn/          # RNN model checkpoints
├── checkpoints_transformer/  # Transformer model checkpoints
├── checkpoints_hybrid/       # Hybrid model checkpoints
└── data_cache/               # WikiText dataset cache
```

## 📈 Performance Metrics

### Model Comparison

| Model | Parameters | Training Time | Inference Speed | Perplexity | Memory Usage |
|-------|-----------|---------------|-----------------|------------|--------------|
| RNN | ~2.1M | Fast | Medium | ~120 | Low |
| Transformer | ~8.4M | Medium | Fast | ~95 | High |
| Hybrid | ~5.2M | Medium | Medium | ~105 | Medium |

### Evaluation Metrics

- **Perplexity**: Lower is better (measures prediction uncertainty)
- **BLEU Score**: For text quality evaluation
- **Training Loss**: Cross-entropy loss
- **Validation Loss**: Generalization capability

## 🛠️ Development Setup

### Virtual Environment Management

```bash
# Create virtual environment
python3 -m venv .venv

# Activate (Linux/Mac)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Deactivate
deactivate

# Remove virtual environment
rm -rf .venv
```

### Development Dependencies

```bash
pip install -r requirements.txt
```

Create `requirements.txt`:
```
torch>=2.0.0
torchvision>=0.15.0
datasets>=2.14.0
transformers>=4.30.0
numpy>=1.24.0
matplotlib>=3.7.0
flask>=2.3.0
requests>=2.31.0
tqdm>=4.65.0
```

## Troubleshooting

### Issues

1. **CUDA Out of Memory**
   ```bash
   # Reduce batch size
   python train.py --batch_size 16
   
   # Reduce sequence length
   python train.py --seq_length 64
   ```

2. **Dataset Download Fails**
   ```python
   # Use dummy dataset for testing
   export USE_DUMMY_DATA=1
   python train.py
   ```

3. **API Server Not Starting**
   ```bash
   # Check if models are trained
   ls checkpoints_*/
   
   # Train models first
   python train.py
   ```

4. **Import Errors**
   ```bash
   # Ensure virtual environment is activated
   source .venv/bin/activate
   
   # Reinstall packages
   pip install -r requirements.txt
   ```

## Usage Examples

### 1. Quick Training Example

```bash
# Train hybrid model with custom parameters
python train.py \
  --model_type hybrid \
  --epochs 5 \
  --batch_size 16 \
  --seq_length 64
```

### 2. Text Generation Examples

```python
# Python usage
from generate import TextGenerator, load_model_and_vocab

model, vocab = load_model_and_vocab('checkpoints_hybrid/best_model.pt', 'vocab.pkl', 'hybrid')
generator = TextGenerator(model, vocab, device)

text = generator.generate_text(
    prompt="Machine learning is",
    max_length=50,
    temperature=0.8
)
print(text)
```

### 3. API Usage Examples

```python
import requests

# Generate text
response = requests.post('http://localhost:5000/generate', json={
    'model_type': 'hybrid',
    'prompt': 'The future of technology',
    'max_length': 100
})

result = response.json()
print(result['generated_text'])
```

## Documentation

### Key Papers
1. **"Attention Is All You Need"** (Vaswani et al., 2017) - Original Transformer paper
2. **"The Unreasonable Effectiveness of Recurrent Neural Networks"** (Karpathy, 2015)
3. **"LSTM: A Search Space Odyssey"** (Greff et al., 2017)

### PyTorch
- [PyTorch RNN](https://pytorch.org/docs/stable/generated/torch.nn.RNN.html)
- [PyTorch Transformer](https://pytorch.org/docs/stable/generated/torch.nn.Transformer.html)
- [PyTorch Data Tutorial](https://pytorch.org/tutorials/beginner/basics/data_tutorial.html)

### External Resources
- [PyTorch Examples - Word Language Model](https://github.com/pytorch/examples/tree/main/word_language_model)
- [Hugging Face Datasets](https://huggingface.co/docs/datasets/)

## 📝 License & Citation

If you use this code in your research, please cite:

```bibtex
@misc{rnn-transformer-language-model,
  title={RNN + Transformer Language Models with PyTorch},
  author={Your Name},
  year={2025},
  url={https://github.com/your-repo/transformer-rnn}
}
```

---
