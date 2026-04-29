#!/usr/bin/env python3
"""
Simple CNN training script for Feature Learning demonstration.
"""

import os
import sys
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import torchvision.transforms as transforms
from datasets import load_dataset
import numpy as np
from tqdm import tqdm
import time

# Simple CNN Model
class SimpleCNN(nn.Module):
    def __init__(self, num_classes=10):
        super(SimpleCNN, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(128 * 3 * 3, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x):
        x = self.features(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x
    
    def extract_features(self, x):
        x = self.features(x)
        x = torch.flatten(x, 1)
        features = self.classifier[:-1](x)
        return features

# Custom Dataset Class
class MNISTDataset(torch.utils.data.Dataset):
    def __init__(self, hf_dataset, transform=None):
        self.hf_dataset = hf_dataset
        self.transform = transform
    
    def __len__(self):
        return len(self.hf_dataset)
    
    def __getitem__(self, idx):
        item = self.hf_dataset[idx]
        image = item['image']
        label = item['label']
        
        # Convert to tensor if needed
        if not isinstance(image, torch.Tensor):
            image = transforms.ToTensor()(image)
        
        if self.transform:
            image = self.transform(image)
        
        return image, label

def train_cnn():
    print("🚀 Starting CNN Feature Learning Training")
    print("="*50)
    
    # Setup device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Load MNIST dataset
    print("📊 Loading MNIST dataset...")
    try:
        dataset = load_dataset("ylecun/mnist")
        
        # Create transforms
        transform = transforms.Compose([
            transforms.Normalize((0.1307,), (0.3081,))
        ])
        
        # Create datasets
        train_dataset = MNISTDataset(dataset['train'], transform=transform)
        test_dataset = MNISTDataset(dataset['test'], transform=transform)
        
        # Create data loaders
        train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True, num_workers=2)
        test_loader = DataLoader(test_dataset, batch_size=1000, shuffle=False, num_workers=2)
        
        print(f"✅ Dataset loaded: {len(train_dataset)} training, {len(test_dataset)} test samples")
        
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return
    
    # Create model
    print("🧠 Creating CNN model...")
    model = SimpleCNN(num_classes=10).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    num_params = sum(p.numel() for p in model.parameters())
    print(f"✅ Model created with {num_params:,} parameters")
    
    # Training loop
    epochs = 3  # Reduced for demo
    print(f"🏋️ Starting training for {epochs} epochs...")
    
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        pbar = tqdm(train_loader, desc=f'Epoch {epoch+1}/{epochs}')
        for batch_idx, (data, target) in enumerate(pbar):
            data, target = data.to(device), target.to(device)
            
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            pred = output.argmax(dim=1)
            correct += pred.eq(target).sum().item()
            total += target.size(0)
            
            if batch_idx % 100 == 0:
                accuracy = 100. * correct / total
                avg_loss = total_loss / (batch_idx + 1)
                pbar.set_postfix({'Loss': f'{avg_loss:.4f}', 'Acc': f'{accuracy:.2f}%'})
        
        # Validation
        model.eval()
        val_loss = 0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for data, target in test_loader:
                data, target = data.to(device), target.to(device)
                output = model(data)
                val_loss += criterion(output, target).item()
                pred = output.argmax(dim=1)
                val_correct += pred.eq(target).sum().item()
                val_total += target.size(0)
        
        val_accuracy = 100. * val_correct / val_total
        val_loss /= len(test_loader)
        
        print(f"Epoch {epoch+1}: Val Loss: {val_loss:.4f}, Val Acc: {val_accuracy:.2f}%")
    
    # Save model
    os.makedirs('models', exist_ok=True)
    model_path = 'models/cnn_model.pth'
    torch.save({
        'model_state_dict': model.state_dict(),
        'accuracy': val_accuracy,
    }, model_path)
    
    print(f"✅ Model saved to {model_path}")
    
    # Extract features
    print("🔍 Extracting features...")
    model.eval()
    features_list = []
    labels_list = []
    
    with torch.no_grad():
        for data, target in tqdm(test_loader, desc='Extracting features'):
            data = data.to(device)
            features = model.extract_features(data)
            features_list.append(features.cpu().numpy())
            labels_list.append(target.numpy())
    
    all_features = np.vstack(features_list)
    all_labels = np.hstack(labels_list)
    
    # Save features
    os.makedirs('results', exist_ok=True)
    features_path = 'results/cnn_features.npz'
    np.savez(features_path, features=all_features, labels=all_labels)
    
    print(f"✅ Features saved to {features_path}")
    print(f"📊 Feature shape: {all_features.shape}")
    
    print("\n🎉 CNN Feature Learning Training Completed!")
    print("="*50)
    print(f"Final Validation Accuracy: {val_accuracy:.2f}%")
    print(f"Features Extracted: {all_features.shape[1]} dimensions")
    print("="*50)

if __name__ == "__main__":
    try:
        train_cnn()
    except KeyboardInterrupt:
        print("\n⚠️ Training interrupted by user")
    except Exception as e:
        print(f"❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
