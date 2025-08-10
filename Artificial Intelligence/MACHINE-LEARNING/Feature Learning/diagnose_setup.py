#!/usr/bin/env python3
"""
🔧 Feature Learning Environment Diagnostics

This script performs comprehensive diagnostics of the PyTorch and CUDA setup
to help troubleshoot common issues with the feature engineering scripts.
"""

import torch
import torchvision
import sys
import os
import platform
import subprocess

def print_header():
    """Print diagnostic header"""
    print("🔧 FEATURE LEARNING ENVIRONMENT DIAGNOSTICS")
    print("=" * 60)

def check_system_info():
    """Check system information"""
    print(" SYSTEM INFORMATION")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Python: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # Check memory
    try:
        import psutil
        print(f"Available RAM: {psutil.virtual_memory().available / 1024**3:.1f} GB")
        print(f"Total RAM: {psutil.virtual_memory().total / 1024**3:.1f} GB")
        print(f"CPU cores: {psutil.cpu_count()} ({psutil.cpu_count(logical=False)} physical)")
    except ImportError:
        print("⚠️  psutil not available - install with: pip install psutil")

def check_pytorch_info():
    """Check PyTorch installation"""
    print("\n PYTORCH INFORMATION")
    print(f"PyTorch version: {torch.__version__}")
    print(f"TorchVision version: {torchvision.__version__}")
    
    # Check if PyTorch was compiled with CUDA support
    print(f"PyTorch compiled with CUDA: {torch.version.cuda is not None}")
    if torch.version.cuda:
        print(f"PyTorch CUDA version: {torch.version.cuda}")
    
    # Check backends
    print(f"cuDNN available: {torch.backends.cudnn.enabled}")
    if torch.backends.cudnn.enabled:
        print(f"cuDNN version: {torch.backends.cudnn.version()}")

def check_cuda_info():
    """Check CUDA availability and GPU information"""
    print("\n CUDA INFORMATION")
    print(f"CUDA available in PyTorch: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"CUDA runtime version: {torch.version.cuda}")
        print(f"GPU count: {torch.cuda.device_count()}")
        print(f"Current GPU: {torch.cuda.current_device()}")
        
        # GPU details
        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            print(f"\nGPU {i}: {props.name}")
            print(f"  Compute capability: {props.major}.{props.minor}")
            print(f"  Total memory: {props.total_memory / 1024**3:.1f} GB")
            print(f"  Memory allocated: {torch.cuda.memory_allocated(i) / 1024**3:.3f} GB")
            print(f"  Memory cached: {torch.cuda.memory_reserved(i) / 1024**3:.3f} GB")
    else:
        print("❌ CUDA not available - running in CPU-only mode")
        print("This means either:")
        print("  1. No NVIDIA GPU is present")
        print("  2. NVIDIA drivers are not installed")
        print("  3. PyTorch was installed without CUDA support")

def check_system_cuda():
    """Check system-level CUDA installation"""
    print("\n SYSTEM CUDA CHECK")
    
    # Check nvidia-smi
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(" nvidia-smi available")
            # Extract driver version
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Driver Version:' in line:
                    print(f"NVIDIA Driver Version: {line.split('Driver Version:')[1].split()[0]}")
                    break
        else:
            print("❌ nvidia-smi failed - NVIDIA drivers may not be installed")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ nvidia-smi not found - NVIDIA drivers not installed")
    
    # Check nvcc
    try:
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(" nvcc (CUDA compiler) available")
            # Extract CUDA version
            for line in result.stdout.split('\n'):
                if 'release' in line:
                    version = line.split('release')[1].split(',')[0].strip()
                    print(f"CUDA compiler version: {version}")
                    break
        else:
            print("❌ nvcc not available - CUDA toolkit may not be installed")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ nvcc not found - CUDA toolkit not installed")

def test_tensor_operations():
    """Test basic tensor operations"""
    print("\n TESTING TENSOR OPERATIONS")
    
    try:
        # CPU test
        print("Testing CPU operations...")
        x = torch.randn(1000, 1000)
        y = torch.mm(x, x)
        print(" CPU tensor operations: OK")
        
        # GPU test (if available)
        if torch.cuda.is_available():
            print("Testing GPU operations...")
            x_gpu = x.cuda()
            y_gpu = torch.mm(x_gpu, x_gpu)
            torch.cuda.synchronize()  # Wait for completion
            print(" GPU tensor operations: OK")
            
            # Memory test
            print("Testing GPU memory management...")
            large_tensor = torch.randn(5000, 5000, device='cuda')
            del large_tensor
            torch.cuda.empty_cache()
            print(" GPU memory management: OK")
        else:
            print(" GPU operations: Skipped (no CUDA)")
            
    except Exception as e:
        print(f"❌ Tensor operations failed: {e}")
        return False
    
    return True

def test_imports():
    """Test importing feature engineering modules"""
    print("\n📦 TESTING FEATURE ENGINEERING IMPORTS")
    
    # Test standard imports
    required_modules = [
        'numpy', 'matplotlib', 'sklearn', 'seaborn', 'PIL'
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - install with: pip install {module}")
    
    # Test optional imports
    optional_modules = [
        ('datasets', 'Hugging Face datasets'),
        ('transformers', 'Hugging Face transformers'),
        ('psutil', 'System monitoring')
    ]
    
    print("\nOptional modules:")
    for module, description in optional_modules:
        try:
            __import__(module)
            print(f"✅ {module} ({description})")
        except ImportError:
            print(f"⚠️  {module} ({description}) - optional")

def provide_recommendations():
    """Provide recommendations based on the diagnostics"""
    print("\n RECOMMENDATIONS")
    print("-" * 30)
    
    if not torch.cuda.is_available():
        print("⚠️  CUDA not available. Recommendations:")
        print("  1. Check if you have an NVIDIA GPU: lspci | grep -i nvidia")
        print("  2. Install NVIDIA drivers: sudo ubuntu-drivers autoinstall")
        print("  3. Install CUDA toolkit from NVIDIA website")
        print("  4. Reinstall PyTorch with CUDA support:")
        print("     pip uninstall torch torchvision torchaudio")
        print("     pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
        print("  5. Or use CPU-only mode (slower but functional)")
    else:
        print(" CUDA is available! Recommendations:")
        print("  1. Use GPU acceleration in scripts with --device cuda")
        print("  2. Monitor GPU memory usage to avoid OOM errors")
        print("  3. Use appropriate batch sizes for your GPU memory")
    
    # Memory recommendations
    try:
        import psutil
        available_gb = psutil.virtual_memory().available / 1024**3
        if available_gb < 8:
            print("⚠️  Low system memory detected. Recommendations:")
            print("  1. Use smaller batch sizes: --batch-size 16 or --batch-size 32")
            print("  2. Reduce model complexity if possible")
            print("  3. Consider using gradient accumulation")
    except ImportError:
        pass
    
    print("\n To run feature engineering scripts:")
    print("  python src/feature_engineering/cnn_feature_engineering.py --dataset MNIST --epochs 5")
    print("  python demo_comprehensive_feature_engineering.py")

def main():
    """Main diagnostic function"""
    print_header()
    check_system_info()
    check_pytorch_info()
    check_cuda_info()
    check_system_cuda()
    success = test_tensor_operations()
    test_imports()
    provide_recommendations()
    
    print("\n" + "=" * 60)
    if success and torch.cuda.is_available():
        print(" Diagnostics complete! Your environment is ready for GPU-accelerated feature learning.")
    elif success:
        print(" Diagnostics complete! Your environment is ready for CPU-based feature learning.")
    else:
        print("⚠️  Diagnostics found issues. Please review the recommendations above.")
    print("=" * 60)

if __name__ == "__main__":
    main()
