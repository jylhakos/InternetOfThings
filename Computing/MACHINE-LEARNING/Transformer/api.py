from flask import Flask, request, jsonify
import torch
import logging
import os
from generate import TextGenerator, load_model_and_vocab


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Global variables for models
generators = {}
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def initialize_models():
    """Initialize all available models."""
    global generators
    
    model_types = ['hybrid', 'transformer', 'rnn']
    vocab_path = 'vocab.pkl'
    
    for model_type in model_types:
        try:
            model_path = f'checkpoints_{model_type}/best_model.pt'
            
            if os.path.exists(model_path) and os.path.exists(vocab_path):
                logger.info(f"Loading {model_type} model...")
                model, vocab = load_model_and_vocab(model_path, vocab_path, model_type)
                generators[model_type] = TextGenerator(model, vocab, device)
                logger.info(f"Successfully loaded {model_type} model")
            else:
                logger.warning(f"Model files not found for {model_type}")
                
        except Exception as e:
            logger.error(f"Failed to load {model_type} model: {e}")
    
    if not generators:
        logger.error("No models could be loaded!")
        return False
    
    logger.info(f"Loaded {len(generators)} models: {list(generators.keys())}")
    return True


@app.route('/')
def home():
    """Home endpoint with API information."""
    return jsonify({
        'message': 'RNN + Transformer Language Model API',
        'available_models': list(generators.keys()),
        'endpoints': {
            '/generate': 'POST - Generate text with specified model',
            '/models': 'GET - List available models',
            '/health': 'GET - Health check'
        },
        'usage': {
            'generate_text': {
                'url': '/generate',
                'method': 'POST',
                'parameters': {
                    'model_type': 'Model type (hybrid, transformer, rnn)',
                    'prompt': 'Text prompt (optional)',
                    'max_length': 'Maximum length (default: 100)',
                    'temperature': 'Sampling temperature (default: 0.8)',
                    'top_k': 'Top-k sampling (default: 50)'
                }
            }
        }
    })


@app.route('/models', methods=['GET'])
def list_models():
    """List available models."""
    return jsonify({
        'available_models': list(generators.keys()),
        'device': str(device)
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'models_loaded': len(generators),
        'device': str(device)
    })


@app.route('/generate', methods=['POST'])
def generate_text():
    """Generate text using specified model."""
    try:
        # Parse request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Extract parameters
        model_type = data.get('model_type', 'hybrid')
        prompt = data.get('prompt', '')
        max_length = data.get('max_length', 100)
        temperature = data.get('temperature', 0.8)
        top_k = data.get('top_k', 50)
        top_p = data.get('top_p', 0.95)
        
        # Validate model type
        if model_type not in generators:
            available_models = list(generators.keys())
            return jsonify({
                'error': f'Model "{model_type}" not available',
                'available_models': available_models
            }), 400
        
        # Validate parameters
        if not isinstance(max_length, int) or max_length <= 0 or max_length > 1000:
            return jsonify({'error': 'max_length must be an integer between 1 and 1000'}), 400
        
        if not isinstance(temperature, (int, float)) or temperature <= 0 or temperature > 2:
            return jsonify({'error': 'temperature must be a number between 0 and 2'}), 400
        
        if not isinstance(top_k, int) or top_k <= 0 or top_k > 1000:
            return jsonify({'error': 'top_k must be an integer between 1 and 1000'}), 400
        
        # Generate text
        logger.info(f"Generating text with {model_type} model, prompt: '{prompt[:50]}...'")
        
        generator = generators[model_type]
        generated_text = generator.generate_text(
            prompt=prompt,
            max_length=max_length,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p
        )
        
        response = {
            'model_type': model_type,
            'prompt': prompt,
            'generated_text': generated_text,
            'parameters': {
                'max_length': max_length,
                'temperature': temperature,
                'top_k': top_k,
                'top_p': top_p
            },
            'device': str(device)
        }
        
        logger.info(f"Text generation completed for {model_type} model")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in text generation: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/compare', methods=['POST'])
def compare_models():
    """Compare text generation across all available models."""
    try:
        # Parse request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Extract parameters
        prompt = data.get('prompt', '')
        max_length = data.get('max_length', 50)
        temperature = data.get('temperature', 0.8)
        top_k = data.get('top_k', 50)
        
        # Validate parameters
        if not isinstance(max_length, int) or max_length <= 0 or max_length > 500:
            return jsonify({'error': 'max_length must be an integer between 1 and 500'}), 400
        
        # Generate text with all available models
        results = {}
        
        for model_type, generator in generators.items():
            try:
                generated_text = generator.generate_text(
                    prompt=prompt,
                    max_length=max_length,
                    temperature=temperature,
                    top_k=top_k
                )
                results[model_type] = generated_text
                
            except Exception as e:
                logger.error(f"Error generating with {model_type}: {e}")
                results[model_type] = f"Error: {str(e)}"
        
        response = {
            'prompt': prompt,
            'results': results,
            'parameters': {
                'max_length': max_length,
                'temperature': temperature,
                'top_k': top_k
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in model comparison: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Initialize models
    if not initialize_models():
        logger.error("Failed to initialize models. Please train models first.")
        exit(1)
    
    # Start Flask app
    logger.info("Starting Flask API server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
