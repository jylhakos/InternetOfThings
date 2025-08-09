"""
Unit tests for RNN models.
"""

import unittest
import torch
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from models.rnn_model import RNNLanguageModel, count_parameters, get_model
except ImportError as e:
    print(f"Warning: Could not import models due to missing dependencies: {e}")
    print("Please install PyTorch to run these tests.")
    
    class TestRNNModel(unittest.TestCase):
        def test_import_error(self):
            self.skipTest("PyTorch not available")


if 'models.rnn_model' in sys.modules:
    class TestRNNModel(unittest.TestCase):
        """Test cases for RNN language models."""
        
        def setUp(self):
            """Set up test fixtures."""
            self.vocab_size = 1000
            self.embed_size = 128
            self.hidden_size = 256
            self.num_layers = 2
            self.batch_size = 4
            self.seq_len = 10
        
        def test_lstm_model_creation(self):
            """Test LSTM model creation."""
            model = RNNLanguageModel(
                vocab_size=self.vocab_size,
                embed_size=self.embed_size,
                hidden_size=self.hidden_size,
                num_layers=self.num_layers,
                rnn_type='LSTM'
            )
            
            self.assertIsInstance(model, RNNLanguageModel)
            self.assertEqual(model.vocab_size, self.vocab_size)
            self.assertEqual(model.embed_size, self.embed_size)
            self.assertEqual(model.hidden_size, self.hidden_size)
        
        def test_model_forward_pass(self):
            """Test model forward pass."""
            model = RNNLanguageModel(
                vocab_size=self.vocab_size,
                embed_size=self.embed_size,
                hidden_size=self.hidden_size,
                num_layers=self.num_layers,
                rnn_type='LSTM'
            )
            
            # Create dummy input
            input_seq = torch.randint(0, self.vocab_size, (self.batch_size, self.seq_len))
            hidden = model.init_hidden(self.batch_size)
            
            # Forward pass
            output, new_hidden = model(input_seq, hidden)
            
            # Check output shape
            expected_shape = (self.batch_size, self.seq_len, self.vocab_size)
            self.assertEqual(output.shape, expected_shape)
        
        def test_different_rnn_types(self):
            """Test different RNN types."""
            for rnn_type in ['LSTM', 'GRU', 'RNN']:
                with self.subTest(rnn_type=rnn_type):
                    model = RNNLanguageModel(
                        vocab_size=self.vocab_size,
                        embed_size=self.embed_size,
                        hidden_size=self.hidden_size,
                        num_layers=self.num_layers,
                        rnn_type=rnn_type
                    )
                    
                    input_seq = torch.randint(0, self.vocab_size, (self.batch_size, self.seq_len))
                    hidden = model.init_hidden(self.batch_size)
                    
                    output, new_hidden = model(input_seq, hidden)
                    
                    expected_shape = (self.batch_size, self.seq_len, self.vocab_size)
                    self.assertEqual(output.shape, expected_shape)
        
        def test_parameter_counting(self):
            """Test parameter counting function."""
            model = RNNLanguageModel(
                vocab_size=self.vocab_size,
                embed_size=self.embed_size,
                hidden_size=self.hidden_size,
                num_layers=self.num_layers,
                rnn_type='LSTM'
            )
            
            param_count = count_parameters(model)
            self.assertIsInstance(param_count, int)
            self.assertGreater(param_count, 0)
        
        def test_get_model_factory(self):
            """Test model factory function."""
            model = get_model(
                'lstm',
                vocab_size=self.vocab_size,
                embed_size=self.embed_size,
                hidden_size=self.hidden_size,
                num_layers=self.num_layers
            )
            
            self.assertIsInstance(model, RNNLanguageModel)
        
        def test_tied_weights(self):
            """Test tied weights functionality."""
            # Should work when embed_size == hidden_size
            model = RNNLanguageModel(
                vocab_size=self.vocab_size,
                embed_size=256,
                hidden_size=256,  # Same as embed_size
                num_layers=self.num_layers,
                rnn_type='LSTM',
                tie_weights=True
            )
            
            # Check that weights are tied
            self.assertTrue(torch.equal(model.embedding.weight, model.output.weight))
        
        def test_tied_weights_error(self):
            """Test tied weights error when dimensions mismatch."""
            with self.assertRaises(ValueError):
                RNNLanguageModel(
                    vocab_size=self.vocab_size,
                    embed_size=128,
                    hidden_size=256,  # Different from embed_size
                    num_layers=self.num_layers,
                    rnn_type='LSTM',
                    tie_weights=True
                )


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
