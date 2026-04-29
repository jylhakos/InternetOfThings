#!/usr/bin/env python3
"""
Usage: This script demonstrates various ways to use the BERT fine-tuning project
"""

def show_usage_examples():
    print("="*70)
    print("BERT FINE-TUNING - USAGE EXAMPLES")
    print("="*70)
    
    examples = {
        "1. Environment Setup": [
            "# Create virtual environment",
            "python3 -m venv bert_env",
            "",
            "# Activate environment (Linux/Mac)",
            "source bert_env/bin/activate",
            "",
            "# Install dependencies", 
            "pip install -r requirements.txt"
        ],
        
        "2. Verify Installation": [
            "# Test environment setup",
            "python test_setup.py",
            "",
            "# Quick functionality test",
            "python simple_test.py"
        ],
        
        "3. Run Fine-tuning": [
            "# Basic fine-tuning (recommended for beginners)",
            "python src/minimal_bert.py",
            "",
            "# Advanced fine-tuning with more features",
            "python src/bert_fine_tuning.py"
        ],
        
        "4. Model Evaluation": [
            "# Comprehensive model evaluation",
            "python test_model.py",
            "",
            "# Interactive testing",
            "python test_model.py  # then choose interactive mode"
        ],
        
        "5. Custom Data Training": [
            "# Modify the texts and labels in minimal_bert.py:",
            "texts = ['Your positive text', 'Your negative text']",
            "labels = [1, 0]  # 1=positive, 0=negative",
            "",
            "# Or load from CSV file:",
            "import pandas as pd",
            "df = pd.read_csv('your_data.csv')",
            "texts = df['text'].tolist()",
            "labels = df['label'].tolist()"
        ],
        
        "6. Using Trained Model": [
            "from transformers import BertTokenizer, BertForSequenceClassification",
            "",
            "# Load your fine-tuned model",
            "model = BertForSequenceClassification.from_pretrained('./fine_tuned_bert')",
            "tokenizer = BertTokenizer.from_pretrained('./fine_tuned_bert')",
            "",
            "# Make predictions",
            "text = 'Your text here'",
            "inputs = tokenizer(text, return_tensors='pt')",
            "outputs = model(**inputs)",
            "prediction = torch.argmax(outputs.logits, dim=-1)"
        ]
    }
    
    for title, commands in examples.items():
        print(f"\n{title}:")
        print("-" * len(title))
        for cmd in commands:
            if cmd.startswith("#"):
                print(f"\033[92m{cmd}\033[0m")  # Green comments
            elif cmd == "":
                print()
            else:
                print(f"  {cmd}")
    
    print("\n" + "="*70)
    print("TROUBLESHOOTING TIPS:")
    print("="*70)
    
    troubleshooting = [
        "• Virtual environment not working? Try: python3 -m venv --clear bert_env",
        "• Import errors? Activate environment first: source bert_env/bin/activate", 
        "• Slow training? Consider using smaller batch sizes or fewer epochs",
        "• Out of memory? Reduce max_length in tokenizer or use CPU instead of GPU",
        "• Model not improving? Try different learning rates (1e-5, 5e-5) or more data"
    ]
    
    for tip in troubleshooting:
        print(tip)
    
    print("\n" + "="*70)

if __name__ == "__main__":
    show_usage_examples()
