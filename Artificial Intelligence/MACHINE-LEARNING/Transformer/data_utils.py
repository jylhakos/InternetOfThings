import torch
from torch.utils.data import Dataset, DataLoader
from datasets import load_dataset
import re
from collections import Counter
import pickle
import os


class Vocabulary:
    """
    Vocabulary class for managing word-to-index and index-to-word mappings.
    """
    def __init__(self):
        self.word2idx = {}
        self.idx2word = {}
        self.word_counts = Counter()
        self.idx = 0
        
        # Add special tokens
        self.add_word('<pad>')  # Padding token
        self.add_word('<unk>')  # Unknown token
        self.add_word('<sos>')  # Start of sequence
        self.add_word('<eos>')  # End of sequence
        
    def add_word(self, word):
        if word not in self.word2idx:
            self.word2idx[word] = self.idx
            self.idx2word[self.idx] = word
            self.idx += 1
        self.word_counts[word] += 1
        
    def __len__(self):
        return len(self.word2idx)
    
    def __call__(self, word):
        return self.word2idx.get(word, self.word2idx['<unk>'])
    
    def decode(self, idx):
        return self.idx2word.get(idx, '<unk>')
    
    def build_vocab_from_texts(self, texts, min_freq=2):
        """Build vocabulary from a list of texts."""
        # Count all words
        for text in texts:
            words = self.tokenize(text)
            for word in words:
                self.word_counts[word] += 1
        
        # Add words that meet minimum frequency requirement
        for word, count in self.word_counts.items():
            if count >= min_freq and word not in self.word2idx:
                self.add_word(word)
    
    @staticmethod
    def tokenize(text):
        """Simple tokenization - split on whitespace and punctuation."""
        # Convert to lowercase and split on whitespace
        text = text.lower()
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        # Split on whitespace
        tokens = text.strip().split()
        return tokens
    
    def save(self, path):
        """Save vocabulary to file."""
        with open(path, 'wb') as f:
            pickle.dump({
                'word2idx': self.word2idx,
                'idx2word': self.idx2word,
                'word_counts': self.word_counts,
                'idx': self.idx
            }, f)
    
    def load(self, path):
        """Load vocabulary from file."""
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.word2idx = data['word2idx']
            self.idx2word = data['idx2word']
            self.word_counts = data['word_counts']
            self.idx = data['idx']


class WikiTextDataset(Dataset):
    """
    PyTorch Dataset for WikiText data.
    """
    def __init__(self, texts, vocab, seq_length=128):
        self.texts = texts
        self.vocab = vocab
        self.seq_length = seq_length
        self.data = self.prepare_data()
    
    def prepare_data(self):
        """Convert texts to token sequences."""
        all_tokens = []
        
        for text in self.texts:
            if text.strip():  # Skip empty lines
                tokens = self.vocab.tokenize(text)
                # Convert to indices
                token_ids = [self.vocab(token) for token in tokens]
                all_tokens.extend(token_ids)
        
        # Create sequences of fixed length
        sequences = []
        for i in range(0, len(all_tokens) - self.seq_length, self.seq_length):
            sequences.append(all_tokens[i:i + self.seq_length + 1])  # +1 for target
        
        return sequences
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        sequence = self.data[idx]
        input_seq = torch.tensor(sequence[:-1], dtype=torch.long)  # All but last
        target_seq = torch.tensor(sequence[1:], dtype=torch.long)  # All but first
        return input_seq, target_seq


def load_wikitext_dataset(config='wikitext-2-raw-v1', cache_dir='./data_cache'):
    """
    Load WikiText dataset using Hugging Face datasets.
    
    Args:
        config: Dataset configuration ('wikitext-2-raw-v1' or 'wikitext-103-raw-v1')
        cache_dir: Directory to cache dataset
    
    Returns:
        Dictionary with train, validation, and test splits
    """
    print(f"Loading {config} dataset...")
    
    # Create cache directory if it doesn't exist
    os.makedirs(cache_dir, exist_ok=True)
    
    # Load dataset
    try:
        dataset = load_dataset("wikitext", config, cache_dir=cache_dir)
        
        # Extract text data
        data = {
            'train': [item['text'] for item in dataset['train'] if item['text'].strip()],
            'validation': [item['text'] for item in dataset['validation'] if item['text'].strip()],
            'test': [item['text'] for item in dataset['test'] if item['text'].strip()]
        }
        
        print(f"Dataset loaded successfully!")
        print(f"Train samples: {len(data['train'])}")
        print(f"Validation samples: {len(data['validation'])}")
        print(f"Test samples: {len(data['test'])}")
        
        return data
        
    except Exception as e:
        print(f"Error loading dataset: {e}")
        print("Creating dummy dataset for demonstration...")
        
        # Create dummy data if loading fails
        dummy_texts = [
            "The quick brown fox jumps over the lazy dog.",
            "Machine learning is a subset of artificial intelligence.",
            "Transformers have revolutionized natural language processing.",
            "Recurrent neural networks process sequential data effectively.",
            "PyTorch is a popular deep learning framework.",
            "Attention mechanisms allow models to focus on relevant information.",
            "Language models can generate coherent text sequences.",
            "Deep learning has achieved remarkable success in various domains."
        ] * 100  # Repeat to create more training data
        
        return {
            'train': dummy_texts[:600],
            'validation': dummy_texts[600:700],
            'test': dummy_texts[700:800]
        }


def create_data_loaders(data_dict, vocab, seq_length=128, batch_size=32, num_workers=2):
    """
    Create PyTorch DataLoaders for train, validation, and test sets.
    
    Args:
        data_dict: Dictionary with 'train', 'validation', 'test' keys
        vocab: Vocabulary object
        seq_length: Sequence length for training
        batch_size: Batch size
        num_workers: Number of worker processes for data loading
    
    Returns:
        Dictionary with DataLoader objects
    """
    datasets = {}
    dataloaders = {}
    
    for split_name, texts in data_dict.items():
        print(f"Creating {split_name} dataset...")
        datasets[split_name] = WikiTextDataset(texts, vocab, seq_length)
        
        # Use shuffle only for training
        shuffle = (split_name == 'train')
        
        dataloaders[split_name] = DataLoader(
            datasets[split_name],
            batch_size=batch_size,
            shuffle=shuffle,
            num_workers=num_workers,
            pin_memory=torch.cuda.is_available()
        )
        
        print(f"{split_name} dataset: {len(datasets[split_name])} sequences")
    
    return dataloaders


def collate_batch(batch):
    """
    Collate function for DataLoader to handle variable-length sequences.
    """
    inputs, targets = zip(*batch)
    inputs = torch.stack(inputs)
    targets = torch.stack(targets)
    return inputs, targets


# Example usage and testing
if __name__ == "__main__":
    # Load dataset
    data = load_wikitext_dataset()
    
    # Create vocabulary
    vocab = Vocabulary()
    vocab.build_vocab_from_texts(data['train'])
    print(f"Vocabulary size: {len(vocab)}")
    
    # Create data loaders
    data_loaders = create_data_loaders(data, vocab, seq_length=64, batch_size=4)
    
    # Test data loading
    train_loader = data_loaders['train']
    for batch_idx, (inputs, targets) in enumerate(train_loader):
        print(f"Batch {batch_idx}:")
        print(f"Input shape: {inputs.shape}")
        print(f"Target shape: {targets.shape}")
        
        # Decode first sequence for inspection
        first_input = inputs[0]
        decoded = [vocab.decode(idx.item()) for idx in first_input[:10]]
        print(f"First 10 tokens: {decoded}")
        
        if batch_idx >= 2:  # Only show first few batches
            break
