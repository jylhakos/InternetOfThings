# Feature Learning

## Project Overview

This Feature Learning project demonstrates approaches to learning feature representations using PyTorch.

1. **Convolutional Neural Networks (CNNs)** - For spatial feature learning from images
2. **Recurrent Neural Networks (RNNs/Transformers)** - For sequential feature learning from text
3. **Autoencoders** - For unsupervised dimensionality reduction and feature learning
4. **Transfer Learning** - For leveraging pre-trained models for feature extraction

## 📁 Project Structure

```
Feature Learning/
├── README.md                           # Main project documentation
├── .gitignore                         # Git ignore file (excludes datasets, models, venv)
├── requirements.txt                   # Python dependencies
├── setup.py                          # Package installation setup
├── test_setup.py                     # Setup verification script
│
├── scripts/                          # Shell scripts for automation
│   ├── setup_environment.sh          # Virtual environment setup
│   ├── download_datasets.sh          # Dataset download automation
│   └── run_experiments.sh           # Run all experiments
│
├── src/                              # Source code
│   ├── __init__.py
│   │
│   ├── data/                         # Data loading and preprocessing
│   │   ├── __init__.py
│   │   ├── data_loaders.py          # Dataset loaders (MNIST, WikiText-2, etc.)
│   │   └── preprocessing.py         # Data preprocessing utilities
│   │
│   ├── models/                       # Neural network architectures
│   │   ├── __init__.py
│   │   ├── cnn_models.py           # CNN architectures
│   │   ├── rnn_models.py           # RNN/LSTM/GRU models
│   │   ├── autoencoder_models.py   # Autoencoder variants
│   │   └── transformer_models.py   # Transformer models
│   │
│   ├── training/                     # Training scripts
│   │   ├── __init__.py
│   │   ├── train_cnn.py            # CNN training
│   │   ├── train_rnn.py            # RNN training
│   │   ├── train_autoencoder.py    # Autoencoder training
│   │   ├── train_transfer_learning.py # Transfer learning
│   │   └── simple_cnn_demo.py      # Simple demo script
│   │
│   ├── utils/                        # Utility functions
│   │   ├── __init__.py
│   │   ├── metrics.py              # Evaluation metrics
│   │   ├── visualization.py        # Plotting and visualization
│   │   └── feature_extraction.py   # Feature extraction utilities
│   │
│   └── evaluation/                   # Evaluation and analysis
│       ├── __init__.py
│       └── evaluate_features.py    # Feature quality evaluation
│
├── notebooks/                        # Jupyter notebooks for exploration
│   ├── cnn_feature_learning.ipynb
│   ├── rnn_feature_learning.ipynb
│   ├── autoencoder_feature_learning.ipynb
│   └── transfer_learning.ipynb
│
├── tests/                            # Unit tests
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_data_loaders.py
│   └── test_training.py
│
├── docs/                             # Documentation
│   ├── architecture_diagram.md
│   ├── workflow.md
│   └── troubleshooting.md
│
├── venv/                             # Virtual environment (excluded from git)
├── datasets/                         # Downloaded datasets (excluded from git)
├── models/                           # Saved models (excluded from git)
├── results/                          # Results and outputs (excluded from git)
└── logs/                            # Training logs (excluded from git)
```

## 🔧 Setup and Usage

### 1. Environment Setup
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Setup virtual environment and install dependencies
bash scripts/setup_environment.sh

# Activate virtual environment
source venv/bin/activate
```

### 2. Download Datasets
```bash
# Download all required datasets
bash scripts/download_datasets.sh
```

### 3. Test Setup
```bash
# Verify everything is working
python test_setup.py
```

### 4. Run Experiments
```bash
# Run all feature learning experiments
bash scripts/run_experiments.sh

# Or run individual experiments
python src/training/simple_cnn_demo.py
```

## Datasets

### 1. MNIST (Handwritten Digits)
- **Size**: 60K training + 10K test samples
- **Format**: 28x28 grayscale images
- **Classes**: 10 (digits 0-9)
- **Use Case**: CNN feature learning

### 2. Fashion-MNIST
- **Size**: 60K training + 10K test samples
- **Format**: 28x28 grayscale images
- **Classes**: 10 (clothing items)
- **Use Case**: Autoencoder feature learning

### 3. WikiText-2
- **Size**: ~36K articles (~4.5MB)
- **Format**: Raw text data
- **Use Case**: RNN/Transformer feature learning

### 4. SQuAD v1.1
- **Size**: 100K+ question-answer pairs (~35MB)
- **Format**: Structured JSON
- **Use Case**: Transfer learning with BERT

## Model Architectures

### 1. CNN Models (src/models/cnn_models.py)

#### SimpleCNN
- 3 convolutional layers (32→64→128 filters)
- BatchNorm + ReLU + MaxPool
- 2 fully connected layers
- Dropout for regularization

#### FeatureCNN
- VGG-like architecture
- Global average pooling
- Dedicated feature projection layer

#### ResNetFeatureExtractor
- Pre-trained ResNet50 backbone
- Frozen/unfrozen backbone options
- Custom feature projection head

### 2. RNN Models (src/models/rnn_models.py)

#### FeatureLSTM
- Bidirectional LSTM
- Variable sequence length support
- Attention mechanisms
- Feature projection layer

#### TransformerFeatureExtractor
- Multi-head attention
- Positional encoding
- Layer normalization
- Global pooling for sequence-level features

### 3. Autoencoder Models (src/models/autoencoder_models.py)

#### ConvAutoencoder
- Encoder: Conv2d → MaxPool → Feature space
- Decoder: ConvTranspose2d → Reconstruction
- Bottleneck feature representation

#### VariationalAutoencoder (VAE)
- Probabilistic encoder (μ, σ)
- Reparameterization trick
- KL divergence regularization
- Latent space interpolation

### 4. Transfer Learning Models (src/models/transformer_models.py)

#### BERTFeatureExtractor
- Pre-trained BERT architecture
- [CLS] token pooling
- Fine-tuning capabilities
- Multi-layer feature extraction

## Feature Learning Use Cases

### Use Case 1: Image Classification with CNN Features

```python
# Train CNN on MNIST
python src/training/train_cnn.py --dataset mnist --epochs 10

# Extract features
features = model.extract_features(images)  # Shape: [batch, 256]

# Use features for downstream tasks
classifier = LogisticRegression()
classifier.fit(features, labels)
```

### Use Case 2: Text Representation with RNN Features

```python
# Train LSTM on WikiText-2
python src/training/train_rnn.py --dataset wikitext2 --epochs 5

# Extract sequence features
sequence_features = model.extract_features(text_sequences)  # Shape: [batch, 128]

# Use for text classification or clustering
```

### Use Case 3: Dimensionality Reduction with Autoencoders

```python
# Train autoencoder for compression
python src/training/train_autoencoder.py --latent_dim 64

# Compress data
compressed = autoencoder.encode(data)  # Shape: [batch, 64]

# Reconstruct data
reconstructed = autoencoder.decode(compressed)
```

### Use Case 4: Transfer Learning with Pre-trained Models

```python
# Use pre-trained BERT features
python src/training/train_transfer_learning.py --pretrained_model bert

# Extract contextual features
contextual_features = bert_model.extract_features(text)
```

## Evaluation and Metrics

### Feature Quality Metrics

```python
# Basic statistics
metrics = {
    'num_features': features.shape[1],
    'sparsity': np.mean(features == 0),
    'mean': np.mean(features),
    'std': np.std(features)
}

# Downstream task performance
knn_accuracy = train_knn_classifier(features, labels)
svm_accuracy = train_svm_classifier(features, labels)
cluster_purity = evaluate_clustering(features, labels)
```

### Evaluation Script Usage

```bash
# Evaluate single feature set
python src/evaluation/evaluate_features.py --features-path results/cnn_features.npz

# Compare multiple methods
python src/evaluation/evaluate_features.py --compare
```

## Visualization and Analysis

### Feature Visualization

1. **t-SNE/PCA Plots**: Visualize high-dimensional features in 2D
2. **Feature Maps**: Visualize CNN activation maps
3. **Attention Maps**: Visualize attention weights in transformers
4. **Reconstruction Quality**: Compare input vs. autoencoder output
5. **Learning Curves**: Plot training/validation loss and accuracy

### Example Visualizations

```python
# t-SNE visualization
plot_tsne(features, labels, save_path='results/tsne_plot.png')

# Feature activation maps
visualize_feature_maps(cnn_model, sample_images)

# Training curves
plot_training_curves(train_losses, val_losses, 'results/training.png')
```

## 🔧 Configuration

### Custom Model Training

```python
# Custom CNN architecture
model = create_cnn_model(
    model_type='feature',
    input_channels=3,
    feature_dim=512
)

# Custom training parameters
train_cnn(
    dataset='custom',
    epochs=50,
    batch_size=128,
    learning_rate=0.0001,
    device='cuda'
)
```

### Hyperparameter Tuning

```yaml
# training_config.yaml
model:
  type: 'cnn'
  architecture: 'resnet'
  pretrained: true

training:
  epochs: 20
  batch_size: 64
  learning_rate: 0.001
  weight_decay: 1e-4
  
data:
  dataset: 'mnist'
  augmentation: true
  validation_split: 0.2
```

## Production Deployment

### Model Serving

```python
# Save trained model
torch.save({
    'model_state_dict': model.state_dict(),
    'feature_dim': model.feature_dim,
    'model_config': model_config
}, 'models/production_model.pth')

# Load and use for inference
checkpoint = torch.load('models/production_model.pth')
model.load_state_dict(checkpoint['model_state_dict'])
features = model.extract_features(new_data)
```

### Batch Processing

```python
# Process large datasets in batches
def extract_features_batch(model, dataloader):
    features = []
    for batch in dataloader:
        with torch.no_grad():
            batch_features = model.extract_features(batch)
            features.append(batch_features.cpu().numpy())
    return np.vstack(features)
```

## Research

### Academic Use Cases

1. **Computer Vision**: Object recognition, medical imaging, satellite imagery
2. **Natural Language Processing**: Sentiment analysis, document classification, machine translation
3. **Bioinformatics**: Protein structure prediction, gene expression analysis
4. **Time Series Analysis**: Financial forecasting, sensor data analysis
5. **Multimodal Learning**: Image captioning, video understanding

### Extension

1. **Self-supervised Learning**: Contrastive learning, masked language modeling
2. **Multi-task Learning**: Shared feature representations across tasks
3. **Federated Learning**: Distributed feature learning
4. **Neural Architecture Search**: Automated model design
5. **Interpretability**: Understanding learned features

## 🛠 Troubleshooting

### Memory Issues
```python
# Reduce batch size
BATCH_SIZE = 16

# Use gradient accumulation
loss = loss / accumulation_steps
loss.backward()
if (step + 1) % accumulation_steps == 0:
    optimizer.step()
    optimizer.zero_grad()
```

### Slow Training
```python
# Use mixed precision training
from torch.cuda.amp import GradScaler, autocast

scaler = GradScaler()
with autocast():
    output = model(input)
    loss = criterion(output, target)

scaler.scale(loss).backward()
scaler.step(optimizer)
scaler.update()
```

### CUDA Out of Memory
```python
# Clear cache
torch.cuda.empty_cache()

# Use CPU for large models
model = model.cpu()
```

## Resources

### Documentation Links
- [PyTorch Tutorials](https://pytorch.org/tutorials/)
- [Hugging Face Datasets](https://huggingface.co/docs/datasets/)
- [Transfer Learning Guide](https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html)

### Research Papers
- "Deep Learning" by Goodfellow, Bengio, and Courville
- "Attention Is All You Need" (Transformer paper)
- "Auto-Encoding Variational Bayes" (VAE paper)

### Community
- [PyTorch Forums](https://discuss.pytorch.org/)
- [Papers with Code](https://paperswithcode.com/)

---
