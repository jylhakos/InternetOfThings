#!/usr/bin/env python3
"""
A demonstration script for electricity forecasting models
This script provides a quick way to test the RNN/LSTM models
"""

import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Add current directory to path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from electricity_forecasting import ElectricityForecastModel
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please install dependencies: pip install -r requirements.txt")
    sys.exit(1)

def quick_demo():
    """
    Quick demonstration of the electricity forecasting system
    """
    print("🔌 ELECTRICITY CONSUMPTION FORECASTING DEMO")
    print("=" * 50)
    
    # Check if datasets exist
    electricity_file = 'Dataset/electrical-consumption-2024.csv'
    temperature_file = 'Dataset/temperature-2024.csv'
    
    if not os.path.exists(electricity_file):
        print(f"❌ Error: {electricity_file} not found!")
        return False
    
    if not os.path.exists(temperature_file):
        print(f"❌ Error: {temperature_file} not found!")
        return False
    
    print("✅ Dataset files found")
    
    # Initialize model
    print("\n📚 Initializing LSTM model...")
    model = ElectricityForecastModel(
        model_type='LSTM',
        sequence_length=24,
        hidden_size=32,  # Smaller for quick demo
        num_layers=2,
        dropout=0.2,
        learning_rate=0.001
    )
    
    # Load data
    print("📊 Loading electricity and temperature data...")
    try:
        data = model.load_data(electricity_file, temperature_file)
        print(f"✅ Loaded {len(data)} daily records")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return False
    
    # Prepare data
    print("🔧 Preparing training sequences...")
    try:
        X_train, y_train, X_test, y_test = model.prepare_sequences(train_ratio=0.8)
        print(f"✅ Training samples: {len(X_train)}, Test samples: {len(X_test)}")
    except Exception as e:
        print(f"❌ Error preparing data: {e}")
        return False
    
    # Quick training (limited epochs for demo)
    print("\n🚀 Training model (quick demo - 10 epochs)...")
    try:
        train_losses = model.train_model(epochs=10, batch_size=16)
        print("✅ Training completed!")
    except Exception as e:
        print(f"❌ Error during training: {e}")
        return False
    
    # Evaluate
    print("\n📈 Evaluating model performance...")
    try:
        metrics = model.evaluate_model()
        print("✅ Model Performance:")
        print(f"   • RMSE: {metrics['RMSE']:.1f} MW")
        print(f"   • MAE: {metrics['MAE']:.1f} MW")
        print(f"   • MAPE: {metrics['MAPE']:.1f}%")
    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        return False
    
    # Save model
    model_file = 'demo_lstm_model.pth'
    print(f"\n💾 Saving model to {model_file}...")
    try:
        model.save_model(model_file)
        print("✅ Model saved successfully!")
    except Exception as e:
        print(f"❌ Error saving model: {e}")
        return False
    
    # Demonstrate prediction
    print("\n🔮 Making sample prediction...")
    try:
        # Use last test sequence for prediction
        last_sequence = X_test[-1:].cpu().numpy()
        prediction = model.predict_next_day(last_sequence)
        
        # Get actual last value for comparison
        last_actual = model.load_scaler.inverse_transform(
            y_test[-1:].cpu().numpy().reshape(-1, 1)
        )[0, 0]
        
        print("✅ Prediction Results:")
        print(f"   • Last observed load: {last_actual:.1f} MW")
        print(f"   • Predicted next day: {prediction:.1f} MW")
        print(f"   • Change: {prediction - last_actual:+.1f} MW")
        
    except Exception as e:
        print(f"❌ Error making prediction: {e}")
        return False
    
    print("\n🎉 Demo completed successfully!")
    print("\nNext steps:")
    print("• Run full training: python train_models.py")
    print("• Start API server: python api_server.py")
    print("• Explore data: python exploratory_data_analysis.py")
    
    return True

def check_dependencies():
    """
    Check if all required dependencies are available
    """
    print("🔍 Checking dependencies...")
    
    required_packages = {
        'torch': 'PyTorch',
        'numpy': 'NumPy',
        'pandas': 'Pandas',
        'sklearn': 'Scikit-learn',
        'matplotlib': 'Matplotlib'
    }
    
    missing = []
    
    for package, name in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - NOT FOUND")
            missing.append(name)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies available!")
    return True

def show_help():
    """
    Show help information
    """
    print("ELECTRICITY FORECASTING DEMO")
    print("=" * 30)
    print("Usage: python demo.py [command]")
    print("\nCommands:")
    print("  demo     - Run quick demonstration")
    print("  check    - Check dependencies")
    print("  help     - Show this help")
    print("\nExamples:")
    print("  python demo.py demo")
    print("  python demo.py check")

def main():
    """
    Main function
    """
    if len(sys.argv) < 2:
        command = 'demo'
    else:
        command = sys.argv[1].lower()
    
    if command == 'demo':
        if check_dependencies():
            quick_demo()
        else:
            print("\n❌ Cannot run demo due to missing dependencies")
    
    elif command == 'check':
        check_dependencies()
    
    elif command == 'help':
        show_help()
    
    else:
        print(f"Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main()
