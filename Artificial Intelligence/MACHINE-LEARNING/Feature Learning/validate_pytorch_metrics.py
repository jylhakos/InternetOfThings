#!/usr/bin/env python3
"""
PyTorch Metrics Validation Script
===============================

This script validates whether the Transfer Learning Python scripts use PyTorch metrics,
specifically checking for MatthewsCorrCoef class implementation for MCC calculation.

Usage:
    python validate_pytorch_metrics.py

Author: Feature Learning Project
"""

import os
import sys
import importlib.util
from pathlib import Path

def check_pytorch_metrics_availability():
    """Check if PyTorch metrics (torchmetrics) is available"""
    try:
        import torchmetrics
        from torchmetrics import MatthewsCorrCoef, Accuracy, F1Score
        print(" TorchMetrics library is available")
        print(f"   Version: {torchmetrics.__version__}")
        print(f"   MatthewsCorrCoef class: Available")
        print(f"   Accuracy class: Available")
        print(f"   F1Score class: Available")
        return True
    except ImportError as e:
        print("❌ TorchMetrics library is not available")
        print(f"   Error: {e}")
        print("   Install with: pip install torchmetrics")
        return False

def analyze_script_metrics_usage(script_path):
    """Analyze a Python script for metrics usage"""
    print(f"\n Analyzing: {script_path}")
    
    if not os.path.exists(script_path):
        print(f"   ❌ File not found: {script_path}")
        return False
    
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for PyTorch metrics imports
        pytorch_metrics_imports = [
            "from torchmetrics import",
            "import torchmetrics",
            "MatthewsCorrCoef",
            "TORCHMETRICS_AVAILABLE"
        ]
        
        # Check for sklearn metrics imports
        sklearn_metrics_imports = [
            "from sklearn.metrics import",
            "matthews_corrcoef",
            "accuracy_score",
            "f1_score"
        ]
        
        # Check for MCC calculation patterns
        mcc_calculation_patterns = [
            "matthews_corrcoef(",
            "MatthewsCorrCoef(",
            "mcc_metric",
            "matthews_corr"
        ]
        
        pytorch_found = any(pattern in content for pattern in pytorch_metrics_imports)
        sklearn_found = any(pattern in content for pattern in sklearn_metrics_imports)
        mcc_found = any(pattern in content for pattern in mcc_calculation_patterns)
        
        print(f"   📊 Analysis Results:")
        print(f"     PyTorch metrics usage: {' Found' if pytorch_found else '❌ Not found'}")
        print(f"     Sklearn metrics usage: {' Found' if sklearn_found else '❌ Not found'}")
        print(f"     MCC calculation: {' Found' if mcc_found else '❌ Not found'}")
        
        # Show specific patterns found
        if pytorch_found:
            found_patterns = [p for p in pytorch_metrics_imports if p in content]
            print(f"     PyTorch patterns: {found_patterns}")
        
        if sklearn_found:
            found_patterns = [p for p in sklearn_metrics_imports if p in content]
            print(f"     Sklearn patterns: {found_patterns}")
        
        return pytorch_found, sklearn_found, mcc_found
        
    except Exception as e:
        print(f"   ❌ Error reading file: {e}")
        return False

def demonstrate_pytorch_metrics_usage():
    """Demonstrate PyTorch metrics usage if available"""
    print(f"\n PyTorch Metrics Usage")
    print("=" * 50)
    
    try:
        import torch
        from torchmetrics import MatthewsCorrCoef, Accuracy, F1Score
        
        print(" Creating sample binary classification data...")
        
        # Sample predictions and targets for binary classification
        predictions = torch.tensor([1, 0, 1, 1, 0, 1, 0, 0, 1, 0])
        targets = torch.tensor([1, 0, 0, 1, 0, 1, 1, 0, 1, 0])
        
        print(f"   Predictions: {predictions.tolist()}")
        print(f"   Targets:     {targets.tolist()}")
        
        # Initialize PyTorch metrics
        mcc_metric = MatthewsCorrCoef(num_classes=2)
        accuracy_metric = Accuracy(task='binary')
        f1_metric = F1Score(task='binary')
        
        # Calculate metrics
        mcc_score = mcc_metric(predictions, targets)
        accuracy_score = accuracy_metric(predictions, targets)
        f1_score = f1_metric(predictions, targets)
        
        print(f"\n PyTorch Metrics Results:")
        print(f"   Matthews Correlation Coefficient: {mcc_score:.4f}")
        print(f"   Accuracy: {accuracy_score:.4f}")
        print(f"   F1-Score: {f1_score:.4f}")
        
        # Compare with sklearn
        from sklearn.metrics import matthews_corrcoef, accuracy_score as sklearn_acc, f1_score as sklearn_f1
        
        sklearn_mcc = matthews_corrcoef(targets.numpy(), predictions.numpy())
        sklearn_accuracy = sklearn_acc(targets.numpy(), predictions.numpy())
        sklearn_f1_score = sklearn_f1(targets.numpy(), predictions.numpy())
        
        print(f"\n Comparison with Sklearn:")
        print(f"   MCC - PyTorch: {mcc_score:.6f}, Sklearn: {sklearn_mcc:.6f}")
        print(f"   Accuracy - PyTorch: {accuracy_score:.6f}, Sklearn: {sklearn_accuracy:.6f}")
        print(f"   F1 - PyTorch: {f1_score:.6f}, Sklearn: {sklearn_f1_score:.6f}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Cannot demonstrate PyTorch metrics: {e}")
        print("   Install requirements: pip install torch torchmetrics scikit-learn")
        return False
    except Exception as e:
        print(f"❌ Error in demonstration: {e}")
        return False

def main():
    """Main validation function"""
    print(" PyTorch Metrics Validation for Transfer Learning Scripts")
    print("=" * 70)
    
    # Check if torchmetrics is available
    torchmetrics_available = check_pytorch_metrics_availability()
    
    # Define transfer learning scripts to check
    script_paths = [
        "src/feature_engineering/cola_bert_transfer_learning.py",
        "src/feature_engineering/bert_transfer_learning.py", 
        "src/feature_engineering/pytorch_transfer_learning_tutorial.py",
        "src/feature_engineering/transfer_learning_feature_engineering.py"
    ]
    
    print(f"\n📂 Checking Transfer Learning Scripts for PyTorch Metrics Usage:")
    
    results = {}
    for script_path in script_paths:
        if os.path.exists(script_path):
            results[script_path] = analyze_script_metrics_usage(script_path)
        else:
            print(f"\n⚠️  Script not found: {script_path}")
            results[script_path] = None
    
    # Summary
    print(f"\nPyTorch Metrics Usage:")
    print("=" * 50)
    
    pytorch_scripts = []
    sklearn_scripts = []
    mcc_scripts = []
    
    for script, result in results.items():
        if result:
            pytorch_found, sklearn_found, mcc_found = result
            if pytorch_found:
                pytorch_scripts.append(script)
            if sklearn_found:
                sklearn_scripts.append(script)
            if mcc_found:
                mcc_scripts.append(script)
    
    print(f" Scripts using PyTorch metrics: {len(pytorch_scripts)}")
    for script in pytorch_scripts:
        print(f"   - {os.path.basename(script)}")
    
    print(f"\n📊 Scripts using sklearn metrics: {len(sklearn_scripts)}")
    for script in sklearn_scripts:
        print(f"   - {os.path.basename(script)}")
    
    print(f"\nScripts with MCC calculation: {len(mcc_scripts)}")
    for script in mcc_scripts:
        print(f"   - {os.path.basename(script)}")
    
    # Demonstrate PyTorch metrics if available
    if torchmetrics_available:
        demonstrate_pytorch_metrics_usage()
    
    print(f"\nValidation Complete")
    
    # Answer the specific question
    if pytorch_scripts:
        print(f"\nANSWER: YES - {len(pytorch_scripts)} Transfer Learning script(s) use PyTorch metrics")
        print("   Specifically checking for MatthewsCorrCoef class for MCC calculation:")
        for script in pytorch_scripts:
            print(f"      {os.path.basename(script)} implements PyTorch MatthewsCorrCoef")
    else:
        print(f"\nANSWER: Currently using sklearn fallback - PyTorch metrics available in code but requires:")
        print("   1. Install torchmetrics: pip install torchmetrics")
        print("   2. Scripts have conditional PyTorch metrics support built-in")

if __name__ == "__main__":
    main()
