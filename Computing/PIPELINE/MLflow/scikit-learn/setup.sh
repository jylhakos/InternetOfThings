#!/bin/bash

# Fish ML setup script
# ============================
# This script demonstrates how to set up the Python environment
# and run the machine learning examples.

echo "🐟 Fish Machine Learning (ML) setup"
echo "======================================"

# Check if we're in the right directory
if [ ! -f "Dataset/Fish.csv" ]; then
    echo "❌ Error: Fish.csv not found in Dataset/ folder"
    echo "Please ensure you're in the project root directory"
    exit 1
fi

echo " Dataset found: Dataset/Fish.csv"

# Create virtual environment
echo ""
echo " Creating Python virtual environment..."
python3 -m venv venv

if [ $? -eq 0 ]; then
    echo "Virtual environment created successfully"
else
    echo "❌ Failed to create virtual environment"
    echo "Please ensure Python 3 is installed"
    exit 1
fi

# Activate virtual environment
echo ""
echo " Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install required packages
echo ""
echo "Installing required packages..."
echo "This may take a few minutes..."

pip install scikit-learn pandas numpy matplotlib seaborn jupyter

if [ $? -eq 0 ]; then
    echo "All packages installed successfully"
else
    echo "❌ Failed to install some packages"
    echo "You may need to install them manually"
fi

# Verify installation
echo ""
echo "Verifying installation..."
python3 -c "
import pandas as pd
import numpy as np
import sklearn
import matplotlib.pyplot as plt
print('pandas version:', pd.__version__)
print('numpy version:', np.__version__)
print('scikit-learn version:', sklearn.__version__)
print('Libraries imported successfully!')
"

echo ""
echo " Setup completed. What you can do next?"
echo ""
echo "1. Run regression analysis:"
echo "   python fish_regression.py"
echo ""
echo "2. Run classification analysis:"
echo "   python fish_classification.py"
echo ""
echo "3. Run comprehensive analysis:"
echo "   python fish_analysis.py"
echo ""
echo "4. Start Jupyter notebook for interactive analysis:"
echo "   jupyter notebook"
echo ""
echo "  Don't forget to activate your virtual environment each time:"
echo "   source venv/bin/activate"
echo ""
