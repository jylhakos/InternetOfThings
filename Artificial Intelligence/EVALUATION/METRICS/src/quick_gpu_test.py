#!/usr/bin/env python3
"""Quick GPU/CUDA test for RNN+LSTM project"""

import torch
import subprocess
import time

print("=== GPU/CUDA STATUS FOR YOUR RNN+LSTM PROJECT ===")
print()

# 1. Hardware Detection
print("🖥️ HARDWARE:")
try:
    nvidia_info = subprocess.run(['nvidia-smi', '--query-gpu=name,driver_version,memory.total', '--format=csv,noheader'], 
                               capture_output=True, text=True)
    if nvidia_info.returncode == 0:
        print(f"✅ GPU: {nvidia_info.stdout.strip()}")
    else:
        print("❌ No NVIDIA GPU detected or driver issue")
except:
    print("❌ nvidia-smi not available")

# 2. PyTorch Analysis  
print("\n🔧 PYTORCH:")
print(f"✅ Version: {torch.__version__}")
print(f"   CUDA Support: {torch.version.cuda}")
print(f"   CUDA Available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"   GPU Count: {torch.cuda.device_count()}")
    print(f"   Device Name: {torch.cuda.get_device_name()}")
else:
    print("   Status: CPU-only mode")

# 3. Performance Test
print("\n⚡ PERFORMANCE TEST:")
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Testing on: {device}")

# LSTM model for electricity forecasting
batch_size = 32
sequence_length = 24  # 24-day lookback
input_features = 7    # electricity + weather features

model = torch.nn.LSTM(input_features, 64, 2, batch_first=True).to(device)
test_input = torch.randn(batch_size, sequence_length, input_features).to(device)

model.eval()
with torch.no_grad():
    # Warmup
    for _ in range(10):
        _ = model(test_input)
    
    # Timing
    start = time.time()
    for _ in range(100):
        output, _ = model(test_input)
    end = time.time()

avg_time_ms = ((end - start) / 100) * 1000
throughput = (batch_size * 100) / (end - start)

print(f"✅ Results:")
print(f"   Inference time: {avg_time_ms:.2f}ms per batch")
print(f"   Throughput: {throughput:.1f} predictions/sec")

# Performance rating
if avg_time_ms < 5:
    print("🚀 EXCELLENT - Perfect for real-time forecasting!")
elif avg_time_ms < 20:
    print("⚡ GOOD - Great for production use")
else:
    print("✅ ADEQUATE - Good for development")

# 4. Diagnosis and Solutions
print("\n🔍 DIAGNOSIS & SOLUTIONS:")

if not torch.cuda.is_available():
    print("❌ ISSUE: CUDA not available")
    print("💡 SOLUTIONS:")
    print("   1. Reinstall PyTorch with compatible CUDA:")
    print("      pip uninstall torch torchvision torchaudio")
    print("      pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124")
    print()
    print("   2. Or use conda for easier CUDA management:")
    print("      conda install pytorch torchvision torchaudio pytorch-cuda=12.4 -c pytorch -c nvidia")
    print()
    print("   3. Verify CUDA toolkit installation:")
    print("      sudo apt install nvidia-cuda-toolkit")
else:
    print("✅ CUDA working perfectly!")

print("\n🎯 PROJECT RECOMMENDATION:")
if avg_time_ms < 10:
    print("✅ Current performance is EXCELLENT for electricity forecasting")
    print("✅ GPU setup optional - CPU performance already exceeds requirements")
else:
    print("⚠️  Consider GPU setup for better training performance")

print("\n🚀 Ready to train your RNN+LSTM electricity forecasting models!")
