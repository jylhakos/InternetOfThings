"""
Training script for RNN language models - simplified version.
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.train_clean import main

if __name__ == '__main__':
    main()
