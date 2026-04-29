#!/usr/bin/env python3
"""
Dataset Manager for BERT Fine-tuning
Handles dataset fetching, preprocessing, and configuration for Apache Airflow BERT pipeline
"""

import os
import pandas as pd
import numpy as np
import json
import requests
import zipfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BERTDatasetConfig:
    """Configuration class for BERT dataset management"""
    
    def __init__(self, config_file: str = None):
        """Initialize dataset configuration"""
        self.config_file = config_file or "config/dataset_config.json"
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Load dataset configuration from JSON file"""
        default_config = {
            "datasets": {
                "imdb": {
                    "name": "IMDB Movie Reviews",
                    "url": "https://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz",
                    "type": "sentiment",
                    "classes": ["negative", "positive"],
                    "text_column": "review",
                    "label_column": "sentiment",
                    "max_samples": 10000,
                    "preprocessing": {
                        "remove_html": True,
                        "lowercase": True,
                        "remove_special_chars": False
                    }
                },
                "amazon_reviews": {
                    "name": "Amazon Product Reviews",
                    "url": "https://s3.amazonaws.com/amazon-reviews-pds/tsv/amazon_reviews_us_Electronics_v1_00.tsv.gz",
                    "type": "sentiment", 
                    "classes": [1, 2, 3, 4, 5],
                    "text_column": "review_body",
                    "label_column": "star_rating",
                    "max_samples": 50000,
                    "preprocessing": {
                        "remove_html": False,
                        "lowercase": True,
                        "min_length": 10
                    }
                },
                "custom": {
                    "name": "Custom Dataset",
                    "path": "data/custom_dataset.csv",
                    "type": "classification",
                    "text_column": "text",
                    "label_column": "label",
                    "max_samples": -1,
                    "preprocessing": {
                        "remove_html": False,
                        "lowercase": True
                    }
                }
            },
            "training": {
                "test_size": 0.2,
                "validation_size": 0.1,
                "random_state": 42,
                "stratify": True
            },
            "tokenization": {
                "max_length": 512,
                "padding": "max_length",
                "truncation": True,
                "return_tensors": "pt"
            },
            "data_paths": {
                "raw_data": "data/raw/",
                "processed_data": "data/processed/",
                "cache": "data/cache/"
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    default_config.update(loaded_config)
                    logger.info(f"Loaded configuration from {self.config_file}")
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}. Using defaults.")
        else:
            logger.info("Using default configuration")
            
        return default_config
    
    def save_config(self):
        """Save current configuration to file"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
        logger.info(f"Configuration saved to {self.config_file}")
    
    def get_dataset_config(self, dataset_name: str) -> Dict:
        """Get configuration for specific dataset"""
        return self.config["datasets"].get(dataset_name, {})
    
    def list_available_datasets(self) -> List[str]:
        """List all available dataset configurations"""
        return list(self.config["datasets"].keys())

class DatasetFetcher:
    """Handles downloading and caching of datasets"""
    
    def __init__(self, config: BERTDatasetConfig):
        self.config = config
        self.cache_dir = Path(config.config["data_paths"]["cache"])
        self.raw_data_dir = Path(config.config["data_paths"]["raw_data"])
        
        # Create directories
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
    
    def download_file(self, url: str, filename: str) -> str:
        """Download file with progress tracking"""
        filepath = self.cache_dir / filename
        
        if filepath.exists():
            logger.info(f"File {filename} already exists in cache")
            return str(filepath)
        
        logger.info(f"Downloading {filename} from {url}")
        
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\rDownload progress: {progress:.1f}%", end="", flush=True)
            
            print()  # New line after progress
            logger.info(f"Successfully downloaded {filename}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to download {filename}: {e}")
            raise
    
    def extract_archive(self, filepath: str, extract_to: str = None) -> str:
        """Extract compressed archives"""
        extract_to = extract_to or self.raw_data_dir
        
        logger.info(f"Extracting {filepath}")
        
        if filepath.endswith('.zip'):
            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
        elif filepath.endswith(('.tar.gz', '.tgz')):
            import tarfile
            with tarfile.open(filepath, 'r:gz') as tar_ref:
                tar_ref.extractall(extract_to)
        elif filepath.endswith('.gz') and not filepath.endswith('.tar.gz'):
            import gzip
            import shutil
            output_path = str(Path(extract_to) / Path(filepath).stem)
            with gzip.open(filepath, 'rb') as f_in:
                with open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            return output_path
        
        logger.info(f"Extraction complete")
        return str(extract_to)

class DataPreprocessor:
    """Handles data cleaning and preprocessing"""
    
    def __init__(self, config: BERTDatasetConfig):
        self.config = config
    
    def clean_text(self, text: str, preprocessing_config: Dict) -> str:
        """Apply text cleaning based on configuration"""
        if pd.isna(text):
            return ""
        
        text = str(text)
        
        # Remove HTML tags
        if preprocessing_config.get("remove_html", False):
            import re
            text = re.sub(r'<[^>]+>', '', text)
        
        # Convert to lowercase
        if preprocessing_config.get("lowercase", True):
            text = text.lower()
        
        # Remove special characters (optional)
        if preprocessing_config.get("remove_special_chars", False):
            import re
            text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def filter_data(self, df: pd.DataFrame, preprocessing_config: Dict) -> pd.DataFrame:
        """Filter data based on preprocessing configuration"""
        original_size = len(df)
        
        # Filter by minimum length
        if "min_length" in preprocessing_config:
            min_length = preprocessing_config["min_length"]
            text_col = preprocessing_config.get("text_column", "text")
            df = df[df[text_col].str.len() >= min_length]
            logger.info(f"Filtered by min_length {min_length}: {len(df)}/{original_size} samples")
        
        # Filter by maximum length
        if "max_length" in preprocessing_config:
            max_length = preprocessing_config["max_length"]
            text_col = preprocessing_config.get("text_column", "text")
            df = df[df[text_col].str.len() <= max_length]
            logger.info(f"Filtered by max_length {max_length}: {len(df)}/{original_size} samples")
        
        return df

class BERTDataset(Dataset):
    """Custom PyTorch Dataset for BERT"""
    
    def __init__(self, texts: List[str], labels: List[int], tokenizer: BertTokenizer, max_length: int = 512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        # Tokenize
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

class DatasetManager:
    """Main dataset management class"""
    
    def __init__(self, config_file: str = None):
        self.config = BERTDatasetConfig(config_file)
        self.fetcher = DatasetFetcher(self.config)
        self.preprocessor = DataPreprocessor(self.config)
        self.processed_data_dir = Path(self.config.config["data_paths"]["processed_data"])
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)
    
    def load_dataset(self, dataset_name: str, limit_samples: int = None) -> Tuple[pd.DataFrame, Dict]:
        """Load and preprocess dataset"""
        dataset_config = self.config.get_dataset_config(dataset_name)
        if not dataset_config:
            raise ValueError(f"Dataset '{dataset_name}' not found in configuration")
        
        logger.info(f"Loading dataset: {dataset_config['name']}")
        
        # Handle different dataset sources
        if dataset_name == "custom":
            df = self._load_custom_dataset(dataset_config)
        elif dataset_name == "imdb":
            df = self._load_imdb_dataset(dataset_config)
        elif dataset_name == "amazon_reviews":
            df = self._load_amazon_reviews(dataset_config)
        else:
            raise ValueError(f"Dataset loading not implemented for: {dataset_name}")
        
        # Apply preprocessing
        df = self._preprocess_dataset(df, dataset_config)
        
        # Limit samples if specified
        max_samples = limit_samples or dataset_config.get("max_samples", -1)
        if max_samples > 0 and len(df) > max_samples:
            df = df.sample(n=max_samples, random_state=self.config.config["training"]["random_state"])
            logger.info(f"Limited dataset to {max_samples} samples")
        
        logger.info(f"Dataset loaded: {len(df)} samples")
        return df, dataset_config
    
    def _load_custom_dataset(self, dataset_config: Dict) -> pd.DataFrame:
        """Load custom dataset from CSV"""
        data_path = dataset_config["path"]
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Custom dataset not found at: {data_path}")
        
        df = pd.read_csv(data_path)
        logger.info(f"Loaded custom dataset from {data_path}")
        return df
    
    def _load_imdb_dataset(self, dataset_config: Dict) -> pd.DataFrame:
        """Load IMDB dataset"""
        # For demonstration - you would implement actual IMDB loading here
        # This creates a sample dataset structure
        sample_data = {
            dataset_config["text_column"]: [
                "This movie was absolutely fantastic! Great acting and plot.",
                "Terrible movie, waste of time and money.",
                "Average film, nothing special but watchable.",
                "Outstanding performance by the lead actor!",
                "Boring and predictable storyline."
            ],
            dataset_config["label_column"]: [1, 0, 1, 1, 0]  # 1=positive, 0=negative
        }
        
        df = pd.DataFrame(sample_data)
        logger.info("Loaded IMDB sample dataset (replace with actual implementation)")
        return df
    
    def _load_amazon_reviews(self, dataset_config: Dict) -> pd.DataFrame:
        """Load Amazon reviews dataset"""
        # For demonstration - implement actual Amazon reviews loading
        sample_data = {
            dataset_config["text_column"]: [
                "Great product, works as expected!",
                "Poor quality, broke after one day.",
                "Good value for money.",
                "Excellent build quality and design.",
                "Not worth the price, disappointed."
            ],
            dataset_config["label_column"]: [5, 1, 4, 5, 2]  # Star ratings 1-5
        }
        
        df = pd.DataFrame(sample_data)
        logger.info("Loaded Amazon reviews sample dataset (replace with actual implementation)")
        return df
    
    def _preprocess_dataset(self, df: pd.DataFrame, dataset_config: Dict) -> pd.DataFrame:
        """Apply preprocessing to dataset"""
        preprocessing_config = dataset_config.get("preprocessing", {})
        text_column = dataset_config["text_column"]
        
        # Clean text
        logger.info("Applying text preprocessing...")
        df[text_column] = df[text_column].apply(
            lambda x: self.preprocessor.clean_text(x, preprocessing_config)
        )
        
        # Filter data
        df = self.preprocessor.filter_data(df, {**preprocessing_config, "text_column": text_column})
        
        # Remove empty texts
        df = df[df[text_column].str.len() > 0]
        
        return df
    
    def prepare_train_val_test(self, df: pd.DataFrame, dataset_config: Dict) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Split dataset into train, validation, and test sets"""
        training_config = self.config.config["training"]
        text_column = dataset_config["text_column"]
        label_column = dataset_config["label_column"]
        
        # Encode labels if necessary
        if df[label_column].dtype == 'object':
            le = LabelEncoder()
            df[label_column] = le.fit_transform(df[label_column])
            logger.info(f"Encoded labels: {list(le.classes_)}")
        
        # First split: train + val vs test
        test_size = training_config["test_size"]
        val_size = training_config["validation_size"]
        
        stratify = df[label_column] if training_config["stratify"] else None
        
        train_val_df, test_df = train_test_split(
            df,
            test_size=test_size,
            random_state=training_config["random_state"],
            stratify=stratify
        )
        
        # Second split: train vs val
        val_size_adjusted = val_size / (1 - test_size)  # Adjust for remaining data
        stratify_train_val = train_val_df[label_column] if training_config["stratify"] else None
        
        train_df, val_df = train_test_split(
            train_val_df,
            test_size=val_size_adjusted,
            random_state=training_config["random_state"],
            stratify=stratify_train_val
        )
        
        logger.info(f"Dataset split - Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
        
        return train_df, val_df, test_df
    
    def create_dataloaders(self, train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame, 
                          dataset_config: Dict, tokenizer: BertTokenizer, batch_size: int = 16) -> Tuple[DataLoader, DataLoader, DataLoader]:
        """Create PyTorch DataLoaders"""
        text_column = dataset_config["text_column"]
        label_column = dataset_config["label_column"]
        max_length = self.config.config["tokenization"]["max_length"]
        
        # Create datasets
        train_dataset = BERTDataset(
            train_df[text_column].tolist(),
            train_df[label_column].tolist(),
            tokenizer,
            max_length
        )
        
        val_dataset = BERTDataset(
            val_df[text_column].tolist(),
            val_df[label_column].tolist(),
            tokenizer,
            max_length
        )
        
        test_dataset = BERTDataset(
            test_df[text_column].tolist(),
            test_df[label_column].tolist(),
            tokenizer,
            max_length
        )
        
        # Create dataloaders
        train_dataloader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_dataloader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
        test_dataloader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
        
        logger.info(f"Created DataLoaders with batch_size={batch_size}")
        
        return train_dataloader, val_dataloader, test_dataloader
    
    def save_processed_data(self, train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame, dataset_name: str):
        """Save processed data to files"""
        output_dir = self.processed_data_dir / dataset_name
        output_dir.mkdir(exist_ok=True)
        
        train_df.to_csv(output_dir / "train.csv", index=False)
        val_df.to_csv(output_dir / "val.csv", index=False)
        test_df.to_csv(output_dir / "test.csv", index=False)
        
        logger.info(f"Saved processed data to {output_dir}")
    
    def load_processed_data(self, dataset_name: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Load previously processed data"""
        data_dir = self.processed_data_dir / dataset_name
        
        train_df = pd.read_csv(data_dir / "train.csv")
        val_df = pd.read_csv(data_dir / "val.csv") 
        test_df = pd.read_csv(data_dir / "test.csv")
        
        logger.info(f"Loaded processed data from {data_dir}")
        return train_df, val_df, test_df

# Example usage and demo functions
def demo_dataset_manager():
    """Demonstrate dataset manager functionality"""
    print("="*70)
    print("BERT DATASET MANAGER DEMO")
    print("="*70)
    
    # Initialize dataset manager
    manager = DatasetManager()
    
    # List available datasets
    print("\n📋 Available Datasets:")
    for dataset in manager.config.list_available_datasets():
        config = manager.config.get_dataset_config(dataset)
        print(f"  • {dataset}: {config.get('name', 'Unknown')}")
    
    # Load and process a dataset
    print("\n📊 Loading sample dataset...")
    df, dataset_config = manager.load_dataset("custom", limit_samples=100)
    
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    print(f"Sample data:")
    print(df.head())
    
    # Prepare train/val/test splits
    print("\n🔄 Preparing train/validation/test splits...")
    train_df, val_df, test_df = manager.prepare_train_val_test(df, dataset_config)
    
    # Save processed data
    print("\n💾 Saving processed data...")
    manager.save_processed_data(train_df, val_df, test_df, "custom")
    
    print("✅ Dataset management demo complete!")

if __name__ == "__main__":
    demo_dataset_manager()
