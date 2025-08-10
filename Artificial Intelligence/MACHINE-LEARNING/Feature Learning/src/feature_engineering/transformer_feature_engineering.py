#!/usr/bin/env python3
"""
Feature Engineering with PyTorch for Transformer

This script demonstrates feature engineering using Transformer architectures.
- Multi-head self-attention mechanisms
- Positional encoding for sequence understanding
- Transformer encoder blocks for feature extraction
- Vision Transformer (ViT) for image features
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset, random_split
import math
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import os
import time
import pickle
import argparse

# Set random seeds
torch.manual_seed(42)
np.random.seed(42)


class PositionalEncoding(nn.Module):
    """
    Positional encoding for transformer models to understand sequence order
    """
    
    def __init__(self, d_model, max_len=5000):
        super(PositionalEncoding, self).__init__()
        
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * 
                           (-math.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        
        self.register_buffer('pe', pe)
        
    def forward(self, x):
        return x + self.pe[:x.size(0), :]


class MultiHeadAttention(nn.Module):
    """
    Multi-head self-attention mechanism
    """
    
    def __init__(self, d_model, n_heads, dropout=0.1):
        super(MultiHeadAttention, self).__init__()
        assert d_model % n_heads == 0
        
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        
        self.w_q = nn.Linear(d_model, d_model)
        self.w_k = nn.Linear(d_model, d_model)
        self.w_v = nn.Linear(d_model, d_model)
        self.w_o = nn.Linear(d_model, d_model)
        
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, query, key, value, mask=None):
        batch_size = query.size(0)
        
        # Linear transformations and split into heads
        Q = self.w_q(query).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        K = self.w_k(key).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        V = self.w_v(value).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        
        # Attention
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
            
        attention_weights = F.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)
        
        context = torch.matmul(attention_weights, V)
        
        # Concatenate heads and put through final linear layer
        context = context.transpose(1, 2).contiguous().view(
            batch_size, -1, self.d_model
        )
        
        output = self.w_o(context)
        return output, attention_weights


class TransformerBlock(nn.Module):
    """
    Transformer encoder block with multi-head attention and feed-forward network
    """
    
    def __init__(self, d_model, n_heads, d_ff, dropout=0.1):
        super(TransformerBlock, self).__init__()
        
        self.attention = MultiHeadAttention(d_model, n_heads, dropout)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        
        self.feed_forward = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),
            nn.Dropout(dropout)
        )
        
    def forward(self, x, mask=None):
        # Multi-head attention with residual connection
        attn_output, attention_weights = self.attention(x, x, x, mask)
        x = self.norm1(x + attn_output)
        
        # Feed-forward with residual connection
        ff_output = self.feed_forward(x)
        x = self.norm2(x + ff_output)
        
        return x, attention_weights


class TransformerFeatureExtractor(nn.Module):
    """
    Transformer-based feature extractor for sequence data
    """
    
    def __init__(self, vocab_size=10000, d_model=256, n_heads=8, n_layers=6, 
                 d_ff=1024, max_len=512, feature_dim=512, num_classes=2, dropout=0.1):
        super(TransformerFeatureExtractor, self).__init__()
        
        self.d_model = d_model
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.positional_encoding = PositionalEncoding(d_model, max_len)
        
        self.transformer_blocks = nn.ModuleList([
            TransformerBlock(d_model, n_heads, d_ff, dropout)
            for _ in range(n_layers)
        ])
        
        self.feature_extractor = nn.Sequential(
            nn.Linear(d_model, feature_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(feature_dim, feature_dim),
            nn.ReLU(),
            nn.Dropout(dropout)
        )
        
        self.classifier = nn.Linear(feature_dim, num_classes)
        self.feature_dim = feature_dim
        
    def create_padding_mask(self, x, pad_idx=0):
        """Create padding mask for attention"""
        return (x != pad_idx).unsqueeze(1).unsqueeze(2)
        
    def extract_features(self, x):
        """Extract features using transformer encoder"""
        # Embedding and positional encoding
        x = self.embedding(x) * math.sqrt(self.d_model)
        x = x.permute(1, 0, 2)  # (seq_len, batch, d_model)
        x = self.positional_encoding(x)
        x = x.permute(1, 0, 2)  # (batch, seq_len, d_model)
        
        # Create padding mask
        mask = self.create_padding_mask(x.sum(dim=-1))
        
        # Apply transformer blocks
        attention_weights = []
        for transformer_block in self.transformer_blocks:
            x, attn_weights = transformer_block(x, mask)
            attention_weights.append(attn_weights)
        
        # Global average pooling over sequence dimension
        x = x.mean(dim=1)  # (batch, d_model)
        
        # Extract features
        features = self.feature_extractor(x)
        return features, attention_weights
        
    def forward(self, x):
        """Forward pass with classification"""
        features, attention_weights = self.extract_features(x)
        output = self.classifier(features)
        return output, features, attention_weights


class VisionTransformer(nn.Module):
    """
    Vision Transformer (ViT) for image feature extraction
    """
    
    def __init__(self, img_size=224, patch_size=16, num_classes=1000, 
                 d_model=768, n_heads=12, n_layers=12, d_ff=3072, 
                 feature_dim=512, dropout=0.1):
        super(VisionTransformer, self).__init__()
        
        self.img_size = img_size
        self.patch_size = patch_size
        self.num_patches = (img_size // patch_size) ** 2
        
        # Patch embedding
        self.patch_embed = nn.Conv2d(3, d_model, kernel_size=patch_size, stride=patch_size)
        
        # Class token and position embeddings
        self.cls_token = nn.Parameter(torch.randn(1, 1, d_model))
        self.pos_embed = nn.Parameter(torch.randn(1, self.num_patches + 1, d_model))
        
        self.dropout = nn.Dropout(dropout)
        
        # Transformer blocks
        self.transformer_blocks = nn.ModuleList([
            TransformerBlock(d_model, n_heads, d_ff, dropout)
            for _ in range(n_layers)
        ])
        
        self.norm = nn.LayerNorm(d_model)
        
        # Feature extraction head
        self.feature_extractor = nn.Sequential(
            nn.Linear(d_model, feature_dim),
            nn.ReLU(),
            nn.Dropout(dropout)
        )
        
        # Classification head
        self.classifier = nn.Linear(feature_dim, num_classes)
        self.feature_dim = feature_dim
        
    def extract_features(self, x):
        """Extract features from images using Vision Transformer"""
        batch_size = x.shape[0]
        
        # Patch embedding
        x = self.patch_embed(x)  # (batch, d_model, H/P, W/P)
        x = x.flatten(2).transpose(1, 2)  # (batch, num_patches, d_model)
        
        # Add class token
        cls_tokens = self.cls_token.expand(batch_size, -1, -1)
        x = torch.cat([cls_tokens, x], dim=1)  # (batch, num_patches+1, d_model)
        
        # Add positional encoding
        x = x + self.pos_embed
        x = self.dropout(x)
        
        # Apply transformer blocks
        attention_weights = []
        for transformer_block in self.transformer_blocks:
            x, attn_weights = transformer_block(x)
            attention_weights.append(attn_weights)
        
        x = self.norm(x)
        
        # Use class token for feature extraction
        cls_features = x[:, 0]  # (batch, d_model)
        features = self.feature_extractor(cls_features)
        
        return features, attention_weights
        
    def forward(self, x):
        """Forward pass with classification"""
        features, attention_weights = self.extract_features(x)
        output = self.classifier(features)
        return output, features, attention_weights


class TransformerFeatureTrainer:
    """
    Trainer class for Transformer feature extraction models
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
            output, features, attention_weights = self.model(data)
            loss = criterion(output, target)
            loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
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
                output, features, attention_weights = self.model(data)
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
        # Use a smaller learning rate for transformers
        optimizer = optim.AdamW(self.model.parameters(), lr=lr, weight_decay=0.01)
        criterion = nn.CrossEntropyLoss()
        
        # Learning rate scheduler
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
        
        print(f"Starting training for {epochs} epochs...")
        print(f"Model has {sum(p.numel() for p in self.model.parameters()):,} parameters")
        
        for epoch in range(epochs):
            start_time = time.time()
            
            train_loss, train_acc = self.train_epoch(train_loader, optimizer, criterion)
            val_loss, val_acc = self.validate_epoch(val_loader, criterion)
            
            scheduler.step()
            
            self.train_losses.append(train_loss)
            self.val_losses.append(val_loss)
            self.train_accuracies.append(train_acc)
            self.val_accuracies.append(val_acc)
            
            epoch_time = time.time() - start_time
            print(f'Epoch {epoch+1}/{epochs} ({epoch_time:.1f}s)')
            print(f'Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%')
            print(f'Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%')
            print(f'LR: {scheduler.get_last_lr()[0]:.6f}')
            print('-' * 60)
            
        return self.train_losses, self.val_losses, self.train_accuracies, self.val_accuracies


def visualize_attention_weights(model, data_loader, device, save_path=None):
    """
    Visualize attention weights from transformer model
    """
    model.eval()
    
    # Get a sample batch
    data, target = next(iter(data_loader))
    data = data.to(device)
    
    with torch.no_grad():
        output, features, attention_weights = model(data)
    
    # Take first sample and last layer attention
    if attention_weights:
        last_attention = attention_weights[-1][0]  # First sample, last layer
        
        # Average across heads
        attention_avg = last_attention.mean(dim=0).cpu().numpy()
        
        plt.figure(figsize=(10, 8))
        plt.imshow(attention_avg, cmap='Blues')
        plt.colorbar()
        plt.title('Transformer Attention Weights (Last Layer, Averaged)')
        plt.xlabel('Key Position')
        plt.ylabel('Query Position')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Attention visualization saved to {save_path}")
        else:
            plt.show()
        
        plt.close()


def visualize_transformer_features(model, data_loader, device, num_samples=1000, save_path=None):
    """
    Extract and visualize transformer features
    """
    model.eval()
    features_list = []
    labels_list = []
    
    print("Extracting transformer features for visualization...")
    with torch.no_grad():
        for i, (data, target) in enumerate(data_loader):
            if len(features_list) * data_loader.batch_size >= num_samples:
                break
                
            data = data.to(device)
            _, features, _ = model(data)
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
    axes[0].set_title('Transformer Features - PCA Visualization')
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
    axes[1].set_title('Transformer Features - t-SNE Visualization')
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


# Import dataset utilities (reuse from previous scripts)
def generate_synthetic_sequence_data(num_samples=5000, seq_len=128, vocab_size=1000):
    """Generate synthetic sequence data for transformer training"""
    sequences = []
    labels = []
    
    for i in range(num_samples):
        # Generate random sequence
        seq = np.random.randint(1, vocab_size, seq_len)
        
        # Simple rule: if sum of first half > sum of second half, label = 1
        first_half_sum = np.sum(seq[:seq_len//2])
        second_half_sum = np.sum(seq[seq_len//2:])
        label = 1 if first_half_sum > second_half_sum else 0
        
        sequences.append(seq)
        labels.append(label)
    
    return np.array(sequences), np.array(labels)


class SyntheticSequenceDataset(Dataset):
    def __init__(self, sequences, labels):
        self.sequences = torch.tensor(sequences, dtype=torch.long)
        self.labels = torch.tensor(labels, dtype=torch.long)
        
    def __len__(self):
        return len(self.sequences)
    
    def __getitem__(self, idx):
        return self.sequences[idx], self.labels[idx]


def main():
    parser = argparse.ArgumentParser(description='Transformer Feature Engineering')
    parser.add_argument('--model', default='transformer', choices=['transformer', 'vit'],
                      help='Transformer model type')
    parser.add_argument('--epochs', type=int, default=10, help='Number of epochs')
    parser.add_argument('--batch-size', type=int, default=32, help='Batch size')
    parser.add_argument('--lr', type=float, default=0.0001, help='Learning rate')
    parser.add_argument('--d-model', type=int, default=256, help='Model dimension')
    parser.add_argument('--n-heads', type=int, default=8, help='Number of attention heads')
    parser.add_argument('--n-layers', type=int, default=6, help='Number of transformer layers')
    parser.add_argument('--feature-dim', type=int, default=512, help='Feature dimension')
    parser.add_argument('--num-samples', type=int, default=5000, help='Number of synthetic samples')
    parser.add_argument('--no-train', action='store_true', help='Skip training')
    parser.add_argument('--visualize', action='store_true', help='Generate visualizations')
    
    args = parser.parse_args()
    
    # Device configuration
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Create output directories
    os.makedirs('../results/transformer_features', exist_ok=True)
    os.makedirs('../models', exist_ok=True)
    
    if args.model == 'transformer':
        # Generate synthetic sequence data
        print("Generating synthetic sequence data...")
        sequences, labels = generate_synthetic_sequence_data(
            num_samples=args.num_samples, seq_len=128, vocab_size=1000
        )
        
        # Create dataset
        dataset = SyntheticSequenceDataset(sequences, labels)
        
        # Create model
        model = TransformerFeatureExtractor(
            vocab_size=1000,
            d_model=args.d_model,
            n_heads=args.n_heads,
            n_layers=args.n_layers,
            feature_dim=args.feature_dim,
            num_classes=2
        )
        
    elif args.model == 'vit':
        # For ViT, we would need image data - here we'll create a simplified version
        print("Vision Transformer model selected - using synthetic image-like data...")
        
        # Create synthetic "image" sequences (flattened patches)
        sequences = np.random.randn(args.num_samples, 196, 768)  # 14x14 patches, 768-dim features
        labels = np.random.randint(0, 2, args.num_samples)
        
        class SyntheticImageDataset(Dataset):
            def __init__(self, data, labels):
                self.data = torch.tensor(data, dtype=torch.float32)
                self.labels = torch.tensor(labels, dtype=torch.long)
                
            def __len__(self):
                return len(self.data)
            
            def __getitem__(self, idx):
                return self.data[idx], self.labels[idx]
        
        dataset = SyntheticImageDataset(sequences, labels)
        
        # Simplified ViT-like model
        model = TransformerFeatureExtractor(
            vocab_size=768,  # Input dimension
            d_model=args.d_model,
            n_heads=args.n_heads,
            n_layers=args.n_layers,
            feature_dim=args.feature_dim,
            num_classes=2
        )
    
    print(f"Model: {args.model.upper()}")
    print(f"Parameters: {sum(p.numel() for p in model.parameters()):,}")
    
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
    
    # Training
    if not args.no_train:
        trainer = TransformerFeatureTrainer(model, device)
        train_losses, val_losses, train_accs, val_accs = trainer.train(
            train_loader, val_loader, args.epochs, args.lr
        )
        
        # Save model
        model_path = f'../models/transformer_features_{args.model}.pth'
        torch.save({
            'model_state_dict': model.state_dict(),
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
        plt.savefig(f'../results/transformer_features/training_curves_{args.model}.png')
        plt.show()
    
    # Feature visualization
    if args.visualize:
        print("Generating feature visualizations...")
        
        features, labels = visualize_transformer_features(
            model, test_loader, device, num_samples=1000,
            save_path=f'../results/transformer_features/feature_space_{args.model}.png'
        )
        
        # Visualize attention weights
        visualize_attention_weights(
            model, test_loader, device,
            save_path=f'../results/transformer_features/attention_weights_{args.model}.png'
        )
        
        # Save extracted features
        features_path = f'../results/transformer_features/extracted_features_{args.model}.pkl'
        with open(features_path, 'wb') as f:
            pickle.dump({'features': features, 'labels': labels}, f)
        print(f"Features saved to {features_path}")
    
    print("Transformer Feature Engineering completed!")


if __name__ == '__main__':
    main()
