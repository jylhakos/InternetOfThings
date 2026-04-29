# CNN with MNIST Dataset using PyTorch

An implementation of a Convolutional Neural Network (CNN) for handwritten digit classification using the MNIST dataset and PyTorch.

## Table of Contents
- [Overview](#overview)
- [What is Convolutional Neural Networks?](#what-is-convolutional-neural-networks)
- [MNIST Dataset](#mnist-dataset)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Convolutional Neural Network Layers](#convolutional-neural-network-layers)
- [Training Process](#training-process)
- [Results](#results)
- [GPU/CPU Support](#gpucpu-support)
- [Troubleshooting](#troubleshooting)
- [Experimentation: Hyperparameters & Data-augmentation](#experimentation-hyperparameters--data-augmentation)
- [Next Steps](#next-steps)
- [References](#references)

## Overview

This project demonstrates how to build, train, and deploy a Convolutional Neural Network (CNN) for classifying handwritten digits from the MNIST dataset using PyTorch. The implementation includes:

- Data loading and preprocessing with torchvision
- CNN model definition with convolutional and fully connected layers
- Training loop with loss function and optimizer
- Model evaluation and testing
- Inference pipeline for new predictions
- Visualization of results
- GPU/CPU compatibility

## What is Convolutional Neural Networks?

### Convolutional Neural Networks (CNN)

A **Convolutional Neural Network (CNN)** is a deep learning architecture specifically designed for processing grid-like data such as images. CNNs are particularly effective for image classification, object detection, and computer vision tasks.

#### Components:

1. **Convolutional Layers**: Apply filters (kernels) to detect local features like edges, shapes, and patterns
2. **Pooling Layers**: Reduce spatial dimensions while retaining important information
3. **Activation Functions**: Introduce non-linearity (typically ReLU)
4. **Fully Connected Layers**: Combine features for final classification
5. **Dropout**: Prevent overfitting by randomly setting some neurons to zero during training

#### How CNNs Work:

```
Input Image (28x28x1)
       ↓
Convolutional Layer 1 (32 filters, 3x3)
       ↓
ReLU Activation
       ↓
Max Pooling (2x2)
       ↓
Convolutional Layer 2 (64 filters, 3x3)
       ↓
ReLU Activation
       ↓
Max Pooling (2x2)
       ↓
Flatten
       ↓
Fully Connected Layer (128 neurons)
       ↓
ReLU + Dropout
       ↓
Output Layer (10 classes)
       ↓
Softmax (probability distribution)
```

#### Advantages of CNNs for Image Processing:

- **Translation Invariance**: Can detect features regardless of their position in the image
- **Parameter Sharing**: Same filter is applied across the entire image, reducing parameters
- **Hierarchical Feature Learning**: Lower layers detect simple features, higher layers detect complex patterns
- **Spatial Locality**: Exploits the fact that nearby pixels are more related than distant ones

## MNIST Dataset

The **MNIST database** (Modified National Institute of Standards and Technology database) is a large database of handwritten digits commonly used for training and testing machine learning algorithms.

### Dataset Characteristics:
- **Training Set**: 60,000 images
- **Test Set**: 10,000 images
- **Image Size**: 28×28 pixels (grayscale)
- **Classes**: 10 digits (0-9)
- **File Format**: Each pixel value ranges from 0 (black) to 255 (white)

### Why MNIST is Perfect for CNN Learning:
- Simple and well-defined problem
- Small image size for fast training
- Clear class boundaries
- Sufficient data for training deep networks
- Standard benchmark for comparing algorithms

## Project Structure

```
CNN/
├── README.md                 # This documentation
├── requirements.txt          # Python dependencies
├── mnist_cnn.py             # Main training script
├── inference_demo.py        # Inference demonstration
├── data/                    # MNIST dataset (auto-downloaded)
├── mnist_cnn_model.pth      # Trained model weights
├── training_history.png     # Training/validation curves
├── mnist_predictions.png    # Sample predictions
└── inference_demo.png       # Inference results
```

## Setup Instructions

### Step 1: Create Virtual Environment

⚠️ **Always use a virtual environment for Python projects to avoid dependency conflicts!**

#### Using venv (Python 3.6+):
```bash
# Create virtual environment
python3 -m venv mnist_env

# Activate virtual environment
# On Linux/Mac:
source mnist_env/bin/activate
# On Windows:
# mnist_env\Scripts\activate

# Verify activation (should show virtual env path)
which python
```

#### Using conda (recommended):
```bash
# Create conda environment
conda create -n mnist_pytorch python=3.9

# Activate environment
conda activate mnist_pytorch

# Verify activation
conda info --envs
```

### Step 2: Install Dependencies

#### Option 1: Install from requirements.txt
```bash
pip install -r requirements.txt
```

#### Option 2: Install manually
```bash
# Install PyTorch (check https://pytorch.org/ for your system)
# CPU version:
pip install torch torchvision torchaudio

# GPU version (CUDA 11.8):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install additional dependencies
pip install matplotlib numpy Pillow
```

#### Option 3: Using conda
```bash
# Install PyTorch
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia

# Install additional packages
conda install matplotlib numpy pillow
```

### Step 3: Verify Installation

```bash
python -c "import torch; print('PyTorch version:', torch.__version__)"
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

### 🗂️ Git

This project follows Git best practices for machine learning projects.

1. **Repository Size**: Excluding large files keeps the repo lightweight
2. **Collaboration**: Virtual environments prevent dependency conflicts
3. **Security**: Avoids committing sensitive data or credentials
4. **Performance**: Git operations remain fast with smaller repos

#### What's Excluded from Git (.gitignore):

**Virtual Environments**:
- `mnist_env/`, `venv/`, `env/`, `.venv/`
- `pytorch_env/`, `conda_env/`

**Large Dataset Files**:
- `data/`, `dataset/`, `datasets/`
- `*.csv`, `*.h5`, `*.npz`, `*.pkl`
- Compressed files: `*.zip`, `*.tar.gz`, `*.rar`

**Model Checkpoints & Weights**:
- `*.pth`, `*.pt`, `*.ckpt`
- `checkpoints/`, `models/`

**Generated Content**:
- Training logs: `*.log`, `logs/`
- Generated images: `*.png`, `*.jpg` (except samples)
- Cache directories: `__pycache__/`, `.cache/`

**Development Files**:
- IDE settings: `.vscode/`, `.idea/`
- OS files: `.DS_Store`, `Thumbs.db`
- Jupyter checkpoints: `.ipynb_checkpoints/`

#### Managing Large Files:

If you need to share large datasets or models, consider:
- **Git LFS**: For large files that need version control
- **External Storage**: Cloud storage (Google Drive, AWS S3)
- **Data Pipelines**: Scripts that download data automatically
- **Model Hubs**: Hugging Face Hub, PyTorch Hub for pre-trained models

#### Virtual Environment Management:

```bash
# Create environment
python -m venv mnist_env

# Activate (always do this before working)
source mnist_env/bin/activate  # Linux/Mac
# mnist_env\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Work on project...

# Deactivate when done
deactivate
```

#### Setup Environments:

```bash
# Save current environment
pip freeze > requirements.txt

# Or create environment.yml for conda
conda env export > environment.yml

# Recreate environment elsewhere
pip install -r requirements.txt
# or
conda env create -f environment.yml
```

## Usage

### Training the Model (CNN)

Run the main training script:

```bash
python mnist_cnn.py
```

This will:
1. Download the MNIST dataset (if not already present)
2. Create and initialize the CNN model
3. Train the model for 10 epochs
4. Evaluate on test data
5. Save the trained model as `mnist_cnn_model.pth`
6. Generate training history plots

### Running Inference

After training, run the inference demo:

```bash
python inference_demo.py
```

This will:
1. Load the trained model
2. Make predictions on test samples
3. Display results with confidence scores
4. Generate visualization plots

### Custom Inference

You can modify `inference_demo.py` to test on your own images:

```python
# Example: Predict on custom image
image_tensor = preprocess_image('your_digit_image.png')
predicted_digit, probabilities = predict_digit(model, image_tensor, device)
print(f"Predicted digit: {predicted_digit}")
```

## 📊 Visualization Outputs

### **Where Are The PNG Files?**

You might notice that PNG files like `training_history.png`, `mnist_predictions.png`, etc., are **not visible in the folder initially**. This is normal! Here's why:

#### **PNG Files Are Generated After Running Scripts:**

| File Name | Created By | Description |
|-----------|------------|-------------|
| `training_history.png` | `mnist_cnn.py` | Training/validation loss and accuracy curves |
| `mnist_predictions.png` | `mnist_cnn.py` | Sample predictions with true/predicted labels |
| `inference_demo.png` | `inference_demo.py` | Inference results on test samples |
| `custom_prediction.png` | `custom_inference.py` | Custom image prediction with confidence |
| `confidence_distribution.png` | `custom_inference.py` | Probability distribution across all digits |

#### **Why PNG Files Are Excluded from Git:**
- **Generated Content**: These are outputs, not source code
- **Reproducible**: Anyone can generate them by running the scripts
- **File Size**: Images can be large and slow down Git operations
- **Personal Results**: Your training results may differ from others

### **Generate Sample Visualizations (Preview)**

To see what these files will look like **before** running the full training:

```bash
# Install basic dependencies first
pip install matplotlib numpy

# Generate sample plots (no training required)
python generate_samples.py
```

This creates sample versions:
- `sample_training_history.png` - What training curves look like
- `sample_mnist_predictions.png` - Example prediction results
- `sample_confidence_distribution.png` - Confidence score visualization
- `sample_inference_demo.png` - Inference output format
- `sample_cnn_architecture.png` - Network architecture diagram

### **Generate Real Visualizations**

To create the actual PNG files with real training data:

```bash
# 1. Set up environment
./setup.sh

# 2. Train model (generates training_history.png, mnist_predictions.png)
python mnist_cnn.py

# 3. Run inference demo (generates inference_demo.png)
python inference_demo.py

# 4. Test custom predictions (generates custom_prediction.png)
python custom_inference.py
```

### 📁 **File Structure After Training:**

```
CNN/
├── 📄 Source Files
│   ├── mnist_cnn.py
│   ├── inference_demo.py
│   └── ...
├── 🤖 Generated Models  
│   └── mnist_cnn_model.pth
├── 📊 Generated Plots
│   ├── training_history.png
│   ├── mnist_predictions.png
│   ├── inference_demo.png
│   └── custom_prediction.png
├── 📁 Downloaded Data
│   └── data/
│       └── MNIST/
└── 🔍 Sample Files (optional)
    ├── sample_training_history.png
    └── sample_*.png
```

### 👀 **Viewing the Results:**

After running the scripts, you can view the generated plots using:

```bash
# Linux/Mac with GUI
eog *.png              # Eye of Gnome
feh *.png               # feh image viewer
xdg-open training_history.png  # Default image viewer

# Command line preview
ls -la *.png            # List generated PNG files
file *.png              # Check file types
```

### **What the Plot Shows?**

#### **training_history.png**:
- **Left plot**: Training vs. Validation Loss over epochs
- **Right plot**: Training vs. Validation Accuracy over epochs
- **Purpose**: Monitor training progress and detect overfitting

#### **mnist_predictions.png**:
- **Grid of 8 images**: Sample MNIST digits with predictions
- **Green titles**: Correct predictions
- **Red titles**: Incorrect predictions (if any)
- **Purpose**: Visual verification of model performance

#### **inference_demo.png**:
- **Grid of 10 images**: Random test samples
- **Labels**: True digit, Predicted digit, Confidence score
- **Purpose**: Demonstrate inference pipeline results

#### **confidence_distribution.png**:
- **Bar chart**: Probability for each digit (0-9)
- **Red bar**: Predicted digit (highest probability)
- **Purpose**: Show model's confidence in predictions

### **Troubleshooting Visualization Issues:**

1. **No PNG files after training**:
   ```bash
   # Check if matplotlib is installed
   python -c "import matplotlib; print('Matplotlib available')"
   
   # Re-run with explicit display backend
   export MPLBACKEND=Agg
   python mnist_cnn.py
   ```

2. **Cannot view PNG files**:
   ```bash
   # Install image viewer
   sudo apt install eog feh  # Ubuntu/Debian
   
   # Or use web browser
   firefox training_history.png
   ```

3. **Blank or corrupted images**:
   ```bash
   # Check file sizes
   ls -lh *.png
   
   # Regenerate with different backend
   python -c "import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt; plt.plot([1,2,3]); plt.savefig('test.png'); print('Plot saved')"
   ```

## Convolutional Neural Network Layers

*Based on CS231n: Convolutional Networks for Visual Recognition*

Understanding the individual layers that make up a Convolutional Neural Network (CNN) is crucial for building effective models. Each layer type serves a specific purpose and transforms the input in a unique way.

### CNN Layer Types

A typical CNN consists of several layer types stacked together:

```
INPUT → [CONV → RELU → POOL?]×M → [FC → RELU]×K → FC → SOFTMAX
```

Where:
- **INPUT**: Raw image data (e.g., 28×28×1 for MNIST)
- **CONV**: Convolutional layers that detect features
- **RELU**: Activation functions that introduce non-linearity
- **POOL**: Pooling layers that downsample spatial dimensions
- **FC**: Fully connected layers for final classification
- **SOFTMAX**: Output layer producing class probabilities

### 1. Convolutional Layer (CONV)

The **convolutional layer** is the core building block that performs most of the computational work.

#### How Convolution Works?

1. **Filters/Kernels**: Small matrices (e.g., 3×3, 5×5) that slide across the input
2. **Feature Detection**: Each filter learns to detect specific features (edges, textures, patterns)
3. **Parameter Sharing**: Same filter weights are used across all spatial locations
4. **Local Connectivity**: Each neuron connects only to a local region of the input

#### Mathematical Operation:

For input volume of size `W₁ × H₁ × D₁` and filter size `F`:
- **Output size**: `W₂ = (W₁ - F + 2P)/S + 1`
- **Parameters per filter**: `F × F × D₁ + 1` (weights + bias)
- **Total parameters**: `(F × F × D₁ + 1) × K` (K = number of filters)

#### Key Hyperparameters:

| Parameter | Description | Common Values |
|-----------|-------------|---------------|
| **Filter Size (F)** | Spatial extent of filters | 3×3, 5×5 |
| **Stride (S)** | Step size when sliding filter | 1, 2 |
| **Padding (P)** | Zero-padding around input | 0, 1, 2 |
| **Number of Filters (K)** | Depth of output volume | 32, 64, 128, 256 |

#### Example in Our MNIST Model:

```python
# First convolutional layer
self.conv1 = nn.Conv2d(
    in_channels=1,    # Grayscale input
    out_channels=32,  # 32 filters
    kernel_size=3,    # 3x3 filters
    stride=1,         # Move 1 pixel at a time
    padding=1         # Preserve input size
)
```

**Input**: `[28×28×1]` → **Output**: `[28×28×32]`

### 2. Activation Function (ReLU) ⚡

**ReLU (Rectified Linear Unit)** introduces non-linearity to the network.

#### Function:
```
ReLU(x) = max(0, x)
```

#### Properties:
- **Non-linear**: Enables learning of complex patterns
- **Computationally efficient**: Simple thresholding operation
- **Sparse activation**: Many neurons output zero
- **Gradient flow**: Helps avoid vanishing gradient problem

#### Why ReLU is Essential:
Without non-linear activation functions, multiple linear layers would collapse into a single linear transformation, severely limiting the network's expressiveness.

### 3. Pooling Layer (POOL)

**Pooling layers** reduce spatial dimensions while preserving important features.

#### Max Pooling (Most Common):

- **Operation**: Takes maximum value in each pooling window
- **Common configuration**: 2×2 filter with stride 2
- **Effect**: Reduces spatial size by 50% in each dimension
- **Parameters**: Zero learnable parameters

#### Benefits:
1. **Translation Invariance**: Small shifts in input don't affect output
2. **Computational Efficiency**: Reduces number of parameters
3. **Overfitting Prevention**: Acts as regularization
4. **Feature Hierarchy**: Enables learning of larger-scale features

#### Mathematical Formulation:

For pooling with filter size `F` and stride `S`:
- **Output size**: `W₂ = (W₁ - F)/S + 1`
- **Common setting**: `F=2, S=2` → reduces size by half

#### Example:
```python
F.max_pool2d(x, kernel_size=2, stride=2)
```
**Input**: `[28×28×32]` → **Output**: `[14×14×32]`

### 4. Fully Connected Layer (FC)

**Fully connected layers** connect every neuron to all neurons in the previous layer.

#### Purpose:
- **Feature Combination**: Combines all learned features for final decision
- **Classification**: Maps features to class probabilities
- **High-level reasoning**: Learns complex relationships between features

#### Characteristics:
- **Dense connectivity**: Every input connected to every output
- **Most parameters**: Often contains majority of network parameters
- **Location in network**: Usually at the end before output layer

#### Parameter Count:
For input size `N` and output size `M`:
- **Parameters**: `N × M + M` (weights + biases)

#### Example in Our Model:
```python
self.fc1 = nn.Linear(64 * 7 * 7, 128)  # 64×7×7 → 128
self.fc2 = nn.Linear(128, 10)          # 128 → 10 classes
```

### 5. Dropout Layer

**Dropout** randomly sets some neurons to zero during training.

#### Purpose:
- **Regularization**: Prevents overfitting
- **Ensemble effect**: Simulates training multiple networks
- **Robustness**: Forces network to not rely on specific neurons

#### Types:
- **Standard Dropout**: Applied to fully connected layers
- **Spatial Dropout**: Applied to convolutional layers

```python
self.conv2_drop = nn.Dropout2d(p=0.25)  # 25% of feature maps
self.fc1_drop = nn.Dropout(p=0.5)       # 50% of neurons
```

### Layer Stacking Patterns

#### Common Architectures

1. **Basic Pattern**:
   ```
   INPUT → CONV → RELU → POOL → FC → SOFTMAX
   ```

2. **Deep Pattern** (Our MNIST model):
   ```
   INPUT → CONV → RELU → POOL → CONV → RELU → POOL → FC → RELU → FC
   ```

3. **VGG-style Pattern**:
   ```
   INPUT → [CONV → RELU]×2 → POOL → [CONV → RELU]×2 → POOL → FC
   ```

#### Design

1. **Small filters preferred**: 3×3 filters are most common
2. **Stack conv layers**: Multiple small filters > single large filter
3. **Increase depth gradually**: 32 → 64 → 128 → 256 filters
4. **Pool periodically**: Reduce spatial size progressively
5. **FC at the end**: Combine features for classification

### 🔢 Parameter and Memory Analysis

#### Our MNIST Model Breakdown:

| Layer | Input Size | Output Size | Parameters | Memory |
|-------|------------|-------------|------------|--------|
| Conv1 | 28×28×1 | 28×28×32 | 320 | 25K |
| Pool1 | 28×28×32 | 14×14×32 | 0 | 6.3K |
| Conv2 | 14×14×32 | 14×14×64 | 18,496 | 12.5K |
| Pool2 | 14×14×64 | 7×7×64 | 0 | 3.1K |
| FC1 | 3,136 | 128 | 401,536 | 512 |
| FC2 | 128 | 10 | 1,290 | 40 |

**Total Parameters**: ~421,642
**Total Memory**: ~47KB per image

### Insights from CS231n

#### Why CNNs Work for Images?

1. **Local Connectivity**: Nearby pixels are more correlated
2. **Parameter Sharing**: Same features useful across image locations
3. **Translation Invariance**: Objects can appear anywhere in image
4. **Hierarchical Features**: Simple → Complex feature progression

#### Common Hyperparameter Choices:

- **Filter sizes**: 3×3 (most common), 5×5, 7×7 (first layer only)
- **Stride**: 1 for CONV layers, 2 for POOL layers
- **Padding**: `P = (F-1)/2` to preserve input size
- **Pooling**: 2×2 max pooling with stride 2

#### Memory Considerations:

- **Early layers**: Most memory consumption (activations)
- **Late layers**: Most parameters (fully connected)
- **Bottleneck**: GPU memory limits (3-12GB typical)

### Tips

1. **Start simple**: Begin with proven architectures
2. **Use batch normalization**: Helps training stability
3. **Data augmentation**: Increase dataset size artificially
4. **Transfer learning**: Use pre-trained models when possible
5. **Monitor overfitting**: Watch training vs. validation accuracy

---

*For more detailed information, see the [CS231n Convolutional Networks lecture](https://cs231n.github.io/convolutional-networks/)*

```python
MNISTNet(
  (conv1): Conv2d(1, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
  (conv2): Conv2d(32, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
  (conv2_drop): Dropout2d(p=0.25, inplace=False)
  (fc1_drop): Dropout(p=0.5, inplace=False)
  (fc1): Linear(in_features=3136, out_features=128, bias=True)
  (fc2): Linear(in_features=128, out_features=10, bias=True)
)
```

### Layer-by-Layer

1. **Input**: 28×28×1 (grayscale image)
2. **Conv1**: 32 filters of size 3×3 → Output: 28×28×32
3. **MaxPool1**: 2×2 pooling → Output: 14×14×32
4. **Conv2**: 64 filters of size 3×3 → Output: 14×14×64
5. **MaxPool2**: 2×2 pooling → Output: 7×7×64
6. **Flatten**: → Output: 3136 features
7. **FC1**: 3136 → 128 neurons
8. **FC2**: 128 → 10 classes (digits 0-9)

### Parameters:
- **Total Parameters**: ~34,826
- **Trainable Parameters**: ~34,826

## Training Process

### Hyperparameters:
- **Batch Size**: 64 (training), 1000 (testing)
- **Learning Rate**: 0.01
- **Optimizer**: SGD with momentum (0.5)
- **Loss Function**: Negative Log Likelihood (NLL)
- **Epochs**: 10
- **Dropout**: 0.25 (conv), 0.5 (fc)

### Training Pipeline:

1. **Data Loading**:
   - Load MNIST dataset using `torchvision.datasets.MNIST`
   - Apply normalization with mean=0.1307, std=0.3081
   - Create DataLoaders for batching

2. **Forward Pass**:
   - Input → Conv layers → Pooling → FC layers → Output
   - Apply activation functions (ReLU) and dropout

3. **Loss Calculation**:
   - Compute NLL loss between predictions and true labels
   - NLL loss works well with log-softmax output

4. **Backward Pass**:
   - Calculate gradients using backpropagation
   - Update weights using SGD optimizer

5. **Evaluation**:
   - Test on validation set after each epoch
   - Calculate accuracy and loss metrics

## Results

### Expected Performance:
- **Training Accuracy**: ~99%
- **Test Accuracy**: ~98-99%
- **Training Time**: ~2-5 minutes (CPU), ~30 seconds (GPU)

### Sample Output:
```
Using device: cuda
Loading MNIST dataset...
Training samples: 60000
Test samples: 10000

Epoch 1/10
--------------------------------------------------
Train Epoch: 1 [0/60000 (0%)]    Loss: 2.300845
Train Epoch: 1 [6400/60000 (11%)]    Loss: 0.711782
...
Training Set: Average loss: 0.2845, Accuracy: 58552/60000 (97.59%)
Test Set: Average loss: 0.0731, Accuracy: 9778/10000 (97.78%)

...

Final Test Accuracy: 99.12%
```

### Visualization Files Generated:
- `training_history.png`: Loss and accuracy curves
- `mnist_predictions.png`: Sample predictions with labels
- `inference_demo.png`: Inference results with confidence scores

## GPU/CPU Support

### Automatic Device Detection:
```python
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'Using device: {device}')
```

### Performance Comparison:
- **CPU (Intel i7)**: ~3-5 minutes for 10 epochs
- **GPU (NVIDIA GTX 1080)**: ~30-60 seconds for 10 epochs
- **GPU (NVIDIA RTX 3080)**: ~15-30 seconds for 10 epochs

### Memory Usage:
- **Model Size**: ~140 KB
- **GPU Memory**: ~100-200 MB during training
- **RAM Usage**: ~500 MB for dataset

### Optimizing for Your Hardware:

#### For CPU:
- Reduce batch size if memory constrained
- Use fewer workers for DataLoader
- Consider mixed precision training

#### For GPU:
- Increase batch size for better GPU utilization
- Use multiple GPUs with DataParallel if available
- Enable CUDA optimizations

## Troubleshooting

### Common Issues:

1. **CUDA out of memory**:
   ```bash
   # Reduce batch size
   batch_size = 32  # instead of 64
   ```

2. **Slow training on CPU**:
   ```bash
   # Install Intel MKL-optimized PyTorch
   conda install pytorch torchvision torchaudio cpuonly -c pytorch
   ```

3. **Import errors**:
   ```bash
   # Reinstall dependencies
   pip install --upgrade torch torchvision matplotlib
   ```

4. **Dataset download issues**:
   ```bash
   # Clear cache and retry
   rm -rf ./data
   python mnist_cnn.py
   ```

## Experimentation: Hyperparameters & Data Augmentation

This section provides guidance on how to modify the project to experiment with different hyperparameters and implement data augmentation techniques to improve model performance.

### Hyperparameter Tuning

Hyperparameters are configuration settings that control the learning process. Here's how to modify key hyperparameters in the code:

#### **Experimentation: Learning Rate**

**Location**: `mnist_cnn.py`, line ~340 in `main()` function

```python
# Original
learning_rate = 0.01

# Experiments to try:
learning_rate = 0.001   # Lower LR - slower but more stable
learning_rate = 0.1     # Higher LR - faster but may overshoot
learning_rate = 0.005   # Middle ground
```

**With Learning Rate Scheduling**:
```python
import torch.optim.lr_scheduler as lr_scheduler

# In main() function, after defining optimizer:
optimizer = optim.SGD(model.parameters(), lr=learning_rate, momentum=momentum)

# Add learning rate scheduler
scheduler = lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)  # Reduce LR by half every 5 epochs
# Or exponential decay:
# scheduler = lr_scheduler.ExponentialLR(optimizer, gamma=0.95)

# In training loop, add after each epoch:
scheduler.step()
```

#### **Experimentation: Optimizer**

**Location**: `mnist_cnn.py`, line ~339

```python
# Original SGD
optimizer = optim.SGD(model.parameters(), lr=learning_rate, momentum=momentum)

# Try different optimizers:

# 1. Adam (adaptive learning rate)
optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-4)

# 2. AdamW (Adam with weight decay)
optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)

# 3. RMSprop
optimizer = optim.RMSprop(model.parameters(), lr=0.001, momentum=0.9)

# 4. SGD with different momentum
optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9, weight_decay=1e-4)
```

#### **Experimentation: Batch Size Tuning**

**Location**: `mnist_cnn.py`, line ~326-327

```python
# Original
batch_size = 64
test_batch_size = 1000

# Experiments:
batch_size = 32     # Smaller batch - more updates, noisier gradients
batch_size = 128    # Larger batch - smoother gradients, more memory
batch_size = 256    # Even larger - may need GPU with more memory
```

#### **Experimentation: Architecture**

**Location**: `mnist_cnn.py`, `MNISTNet` class definition

**1. Change Filter Numbers**:
```python
class MNISTNet(nn.Module):
    def __init__(self):
        super(MNISTNet, self).__init__()
        # Original: 32, 64 filters
        self.conv1 = nn.Conv2d(1, 64, kernel_size=3, stride=1, padding=1)    # More filters
        self.conv2 = nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1)  # More filters
        
        # Adjust FC layer accordingly
        self.fc1 = nn.Linear(128 * 7 * 7, 256)  # More neurons
        self.fc2 = nn.Linear(256, 10)
```

**2. Add More Convolutional Layers**:
```python
class DeepMNISTNet(nn.Module):
    def __init__(self):
        super(DeepMNISTNet, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 32, kernel_size=3, padding=1)     # Additional layer
        self.conv3 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv4 = nn.Conv2d(64, 64, kernel_size=3, padding=1)     # Additional layer
        
        self.conv_drop = nn.Dropout2d(p=0.25)
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.fc1_drop = nn.Dropout(p=0.5)
        self.fc2 = nn.Linear(128, 10)
        
    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.max_pool2d(x, 2)
        
        x = F.relu(self.conv3(x))
        x = F.relu(self.conv4(x))
        x = F.max_pool2d(x, 2)
        x = self.conv_drop(x)
        
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        x = self.fc1_drop(x)
        x = self.fc2(x)
        return F.log_softmax(x, dim=1)
```

#### **Experimentation: Dropout Rate Tuning**

**Location**: `mnist_cnn.py`, `MNISTNet` class

```python
# Original dropout rates
self.conv2_drop = nn.Dropout2d(p=0.25)  # 25% for conv layers
self.fc1_drop = nn.Dropout(p=0.5)       # 50% for FC layers

# Experiments:
self.conv2_drop = nn.Dropout2d(p=0.1)   # Less aggressive
self.fc1_drop = nn.Dropout(p=0.3)       # Less aggressive

# Or more aggressive:
self.conv2_drop = nn.Dropout2d(p=0.4)   # More dropout
self.fc1_drop = nn.Dropout(p=0.7)       # More dropout
```

### Data Augmentation

Data augmentation artificially increases dataset size by applying transformations to existing images.

#### **Method 1: Modify Transform Pipeline**

**Location**: `mnist_cnn.py`, `get_data_loaders()` function

```python
def get_data_loaders(batch_size=64, test_batch_size=1000):
    # Original transform (no augmentation)
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    # Enhanced transform with data augmentation
    train_transform = transforms.Compose([
        transforms.RandomRotation(10),                    # Rotate ±10 degrees
        transforms.RandomAffine(0, translate=(0.1, 0.1)), # Translate ±10%
        transforms.RandomAffine(0, scale=(0.9, 1.1)),     # Scale 90%-110%
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    # Keep test transform simple (no augmentation for evaluation)
    test_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    # Apply different transforms for train and test
    train_dataset = torchvision.datasets.MNIST(
        root='./data',
        train=True,
        download=True,
        transform=train_transform  # Use augmented transform
    )
    
    test_dataset = torchvision.datasets.MNIST(
        root='./data',
        train=False,
        download=True,
        transform=test_transform   # Use simple transform
    )
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=test_batch_size, shuffle=False)
    
    return train_loader, test_loader
```

#### **Method 2: Advanced Augmentation**

```python
# More aggressive augmentation
train_transform = transforms.Compose([
    transforms.RandomRotation(15),                           # More rotation
    transforms.RandomAffine(
        degrees=0,
        translate=(0.15, 0.15),                             # More translation
        scale=(0.85, 1.15),                                 # More scaling
        shear=5                                             # Add shear
    ),
    transforms.RandomPerspective(distortion_scale=0.2, p=0.5),  # Perspective distortion
    transforms.ColorJitter(brightness=0.2, contrast=0.2),       # For RGB images
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,)),
    transforms.RandomErasing(p=0.1, scale=(0.02, 0.33))        # Random erasing
])
```

#### **Method 3: Custom Augmentation with Noise**

```python
class GaussianNoise:
    def __init__(self, mean=0., std=0.1):
        self.std = std
        self.mean = mean
        
    def __call__(self, tensor):
        return tensor + torch.randn(tensor.size()) * self.std + self.mean

# Add to transform pipeline
train_transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,)),
    GaussianNoise(0., 0.05),  # Add slight noise
])
```

### Experiment Tracking

#### **Method 1: Simple Logging**

Add experiment tracking to your training loop:

```python
import csv
import datetime

def log_experiment(hyperparams, results, filename='experiments.csv'):
    """Log experiment hyperparameters and results"""
    fieldnames = ['timestamp', 'learning_rate', 'batch_size', 'optimizer', 
                  'final_accuracy', 'best_accuracy', 'training_time']
    
    # Create experiment record
    experiment = {
        'timestamp': datetime.datetime.now().isoformat(),
        'learning_rate': hyperparams['lr'],
        'batch_size': hyperparams['batch_size'],
        'optimizer': hyperparams['optimizer'],
        'final_accuracy': results['final_acc'],
        'best_accuracy': results['best_acc'],
        'training_time': results['time']
    }
    
    # Write to CSV
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(experiment)

# Use in main():
hyperparams = {'lr': learning_rate, 'batch_size': batch_size, 'optimizer': 'SGD'}
results = {'final_acc': test_accuracies[-1], 'best_acc': max(test_accuracies), 'time': training_time}
log_experiment(hyperparams, results)
```

#### **Method 2: Using Weights & Biases (wandb)**

```python
# Install: pip install wandb

import wandb

# Initialize wandb in main():
wandb.init(project="mnist-cnn-experiments", config={
    "learning_rate": learning_rate,
    "batch_size": batch_size,
    "epochs": epochs,
    "architecture": "CNN",
    "optimizer": "SGD"
})

# Log metrics during training:
for epoch in range(1, epochs + 1):
    train_loss, train_acc = train_epoch(model, device, train_loader, optimizer, epoch)
    test_loss, test_acc = test_epoch(model, device, test_loader)
    
    # Log to wandb
    wandb.log({
        "epoch": epoch,
        "train_loss": train_loss,
        "train_accuracy": train_acc,
        "test_loss": test_loss,
        "test_accuracy": test_acc
    })

wandb.finish()
```

### Systematic Experimentation

#### **1. Create Experiment Scripts**

Create separate files for different experiments:

**`experiment_optimizers.py`**:
```python
from mnist_cnn import *

optimizers_to_test = [
    {'name': 'SGD', 'params': {'lr': 0.01, 'momentum': 0.9}},
    {'name': 'Adam', 'params': {'lr': 0.001}},
    {'name': 'AdamW', 'params': {'lr': 0.001, 'weight_decay': 0.01}},
    {'name': 'RMSprop', 'params': {'lr': 0.001}}
]

for opt_config in optimizers_to_test:
    print(f"Testing {opt_config['name']}...")
    # Run training with this optimizer
    # Save results
```

**`experiment_augmentation.py`**:
```python
from mnist_cnn import *

augmentation_configs = [
    {'name': 'none', 'transform': basic_transform},
    {'name': 'rotation', 'transform': rotation_transform},
    {'name': 'full_aug', 'transform': full_augmentation_transform}
]

for aug_config in augmentation_configs:
    print(f"Testing augmentation: {aug_config['name']}...")
    # Run training with this augmentation
    # Save results
```

#### **2. Grid Search Implementation**

```python
def grid_search():
    learning_rates = [0.001, 0.01, 0.1]
    batch_sizes = [32, 64, 128]
    dropout_rates = [0.1, 0.25, 0.5]
    
    best_accuracy = 0
    best_params = {}
    
    for lr in learning_rates:
        for batch_size in batch_sizes:
            for dropout in dropout_rates:
                print(f"Testing: LR={lr}, Batch={batch_size}, Dropout={dropout}")
                
                # Create model with these parameters
                accuracy = train_and_evaluate(lr, batch_size, dropout)
                
                if accuracy > best_accuracy:
                    best_accuracy = accuracy
                    best_params = {'lr': lr, 'batch_size': batch_size, 'dropout': dropout}
                
                print(f"Accuracy: {accuracy:.2f}%")
    
    print(f"Best parameters: {best_params}")
    print(f"Best accuracy: {best_accuracy:.2f}%")
```

### Tips for Experimentation

1. **Start Small**: Test one hyperparameter at a time
2. **Use Validation Set**: Split training data to avoid overfitting to test set
3. **Save Checkpoints**: Save models during training to resume if interrupted
4. **Document Everything**: Keep detailed notes of what you tried
5. **Visualize Results**: Plot training curves to understand behavior
6. **Cross-Validation**: Use k-fold CV for robust results

### Expected Improvements

With proper hyperparameter tuning and data augmentation, you can expect:

- **Baseline Model**: 98-99% accuracy
- **With Augmentation**: 99.2-99.4% accuracy
- **With Tuned Hyperparameters**: 99.3-99.5% accuracy
- **With Both**: 99.4-99.6% accuracy

### 🔧 Experiment Template

Here's a template for running quick experiments:

```python
def run_experiment(config):
    """Run a single experiment with given configuration"""
    # Set hyperparameters
    model = MNISTNet()
    if config['optimizer'] == 'SGD':
        optimizer = optim.SGD(model.parameters(), lr=config['lr'])
    elif config['optimizer'] == 'Adam':
        optimizer = optim.Adam(model.parameters(), lr=config['lr'])
    
    # Train model
    accuracies = []
    for epoch in range(config['epochs']):
        # Training code here
        pass
    
    return max(accuracies)

# Run experiments
experiments = [
    {'name': 'baseline', 'lr': 0.01, 'optimizer': 'SGD', 'epochs': 5},
    {'name': 'adam', 'lr': 0.001, 'optimizer': 'Adam', 'epochs': 5},
    {'name': 'high_lr', 'lr': 0.1, 'optimizer': 'SGD', 'epochs': 5}
]

for exp in experiments:
    accuracy = run_experiment(exp)
    print(f"{exp['name']}: {accuracy:.2f}%")
```

## Next Steps

### Experimentation
1. **Data Augmentation**: Rotation, scaling, translation
2. **Advanced Architectures**: ResNet, DenseNet, EfficientNet
3. **Hyperparameter Tuning**: Learning rate scheduling, different optimizers
4. **Regularization**: Batch normalization, different dropout rates
5. **Transfer Learning**: Pre-trained models fine-tuning

### Other Datasets to Explore:
- CIFAR-10/CIFAR-100 (color images, more classes)
- Fashion-MNIST (clothing items)
- SVHN (Street View House Numbers)
- Custom datasets

## References

### Official Documentation:
- [PyTorch Documentation](https://pytorch.org/docs/stable/index.html)
- [PyTorch Tutorials](https://pytorch.org/tutorials/)
- [CIFAR-10 Tutorial](https://docs.pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html)

### MNIST Dataset:
- [MNIST Database](https://huggingface.co/datasets/ylecun/mnist/)
- [PyTorch MNIST Examples](https://github.com/pytorch/examples/tree/main/mnist)

### Deep Learning Resources:
- [Deep Learning Book](http://www.deeplearningbook.org/)
- [CS231n: Convolutional Neural Networks](http://cs231n.stanford.edu/)
- [PyTorch Examples Repository](https://github.com/pytorch/examples)

### CNN Architecture Papers:
- LeNet-5: LeCun et al., "Gradient-based learning applied to document recognition"
- AlexNet: Krizhevsky et al., "ImageNet Classification with Deep Convolutional Neural Networks"
- ResNet: He et al., "Deep Residual Learning for Image Recognition"

---
