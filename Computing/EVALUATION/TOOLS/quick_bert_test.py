#!/usr/bin/env python3
"""
Quick BERT Test - Minimal test to verify BERT fine-tuning setup works
"""

import torch
from transformers import BertForSequenceClassification, BertTokenizer
from torch.optim import AdamW

def quick_bert_test():
    """Run a minimal test to ensure BERT setup is working"""
    
    print("🚀 QUICK BERT SETUP TEST")
    print("="*40)
    
    try:
        # Test device
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Device: {device}")
        
        # Test model loading
        print("Loading BERT model...")
        model = BertForSequenceClassification.from_pretrained(
            'bert-base-uncased',
            num_labels=2,
            return_dict=True
        )
        model.to(device)
        print("✅ Model loaded successfully")
        
        # Test tokenizer
        print("Loading tokenizer...")
        tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        print("✅ Tokenizer loaded successfully")
        
        # Test optimizer
        print("Creating optimizer...")
        optimizer = AdamW(model.parameters(), lr=2e-5)
        print("✅ Optimizer created successfully")
        
        # Test forward pass
        print("Testing forward pass...")
        test_text = "This is a positive sentiment test"
        inputs = tokenizer(
            test_text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=128
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            prediction = torch.argmax(logits, dim=-1)
            
        print(f"✅ Forward pass successful")
        print(f"   Input shape: {inputs['input_ids'].shape}")
        print(f"   Output shape: {logits.shape}")
        print(f"   Prediction: {prediction.item()}")
        
        # Test backward pass
        print("Testing backward pass...")
        model.train()
        
        # Create dummy labels
        labels = torch.tensor([1]).to(device)  # Positive sentiment
        
        # Forward pass with labels for loss
        outputs = model(**inputs, labels=labels)
        loss = outputs.loss
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        print(f"✅ Backward pass successful")
        print(f"   Loss: {loss.item():.4f}")
        
        print("\n🎉 ALL TESTS PASSED!")
        print("BERT fine-tuning setup is ready!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = quick_bert_test()
    if success:
        print("\n✅ Ready to run full fine-tuning:")
        print("   python src/bert_fine_tuning.py")
    else:
        print("\n❌ Setup needs fixing before fine-tuning")
