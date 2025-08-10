#!/usr/bin/env python3
"""
Feature Engineering with PyTorch for Transfer Learning

This script demonstrates feature engineering using transfer learning approaches.
- Pre-trained CNN models (ResNet, VGG, DenseNet) as feature extractors
- Fine-tuning strategies for domain adaptation
- Multi-domain feature extraction and comparison
- Cross-domain transfer learning evaluation
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
import pickle
import argparse
from collections import defaultdict

# Set random seeds
torch.manual_seed(42)
np.random.seed(42)


class PretrainedFeatureExtractor(nn.Module):
    """
    Feature extractor using pre-trained models
    """
    
    def __init__(self, architecture='resnet50', pretrained=True, feature_dim=512, 
                 num_classes=10, freeze_backbone=True):
        super(PretrainedFeatureExtractor, self).__init__()
        
        self.architecture = architecture
        self.feature_dim = feature_dim
        
        # Load pre-trained model
        if architecture == 'resnet18':
            self.backbone = models.resnet18(pretrained=pretrained)
            backbone_features = self.backbone.fc.in_features
            self.backbone = nn.Sequential(*list(self.backbone.children())[:-1])
            
        elif architecture == 'resnet50':
            self.backbone = models.resnet50(pretrained=pretrained)
            backbone_features = self.backbone.fc.in_features
            self.backbone = nn.Sequential(*list(self.backbone.children())[:-1])
            
        elif architecture == 'vgg16':
            self.backbone = models.vgg16(pretrained=pretrained)
            backbone_features = self.backbone.classifier[6].in_features
            self.backbone.classifier = self.backbone.classifier[:-1]
            
        elif architecture == 'densenet121':
            self.backbone = models.densenet121(pretrained=pretrained)
            backbone_features = self.backbone.classifier.in_features
            self.backbone.classifier = nn.Identity()
            
        elif architecture == 'efficientnet_b0':
            self.backbone = models.efficientnet_b0(pretrained=pretrained)
            backbone_features = self.backbone.classifier[1].in_features
            self.backbone.classifier = nn.Identity()
            
        else:
            raise ValueError(f"Unsupported architecture: {architecture}")
        
        # Freeze backbone if requested
        if freeze_backbone:
            for param in self.backbone.parameters():
                param.requires_grad = False
                
        # Custom feature extraction head
        self.feature_extractor = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(0.5),
            nn.Linear(backbone_features, feature_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(feature_dim, feature_dim),
            nn.ReLU(inplace=True)
        )
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(feature_dim, num_classes)
        )
        
        self.backbone_features = backbone_features
        
    def extract_backbone_features(self, x):
        """Extract raw features from pre-trained backbone"""
        return self.backbone(x)
    
    def extract_features(self, x):
        """Extract processed features through custom head"""
        backbone_features = self.extract_backbone_features(x)
        features = self.feature_extractor(backbone_features)
        return features
    
    def forward(self, x):
        """Forward pass with classification"""
        features = self.extract_features(x)
        output = self.classifier(features)
        return output, features


class ProgressiveFineTuner(nn.Module):
    """
    Progressive fine-tuning approach for transfer learning
    """
    
    def __init__(self, base_model, fine_tune_layers=None):
        super(ProgressiveFineTuner, self).__init__()
        
        self.base_model = base_model
        self.fine_tune_layers = fine_tune_layers or []
        
    def freeze_all(self):
        """Freeze all parameters"""
        for param in self.base_model.parameters():
            param.requires_grad = False
            
    def unfreeze_classifier(self):
        """Unfreeze only classifier layers"""
        for param in self.base_model.classifier.parameters():
            param.requires_grad = True
        for param in self.base_model.feature_extractor.parameters():
            param.requires_grad = True
            
    def unfreeze_top_layers(self, num_layers=2):
        """Unfreeze top layers of backbone"""
        backbone_children = list(self.base_model.backbone.children())
        
        for layer in backbone_children[-num_layers:]:
            for param in layer.parameters():
                param.requires_grad = True
                
    def unfreeze_all(self):
        """Unfreeze all parameters"""
        for param in self.base_model.parameters():
            param.requires_grad = True
            
    def forward(self, x):
        return self.base_model(x)


class MultiDomainFeatureExtractor:
    """
    Extract and compare features from multiple pre-trained models
    """
    
    def __init__(self, architectures=['resnet18', 'vgg16', 'densenet121'], 
                 feature_dim=256, num_classes=10):
        self.models = {}
        self.architectures = architectures
        
        for arch in architectures:
            try:
                model = PretrainedFeatureExtractor(
                    architecture=arch,
                    feature_dim=feature_dim,
                    num_classes=num_classes,
                    freeze_backbone=True
                )
                self.models[arch] = model
            except Exception as e:
                print(f"Failed to load {arch}: {e}")
                
    def extract_features(self, x, device='cpu'):
        """Extract features from all models"""
        features = {}
        
        for arch, model in self.models.items():
            model.to(device)
            model.eval()
            
            with torch.no_grad():
                x = x.to(device)
                _, feat = model(x)
                features[arch] = feat.cpu().numpy()
                
        return features
    
    def compare_features(self, data_loader, device='cpu', num_samples=1000):
        """Compare features from different architectures"""
        all_features = defaultdict(list)
        labels = []
        
        print("Extracting features from multiple architectures...")
        
        with torch.no_grad():
            for i, (data, target) in enumerate(data_loader):
                if len(labels) >= num_samples:
                    break
                    
                features = self.extract_features(data, device)
                
                for arch, feat in features.items():
                    all_features[arch].append(feat)
                    
                labels.extend(target.numpy())
        
        # Concatenate features
        for arch in all_features:
            all_features[arch] = np.concatenate(all_features[arch], axis=0)
            
        return dict(all_features), np.array(labels)


class TransferLearningTrainer:
    """
    Trainer with progressive fine-tuning strategies
    """
    
    def __init__(self, model, device='cpu', fine_tuning_strategy='progressive'):
        self.model = model.to(device)
        self.device = device
        self.strategy = fine_tuning_strategy
        self.train_losses = []
        self.val_losses = []
        self.train_accuracies = []
        self.val_accuracies = []
        
    def train_epoch(self, train_loader, optimizer, criterion, epoch=0):
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
                print(f'Epoch {epoch}, Batch {batch_idx}/{len(train_loader)}, '
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
    
    def progressive_fine_tune(self, train_loader, val_loader, total_epochs=30):
        """Progressive fine-tuning strategy"""
        criterion = nn.CrossEntropyLoss()
        
        # Stage 1: Train only classifier (epochs 0-9)
        print("Stage 1: Training classifier only...")
        if hasattr(self.model, 'freeze_all'):
            self.model.freeze_all()
            self.model.unfreeze_classifier()
        
        optimizer = optim.Adam([p for p in self.model.parameters() if p.requires_grad], 
                             lr=0.001, weight_decay=1e-4)
        
        for epoch in range(10):
            train_loss, train_acc = self.train_epoch(train_loader, optimizer, criterion, epoch)
            val_loss, val_acc = self.validate_epoch(val_loader, criterion)
            
            self.train_losses.append(train_loss)
            self.val_losses.append(val_loss)
            self.train_accuracies.append(train_acc)
            self.val_accuracies.append(val_acc)
            
            print(f'Epoch {epoch+1}/10 - Train: {train_loss:.4f} ({train_acc:.2f}%) '
                  f'Val: {val_loss:.4f} ({val_acc:.2f}%)')
        
        # Stage 2: Fine-tune top layers (epochs 10-19)
        print("\nStage 2: Fine-tuning top layers...")
        if hasattr(self.model, 'unfreeze_top_layers'):
            self.model.unfreeze_top_layers(num_layers=2)
        
        optimizer = optim.Adam([p for p in self.model.parameters() if p.requires_grad], 
                             lr=0.0001, weight_decay=1e-4)
        
        for epoch in range(10, 20):
            train_loss, train_acc = self.train_epoch(train_loader, optimizer, criterion, epoch)
            val_loss, val_acc = self.validate_epoch(val_loader, criterion)
            
            self.train_losses.append(train_loss)
            self.val_losses.append(val_loss)
            self.train_accuracies.append(train_acc)
            self.val_accuracies.append(val_acc)
            
            print(f'Epoch {epoch+1}/20 - Train: {train_loss:.4f} ({train_acc:.2f}%) '
                  f'Val: {val_loss:.4f} ({val_acc:.2f}%)')
        
        # Stage 3: Fine-tune entire network (epochs 20-29)
        if total_epochs > 20:
            print("\nStage 3: Fine-tuning entire network...")
            if hasattr(self.model, 'unfreeze_all'):
                self.model.unfreeze_all()
            
            optimizer = optim.Adam(self.model.parameters(), lr=0.00001, weight_decay=1e-4)
            
            for epoch in range(20, min(total_epochs, 30)):
                train_loss, train_acc = self.train_epoch(train_loader, optimizer, criterion, epoch)
                val_loss, val_acc = self.validate_epoch(val_loader, criterion)
                
                self.train_losses.append(train_loss)
                self.val_losses.append(val_loss)
                self.train_accuracies.append(train_acc)
                self.val_accuracies.append(val_acc)
                
                print(f'Epoch {epoch+1}/{total_epochs} - Train: {train_loss:.4f} ({train_acc:.2f}%) '
                      f'Val: {val_loss:.4f} ({val_acc:.2f}%)')
        
        return self.train_losses, self.val_losses, self.train_accuracies, self.val_accuracies
    
    def standard_fine_tune(self, train_loader, val_loader, epochs=20, freeze_backbone=False):
        """Standard fine-tuning approach"""
        criterion = nn.CrossEntropyLoss()
        
        if freeze_backbone and hasattr(self.model, 'freeze_all'):
            self.model.freeze_all()
            self.model.unfreeze_classifier()
            lr = 0.001
        else:
            lr = 0.0001
            
        optimizer = optim.Adam([p for p in self.model.parameters() if p.requires_grad], 
                             lr=lr, weight_decay=1e-4)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=3)
        
        print(f"Starting {'frozen backbone' if freeze_backbone else 'full'} fine-tuning...")
        print(f"Trainable parameters: {sum(p.numel() for p in self.model.parameters() if p.requires_grad):,}")
        
        for epoch in range(epochs):
            train_loss, train_acc = self.train_epoch(train_loader, optimizer, criterion, epoch)
            val_loss, val_acc = self.validate_epoch(val_loader, criterion)
            
            scheduler.step(val_loss)
            
            self.train_losses.append(train_loss)
            self.val_losses.append(val_loss)
            self.train_accuracies.append(train_acc)
            self.val_accuracies.append(val_acc)
            
            print(f'Epoch {epoch+1}/{epochs} - Train: {train_loss:.4f} ({train_acc:.2f}%) '
                  f'Val: {val_loss:.4f} ({val_acc:.2f}%)')
        
        return self.train_losses, self.val_losses, self.train_accuracies, self.val_accuracies


def visualize_transfer_features(model, data_loader, device, num_samples=1000, save_path=None):
    """
    Visualize features from transfer learning model
    """
    model.eval()
    features_list = []
    labels_list = []
    
    print("Extracting transfer learning features for visualization...")
    with torch.no_grad():
        for i, (data, target) in enumerate(data_loader):
            if len(features_list) * data_loader.batch_size >= num_samples:
                break
                
            data = data.to(device)
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
                            c=all_labels, cmap='tab10', alpha=0.6, s=20)
    axes[0].set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2f})')
    axes[0].set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2f})')
    axes[0].set_title('Transfer Learning Features - PCA')
    axes[0].grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=axes[0])
    
    # t-SNE visualization
    tsne = TSNE(n_components=2, random_state=42, perplexity=30)
    features_tsne = tsne.fit_transform(all_features[:min(1000, len(all_features))])
    labels_tsne = all_labels[:min(1000, len(all_labels))]
    
    scatter2 = axes[1].scatter(features_tsne[:, 0], features_tsne[:, 1], 
                             c=labels_tsne, cmap='tab10', alpha=0.6, s=20)
    axes[1].set_xlabel('t-SNE 1')
    axes[1].set_ylabel('t-SNE 2')
    axes[1].set_title('Transfer Learning Features - t-SNE')
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


def compare_architecture_features(multi_extractor, data_loader, device, save_path=None):
    """
    Compare features from different architectures
    """
    features_dict, labels = multi_extractor.compare_features(data_loader, device, num_samples=1000)
    
    n_archs = len(features_dict)
    fig, axes = plt.subplots(2, n_archs, figsize=(5*n_archs, 10))
    
    if n_archs == 1:
        axes = axes.reshape(2, 1)
    
    for i, (arch, features) in enumerate(features_dict.items()):
        # PCA visualization
        pca = PCA(n_components=2, random_state=42)
        features_pca = pca.fit_transform(features)
        
        scatter = axes[0, i].scatter(features_pca[:, 0], features_pca[:, 1], 
                                   c=labels, cmap='tab10', alpha=0.6, s=15)
        axes[0, i].set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2f})')
        axes[0, i].set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2f})')
        axes[0, i].set_title(f'{arch.upper()} Features - PCA')
        axes[0, i].grid(True, alpha=0.3)
        
        # t-SNE visualization
        tsne = TSNE(n_components=2, random_state=42, perplexity=30)
        features_tsne = tsne.fit_transform(features[:min(500, len(features))])
        labels_tsne = labels[:min(500, len(labels))]
        
        scatter2 = axes[1, i].scatter(features_tsne[:, 0], features_tsne[:, 1], 
                                    c=labels_tsne, cmap='tab10', alpha=0.6, s=15)
        axes[1, i].set_xlabel('t-SNE 1')
        axes[1, i].set_ylabel('t-SNE 2')
        axes[1, i].set_title(f'{arch.upper()} Features - t-SNE')
        axes[1, i].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Architecture comparison saved to {save_path}")
    else:
        plt.show()
    
    plt.close()
    return features_dict, labels


def prepare_datasets(dataset_name='CIFAR10', batch_size=64):
    """
    Prepare datasets with appropriate transforms for pre-trained models
    """
    # ImageNet normalization for pre-trained models
    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                   std=[0.229, 0.224, 0.225])
    
    if dataset_name == 'CIFAR10':
        transform_train = transforms.Compose([
            transforms.Resize(224),  # Resize for pre-trained models
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            normalize
        ])
        
        transform_test = transforms.Compose([
            transforms.Resize(224),
            transforms.ToTensor(),
            normalize
        ])
        
        full_train_dataset = datasets.CIFAR10(
            root='../datasets', train=True, download=True, transform=transform_train
        )
        test_dataset = datasets.CIFAR10(
            root='../datasets', train=False, download=True, transform=transform_test
        )
        
        num_classes = 10
        
    elif dataset_name == 'CIFAR100':
        transform_train = transforms.Compose([
            transforms.Resize(224),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            normalize
        ])
        
        transform_test = transforms.Compose([
            transforms.Resize(224),
            transforms.ToTensor(),
            normalize
        ])
        
        full_train_dataset = datasets.CIFAR100(
            root='../datasets', train=True, download=True, transform=transform_train
        )
        test_dataset = datasets.CIFAR100(
            root='../datasets', train=False, download=True, transform=transform_test
        )
        
        num_classes = 100
        
    else:
        raise ValueError(f"Unsupported dataset: {dataset_name}")
    
    # Split training set
    train_size = int(0.8 * len(full_train_dataset))
    val_size = len(full_train_dataset) - train_size
    
    train_dataset, val_dataset = random_split(
        full_train_dataset, [train_size, val_size],
        generator=torch.Generator().manual_seed(42)
    )
    
    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=2)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=2)
    
    return train_loader, val_loader, test_loader, num_classes


def main():
    parser = argparse.ArgumentParser(description='Transfer Learning Feature Engineering')
    parser.add_argument('--architecture', default='resnet18', 
                      choices=['resnet18', 'resnet50', 'vgg16', 'densenet121'],
                      help='Pre-trained model architecture')
    parser.add_argument('--dataset', default='CIFAR10', choices=['CIFAR10', 'CIFAR100'],
                      help='Dataset to use')
    parser.add_argument('--strategy', default='progressive', 
                      choices=['progressive', 'frozen', 'full'],
                      help='Fine-tuning strategy')
    parser.add_argument('--epochs', type=int, default=20, help='Number of epochs')
    parser.add_argument('--batch-size', type=int, default=64, help='Batch size')
    parser.add_argument('--feature-dim', type=int, default=256, help='Feature dimension')
    parser.add_argument('--no-train', action='store_true', help='Skip training')
    parser.add_argument('--visualize', action='store_true', help='Generate visualizations')
    parser.add_argument('--compare-architectures', action='store_true', 
                      help='Compare multiple architectures')
    
    args = parser.parse_args()
    
    # Device configuration
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Create output directories
    os.makedirs('../results/transfer_features', exist_ok=True)
    os.makedirs('../models', exist_ok=True)
    
    # Prepare datasets
    print(f"Preparing {args.dataset} dataset...")
    train_loader, val_loader, test_loader, num_classes = prepare_datasets(
        args.dataset, args.batch_size
    )
    
    # Create model
    model = PretrainedFeatureExtractor(
        architecture=args.architecture,
        feature_dim=args.feature_dim,
        num_classes=num_classes,
        freeze_backbone=(args.strategy == 'frozen')
    )
    
    # Wrap in progressive fine-tuner if needed
    if args.strategy == 'progressive':
        model = ProgressiveFineTuner(model)
    
    print(f"Model: {args.architecture.upper()} (Transfer Learning)")
    print(f"Strategy: {args.strategy}")
    print(f"Total parameters: {sum(p.numel() for p in model.parameters()):,}")
    print(f"Trainable parameters: {sum(p.numel() for p in model.parameters() if p.requires_grad):,}")
    
    # Training
    if not args.no_train:
        trainer = TransferLearningTrainer(model, device, args.strategy)
        
        if args.strategy == 'progressive':
            train_losses, val_losses, train_accs, val_accs = trainer.progressive_fine_tune(
                train_loader, val_loader, args.epochs
            )
        else:
            freeze_backbone = (args.strategy == 'frozen')
            train_losses, val_losses, train_accs, val_accs = trainer.standard_fine_tune(
                train_loader, val_loader, args.epochs, freeze_backbone
            )
        
        # Save model
        model_path = f'../models/transfer_features_{args.architecture}_{args.strategy}_{args.dataset.lower()}.pth'
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
        plt.title(f'Transfer Learning Training Loss ({args.strategy})')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(1, 2, 2)
        plt.plot(train_accs, label='Train Accuracy')
        plt.plot(val_accs, label='Val Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy (%)')
        plt.title(f'Transfer Learning Accuracy ({args.strategy})')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig(f'../results/transfer_features/training_curves_{args.architecture}_{args.strategy}_{args.dataset.lower()}.png')
        plt.show()
    
    # Visualizations
    if args.visualize:
        print("Generating feature visualizations...")
        
        # Single model visualization
        features, labels = visualize_transfer_features(
            model, test_loader, device, num_samples=1000,
            save_path=f'../results/transfer_features/feature_space_{args.architecture}_{args.strategy}_{args.dataset.lower()}.png'
        )
        
        # Save features
        features_path = f'../results/transfer_features/extracted_features_{args.architecture}_{args.strategy}_{args.dataset.lower()}.pkl'
        with open(features_path, 'wb') as f:
            pickle.dump({'features': features, 'labels': labels}, f)
        print(f"Features saved to {features_path}")
    
    # Compare architectures
    if args.compare_architectures:
        print("Comparing multiple architectures...")
        
        multi_extractor = MultiDomainFeatureExtractor(
            architectures=['resnet18', 'vgg16', 'densenet121'],
            feature_dim=args.feature_dim,
            num_classes=num_classes
        )
        
        features_dict, labels = compare_architecture_features(
            multi_extractor, test_loader, device,
            save_path=f'../results/transfer_features/architecture_comparison_{args.dataset.lower()}.png'
        )
        
        # Save comparison results
        comparison_path = f'../results/transfer_features/architecture_features_{args.dataset.lower()}.pkl'
        with open(comparison_path, 'wb') as f:
            pickle.dump({'features_dict': features_dict, 'labels': labels}, f)
        print(f"Architecture comparison saved to {comparison_path}")
    
    print("Transfer Learning Feature Engineering completed!")


if __name__ == '__main__':
    main()
