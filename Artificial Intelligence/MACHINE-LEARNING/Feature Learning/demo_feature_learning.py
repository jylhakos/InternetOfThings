#!/usr/bin/env python3
"""
Demo: Feature Learning with PyTorch

This script demonstrates the basic concepts of feature learning using a simple CNN
on synthetic data. It's designed to work immediately after environment setup.
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import os

# Simple CNN for feature learning
class FeatureLearningCNN(nn.Module):
    def __init__(self, input_channels=1, feature_dim=64, num_classes=3):
        super().__init__()
        
        # Feature extractor (encoder part)
        self.feature_extractor = nn.Sequential(
            nn.Conv2d(input_channels, 32, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(64, feature_dim),
            nn.ReLU(inplace=True)
        )
        
        # Classifier head
        self.classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(feature_dim, num_classes)
        )
        
        self.feature_dim = feature_dim
    
    def extract_features(self, x):
        """Extract feature representations"""
        return self.feature_extractor(x)
    
    def forward(self, x):
        """Forward pass for training"""
        features = self.extract_features(x)
        return self.classifier(features)

def generate_synthetic_data(num_samples_per_class=200, image_size=28):
    """
    Generate synthetic 2D data with different patterns for demonstration.
    """
    print(" Generating synthetic data...")
    
    data = []
    labels = []
    
    # Class 0: Circles
    for _ in range(num_samples_per_class):
        img = np.zeros((image_size, image_size))
        center_x, center_y = np.random.randint(8, image_size-8, 2)
        radius = np.random.randint(3, 8)
        
        # Create circle
        y, x = np.ogrid[:image_size, :image_size]
        mask = (x - center_x)**2 + (y - center_y)**2 <= radius**2
        img[mask] = 1.0
        
        # Add noise
        noise = np.random.normal(0, 0.1, img.shape)
        img = np.clip(img + noise, 0, 1)
        
        data.append(img)
        labels.append(0)
    
    # Class 1: Rectangles
    for _ in range(num_samples_per_class):
        img = np.zeros((image_size, image_size))
        x1, y1 = np.random.randint(2, image_size//2, 2)
        width, height = np.random.randint(5, 15, 2)
        x2, y2 = min(x1 + width, image_size), min(y1 + height, image_size)
        
        img[y1:y2, x1:x2] = 1.0
        
        # Add noise
        noise = np.random.normal(0, 0.1, img.shape)
        img = np.clip(img + noise, 0, 1)
        
        data.append(img)
        labels.append(1)
    
    # Class 2: Diagonal lines
    for _ in range(num_samples_per_class):
        img = np.zeros((image_size, image_size))
        
        # Add diagonal lines
        for i in range(0, image_size, 4):
            if i + 1 < image_size:
                img[i, :] = 1.0
            if i + 1 < image_size:
                img[:, i] = 1.0
        
        # Add noise
        noise = np.random.normal(0, 0.1, img.shape)
        img = np.clip(img + noise, 0, 1)
        
        data.append(img)
        labels.append(2)
    
    # Convert to tensors
    data = torch.FloatTensor(data).unsqueeze(1)  # Add channel dimension
    labels = torch.LongTensor(labels)
    
    print(f" Generated {len(data)} samples with {len(torch.unique(labels))} classes")
    return data, labels

def train_model(model, train_data, train_labels, epochs=20, batch_size=32):
    """Train the feature learning model."""
    print(" Training feature learning model...")
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # Create simple batches
    dataset_size = len(train_data)
    num_batches = dataset_size // batch_size
    
    train_losses = []
    train_accuracies = []
    
    for epoch in range(epochs):
        # Shuffle data
        perm = torch.randperm(dataset_size)
        train_data_shuffled = train_data[perm]
        train_labels_shuffled = train_labels[perm]
        
        epoch_loss = 0
        correct = 0
        total = 0
        
        for i in range(0, dataset_size, batch_size):
            batch_data = train_data_shuffled[i:i+batch_size]
            batch_labels = train_labels_shuffled[i:i+batch_size]
            
            optimizer.zero_grad()
            outputs = model(batch_data)
            loss = criterion(outputs, batch_labels)
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
            _, predicted = outputs.max(1)
            total += batch_labels.size(0)
            correct += predicted.eq(batch_labels).sum().item()
        
        accuracy = 100. * correct / total
        avg_loss = epoch_loss / num_batches
        
        train_losses.append(avg_loss)
        train_accuracies.append(accuracy)
        
        if epoch % 5 == 0 or epoch == epochs - 1:
            print(f"Epoch {epoch+1}/{epochs}: Loss: {avg_loss:.4f}, Accuracy: {accuracy:.2f}%")
    
    return train_losses, train_accuracies

def extract_and_analyze_features(model, data, labels):
    """Extract features and perform analysis."""
    print(" Extracting and analyzing features...")
    
    model.eval()
    with torch.no_grad():
        features = model.extract_features(data)
    
    features_np = features.numpy()
    labels_np = labels.numpy()
    
    print(f" Extracted features: {features_np.shape}")
    
    # Basic feature statistics
    print(f" Feature Statistics:")
    print(f"   Mean: {np.mean(features_np):.4f}")
    print(f"   Std: {np.std(features_np):.4f}")
    print(f"   Min: {np.min(features_np):.4f}")
    print(f"   Max: {np.max(features_np):.4f}")
    
    return features_np, labels_np

def visualize_features(features, labels, method='pca', save_path=None):
    """Visualize features using dimensionality reduction."""
    print(f" Visualizing features using {method.upper()}...")
    
    try:
        if method == 'pca':
            reducer = PCA(n_components=2, random_state=42)
        elif method == 'tsne':
            reducer = TSNE(n_components=2, random_state=42, perplexity=30)
        else:
            print(f"Unknown method: {method}")
            return
        
        features_2d = reducer.fit_transform(features)
        
        # Create plot
        plt.figure(figsize=(8, 6))
        colors = ['red', 'blue', 'green', 'orange', 'purple']
        class_names = ['Circles', 'Rectangles', 'Lines']
        
        for class_id in np.unique(labels):
            mask = labels == class_id
            plt.scatter(features_2d[mask, 0], features_2d[mask, 1], 
                       c=colors[class_id], label=class_names[class_id], alpha=0.6)
        
        plt.xlabel(f'{method.upper()} Component 1')
        plt.ylabel(f'{method.upper()} Component 2')
        plt.title(f'Feature Visualization using {method.upper()}')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f" Visualization saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
        
    except Exception as e:
        print(f"❌ Visualization failed: {e}")

def evaluate_feature_separability(features, labels):
    """Evaluate how well features separate different classes."""
    print(" Evaluating feature separability...")
    
    unique_labels = np.unique(labels)
    within_class_distances = []
    between_class_distances = []
    
    for label in unique_labels:
        class_features = features[labels == label]
        
        # Within-class distances
        if len(class_features) > 1:
            # Sample pairs for efficiency
            n_pairs = min(100, len(class_features) * (len(class_features) - 1) // 2)
            for _ in range(n_pairs):
                idx1, idx2 = np.random.choice(len(class_features), 2, replace=False)
                dist = np.linalg.norm(class_features[idx1] - class_features[idx2])
                within_class_distances.append(dist)
        
        # Between-class distances
        for other_label in unique_labels:
            if other_label != label:
                other_class_features = features[labels == other_label]
                # Sample pairs
                n_pairs = min(50, len(class_features) * len(other_class_features))
                for _ in range(n_pairs):
                    idx1 = np.random.choice(len(class_features))
                    idx2 = np.random.choice(len(other_class_features))
                    dist = np.linalg.norm(class_features[idx1] - other_class_features[idx2])
                    between_class_distances.append(dist)
    
    if within_class_distances and between_class_distances:
        avg_within = np.mean(within_class_distances)
        avg_between = np.mean(between_class_distances)
        separability_ratio = avg_between / (avg_within + 1e-8)
        
        print(f" Separability Analysis:")
        print(f"   Average within-class distance: {avg_within:.4f}")
        print(f"   Average between-class distance: {avg_between:.4f}")
        print(f"   Separability ratio: {separability_ratio:.4f}")
        
        return separability_ratio
    
    return 0.0

def main():
    """Main demonstration function."""
    print(" Feature Learning Demo with PyTorch")
    print("=" * 50)
    
    # Set random seeds for reproducibility
    torch.manual_seed(42)
    np.random.seed(42)
    
    # 1. Generate synthetic data
    data, labels = generate_synthetic_data(num_samples_per_class=150)
    
    # 2. Create model
    print("\n Creating feature learning model...")
    model = FeatureLearningCNN(input_channels=1, feature_dim=32, num_classes=3)
    print(f" Model created with {sum(p.numel() for p in model.parameters())} parameters")
    
    # 3. Train model
    print("\n Training phase...")
    train_losses, train_accuracies = train_model(model, data, labels, epochs=15)
    print(f" Training completed. Final accuracy: {train_accuracies[-1]:.2f}%")
    
    # 4. Extract features
    print("\n Feature extraction phase...")
    features, labels_np = extract_and_analyze_features(model, data, labels)
    
    # 5. Evaluate feature quality
    print("\n Feature evaluation phase...")
    separability = evaluate_feature_separability(features, labels_np)
    
    # 6. Visualize features
    print("\n Visualization phase...")
    os.makedirs('results', exist_ok=True)
    
    # PCA visualization
    try:
        visualize_features(features, labels_np, method='pca', 
                         save_path='results/demo_features_pca.png')
    except Exception as e:
        print(f"⚠️ PCA visualization failed: {e}")
    
    # t-SNE visualization (if sklearn available)
    try:
        visualize_features(features, labels_np, method='tsne', 
                         save_path='results/demo_features_tsne.png')
    except Exception as e:
        print(f"⚠️ t-SNE visualization failed: {e}")
    
    # 7. Summary
    print("\n SUMMARY")
    print("=" * 50)
    print(f" Data: {len(data)} samples, {len(np.unique(labels_np))} classes")
    print(f" Model: {model.feature_dim}-dimensional features")
    print(f" Final Accuracy: {train_accuracies[-1]:.2f}%")
    print(f" Feature Separability: {separability:.4f}")
    print(f" isualizations saved to: results/")
    print("=" * 50)
    
    print("\n Feature learning demo completed successfully!")
    print(" Check the 'results/' directory for feature visualizations.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
