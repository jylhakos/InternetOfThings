#!/usr/bin/env python3
"""
Kubeflow Pipeline for BERT Model Fine-tuning and Deployment

This pipeline implements a complete ML workflow:
1. Data preprocessing and validation
2. BERT model fine-tuning
3. Model evaluation and validation
4. Model deployment to serving infrastructure

Author: ML Pipeline Team
Date: 2025
"""

import kfp
from kfp import dsl
from kfp.components import create_component_from_func, InputPath, OutputPath
from typing import NamedTuple
import os


def data_preprocessing_op(
    data_path: str,
    output_data_path: OutputPath(str),
    test_size: float = 0.2,
    max_length: int = 128
) -> NamedTuple('Outputs', [('num_samples', int), ('num_classes', int)]):
    """
    Data preprocessing component for BERT training
    
    Args:
        data_path: Path to input data
        output_data_path: Path to save processed data
        test_size: Fraction of data for testing
        max_length: Maximum sequence length for tokenization
    
    Returns:
        NamedTuple with dataset statistics
    """
    import pandas as pd
    import numpy as np
    from sklearn.model_selection import train_test_split
    from transformers import BertTokenizer
    import pickle
    import os
    
    print("Starting data preprocessing...")
    
    # Initialize tokenizer
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    
    # Create sample data if none provided (for demo)
    if not os.path.exists(data_path):
        print("Creating sample dataset...")
        data = {
            'text': [
                "This is an excellent product!",
                "I love this item, highly recommended.",
                "Great quality and fast shipping.",
                "Amazing customer service experience.",
                "Best purchase I've made this year.",
                "Terrible quality, waste of money.",
                "Poor customer service, very disappointed.",
                "Product broke after one day.",
                "Not worth the price at all.",
                "Would not recommend to anyone.",
            ],
            'label': [1, 1, 1, 1, 1, 0, 0, 0, 0, 0]  # 1: positive, 0: negative
        }
        df = pd.DataFrame(data)
    else:
        df = pd.read_csv(data_path)
    
    # Basic data validation
    assert 'text' in df.columns, "Dataset must have 'text' column"
    assert 'label' in df.columns, "Dataset must have 'label' column"
    
    # Split data
    train_texts, test_texts, train_labels, test_labels = train_test_split(
        df['text'].tolist(),
        df['label'].tolist(),
        test_size=test_size,
        random_state=42,
        stratify=df['label']
    )
    
    # Tokenize data
    train_encodings = tokenizer(
        train_texts,
        truncation=True,
        padding=True,
        max_length=max_length,
        return_tensors='pt'
    )
    
    test_encodings = tokenizer(
        test_texts,
        truncation=True,
        padding=True,
        max_length=max_length,
        return_tensors='pt'
    )
    
    # Save processed data
    os.makedirs(output_data_path, exist_ok=True)
    
    processed_data = {
        'train_encodings': train_encodings,
        'test_encodings': test_encodings,
        'train_labels': train_labels,
        'test_labels': test_labels,
        'num_classes': len(set(df['label'])),
        'num_samples': len(df)
    }
    
    with open(os.path.join(output_data_path, 'processed_data.pkl'), 'wb') as f:
        pickle.dump(processed_data, f)
    
    print(f"Data preprocessing completed. Samples: {len(df)}, Classes: {len(set(df['label']))}")
    
    from collections import namedtuple
    outputs = namedtuple('Outputs', ['num_samples', 'num_classes'])
    return outputs(len(df), len(set(df['label'])))


def bert_training_op(
    data_path: InputPath(str),
    model_output_path: OutputPath(str),
    learning_rate: float = 2e-5,
    num_epochs: int = 3,
    batch_size: int = 16
) -> NamedTuple('Outputs', [('final_accuracy', float), ('training_loss', float)]):
    """
    BERT model fine-tuning component
    
    Args:
        data_path: Path to processed data
        model_output_path: Path to save trained model
        learning_rate: Learning rate for training
        num_epochs: Number of training epochs
        batch_size: Training batch size
    
    Returns:
        NamedTuple with training metrics
    """
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, TensorDataset
    from transformers import BertForSequenceClassification, AdamW
    import pickle
    import os
    
    print("Starting BERT fine-tuning...")
    
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Load processed data
    with open(os.path.join(data_path, 'processed_data.pkl'), 'rb') as f:
        data = pickle.load(f)
    
    # Create datasets
    train_dataset = TensorDataset(
        data['train_encodings']['input_ids'],
        data['train_encodings']['attention_mask'],
        torch.tensor(data['train_labels'])
    )
    
    test_dataset = TensorDataset(
        data['test_encodings']['input_ids'],
        data['test_encodings']['attention_mask'],
        torch.tensor(data['test_labels'])
    )
    
    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    # Initialize model
    model = BertForSequenceClassification.from_pretrained(
        'bert-base-uncased',
        num_labels=data['num_classes']
    ).to(device)
    
    # Initialize optimizer
    optimizer = AdamW(model.parameters(), lr=learning_rate)
    
    # Training loop
    model.train()
    total_loss = 0.0
    
    for epoch in range(num_epochs):
        epoch_loss = 0.0
        for batch in train_loader:
            input_ids, attention_mask, labels = [b.to(device) for b in batch]
            
            optimizer.zero_grad()
            
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
        
        avg_epoch_loss = epoch_loss / len(train_loader)
        total_loss += avg_epoch_loss
        print(f"Epoch {epoch + 1}/{num_epochs}, Loss: {avg_epoch_loss:.4f}")
    
    # Evaluation
    model.eval()
    correct = 0
    total = 0
    
    with torch.no_grad():
        for batch in test_loader:
            input_ids, attention_mask, labels = [b.to(device) for b in batch]
            
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            predictions = torch.argmax(outputs.logits, dim=1)
            
            total += labels.size(0)
            correct += (predictions == labels).sum().item()
    
    accuracy = correct / total
    avg_training_loss = total_loss / num_epochs
    
    print(f"Training completed. Final accuracy: {accuracy:.4f}")
    
    # Save model
    os.makedirs(model_output_path, exist_ok=True)
    model.save_pretrained(model_output_path)
    
    # Save tokenizer as well
    from transformers import BertTokenizer
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    tokenizer.save_pretrained(model_output_path)
    
    from collections import namedtuple
    outputs = namedtuple('Outputs', ['final_accuracy', 'training_loss'])
    return outputs(accuracy, avg_training_loss)


def model_evaluation_op(
    model_path: InputPath(str),
    data_path: InputPath(str),
    evaluation_output_path: OutputPath(str)
) -> NamedTuple('Outputs', [('accuracy', float), ('precision', float), ('recall', float), ('f1_score', float)]):
    """
    Model evaluation component
    
    Args:
        model_path: Path to trained model
        data_path: Path to processed data
        evaluation_output_path: Path to save evaluation results
    
    Returns:
        NamedTuple with evaluation metrics
    """
    import torch
    from torch.utils.data import DataLoader, TensorDataset
    from transformers import BertForSequenceClassification, BertTokenizer
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
    import pickle
    import json
    import os
    
    print("Starting model evaluation...")
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Load model
    model = BertForSequenceClassification.from_pretrained(model_path).to(device)
    model.eval()
    
    # Load test data
    with open(os.path.join(data_path, 'processed_data.pkl'), 'rb') as f:
        data = pickle.load(f)
    
    test_dataset = TensorDataset(
        data['test_encodings']['input_ids'],
        data['test_encodings']['attention_mask'],
        torch.tensor(data['test_labels'])
    )
    
    test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False)
    
    # Evaluate model
    all_predictions = []
    all_labels = []
    
    with torch.no_grad():
        for batch in test_loader:
            input_ids, attention_mask, labels = [b.to(device) for b in batch]
            
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            predictions = torch.argmax(outputs.logits, dim=1)
            
            all_predictions.extend(predictions.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    # Calculate metrics
    accuracy = accuracy_score(all_labels, all_predictions)
    precision, recall, f1, _ = precision_recall_fscore_support(
        all_labels, all_predictions, average='weighted'
    )
    
    # Generate detailed report
    report = classification_report(all_labels, all_predictions, output_dict=True)
    
    # Save evaluation results
    os.makedirs(evaluation_output_path, exist_ok=True)
    
    results = {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'detailed_report': report
    }
    
    with open(os.path.join(evaluation_output_path, 'evaluation_results.json'), 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation completed:")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1-Score: {f1:.4f}")
    
    from collections import namedtuple
    outputs = namedtuple('Outputs', ['accuracy', 'precision', 'recall', 'f1_score'])
    return outputs(accuracy, precision, recall, f1)


def model_deployment_op(
    model_path: InputPath(str),
    deployment_config: dict = None
) -> str:
    """
    Model deployment component
    
    Args:
        model_path: Path to trained model
        deployment_config: Deployment configuration
    
    Returns:
        Deployment status message
    """
    import os
    import yaml
    
    print("Starting model deployment...")
    
    if deployment_config is None:
        deployment_config = {
            'replicas': 2,
            'cpu_request': '500m',
            'memory_request': '1Gi',
            'cpu_limit': '1000m',
            'memory_limit': '2Gi'
        }
    
    # Create Kubernetes deployment manifest
    deployment_manifest = {
        'apiVersion': 'apps/v1',
        'kind': 'Deployment',
        'metadata': {
            'name': 'bert-model-serving',
            'labels': {'app': 'bert-model'}
        },
        'spec': {
            'replicas': deployment_config['replicas'],
            'selector': {'matchLabels': {'app': 'bert-model'}},
            'template': {
                'metadata': {'labels': {'app': 'bert-model'}},
                'spec': {
                    'containers': [{
                        'name': 'bert-serving',
                        'image': 'bert-pipeline:serving',
                        'ports': [{'containerPort': 8000}],
                        'resources': {
                            'requests': {
                                'cpu': deployment_config['cpu_request'],
                                'memory': deployment_config['memory_request']
                            },
                            'limits': {
                                'cpu': deployment_config['cpu_limit'],
                                'memory': deployment_config['memory_limit']
                            }
                        },
                        'env': [
                            {'name': 'MODEL_PATH', 'value': '/app/model'},
                            {'name': 'API_HOST', 'value': '0.0.0.0'},
                            {'name': 'API_PORT', 'value': '8000'}
                        ],
                        'volumeMounts': [{
                            'name': 'model-volume',
                            'mountPath': '/app/model'
                        }]
                    }],
                    'volumes': [{
                        'name': 'model-volume',
                        'persistentVolumeClaim': {
                            'claimName': 'bert-model-pvc'
                        }
                    }]
                }
            }
        }
    }
    
    # Service manifest
    service_manifest = {
        'apiVersion': 'v1',
        'kind': 'Service',
        'metadata': {
            'name': 'bert-model-service',
            'labels': {'app': 'bert-model'}
        },
        'spec': {
            'selector': {'app': 'bert-model'},
            'ports': [{
                'protocol': 'TCP',
                'port': 80,
                'targetPort': 8000
            }],
            'type': 'LoadBalancer'
        }
    }
    
    # Save manifests
    os.makedirs('/tmp/deployment', exist_ok=True)
    
    with open('/tmp/deployment/deployment.yaml', 'w') as f:
        yaml.dump(deployment_manifest, f)
    
    with open('/tmp/deployment/service.yaml', 'w') as f:
        yaml.dump(service_manifest, f)
    
    print("Deployment manifests created successfully")
    print(f"Model path: {model_path}")
    print(f"Deployment config: {deployment_config}")
    
    return "Model deployment manifests created successfully"


# Create Kubeflow components
data_preprocessing_component = create_component_from_func(
    data_preprocessing_op,
    output_component_file='components/data_preprocessing_component.yaml',
    base_image='python:3.9-slim',
    packages_to_install=['pandas==1.5.3', 'scikit-learn==1.3.0', 'transformers==4.30.0', 'torch==2.0.0']
)

bert_training_component = create_component_from_func(
    bert_training_op,
    output_component_file='components/bert_training_component.yaml',
    base_image='python:3.9-slim',
    packages_to_install=['torch==2.0.0', 'transformers==4.30.0', 'scikit-learn==1.3.0']
)

model_evaluation_component = create_component_from_func(
    model_evaluation_op,
    output_component_file='components/model_evaluation_component.yaml',
    base_image='python:3.9-slim',
    packages_to_install=['torch==2.0.0', 'transformers==4.30.0', 'scikit-learn==1.3.0']
)

model_deployment_component = create_component_from_func(
    model_deployment_op,
    output_component_file='components/model_deployment_component.yaml',
    base_image='python:3.9-slim',
    packages_to_install=['pyyaml==6.0']
)


@dsl.pipeline(
    name='BERT Fine-tuning Pipeline',
    description='Complete pipeline for BERT model fine-tuning, evaluation, and deployment'
)
def bert_pipeline(
    data_path: str = '',
    learning_rate: float = 2e-5,
    num_epochs: int = 3,
    batch_size: int = 16,
    test_size: float = 0.2,
    max_length: int = 128
):
    """
    Main pipeline definition
    
    Args:
        data_path: Path to training data
        learning_rate: Learning rate for training
        num_epochs: Number of training epochs
        batch_size: Training batch size
        test_size: Fraction of data for testing
        max_length: Maximum sequence length
    """
    
    # Step 1: Data preprocessing
    preprocessing_task = data_preprocessing_component(
        data_path=data_path,
        test_size=test_size,
        max_length=max_length
    )
    
    # Step 2: Model training
    training_task = bert_training_component(
        data_path=preprocessing_task.outputs['output_data_path'],
        learning_rate=learning_rate,
        num_epochs=num_epochs,
        batch_size=batch_size
    )
    training_task.after(preprocessing_task)
    
    # Step 3: Model evaluation
    evaluation_task = model_evaluation_component(
        model_path=training_task.outputs['model_output_path'],
        data_path=preprocessing_task.outputs['output_data_path']
    )
    evaluation_task.after(training_task)
    
    # Step 4: Model deployment (conditional on good performance)
    with dsl.Condition(evaluation_task.outputs['accuracy'] > 0.7):
        deployment_task = model_deployment_component(
            model_path=training_task.outputs['model_output_path']
        )
        deployment_task.after(evaluation_task)


if __name__ == '__main__':
    # Compile pipeline
    import kfp.compiler as compiler
    
    # Create components directory
    os.makedirs('components', exist_ok=True)
    
    # Compile the pipeline
    compiler.Compiler().compile(bert_pipeline, 'bert_pipeline.yaml')
    
    print("Pipeline compiled successfully!")
    print("Upload 'bert_pipeline.yaml' to Kubeflow UI to run the pipeline.")
    
    # Optional: Submit pipeline run programmatically
    # This requires proper authentication setup
    try:
        # Initialize client (adjust host as needed)
        client = kfp.Client(host='http://localhost:8080')
        
        # Create experiment
        experiment = client.create_experiment('BERT Fine-tuning Experiment')
        
        # Submit pipeline run
        run = client.run_pipeline(
            experiment.id,
            'BERT Pipeline Run',
            'bert_pipeline.yaml',
            params={
                'learning_rate': 2e-5,
                'num_epochs': 3,
                'batch_size': 16
            }
        )
        
        print(f"Pipeline run submitted: {run.id}")
        print(f"Monitor at: http://localhost:8080/#/runs/details/{run.id}")
        
    except Exception as e:
        print(f"Could not submit pipeline automatically: {e}")
        print("Please upload 'bert_pipeline.yaml' manually to Kubeflow UI")
