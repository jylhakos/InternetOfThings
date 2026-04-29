#!/usr/bin/env python3
"""
Demo: Modern Optimizer Choices for BERT Fine-tuning
Shows how to switch between different optimizers in 2025
"""

import torch
from torch.optim import AdamW, RAdam, Adamax
from transformers.optimization import Adafactor
from transformers import BertForSequenceClassification, BertTokenizer
import time

def demo_optimizer_comparison():
    """Demonstrate different modern optimizers for BERT"""
    
    print("🚀 MODERN BERT OPTIMIZER DEMO (2025)")
    print("="*60)
    
    # Load a small BERT model for demo
    print("Loading BERT model...")
    model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)
    model.train()
    
    # Demo data
    dummy_loss = torch.tensor(2.5, requires_grad=True)
    
    optimizers_config = {
        "AdamW": {
            "optimizer": AdamW(model.parameters(), lr=2e-5, weight_decay=0.01),
            "description": "🎯 Default choice - Most stable and well-tested",
            "best_for": "General BERT fine-tuning, production use",
            "memory": "Medium",
            "stability": "⭐⭐⭐⭐⭐"
        },
        
        "Adafactor": {
            "optimizer": Adafactor(model.parameters(), scale_parameter=False, 
                                 relative_step=False, lr=1e-3),
            "description": "💾 Memory efficient - Great for large models",
            "best_for": "Large models, memory constraints, multi-GPU training",
            "memory": "⭐⭐⭐⭐⭐ (Very Low)",
            "stability": "⭐⭐⭐"
        },
        
        "RAdam": {
            "optimizer": RAdam(model.parameters(), lr=2e-5, weight_decay=0.01),
            "description": "🔬 Self-correcting - No manual warmup needed",
            "best_for": "Research, stable training without warmup tuning",
            "memory": "Medium",
            "stability": "⭐⭐⭐⭐⭐"
        },
        
        "Adamax": {
            "optimizer": Adamax(model.parameters(), lr=2e-3, weight_decay=0.01),
            "description": "⚡ Infinity norm - Good for sparse gradients",
            "best_for": "Sparse data, noisy gradients, unstable training",
            "memory": "Medium", 
            "stability": "⭐⭐⭐"
        }
    }
    
    print("\n📊 OPTIMIZER COMPARISON")
    print("-"*80)
    print(f"{'Optimizer':<12} {'Memory':<15} {'Stability':<15} {'Best Use Case':<30}")
    print("-"*80)
    
    for name, config in optimizers_config.items():
        print(f"{name:<12} {config['memory']:<15} {config['stability']:<15} {config['best_for'][:29]:<30}")
    
    print(f"\n🧪 TESTING OPTIMIZER FUNCTIONALITY")
    print("-"*45)
    
    for name, config in optimizers_config.items():
        print(f"\n{name}:")
        print(f"   {config['description']}")
        
        try:
            # Simulate one optimization step
            start_time = time.time()
            
            config['optimizer'].zero_grad()
            dummy_loss.backward(retain_graph=True)
            config['optimizer'].step()
            
            step_time = time.time() - start_time
            print(f"   ✅ Working - Step time: {step_time:.4f}s")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n💡 QUICK START EXAMPLES")
    print("-"*25)
    
    print("""
# 1. Default AdamW (Recommended)
from torch.optim import AdamW
optimizer = AdamW(model.parameters(), lr=2e-5, weight_decay=0.01)

# 2. Memory-efficient Adafactor  
from transformers.optimization import Adafactor
optimizer = Adafactor(model.parameters(), scale_parameter=False, 
                      relative_step=False, lr=1e-3)

# 3. Self-correcting RAdam
from torch.optim import RAdam
optimizer = RAdam(model.parameters(), lr=2e-5, weight_decay=0.01)

# 4. Sparse-friendly Adamax
from torch.optim import Adamax
optimizer = Adamax(model.parameters(), lr=2e-3, weight_decay=0.01)
""")
    
    print("\n🎯 RECOMMENDATIONS")
    print("-"*20)
    print("✅ **Start with AdamW** - Most reliable for general use")
    print("🔧 **Use Adafactor** - If you have memory constraints")
    print("🔬 **Try RAdam** - For research or if you want stability without warmup")
    print("⚡ **Consider Adamax** - If your data is sparse or training is unstable")
    
    print(f"\n🚀 To use in bert_fine_tuning.py:")
    print("   Change OPTIMIZER_TYPE = 'adamw' to your preferred choice!")

if __name__ == "__main__":
    demo_optimizer_comparison()
