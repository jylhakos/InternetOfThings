#!/usr/bin/env python3
"""
Quick Start Script for RNN+LSTM Time-Series Forecasting
Electricity consumption prediction with comprehensive evaluation
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def print_header():
    print("🚀 RNN+LSTM TIME-SERIES FORECASTING - QUICK START")
    print("="*60)
    print("Electricity Consumption Prediction with Deep Learning")
    print("Real-time weather integration • Comprehensive evaluation")
    print("="*60)

def check_environment():
    print("\n🔧 Checking environment...")
    
    # Check if we're in the right directory
    if not os.path.exists('Dataset/electrical-consumption-2024.csv'):
        print("❌ Please run this script from the src/ directory")
        print("   cd src/")
        print("   python quick_start.py")
        return False
    
    # Check Python environment
    try:
        import torch
        import pandas as pd
        import numpy as np
        print("✅ Python environment ready")
        print(f"   PyTorch: {torch.__version__}")
        print(f"   Device: {'GPU' if torch.cuda.is_available() else 'CPU'}")
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("   Please install requirements: pip install -r requirements.txt")
        return False

def run_pipeline_step(script_name, description, estimated_time):
    print(f"\n📊 {description}")
    print(f"⏱️  Estimated time: {estimated_time}")
    print("-" * 50)
    
    # Ask user if they want to run this step
    response = input(f"Run {script_name}? (y/n/q): ").lower().strip()
    
    if response == 'q':
        print("👋 Goodbye!")
        return False
    elif response == 'y' or response == '':
        print(f"🚀 Running {script_name}...")
        start_time = time.time()
        
        try:
            # Run the script
            result = subprocess.run([sys.executable, script_name], 
                                  capture_output=True, text=True, timeout=1800)  # 30 min timeout
            
            elapsed_time = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ {script_name} completed successfully in {elapsed_time:.1f}s")
                if result.stdout:
                    # Show last few lines of output
                    lines = result.stdout.split('\n')[-10:]
                    print("📄 Output summary:")
                    for line in lines:
                        if line.strip():
                            print(f"   {line}")
                return True
            else:
                print(f"❌ {script_name} failed:")
                print(result.stderr)
                return True  # Continue with other steps
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {script_name} timed out after 30 minutes")
            return True
        except Exception as e:
            print(f"❌ Error running {script_name}: {e}")
            return True
    else:
        print(f"⏭️  Skipping {script_name}")
        return True

def main():
    print_header()
    
    # Check environment
    if not check_environment():
        return
    
    print("\n🎯 PIPELINE OVERVIEW:")
    print("1. Exploratory Data Analysis - Understand patterns in electricity consumption")
    print("2. Model Training - Train RNN, LSTM, and Deep LSTM models")
    print("3. Advanced Evaluation - Comprehensive metrics and validation")
    print("4. Hyperparameter Optimization - Find optimal model configuration")
    print("5. API Server - Deploy real-time prediction service")
    
    # Pipeline steps
    steps = [
        ("validate_pipeline.py", "Environment Validation", "1-2 minutes"),
        ("exploratory_data_analysis.py", "Exploratory Data Analysis", "5-10 minutes"),
        ("train_models.py", "Model Training & Comparison", "15-30 minutes"),
        ("advanced_evaluation.py", "Advanced Metrics Evaluation", "2-5 minutes"),
    ]
    
    # Run each step
    for script, description, time_est in steps:
        if not run_pipeline_step(script, description, time_est):
            break
    
    # Optional steps
    print("\n🎯 OPTIONAL ADVANCED STEPS:")
    
    # Hyperparameter optimization (can take a while)
    response = input("Run hyperparameter optimization? (takes 30-60 minutes) (y/n): ").lower()
    if response == 'y':
        run_pipeline_step("model_optimization.py", "Hyperparameter Optimization", "30-60 minutes")
    
    # API server
    response = input("Start API server for real-time predictions? (y/n): ").lower()
    if response == 'y':
        print("\n🌐 Starting API Server...")
        print("Server will start at: http://localhost:5000")
        print("Press Ctrl+C to stop the server")
        print("-" * 50)
        try:
            subprocess.run([sys.executable, "api_server.py"])
        except KeyboardInterrupt:
            print("\n👋 API server stopped")
    
    # Jupyter notebook
    if os.path.exists("RNN_LSTM_Electricity_Forecasting.ipynb"):
        response = input("Open Jupyter notebook for interactive analysis? (y/n): ").lower()
        if response == 'y':
            print("🔬 Opening Jupyter notebook...")
            try:
                subprocess.run(["jupyter", "notebook", "RNN_LSTM_Electricity_Forecasting.ipynb"])
            except FileNotFoundError:
                print("❌ Jupyter not found. Install with: pip install jupyter")
    
    print("\n🎉 QUICK START COMPLETED!")
    print("="*60)
    print("📊 Your RNN+LSTM forecasting pipeline is ready!")
    print("📈 Check the generated plots and reports for insights")
    print("🔧 Modify hyperparameters and retrain for optimal performance")
    print("🌐 Use the API server for real-time electricity consumption predictions")
    print("="*60)

if __name__ == "__main__":
    main()
