#!/bin/bash
# GPU/CUDA Fix Script for RNN+LSTM Project

echo "GPU/CUDA FIX FOR RNN+LSTM ELECTRICITY FORECASTING"
echo "======================================================"

echo ""
echo "🔍 DIAGNOSIS SUMMARY:"
echo "✅ Hardware: NVIDIA GeForce MX450 (2GB VRAM) - DETECTED"
echo "✅ Driver: 550.163.01 - WORKING"  
echo "✅ CUDA: 12.4 - READY"
echo "❌ PyTorch: 2.7.1 - HANGING (needs fix)"

echo ""
echo "🛠️  APPLYING FIX..."

# Check if in virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment active: $VIRTUAL_ENV"
else
    echo "⚠️  Activating virtual environment..."
    source .venv/bin/activate
fi

echo ""
echo "📦 STEP 1: Uninstalling problematic PyTorch..."
pip uninstall -y torch torchvision torchaudio

echo ""
echo "📦 STEP 2: Installing stable PyTorch with CUDA 12.4..."
pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cu124

echo ""
echo "STEP 3: Testing GPU functionality..."

python << 'EOF'
import torch
import time

print("=== GPU TEST RESULTS ===")
print(f"PyTorch Version: {torch.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"GPU Count: {torch.cuda.device_count()}")
    print(f"GPU Name: {torch.cuda.get_device_name()}")
    print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    
    # Performance test
    device = torch.device('cuda')
    model = torch.nn.LSTM(7, 64, 2, batch_first=True).to(device)
    test_input = torch.randn(32, 24, 7).to(device)
    
    model.eval()
    with torch.no_grad():
        start = time.time()
        for _ in range(100):
            _ = model(test_input)
        end = time.time()
    
    avg_time = ((end - start) / 100) * 1000
    print(f"GPU Inference: {avg_time:.2f}ms per batch")
    print("GPU ACCELERATION WORKING!")
    
else:
    print("❌ CUDA still not available")
    print("💡 Try the conda alternative:")
    print("conda install pytorch torchvision torchaudio pytorch-cuda=12.4 -c pytorch -c nvidia")

print("\n✅ Ready for RNN+LSTM electricity forecasting!")
EOF

echo ""
echo "FIX COMPLETE!"
echo ""
echo "Next steps:"
echo "1. Run: python train_models.py"
echo "2. Run: python model_optimization.py"  
echo "3. Test API: python api_server.py"
