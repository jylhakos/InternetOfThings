#!/bin/bash

# Dataset Download Script for Feature Learning Project: downloads all the datasets used in the project

set -e  # Exit on any error

echo "Downloading datasets for Feature Learning project..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_dataset() {
    echo -e "${BLUE}[DATASET]${NC} $1"
}

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    print_warning "Virtual environment not activated. Activating..."
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        print_error "Virtual environment not found. Please run setup_environment.sh first."
        exit 1
    fi
fi

# Create datasets directory
mkdir -p datasets
cd datasets

# Download script using Python
cat > download_datasets.py << 'EOF'
"""
Script to download all datasets for the Feature Learning project.
"""
import os
from datasets import load_dataset
import sys

def download_with_progress(dataset_name, config_name=None, split=None):
    """Download dataset with progress information."""
    try:
        print(f"Downloading {dataset_name}...")
        if config_name:
            if split:
                dataset = load_dataset(dataset_name, config_name, split=split)
            else:
                dataset = load_dataset(dataset_name, config_name)
        else:
            if split:
                dataset = load_dataset(dataset_name, split=split)
            else:
                dataset = load_dataset(dataset_name)
        
        print(f"✓ Successfully downloaded {dataset_name}")
        if hasattr(dataset, 'num_rows'):
            print(f"  Samples: {dataset.num_rows:,}")
        elif isinstance(dataset, dict):
            for split_name, split_data in dataset.items():
                print(f"  {split_name}: {len(split_data):,} samples")
        
        return dataset
    except Exception as e:
        print(f"✗ Failed to download {dataset_name}: {str(e)}")
        return None

def main():
    """Download all datasets."""
    print("Starting dataset download process...")
    
    datasets_info = [
        ("MNIST", "ylecun/mnist", None, None),
        ("Fashion-MNIST", "fashion_mnist", None, None),
        ("WikiText-2", "wikitext", "wikitext-2-raw-v1", None),
        ("SQuAD v1.1", "squad", None, None),
        ("SQuAD v2.0", "squad_v2", None, None),
    ]
    
    successful_downloads = 0
    total_datasets = len(datasets_info)
    
    for name, dataset_id, config, split in datasets_info:
        print(f"\n{'='*50}")
        print(f"Downloading {name}...")
        print(f"{'='*50}")
        
        dataset = download_with_progress(dataset_id, config, split)
        if dataset is not None:
            successful_downloads += 1
        
        # Add a small delay between downloads
        import time
        time.sleep(1)
    
    print(f"\n{'='*60}")
    print(f"Dataset download summary:")
    print(f"Successfully downloaded: {successful_downloads}/{total_datasets}")
    print(f"{'='*60}")
    
    if successful_downloads == total_datasets:
        print("The datasets downloaded successfully.")
        return 0
    else:
        print(f"⚠️  {total_datasets - successful_downloads} datasets failed to download")
        return 1

if __name__ == "__main__":
    sys.exit(main())
EOF

print_status "Starting dataset downloads..."

# Run the Python download script
python download_datasets.py

# Check if downloads were successful
if [ $? -eq 0 ]; then
    print_status "The datasets downloaded successfully."
else
    print_warning "Some datasets may have failed to download. Check the output above."
fi

# Clean up the download script
rm download_datasets.py

# Return to the project root
cd ..

# Create a simple verification script
cat > verify_datasets.py << 'EOF'
"""
Verify that all datasets are available and accessible.
"""
from datasets import load_dataset
import sys

def verify_dataset(name, dataset_id, config=None):
    """Verify that a dataset can be loaded."""
    try:
        print(f"Verifying {name}...")
        if config:
            dataset = load_dataset(dataset_id, config)
        else:
            dataset = load_dataset(dataset_id)
        
        print(f"✓ {name} is available")
        return True
    except Exception as e:
        print(f"✗ {name} verification failed: {str(e)}")
        return False

def main():
    """Verify all datasets."""
    datasets_to_verify = [
        ("MNIST", "ylecun/mnist", None),
        ("Fashion-MNIST", "fashion_mnist", None),
        ("WikiText-2", "wikitext", "wikitext-2-raw-v1"),
        ("SQuAD v1.1", "squad", None),
        ("SQuAD v2.0", "squad_v2", None),
    ]
    
    verified = 0
    total = len(datasets_to_verify)
    
    for name, dataset_id, config in datasets_to_verify:
        if verify_dataset(name, dataset_id, config):
            verified += 1
    
    print(f"\nVerification complete: {verified}/{total} datasets verified")
    
    if verified == total:
        print("The datasets verified successfully!")
        return 0
    else:
        print("⚠️  Some datasets could not be verified")
        return 1

if __name__ == "__main__":
    sys.exit(main())
EOF

print_status "Verifying dataset accessibility..."
python verify_datasets.py

# Clean up verification script
rm verify_datasets.py

echo ""
print_status "Dataset download and verification completed!"
echo "Next steps:"
echo "1. Start training models: bash scripts/run_experiments.sh"
echo "2. Or run individual training scripts from the src/training/ directory"
