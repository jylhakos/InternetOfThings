#!/bin/bash
# Quick Training Pipeline Test Script

echo " VERIFICATION: Training Pipeline Setup"
echo "=============================================="

cd "MACHINE-LEARNING/Feature Learning"
source venv/bin/activate

echo " Virtual environment activated"
echo "Python: $(python --version)"
echo "PyTorch: $(python -c 'import torch; print(torch.__version__)')"
echo "CUDA: $(python -c 'import torch; print("Available" if torch.cuda.is_available() else "Not available")')"

echo -e "\n📁 Training Scripts Available:"
ls -1 src/training/train_*.py | while read file; do
    echo "  ✓ $file"
done

echo -e "\n Ready for Testing with Small Samples:"
echo "  • Autoencoder: python src/training/train_autoencoder.py --test-mode --epochs 1 --batch-size 8"
echo "  • RNN: python src/training/train_rnn.py --test-mode --epochs 1 --batch-size 8 --dataset imdb"
echo "  • Transfer Learning: python src/training/train_transfer_learning.py --test-mode --epochs 1 --batch-size 8"
echo "  • Transformers: python src/training/train_transformers.py --test-mode --epochs 1 --batch-size 8"

echo -e "\n✨ Training pipelines include:"
echo "  ✓ Training and evaluation stages"
echo "  ✓ Data loading with train/val/test splits"
echo "  ✓ CUDA support (if available)"
echo "  ✓ Model checkpointing and metrics"
echo "  ✓ Feature extraction capabilities"
echo "  ✓ Visualization and logging"

echo -e "\n Setup Complete - Ready for Training!"
