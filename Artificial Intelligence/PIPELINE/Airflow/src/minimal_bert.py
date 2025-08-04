#!/usr/bin/env python3
"""
Minimal BERT Fine-tuning example
Demonstrates basic fine-tuning workflow with simplified error handling
"""

try:
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, TensorDataset
    from transformers import BertForSequenceClassification, BertTokenizer, AdamW
    print("✓ All libraries imported successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Please install required packages: pip install -r requirements.txt")
    exit(1)

def main():
    print("="*60)
    print("BERT FINE-TUNING FOR TEXT CLASSIFICATION")
    print("="*60)
    
    # Check device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    try:
        # Load model and tokenizer
        print("\\nLoading BERT model and tokenizer...")
        model_name = 'bert-base-uncased'
        tokenizer = BertTokenizer.from_pretrained(model_name)
        model = BertForSequenceClassification.from_pretrained(model_name, num_labels=2)
        model.to(device)
        print("Model loaded successfully")
        
        # Sample data (in real scenarios, load from files)
        texts = [
            "I absolutely love this product!",
            "This is terrible and doesn't work.",
            "Great quality and fast delivery.",
            "Worst purchase ever, waste of money.",
            "Pretty good, would recommend.",
            "Not satisfied with the quality."
        ]
        labels = [1, 0, 1, 0, 1, 0]  # 1=positive, 0=negative
        
        print(f"\\nTraining data: {len(texts)} samples")
        
        # Tokenize data
        print("Tokenizing input data...")
        inputs = tokenizer(texts, padding=True, truncation=True,return_tensors="pt", max_length=128)
        
        # Create dataset and dataloader
        dataset = TensorDataset(inputs['input_ids'], inputs['attention_mask'], torch.tensor(labels))
        dataloader = DataLoader(dataset, batch_size=2, shuffle=True)
        print(f"Created dataloader with batch size 2")
        
        # Setup optimizer
        optimizer = AdamW(model.parameters(), lr=2e-5)
        
        # Training loop
        print("\\nStarting fine-tuning...")
        model.train()
        num_epochs = 2  # Reduced for demonstration
        
        for epoch in range(num_epochs):
            total_loss = 0
            for batch_idx, batch in enumerate(dataloader):
                optimizer.zero_grad()
                
                input_ids, attention_mask, label = batch
                input_ids = input_ids.to(device)
                attention_mask = attention_mask.to(device)
                label = label.to(device)
                
                # Forward pass
                outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=label)
                loss = outputs.loss
                
                # Backward pass
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
                print(f"Epoch {epoch+1}/{num_epochs}, Batch {batch_idx+1}/{len(dataloader)}, Loss: {loss.item():.4f}")
            
            avg_loss = total_loss / len(dataloader)
            print(f"Epoch {epoch+1} completed. Average Loss: {avg_loss:.4f}")
        
        print("\\n✓ Fine-tuning completed!")
        
        # Test the model
        print("\\nTesting the fine-tuned model...")
        model.eval()
        
        test_texts = ["This is amazing!", "I hate this product."]
        test_labels = [1, 0]
        
        correct = 0
        with torch.no_grad():
            for i, text in enumerate(test_texts):
                inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
                inputs = {key: val.to(device) for key, val in inputs.items()}
                
                outputs = model(**inputs)
                prediction = torch.argmax(outputs.logits, dim=-1).cpu().numpy()[0]
                
                print(f"Text: '{text}'")
                print(f"True label: {test_labels[i]}, Predicted: {prediction}")
                print(f"Result: {'Correct' if prediction == test_labels[i] else '✗ Incorrect'}")
                
                if prediction == test_labels[i]:
                    correct += 1
                print()
        
        accuracy = correct / len(test_texts)
        print(f"Test Accuracy: {accuracy:.2f} ({correct}/{len(test_texts)})")
        
        # Save the model
        print("\\nSaving fine-tuned model...")
        model.save_pretrained("./fine_tuned_bert")
        tokenizer.save_pretrained("./fine_tuned_bert")
        print("Model saved to './fine_tuned_bert'")
        
        print("\\n" + "="*60)
        print("FINE-TUNING COMPLETED SUCCESSFULLY!")
        print("="*60)
        
    except Exception as e:
        print(f"\\n✗ Error during fine-tuning: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
