"""
Feature Learning with PyTorch

A comprehensive project demonstrating feature learning techniques using:
- Convolutional Neural Networks (CNNs)
- Recurrent Neural Networks (RNNs) and Transformers  
- Autoencoders
- Transfer Learning

Author: Feature Learning Team
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Feature Learning Team"
__email__ = "team@example.com"

from . import data
from . import models  
from . import training
from . import utils
from . import evaluation

__all__ = [
    "data",
    "models", 
    "training",
    "utils",
    "evaluation",
]
