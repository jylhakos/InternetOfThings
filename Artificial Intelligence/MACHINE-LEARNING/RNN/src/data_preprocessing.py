"""
Data preprocessing utilities for WikiText dataset.
"""

import torch
from torch.utils.data import Dataset, DataLoader
from datasets import load_dataset
from collections import Counter
import re
import pickle
import os


class Vocabulary:
    """
    Vocabulary class for handling word-to-index mappings.
    """
    
    def __init__(self):
        self.token2idx = {}
        self.idx2token = {}
        self.token_counts = Counter()
        
        # Special tokens
        self.pad_token = '<pad>'
        self.unk_token = '<unk>'
        self.eos_token = '<eos>'
        self.bos_token = '<bos>'
        
        # Add special tokens
        self._add_token(self.pad_token)
        self._add_token(self.unk_token) 
        self._add_token(self.eos_token)
        self._add_token(self.bos_token)
        
    def _add_token(self, token):
        """Add a single token to vocabulary."""
        if token not in self.token2idx:
            idx = len(self.token2idx)
            self.token2idx[token] = idx
            self.idx2token[idx] = token
    
    def build_from_text(self, texts, min_freq=2, max_vocab_size=None):
        """
        Build vocabulary from a list of texts.
        
        Args:
            texts (list): List of text strings
            min_freq (int): Minimum frequency for a word to be included
            max_vocab_size (int): Maximum vocabulary size
        """
        # Count all tokens
        for text in texts:
            tokens = self.tokenize(text)
            self.token_counts.update(tokens)
        
        # Filter by frequency and sort by count
        valid_tokens = [token for token, count in self.token_counts.items() 
                       if count >= min_freq]
        
        # Sort by frequency (descending)
        valid_tokens.sort(key=lambda x: self.token_counts[x], reverse=True)
        
        # Limit vocabulary size
        if max_vocab_size:
            valid_tokens = valid_tokens[:max_vocab_size - len(self.token2idx)]
        
        # Add tokens to vocabulary
        for token in valid_tokens:
            self._add_token(token)
    
    def tokenize(self, text):
        """
        Simple tokenization function.
        
        Args:
            text (str): Input text
            
        Returns:
            list: List of tokens
        """
        # Basic preprocessing
        text = text.lower().strip()
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Split on whitespace and punctuation
        tokens = re.findall(r'\b\w+\b|[^\w\s]', text)
        
        return tokens
    
    def encode(self, text):
        """
        Convert text to indices.
        
        Args:
            text (str): Input text
            
        Returns:
            list: List of token indices
        """
        tokens = self.tokenize(text)
        return [self.token2idx.get(token, self.token2idx[self.unk_token]) 
                for token in tokens]
    
    def decode(self, indices):
        """
        Convert indices back to text.
        
        Args:
            indices (list): List of token indices
            
        Returns:
            str: Decoded text
        """
        tokens = [self.idx2token[idx] for idx in indices 
                 if idx in self.idx2token]
        return ' '.join(tokens)
    
    def __len__(self):
        return len(self.token2idx)
    
    def __getitem__(self, token):
        return self.token2idx.get(token, self.token2idx[self.unk_token])
    
    def save(self, filepath):
        """Save vocabulary to file."""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'token2idx': self.token2idx,
                'idx2token': self.idx2token,
                'token_counts': self.token_counts
            }, f)
    
    def load(self, filepath):
        """Load vocabulary from file."""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.token2idx = data['token2idx']
            self.idx2token = data['idx2token']
            self.token_counts = data['token_counts']


class WikiTextDataset(Dataset):
    """
    WikiText dataset for language modeling.
    """
    
    def __init__(self, data, vocab, seq_length=128, stride=64):
        """
        Args:
            data (list): List of text strings
            vocab (Vocabulary): Vocabulary object
            seq_length (int): Length of each sequence
            stride (int): Stride for sequence extraction
        """
        self.vocab = vocab
        self.seq_length = seq_length
        self.stride = stride
        
        # Encode all texts and concatenate
        self.tokens = []
        for text in data:
            if text.strip():  # Skip empty texts
                encoded = vocab.encode(text)
                if encoded:  # Skip if encoding results in empty list
                    self.tokens.extend(encoded)
                    self.tokens.append(vocab.token2idx[vocab.eos_token])
        
        # Create sequences
        self.sequences = []
        for i in range(0, len(self.tokens) - seq_length, stride):
            self.sequences.append(self.tokens[i:i + seq_length + 1])
    
    def __len__(self):
        return len(self.sequences)
    
    def __getitem__(self, idx):
        sequence = self.sequences[idx]
        input_seq = torch.tensor(sequence[:-1], dtype=torch.long)
        target_seq = torch.tensor(sequence[1:], dtype=torch.long)
        return input_seq, target_seq


def load_wikitext_data(dataset_name="wikitext-2-v1", cache_dir=None):
    """
    Load WikiText dataset from HuggingFace.
    
    Args:
        dataset_name (str): Name of the WikiText dataset
        cache_dir (str): Directory to cache the dataset
        
    Returns:
        dict: Dictionary containing train, validation, and test data
    """
    try:
        # Load dataset from HuggingFace
        dataset = load_dataset("wikitext", dataset_name, cache_dir=cache_dir)
        
        return {
            'train': [item['text'] for item in dataset['train'] if item['text'].strip()],
            'validation': [item['text'] for item in dataset['validation'] if item['text'].strip()],
            'test': [item['text'] for item in dataset['test'] if item['text'].strip()]
        }
    except Exception as e:
        print(f"Error loading dataset: {e}")
        print("Using dummy data for demonstration...")
        
        # Dummy data for testing
        dummy_texts = [
            "The quick brown fox jumps over the lazy dog.",
            "Machine learning is a subset of artificial intelligence.",
            "Natural language processing involves computational linguistics.",
            "Deep learning models can process sequential data effectively.",
            "Recurrent neural networks are designed for sequence modeling."
        ] * 100  # Repeat to have enough data
        
        return {
            'train': dummy_texts[:400],
            'validation': dummy_texts[400:450], 
            'test': dummy_texts[450:500]
        }


def create_data_loaders(data_dict, vocab, batch_size=32, seq_length=128, 
                       stride=64, num_workers=0):
    """
    Create DataLoaders for train, validation, and test sets.
    
    Args:
        data_dict (dict): Dictionary with train/validation/test data
        vocab (Vocabulary): Vocabulary object
        batch_size (int): Batch size
        seq_length (int): Sequence length
        stride (int): Stride for sequence extraction
        num_workers (int): Number of worker processes
        
    Returns:
        dict: Dictionary with DataLoaders
    """
    data_loaders = {}
    
    for split, data in data_dict.items():
        dataset = WikiTextDataset(data, vocab, seq_length, stride)
        
        # Shuffle only training data
        shuffle = (split == 'train')
        
        data_loader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            num_workers=num_workers,
            pin_memory=torch.cuda.is_available(),
            drop_last=True  # Ensure consistent batch sizes
        )
        
        data_loaders[split] = data_loader
    
    return data_loaders


def preprocess_wikitext(dataset_name="wikitext-2-v1", vocab_size=10000, 
                       min_freq=2, seq_length=128, batch_size=32, 
                       cache_dir="./data", save_vocab=True):
    """
    Complete preprocessing pipeline for WikiText dataset.
    
    Args:
        dataset_name (str): Name of WikiText dataset
        vocab_size (int): Maximum vocabulary size
        min_freq (int): Minimum token frequency
        seq_length (int): Sequence length
        batch_size (int): Batch size
        cache_dir (str): Cache directory
        save_vocab (bool): Whether to save vocabulary
        
    Returns:
        tuple: (data_loaders, vocabulary)
    """
    print("Loading WikiText dataset...")
    data_dict = load_wikitext_data(dataset_name, cache_dir)
    
    print(f"Train samples: {len(data_dict['train'])}")
    print(f"Validation samples: {len(data_dict['validation'])}")
    print(f"Test samples: {len(data_dict['test'])}")
    
    # Build vocabulary
    print("Building vocabulary...")
    vocab = Vocabulary()
    vocab.build_from_text(data_dict['train'], min_freq, vocab_size)
    
    print(f"Vocabulary size: {len(vocab)}")
    
    # Save vocabulary if requested
    if save_vocab:
        os.makedirs(cache_dir, exist_ok=True)
        vocab_path = os.path.join(cache_dir, 'vocab.pkl')
        vocab.save(vocab_path)
        print(f"Vocabulary saved to {vocab_path}")
    
    # Create data loaders
    print("Creating data loaders...")
    data_loaders = create_data_loaders(
        data_dict, vocab, batch_size, seq_length
    )
    
    # Print data loader information
    for split, loader in data_loaders.items():
        print(f"{split.capitalize()} batches: {len(loader)}")
    
    return data_loaders, vocab


if __name__ == "__main__":
    # Example usage
    data_loaders, vocab = preprocess_wikitext(
        dataset_name="wikitext-2-v1",
        vocab_size=5000,
        seq_length=64,
        batch_size=16
    )
    
    # Test the data loader
    train_loader = data_loaders['train']
    batch = next(iter(train_loader))
    input_seq, target_seq = batch
    
    print(f"Input sequence shape: {input_seq.shape}")
    print(f"Target sequence shape: {target_seq.shape}")
    
    # Decode a sample
    sample_text = vocab.decode(input_seq[0].tolist())
    print(f"Sample text: {sample_text}")
