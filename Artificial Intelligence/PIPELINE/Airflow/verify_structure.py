#!/usr/bin/env python3
"""
Project Structure Verification
==============================

This script verifies that all files are in their correct locations after reorganization.
"""

import os
import sys

def check_file_exists(filepath, description):
    """Check if a file exists and print status"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} (NOT FOUND)")
        return False

def main():
    print("🔍 Verifying Project Structure...")
    print("=" * 50)
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    all_good = True
    
    # Core source files
    print("\n📁 Core Source Files (src/):")
    all_good &= check_file_exists(os.path.join(base_path, "src", "bert_fine_tuning.py"), "Main fine-tuning script")
    all_good &= check_file_exists(os.path.join(base_path, "src", "minimal_bert.py"), "Minimal BERT implementation")
    all_good &= check_file_exists(os.path.join(base_path, "src", "test_environment.py"), "Environment testing")
    
    # Test files
    print("\n🧪 Test Files (tests/):")
    all_good &= check_file_exists(os.path.join(base_path, "tests", "test_setup.py"), "Setup verification")
    all_good &= check_file_exists(os.path.join(base_path, "tests", "simple_test.py"), "Basic functionality test")
    all_good &= check_file_exists(os.path.join(base_path, "tests", "test_model.py"), "Model evaluation suite")
    all_good &= check_file_exists(os.path.join(base_path, "tests", "test_api.sh"), "API testing script")
    all_good &= check_file_exists(os.path.join(base_path, "tests", "README.py"), "Test documentation")
    
    # Examples and documentation
    print("\n📚 Examples and Documentation (examples/):")
    all_good &= check_file_exists(os.path.join(base_path, "examples", "examples.py"), "Usage examples")
    all_good &= check_file_exists(os.path.join(base_path, "examples", "project_summary.py"), "Project summary")
    all_good &= check_file_exists(os.path.join(base_path, "examples", "README.py"), "Examples documentation")
    
    # Airflow DAGs
    print("\n🔄 Airflow DAGs (dags/):")
    all_good &= check_file_exists(os.path.join(base_path, "dags", "bert_fine_tuning_dag.py"), "Main ML pipeline DAG")
    
    # Infrastructure
    print("\n☁️ Infrastructure (terraform/, cloudformation/, scripts/):")
    all_good &= check_file_exists(os.path.join(base_path, "terraform", "variables.tf"), "Terraform variables")
    all_good &= check_file_exists(os.path.join(base_path, "scripts", "install-ollama.sh"), "Ollama installation script")
    
    # Main application files
    print("\n🚀 Main Application Files:")
    all_good &= check_file_exists(os.path.join(base_path, "api.py"), "FastAPI backend")
    all_good &= check_file_exists(os.path.join(base_path, "deploy.sh"), "Deployment script")
    all_good &= check_file_exists(os.path.join(base_path, "README.md"), "Main documentation")
    all_good &= check_file_exists(os.path.join(base_path, "requirements.txt"), "Python dependencies")
    all_good &= check_file_exists(os.path.join(base_path, "docker-compose.yml"), "Docker compose file")
    
    print("\n" + "=" * 50)
    if all_good:
        print("✅ All files are in their correct locations!")
        print("\n📋 Usage Instructions:")
        print("  Core development: src/")
        print("  Testing: tests/")
        print("  Examples: examples/")
        print("  Airflow: dags/")
        print("\n🚀 Quick commands:")
        print("  python tests/test_setup.py")
        print("  python src/test_environment.py")
        print("  python src/bert_fine_tuning.py")
        print("  ./tests/test_api.sh")
        print("  python examples/examples.py")
        return 0
    else:
        print("❌ Some files are missing or in wrong locations!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
