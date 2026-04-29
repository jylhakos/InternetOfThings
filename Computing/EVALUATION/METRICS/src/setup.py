#!/usr/bin/env python3
"""
Setup script for the Electricity Forecasting project
This script helps set up the environment and run initial checks
"""

import os
import sys
import subprocess
import platform

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_step(step_num, description):
    """Print formatted step"""
    print(f"\n{step_num}. {description}")
    print("-" * 40)

def run_command(command, description=""):
    """Run system command and return success status"""
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Success")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print("❌ Failed")
            if result.stderr.strip():
                print(f"Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def check_python_version():
    """Check Python version"""
    print_step(1, "Checking Python version")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("✅ Python version is compatible")
        return True
    else:
        print("❌ Python 3.8+ required")
        return False

def check_pip():
    """Check pip availability"""
    print_step(2, "Checking pip")
    
    return run_command("pip --version", "Check pip")

def install_requirements():
    """Install Python requirements"""
    print_step(3, "Installing Python packages")
    
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found")
        return False
    
    print("Installing packages from requirements.txt...")
    return run_command("pip install -r requirements.txt")

def check_datasets():
    """Check if dataset files exist"""
    print_step(4, "Checking dataset files")
    
    dataset_dir = "Dataset"
    electricity_file = os.path.join(dataset_dir, "electrical-consumption-2024.csv")
    temperature_file = os.path.join(dataset_dir, "temperature-2024.csv")
    
    if not os.path.exists(dataset_dir):
        print(f"❌ Dataset directory '{dataset_dir}' not found")
        return False
    
    if not os.path.exists(electricity_file):
        print(f"❌ Electricity data file not found: {electricity_file}")
        return False
    
    if not os.path.exists(temperature_file):
        print(f"❌ Temperature data file not found: {temperature_file}")
        return False
    
    print("✅ All dataset files found")
    
    # Check file sizes
    elec_size = os.path.getsize(electricity_file) / (1024 * 1024)  # MB
    temp_size = os.path.getsize(temperature_file) / (1024 * 1024)  # MB
    
    print(f"   • Electricity data: {elec_size:.1f} MB")
    print(f"   • Temperature data: {temp_size:.1f} MB")
    
    return True

def test_imports():
    """Test importing required packages"""
    print_step(5, "Testing package imports")
    
    packages = {
        'torch': 'PyTorch',
        'numpy': 'NumPy', 
        'pandas': 'Pandas',
        'matplotlib': 'Matplotlib',
        'sklearn': 'Scikit-learn',
        'flask': 'Flask'
    }
    
    success = True
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - Import failed")
            success = False
    
    return success

def test_torch_cuda():
    """Test PyTorch CUDA availability"""
    print_step(6, "Checking PyTorch and CUDA")
    
    try:
        import torch
        print(f"PyTorch version: {torch.__version__}")
        
        if torch.cuda.is_available():
            print(f"✅ CUDA available - {torch.cuda.get_device_name(0)}")
            print(f"   CUDA version: {torch.version.cuda}")
        else:
            print("⚠️  CUDA not available - will use CPU")
            
        return True
    except ImportError:
        print("❌ PyTorch not available")
        return False

def test_basic_functionality():
    """Test basic model functionality"""
    print_step(7, "Testing basic functionality")
    
    try:
        # Test data loading
        import pandas as pd
        
        electricity_file = "Dataset/electrical-consumption-2024.csv"
        temperature_file = "Dataset/temperature-2024.csv"
        
        print("Testing data loading...")
        elec_df = pd.read_csv(electricity_file)
        temp_df = pd.read_csv(temperature_file)
        
        print(f"✅ Electricity data: {len(elec_df)} records")
        print(f"✅ Temperature data: {len(temp_df)} records")
        
        # Test model import
        print("Testing model import...")
        from electricity_forecasting import ElectricityForecastModel
        
        model = ElectricityForecastModel(model_type='LSTM')
        print("✅ Model class imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def create_virtual_environment():
    """Create virtual environment"""
    print_step("Optional", "Create virtual environment")
    
    venv_name = "electricity_forecast_env"
    
    response = input(f"Create virtual environment '{venv_name}'? (y/n): ").lower()
    
    if response == 'y':
        print(f"Creating virtual environment: {venv_name}")
        
        # Create virtual environment
        if run_command(f"python -m venv {venv_name}"):
            print(f"✅ Virtual environment '{venv_name}' created")
            
            # Show activation commands
            system = platform.system().lower()
            if system == "windows":
                activate_cmd = f"{venv_name}\\Scripts\\activate"
            else:
                activate_cmd = f"source {venv_name}/bin/activate"
            
            print(f"\nTo activate the virtual environment:")
            print(f"   {activate_cmd}")
            print(f"\nThen install packages:")
            print(f"   pip install -r requirements.txt")
            
            return True
        else:
            print(f"❌ Failed to create virtual environment")
            return False
    else:
        print("Skipping virtual environment creation")
        return True

def show_next_steps():
    """Show next steps after setup"""
    print_header("NEXT STEPS")
    
    print("🚀 Your electricity forecasting project is ready!")
    print("\nRecommended workflow:")
    print("1. Explore the data:")
    print("   python exploratory_data_analysis.py")
    
    print("\n2. Train models:")
    print("   python train_models.py")
    
    print("\n3. Start API server:")
    print("   python api_server.py")
    
    print("\n4. Test API (in another terminal):")
    print("   python test_api.py")
    
    print("\n5. Quick demo:")
    print("   python demo.py")
    
    print("\n📚 Key files:")
    print("• README.md - Complete documentation")
    print("• config.py - Configuration settings")
    print("• requirements.txt - Python dependencies")
    
    print("\n🔗 API endpoints (after starting server):")
    print("• http://localhost:5000/ - Documentation")
    print("• http://localhost:5000/model/status - Model status")
    print("• http://localhost:5000/forecast/next-day - Forecast API")

def main():
    """Main setup function"""
    print_header("ELECTRICITY FORECASTING PROJECT SETUP")
    print("This script will help you set up the environment for")
    print("electricity consumption forecasting with RNN/LSTM models.")
    
    # Setup steps
    steps = [
        check_python_version,
        check_pip,
        install_requirements,
        check_datasets,
        test_imports,
        test_torch_cuda,
        test_basic_functionality
    ]
    
    success_count = 0
    
    for step_func in steps:
        if step_func():
            success_count += 1
        else:
            print(f"\n⚠️  Step failed: {step_func.__name__}")
    
    # Summary
    print_header("SETUP SUMMARY")
    print(f"Completed: {success_count}/{len(steps)} steps")
    
    if success_count == len(steps):
        print("🎉 Setup completed successfully!")
        show_next_steps()
    elif success_count >= len(steps) - 2:
        print("⚠️  Setup mostly successful with minor issues")
        show_next_steps()
    else:
        print("❌ Setup failed. Please check the errors above.")
        print("\nCommon solutions:")
        print("• Install Python 3.8+")
        print("• Install pip: python -m ensurepip --upgrade")
        print("• Install packages: pip install -r requirements.txt")
        print("• Check dataset files in Dataset/ folder")
    
    # Optional virtual environment
    create_virtual_environment()

if __name__ == "__main__":
    main()
