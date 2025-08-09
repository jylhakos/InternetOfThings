"""
Flask API for RNN text generation.
"""

from flask import Flask, request, jsonify, send_from_directory
import torch
import time
import os
import logging
from datetime import datetime

from src.generate import load_model_and_vocab, generate_text


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Global variables for model and vocabulary
model = None
vocab = None
device = None
model_info = {}

def initialize_model(checkpoint_path, vocab_path=None):
    """
    Initialize the model and vocabulary.
    
    Args:
        checkpoint_path (str): Path to model checkpoint
        vocab_path (str): Path to vocabulary file
    """
    global model, vocab, device, model_info
    
    try:
        logger.info(f"Loading model from {checkpoint_path}")
        model, vocab, device = load_model_and_vocab(checkpoint_path, vocab_path)
        
        # Store model information
        checkpoint = torch.load(checkpoint_path, map_location=device)
        model_info = {
            'model_type': checkpoint['model_config']['model_type'],
            'vocab_size': len(vocab),
            'parameters': sum(p.numel() for p in model.parameters()),
            'embed_size': checkpoint['model_config']['embed_size'],
            'hidden_size': checkpoint['model_config']['hidden_size'],
            'num_layers': checkpoint['model_config']['num_layers'],
            'loaded_at': datetime.now().isoformat()
        }
        
        logger.info("Model loaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return False


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    """
    global model
    
    status = {
        'status': 'healthy' if model is not None else 'unhealthy',
        'timestamp': datetime.now().isoformat(),
        'model_loaded': model is not None
    }
    
    return jsonify(status), 200 if model is not None else 503


@app.route('/model/info', methods=['GET'])
def get_model_info():
    """
    Get model information.
    """
    global model_info
    
    if not model_info:
        return jsonify({'error': 'Model not loaded'}), 503
    
    return jsonify(model_info), 200


@app.route('/generate', methods=['POST'])
def generate_text_endpoint():
    """
    Generate text using the loaded model.
    """
    global model, vocab, device
    
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 503
    
    try:
        # Parse request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Extract parameters
        prompt = data.get('prompt', '')
        max_length = data.get('max_length', 50)
        temperature = data.get('temperature', 0.8)
        top_k = data.get('top_k', 40)
        
        # Validate parameters
        if not isinstance(prompt, str):
            return jsonify({'error': 'Prompt must be a string'}), 400
        
        if not isinstance(max_length, int) or max_length <= 0 or max_length > 500:
            return jsonify({'error': 'max_length must be an integer between 1 and 500'}), 400
        
        if not isinstance(temperature, (int, float)) or temperature <= 0 or temperature > 2.0:
            return jsonify({'error': 'temperature must be a number between 0 and 2.0'}), 400
        
        if top_k is not None and (not isinstance(top_k, int) or top_k <= 0):
            return jsonify({'error': 'top_k must be a positive integer or null'}), 400
        
        # Generate text
        start_time = time.time()
        
        generated_text = generate_text(
            model=model,
            vocab=vocab,
            prompt=prompt,
            max_length=max_length,
            temperature=float(temperature),
            top_k=top_k,
            device=device
        )
        
        generation_time = time.time() - start_time
        
        # Prepare response
        response = {
            'generated_text': generated_text,
            'prompt': prompt,
            'generation_time': round(generation_time, 3),
            'model': model_info.get('model_type', 'unknown'),
            'parameters': {
                'max_length': max_length,
                'temperature': temperature,
                'top_k': top_k
            },
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Generated text for prompt: '{prompt[:50]}...' in {generation_time:.3f}s")
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error generating text: {e}")
        return jsonify({'error': f'Generation failed: {str(e)}'}), 500


@app.route('/generate/multiple', methods=['POST'])
def generate_multiple_endpoint():
    """
    Generate multiple text samples.
    """
    global model, vocab, device
    
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 503
    
    try:
        # Parse request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Extract parameters
        prompt = data.get('prompt', '')
        max_length = data.get('max_length', 50)
        temperature = data.get('temperature', 0.8)
        top_k = data.get('top_k', 40)
        num_samples = data.get('num_samples', 3)
        
        # Validate parameters
        if not isinstance(num_samples, int) or num_samples <= 0 or num_samples > 10:
            return jsonify({'error': 'num_samples must be an integer between 1 and 10'}), 400
        
        # Generate multiple samples
        start_time = time.time()
        samples = []
        
        for i in range(num_samples):
            sample = generate_text(
                model=model,
                vocab=vocab,
                prompt=prompt,
                max_length=max_length,
                temperature=float(temperature),
                top_k=top_k,
                device=device
            )
            samples.append(sample)
        
        generation_time = time.time() - start_time
        
        # Prepare response
        response = {
            'samples': samples,
            'prompt': prompt,
            'num_samples': num_samples,
            'generation_time': round(generation_time, 3),
            'model': model_info.get('model_type', 'unknown'),
            'parameters': {
                'max_length': max_length,
                'temperature': temperature,
                'top_k': top_k
            },
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Generated {num_samples} samples for prompt: '{prompt[:50]}...' in {generation_time:.3f}s")
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error generating multiple samples: {e}")
        return jsonify({'error': f'Generation failed: {str(e)}'}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


def main():
    """
    Main function to run the Flask app.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='RNN Text Generation API Server')
    parser.add_argument('--checkpoint', type=str, required=True,
                        help='Path to model checkpoint')
    parser.add_argument('--vocab', type=str, default=None,
                        help='Path to vocabulary file')
    parser.add_argument('--host', type=str, default='localhost',
                        help='Host to run the server on')
    parser.add_argument('--port', type=int, default=5000,
                        help='Port to run the server on')
    parser.add_argument('--debug', action='store_true',
                        help='Run in debug mode')
    
    args = parser.parse_args()
    
    # Check if checkpoint exists
    if not os.path.exists(args.checkpoint):
        print(f"Error: Checkpoint file not found: {args.checkpoint}")
        return
    
    # Initialize model
    print("Initializing model...")
    success = initialize_model(args.checkpoint, args.vocab)
    
    if not success:
        print("Failed to initialize model. Exiting.")
        return
    
    print(f"Model initialized successfully!")
    print(f"Model type: {model_info['model_type']}")
    print(f"Vocabulary size: {model_info['vocab_size']:,}")
    print(f"Parameters: {model_info['parameters']:,}")
    print()
    print(f"Starting server on {args.host}:{args.port}")
    print("Available endpoints:")
    print("  GET  /health - Health check")
    print("  GET  /model/info - Model information")
    print("  POST /generate - Generate text")
    print("  POST /generate/multiple - Generate multiple samples")
    print()
    
    # Run Flask app
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
