"""
Custom Image Inference Example
==============================

This script shows how to use the trained MNIST CNN model to predict
handwritten digits from custom images.
"""

import torch
import torchvision.transforms as transforms
from PIL import Image, ImageOps
import numpy as np
import matplotlib.pyplot as plt
from mnist_cnn import MNISTNet

def preprocess_custom_image(image_path):
    """
    Preprocess a custom image to match MNIST format.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        torch.Tensor: Preprocessed image tensor
    """
    # Open image
    img = Image.open(image_path).convert('L')  # Convert to grayscale
    
    # Invert colors if needed (MNIST has white digits on black background)
    # You might need to adjust this based on your image
    img = ImageOps.invert(img)
    
    # Resize to 28x28
    img = img.resize((28, 28), Image.LANCZOS)
    
    # Convert to numpy array and normalize
    img_array = np.array(img)
    
    # Apply the same transforms as training
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    # Convert back to PIL Image for transform
    img_pil = Image.fromarray(img_array)
    img_tensor = transform(img_pil).unsqueeze(0)  # Add batch dimension
    
    return img_tensor, img_array

def create_sample_digit(digit=5, save_path='sample_digit.png'):
    """
    Create a sample digit image for testing.
    
    Args:
        digit (int): Digit to create (0-9)
        save_path (str): Path to save the created image
    """
    # Create a simple digit image using matplotlib
    fig, ax = plt.subplots(figsize=(2, 2))
    ax.text(0.5, 0.5, str(digit), fontsize=60, ha='center', va='center',
            color='white', weight='bold')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_facecolor('black')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(save_path, facecolor='black', bbox_inches='tight', 
                pad_inches=0.1, dpi=50)
    plt.close()
    
    print(f"Sample digit '{digit}' saved to {save_path}")
    return save_path

def predict_custom_image(model_path, image_path, device='cpu'):
    """
    Predict digit from custom image.
    
    Args:
        model_path (str): Path to trained model
        image_path (str): Path to input image
        device (str): Device for inference
    """
    # Load model
    model = MNISTNet()
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()
    
    # Preprocess image
    img_tensor, img_array = preprocess_custom_image(image_path)
    img_tensor = img_tensor.to(device)
    
    # Make prediction
    with torch.no_grad():
        output = model(img_tensor)
        probabilities = torch.exp(output).cpu().numpy()[0]
        predicted_digit = output.argmax(dim=1).item()
        confidence = probabilities[predicted_digit]
    
    # Visualize results
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Show preprocessed image
    ax1.imshow(img_array, cmap='gray')
    ax1.set_title(f'Preprocessed Image\\nPredicted: {predicted_digit} (Confidence: {confidence:.3f})')
    ax1.axis('off')
    
    # Show probability distribution
    colors = ['red' if i == predicted_digit else 'blue' for i in range(10)]
    bars = ax2.bar(range(10), probabilities, color=colors, alpha=0.7)
    ax2.set_xlabel('Digit')
    ax2.set_ylabel('Probability')
    ax2.set_title('Prediction Probabilities')
    ax2.set_xticks(range(10))
    
    # Add probability values on bars
    for i, prob in enumerate(probabilities):
        ax2.text(i, prob + 0.01, f'{prob:.3f}', ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.savefig('custom_prediction.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    return predicted_digit, confidence, probabilities

def main():
    """Main function for custom image inference."""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model_path = 'mnist_cnn_model.pth'
    
    print("🔍 Custom Image Inference Demo")
    print("=" * 40)
    
    # Check if model exists
    try:
        # Create a sample digit for testing
        print("📝 Creating sample digit image...")
        sample_path = create_sample_digit(digit=7)
        
        # Predict the sample
        print(f"🤖 Predicting digit from {sample_path}...")
        predicted_digit, confidence, probabilities = predict_custom_image(
            model_path, sample_path, device
        )
        
        print(f"✅ Prediction: {predicted_digit}")
        print(f"🎯 Confidence: {confidence:.3f}")
        print(f"📊 Top 3 predictions:")
        
        # Sort probabilities to get top predictions
        top_indices = np.argsort(probabilities)[::-1][:3]
        for i, idx in enumerate(top_indices):
            print(f"   {i+1}. Digit {idx}: {probabilities[idx]:.3f}")
        
        print("\\n📸 Results saved as 'custom_prediction.png'")
        
        # Instructions for using custom images
        print("\\n💡 To use your own images:")
        print("1. Prepare a 28x28 grayscale image of a handwritten digit")
        print("2. Make sure the digit is white/bright on dark background")
        print("3. Call: predict_custom_image('mnist_cnn_model.pth', 'your_image.png')")
        
    except FileNotFoundError:
        print("❌ Model file 'mnist_cnn_model.pth' not found!")
        print("Please run 'python mnist_cnn.py' first to train the model.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()
