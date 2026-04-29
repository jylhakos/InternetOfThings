"""
MNIST CNN Classification with PyTorch
=====================================

This script implements a Convolutional Neural Network (CNN) for classifying
handwritten digits from the MNIST dataset using PyTorch.

Features:
- Data loading and normalization
- CNN architecture definition
- Training loop with GPU/CPU support
- Model evaluation and testing
- Model saving and loading
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import numpy as np
import time
import os

class MNISTNet(nn.Module):
    """
    Convolutional Neural Network for MNIST digit classification.
    
    Architecture:
    - Conv2d(1, 32, 3x3) -> ReLU -> MaxPool2d(2x2)
    - Conv2d(32, 64, 3x3) -> ReLU -> MaxPool2d(2x2)
    - Dropout(0.25)
    - Flatten -> Linear(9216, 128) -> ReLU -> Dropout(0.5)
    - Linear(128, 10) -> LogSoftmax
    """
    
    def __init__(self):
        super(MNISTNet, self).__init__()
        # First convolutional layer
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1)
        # Second convolutional layer
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        # Dropout layers
        self.conv2_drop = nn.Dropout2d(p=0.25)
        self.fc1_drop = nn.Dropout(p=0.5)
        # Fully connected layers
        self.fc1 = nn.Linear(64 * 7 * 7, 128)  # 7*7 from image dimension after conv/pool
        self.fc2 = nn.Linear(128, 10)
        
    def forward(self, x):
        # First conv layer: Conv -> ReLU -> MaxPool
        x = F.relu(self.conv1(x))
        x = F.max_pool2d(x, 2)
        
        # Second conv layer: Conv -> ReLU -> MaxPool -> Dropout
        x = F.relu(self.conv2(x))
        x = F.max_pool2d(x, 2)
        x = self.conv2_drop(x)
        
        # Flatten the tensor for fully connected layers
        x = x.view(x.size(0), -1)
        
        # First fully connected layer: Linear -> ReLU -> Dropout
        x = F.relu(self.fc1(x))
        x = self.fc1_drop(x)
        
        # Output layer: Linear -> LogSoftmax
        x = self.fc2(x)
        return F.log_softmax(x, dim=1)

def get_data_loaders(batch_size=64, test_batch_size=1000):
    """
    Load and normalize MNIST training and test datasets.
    
    Args:
        batch_size (int): Training batch size
        test_batch_size (int): Testing batch size
        
    Returns:
        tuple: (train_loader, test_loader)
    """
    # Define transforms for data preprocessing
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))  # MNIST mean and std
    ])
    
    # Download and load training dataset
    train_dataset = torchvision.datasets.MNIST(
        root='./data', 
        train=True,
        download=True, 
        transform=transform
    )
    
    # Download and load test dataset
    test_dataset = torchvision.datasets.MNIST(
        root='./data', 
        train=False,
        download=True, 
        transform=transform
    )
    
    # Create data loaders
    train_loader = DataLoader(
        train_dataset, 
        batch_size=batch_size, 
        shuffle=True
    )
    
    test_loader = DataLoader(
        test_dataset, 
        batch_size=test_batch_size, 
        shuffle=False
    )
    
    return train_loader, test_loader

def train_model(model, device, train_loader, optimizer, epoch):
    """
    Train the model for one epoch.
    
    Args:
        model: The neural network model
        device: torch.device (cuda or cpu)
        train_loader: Training data loader
        optimizer: Optimizer for training
        epoch: Current epoch number
    """
    model.train()  # Set model to training mode
    train_loss = 0
    correct = 0
    total = 0
    
    for batch_idx, (data, target) in enumerate(train_loader):
        # Move data to device (GPU/CPU)
        data, target = data.to(device), target.to(device)
        
        # Clear gradients
        optimizer.zero_grad()
        
        # Forward pass
        output = model(data)
        
        # Calculate loss
        loss = F.nll_loss(output, target)
        
        # Backward pass
        loss.backward()
        
        # Update weights
        optimizer.step()
        
        # Statistics
        train_loss += loss.item()
        pred = output.argmax(dim=1, keepdim=True)
        correct += pred.eq(target.view_as(pred)).sum().item()
        total += target.size(0)
        
        # Print progress
        if batch_idx % 100 == 0:
            print(f'Train Epoch: {epoch} [{batch_idx * len(data)}/{len(train_loader.dataset)} '
                  f'({100. * batch_idx / len(train_loader):.0f}%)]\tLoss: {loss.item():.6f}')
    
    accuracy = 100. * correct / total
    avg_loss = train_loss / len(train_loader)
    print(f'Training Set: Average loss: {avg_loss:.4f}, '
          f'Accuracy: {correct}/{total} ({accuracy:.2f}%)')
    
    return avg_loss, accuracy

def test_model(model, device, test_loader):
    """
    Test the model on test dataset.
    
    Args:
        model: The neural network model
        device: torch.device (cuda or cpu)
        test_loader: Test data loader
        
    Returns:
        tuple: (test_loss, accuracy)
    """
    model.eval()  # Set model to evaluation mode
    test_loss = 0
    correct = 0
    
    with torch.no_grad():  # Disable gradient computation
        for data, target in test_loader:
            # Move data to device
            data, target = data.to(device), target.to(device)
            
            # Forward pass
            output = model(data)
            
            # Calculate loss
            test_loss += F.nll_loss(output, target, reduction='sum').item()
            
            # Get predictions
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()
    
    test_loss /= len(test_loader.dataset)
    accuracy = 100. * correct / len(test_loader.dataset)
    
    print(f'Test Set: Average loss: {test_loss:.4f}, '
          f'Accuracy: {correct}/{len(test_loader.dataset)} ({accuracy:.2f}%)')
    
    return test_loss, accuracy

def visualize_predictions(model, device, test_loader, num_images=8):
    """
    Visualize model predictions on test images.
    
    Args:
        model: Trained model
        device: torch.device
        test_loader: Test data loader
        num_images: Number of images to display
    """
    model.eval()
    
    # Get a batch of test data
    data_iter = iter(test_loader)
    images, labels = next(data_iter)
    images, labels = images.to(device), labels.to(device)
    
    # Make predictions
    with torch.no_grad():
        outputs = model(images)
        predictions = outputs.argmax(dim=1)
    
    # Plot images with predictions
    fig, axes = plt.subplots(2, 4, figsize=(12, 6))
    axes = axes.ravel()
    
    for i in range(num_images):
        img = images[i].cpu().squeeze()
        axes[i].imshow(img, cmap='gray')
        axes[i].set_title(f'True: {labels[i].item()}, Pred: {predictions[i].item()}')
        axes[i].axis('off')
    
    plt.tight_layout()
    plt.savefig('mnist_predictions.png', dpi=150, bbox_inches='tight')
    plt.show()

def save_model(model, filepath='mnist_cnn_model.pth'):
    """Save the trained model."""
    torch.save(model.state_dict(), filepath)
    print(f"Model saved to {filepath}")

def load_model(filepath='mnist_cnn_model.pth', device='cpu'):
    """Load a saved model."""
    model = MNISTNet()
    model.load_state_dict(torch.load(filepath, map_location=device))
    model.to(device)
    return model

def main():
    """Main training and evaluation pipeline."""
    # Set random seeds for reproducibility
    torch.manual_seed(1)
    np.random.seed(1)
    
    # Training parameters
    batch_size = 64
    test_batch_size = 1000
    epochs = 10
    learning_rate = 0.01
    momentum = 0.5
    
    # Device configuration - Use GPU if available
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Using device: {device}')
    
    if torch.cuda.is_available():
        print(f'GPU: {torch.cuda.get_device_name(0)}')
        print(f'Memory Usage:')
        print(f'Allocated: {round(torch.cuda.memory_allocated(0)/1024**3,1)} GB')
        print(f'Cached: {round(torch.cuda.memory_reserved(0)/1024**3,1)} GB')
    
    # Load data
    print("Loading MNIST dataset...")
    train_loader, test_loader = get_data_loaders(batch_size, test_batch_size)
    print(f"Training samples: {len(train_loader.dataset)}")
    print(f"Test samples: {len(test_loader.dataset)}")
    
    # Initialize model
    model = MNISTNet().to(device)
    print(f"\nModel architecture:\n{model}")
    
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"\nTotal parameters: {total_params:,}")
    print(f"Trainable parameters: {trainable_params:,}")
    
    # Define optimizer
    optimizer = optim.SGD(model.parameters(), lr=learning_rate, momentum=momentum)
    
    # Training loop
    train_losses = []
    train_accuracies = []
    test_losses = []
    test_accuracies = []
    
    print(f"\nStarting training for {epochs} epochs...")
    start_time = time.time()
    
    for epoch in range(1, epochs + 1):
        print(f"\nEpoch {epoch}/{epochs}")
        print("-" * 50)
        
        # Train
        train_loss, train_acc = train_model(model, device, train_loader, optimizer, epoch)
        train_losses.append(train_loss)
        train_accuracies.append(train_acc)
        
        # Test
        test_loss, test_acc = test_model(model, device, test_loader)
        test_losses.append(test_loss)
        test_accuracies.append(test_acc)
    
    training_time = time.time() - start_time
    print(f"\nTraining completed in {training_time:.2f} seconds")
    
    # Save the model
    save_model(model, 'mnist_cnn_model.pth')
    
    # Plot training history
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(train_losses, label='Training Loss')
    plt.plot(test_losses, label='Test Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training and Test Loss')
    plt.legend()
    
    plt.subplot(1, 2, 2)
    plt.plot(train_accuracies, label='Training Accuracy')
    plt.plot(test_accuracies, label='Test Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy (%)')
    plt.title('Training and Test Accuracy')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('training_history.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    # Visualize predictions
    print("\nGenerating prediction visualizations...")
    visualize_predictions(model, device, test_loader)
    
    print(f"\nFinal Test Accuracy: {test_accuracies[-1]:.2f}%")

if __name__ == '__main__':
    main()
