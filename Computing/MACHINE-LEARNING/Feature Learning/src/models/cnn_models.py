"""
Convolutional Neural Network models for feature learning.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
from typing import Tuple, Optional


class SimpleCNN(nn.Module):
    """Simple CNN for MNIST-like datasets."""
    
    def __init__(self, num_classes: int = 10, num_channels: int = 1):
        super(SimpleCNN, self).__init__()
        
        self.features = nn.Sequential(
            # First convolutional block
            nn.Conv2d(num_channels, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            # Second convolutional block  
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            # Third convolutional block
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )
        
        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(128 * 3 * 3, 512),  # Assuming 28x28 input -> 3x3 after pooling
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x
    
    def extract_features(self, x: torch.Tensor) -> torch.Tensor:
        """Extract features from the penultimate layer."""
        x = self.features(x)
        x = torch.flatten(x, 1)
        x = self.classifier[:-1](x)  # Exclude final classification layer
        return x


class FeatureCNN(nn.Module):
    """CNN specifically designed for feature extraction."""
    
    def __init__(self, input_channels: int = 1, feature_dim: int = 256):
        super(FeatureCNN, self).__init__()
        
        self.feature_extractor = nn.Sequential(
            # Block 1
            nn.Conv2d(input_channels, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            # Block 2
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            # Block 3
            nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            # Global Average Pooling
            nn.AdaptiveAvgPool2d((1, 1))
        )
        
        self.feature_projection = nn.Sequential(
            nn.Linear(256, feature_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2)
        )
        
        self.feature_dim = feature_dim
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        features = self.extract_features(x)
        return features
    
    def extract_features(self, x: torch.Tensor) -> torch.Tensor:
        """Extract feature representations."""
        x = self.feature_extractor(x)
        x = torch.flatten(x, 1)
        features = self.feature_projection(x)
        return features


class ResNetFeatureExtractor(nn.Module):
    """ResNet-based feature extractor using transfer learning."""
    
    def __init__(self, pretrained: bool = True, feature_dim: int = 512, freeze_backbone: bool = True):
        super(ResNetFeatureExtractor, self).__init__()
        
        # Load pretrained ResNet
        self.backbone = models.resnet50(pretrained=pretrained)
        
        # Remove the final classification layer
        self.backbone.fc = nn.Identity()
        
        # Freeze backbone if specified
        if freeze_backbone:
            for param in self.backbone.parameters():
                param.requires_grad = False
        
        # Add custom feature projection layer
        self.feature_projection = nn.Sequential(
            nn.Linear(2048, feature_dim),  # ResNet50 has 2048 features
            nn.ReLU(inplace=True),
            nn.Dropout(0.3)
        )
        
        self.feature_dim = feature_dim
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Handle grayscale images by converting to RGB
        if x.size(1) == 1:
            x = x.repeat(1, 3, 1, 1)
        
        # Extract backbone features
        backbone_features = self.backbone(x)
        
        # Project to desired feature dimension
        features = self.feature_projection(backbone_features)
        
        return features
    
    def extract_features(self, x: torch.Tensor) -> torch.Tensor:
        """Extract feature representations."""
        return self.forward(x)


class CNNWithAttention(nn.Module):
    """CNN with attention mechanism for feature learning."""
    
    def __init__(self, input_channels: int = 1, num_classes: int = 10):
        super(CNNWithAttention, self).__init__()
        
        self.features = nn.Sequential(
            nn.Conv2d(input_channels, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True)
        )
        
        # Spatial attention mechanism
        self.spatial_attention = nn.Sequential(
            nn.Conv2d(256, 1, kernel_size=1),
            nn.Sigmoid()
        )
        
        # Channel attention mechanism
        self.channel_attention = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(256, 256//16, kernel_size=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(256//16, 256, kernel_size=1),
            nn.Sigmoid()
        )
        
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(256, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(128, num_classes)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Extract basic features
        features = self.features(x)
        
        # Apply attention mechanisms
        spatial_att = self.spatial_attention(features)
        channel_att = self.channel_attention(features)
        
        # Apply attention
        attended_features = features * spatial_att * channel_att
        
        # Classification
        output = self.classifier(attended_features)
        
        return output
    
    def extract_features(self, x: torch.Tensor) -> torch.Tensor:
        """Extract attention-weighted features."""
        features = self.features(x)
        
        spatial_att = self.spatial_attention(features)
        channel_att = self.channel_attention(features)
        
        attended_features = features * spatial_att * channel_att
        
        # Global average pooling to get feature vector
        pooled_features = F.adaptive_avg_pool2d(attended_features, 1)
        return torch.flatten(pooled_features, 1)


def create_cnn_model(model_type: str, **kwargs) -> nn.Module:
    """
    Factory function to create CNN models.
    
    Args:
        model_type: Type of model ('simple', 'feature', 'resnet', 'attention')
        **kwargs: Additional arguments for model initialization
        
    Returns:
        CNN model instance
    """
    if model_type == 'simple':
        return SimpleCNN(**kwargs)
    elif model_type == 'feature':
        return FeatureCNN(**kwargs)
    elif model_type == 'resnet':
        return ResNetFeatureExtractor(**kwargs)
    elif model_type == 'attention':
        return CNNWithAttention(**kwargs)
    else:
        raise ValueError(f"Unknown model type: {model_type}")


if __name__ == "__main__":
    # Test the models
    print("Testing CNN models...")
    
    # Test SimpleCNN
    model = SimpleCNN(num_classes=10, num_channels=1)
    x = torch.randn(4, 1, 28, 28)
    output = model(x)
    features = model.extract_features(x)
    print(f"SimpleCNN - Output shape: {output.shape}, Features shape: {features.shape}")
    
    # Test FeatureCNN
    model = FeatureCNN(input_channels=1, feature_dim=256)
    features = model(x)
    print(f"FeatureCNN - Features shape: {features.shape}")
    
    # Test ResNetFeatureExtractor
    model = ResNetFeatureExtractor(pretrained=False, feature_dim=512)
    features = model(x)
    print(f"ResNetFeatureExtractor - Features shape: {features.shape}")
    
    print("CNN models test completed!")
