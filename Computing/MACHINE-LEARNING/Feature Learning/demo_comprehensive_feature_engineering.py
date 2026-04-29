#!/usr/bin/env python3
"""
Feature Engineering (Demo)

This script demonstrates and validates feature engineering.
1. CNN Feature Engineering
2. RNN Feature Engineering
3. Transformer Feature Engineering
4. Autoencoder Feature Engineering
5. Transfer Learning Feature Engineering
"""

import sys
import os
import subprocess
import time
import numpy as np
import matplotlib.pyplot as plt
import argparse

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def run_script(script_path, args=None, timeout=300):
    """
    Run a Python script with optional arguments and timeout
    """
    cmd = ['python', script_path]
    if args:
        cmd.extend(args)
    
    print(f"Running: {' '.join(cmd)}")
    print("-" * 80)
    
    try:
        start_time = time.time()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode == 0:
            print(f"✅ SUCCESS ({duration:.1f}s)")
            if result.stdout:
                print("STDOUT:")
                print(result.stdout[-1000:])  # Show last 1000 characters
        else:
            print(f"❌ FAILED ({duration:.1f}s)")
            print("STDERR:")
            print(result.stderr[-1000:])  # Show last 1000 characters
            
        print("-" * 80)
        return result.returncode == 0, duration
        
    except subprocess.TimeoutExpired:
        print(f"⏰ TIMEOUT after {timeout}s")
        print("-" * 80)
        return False, timeout
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("-" * 80)
        return False, 0


def test_cnn_feature_engineering():
    """Test CNN Feature Engineering"""
    print("🔬 Testing CNN Feature Engineering")
    print("=" * 80)
    
    script_path = "src/feature_engineering/cnn_feature_engineering.py"
    
    # Test 1: Custom CNN with MNIST (quick test)
    success1, duration1 = run_script(script_path, [
        '--dataset', 'MNIST',
        '--model', 'custom',
        '--epochs', '3',
        '--batch-size', '128',
        '--feature-dim', '128',
        '--visualize'
    ])
    
    # Test 2: Transfer learning with CIFAR10 (quick test)
    success2, duration2 = run_script(script_path, [
        '--dataset', 'CIFAR10',
        '--model', 'resnet18',
        '--epochs', '2',
        '--batch-size', '64',
        '--feature-dim', '256',
        '--visualize'
    ])
    
    return success1 and success2, duration1 + duration2


def test_rnn_feature_engineering():
    """Test RNN Feature Engineering"""
    print(" Testing RNN Feature Engineering")
    print("=" * 80)
    
    script_path = "src/feature_engineering/rnn_feature_engineering.py"
def test_rnn_feature_engineering():
    """Test RNN Feature Engineering"""
    print(" Testing RNN Feature Engineering")
    print("=" * 80)
    
    script_path = "feature_engineering/rnn_feature_engineering.py"
    
    # Test 1: LSTM model (quick test)
    success1, duration1 = run_script(script_path, [
        '--model', 'lstm',
        '--epochs', '3',
        '--batch-size', '64',
        '--hidden-dim', '64',
        '--feature-dim', '128',
        '--num-samples', '1000',
        '--visualize'
    ])
    
    # Test 2: GRU model (quick test)
    success2, duration2 = run_script(script_path, [
        '--model', 'gru',
        '--epochs', '2',
        '--batch-size', '64',
        '--hidden-dim', '64',
        '--feature-dim', '128',
        '--num-samples', '1000',
        '--visualize'
    ])
    
    return success1 and success2, duration1 + duration2


def test_transformer_feature_engineering():
    """Test Transformer Feature Engineering"""
    print(" Testing Transformer Feature Engineering")
    print("=" * 80)
    
    script_path = "src/feature_engineering/transformer_feature_engineering.py"
    
    # Test: Small transformer model (quick test)
    success, duration = run_script(script_path, [
        '--model', 'transformer',
        '--epochs', '2',
        '--batch-size', '32',
        '--d-model', '128',
        '--n-heads', '4',
        '--n-layers', '2',
        '--feature-dim', '128',
        '--visualize'
    ])
    
    return success, duration


def test_autoencoder_feature_engineering():
    """Test Autoencoder Feature Engineering"""
    print(" Testing Autoencoder Feature Engineering")
    print("=" * 80)
    
    script_path = "src/feature_engineering/autoencoder_feature_engineering.py"
    
    # Test 1: Simple autoencoder (quick test)
    success1, duration1 = run_script(script_path, [
        '--model', 'simple',
        '--dataset', 'MNIST',
        '--epochs', '3',
        '--batch-size', '128',
        '--latent-dim', '32',
        '--visualize'
    ])
    
    # Test 2: VAE (quick test)
    success2, duration2 = run_script(script_path, [
        '--model', 'vae',
        '--dataset', 'MNIST',
        '--epochs', '2',
        '--batch-size', '128',
        '--latent-dim', '16',
        '--visualize'
    ])
    
    return success1 and success2, duration1 + duration2


def test_transfer_learning_feature_engineering():
    """Test Transfer Learning Feature Engineering"""
    print(" Testing Transfer Learning Feature Engineering")
    print("=" * 80)
    
    script_path = "src/feature_engineering/transfer_learning_feature_engineering.py"


def test_autoencoder_feature_engineering():
    """Test Autoencoder Feature Engineering"""
    print(" Testing Autoencoder Feature Engineering")
    print("=" * 80)
    
    script_path = "feature_engineering/autoencoder_feature_engineering.py"
    
    # Test 1: Simple Autoencoder
    success1, duration1 = run_script(script_path, [
        '--model', 'simple',
        '--dataset', 'MNIST',
        '--epochs', '3',
        '--batch-size', '128',
        '--latent-dim', '64',
        '--visualize'
    ])
    
    # Test 2: VAE
    success2, duration2 = run_script(script_path, [
        '--model', 'vae',
        '--dataset', 'MNIST',
        '--epochs', '2',
        '--batch-size', '128',
        '--latent-dim', '32',
        '--visualize'
    ])
    
    return success1 and success2, duration1 + duration2


def test_transfer_learning_feature_engineering():
    """Test Transfer Learning Feature Engineering"""
    print(" Testing Transfer Learning Feature Engineering")
    print("=" * 80)
    
    script_path = "feature_engineering/transfer_learning_feature_engineering.py"
    
    # Test: ResNet18 with frozen backbone (quick test)
    success, duration = run_script(script_path, [
        '--architecture', 'resnet18',
        '--dataset', 'CIFAR10',
        '--strategy', 'frozen',
        '--epochs', '2',
        '--batch-size', '32',
        '--feature-dim', '128',
        '--visualize'
    ])
    
    return success, duration


def check_environment():
    """Check if the environment is properly set up"""
    print(" Checking Environment")
    print("=" * 80)
    
    # Check Python packages
    required_packages = [
        'torch', 'torchvision', 'numpy', 'matplotlib', 
        'sklearn', 'seaborn', 'PIL'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {missing_packages}")
        return False
    
    # Check directories
    required_dirs = [
        '../results',
        '../models', 
        '../datasets',
        'feature_engineering'
    ]
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ Directory: {directory}")
        else:
            print(f"❌ Directory: {directory}")
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"   Created: {directory}")
            except Exception as e:
                print(f"   Failed to create: {e}")
                return False
    
    print("✅ Environment check passed!")
    return True


def create_summary_report(results):
    """Create a summary report of all tests"""
    print("\n" + "=" * 80)
    print(" FEATURE ENGINEERING DEMO SUMMARY REPORT")
    print("=" * 80)
    
    total_duration = 0
    successful_tests = 0
    total_tests = len(results)
    
    for test_name, (success, duration) in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:<40} {status:>10} ({duration:>6.1f}s)")
        total_duration += duration
        if success:
            successful_tests += 1
    
    print("-" * 80)
    print(f"{'TOTAL TESTS':<40} {successful_tests}/{total_tests:>10} ({total_duration:>6.1f}s)")
    
    success_rate = (successful_tests / total_tests) * 100
    print(f"{'SUCCESS RATE':<40} {success_rate:>10.1f}%")
    
    if successful_tests == total_tests:
        print("\n FEATURE ENGINEERING TESTS PASSED.")
        print("Your Feature Engineering pipeline is working correctly!")
    else:
        print(f"\n⚠️  {total_tests - successful_tests} test(s) failed.")
        print("❗ Please check the error messages above.")
    
    # Recommendations
    print("\nRECOMMENDATIONS:")
    print("-" * 80)
    
    if successful_tests > 0:
        print(" Working components can be used for feature engineering")
        print(" Check ../results/ directory for generated visualizations")
        print(" Check ../models/ directory for saved models")
    
    if successful_tests < total_tests:
        print("⚠️  For failed tests, consider:")
        print("   • Reducing batch sizes if running out of memory")
        print("   • Reducing model complexity for faster testing")
        print("   • Checking CUDA availability for GPU acceleration")
    
    print(" See README.md for detailed usage instructions")
    print("=" * 80)
    
    return successful_tests == total_tests


def main():
    parser = argparse.ArgumentParser(description='Feature Engineering Demo')
    parser.add_argument('--quick', action='store_true', 
                      help='Run quick tests only (reduced epochs)')
    parser.add_argument('--skip-env-check', action='store_true',
                      help='Skip environment check')
    parser.add_argument('--test', choices=['cnn', 'rnn', 'transformer', 'autoencoder', 'transfer'],
                      help='Run specific test only')
    
    args = parser.parse_args()
    
    print(" Feature Engineering (Demo)")
    print("=" * 80)
    print("This demo will test all feature engineering approaches:")
    print("1. CFeature Engineering for NN ")
    print("2. Feature Engineering for RNN ")
    print("3. Feature Engineering for Transformer ")
    print("4. Feature Engineering for Autoencoder ")
    print("5. Feature Engineering for Transfer Learning")
    print("=" * 80)
    
    if not args.skip_env_check:
        if not check_environment():
            print("❌ Environment check failed. Please fix issues before proceeding.")
            return
    
    # Stay in current directory - scripts are here
    original_dir = os.getcwd()
    
    try:
        results = {}
        
        # Run tests
        if args.test is None or args.test == 'cnn':
            success, duration = test_cnn_feature_engineering()
            results['CNN Feature Engineering'] = (success, duration)
        
        if args.test is None or args.test == 'rnn':
            success, duration = test_rnn_feature_engineering()
            results['RNN Feature Engineering'] = (success, duration)
        
        if args.test is None or args.test == 'transformer':
            success, duration = test_transformer_feature_engineering()
            results['Transformer Feature Engineering'] = (success, duration)
        
        if args.test is None or args.test == 'autoencoder':
            success, duration = test_autoencoder_feature_engineering()
            results['Autoencoder Feature Engineering'] = (success, duration)
        
        if args.test is None or args.test == 'transfer':
            success, duration = test_transfer_learning_feature_engineering()
            results['Transfer Learning Feature Engineering'] = (success, duration)
        
        # Create summary report
        all_passed = create_summary_report(results)
        
        # Return appropriate exit code
        return 0 if all_passed else 1
        
    finally:
        # Return to original directory
        os.chdir(original_dir)


if __name__ == '__main__':
    exit(main())
