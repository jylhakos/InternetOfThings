#!/usr/bin/env python3
"""
Test script to verify Dagster pipeline setup
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import dagster
        print(f"✓ Dagster imported successfully (version: {dagster.__version__})")
    except ImportError as e:
        print(f"✗ Failed to import Dagster: {e}")
        return False
    
    try:
        import torch
        print(f"✓ PyTorch imported successfully (version: {torch.__version__})")
    except ImportError as e:
        print(f"✗ Failed to import PyTorch: {e}")
        return False
    
    try:
        import transformers
        print(f"✓ Transformers imported successfully (version: {transformers.__version__})")
    except ImportError as e:
        print(f"✗ Failed to import Transformers: {e}")
        return False
    
    try:
        import pandas as pd
        print(f"✓ Pandas imported successfully (version: {pd.__version__})")
    except ImportError as e:
        print(f"✗ Failed to import Pandas: {e}")
        return False
    
    return True

def test_dagster_project():
    """Test if Dagster project can be loaded"""
    print("\nTesting Dagster project...")
    
    try:
        # Set environment variables
        os.environ['DAGSTER_HOME'] = os.path.join(os.getcwd(), 'dagster_home')
        os.environ['PYTHONPATH'] = os.getcwd()
        
        # Try to import the main definitions
        from dagster_project import defs
        print("✓ Dagster project definitions loaded successfully")
        
        # Check assets
        assets = defs.get_assets_defs()
        print(f"✓ Found {len(assets)} assets in the project")
        
        # Check jobs
        jobs = defs.get_job_defs()
        print(f"✓ Found {len(jobs)} jobs in the project")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to load Dagster project: {e}")
        return False

def test_workspace_yaml():
    """Test if workspace.yaml is valid"""
    print("\nTesting workspace configuration...")
    
    try:
        import yaml
        
        if os.path.exists('workspace.yaml'):
            with open('workspace.yaml', 'r') as f:
                workspace_config = yaml.safe_load(f)
            print("✓ workspace.yaml is valid YAML")
            print(f"✓ Workspace config: {workspace_config}")
            return True
        else:
            print("✗ workspace.yaml not found")
            return False
            
    except Exception as e:
        print(f"✗ Failed to load workspace.yaml: {e}")
        return False

def main():
    """Run all tests"""
    print("=== Dagster BERT Pipeline Test ===\n")
    
    tests = [
        test_imports,
        test_workspace_yaml,
        test_dagster_project
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append(False)
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("✓ All tests passed! Pipeline is ready.")
        return 0
    else:
        print("✗ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
