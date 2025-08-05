#!/usr/bin/env python3
"""
Testing Suite Overview
=====================

This directory contains all testing scripts for the BERT Fine-tuning Apache Airflow project.

Test Files:
-----------

1. test_setup.py
   - Quick dependency verification
   - Tests basic imports (PyTorch, Transformers, etc.)
   - Lightweight environment check
   - Usage: python tests/test_setup.py

2. simple_test.py
   - Basic BERT model loading test
   - Simple inference test
   - Quick functionality verification
   - Usage: python tests/simple_test.py

3. test_model.py
   - Comprehensive model evaluation suite
   - Performance metrics calculation
   - Advanced testing with confusion matrix
   - Usage: python tests/test_model.py

4. test_api.sh
   - Complete API endpoint testing
   - Tests all FastAPI routes
   - Automated curl-based testing
   - Usage: ./tests/test_api.sh

Testing Workflow:
-----------------

For quick verification:
    python tests/test_setup.py

For basic functionality:
    python tests/simple_test.py

For comprehensive model testing:
    python tests/test_model.py

For API testing (requires running server):
    python api.py &
    ./tests/test_api.sh

For environment verification:
    python src/test_environment.py

Integration Testing:
--------------------

The test suite integrates with Apache Airflow for automated testing:
- DAG testing through Airflow UI
- Automated pipeline validation
- CI/CD integration support

Dependencies:
-------------

All tests require the main project dependencies:
- torch
- transformers
- scikit-learn
- numpy
- pandas
- fastapi (for API tests)

For API tests specifically:
- curl
- jq (optional, for JSON formatting)
"""

if __name__ == "__main__":
    print(__doc__)
