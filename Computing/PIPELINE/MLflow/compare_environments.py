#!/usr/bin/env python3
"""
Environment Comparison Demo
Demonstrates the differences between conda and venv for MLflow projects
"""

import os
import sys
import subprocess
import time

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🔬 {title}")
    print(f"{'='*60}")

def check_environment_type():
    """Detect the current environment type"""
    if 'CONDA_DEFAULT_ENV' in os.environ:
        conda_env = os.environ['CONDA_DEFAULT_ENV']
        print(f"🐍 Environment Type: Conda")
        print(f"📦 Conda Environment: {conda_env}")
        return 'conda'
    elif 'VIRTUAL_ENV' in os.environ:
        venv_path = os.environ['VIRTUAL_ENV']
        print(f"🐍 Environment Type: Python Virtual Environment")
        print(f"📁 Virtual Environment: {venv_path}")
        return 'venv'
    else:
        print("❌ No virtual environment detected")
        return 'none'

def check_mlflow_integration():
    """Check MLflow integration capabilities"""
    print_header("MLflow Integration Check")
    
    try:
        import mlflow
        print(f"✅ MLflow version: {mlflow.__version__}")
        
        # Check if conda.yaml exists and is properly configured
        if os.path.exists('conda.yaml'):
            print("✅ conda.yaml found - MLflow can auto-create environments")
            
            # Try to validate the conda.yaml
            try:
                subprocess.run(['conda', 'env', 'create', '--dry-run', '-f', 'conda.yaml'], 
                             capture_output=True, check=True)
                print("✅ conda.yaml is valid and MLflow-compatible")
            except subprocess.CalledProcessError:
                print("⚠️ conda.yaml has validation issues")
        else:
            print("❌ conda.yaml not found - MLflow will use requirements.txt fallback")
        
        return True
    except ImportError:
        print("❌ MLflow not installed")
        return False

def check_scientific_libraries():
    """Check scientific computing optimizations"""
    print_header("Scientific Computing Libraries Check")
    
    try:
        import numpy as np
        print(f"✅ NumPy version: {np.__version__}")
        
        # Check BLAS configuration
        try:
            config = np.__config__.show()
            if 'mkl' in str(config).lower():
                print("🚀 NumPy is using Intel MKL (optimized)")
            elif 'openblas' in str(config).lower():
                print("⚡ NumPy is using OpenBLAS (good)")
            else:
                print("⚠️ NumPy using basic BLAS (slower)")
        except:
            print("❓ Cannot determine BLAS backend")
        
        # Check scikit-learn
        import sklearn
        print(f"✅ Scikit-learn version: {sklearn.__version__}")
        
        # Quick performance test
        start_time = time.time()
        from sklearn.datasets import make_regression
        from sklearn.linear_model import LinearRegression
        
        X, y = make_regression(n_samples=10000, n_features=100, random_state=42)
        model = LinearRegression()
        model.fit(X, y)
        
        fit_time = time.time() - start_time
        print(f"⏱️ LinearRegression fit time: {fit_time:.4f}s")
        
        if fit_time < 0.1:
            print("🚀 Excellent performance (likely optimized libraries)")
        elif fit_time < 0.5:
            print("⚡ Good performance")
        else:
            print("⚠️ Slower performance (may benefit from optimized libraries)")
        
        return True
    except ImportError as e:
        print(f"❌ Scientific library import failed: {e}")
        return False

def check_package_sources():
    """Check where packages were installed from"""
    print_header("Package Source Analysis")
    
    env_type = check_environment_type()
    
    if env_type == 'conda':
        try:
            result = subprocess.run(['conda', 'list'], capture_output=True, text=True)
            conda_packages = []
            pip_packages = []
            
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('#'):
                    parts = line.split()
                    if len(parts) >= 4:
                        package_name = parts[0]
                        source = parts[-1]
                        if 'conda' in source or 'anaconda' in source:
                            conda_packages.append(package_name)
                        elif 'pypi' in source:
                            pip_packages.append(package_name)
            
            print(f"📦 Conda packages: {len(conda_packages)}")
            print(f"🐍 Pip packages: {len(pip_packages)}")
            
            key_ml_packages = ['numpy', 'scipy', 'scikit-learn', 'pandas', 'matplotlib']
            conda_ml = [pkg for pkg in conda_packages if any(ml in pkg for ml in key_ml_packages)]
            
            if conda_ml:
                print(f"✅ Key ML packages from conda: {conda_ml}")
                print("🚀 This ensures optimized builds with proper BLAS/LAPACK")
            else:
                print("⚠️ Key ML packages not from conda - may be suboptimal")
        
        except Exception as e:
            print(f"❌ Failed to analyze conda packages: {e}")
    
    elif env_type == 'venv':
        print("🐍 Python virtual environment detected")
        print("📦 All packages installed via pip")
        print("⚠️ May not have optimized scientific computing libraries")
        
        try:
            result = subprocess.run(['pip', 'list'], capture_output=True, text=True)
            pip_lines = result.stdout.split('\n')
            package_count = len([line for line in pip_lines if line.strip() and not line.startswith('Package')])
            print(f"📦 Total pip packages: {package_count}")
        except:
            pass

def demonstrate_mlflow_usage():
    """Demonstrate MLflow project usage"""
    print_header("MLflow Project Usage Demo")
    
    env_type = check_environment_type()
    
    print("🔧 Available MLflow commands based on your environment:")
    
    if env_type == 'conda':
        print("\n✅ Conda Environment - Full MLflow Integration:")
        print("  mlflow run . --experiment-name fish_weight_prediction")
        print("  mlflow run . -e train -P test_size=0.3")
        print("  mlflow run . -e pipeline")
        print("\n🚀 MLflow will automatically:")
        print("  - Create conda environment from conda.yaml")
        print("  - Install optimized scientific libraries")
        print("  - Manage all dependencies")
        print("  - Ensure reproducibility")
    
    elif env_type == 'venv':
        print("\n⚠️ Virtual Environment - Limited MLflow Integration:")
        print("  mlflow run . --no-conda --experiment-name fish_weight_prediction")
        print("  python train.py  # Manual execution")
        print("  make pipeline    # Using Makefile")
        print("\n⚠️ Limitations:")
        print("  - Must use --no-conda flag")
        print("  - Manual dependency management")
        print("  - Less reproducible across systems")
        print("  - May have suboptimal performance")
    
    else:
        print("❌ No environment detected - setup required")

def main():
    """Main comparison demo"""
    print_header("Environment Setup Comparison for MLflow Projects")
    
    print("This demo analyzes your current environment and shows the differences")
    print("between conda and Python virtual environments for MLflow projects.")
    
    # Environment detection
    env_type = check_environment_type()
    
    # MLflow integration check
    mlflow_ok = check_mlflow_integration()
    
    # Scientific computing check
    sci_ok = check_scientific_libraries()
    
    # Package source analysis
    check_package_sources()
    
    # MLflow usage demonstration
    demonstrate_mlflow_usage()
    
    # Final recommendations
    print_header("Recommendations")
    
    if env_type == 'conda':
        print("🎉 Excellent choice! You're using conda.")
        print("✅ Optimal setup for MLflow projects")
        print("✅ Best performance for scientific computing")
        print("✅ Most reproducible configuration")
        print("\n🚀 Ready to run:")
        print("  mlflow run . --experiment-name fish_weight_prediction")
    
    elif env_type == 'venv':
        print("👍 You're using Python virtual environment.")
        print("✅ Standard Python development approach")
        print("⚠️ Suboptimal for MLflow projects")
        print("⚠️ May have performance limitations")
        print("\n🔄 Consider switching to conda:")
        print("  ./setup_conda.sh")
        print("  source activate_conda_env.sh")
        print("\n🚀 Current usage:")
        print("  make pipeline  # Use Makefile instead of mlflow run")
    
    else:
        print("❌ No environment detected")
        print("🔧 Please set up an environment:")
        print("  For conda: ./setup_conda.sh")
        print("  For venv:  ./setup_mlflow.sh")
    
    print("\n📚 See README.md for detailed comparison and setup instructions")

if __name__ == "__main__":
    main()
