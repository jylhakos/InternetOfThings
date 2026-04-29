#!/usr/bin/env python3
"""
Modern Optimizer Guide for BERT Fine-tuning
Comprehensive comparison of optimizers for transformer models
"""

import torch
from transformers import optimization
import time

def test_available_optimizers():
    """Test and demonstrate available optimizers for BERT fine-tuning"""
    
    print("🔧 MODERN OPTIMIZERS FOR BERT FINE-TUNING")
    print("="*60)
    
    # Create a dummy model for testing
    from transformers import BertForSequenceClassification
    model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)
    
    optimizers_guide = {
        "torch_adamw": {
            "description": "PyTorch AdamW - Standard choice, moved from transformers",
            "import": "from torch.optim import AdamW",
            "usage": "AdamW(model.parameters(), lr=2e-5, weight_decay=0.01)",
            "pros": ["Stable", "Well-tested", "Good default choice"],
            "cons": ["Can be memory intensive"],
            "best_for": "General BERT fine-tuning"
        },
        
        "transformers_adafactor": {
            "description": "Adafactor - Memory efficient, good for large models",
            "import": "from transformers.optimization import Adafactor",
            "usage": "Adafactor(model.parameters(), scale_parameter=False, relative_step=False, lr=1e-3)",
            "pros": ["Memory efficient", "Good for large models", "Adaptive learning rate"],
            "cons": ["Can be unstable", "Requires tuning"],
            "best_for": "Large models with memory constraints"
        },
        
        "torch_adamax": {
            "description": "Adamax - Variant of Adam based on infinity norm",
            "import": "from torch.optim import Adamax",
            "usage": "Adamax(model.parameters(), lr=2e-3)",
            "pros": ["More stable than Adam", "Good for sparse gradients"],
            "cons": ["Less common", "May need lr tuning"],
            "best_for": "Sparse data or unstable training"
        },
        
        "torch_radam": {
            "description": "RAdam - Rectified Adam with warmup",
            "import": "from torch.optim import RAdam",
            "usage": "RAdam(model.parameters(), lr=2e-5)",
            "pros": ["Self-correcting", "No warmup needed", "Stable"],
            "cons": ["Newer, less tested"],
            "best_for": "When you want stability without manual warmup"
        },
        
        "torch_lamb": {
            "description": "LAMB - Layer-wise Adaptive Moments optimizer (if available)",
            "import": "# pip install pytorch-lamb\n# from pytorch_lamb import Lamb",
            "usage": "# Lamb(model.parameters(), lr=1e-3)",
            "pros": ["Good for large batch training", "Layer-wise adaptation"],
            "cons": ["Requires additional package", "More complex"],
            "best_for": "Large batch training scenarios"
        }
    }
    
    print("\n📊 OPTIMIZER COMPARISON TABLE")
    print("-"*80)
    print(f"{'Optimizer':<20} {'Memory':<10} {'Stability':<12} {'Performance':<12} {'Ease':<8}")
    print("-"*80)
    print(f"{'torch.optim.AdamW':<20} {'Medium':<10} {'High':<12} {'High':<12} {'Easy':<8}")
    print(f"{'Adafactor':<20} {'Low':<10} {'Medium':<12} {'High':<12} {'Medium':<8}")
    print(f"{'torch.optim.RAdam':<20} {'Medium':<10} {'High':<12} {'High':<12} {'Easy':<8}")
    print(f"{'torch.optim.Adamax':<20} {'Medium':<10} {'Medium':<12} {'Medium':<12} {'Easy':<8}")
    print(f"{'LAMB (external)':<20} {'Medium':<10} {'High':<12} {'High':<12} {'Hard':<8}")
    
    print("\n🎯 RECOMMENDATIONS BY USE CASE")
    print("-"*40)
    print("✅ **Default Choice**: torch.optim.AdamW")
    print("   - Most stable and well-tested")
    print("   - Good performance on most tasks")
    print("   - Easy to use with standard hyperparameters")
    print()
    print("🚀 **Large Models/Memory Constrained**: Adafactor")
    print("   - Significantly lower memory usage")
    print("   - Built into transformers library")
    print("   - Good for models > 1B parameters")
    print()
    print("🔬 **Research/Experimentation**: RAdam")
    print("   - Self-correcting behavior")
    print("   - No manual warmup required")
    print("   - More robust to hyperparameter choices")
    print()
    print("⚡ **Large Batch Training**: LAMB (external)")
    print("   - Designed for very large batch sizes")
    print("   - Layer-wise learning rate adaptation")
    print("   - Requires pip install pytorch-lamb")
    
    # Test imports
    print(f"\n🧪 TESTING OPTIMIZER AVAILABILITY")
    print("-"*35)
    
    # Test PyTorch AdamW
    try:
        from torch.optim import AdamW
        optimizer = AdamW(model.parameters(), lr=2e-5)
        print("✅ torch.optim.AdamW: Available and working")
    except Exception as e:
        print(f"❌ torch.optim.AdamW: {e}")
    
    # Test Adafactor
    try:
        from transformers.optimization import Adafactor
        optimizer = Adafactor(model.parameters(), scale_parameter=False, relative_step=False, lr=1e-3)
        print("✅ transformers.Adafactor: Available and working")
    except Exception as e:
        print(f"❌ transformers.Adafactor: {e}")
    
    # Test RAdam
    try:
        from torch.optim import RAdam
        optimizer = RAdam(model.parameters(), lr=2e-5)
        print("✅ torch.optim.RAdam: Available and working")
    except Exception as e:
        print(f"❌ torch.optim.RAdam: {e}")
    
    # Test Adamax
    try:
        from torch.optim import Adamax
        optimizer = Adamax(model.parameters(), lr=2e-3)
        print("✅ torch.optim.Adamax: Available and working")
    except Exception as e:
        print(f"❌ torch.optim.Adamax: {e}")
    
    print(f"\n💡 MODERN BERT FINE-TUNING SETUP (2025)")
    print("-"*45)
    print("""
# Option 1: Standard AdamW (Recommended for most cases)
from torch.optim import AdamW
from transformers import get_linear_schedule_with_warmup

optimizer = AdamW(
    model.parameters(),
    lr=2e-5,
    weight_decay=0.01,
    eps=1e-8
)

# Option 2: Adafactor for large models
from transformers.optimization import Adafactor

optimizer = Adafactor(
    model.parameters(),
    scale_parameter=False,
    relative_step=False,
    warmup_init=False,
    lr=1e-3
)

# Option 3: RAdam with built-in warmup
from torch.optim import RAdam

optimizer = RAdam(
    model.parameters(),
    lr=2e-5,
    weight_decay=0.01
)
""")

def generate_updated_bert_script():
    """Generate updated BERT fine-tuning script with modern optimizers"""
    
    script_content = '''
# Modern BERT Fine-tuning with Multiple Optimizer Options
import torch
from torch.optim import AdamW, RAdam, Adamax
from transformers import (
    BertForSequenceClassification, 
    BertTokenizer, 
    get_linear_schedule_with_warmup
)
from transformers.optimization import Adafactor

def create_optimizer(model, optimizer_name="adamw", learning_rate=2e-5):
    """
    Create optimizer based on specified type
    
    Args:
        model: The BERT model
        optimizer_name: One of ["adamw", "adafactor", "radam", "adamax"]
        learning_rate: Learning rate
        
    Returns:
        optimizer: Configured optimizer
    """
    
    if optimizer_name.lower() == "adamw":
        # Standard AdamW - Best general choice
        optimizer = AdamW(
            model.parameters(),
            lr=learning_rate,
            weight_decay=0.01,
            eps=1e-8,
            betas=(0.9, 0.999)
        )
        print(f"✅ Using AdamW optimizer (lr={learning_rate})")
        
    elif optimizer_name.lower() == "adafactor":
        # Adafactor - Memory efficient for large models
        optimizer = Adafactor(
            model.parameters(),
            scale_parameter=False,
            relative_step=False,
            warmup_init=False,
            lr=learning_rate
        )
        print(f"✅ Using Adafactor optimizer (lr={learning_rate})")
        
    elif optimizer_name.lower() == "radam":
        # RAdam - Self-correcting Adam
        optimizer = RAdam(
            model.parameters(),
            lr=learning_rate,
            weight_decay=0.01,
            eps=1e-8
        )
        print(f"✅ Using RAdam optimizer (lr={learning_rate})")
        
    elif optimizer_name.lower() == "adamax":
        # Adamax - Adam with infinity norm
        optimizer = Adamax(
            model.parameters(),
            lr=learning_rate * 10,  # Adamax typically needs higher LR
            weight_decay=0.01,
            eps=1e-8
        )
        print(f"✅ Using Adamax optimizer (lr={learning_rate * 10})")
        
    else:
        raise ValueError(f"Unknown optimizer: {optimizer_name}")
    
    return optimizer

# Example usage in training loop
def setup_training(model, optimizer_choice="adamw"):
    """Setup training with modern optimizer choices"""
    
    # Create optimizer
    optimizer = create_optimizer(model, optimizer_choice, learning_rate=2e-5)
    
    # Create scheduler (optional, but recommended)
    num_training_steps = 1000  # Adjust based on your data
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=num_training_steps * 0.1,  # 10% warmup
        num_training_steps=num_training_steps
    )
    
    return optimizer, scheduler
'''
    
    return script_content

if __name__ == "__main__":
    test_available_optimizers()
    print(f"\n📝 Updated script template generated!")
    print("Run this to see modern optimizer choices for BERT fine-tuning.")
