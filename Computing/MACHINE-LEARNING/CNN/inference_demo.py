"""
MNIST CNN Inference Demo
========================

This script demonstrates how to use a trained MNIST CNN model for inference
on new images or test samples.
"""

import torch
import torchvision.transforms as transforms
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from mnist_cnn import MNISTNet, get_data_loaders

def load_trained_model(model_path='mnist_cnn_model.pth', device='cpu'):
    """Load the trained model for inference."""
    model = MNISTNet()
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()
    return model

def preprocess_image(image_path):
    """
    Preprocess a custom image for MNIST prediction.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        torch.Tensor: Preprocessed image tensor
    """
    # Define the same transform used during training
    transform = transforms.Compose([
        transforms.Grayscale(num_output_channels=1),  # Convert to grayscale
        transforms.Resize((28, 28)),  # Resize to 28x28
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))  # MNIST normalization
    ])
    
    # Load and preprocess the image
    image = Image.open(image_path)
    image_tensor = transform(image).unsqueeze(0)  # Add batch dimension
    
    return image_tensor

def predict_digit(model, image_tensor, device='cpu'):
    """
    Predict the digit in the input image.
    
    Args:
        model: Trained MNIST model
        image_tensor: Preprocessed image tensor
        device: Device to run inference on
        
    Returns:
        tuple: (predicted_digit, confidence_scores)
    """
    image_tensor = image_tensor.to(device)
    
    with torch.no_grad():
        output = model(image_tensor)
        probabilities = torch.softmax(output, dim=1)
        predicted_digit = output.argmax(dim=1).item()
        confidence = probabilities[0][predicted_digit].item()
    
    return predicted_digit, probabilities[0].cpu().numpy()

def demo_test_samples(model, device, num_samples=10):
    """
    Demonstrate inference on test samples.
    
    Args:
        model: Trained model
        device: Device for inference
        num_samples: Number of test samples to show
    """
    # Get test data
    _, test_loader = get_data_loaders(batch_size=1000)
    
    # Get a batch of test data
    data_iter = iter(test_loader)
    images, labels = next(data_iter)
    
    # Select random samples
    indices = np.random.choice(len(images), num_samples, replace=False)
    
    fig, axes = plt.subplots(2, 5, figsize=(15, 6))
    axes = axes.ravel()
    
    print("Test Sample Predictions:")
    print("-" * 50)
    
    for i, idx in enumerate(indices):
        image = images[idx:idx+1]  # Keep batch dimension
        true_label = labels[idx].item()
        
        # Make prediction
        predicted_digit, probabilities = predict_digit(model, image, device)
        confidence = probabilities[predicted_digit]
        
        # Display results
        print(f"Sample {i+1}: True={true_label}, Predicted={predicted_digit}, "
              f"Confidence={confidence:.3f}")
        
        # Plot image
        img = image.squeeze().numpy()
        axes[i].imshow(img, cmap='gray')
        axes[i].set_title(f'True: {true_label}\nPred: {predicted_digit} ({confidence:.2f})')
        axes[i].axis('off')
    
    plt.tight_layout()
    plt.savefig('inference_demo.png', dpi=150, bbox_inches='tight')
    plt.show()

def show_confidence_distribution(probabilities):
    """
    Show confidence distribution for all digits.
    
    Args:
        probabilities: Array of probabilities for each digit (0-9)
    """
    digits = list(range(10))
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(digits, probabilities)
    plt.xlabel('Digit')
    plt.ylabel('Probability')
    plt.title('Confidence Distribution for Each Digit')
    plt.xticks(digits)
    
    # Highlight the predicted digit
    max_idx = np.argmax(probabilities)
    bars[max_idx].set_color('red')
    
    # Add probability values on top of bars
    for i, prob in enumerate(probabilities):
        plt.text(i, prob + 0.01, f'{prob:.3f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('confidence_distribution.png', dpi=150, bbox_inches='tight')
    plt.show()

def main():
    """Main inference demonstration."""
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Using device: {device}')
    
    try:
        # Load trained model
        print("Loading trained model...")
        model = load_trained_model('mnist_cnn_model.pth', device)
        print("Model loaded successfully!")
        
        # Demo on test samples
        print("\nRunning inference on test samples...")
        demo_test_samples(model, device, num_samples=10)
        
        print("\nInference demo completed!")
        print("Generated files:")
        print("- inference_demo.png: Visual results of predictions")
        print("- confidence_distribution.png: Confidence scores for each digit")
        
    except FileNotFoundError:
        print("Error: Model file 'mnist_cnn_model.pth' not found!")
        print("Please run 'python mnist_cnn.py' first to train the model.")
    except Exception as e:
        print(f"Error during inference: {e}")

if __name__ == '__main__':
    main()
