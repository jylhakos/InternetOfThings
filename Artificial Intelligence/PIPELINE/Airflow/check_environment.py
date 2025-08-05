#!/usr/bin/env python3
"""
Environment Check Script
Verifies that the environment is properly set up for BERT fine-tuning and Apache Airflow
"""

import sys
import subprocess
import importlib
from pathlib import Path

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def check_python_version():
    """Check Python version"""
    print_header("PYTHON VERSION CHECK")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    print_info(f"Python version: {version_str}")
    
    if version.major >= 3 and version.minor >= 8:
        print_success("Python version is compatible (3.8+)")
        return True
    else:
        print_error(f"Python 3.8+ required, found {version_str}")
        return False

def check_virtual_environment():
    """Check if running in virtual environment"""
    print_header("VIRTUAL ENVIRONMENT CHECK")
    
    # Check for virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print_success("Running in virtual environment")
        print_info(f"Python executable: {sys.executable}")
        return True
    else:
        print_warning("Not running in virtual environment")
        print_warning("Consider using: python3 -m venv bert_airflow_env")
        return False

def check_package_import(package_name, display_name=None, version_attr='__version__'):
    """Check if a package can be imported and get version"""
    if display_name is None:
        display_name = package_name
    
    try:
        module = importlib.import_module(package_name)
        if hasattr(module, version_attr):
            version = getattr(module, version_attr)
            print_success(f"{display_name}: {version}")
        else:
            print_success(f"{display_name}: Imported successfully")
        return True
    except ImportError:
        print_error(f"{display_name}: Not installed")
        return False

def check_core_packages():
    """Check core ML packages"""
    print_header("CORE PACKAGES CHECK")
    
    packages = [
        ('torch', 'PyTorch'),
        ('transformers', 'Transformers'),
        ('sklearn', 'scikit-learn', '__version__'),
        ('pandas', 'Pandas'),
        ('numpy', 'NumPy'),
    ]
    
    all_ok = True
    for package_info in packages:
        if len(package_info) == 2:
            package, display = package_info
            result = check_package_import(package, display)
        else:
            package, display, version_attr = package_info
            result = check_package_import(package, display, version_attr)
        all_ok = all_ok and result
    
    return all_ok

def check_optional_packages():
    """Check optional packages"""
    print_header("OPTIONAL PACKAGES CHECK")
    
    packages = [
        ('matplotlib', 'Matplotlib'),
        ('seaborn', 'Seaborn'),
        ('plotly', 'Plotly'),
        ('wordcloud', 'WordCloud'),
        ('textstat', 'TextStat'),
        ('fastapi', 'FastAPI'),
        ('requests', 'Requests'),
    ]
    
    installed_count = 0
    for package, display in packages:
        if check_package_import(package, display):
            installed_count += 1
    
    print_info(f"Optional packages: {installed_count}/{len(packages)} installed")
    return installed_count >= len(packages) // 2  # At least half should be installed

def check_airflow():
    """Check Apache Airflow installation"""
    print_header("APACHE AIRFLOW CHECK")
    
    # Check Airflow import
    airflow_ok = check_package_import('airflow', 'Apache Airflow')
    
    if airflow_ok:
        # Check Airflow CLI
        try:
            result = subprocess.run(['airflow', 'version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print_success("Airflow CLI working")
                print_info(f"Airflow version: {result.stdout.strip()}")
            else:
                print_warning("Airflow CLI not working properly")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print_warning("Airflow CLI not accessible")
    
    return airflow_ok

def check_gpu_support():
    """Check GPU support"""
    print_header("GPU SUPPORT CHECK")
    
    try:
        import torch
        
        # Check CUDA availability
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            current_device = torch.cuda.current_device()
            gpu_name = torch.cuda.get_device_name(current_device)
            
            print_success(f"CUDA available: YES")
            print_info(f"GPU count: {gpu_count}")
            print_info(f"Current GPU: {gpu_name}")
            print_info(f"CUDA version: {torch.version.cuda}")
            
            # Check GPU memory
            gpu_memory = torch.cuda.get_device_properties(current_device).total_memory
            gpu_memory_gb = gpu_memory / (1024**3)
            print_info(f"GPU memory: {gpu_memory_gb:.1f} GB")
            
            return True
        else:
            print_warning("CUDA not available - will use CPU")
            return False
    except ImportError:
        print_error("PyTorch not installed - cannot check GPU")
        return False

def check_project_structure():
    """Check project file structure"""
    print_header("PROJECT STRUCTURE CHECK")
    
    required_files = [
        'src/dataset_manager.py',
        'src/data_wrangling.py',
        'src/enhanced_bert_training.py',
        'config/dataset_config.json',
        'data/custom_dataset.csv',
        'requirements.txt',
        'README.md'
    ]
    
    optional_files = [
        'dags/enhanced_bert_fine_tuning_dag.py',
        'tests/test_setup.py',
        'demo_complete_pipeline.py',
        'setup_environment.sh'
    ]
    
    all_required = True
    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"Required: {file_path}")
        else:
            print_error(f"Missing required: {file_path}")
            all_required = False
    
    optional_count = 0
    for file_path in optional_files:
        if Path(file_path).exists():
            print_success(f"Optional: {file_path}")
            optional_count += 1
        else:
            print_warning(f"Missing optional: {file_path}")
    
    print_info(f"Optional files: {optional_count}/{len(optional_files)} present")
    return all_required

def check_project_imports():
    """Check if project modules can be imported"""
    print_header("PROJECT MODULES CHECK")
    
    # Add src to path
    sys.path.insert(0, str(Path(__file__).parent / 'src'))
    
    modules = [
        ('dataset_manager', 'Dataset Manager'),
        ('data_wrangling', 'Data Wrangling'),
        ('enhanced_bert_training', 'Enhanced BERT Training')
    ]
    
    all_ok = True
    for module, display in modules:
        try:
            importlib.import_module(module)
            print_success(f"{display}: Imported successfully")
        except ImportError as e:
            print_error(f"{display}: Import failed - {e}")
            all_ok = False
    
    return all_ok

def test_basic_functionality():
    """Test basic functionality"""
    print_header("BASIC FUNCTIONALITY TEST")
    
    try:
        # Test dataset manager
        sys.path.insert(0, str(Path(__file__).parent / 'src'))
        from dataset_manager import DatasetManager
        
        manager = DatasetManager()
        datasets = manager.config.list_available_datasets()
        print_success(f"Dataset manager works - {len(datasets)} datasets configured")
        
        # Test loading a small sample
        if 'custom' in datasets:
            try:
                df, config = manager.load_dataset('custom', limit_samples=5)
                print_success(f"Dataset loading works - loaded {len(df)} samples")
            except Exception as e:
                print_warning(f"Dataset loading issue: {e}")
        
        return True
    except Exception as e:
        print_error(f"Basic functionality test failed: {e}")
        return False

def main():
    """Run all environment checks"""
    print_header("BERT FINE-TUNING ENVIRONMENT CHECK")
    print_info("Checking environment setup for BERT fine-tuning with Apache Airflow")
    
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_environment),
        ("Core Packages", check_core_packages),
        ("Optional Packages", check_optional_packages),
        ("Apache Airflow", check_airflow),
        ("GPU Support", check_gpu_support),
        ("Project Structure", check_project_structure),
        ("Project Modules", check_project_imports),
        ("Basic Functionality", test_basic_functionality),
    ]
    
    results = {}
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print_error(f"Check '{check_name}' failed with error: {e}")
            results[check_name] = False
    
    # Summary
    print_header("ENVIRONMENT CHECK SUMMARY")
    
    passed = sum(results.values())
    total = len(results)
    
    for check_name, result in results.items():
        if result:
            print_success(f"{check_name}: PASSED")
        else:
            print_error(f"{check_name}: FAILED")
    
    print(f"\n{Colors.BOLD}Overall Result: {passed}/{total} checks passed{Colors.END}")
    
    if passed == total:
        print_success("🎉 Environment is fully configured and ready!")
    elif passed >= total * 0.8:
        print_warning("⚠️  Environment is mostly ready, minor issues detected")
    else:
        print_error("❌ Environment needs attention before proceeding")
    
    # Recommendations
    print_header("RECOMMENDATIONS")
    
    if not results.get("Virtual Environment", True):
        print_info("Consider setting up a virtual environment:")
        print_info("  python3 -m venv bert_airflow_env")
        print_info("  source bert_airflow_env/bin/activate")
    
    if not results.get("Core Packages", True):
        print_info("Install core packages:")
        print_info("  pip install -r requirements.txt")
    
    if not results.get("Apache Airflow", True):
        print_info("Install Apache Airflow:")
        print_info("  pip install apache-airflow==2.7.2")
    
    if not results.get("Project Structure", True):
        print_info("Ensure all project files are present")
        print_info("Check the repository structure in README.md")
    
    print_info("\nFor automated setup, run: ./setup_environment.sh")
    
    return passed >= total * 0.8

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
