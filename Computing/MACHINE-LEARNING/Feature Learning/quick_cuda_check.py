#!/usr/bin/env python3
"""
Quick CUDA Check Script

This is a simple script to quickly check CUDA availability and provide
basic troubleshooting guidance for the Feature Learning project.
"""

import torch

def main():
    print("🔍 Quick CUDA Check for Feature Learning")
    print("=" * 45)
    
    # Basic PyTorch info
    print(f"PyTorch version: {torch.__version__}")
    
    # CUDA availability
    cuda_available = torch.cuda.is_available()
    print(f"CUDA available: {cuda_available}")
    
    if cuda_available:
        print(f"CUDA version: {torch.version.cuda}")
        print(f"GPU count: {torch.cuda.device_count()}")
        print(f"Current GPU: {torch.cuda.get_device_name(0)}")
        print(" GPU acceleration ready!")
        
        # Quick memory test
        try:
            test_tensor = torch.randn(1000, 1000).cuda()
            result = torch.mm(test_tensor, test_tensor)
            print(" GPU operations working")
            
            # Memory info
            memory_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"GPU Memory: {memory_gb:.1f} GB")
            
        except RuntimeError as e:
            print(f"⚠️  GPU test failed: {e}")
    else:
        print("❌ CUDA not available")
        print("\nTo enable GPU acceleration:")
        print("1. Check if you have NVIDIA GPU:")
        print("   nvidia-smi")
        print("2. Install PyTorch with CUDA:")
        print("   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118")
        print("3. Run full diagnostics:")
        print("   python diagnose_setup.py")
        
    print("\nRun Feature Learning scripts.")
    print("   python src/feature_engineering/cnn_feature_engineering.py --dataset MNIST")

if __name__ == "__main__":
    main()
