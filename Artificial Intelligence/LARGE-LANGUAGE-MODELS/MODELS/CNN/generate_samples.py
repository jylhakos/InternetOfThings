#!/usr/bin/env python3
"""
Generate Sample Visualizations
==============================

This script creates sample PNG files to demonstrate what the training and inference
outputs will look like, without requiring a full training run.
"""

import matplotlib.pyplot as plt
import numpy as np

def create_sample_training_history():
    """Create a sample training history plot."""
    epochs = range(1, 11)
    
    # Simulated training data
    train_losses = [2.3, 0.8, 0.4, 0.3, 0.25, 0.2, 0.18, 0.16, 0.15, 0.14]
    test_losses = [2.2, 0.7, 0.35, 0.28, 0.22, 0.19, 0.17, 0.15, 0.14, 0.13]
    train_accuracies = [10, 75, 88, 92, 94, 96, 97, 98, 98.5, 99]
    test_accuracies = [12, 78, 90, 93, 95, 96.5, 97.5, 98.2, 98.8, 99.1]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    # Loss plot
    ax1.plot(epochs, train_losses, 'b-', marker='o', label='Training Loss')
    ax1.plot(epochs, test_losses, 'r-', marker='s', label='Test Loss')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.set_title('Training and Test Loss')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Accuracy plot
    ax2.plot(epochs, train_accuracies, 'b-', marker='o', label='Training Accuracy')
    ax2.plot(epochs, test_accuracies, 'r-', marker='s', label='Test Accuracy')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Accuracy (%)')
    ax2.set_title('Training and Test Accuracy')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 100)
    
    plt.tight_layout()
    plt.savefig('sample_training_history.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ Created: sample_training_history.png")

def create_sample_mnist_predictions():
    """Create sample MNIST prediction visualization."""
    fig, axes = plt.subplots(2, 4, figsize=(12, 6))
    axes = axes.ravel()
    
    # Sample digit images (simplified)
    np.random.seed(42)
    sample_digits = [7, 3, 4, 6, 1, 8, 1, 0]
    predictions = [7, 3, 4, 6, 1, 8, 1, 0]  # Perfect predictions for demo
    
    for i in range(8):
        # Create a simple digit-like pattern
        img = np.random.rand(28, 28) * 0.3
        
        # Add some structure to make it look more like a digit
        if sample_digits[i] == 0:
            img[8:20, 10:18] = 0.8
            img[12:16, 12:16] = 0.2
        elif sample_digits[i] == 1:
            img[6:22, 13:15] = 0.9
        elif sample_digits[i] == 3:
            img[8:12, 10:18] = 0.8
            img[14:16, 10:18] = 0.8
            img[18:22, 10:18] = 0.8
        else:
            # Generic pattern
            img[8:20, 8:20] = np.random.rand(12, 12) * 0.8
        
        axes[i].imshow(img, cmap='gray')
        
        # Color: green for correct, red for incorrect
        color = 'green' if sample_digits[i] == predictions[i] else 'red'
        axes[i].set_title(f'True: {sample_digits[i]}, Pred: {predictions[i]}', color=color)
        axes[i].axis('off')
    
    plt.tight_layout()
    plt.savefig('sample_mnist_predictions.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ Created: sample_mnist_predictions.png")

def create_sample_confidence_distribution():
    """Create sample confidence distribution plot."""
    digits = list(range(10))
    
    # Simulate confidence scores for predicting digit "7"
    probabilities = [0.02, 0.01, 0.05, 0.08, 0.03, 0.04, 0.02, 0.92, 0.01, 0.06]
    predicted_digit = 7
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(digits, probabilities, alpha=0.7)
    
    # Highlight the predicted digit
    bars[predicted_digit].set_color('red')
    bars[predicted_digit].set_alpha(1.0)
    
    plt.xlabel('Digit')
    plt.ylabel('Probability')
    plt.title('Sample Confidence Distribution (Predicted: 7)')
    plt.xticks(digits)
    plt.ylim(0, 1)
    
    # Add probability values on top of bars
    for i, prob in enumerate(probabilities):
        plt.text(i, prob + 0.02, f'{prob:.2f}', ha='center', va='bottom', fontsize=10)
    
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig('sample_confidence_distribution.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ Created: sample_confidence_distribution.png")

def create_sample_inference_demo():
    """Create sample inference demo visualization."""
    fig, axes = plt.subplots(2, 5, figsize=(15, 6))
    axes = axes.ravel()
    
    np.random.seed(123)
    sample_results = [
        (3, 3, 0.98), (7, 7, 0.95), (1, 1, 0.99), (0, 0, 0.97), (4, 4, 0.93),
        (1, 1, 0.96), (9, 9, 0.91), (5, 8, 0.67), (9, 9, 0.94), (2, 2, 0.99)
    ]
    
    for i, (true_label, pred_label, confidence) in enumerate(sample_results):
        # Generate sample digit pattern
        img = np.random.rand(28, 28) * 0.4
        
        # Add some structure based on the digit
        center_x, center_y = 14, 14
        if true_label == 0:
            y, x = np.ogrid[:28, :28]
            mask = ((x - center_x)**2 + (y - center_y)**2 < 64) & ((x - center_x)**2 + (y - center_y)**2 > 25)
            img[mask] = 0.9
        elif true_label == 1:
            img[4:24, 12:16] = 0.9
        else:
            # Generic pattern
            img[6:22, 6:22] = np.random.rand(16, 16) * 0.8
        
        axes[i].imshow(img, cmap='gray')
        
        # Color coding
        color = 'green' if true_label == pred_label else 'red'
        axes[i].set_title(f'True: {true_label}, Pred: {pred_label}\\nConf: {confidence:.2f}', 
                         color=color, fontsize=9)
        axes[i].axis('off')
    
    plt.suptitle('Sample Inference Results', fontsize=16, y=1.02)
    plt.tight_layout()
    plt.savefig('sample_inference_demo.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ Created: sample_inference_demo.png")

def create_cnn_architecture_diagram():
    """Create a CNN architecture visualization."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 6))
    
    # Define layer positions and sizes
    layers = [
        {'name': 'Input\\n28x28x1', 'pos': (1, 3), 'size': (0.8, 2), 'color': 'lightblue'},
        {'name': 'Conv1\\n28x28x32', 'pos': (3, 3), 'size': (0.8, 2), 'color': 'lightcoral'},
        {'name': 'Pool1\\n14x14x32', 'pos': (5, 3), 'size': (0.8, 1.5), 'color': 'lightgreen'},
        {'name': 'Conv2\\n14x14x64', 'pos': (7, 3), 'size': (0.8, 1.5), 'color': 'lightcoral'},
        {'name': 'Pool2\\n7x7x64', 'pos': (9, 3), 'size': (0.8, 1), 'color': 'lightgreen'},
        {'name': 'Flatten\\n3136', 'pos': (11, 3), 'size': (0.8, 0.5), 'color': 'lightyellow'},
        {'name': 'FC1\\n128', 'pos': (13, 3), 'size': (0.6, 0.8), 'color': 'plum'},
        {'name': 'FC2\\n10', 'pos': (15, 3), 'size': (0.4, 0.6), 'color': 'plum'}
    ]
    
    # Draw layers
    for layer in layers:
        rect = plt.Rectangle(
            (layer['pos'][0] - layer['size'][0]/2, layer['pos'][1] - layer['size'][1]/2),
            layer['size'][0], layer['size'][1],
            facecolor=layer['color'], edgecolor='black', linewidth=1
        )
        ax.add_patch(rect)
        
        # Add text
        ax.text(layer['pos'][0], layer['pos'][1], layer['name'], 
                ha='center', va='center', fontsize=9, weight='bold')
    
    # Draw arrows
    for i in range(len(layers) - 1):
        start_x = layers[i]['pos'][0] + layers[i]['size'][0]/2
        end_x = layers[i+1]['pos'][0] - layers[i+1]['size'][0]/2
        y = layers[i]['pos'][1]
        ax.annotate('', xy=(end_x, y), xytext=(start_x, y),
                   arrowprops=dict(arrowstyle='->', lw=1.5, color='black'))
    
    ax.set_xlim(0, 16)
    ax.set_ylim(1, 5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('CNN Architecture for MNIST Classification', fontsize=14, weight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig('sample_cnn_architecture.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ Created: sample_cnn_architecture.png")

def main():
    """Generate all sample visualizations."""
    print("🎨 Generating Sample Visualizations")
    print("=" * 50)
    print("Note: These are sample plots showing what the actual")
    print("training and inference outputs will look like.")
    print()
    
    try:
        create_sample_training_history()
        create_sample_mnist_predictions()
        create_sample_confidence_distribution()
        create_sample_inference_demo()
        create_cnn_architecture_diagram()
        
        print()
        print("🎉 All sample visualizations created!")
        print()
        print("📁 Generated files:")
        print("  • sample_training_history.png - Training progress curves")
        print("  • sample_mnist_predictions.png - Model predictions on digits")
        print("  • sample_confidence_distribution.png - Confidence scores")
        print("  • sample_inference_demo.png - Inference results")
        print("  • sample_cnn_architecture.png - Network architecture")
        print()
        print("🚀 To generate real plots, run:")
        print("  1. ./setup.sh (install dependencies)")
        print("  2. python mnist_cnn.py (train model)")
        print("  3. python inference_demo.py (run inference)")
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install matplotlib: pip install matplotlib")
    except Exception as e:
        print(f"❌ Error generating plots: {e}")

if __name__ == '__main__':
    main()
