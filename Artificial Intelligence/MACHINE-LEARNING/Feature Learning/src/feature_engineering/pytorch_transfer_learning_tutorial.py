#!/usr/bin/env python3
"""
Transfer Learning (PyTorch)
==============================================

This script implements the PyTorch Transfer Learning for Computer Vision,
demonstrating how to use pre-trained ResNet-18 models for feature learning on the
Hymenoptera dataset (Ants vs Bees classification).

Tutorial Reference: https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html

Author: Feature Learning Project
License: MIT
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim import lr_scheduler
import numpy as np
import torchvision
from torchvision import datasets, models, transforms
import matplotlib.pyplot as plt
import time
import os
import copy
from PIL import Image
from tempfile import TemporaryDirectory
import argparse

# Set device
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")


def setup_data_transforms():
    """Setup data transformations following PyTorch tutorial standards"""
    data_transforms = {
        'train': transforms.Compose([
            transforms.RandomResizedCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
        'val': transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
    }
    return data_transforms


def load_hymenoptera_dataset(data_dir='data/hymenoptera_data'):
    """
    Load Hymenoptera dataset (Ants vs Bees)
    
    Download from: https://download.pytorch.org/tutorial/hymenoptera_data.zip
    Extract to data_dir
    """
    data_transforms = setup_data_transforms()
    
    try:
        image_datasets = {x: datasets.ImageFolder(os.path.join(data_dir, x), data_transforms[x])
                          for x in ['train', 'val']}
        dataloaders = {x: torch.utils.data.DataLoader(image_datasets[x], batch_size=4,
                                                     shuffle=True, num_workers=4)
                      for x in ['train', 'val']}
        dataset_sizes = {x: len(image_datasets[x]) for x in ['train', 'val']}
        class_names = image_datasets['train'].classes
        
        print(f"Dataset loaded successfully!")
        print(f"Classes: {class_names}")
        print(f"Training samples: {dataset_sizes['train']}")
        print(f"Validation samples: {dataset_sizes['val']}")
        
        return dataloaders, dataset_sizes, class_names
        
    except FileNotFoundError:
        print(f"❌ Dataset not found at {data_dir}")
        print("📥 Please download the Hymenoptera dataset:")
        print("   wget https://download.pytorch.org/tutorial/hymenoptera_data.zip")
        print("   unzip hymenoptera_data.zip -d data/")
        return None, None, None


def imshow(inp, title=None):
    """Display image for Tensor."""
    inp = inp.numpy().transpose((1, 2, 0))
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    inp = std * inp + mean
    inp = np.clip(inp, 0, 1)
    plt.imshow(inp)
    if title is not None:
        plt.title(title)
    plt.pause(0.001)


def visualize_dataset_samples(dataloaders, class_names):
    """Visualize a few training images"""
    # Get a batch of training data
    inputs, classes = next(iter(dataloaders['train']))

    # Make a grid from batch
    out = torchvision.utils.make_grid(inputs)

    plt.figure(figsize=(12, 8))
    imshow(out, title=[class_names[x] for x in classes])
    plt.title('Sample Training Images')
    plt.show()


def train_model(model, criterion, optimizer, scheduler, dataloaders, dataset_sizes, num_epochs=25):
    """
    Training function following PyTorch tutorial methodology
    """
    since = time.time()

    # Create a temporary directory to save training checkpoints
    with TemporaryDirectory() as tempdir:
        best_model_params_path = os.path.join(tempdir, 'best_model_params.pt')

        torch.save(model.state_dict(), best_model_params_path)
        best_acc = 0.0

        for epoch in range(num_epochs):
            print(f'Epoch {epoch}/{num_epochs - 1}')
            print('-' * 10)

            # Each epoch has a training and validation phase
            for phase in ['train', 'val']:
                if phase == 'train':
                    model.train()  # Set model to training mode
                else:
                    model.eval()   # Set model to evaluate mode

                running_loss = 0.0
                running_corrects = 0

                # Iterate over data
                for inputs, labels in dataloaders[phase]:
                    inputs = inputs.to(device)
                    labels = labels.to(device)

                    # Zero the parameter gradients
                    optimizer.zero_grad()

                    # Forward pass
                    # Track history if only in train
                    with torch.set_grad_enabled(phase == 'train'):
                        outputs = model(inputs)
                        _, preds = torch.max(outputs, 1)
                        loss = criterion(outputs, labels)

                        # Backward + optimize only if in training phase
                        if phase == 'train':
                            loss.backward()
                            optimizer.step()

                    # Statistics
                    running_loss += loss.item() * inputs.size(0)
                    running_corrects += torch.sum(preds == labels.data)
                    
                if phase == 'train':
                    scheduler.step()

                epoch_loss = running_loss / dataset_sizes[phase]
                epoch_acc = running_corrects.double() / dataset_sizes[phase]

                print(f'{phase} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}')

                # Deep copy the model
                if phase == 'val' and epoch_acc > best_acc:
                    best_acc = epoch_acc
                    torch.save(model.state_dict(), best_model_params_path)

            print()

        time_elapsed = time.time() - since
        print(f'Training complete in {time_elapsed // 60:.0f}m {time_elapsed % 60:.0f}s')
        print(f'Best val Acc: {best_acc:4f}')

        # Load best model weights
        model.load_state_dict(torch.load(best_model_params_path, weights_only=True))
    
    return model


def visualize_model_predictions(model, dataloaders, class_names, device, num_images=6):
    """Generic function to display predictions for a few images"""
    was_training = model.training
    model.eval()
    images_so_far = 0
    fig = plt.figure(figsize=(15, 10))

    with torch.no_grad():
        for i, (inputs, labels) in enumerate(dataloaders['val']):
            inputs = inputs.to(device)
            labels = labels.to(device)

            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)

            for j in range(inputs.size()[0]):
                images_so_far += 1
                ax = plt.subplot(num_images//2, 2, images_so_far)
                ax.axis('off')
                ax.set_title(f'predicted: {class_names[preds[j]]}')
                imshow(inputs.cpu().data[j])

                if images_so_far == num_images:
                    model.train(mode=was_training)
                    plt.tight_layout()
                    plt.show()
                    return
        model.train(mode=was_training)


def create_finetuning_model(num_classes=2):
    """
    Method 1: Finetuning the ConvNet
    Load a pretrained model and reset final fully connected layer.
    """
    print("🔧 Creating Fine-tuning Model (Method 1)")
    model_ft = models.resnet18(weights='IMAGENET1K_V1')
    num_ftrs = model_ft.fc.in_features
    # Here the size of each output sample is set to num_classes
    model_ft.fc = nn.Linear(num_ftrs, num_classes)

    model_ft = model_ft.to(device)

    criterion = nn.CrossEntropyLoss()
    
    # Observe that all parameters are being optimized
    optimizer_ft = optim.SGD(model_ft.parameters(), lr=0.001, momentum=0.9)

    # Decay LR by a factor of 0.1 every 7 epochs
    exp_lr_scheduler = lr_scheduler.StepLR(optimizer_ft, step_size=7, gamma=0.1)
    
    return model_ft, criterion, optimizer_ft, exp_lr_scheduler


def create_feature_extractor_model(num_classes=2):
    """
    Method 2: ConvNet as fixed feature extractor
    Freeze all the network except the final layer.
    """
    print("🔧 Creating Feature Extractor Model (Method 2)")
    model_conv = models.resnet18(weights='IMAGENET1K_V1')
    for param in model_conv.parameters():
        param.requires_grad = False

    # Parameters of newly constructed modules have requires_grad=True by default
    num_ftrs = model_conv.fc.in_features
    model_conv.fc = nn.Linear(num_ftrs, num_classes)

    model_conv = model_conv.to(device)

    criterion = nn.CrossEntropyLoss()

    # Observe that only parameters of final layer are being optimized
    optimizer_conv = optim.SGD(model_conv.fc.parameters(), lr=0.001, momentum=0.9)

    # Decay LR by a factor of 0.1 every 7 epochs
    exp_lr_scheduler = lr_scheduler.StepLR(optimizer_conv, step_size=7, gamma=0.1)
    
    return model_conv, criterion, optimizer_conv, exp_lr_scheduler


def extract_features(model, dataloader, device):
    """Extract features from pre-trained model"""
    model.eval()
    features_list = []
    labels_list = []
    
    with torch.no_grad():
        for inputs, labels in dataloader:
            inputs = inputs.to(device)
            
            # Remove final classification layer to get features
            features = model.avgpool(model.layer4(model.layer3(model.layer2(model.layer1(model.conv1(inputs))))))
            features = torch.flatten(features, 1)
            
            features_list.append(features.cpu().numpy())
            labels_list.append(labels.numpy())
    
    return np.vstack(features_list), np.hstack(labels_list)


def main():
    parser = argparse.ArgumentParser(description='PyTorch Transfer Learning Tutorial')
    parser.add_argument('--data-dir', default='data/hymenoptera_data', help='Dataset directory')
    parser.add_argument('--method', choices=['finetune', 'feature_extractor', 'both'], 
                       default='both', help='Transfer learning method')
    parser.add_argument('--epochs', type=int, default=25, help='Number of training epochs')
    parser.add_argument('--visualize', action='store_true', help='Visualize results')
    parser.add_argument('--extract-features', action='store_true', help='Extract and save features')
    
    args = parser.parse_args()
    
    print(" PyTorch Transfer Learning Tutorial")
    print("=" * 50)
    
    # Load dataset
    dataloaders, dataset_sizes, class_names = load_hymenoptera_dataset(args.data_dir)
    if dataloaders is None:
        return
    
    # Visualize some training images
    if args.visualize:
        print(" Visualizing dataset samples...")
        visualize_dataset_samples(dataloaders, class_names)
    
    if args.method in ['finetune', 'both']:
        print("\n Method 1: Fine-tuning the ConvNet")
        print("-" * 40)
        
        model_ft, criterion, optimizer_ft, exp_lr_scheduler = create_finetuning_model(len(class_names))
        
        # Train and evaluate
        model_ft = train_model(model_ft, criterion, optimizer_ft, exp_lr_scheduler, 
                              dataloaders, dataset_sizes, num_epochs=args.epochs)
        
        if args.visualize:
            print(" Visualizing fine-tuned model predictions...")
            visualize_model_predictions(model_ft, dataloaders, class_names, device)
        
        # Save model
        torch.save(model_ft.state_dict(), 'transfer_learning_finetuned.pth')
        print(" Fine-tuned model saved as 'transfer_learning_finetuned.pth'")
    
    if args.method in ['feature_extractor', 'both']:
        print("\n Method 2: ConvNet as fixed feature extractor")
        print("-" * 50)
        
        model_conv, criterion, optimizer_conv, exp_lr_scheduler = create_feature_extractor_model(len(class_names))
        
        # Train and evaluate
        model_conv = train_model(model_conv, criterion, optimizer_conv, exp_lr_scheduler, 
                                dataloaders, dataset_sizes, num_epochs=args.epochs)
        
        if args.visualize:
            print(" Visualizing feature extractor model predictions...")
            visualize_model_predictions(model_conv, dataloaders, class_names, device)
        
        # Save model
        torch.save(model_conv.state_dict(), 'transfer_learning_feature_extractor.pth')
        print(" Feature extractor model saved as 'transfer_learning_feature_extractor.pth'")
    
    if args.extract_features:
        print("\n Extracting features from pre-trained model...")
        model = models.resnet18(weights='IMAGENET1K_V1').to(device)
        
        train_features, train_labels = extract_features(model, dataloaders['train'], device)
        val_features, val_labels = extract_features(model, dataloaders['val'], device)
        
        np.save('hymenoptera_train_features.npy', train_features)
        np.save('hymenoptera_train_labels.npy', train_labels)
        np.save('hymenoptera_val_features.npy', val_features)
        np.save('hymenoptera_val_labels.npy', val_labels)
        
        print(f" Features saved:")
        print(f"   Training: {train_features.shape} features, {train_labels.shape} labels")
        print(f"   Validation: {val_features.shape} features, {val_labels.shape} labels")
    
    print("\n Transfer Learning Tutorial Complete!")
    print(" Tutorial Reference: https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html")


if __name__ == '__main__':
    main()
