# Quick Start - MNIST CNN with PyTorch

## Setup (shell)

```bash
# Make setup script executable and run it
chmod +x setup.sh && ./setup.sh
```

## Manual Setup (Alternative)

```bash
# 1. Create and activate virtual environment
python3 -m venv mnist_env
source mnist_env/bin/activate

# 2. Install dependencies
pip install torch torchvision matplotlib numpy Pillow

# 3. Verify installation
python -c "import torch; print('PyTorch:', torch.__version__)"
```

## Running the Project

### 1. Train the Model
```bash
python mnist_cnn.py
```
**Expected time**: 2-5 minutes (CPU), 30 seconds (GPU)
**Output**: Model saved as `mnist_cnn_model.pth`

### 2. Run Inference Demo
```bash
python inference_demo.py
```
**Output**: Prediction visualizations and accuracy metrics

### 3. Test Custom Images
```bash
python custom_inference.py
```
**Output**: Sample digit creation and prediction demo

### 4. Interactive Notebook
```bash
# Install Jupyter (if not already installed)
pip install jupyter

# Launch notebook
jupyter notebook mnist_cnn_notebook.ipynb
```

## Files

| File | Purpose |
|------|---------|
| `mnist_cnn.py` | Main training script with full CNN implementation |
| `inference_demo.py` | Demonstration of model inference on test data |
| `custom_inference.py` | Example of using the model on custom images |
| `mnist_cnn_notebook.ipynb` | Interactive Jupyter notebook version |
| `requirements.txt` | Python package dependencies |
| `setup.sh` | Automated setup script |

## Expected Results

- **Test Accuracy**: 98-99%
- **Model Size**: ~140 KB
- **Parameters**: ~34,826
- **Training Speed**: 2-5 min (CPU), 30s (GPU)

## Troubleshooting

### Issues:

1. **CUDA out of memory**:
   ```python
   # Reduce batch size in the code
   batch_size = 32  # instead of 64
   ```

2. **Module not found errors**:
   ```bash
   # Make sure virtual environment is activated
   source mnist_env/bin/activate
   pip install -r requirements.txt
   ```

3. **Slow training**:
   - GPU: Check if CUDA is installed and detected
   - CPU: Consider using Intel MKL optimized PyTorch

### GPU Setup (Optional):

Check GPU availability:
```bash
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

Install GPU version of PyTorch (if you have NVIDIA GPU):
```bash
# For CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Next Steps

1. **Experiment with hyperparameters** (learning rate, batch size, architecture)
2. **Try data augmentation** (rotation, scaling, noise)
3. **Test on other datasets** (CIFAR-10, Fashion-MNIST)
4. **Implement advanced architectures** (ResNet, DenseNet)
5. **Deploy the model** (Flask web app, mobile app)

## References

- **PyTorch Documentation**: https://pytorch.org/docs/
- **MNIST Dataset**: http://yann.lecun.com/exdb/mnist/
- **CNN Tutorial**: https://docs.pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html

---
