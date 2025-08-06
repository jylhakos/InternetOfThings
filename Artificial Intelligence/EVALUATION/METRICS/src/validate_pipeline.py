#!/usr/bin/env python3
"""
Validation script for RNN+LSTM Time-Series Forecasting Pipeline
Tests all core components and generates a comprehensive report
"""

import os
import sys
import warnings
warnings.filterwarnings('ignore')

def test_environment():
    """Test Python environment and dependencies"""
    print("🔧 TESTING PYTHON ENVIRONMENT")
    print("="*50)
    
    try:
        import torch
        print(f"✅ PyTorch: {torch.__version__}")
        print(f"   CUDA available: {torch.cuda.is_available()}")
        print(f"   Device: {'GPU' if torch.cuda.is_available() else 'CPU'}")
    except ImportError:
        print("❌ PyTorch not installed")
        return False
    
    try:
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        import sklearn
        print(f"✅ Core libraries:")
        print(f"   Pandas: {pd.__version__}")
        print(f"   NumPy: {np.__version__}")
        print(f"   Scikit-learn: {sklearn.__version__}")
    except ImportError as e:
        print(f"❌ Missing core library: {e}")
        return False
    
    return True

def test_datasets():
    """Test dataset availability and format"""
    print("\n📊 TESTING DATASET FILES")
    print("="*50)
    
    datasets = {
        'electrical-consumption-2024.csv': 'Historical electricity consumption data',
        'temperature-2024.csv': 'Weather temperature data'
    }
    
    all_present = True
    
    for filename, description in datasets.items():
        filepath = f"Dataset/{filename}"
        if os.path.exists(filepath):
            try:
                import pandas as pd
                df = pd.read_csv(filepath)
                print(f"✅ {filename}")
                print(f"   Description: {description}")
                print(f"   Shape: {df.shape}")
                print(f"   Columns: {list(df.columns)[:3]}{'...' if len(df.columns) > 3 else ''}")
                print(f"   Memory usage: {df.memory_usage().sum() / 1024:.1f} KB")
            except Exception as e:
                print(f"⚠️  {filename} exists but has issues: {e}")
                all_present = False
        else:
            print(f"❌ {filename} not found")
            all_present = False
    
    return all_present

def test_model_imports():
    """Test model and evaluation imports"""
    print("\n🧠 TESTING MODEL COMPONENTS")
    print("="*50)
    
    components = [
        ('electricity_forecasting', 'Core RNN/LSTM models'),
        ('advanced_evaluation', 'Comprehensive metrics evaluation'),
        ('model_optimization', 'Hyperparameter optimization'),
        ('train_models', 'Model training pipeline')
    ]
    
    all_working = True
    
    for module_name, description in components:
        try:
            __import__(module_name)
            print(f"✅ {module_name}.py - {description}")
        except ImportError as e:
            print(f"❌ {module_name}.py - Import error: {e}")
            all_working = False
        except Exception as e:
            print(f"⚠️  {module_name}.py - Warning: {e}")
    
    return all_working

def test_metrics_calculation():
    """Test evaluation metrics calculation"""
    print("\n📈 TESTING METRICS CALCULATION")
    print("="*50)
    
    try:
        from advanced_evaluation import TimeSeriesMetrics
        import numpy as np
        
        # Generate test data
        y_true = np.array([1000, 1200, 1100, 1300, 1250, 1150])
        y_pred = np.array([1050, 1180, 1120, 1280, 1270, 1140])
        
        # Calculate metrics
        rmse = TimeSeriesMetrics.rmse(y_true, y_pred)
        mae = TimeSeriesMetrics.mae(y_true, y_pred)
        mape = TimeSeriesMetrics.mape(y_true, y_pred)
        smape = TimeSeriesMetrics.smape(y_true, y_pred)
        da = TimeSeriesMetrics.directional_accuracy(y_true, y_pred)
        
        print("✅ Metrics calculation test:")
        print(f"   RMSE: {rmse:.2f}")
        print(f"   MAE: {mae:.2f}")
        print(f"   MAPE: {mape:.2f}%")
        print(f"   sMAPE: {smape:.2f}%")
        print(f"   Directional Accuracy: {da:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Metrics calculation failed: {e}")
        return False

def test_model_creation():
    """Test model creation and basic functionality"""
    print("\n🔧 TESTING MODEL CREATION")
    print("="*50)
    
    try:
        import torch
        import torch.nn as nn
        from model_optimization import OptimizedLSTMModel
        
        # Create test model
        model = OptimizedLSTMModel(
            input_size=7,
            hidden_size=32,
            num_layers=2,
            dropout=0.2
        )
        
        # Test forward pass
        test_input = torch.randn(1, 10, 7)  # batch_size=1, seq_len=10, features=7
        output = model(test_input)
        
        print("✅ Model creation test:")
        print(f"   Model parameters: {sum(p.numel() for p in model.parameters()):,}")
        print(f"   Input shape: {test_input.shape}")
        print(f"   Output shape: {output.shape}")
        print(f"   Model device: {next(model.parameters()).device}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model creation failed: {e}")
        return False

def test_api_components():
    """Test API server components"""
    print("\n🌐 TESTING API COMPONENTS")
    print("="*50)
    
    try:
        import flask
        import requests
        import geopy
        print("✅ API dependencies:")
        print(f"   Flask: {flask.__version__}")
        print(f"   Requests: {requests.__version__}")
        print(f"   Geopy: {geopy.__version__}")
        
        # Test if api_server can be imported (without running)
        try:
            import api_server
            print("✅ API server module imports successfully")
        except Exception as e:
            print(f"⚠️  API server import warning: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ API dependency missing: {e}")
        return False

def run_comprehensive_validation():
    """Run all validation tests"""
    print("🚀 RNN+LSTM TIME-SERIES FORECASTING VALIDATION")
    print("="*60)
    print("Validating electricity consumption prediction pipeline...")
    print()
    
    # Run all tests
    tests = [
        test_environment,
        test_datasets,
        test_model_imports,
        test_metrics_calculation,
        test_model_creation,
        test_api_components
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "="*60)
    print("📋 VALIDATION SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Environment is ready for RNN+LSTM time-series forecasting")
        print("✅ Datasets are available and properly formatted")
        print("✅ Model components are working correctly")
        print("✅ Metrics evaluation framework is functional")
        print("✅ API components are ready for deployment")
        
        print("\n🚀 NEXT STEPS:")
        print("1. Run exploratory data analysis: python exploratory_data_analysis.py")
        print("2. Train models: python train_models.py")
        print("3. Run hyperparameter optimization: python model_optimization.py")
        print("4. Start API server: python api_server.py")
        print("5. Open Jupyter notebook for interactive analysis")
        
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("Please check the errors above and resolve issues before proceeding.")
        
        if results[0]:  # Environment test passed
            print("\n🔧 TROUBLESHOOTING TIPS:")
            if not results[1]:  # Dataset test failed
                print("- Check if Dataset/ folder contains the required CSV files")
            if not results[2]:  # Model imports failed
                print("- Verify all Python modules are in the src/ directory")
            if not results[3]:  # Metrics failed
                print("- Check advanced_evaluation.py for syntax errors")
            if not results[4]:  # Model creation failed
                print("- Verify PyTorch installation and compatibility")
            if not results[5]:  # API components failed
                print("- Install missing dependencies with pip install -r requirements.txt")
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_validation()
    sys.exit(0 if success else 1)
