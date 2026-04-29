#!/usr/bin/env python3
"""
Quick setup verification script for n8n + Ollama project.
Run: python check_setup.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from helpers import print_status_report
    print_status_report()
except ImportError as e:
    print(f"❌ Error importing helpers: {e}")
    print("\nMake sure you have activated the virtual environment:")
    print("  source venv/bin/activate")
    print("\nand installed dependencies:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
