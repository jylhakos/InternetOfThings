#!/usr/bin/env python3
"""
Test Script for MNIST CNN Project
==================================

This script runs basic tests to verify that the project is set up correctly
and all components are working.
"""

import sys
import subprocess
import importlib.util

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7+ required. Current version:", sys.version)
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_package(package_name, import_name=None):
    """Check if a package is installed and importable."""
    if import_name is None:
        import_name = package_name
    
    spec = importlib.util.find_spec(import_name)
    if spec is None:
        print(f"❌ {package_name} not found")
        return False
    
    try:
        module = importlib.import_module(import_name)
        if hasattr(module, '__version__'):
            version = module.__version__
        else:
            version = "unknown version"
        print(f"✅ {package_name}: {version}")
        return True
    except ImportError as e:
        print(f"❌ {package_name}: Import error - {e}")
        return False

def check_gpu():
    """Check GPU availability."""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            print(f"🎮 GPU available: {gpu_name} ({gpu_memory:.1f} GB)")
            return True
        else:
            print("💻 No GPU available, will use CPU")
            return False
    except ImportError:
        print("❌ Cannot check GPU - PyTorch not installed")
        return False

def test_model_creation():
    """Test if the CNN model can be created."""
    try:
        from mnist_cnn import MNISTNet
        model = MNISTNet()
        total_params = sum(p.numel() for p in model.parameters())
        print(f"✅ Model creation successful ({total_params:,} parameters)")
        return True
    except ImportError:
        print("❌ Cannot import MNISTNet from mnist_cnn.py")
        return False
    except Exception as e:
        print(f"❌ Model creation failed: {e}")
        return False

def test_data_loading():
    """Test if MNIST data can be loaded."""
    try:
        import torch
        import torchvision
        import torchvision.transforms as transforms
        
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ])
        
        # Try to load a small sample
        dataset = torchvision.datasets.MNIST(
            root='./data', 
            train=True,
            download=True, 
            transform=transform
        )
        
        print(f"✅ MNIST dataset loaded ({len(dataset)} samples)")
        return True
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        return False

def run_quick_training_test():
    """Run a very quick training test (1 epoch, small batch)."""
    try:
        import torch
        import torch.nn.functional as F
        import torch.optim as optim
        from torch.utils.data import DataLoader
        from mnist_cnn import MNISTNet, get_data_loaders
        
        print("🧪 Running quick training test (this may take a minute)...")
        
        # Get a small subset for testing
        train_loader, _ = get_data_loaders(batch_size=32)
        
        # Create model and optimizer
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model = MNISTNet().to(device)
        optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.5)
        
        # Train for 1 batch only
        model.train()
        for batch_idx, (data, target) in enumerate(train_loader):
            if batch_idx >= 1:  # Only test 1 batch
                break
                
            data, target = data.to(device), target.to(device)
            optimizer.zero_grad()
            output = model(data)
            loss = F.nll_loss(output, target)
            loss.backward()
            optimizer.step()
            
            print(f"✅ Training test successful (loss: {loss.item():.4f})")
            return True
            
    except Exception as e:
        print(f"❌ Training test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🔍 MNIST CNN Project Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 7
    
    # Test 1: Python version
    if check_python_version():
        tests_passed += 1
    
    # Test 2-5: Required packages
    required_packages = [
        ('torch', 'torch'),
        ('torchvision', 'torchvision'),
        ('matplotlib', 'matplotlib'),
        ('numpy', 'numpy')
    ]
    
    for pkg_name, import_name in required_packages:
        if check_package(pkg_name, import_name):
            tests_passed += 1
    
    # Test 6: Model creation
    if test_model_creation():
        tests_passed += 1
    
    # Test 7: Data loading
    if test_data_loading():
        tests_passed += 1
    
    # Bonus: GPU check (doesn't count towards pass/fail)
    check_gpu()
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The project is ready to use.")
        print("\nNext steps:")
        print("  python mnist_cnn.py      # Train the model")
        print("  python inference_demo.py # Run inference demo")
        
        # Optional: Run quick training test
        if input("\n🤔 Run quick training test? (y/n): ").lower() == 'y':
            run_quick_training_test()
            
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
        print("\nTroubleshooting:")
        print("  pip install -r requirements.txt  # Install dependencies")
        print("  ./setup.sh                       # Run setup script")
    
    return tests_passed == total_tests

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
