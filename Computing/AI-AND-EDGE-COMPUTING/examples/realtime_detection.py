"""
Real-time Detection Example - Continuous inference simulation

This example demonstrates real-time processing on edge devices:
- Continuous data stream processing
- Low-latency inference
- Real-time decision making
"""

import os
import sys
import time
import numpy as np
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def simulate_sensor_stream():
    """
    Simulate a real-time sensor data stream
    """
    import random
    
    return {
        'timestamp': datetime.now().isoformat(),
        'temperature': 20 + random.uniform(-5, 15),
        'vibration': random.uniform(0, 10),
        'sound_level': random.uniform(30, 90),
        'current': random.uniform(0.5, 3.0)
    }


def analyze_sensor_data(data: dict) -> dict:
    """
    Analyze sensor data for anomalies using simple rules
    (In production, this would use a trained ML model)
    
    Args:
        data: Sensor readings
        
    Returns:
        Analysis results
    """
    anomalies = []
    
    # Check thresholds
    if data['temperature'] > 30:
        anomalies.append('HIGH_TEMPERATURE')
    elif data['temperature'] < 18:
        anomalies.append('LOW_TEMPERATURE')
    
    if data['vibration'] > 7:
        anomalies.append('EXCESSIVE_VIBRATION')
    
    if data['sound_level'] > 80:
        anomalies.append('EXCESSIVE_NOISE')
    
    if data['current'] > 2.5:
        anomalies.append('HIGH_CURRENT')
    
    return {
        'timestamp': data['timestamp'],
        'status': 'ALERT' if anomalies else 'NORMAL',
        'anomalies': anomalies,
        'sensor_data': data
    }


def run_realtime_detection(duration_seconds: int = 30):
    """
    Run real-time detection simulation
    
    Args:
        duration_seconds: How long to run the simulation
    """
    print("\n" + "="*60)
    print("Real-time Edge Detection Demo")
    print("="*60)
    
    print(f"\nSimulating real-time sensor monitoring for {duration_seconds} seconds")
    print("Processing interval: ~100ms (10 Hz)")
    print("\nPress Ctrl+C to stop...\n")
    
    # Statistics
    total_samples = 0
    total_alerts = 0
    processing_times = []
    
    start_time = time.time()
    
    try:
        while (time.time() - start_time) < duration_seconds:
            iteration_start = time.perf_counter()
            
            # Simulate sensor reading
            sensor_data = simulate_sensor_stream()
            
            # Analyze data (edge inference)
            analysis_start = time.perf_counter()
            result = analyze_sensor_data(sensor_data)
            analysis_time = (time.perf_counter() - analysis_start) * 1000
            
            processing_times.append(analysis_time)
            total_samples += 1
            
            # Display result
            if result['status'] == 'ALERT':
                total_alerts += 1
                print(f"\n🚨 ALERT [{result['timestamp']}]")
                print(f"   Anomalies: {', '.join(result['anomalies'])}")
                print(f"   Temperature: {sensor_data['temperature']:.1f}°C")
                print(f"   Vibration: {sensor_data['vibration']:.1f}")
                print(f"   Sound: {sensor_data['sound_level']:.1f} dB")
                print(f"   Current: {sensor_data['current']:.2f} A")
                print(f"   Processing time: {analysis_time:.2f} ms")
            else:
                # Show normal status every 10 samples
                if total_samples % 10 == 0:
                    print(f"✓ Sample {total_samples}: Normal (processing: {analysis_time:.2f} ms)")
            
            # Calculate time to wait for ~100ms intervals
            iteration_time = (time.perf_counter() - iteration_start) * 1000
            wait_time = max(0, 100 - iteration_time) / 1000
            time.sleep(wait_time)
        
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    
    # Print statistics
    print("\n" + "="*60)
    print("Detection Statistics")
    print("="*60)
    
    elapsed_time = time.time() - start_time
    
    print(f"Duration: {elapsed_time:.2f} seconds")
    print(f"Total samples processed: {total_samples}")
    print(f"Total alerts: {total_alerts}")
    print(f"Alert rate: {(total_alerts/total_samples)*100:.1f}%")
    
    if processing_times:
        avg_time = np.mean(processing_times)
        max_time = np.max(processing_times)
        min_time = np.min(processing_times)
        
        print(f"\nProcessing Performance:")
        print(f"  Average latency: {avg_time:.2f} ms")
        print(f"  Min latency: {min_time:.2f} ms")
        print(f"  Max latency: {max_time:.2f} ms")
        print(f"  Throughput: {total_samples/elapsed_time:.1f} samples/second")
    
    print("="*60 + "\n")


def run_image_detection_simulation():
    """
    Simulate real-time image detection
    """
    print("\n" + "="*60)
    print("Real-time Image Detection Simulation")
    print("="*60)
    
    try:
        import tensorflow as tf
        print(f"\nTensorFlow version: {tf.__version__}")
    except ImportError:
        print("\n✗ TensorFlow not installed")
        print("Falling back to sensor-based detection...")
        return run_realtime_detection()
    
    model_path = "models/sample_model.tflite"
    
    if not os.path.exists(model_path):
        print(f"\n✗ Model not found at: {model_path}")
        print("Run model_converter.py to create a sample model first.")
        print("\nFalling back to sensor-based detection...")
        return run_realtime_detection()
    
    print("\nLoading model...")
    
    try:
        # Load model
        interpreter = tf.lite.Interpreter(model_path=model_path)
        interpreter.allocate_tensors()
        
        input_details = interpreter.get_input_details()
        input_shape = input_details[0]['shape']
        
        print(f"✓ Model loaded (input shape: {input_shape})")
        
        # Simulate continuous image stream
        print("\nSimulating image stream (30 seconds)...")
        print("Processing synthetic frames at ~10 FPS\n")
        
        start_time = time.time()
        frame_count = 0
        
        while (time.time() - start_time) < 30:
            frame_start = time.perf_counter()
            
            # Generate synthetic frame
            frame = np.random.random(input_shape).astype(np.float32)
            
            # Run inference
            interpreter.set_tensor(input_details[0]['index'], frame)
            interpreter.invoke()
            
            frame_time = (time.perf_counter() - frame_start) * 1000
            frame_count += 1
            
            if frame_count % 10 == 0:
                print(f"Frame {frame_count}: {frame_time:.2f} ms")
            
            # Target 10 FPS
            time.sleep(max(0, (100 - frame_time) / 1000))
        
        elapsed = time.time() - start_time
        fps = frame_count / elapsed
        
        print(f"\n✓ Processed {frame_count} frames in {elapsed:.2f} seconds")
        print(f"  Average FPS: {fps:.1f}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nFalling back to sensor-based detection...")
        return run_realtime_detection()
    
    print("\n" + "="*60 + "\n")


def main():
    """Main function"""
    print("\nChoose detection mode:")
    print("1. Sensor-based detection (default)")
    print("2. Image-based detection (requires model)")
    
    # For automated demo, run sensor-based
    print("\nRunning sensor-based real-time detection...\n")
    run_realtime_detection(duration_seconds=30)


if __name__ == "__main__":
    main()
