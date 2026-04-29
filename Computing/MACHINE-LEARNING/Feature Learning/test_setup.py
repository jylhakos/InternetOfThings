#!/usr/bin/env python3
"""
Quick test script to verify the Feature Learning project setup.
"""

import sys
import os

def test_basic_imports():
    """Test if basic packages can be imported."""
    print("🧪 Testing basic imports...")
    
    try:
        import torch
        print(f"✅ PyTorch: {torch.__version__}")
    except ImportError as e:
        print(f"❌ PyTorch import failed: {e}")
        return False
    
    try:
        import numpy as np
        print(f"✅ NumPy: {np.__version__}")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        from datasets import load_dataset
        print("✅ Hugging Face Datasets")
    except ImportError as e:
        print(f"❌ Datasets import failed: {e}")
        return False
    
    return True

def test_cuda_availability():
    """Test CUDA availability."""
    print("\n🔧 Testing CUDA availability...")
    
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✅ CUDA available: {torch.cuda.get_device_name()}")
            print(f"   CUDA version: {torch.version.cuda}")
        else:
            print("⚠️ CUDA not available, using CPU")
    except Exception as e:
        print(f"❌ CUDA test failed: {e}")

def test_project_structure():
    """Test project structure."""
    print("\n📁 Testing project structure...")
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    required_dirs = [
        'src',
        'src/data',
        'src/models',
        'src/training',
        'src/utils',
        'src/evaluation',
        'scripts',
        'notebooks'
    ]
    
    for dir_name in required_dirs:
        dir_path = os.path.join(base_path, dir_name)
        if os.path.exists(dir_path):
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/ missing")

def test_model_creation():
    """Test simple model creation."""
    print("\n🧠 Testing model creation...")
    
    try:
        import torch
        import torch.nn as nn
        
        # Create a simple CNN
        model = nn.Sequential(
            nn.Conv2d(1, 32, 3),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(32, 10)
        )
        
        # Test forward pass
        x = torch.randn(1, 1, 28, 28)
        output = model(x)
        
        print(f"✅ Model created successfully")
        print(f"   Input shape: {x.shape}")
        print(f"   Output shape: {output.shape}")
        
        return True
    except Exception as e:
        print(f"❌ Model creation failed: {e}")
        return False

def test_dataset_loading():
    """Test dataset loading capability."""
    print("\n📊 Testing dataset loading...")
    
    try:
        from datasets import load_dataset
        
        # Test loading a small sample
        print("   Loading MNIST sample...")
        dataset = load_dataset("ylecun/mnist", split="train[:100]")
        
        print(f"✅ Dataset loaded successfully")
        print(f"   Sample size: {len(dataset)}")
        print(f"   Features: {list(dataset.features.keys())}")
        
        return True
    except Exception as e:
        print(f"❌ Dataset loading failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Feature Learning Project Setup Test")
    print("=" * 50)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("CUDA Availability", test_cuda_availability),
        ("Project Structure", test_project_structure),
        ("Model Creation", test_model_creation),
        ("Dataset Loading", test_dataset_loading),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 30)
        
        try:
            result = test_func()
            results.append((test_name, result if result is not None else True))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📋 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print("-" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Setup is ready.")
        return 0
    else:
        print("⚠️ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
