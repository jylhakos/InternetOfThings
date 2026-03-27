"""
Image Classification on Edge Device using TensorFlow Lite

This module demonstrates how to perform image classification on edge devices
using optimized TensorFlow Lite models.
"""

import os
import numpy as np
from PIL import Image
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EdgeImageClassifier:
    """
    Image classifier optimized for edge devices
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialize the Edge Image Classifier
        
        Args:
            model_path: Path to the TFLite model file
        """
        self.model_path = model_path
        self.interpreter = None
        self.input_details = None
        self.output_details = None
        self.input_shape = None
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def load_model(self, model_path: str):
        """
        Load TensorFlow Lite model
        
        Args:
            model_path: Path to the .tflite model file
        """
        try:
            import tensorflow as tf
            
            self.interpreter = tf.lite.Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()
            
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            self.input_shape = self.input_details[0]['shape']
            
            logger.info(f"Model loaded successfully from {model_path}")
            logger.info(f"Input shape: {self.input_shape}")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess image for model input
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Preprocessed image array
        """
        # Get target size from model input shape
        target_size = (self.input_shape[1], self.input_shape[2])
        
        # Load and resize image
        img = Image.open(image_path).convert('RGB')
        img = img.resize(target_size)
        
        # Convert to numpy array and normalize
        img_array = np.array(img, dtype=np.float32)
        img_array = img_array / 255.0  # Normalize to [0, 1]
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    
    def predict(self, image_path: str) -> np.ndarray:
        """
        Run inference on an image
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Model predictions
        """
        if self.interpreter is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Preprocess image
        input_data = self.preprocess_image(image_path)
        
        # Run inference
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()
        
        # Get output
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
        
        return output_data
    
    def classify(self, image_path: str, class_labels: list = None) -> dict:
        """
        Classify an image and return results
        
        Args:
            image_path: Path to the image file
            class_labels: List of class labels (optional)
            
        Returns:
            Dictionary with classification results
        """
        predictions = self.predict(image_path)
        
        # Get top prediction
        predicted_class = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class])
        
        result = {
            'predicted_class': int(predicted_class),
            'confidence': confidence,
            'all_predictions': predictions[0].tolist()
        }
        
        if class_labels and predicted_class < len(class_labels):
            result['class_name'] = class_labels[predicted_class]
        
        logger.info(f"Classification result: Class {predicted_class}, Confidence: {confidence:.4f}")
        
        return result


def demo_without_model():
    """
    Demo function that simulates classification without a real model
    """
    print("\n" + "="*60)
    print("Edge Image Classification Demo")
    print("="*60)
    
    print("\nNOTE: This demo simulates classification without a real model.")
    print("To use a real model, follow these steps:")
    print("\n1. Train a model or download a pre-trained model")
    print("2. Convert it to TensorFlow Lite format (.tflite)")
    print("3. Place it in the models/ directory")
    print("4. Update the model_path in the code")
    
    # Simulate classification
    print("\n" + "-"*60)
    print("Simulating image classification...")
    print("-"*60)
    
    # Simulate predictions
    import random
    
    class_labels = ['cat', 'dog', 'bird', 'fish', 'horse']
    predicted_class = random.randint(0, len(class_labels) - 1)
    confidence = random.uniform(0.7, 0.99)
    
    print(f"\nImage: sample_image.jpg")
    print(f"Predicted Class: {class_labels[predicted_class]}")
    print(f"Confidence: {confidence:.2%}")
    
    print("\n" + "="*60)
    print("Demo completed!")
    print("="*60 + "\n")


def main():
    """Main function"""
    # Check if TensorFlow is available
    try:
        import tensorflow as tf
        print(f"TensorFlow version: {tf.__version__}")
    except ImportError:
        print("TensorFlow not installed. Run: pip install tensorflow")
        return
    
    # For now, run demo without model
    demo_without_model()
    
    print("\nTo run with a real model:")
    print("  classifier = EdgeImageClassifier('models/your_model.tflite')")
    print("  result = classifier.classify('data/sample_image.jpg')")


if __name__ == "__main__":
    main()
