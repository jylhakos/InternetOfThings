#!/usr/bin/env python3
"""
Feature Engineering with PyTorch for RNN

This script demonstrates feature engineering using Recurrent Neural Networks (RNNs).
- LSTM and GRU architectures for sequence feature extraction
- Bidirectional RNNs for enhanced context understanding
- Attention mechanisms for focused feature extraction
- Text and time-series feature engineering
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset, random_split
from torch.nn.utils.rnn import pad_sequence, pack_padded_sequence, pad_packed_sequence

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import classification_report, confusion_matrix
import os
import time
import pickle
import argparse
from collections import Counter
import string

# Set random seeds
torch.manual_seed(42)
np.random.seed(42)


class LSTMFeatureExtractor(nn.Module):
    """
    LSTM-based feature extractor for sequence data.
    
    This model uses bidirectional LSTM layers to capture both past and future
    context for robust sequence feature extraction.
    """
    
    def __init__(self, vocab_size=10000, embed_dim=128, hidden_dim=256, 
                 num_layers=2, feature_dim=512, num_classes=2, dropout=0.3):
        super(LSTMFeatureExtractor, self).__init__()
        
        # Embedding layer
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        
        # Bidirectional LSTM layers
        self.lstm = nn.LSTM(
            embed_dim, hidden_dim, num_layers,
            batch_first=True, dropout=dropout if num_layers > 1 else 0,
            bidirectional=True
        )
        
        # Feature extraction head
        self.feature_extractor = nn.Sequential(
            nn.Linear(hidden_dim * 2, feature_dim),  # *2 for bidirectional
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(feature_dim, feature_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout)
        )
        
        # Classification head
        self.classifier = nn.Linear(feature_dim, num_classes)
        
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.feature_dim = feature_dim
        
    def extract_features(self, x, lengths=None):
        """Extract sequence features using LSTM"""
        # Embedding
        embedded = self.embedding(x)  # (batch, seq_len, embed_dim)
        
        # LSTM processing
        if lengths is not None:
            # Pack sequences for efficiency
            packed_embedded = pack_padded_sequence(embedded, lengths, 
                                                 batch_first=True, enforce_sorted=False)
            lstm_out, (hidden, cell) = self.lstm(packed_embedded)
            lstm_out, _ = pad_packed_sequence(lstm_out, batch_first=True)
        else:
            lstm_out, (hidden, cell) = self.lstm(embedded)
        
        # Use last hidden state from both directions
        # hidden shape: (num_layers * num_directions, batch, hidden_dim)
        last_hidden = hidden[-2:, :, :].transpose(0, 1).contiguous()  # Last layer, both directions
        last_hidden = last_hidden.view(last_hidden.size(0), -1)  # Concatenate directions
        
        # Extract features
        features = self.feature_extractor(last_hidden)
        return features
    
    def forward(self, x, lengths=None):
        """Forward pass with classification"""
        features = self.extract_features(x, lengths)
        output = self.classifier(features)
        return output, features


class GRUFeatureExtractor(nn.Module):
    """
    GRU-based feature extractor as an alternative to LSTM.
    
    GRU often provides similar performance to LSTM with fewer parameters
    and faster training.
    """
    
    def __init__(self, vocab_size=10000, embed_dim=128, hidden_dim=256, 
                 num_layers=2, feature_dim=512, num_classes=2, dropout=0.3):
        super(GRUFeatureExtractor, self).__init__()
        
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        
        self.gru = nn.GRU(
            embed_dim, hidden_dim, num_layers,
            batch_first=True, dropout=dropout if num_layers > 1 else 0,
            bidirectional=True
        )
        
        self.feature_extractor = nn.Sequential(
            nn.Linear(hidden_dim * 2, feature_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(feature_dim, feature_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout)
        )
        
        self.classifier = nn.Linear(feature_dim, num_classes)
        self.feature_dim = feature_dim
        
    def extract_features(self, x, lengths=None):
        """Extract features using GRU"""
        embedded = self.embedding(x)
        
        if lengths is not None:
            packed_embedded = pack_padded_sequence(embedded, lengths, 
                                                 batch_first=True, enforce_sorted=False)
            gru_out, hidden = self.gru(packed_embedded)
        else:
            gru_out, hidden = self.gru(embedded)
        
        # Use last hidden state
        last_hidden = hidden[-2:, :, :].transpose(0, 1).contiguous()
        last_hidden = last_hidden.view(last_hidden.size(0), -1)
        
        features = self.feature_extractor(last_hidden)
        return features
    
    def forward(self, x, lengths=None):
        features = self.extract_features(x, lengths)
        output = self.classifier(features)
        return output, features


class AttentionLSTMFeatureExtractor(nn.Module):
    """
    LSTM with attention mechanism for enhanced feature extraction.
    
    The attention mechanism allows the model to focus on the most relevant
    parts of the sequence when extracting features.
    """
    
    def __init__(self, vocab_size=10000, embed_dim=128, hidden_dim=256, 
                 num_layers=2, feature_dim=512, num_classes=2, dropout=0.3):
        super(AttentionLSTMFeatureExtractor, self).__init__()
        
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        
        self.lstm = nn.LSTM(
            embed_dim, hidden_dim, num_layers,
            batch_first=True, dropout=dropout if num_layers > 1 else 0,
            bidirectional=True
        )
        
        # Attention mechanism
        self.attention = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, 1)
        )
        
        self.feature_extractor = nn.Sequential(
            nn.Linear(hidden_dim * 2, feature_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(feature_dim, feature_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout)
        )
        
        self.classifier = nn.Linear(feature_dim, num_classes)
        self.feature_dim = feature_dim
        
    def extract_features(self, x, lengths=None):
        """Extract features with attention mechanism"""
        embedded = self.embedding(x)
        
        if lengths is not None:
            packed_embedded = pack_padded_sequence(embedded, lengths, 
                                                 batch_first=True, enforce_sorted=False)
            lstm_out, _ = self.lstm(packed_embedded)
            lstm_out, _ = pad_packed_sequence(lstm_out, batch_first=True)
        else:
            lstm_out, _ = self.lstm(embedded)
        
        # Apply attention
        attention_weights = self.attention(lstm_out)  # (batch, seq_len, 1)
        attention_weights = F.softmax(attention_weights, dim=1)
        
        # Weighted sum of LSTM outputs
        attended_features = torch.sum(lstm_out * attention_weights, dim=1)  # (batch, hidden_dim*2)
        
        # Extract features
        features = self.feature_extractor(attended_features)
        return features, attention_weights
    
    def forward(self, x, lengths=None):
        features, attention_weights = self.extract_features(x, lengths)
        output = self.classifier(features)
        return output, features, attention_weights


class TextDataset(Dataset):
    """
    Custom dataset for text classification tasks
    """
    
    def __init__(self, texts, labels, vocab_to_idx, max_length=256):
        self.texts = texts
        self.labels = labels
        self.vocab_to_idx = vocab_to_idx
        self.max_length = max_length
        
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]
        
        # Convert text to indices
        indices = [self.vocab_to_idx.get(word, self.vocab_to_idx['<UNK>']) 
                  for word in text.split()[:self.max_length]]
        
        # Pad or truncate
        if len(indices) < self.max_length:
            indices.extend([0] * (self.max_length - len(indices)))
        
        return torch.tensor(indices, dtype=torch.long), torch.tensor(label, dtype=torch.long)


def create_vocabulary(texts, min_freq=2, max_vocab=10000):
    """
    Create vocabulary from text data
    """
    word_freq = Counter()
    for text in texts:
        words = text.lower().translate(str.maketrans('', '', string.punctuation)).split()
        word_freq.update(words)
    
    # Keep most frequent words
    vocab = ['<PAD>', '<UNK>'] + [word for word, freq in word_freq.most_common(max_vocab-2) 
                                  if freq >= min_freq]
    
    vocab_to_idx = {word: idx for idx, word in enumerate(vocab)}
    return vocab_to_idx, vocab


def generate_synthetic_text_data(num_samples=5000, max_length=50):
    """
    Generate synthetic text data for demonstration
    """
    # Simple synthetic text generation
    positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 
                     'perfect', 'outstanding', 'brilliant', 'superb', 'love', 'enjoy']
    negative_words = ['bad', 'terrible', 'awful', 'horrible', 'disappointing', 'poor',
                     'worst', 'hate', 'dislike', 'annoying', 'frustrating', 'useless']
    neutral_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of',
                    'with', 'by', 'this', 'that', 'these', 'those', 'very', 'really']
    
    texts = []
    labels = []
    
    for i in range(num_samples):
        # Generate random text length
        text_length = np.random.randint(10, max_length)
        
        # Determine sentiment
        sentiment = np.random.choice([0, 1])
        labels.append(sentiment)
        
        # Generate text with bias towards chosen sentiment
        text_words = []
        for _ in range(text_length):
            if sentiment == 1:  # Positive
                if np.random.random() < 0.3:
                    text_words.append(np.random.choice(positive_words))
                elif np.random.random() < 0.1:
                    text_words.append(np.random.choice(negative_words))
                else:
                    text_words.append(np.random.choice(neutral_words))
            else:  # Negative
                if np.random.random() < 0.3:
                    text_words.append(np.random.choice(negative_words))
                elif np.random.random() < 0.1:
                    text_words.append(np.random.choice(positive_words))
                else:
                    text_words.append(np.random.choice(neutral_words))
        
        texts.append(' '.join(text_words))
    
    return texts, labels


class RNNFeatureTrainer:
    """
    Trainer class for RNN feature extraction models
    """
    
    def __init__(self, model, device='cpu'):
        self.model = model.to(device)
        self.device = device
        self.train_losses = []
        self.val_losses = []
        self.train_accuracies = []
        self.val_accuracies = []
        
    def train_epoch(self, train_loader, optimizer, criterion):
        """Train for one epoch"""
        self.model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(self.device), target.to(self.device)
            
            optimizer.zero_grad()
            
            # Handle different model types
            if isinstance(self.model, AttentionLSTMFeatureExtractor):
                output, features, attention_weights = self.model(data)
            else:
                output, features = self.model(data)
            
            loss = criterion(output, target)
            loss.backward()
            
            # Gradient clipping for RNNs
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=5.0)
            
            optimizer.step()
            
            running_loss += loss.item()
            _, predicted = output.max(1)
            total += target.size(0)
            correct += predicted.eq(target).sum().item()
            
            if batch_idx % 50 == 0:
                print(f'Batch {batch_idx}/{len(train_loader)}, '
                      f'Loss: {loss.item():.6f}, '
                      f'Accuracy: {100.*correct/total:.2f}%')
                
        epoch_loss = running_loss / len(train_loader)
        epoch_acc = 100. * correct / total
        return epoch_loss, epoch_acc
    
    def validate_epoch(self, val_loader, criterion):
        """Validate for one epoch"""
        self.model.eval()
        running_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for data, target in val_loader:
                data, target = data.to(self.device), target.to(self.device)
                
                if isinstance(self.model, AttentionLSTMFeatureExtractor):
                    output, features, attention_weights = self.model(data)
                else:
                    output, features = self.model(data)
                
                loss = criterion(output, target)
                
                running_loss += loss.item()
                _, predicted = output.max(1)
                total += target.size(0)
                correct += predicted.eq(target).sum().item()
                
        epoch_loss = running_loss / len(val_loader)
        epoch_acc = 100. * correct / total
        return epoch_loss, epoch_acc
    
    def train(self, train_loader, val_loader, epochs=10, lr=0.001):
        """Full training loop"""
        optimizer = optim.Adam(self.model.parameters(), lr=lr, weight_decay=1e-4)
        criterion = nn.CrossEntropyLoss()
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=3)
        
        print(f"Starting training for {epochs} epochs...")
        print(f"Model has {sum(p.numel() for p in self.model.parameters()):,} parameters")
        
        for epoch in range(epochs):
            start_time = time.time()
            
            train_loss, train_acc = self.train_epoch(train_loader, optimizer, criterion)
            val_loss, val_acc = self.validate_epoch(val_loader, criterion)
            
            scheduler.step(val_loss)
            
            self.train_losses.append(train_loss)
            self.val_losses.append(val_loss)
            self.train_accuracies.append(train_acc)
            self.val_accuracies.append(val_acc)
            
            epoch_time = time.time() - start_time
            print(f'Epoch {epoch+1}/{epochs} ({epoch_time:.1f}s)')
            print(f'Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%')
            print(f'Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%')
            print('-' * 60)
            
        return self.train_losses, self.val_losses, self.train_accuracies, self.val_accuracies


def visualize_rnn_features(model, data_loader, device, num_samples=1000, save_path=None):
    """
    Extract and visualize RNN features
    """
    model.eval()
    features_list = []
    labels_list = []
    
    print("Extracting RNN features for visualization...")
    with torch.no_grad():
        for i, (data, target) in enumerate(data_loader):
            if len(features_list) * data_loader.batch_size >= num_samples:
                break
                
            data = data.to(device)
            
            if isinstance(model, AttentionLSTMFeatureExtractor):
                _, features, _ = model(data)
            else:
                _, features = model(data)
                
            features_list.append(features.cpu().numpy())
            labels_list.append(target.numpy())
    
    all_features = np.concatenate(features_list, axis=0)
    all_labels = np.concatenate(labels_list, axis=0)
    
    print(f"Visualizing {len(all_features)} samples with {all_features.shape[1]} features")
    
    # Create visualization
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    # PCA visualization
    pca = PCA(n_components=2, random_state=42)
    features_pca = pca.fit_transform(all_features)
    
    scatter = axes[0].scatter(features_pca[:, 0], features_pca[:, 1], 
                            c=all_labels, cmap='viridis', alpha=0.6, s=20)
    axes[0].set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2f})')
    axes[0].set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2f})')
    axes[0].set_title('RNN Features - PCA Visualization')
    axes[0].grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=axes[0])
    
    # t-SNE visualization
    tsne = TSNE(n_components=2, random_state=42, perplexity=30)
    features_tsne = tsne.fit_transform(all_features[:min(1000, len(all_features))])
    labels_tsne = all_labels[:min(1000, len(all_labels))]
    
    scatter2 = axes[1].scatter(features_tsne[:, 0], features_tsne[:, 1], 
                             c=labels_tsne, cmap='viridis', alpha=0.6, s=20)
    axes[1].set_xlabel('t-SNE 1')
    axes[1].set_ylabel('t-SNE 2')
    axes[1].set_title('RNN Features - t-SNE Visualization')
    axes[1].grid(True, alpha=0.3)
    plt.colorbar(scatter2, ax=axes[1])
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Visualization saved to {save_path}")
    else:
        plt.show()
    
    plt.close()
    return all_features, all_labels


def main():
    parser = argparse.ArgumentParser(description='RNN Feature Engineering')
    parser.add_argument('--model', default='lstm', choices=['lstm', 'gru', 'attention'],
                      help='RNN model type')
    parser.add_argument('--epochs', type=int, default=15, help='Number of epochs')
    parser.add_argument('--batch-size', type=int, default=64, help='Batch size')
    parser.add_argument('--lr', type=float, default=0.001, help='Learning rate')
    parser.add_argument('--hidden-dim', type=int, default=128, help='Hidden dimension')
    parser.add_argument('--feature-dim', type=int, default=256, help='Feature dimension')
    parser.add_argument('--num-samples', type=int, default=5000, help='Number of synthetic samples')
    parser.add_argument('--no-train', action='store_true', help='Skip training')
    parser.add_argument('--visualize', action='store_true', help='Generate visualizations')
    
    args = parser.parse_args()
    
    # Device configuration
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Create output directories
    os.makedirs('../results/rnn_features', exist_ok=True)
    os.makedirs('../models', exist_ok=True)
    
    # Generate synthetic data
    print("Generating synthetic text data...")
    texts, labels = generate_synthetic_text_data(num_samples=args.num_samples)
    
    # Create vocabulary
    vocab_to_idx, vocab = create_vocabulary(texts)
    print(f"Vocabulary size: {len(vocab)}")
    
    # Create dataset
    dataset = TextDataset(texts, labels, vocab_to_idx)
    
    # Split dataset
    train_size = int(0.8 * len(dataset))
    val_size = int(0.1 * len(dataset))
    test_size = len(dataset) - train_size - val_size
    
    train_dataset, val_dataset, test_dataset = random_split(
        dataset, [train_size, val_size, test_size],
        generator=torch.Generator().manual_seed(42)
    )
    
    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False)
    
    # Create model
    model_params = {
        'vocab_size': len(vocab),
        'embed_dim': 128,
        'hidden_dim': args.hidden_dim,
        'feature_dim': args.feature_dim,
        'num_classes': 2
    }
    
    if args.model == 'lstm':
        model = LSTMFeatureExtractor(**model_params)
    elif args.model == 'gru':
        model = GRUFeatureExtractor(**model_params)
    elif args.model == 'attention':
        model = AttentionLSTMFeatureExtractor(**model_params)
    
    print(f"Model: {args.model.upper()}")
    print(f"Parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # Training
    if not args.no_train:
        trainer = RNNFeatureTrainer(model, device)
        train_losses, val_losses, train_accs, val_accs = trainer.train(
            train_loader, val_loader, args.epochs, args.lr
        )
        
        # Save model
        model_path = f'../models/rnn_features_{args.model}_text.pth'
        torch.save({
            'model_state_dict': model.state_dict(),
            'vocab_to_idx': vocab_to_idx,
            'train_losses': train_losses,
            'val_losses': val_losses,
            'train_accuracies': train_accs,
            'val_accuracies': val_accs,
            'args': args
        }, model_path)
        print(f"Model saved to {model_path}")
        
        # Plot training curves
        plt.figure(figsize=(12, 4))
        
        plt.subplot(1, 2, 1)
        plt.plot(train_losses, label='Train Loss')
        plt.plot(val_losses, label='Val Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.title('Training and Validation Loss')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(1, 2, 2)
        plt.plot(train_accs, label='Train Accuracy')
        plt.plot(val_accs, label='Val Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy (%)')
        plt.title('Training and Validation Accuracy')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig(f'../results/rnn_features/training_curves_{args.model}_text.png')
        plt.show()
    
    # Feature visualization
    if args.visualize:
        print("Generating feature visualizations...")
        
        features, labels = visualize_rnn_features(
            model, test_loader, device, num_samples=1000,
            save_path=f'../results/rnn_features/feature_space_{args.model}_text.png'
        )
        
        # Save extracted features
        features_path = f'../results/rnn_features/extracted_features_{args.model}_text.pkl'
        with open(features_path, 'wb') as f:
            pickle.dump({'features': features, 'labels': labels}, f)
        print(f"Features saved to {features_path}")
    
    print("RNN Feature Engineering completed!")


if __name__ == '__main__':
    main()
