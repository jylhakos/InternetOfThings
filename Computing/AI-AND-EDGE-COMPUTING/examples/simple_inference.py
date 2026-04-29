"""
Simple Inference Example - Basic image classification on edge device

This example demonstrates the TensorFlow Lite workflow for edge computing:
1. Load a pre-converted .tflite model
2. Preprocess an image
3. Run inference
4. Display results
"""

import os
import sys
import numpy as np
from PIL import Image

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def run_simple_inference():
    """
    Run a simple inference example
    """
    print("\n" + "="*60)
    print("Simple Edge Inference Example")
    print("="*60)
    
    try:
        import tensorflow as tf
        print(f"\nTensorFlow version: {tf.__version__}")
    except ImportError:
        print("\n✗ TensorFlow not installed.")
        print("Run: pip install tensorflow")
        return
    
    # Define paths
    model_path = "models/sample_model.tflite"
    image_path = "data/sample_image.jpg"
    
    # Check if model exists
    if not os.path.exists(model_path):
        print(f"\n✗ Model not found at: {model_path}")
        print("\nCreating a sample model...")
        
        from src.model_converter import ModelConverter
        ModelConverter.create_sample_model(model_path)
    
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"\n✗ Image not found at: {image_path}")
        print("\nCreating a sample image...")
        create_sample_image(image_path)
    
    print("\n" + "-"*60)
    print("Step 1: Loading TFLite Model")
    print("-"*60)
    
    try:
        # Load the TFLite model
        interpreter = tf.lite.Interpreter(model_path=model_path)
        interpreter.allocate_tensors()
        
        # Get input and output details
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        print(f"✓ Model loaded successfully")
        print(f"  Input shape: {input_details[0]['shape']}")
        print(f"  Output shape: {output_details[0]['shape']}")
        
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        return
    
    print("\n" + "-"*60)
    print("Step 2: Preprocessing Image")
    print("-"*60)
    
    try:
        # Get target size from model
        target_size = (input_details[0]['shape'][1], input_details[0]['shape'][2])
        
        # Load and preprocess image
        img = Image.open(image_path).convert('RGB')
        print(f"✓ Original image size: {img.size}")
        
        img = img.resize(target_size)
        print(f"✓ Resized to: {target_size}")
        
        # Convert to array and normalize
        img_array = np.array(img, dtype=np.float32) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        print(f"✓ Preprocessed array shape: {img_array.shape}")
        
    except Exception as e:
        print(f"✗ Error preprocessing image: {e}")
        return
    
    print("\n" + "-"*60)
    print("Step 3: Running Inference")
    print("-"*60)
    
    try:
        import time
        
        # Warm-up run
        interpreter.set_tensor(input_details[0]['index'], img_array)
        interpreter.invoke()
        
        # Timed inference
        num_runs = 10
        times = []
        
        for _ in range(num_runs):
            start = time.perf_counter()
            interpreter.set_tensor(input_details[0]['index'], img_array)
            interpreter.invoke()
            end = time.perf_counter()
            times.append((end - start) * 1000)
        
        # Get output
        output_data = interpreter.get_tensor(output_details[0]['index'])
        
        avg_time = np.mean(times)
        print(f"✓ Inference completed")
        print(f"  Average inference time: {avg_time:.2f} ms ({num_runs} runs)")
        print(f"  Throughput: {1000/avg_time:.2f} inferences/second")
        
    except Exception as e:
        print(f"✗ Error during inference: {e}")
        return
    
    print("\n" + "-"*60)
    print("Step 4: Processing Results")
    print("-"*60)
    
    # Get predictions
    predictions = output_data[0]
    predicted_class = np.argmax(predictions)
    confidence = predictions[predicted_class]
    
    # Example class labels (for demonstration)
    class_labels = [
        'cat', 'dog', 'bird', 'fish', 'horse',
        'car', 'truck', 'airplane', 'ship', 'building'
    ]
    
    if predicted_class < len(class_labels):
        class_name = class_labels[predicted_class]
    else:
        class_name = f"Class {predicted_class}"
    
    print(f"✓ Prediction: {class_name}")
    print(f"  Confidence: {confidence:.2%}")
    print(f"  Class ID: {predicted_class}")
    
    # Show top 3 predictions
    top_indices = np.argsort(predictions)[-3:][::-1]
    print("\n  Top 3 predictions:")
    for i, idx in enumerate(top_indices, 1):
        label = class_labels[idx] if idx < len(class_labels) else f"Class {idx}"
        print(f"    {i}. {label}: {predictions[idx]:.2%}")
    
    print("\n" + "="*60)
    print("Inference completed successfully!")
    print("="*60 + "\n")


def create_sample_image(image_path: str):
    """
    Create a sample image for testing
    
    Args:
        image_path: Path to save the image
    """
    # Create a colorful test image
    img_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    
    # Add some patterns
    for i in range(0, 224, 20):
        img_array[i:i+10, :, :] = [100, 150, 200]
    
    img = Image.fromarray(img_array)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    
    img.save(image_path)
    print(f"✓ Sample image created at: {image_path}")


def main():
    """Main function"""
    run_simple_inference()


if __name__ == "__main__":
    main()
