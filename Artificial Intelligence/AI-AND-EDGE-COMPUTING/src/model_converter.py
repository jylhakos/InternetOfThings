"""
Model Converter - Convert trained models to TensorFlow Lite format

This module provides utilities to convert TensorFlow/Keras models
to TensorFlow Lite format optimized for edge devices.
"""

import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelConverter:
    """
    Convert and optimize models for edge deployment
    """
    
    @staticmethod
    def convert_keras_to_tflite(
        model_path: str,
        output_path: str,
        quantize: bool = False
    ) -> bool:
        """
        Convert a Keras model to TensorFlow Lite format
        
        Args:
            model_path: Path to the saved Keras model (.h5 or SavedModel)
            output_path: Path to save the TFLite model
            quantize: Whether to apply quantization
            
        Returns:
            Success status
        """
        try:
            import tensorflow as tf
            
            logger.info(f"Loading model from {model_path}")
            
            # Load the model
            if model_path.endswith('.h5'):
                model = tf.keras.models.load_model(model_path)
                converter = tf.lite.TFLiteConverter.from_keras_model(model)
            else:
                converter = tf.lite.TFLiteConverter.from_saved_model(model_path)
            
            # Apply optimizations
            if quantize:
                logger.info("Applying post-training quantization")
                converter.optimizations = [tf.lite.Optimize.DEFAULT]
                converter.target_spec.supported_types = [tf.float16]
            
            # Convert the model
            logger.info("Converting model to TFLite format...")
            tflite_model = converter.convert()
            
            # Save the model
            with open(output_path, 'wb') as f:
                f.write(tflite_model)
            
            # Get file sizes
            original_size = os.path.getsize(model_path) / (1024 * 1024)
            tflite_size = os.path.getsize(output_path) / (1024 * 1024)
            
            logger.info(f"Conversion successful!")
            logger.info(f"Original size: {original_size:.2f} MB")
            logger.info(f"TFLite size: {tflite_size:.2f} MB")
            logger.info(f"Compression ratio: {original_size/tflite_size:.2f}x")
            
            return True
            
        except Exception as e:
            logger.error(f"Error converting model: {e}")
            return False
    
    @staticmethod
    def create_sample_model(output_path: str = "models/sample_model.tflite"):
        """
        Create a simple sample model for demonstration
        
        Args:
            output_path: Where to save the model
        """
        try:
            import tensorflow as tf
            
            logger.info("Creating sample model...")
            
            # Create a simple sequential model
            model = tf.keras.Sequential([
                tf.keras.layers.Input(shape=(224, 224, 3)),
                tf.keras.layers.Conv2D(32, (3, 3), activation='relu'),
                tf.keras.layers.MaxPooling2D((2, 2)),
                tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
                tf.keras.layers.MaxPooling2D((2, 2)),
                tf.keras.layers.Flatten(),
                tf.keras.layers.Dense(128, activation='relu'),
                tf.keras.layers.Dropout(0.5),
                tf.keras.layers.Dense(10, activation='softmax')
            ])
            
            # Compile the model
            model.compile(
                optimizer='adam',
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy']
            )
            
            logger.info("Model architecture created")
            model.summary()
            
            # Convert to TFLite
            converter = tf.lite.TFLiteConverter.from_keras_model(model)
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            tflite_model = converter.convert()
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save the model
            with open(output_path, 'wb') as f:
                f.write(tflite_model)
            
            logger.info(f"Sample model saved to {output_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating sample model: {e}")
            return False
    
    @staticmethod
    def benchmark_model(model_path: str, num_runs: int = 100):
        """
        Benchmark inference speed of a TFLite model
        
        Args:
            model_path: Path to the TFLite model
            num_runs: Number of inference runs
        """
        try:
            import tensorflow as tf
            import time
            import numpy as np
            
            logger.info(f"Benchmarking model: {model_path}")
            
            # Load model
            interpreter = tf.lite.Interpreter(model_path=model_path)
            interpreter.allocate_tensors()
            
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            
            # Create dummy input
            input_shape = input_details[0]['shape']
            dummy_input = np.random.random(input_shape).astype(np.float32)
            
            # Warmup
            for _ in range(10):
                interpreter.set_tensor(input_details[0]['index'], dummy_input)
                interpreter.invoke()
            
            # Benchmark
            times = []
            for _ in range(num_runs):
                start = time.perf_counter()
                interpreter.set_tensor(input_details[0]['index'], dummy_input)
                interpreter.invoke()
                end = time.perf_counter()
                times.append((end - start) * 1000)  # Convert to ms
            
            # Calculate statistics
            avg_time = np.mean(times)
            std_time = np.std(times)
            min_time = np.min(times)
            max_time = np.max(times)
            
            print("\n" + "="*50)
            print("Benchmark Results")
            print("="*50)
            print(f"Runs: {num_runs}")
            print(f"Average inference time: {avg_time:.2f} ms")
            print(f"Std deviation: {std_time:.2f} ms")
            print(f"Min time: {min_time:.2f} ms")
            print(f"Max time: {max_time:.2f} ms")
            print(f"Throughput: {1000/avg_time:.2f} inferences/second")
            print("="*50 + "\n")
            
        except Exception as e:
            logger.error(f"Error benchmarking model: {e}")


def main():
    """Main function"""
    print("\n" + "="*60)
    print("Model Converter for Edge Deployment")
    print("="*60)
    
    try:
        import tensorflow as tf
        print(f"\nTensorFlow version: {tf.__version__}")
    except ImportError:
        print("\nTensorFlow not installed. Run: pip install tensorflow")
        return
    
    print("\nAvailable operations:")
    print("1. Convert Keras model to TFLite")
    print("2. Create sample model")
    print("3. Benchmark model")
    
    print("\nExample usage:")
    print("  # Convert existing model")
    print("  converter = ModelConverter()")
    print("  converter.convert_keras_to_tflite('model.h5', 'model.tflite', quantize=True)")
    print("\n  # Create sample model")
    print("  converter.create_sample_model('models/sample_model.tflite')")
    
    # Create sample model for demonstration
    print("\nCreating sample model for demonstration...")
    ModelConverter.create_sample_model()
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
