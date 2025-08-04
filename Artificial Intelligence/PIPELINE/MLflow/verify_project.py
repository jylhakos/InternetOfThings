#!/usr/bin/env python3
"""
Project verification script
This script verifies that all essential files are present and properly configured
for the PowerBI Fish Weight Prediction project.
"""

import os
import sys
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists and is not empty"""
    if os.path.exists(file_path):
        if os.path.getsize(file_path) > 0:
            print(f"✓ {description}: {file_path}")
            return True
        else:
            print(f"⚠ {description}: {file_path} (exists but empty)")
            return False
    else:
        print(f"❌ {description}: {file_path} (missing)")
        return False

def check_directory_exists(dir_path, description):
    """Check if a directory exists"""
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        print(f"✓ {description}: {dir_path}")
        return True
    else:
        print(f"❌ {description}: {dir_path} (missing)")
        return False

def main():
    """Main verification function"""
    print("PowerBI Fish Weight Prediction Project Verification")
    print("=" * 60)
    
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Track verification results
    all_checks_passed = True
    
    print("\n📋 Essential Files Check:")
    print("-" * 30)
    
    # Essential files to check
    essential_files = [
        ("requirements.txt", "Main requirements file"),
        ("setup.sh", "Setup script"),
        ("powerbi_integration.py", "PowerBI integration script"),
        ("scikit-learn/fish_predictive_model.py", "Fish prediction model"),
        ("Apache Airflow/fish_prediction_dag.py", "Airflow DAG"),
        ("Apache Airflow/requirements.txt", "Airflow requirements"),
        ("scikit-learn/requirements.txt", "Scikit-learn requirements"),
        (".gitignore", "Git ignore file"),
    ]
    
    for file_path, description in essential_files:
        if not check_file_exists(file_path, description):
            all_checks_passed = False
    
    print("\n📁 Directory Structure Check:")
    print("-" * 35)
    
    # Essential directories
    essential_directories = [
        ("data", "Data directory"),
        ("scikit-learn", "Scikit-learn directory"),
        ("Apache Airflow", "Apache Airflow directory"),
        ("notebooks", "Notebooks directory"),
    ]
    
    for dir_path, description in essential_directories:
        if not check_directory_exists(dir_path, description):
            all_checks_passed = False
    
    print("
📊 Data Files Check:")
    print("-" * 25)
    
    # Data files
    data_files = [
        ("data/Fish.csv", "Fish dataset in data directory"),
        ("Dataset/Fish.csv", "Fish dataset in Dataset directory"),
    ]
    
    data_found = False
    for file_path, description in data_files:
        if check_file_exists(file_path, description):
            data_found = True
    
    if not data_found:
        print("⚠ Warning: No Fish.csv found in data/ or Dataset/ directories")
        all_checks_passed = False
    
    print("
🔧 Configuration Check:")
    print("-" * 28)
    
    # Check if setup script is executable
    setup_script = "setup.sh"
    if os.path.exists(setup_script):
        if os.access(setup_script, os.X_OK):
            print(f"✓ Setup script is executable: {setup_script}")
        else:
            print(f"⚠ Setup script not executable: {setup_script}")
            print("  Run: chmod +x setup.sh")
    
    # Check for environment file
    if os.path.exists(".env"):
        print("✓ Environment file found: .env")
    else:
        print("ℹ Environment file not found: .env (will be created by setup.sh)")
    
    print("
🐍 Python Dependencies Check:")
    print("-" * 35)
    
    # Try importing key packages
    packages_to_check = [
        "pandas", "numpy", "sklearn", "matplotlib", "seaborn"
    ]
    
    missing_packages = []
    for package in packages_to_check:
        try:
            __import__(package)
            print(f"✓ {package} is available")
        except ImportError:
            print(f"❌ {package} not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"
⚠ Missing packages: {', '.join(missing_packages)}")
        print("  Run setup.sh to install dependencies")
        all_checks_passed = False
    
    print("
" + "=" * 60)
    
    if all_checks_passed:
        print("🎉 All essential files and configurations are present!")
        print("
📋 Next Steps:")
        print("1. Run: ./setup.sh (to set up environment)")
        print("2. Run: source venv/bin/activate (to activate environment)")
        print("3. Run: python scikit-learn/fish_predictive_model.py (to train model)")
        print("4. Run: python powerbi_integration.py (to prepare PowerBI data)")
        print("5. Set up Airflow DAG in Apache Airflow directory")
    else:
        print("❌ Some essential files or configurations are missing!")
        print("
🔧 Recommended Actions:")
        print("1. Ensure all required files are present")
        print("2. Run setup.sh to create missing directories and files")
        print("3. Check that Fish.csv dataset is available")
        print("4. Install missing Python packages")
        
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

import os
import sys
import csv

def check_project_structure():
    """Check if the project structure is correctly set up."""
    print("🔍 Checking Project Structure...")
    
    required_files = [
        'Dataset/Fish.csv',
        'requirements.txt',
        'setup.sh',
        'README.md',
        'scikit-learn/fish_predictive_model.py',
        'powerbi_integration.py',
        'Apache Airflow/fish_prediction_dag.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")
    
    if missing_files:
        print(f"  ❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("  🎉 All required files present!")
    return True

def check_fish_dataset():
    """Verify the Fish.csv dataset is properly formatted."""
    print("\n🐟 Checking Fish Dataset...")
    
    try:
        with open('Dataset/Fish.csv', 'r') as f:
            reader = csv.DictReader(f)
            
            # Check headers
            expected_headers = ['Species', 'Weight', 'Length1', 'Length2', 'Length3', 'Height', 'Width']
            if list(reader.fieldnames) != expected_headers:
                print(f"  ❌ Incorrect headers. Expected: {expected_headers}")
                print(f"     Found: {list(reader.fieldnames)}")
                return False
            
            # Count rows and check data
            rows = list(reader)
            row_count = len(rows)
            
            if row_count == 0:
                print("  ❌ Dataset is empty")
                return False
            
            # Check for species variety
            species = set(row['Species'] for row in rows)
            
            print(f"  ✅ Dataset loaded: {row_count} records")
            print(f"  ✅ Species found: {len(species)} types")
            print(f"     Species: {', '.join(sorted(species))}")
            
            # Sample data validation
            sample_row = rows[0]
            try:
                weight = float(sample_row['Weight'])
                length1 = float(sample_row['Length1'])
                print(f"  ✅ Sample data validation passed")
                print(f"     First fish: {sample_row['Species']}, Weight: {weight}g, Length1: {length1}cm")
            except ValueError as e:
                print(f"  ❌ Data format error: {e}")
                return False
            
            return True
            
    except FileNotFoundError:
        print("  ❌ Fish.csv not found in Dataset/ directory")
        return False
    except Exception as e:
        print(f"  ❌ Error reading dataset: {e}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    print("\n🐍 Checking Python Version...")
    
    version = sys.version_info
    print(f"  Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("  ❌ Python 3.8+ required")
        return False
    
    print("  ✅ Python version is compatible")
    return True

def check_directory_permissions():
    """Check if we have write permissions for necessary directories."""
    print("\n📁 Checking Directory Permissions...")
    
    test_dirs = ['.', 'models', 'output', 'data']
    
    for dirname in test_dirs:
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname, exist_ok=True)
                print(f"  ✅ Created directory: {dirname}")
            except PermissionError:
                print(f"  ❌ Cannot create directory: {dirname}")
                return False
        
        # Test write permission
        try:
            test_file = os.path.join(dirname, '.test_write')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print(f"  ✅ Write permission: {dirname}")
        except PermissionError:
            print(f"  ❌ No write permission: {dirname}")
            return False
    
    return True

def check_environment_setup():
    """Check if virtual environment is set up correctly."""
    print("\n🌐 Checking Environment Setup...")
    
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if in_venv:
        print(f"  ✅ Virtual environment active: {sys.prefix}")
    else:
        print("  ⚠️  Not in virtual environment (run: source activate_env.sh)")
    
    # Check if activate script exists
    if os.path.exists('activate_env.sh'):
        print("  ✅ Activation script found: activate_env.sh")
    else:
        print("  ⚠️  Activation script not found (run: ./setup.sh)")
    
    # Check if virtual environment directory exists
    if os.path.exists('fish_analysis_env'):
        print("  ✅ Virtual environment directory found")
    else:
        print("  ⚠️  Virtual environment not created (run: ./setup.sh)")
    
    return True

def test_basic_imports():
    """Test if basic Python packages can be imported."""
    print("\n📦 Testing Basic Imports...")
    
    basic_packages = ['csv', 'os', 'sys', 'json']
    
    for package in basic_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            return False
    
    # Test optional ML packages
    ml_packages = {
        'pandas': 'pandas',
        'numpy': 'numpy', 
        'sklearn': 'scikit-learn',
        'matplotlib': 'matplotlib',
        'joblib': 'joblib'
    }
    
    print("\n📊 Testing ML Package Imports (may fail if environment not set up)...")
    
    for package, install_name in ml_packages.items():
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ⚠️  {package} (install with: pip install {install_name})")
    
    return True

def generate_simple_report():
    """Generate a simple analysis report using basic Python."""
    print("\n📊 Generating Simple Dataset Report...")
    
    try:
        with open('Dataset/Fish.csv', 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # Basic statistics
        species_count = {}
        weights = []
        
        for row in rows:
            species = row['Species']
            weight = float(row['Weight'])
            
            species_count[species] = species_count.get(species, 0) + 1
            weights.append(weight)
        
        # Calculate basic stats
        total_fish = len(weights)
        avg_weight = sum(weights) / len(weights)
        min_weight = min(weights)
        max_weight = max(weights)
        
        print(f"\n📈 Dataset Summary:")
        print(f"  Total Fish: {total_fish}")
        print(f"  Species Count: {len(species_count)}")
        print(f"  Average Weight: {avg_weight:.2f}g")
        print(f"  Weight Range: {min_weight}g - {max_weight}g")
        
        print(f"\n🐟 Fish by Species:")
        for species, count in sorted(species_count.items()):
            print(f"  {species}: {count} fish")
        
        # Save basic report
        with open('basic_dataset_report.txt', 'w') as f:
            f.write("Fish Weight Prediction Dataset - Basic Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Total Fish: {total_fish}\n")
            f.write(f"Species Count: {len(species_count)}\n")
            f.write(f"Average Weight: {avg_weight:.2f}g\n")
            f.write(f"Weight Range: {min_weight}g - {max_weight}g\n\n")
            f.write("Fish by Species:\n")
            for species, count in sorted(species_count.items()):
                f.write(f"  {species}: {count} fish\n")
        
        print(f"  ✅ Basic report saved: basic_dataset_report.txt")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error generating report: {e}")
        return False

def main():
    """Run all verification checks."""
    print("🔬 Fish Weight Prediction Project - Verification Script")
    print("=" * 60)
    
    checks = [
        ("Project Structure", check_project_structure),
        ("Python Version", check_python_version),
        ("Fish Dataset", check_fish_dataset),
        ("Directory Permissions", check_directory_permissions),
        ("Environment Setup", check_environment_setup),
        ("Basic Imports", test_basic_imports),
        ("Simple Report", generate_simple_report)
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        try:
            if check_func():
                passed += 1
        except Exception as e:
            print(f"  ❌ {check_name} failed with error: {e}")
    
    print("\n" + "=" * 60)
    print(f"🎯 Verification Complete: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All checks passed! Your project is ready to go!")
        print("\nNext steps:")
        print("1. Run: source activate_env.sh (to activate environment)")
        print("2. Run: python scikit-learn/fish_predictive_model.py (full analysis)")
        print("3. Run: python powerbi_integration.py (prepare Power BI data)")
    elif passed >= total - 2:
        print("✅ Most checks passed! Minor issues may need attention.")
        print("🔧 Run ./setup.sh to complete environment setup.")
    else:
        print("⚠️  Several issues found. Please review the output above.")
        print("🔧 Run ./setup.sh to set up the project properly.")
    
    return passed == total

if __name__ == "__main__":
    main()
