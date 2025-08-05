#!/usr/bin/env python3
"""
Simple BERT test script
"""

import torch
from transformers import BertTokenizer, BertForSequenceClassification

print("Testing BERT model loading and prediction...")

# Load pre-trained BERT model
model_name = 'bert-base-uncased'
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(model_name, num_labels=2)

# Simple test
text = "I love this product!"
print(f"Testing text: {text}")

# Tokenize
inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)
print(f"Tokenized input shape: {inputs['input_ids'].shape}")

# Get prediction
with torch.no_grad():
    outputs = model(**inputs)
    logits = outputs.logits
    prediction = torch.argmax(logits, dim=-1)
    probabilities = torch.softmax(logits, dim=-1)

print(f"Prediction: {prediction.item()}")
print(f"Probabilities: {probabilities.numpy()}")
print("✓ BERT model test completed successfully!")
