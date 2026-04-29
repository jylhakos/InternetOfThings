#!/usr/bin/env python3
"""
Feature Engineering with PyTorch for CNN

This script demonstrates feature engineering using Convolutional Neural Networks.
- Custom CNN architectures for feature extraction
- Transfer learning with pre-trained models
- Feature visualization and analysis
- Training and evaluation pipelines
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset, random_split
import torchvision
import torchvision.transforms as transforms
from torchvision import models, datasets

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import classification_report, confusion_matrix
import os
import time
from datetime import datetime
import argparse
import pickle

# Set random seeds for reproducibility
torch.manual_seed(42)
np.random.seed(42)

class CNNFeatureExtractor(nn.Module):
    """
    CNN architecture specifically designed for feature extraction from images.
    
    This model uses multiple convolutional blocks with batch normalization,
    dropout, and global average pooling to extract meaningful features.
    """
    
    def __init__(self, input_channels=3, feature_dim=512, num_classes=10):
        super(CNNFeatureExtractor, self).__init__()
        
        # Convolutional Feature Extraction Layers
        self.conv_layers = nn.Sequential(
            # Block 1: Basic feature detection
            nn.Conv2d(input_channels, 32, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.Conv2d(32, 32, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dropout2d(0.1),
            
            # Block 2: More complex patterns
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dropout2d(0.2),
            
            # Block 3: High-level features
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dropout2d(0.3),
            
            # Global Average Pooling for spatial invariance
            nn.AdaptiveAvgPool2d((1, 1))
        )
        
        # Feature extraction head
        self.feature_extractor = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128, feature_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(0.4)
        )
        
        # Classification head (optional)
        self.classifier = nn.Linear(feature_dim, num_classes)
        self.feature_dim = feature_dim
        
    def extract_features(self, x):
        """Extract features without classification"""
        conv_features = self.conv_layers(x)
        features = self.feature_extractor(conv_features)
        return features
        
    def get_conv_features(self, x):
        """Get intermediate convolutional features for visualization"""
        features = []
        for i, layer in enumerate(self.conv_layers):
            x = layer(x)
            if isinstance(layer, nn.Conv2d):
                features.append(x.clone())
        return features
        
    def forward(self, x):
        """Forward pass with both classification output and features"""
        features = self.extract_features(x)
        output = self.classifier(features)
        return output, features


class ResNetFeatureExtractor(nn.Module):
    """
    Feature extractor using pre-trained ResNet with custom feature head.
    
    This leverages transfer learning to extract high-quality features
    from pre-trained ImageNet models.
    """
    
    def __init__(self, feature_dim=512, num_classes=10, pretrained=True, architecture='resnet18'):
        super(ResNetFeatureExtractor, self).__init__()
        
        # Select ResNet architecture
        if architecture == 'resnet18':
            self.backbone = models.resnet18(pretrained=pretrained)
            backbone_features = 512
        elif architecture == 'resnet34':
            self.backbone = models.resnet34(pretrained=pretrained)
            backbone_features = 512
        elif architecture == 'resnet50':
            self.backbone = models.resnet50(pretrained=pretrained)
            backbone_features = 2048
        else:
            raise ValueError(f"Unsupported architecture: {architecture}")
        
        # Remove the final classification layer
        self.backbone = nn.Sequential(*list(self.backbone.children())[:-1])
        
        # Custom feature extraction head
        self.feature_extractor = nn.Sequential(
            nn.Flatten(),
            nn.Linear(backbone_features, feature_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3)
        )
        
        # Classification head
        self.classifier = nn.Linear(feature_dim, num_classes)
        self.feature_dim = feature_dim
        self.architecture = architecture
        
    def extract_features(self, x):
        """Extract features using pre-trained backbone"""
        backbone_features = self.backbone(x)
        features = self.feature_extractor(backbone_features)
        return features
        
    def forward(self, x):
        """Forward pass with classification"""
        features = self.extract_features(x)
        output = self.classifier(features)
        return output, features


class CNNFeatureTrainer:
    """
    Trainer class for CNN feature extraction models
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
            output, features = self.model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            _, predicted = output.max(1)
            total += target.size(0)
            correct += predicted.eq(target).sum().item()
            
            if batch_idx % 100 == 0:
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
            
            # Training
            train_loss, train_acc = self.train_epoch(train_loader, optimizer, criterion)
            
            # Validation
            val_loss, val_acc = self.validate_epoch(val_loader, criterion)
            
            # Learning rate scheduling
            scheduler.step(val_loss)
            
            # Store metrics
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


def visualize_features(model, data_loader, device, num_samples=1000, save_path=None):
    """
    Extract and visualize features using PCA and t-SNE
    """
    model.eval()
    features_list = []
    labels_list = []
    
    print("Extracting features for visualization...")
    with torch.no_grad():
        for i, (data, target) in enumerate(data_loader):
            if len(features_list) * data_loader.batch_size >= num_samples:
                break
                
            data = data.to(device)
            _, features = model(data)
            features_list.append(features.cpu().numpy())
            labels_list.append(target.numpy())
    
    # Concatenate all features
    all_features = np.concatenate(features_list, axis=0)
    all_labels = np.concatenate(labels_list, axis=0)
    
    print(f"Visualizing {len(all_features)} samples with {all_features.shape[1]} features")
    
    # Create visualization
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    # PCA visualization
    print("Computing PCA...")
    pca = PCA(n_components=2, random_state=42)
    features_pca = pca.fit_transform(all_features)
    
    scatter = axes[0].scatter(features_pca[:, 0], features_pca[:, 1], 
                            c=all_labels, cmap='tab10', alpha=0.6, s=20)
    axes[0].set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2f})')
    axes[0].set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2f})')
    axes[0].set_title('CNN Features - PCA Visualization')
    axes[0].grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=axes[0])
    
    # t-SNE visualization
    print("Computing t-SNE...")
    tsne = TSNE(n_components=2, random_state=42, perplexity=30)
    features_tsne = tsne.fit_transform(all_features[:min(1000, len(all_features))])
    labels_tsne = all_labels[:min(1000, len(all_labels))]
    
    scatter2 = axes[1].scatter(features_tsne[:, 0], features_tsne[:, 1], 
                             c=labels_tsne, cmap='tab10', alpha=0.6, s=20)
    axes[1].set_xlabel('t-SNE 1')
    axes[1].set_ylabel('t-SNE 2')
    axes[1].set_title('CNN Features - t-SNE Visualization')
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


def visualize_conv_features(model, sample_input, save_path=None):
    """
    Visualize convolutional feature maps
    """
    model.eval()
    
    with torch.no_grad():
        conv_features = model.get_conv_features(sample_input)
    
    # Visualize first few layers
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    for i in range(min(6, len(conv_features))):
        # Take first sample and first few channels
        feature_map = conv_features[i][0]  # First sample
        
        # Average across channels for visualization
        if feature_map.dim() == 3:
            feature_map = feature_map.mean(dim=0)
        
        im = axes[i].imshow(feature_map.cpu().numpy(), cmap='viridis')
        axes[i].set_title(f'Conv Layer {i+1} Features')
        axes[i].axis('off')
        plt.colorbar(im, ax=axes[i])
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Feature maps saved to {save_path}")
    else:
        plt.show()
    
    plt.close()


def prepare_datasets(dataset_name='CIFAR10', batch_size=128, val_split=0.1):
    """
    Prepare datasets for training
    """
    # Data transforms
    if dataset_name == 'CIFAR10':
        transform_train = transforms.Compose([
            transforms.RandomCrop(32, padding=4),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
        ])
        
        transform_test = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
        ])
        
        # Load datasets
        full_train_dataset = datasets.CIFAR10(
            root='../datasets', train=True, download=True, transform=transform_train
        )
        test_dataset = datasets.CIFAR10(
            root='../datasets', train=False, download=True, transform=transform_test
        )
        
        num_classes = 10
        input_channels = 3
        
    elif dataset_name == 'MNIST':
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ])
        
        full_train_dataset = datasets.MNIST(
            root='../datasets', train=True, download=True, transform=transform
        )
        test_dataset = datasets.MNIST(
            root='../datasets', train=False, download=True, transform=transform
        )
        
        num_classes = 10
        input_channels = 1
    
    else:
        raise ValueError(f"Unsupported dataset: {dataset_name}")
    
    # Split training set into train and validation
    train_size = int((1 - val_split) * len(full_train_dataset))
    val_size = len(full_train_dataset) - train_size
    
    train_dataset, val_dataset = random_split(
        full_train_dataset, [train_size, val_size],
        generator=torch.Generator().manual_seed(42)
    )
    
    # Create data loaders
    train_loader = DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True, num_workers=2
    )
    val_loader = DataLoader(
        val_dataset, batch_size=batch_size, shuffle=False, num_workers=2
    )
    test_loader = DataLoader(
        test_dataset, batch_size=batch_size, shuffle=False, num_workers=2
    )
    
    return train_loader, val_loader, test_loader, num_classes, input_channels


def main():
    parser = argparse.ArgumentParser(description='CNN Feature Engineering')
    parser.add_argument('--dataset', default='CIFAR10', choices=['CIFAR10', 'MNIST'],
                      help='Dataset to use')
    parser.add_argument('--model', default='custom', choices=['custom', 'resnet18', 'resnet34'],
                      help='Model architecture')
    parser.add_argument('--epochs', type=int, default=20, help='Number of epochs')
    parser.add_argument('--batch-size', type=int, default=128, help='Batch size')
    parser.add_argument('--lr', type=float, default=0.001, help='Learning rate')
    parser.add_argument('--feature-dim', type=int, default=256, help='Feature dimension')
    parser.add_argument('--no-train', action='store_true', help='Skip training')
    parser.add_argument('--visualize', action='store_true', help='Generate visualizations')
    
    args = parser.parse_args()
    
    # Enhanced device configuration with CUDA error handling
    print("🔧 Configuring device for PyTorch...")
    
    try:
        if torch.cuda.is_available():
            device = torch.device('cuda')
            print(f" Using GPU: {torch.cuda.get_device_name(0)}")
            print(f"   CUDA Version: {torch.version.cuda}")
            print(f"   GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
            
            # Test GPU functionality
            test_tensor = torch.randn(10, 10).cuda()
            _ = torch.mm(test_tensor, test_tensor)
            print("   GPU operations: Working")
            
            # Memory management settings
            if hasattr(torch.cuda, 'memory_fraction'):
                torch.cuda.set_memory_fraction(0.8)  # Use 80% of GPU memory
            
        else:
            device = torch.device('cpu')
            print("⚠️  CUDA not available - using CPU")
            print("   For GPU acceleration:")
            print("   1. Check if NVIDIA GPU is installed: nvidia-smi")
            print("   2. Install CUDA-enabled PyTorch:")
            print("      pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118")
            
    except RuntimeError as e:
        print(f"⚠️  CUDA error detected: {e}")
        print("   Falling back to CPU mode")
        print("   This might be due to:")
        print("   - GPU memory insufficient")
        print("   - CUDA version mismatch")
        print("   - Driver compatibility issues")
        device = torch.device('cpu')
    
    except Exception as e:
        print(f"❌ Unexpected device error: {e}")
        print("   Using CPU as fallback")
        device = torch.device('cpu')
    
    print(f"The device: {device}")
    
    # Adjust batch size based on device
    if device.type == 'cpu' and args.batch_size > 64:
        print(f"⚠️  Large batch size ({args.batch_size}) on CPU - consider reducing for better performance")
        if args.batch_size > 128:
            args.batch_size = 64
            print(f"   Automatically reduced batch size to {args.batch_size}")
    
    # Create output directories
    os.makedirs('../results/cnn_features', exist_ok=True)
    os.makedirs('../models', exist_ok=True)
    
    # Prepare datasets
    print(f"Preparing {args.dataset} dataset...")
    train_loader, val_loader, test_loader, num_classes, input_channels = prepare_datasets(
        args.dataset, args.batch_size
    )
    
    # Create model
    if args.model == 'custom':
        model = CNNFeatureExtractor(
            input_channels=input_channels,
            feature_dim=args.feature_dim,
            num_classes=num_classes
        )
    else:
        model = ResNetFeatureExtractor(
            feature_dim=args.feature_dim,
            num_classes=num_classes,
            architecture=args.model
        )
    
    print(f"Model: {args.model}")
    print(f"Parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # Training
    if not args.no_train:
        trainer = CNNFeatureTrainer(model, device)
        train_losses, val_losses, train_accs, val_accs = trainer.train(
            train_loader, val_loader, args.epochs, args.lr
        )
        
        # Save model
        model_path = f'../models/cnn_features_{args.model}_{args.dataset.lower()}.pth'
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
        plt.savefig(f'../results/cnn_features/training_curves_{args.model}_{args.dataset.lower()}.png')
        plt.show()
    
    # Feature visualization
    if args.visualize:
        print("Generating feature visualizations...")
        
        # Extract and visualize features
        features, labels = visualize_features(
            model, test_loader, device, num_samples=2000,
            save_path=f'../results/cnn_features/feature_space_{args.model}_{args.dataset.lower()}.png'
        )
        
        # Visualize convolutional features
        sample_batch = next(iter(test_loader))
        sample_input = sample_batch[0][:4].to(device)  # First 4 samples
        
        if hasattr(model, 'get_conv_features'):
            visualize_conv_features(
                model, sample_input,
                save_path=f'../results/cnn_features/conv_features_{args.model}_{args.dataset.lower()}.png'
            )
        
        # Save extracted features
        features_path = f'../results/cnn_features/extracted_features_{args.model}_{args.dataset.lower()}.pkl'
        with open(features_path, 'wb') as f:
            pickle.dump({'features': features, 'labels': labels}, f)
        print(f"Features saved to {features_path}")
    
    print("CNN Feature Engineering completed!")


if __name__ == '__main__':
    main()
