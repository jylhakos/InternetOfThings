# Machine Learning Projects

This repository contains a collection of machine learning projects focusing on different neural network architectures and feature engineering techniques. Each project demonstrates specific concepts and provide hands-on experience with various deep learning approaches.

## Table of Contents

- [Project Overview](#project-overview)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Projects Description](#projects-description)
- [Requirements](#requirements)
- [Usage](#usage)


## Project Overview

The folders include implementations of deep learning architectures.
- **Convolutional Neural Networks (CNN)** for image processing
- **Recurrent Neural Networks (RNN)** for sequential data
- **Transformers** for natural language processing
- **Feature Learning** techniques for data representation

## Project Structure

```
MACHINE-LEARNING/
├── CNN/                         # Convolutional Neural Networks
├── Feature Learning/            # Feature Engineering & Learning
├── RNN/                         # Recurrent Neural Networks
├── Transformer/                 # Transformer Architecture
└── README.md                    # This file
```

## Projects Description

### CNN (Convolutional Neural Networks)
**Focus**: Image processing and computer vision

The CNN folder contains implementations for image classification and processing tasks:
- **MNIST digit classification** with custom CNN architecture
- **Inference demonstrations** for trained models
- **Sample generation** utilities
- **Interactive Jupyter notebooks** for experimentation

**Files**:
- `mnist_cnn.py` - Main CNN implementation
- `mnist_cnn_notebook.ipynb` - Interactive tutorial
- `custom_inference.py` - Custom model inference
- `generate_samples.py` - Data sample generation

### Feature Learning
**Focus**: Feature engineering and representation learning

This folder explores various feature learning techniques:
- **CNN-based feature extraction**
- **RNN feature learning** for sequential patterns
- **Transformer feature engineering**
- **Autoencoder dimensionality reduction**
- **Transfer learning** approaches

**Components**:
- `notebooks/` - 5 specialized Jupyter notebooks covering different techniques
- `feature_engineering/` - Extracted features and processed datasets
- `src/` - Modular source code with data loaders, models, and utilities
- `scripts/` - Automation scripts for experiments and environment setup

### RNN (Recurrent Neural Networks)
**Focus**: Sequential data processing and time series analysis

The RNN project implements recurrent architectures for sequence modeling:
- **Custom RNN model** implementations
- **API endpoints** for model serving
- **Training scripts** with checkpoint management
- **Data preprocessing** utilities

**Features**:
- `models/rnn_model.py` - Core RNN architecture
- `api/app.py` - REST API for model inference
- `scripts/train_model.py` - Training pipeline
- `notebooks/exploration.ipynb` - Data exploration

### Transformer
**Focus**: Attention-based models for NLP tasks

Modern transformer implementation with:
- **Self-attention mechanisms**
- **Multi-head attention**
- **Position encoding**
- **Text generation capabilities**

**Components**:
- `model.py` - Transformer architecture
- `train.py` - Training pipeline
- `generate.py` - Text generation utilities
- `api.py` - API interface
- `demo.py` - Interactive demonstrations

## Getting Started

### Prerequisites
- Python 3.8+
- CUDA-compatible GPU (recommended)
- pip or conda for package management

### Quick Setup
Each project folder contains its own setup instructions:

1. **Navigate to desired project**:
   ```bash
   cd CNN/  # or Feature Learning/, RNN/, Transformer/
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run setup script** (if available):
   ```bash
   bash setup.sh
   ```

### Running Projects
Each folder contains specific instructions in their respective README.md files:
- `CNN/README.md` - CNN project details
- `Feature Learning/README.md` - Feature learning guide
- `RNN/README.md` - RNN implementation guide
- `Transformer/README.md` - Transformer usage

## Requirements

### Dependencies
- PyTorch / TensorFlow
- NumPy
- Pandas
- Matplotlib
- Jupyter Notebook
- scikit-learn

### Project
Each project folder contains a `requirements.txt` file with specific dependencies.

## Usage

### For Beginners
Start with the CNN project as it provides fundamental concepts:
```bash
cd CNN/
jupyter notebook mnist_cnn_notebook.ipynb
```

### For Users
Explore the Feature Learning project for comprehensive techniques:
```bash
cd "Feature Learning"/
python demo_comprehensive_feature_engineering.py
```

### For Production Use
Check out the API implementations in RNN and Transformer folders for deployment-ready models.

## Project Highlights

- **Coverage**: From basic CNNs to advanced Transformers
- **Practical Implementation**: Ready-to-run code with real datasets
- **Production Ready**: API implementations for model deployment
- **Modular Design**: Reusable components across projects

## Git Usage

Create a feature branch (`git checkout -b feature/amazing-feature`)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---
