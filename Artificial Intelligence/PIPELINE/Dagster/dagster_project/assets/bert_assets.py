"""
BERT Fine-tuning Assets for Dagster Pipeline
Contains all assets for data preparation, model training, evaluation, and deployment.
"""

import os
import json
import torch
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional

from dagster import (
    asset, 
    AssetExecutionContext, 
    MaterializeResult, 
    MetadataValue,
    Config,
    Backoff,
    Jitter,
    RetryPolicy
)

# Import existing BERT modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from bert_fine_tuning import (
    get_device_info,
    create_dummy_dataset,
    BertClassificationDataset,
    train_bert_model,
    evaluate_model,
    save_model_artifacts
)

# Retry policy for robust operations
RETRY_POLICY = RetryPolicy(
    max_retries=3,
    delay=1,
    backoff=Backoff.EXPONENTIAL,
    jitter=Jitter.PLUS_MINUS
)

class BertConfig(Config):
    """Configuration for BERT training parameters"""
    model_name: str = "bert-base-uncased"
    num_labels: int = 2
    max_length: int = 128
    batch_size: int = 16
    learning_rate: float = 2e-5
    epochs: int = 3
    dataset_size: int = 1000

@asset(
    description="Generate training dataset for BERT fine-tuning",
    group_name="data_preparation",
    retry_policy=RETRY_POLICY
)
def training_dataset(context: AssetExecutionContext, config: BertConfig) -> Dict[str, Any]:
    """
    Create training dataset for BERT fine-tuning.
    Returns dataset metadata and saves data to storage.
    """
    context.log.info("Creating training dataset for BERT fine-tuning")
    
    # Create dummy dataset (in production, this would load real data)
    texts, labels = create_dummy_dataset(size=config.dataset_size)
    
    # Create DataFrame for easier handling
    df = pd.DataFrame({
        'text': texts,
        'label': labels
    })
    
    # Save dataset to local storage
    output_dir = Path("data/training")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    dataset_path = output_dir / "training_data.csv"
    df.to_csv(dataset_path, index=False)
    
    context.log.info(f"Training dataset created with {len(texts)} samples")
    context.log.info(f"Dataset saved to: {dataset_path}")
    
    # Calculate dataset statistics
    label_counts = df['label'].value_counts().to_dict()
    avg_text_length = df['text'].str.len().mean()
    
    metadata = {
        "dataset_size": len(texts),
        "label_distribution": label_counts,
        "average_text_length": avg_text_length,
        "dataset_path": str(dataset_path),
        "positive_samples": int(label_counts.get(1, 0)),
        "negative_samples": int(label_counts.get(0, 0))
    }
    
    return MaterializeResult(
        metadata={
            "dataset_size": MetadataValue.int(metadata["dataset_size"]),
            "positive_samples": MetadataValue.int(metadata["positive_samples"]),
            "negative_samples": MetadataValue.int(metadata["negative_samples"]),
            "avg_text_length": MetadataValue.float(metadata["average_text_length"]),
            "dataset_path": MetadataValue.path(metadata["dataset_path"])
        },
        asset_materialization_data=metadata
    )

@asset(
    description="Fine-tune BERT model for text classification",
    group_name="model_training",
    deps=[training_dataset],
    retry_policy=RETRY_POLICY
)
def trained_bert_model(
    context: AssetExecutionContext, 
    config: BertConfig,
    training_dataset: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Fine-tune BERT model using the training dataset.
    """
    context.log.info("Starting BERT model fine-tuning")
    
    # Get device information
    device_info = get_device_info()
    context.log.info(f"Training on device: {device_info}")
    
    # Load training data
    dataset_path = training_dataset["dataset_path"]
    df = pd.read_csv(dataset_path)
    texts = df['text'].tolist()
    labels = df['label'].tolist()
    
    context.log.info(f"Loaded training data: {len(texts)} samples")
    
    # Train the model
    try:
        model, tokenizer, training_stats = train_bert_model(
            texts=texts,
            labels=labels,
            model_name=config.model_name,
            num_labels=config.num_labels,
            max_length=config.max_length,
            batch_size=config.batch_size,
            learning_rate=config.learning_rate,
            epochs=config.epochs
        )
        
        # Save model artifacts
        model_dir = Path("models/bert_fine_tuned")
        model_dir.mkdir(parents=True, exist_ok=True)
        
        model_path = save_model_artifacts(
            model=model,
            tokenizer=tokenizer,
            save_directory=str(model_dir),
            training_stats=training_stats
        )
        
        context.log.info(f"Model saved to: {model_path}")
        
        # Prepare metadata
        final_loss = training_stats['training_loss'][-1] if training_stats['training_loss'] else 0.0
        total_training_time = sum(training_stats.get('epoch_times', [0]))
        
        model_metadata = {
            "model_path": model_path,
            "model_name": config.model_name,
            "num_epochs": config.epochs,
            "batch_size": config.batch_size,
            "learning_rate": config.learning_rate,
            "final_training_loss": final_loss,
            "total_training_time": total_training_time,
            "training_samples": len(texts)
        }
        
        return MaterializeResult(
            metadata={
                "model_path": MetadataValue.path(model_metadata["model_path"]),
                "final_loss": MetadataValue.float(model_metadata["final_training_loss"]),
                "training_time_seconds": MetadataValue.float(model_metadata["total_training_time"]),
                "num_epochs": MetadataValue.int(model_metadata["num_epochs"]),
                "batch_size": MetadataValue.int(model_metadata["batch_size"]),
                "learning_rate": MetadataValue.float(model_metadata["learning_rate"])
            },
            asset_materialization_data=model_metadata
        )
        
    except Exception as e:
        context.log.error(f"Training failed: {str(e)}")
        raise

@asset(
    description="Evaluate the fine-tuned BERT model",
    group_name="model_evaluation",
    deps=[trained_bert_model, training_dataset],
    retry_policy=RETRY_POLICY
)
def model_evaluation(
    context: AssetExecutionContext,
    trained_bert_model: Dict[str, Any],
    training_dataset: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Evaluate the trained BERT model on test data.
    """
    context.log.info("Starting model evaluation")
    
    # Load the trained model
    model_path = trained_bert_model["model_path"]
    
    try:
        from transformers import BertForSequenceClassification, BertTokenizer
        
        model = BertForSequenceClassification.from_pretrained(model_path)
        tokenizer = BertTokenizer.from_pretrained(model_path)
        
        context.log.info(f"Loaded model from: {model_path}")
        
        # Create evaluation dataset (using a portion of training data for demo)
        dataset_path = training_dataset["dataset_path"]
        df = pd.read_csv(dataset_path)
        
        # Use last 20% of data for evaluation
        eval_size = int(len(df) * 0.2)
        eval_df = df.tail(eval_size)
        
        eval_texts = eval_df['text'].tolist()
        eval_labels = eval_df['label'].tolist()
        
        context.log.info(f"Evaluating on {len(eval_texts)} samples")
        
        # Evaluate the model
        eval_results = evaluate_model(
            model=model,
            tokenizer=tokenizer,
            texts=eval_texts,
            labels=eval_labels,
            batch_size=16
        )
        
        # Save evaluation results
        eval_dir = Path("results/evaluation")
        eval_dir.mkdir(parents=True, exist_ok=True)
        
        eval_results_path = eval_dir / "evaluation_results.json"
        with open(eval_results_path, 'w') as f:
            json.dump(eval_results, f, indent=2)
        
        context.log.info(f"Evaluation completed. Accuracy: {eval_results['accuracy']:.4f}")
        context.log.info(f"Results saved to: {eval_results_path}")
        
        evaluation_metadata = {
            "accuracy": eval_results["accuracy"],
            "precision": eval_results["precision"],
            "recall": eval_results["recall"],
            "f1_score": eval_results["f1_score"],
            "eval_samples": len(eval_texts),
            "results_path": str(eval_results_path)
        }
        
        return MaterializeResult(
            metadata={
                "accuracy": MetadataValue.float(evaluation_metadata["accuracy"]),
                "precision": MetadataValue.float(evaluation_metadata["precision"]),
                "recall": MetadataValue.float(evaluation_metadata["recall"]),
                "f1_score": MetadataValue.float(evaluation_metadata["f1_score"]),
                "eval_samples": MetadataValue.int(evaluation_metadata["eval_samples"]),
                "results_path": MetadataValue.path(evaluation_metadata["results_path"])
            },
            asset_materialization_data=evaluation_metadata
        )
        
    except Exception as e:
        context.log.error(f"Evaluation failed: {str(e)}")
        raise

@asset(
    description="Deploy BERT model for inference",
    group_name="model_deployment",
    deps=[trained_bert_model, model_evaluation],
    retry_policy=RETRY_POLICY
)
def deployed_model(
    context: AssetExecutionContext,
    trained_bert_model: Dict[str, Any],
    model_evaluation: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Deploy the trained BERT model for inference.
    """
    context.log.info("Starting model deployment")
    
    # Check if model meets quality threshold
    accuracy_threshold = 0.8
    model_accuracy = model_evaluation["accuracy"]
    
    if model_accuracy < accuracy_threshold:
        context.log.warning(f"Model accuracy {model_accuracy:.4f} below threshold {accuracy_threshold}")
        # In production, this might trigger model retraining or alert
    
    # Copy model to deployment directory
    model_path = trained_bert_model["model_path"]
    deploy_dir = Path("deployed_models/bert_classifier")
    deploy_dir.mkdir(parents=True, exist_ok=True)
    
    # In a real deployment, this would involve:
    # - Uploading to model registry (MLflow, S3, etc.)
    # - Creating deployment endpoints (SageMaker, Lambda, etc.)
    # - Updating API configurations
    
    # For demo, we'll create a deployment manifest
    deployment_manifest = {
        "model_name": "bert-text-classifier",
        "model_version": "1.0.0",
        "model_path": model_path,
        "accuracy": model_accuracy,
        "deployment_timestamp": pd.Timestamp.now().isoformat(),
        "deployment_status": "deployed",
        "endpoint_url": "http://localhost:8000/classify"  # API endpoint
    }
    
    manifest_path = deploy_dir / "deployment_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(deployment_manifest, f, indent=2)
    
    context.log.info(f"Model deployed successfully")
    context.log.info(f"Deployment manifest saved to: {manifest_path}")
    
    return MaterializeResult(
        metadata={
            "model_version": MetadataValue.text(deployment_manifest["model_version"]),
            "deployment_status": MetadataValue.text(deployment_manifest["deployment_status"]),
            "model_accuracy": MetadataValue.float(deployment_manifest["accuracy"]),
            "endpoint_url": MetadataValue.url(deployment_manifest["endpoint_url"]),
            "manifest_path": MetadataValue.path(str(manifest_path))
        },
        asset_materialization_data=deployment_manifest
    )

@asset(
    description="Run inference tests on deployed model",
    group_name="model_testing",
    deps=[deployed_model],
    retry_policy=RETRY_POLICY
)
def inference_tests(
    context: AssetExecutionContext,
    deployed_model: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Run inference tests on the deployed model.
    """
    context.log.info("Running inference tests")
    
    # Test data
    test_cases = [
        {"text": "I love this product! It's amazing!", "expected": 1},
        {"text": "This is terrible quality, very disappointed.", "expected": 0},
        {"text": "The service was okay, nothing special.", "expected": 0},
        {"text": "Excellent customer support and fast delivery!", "expected": 1},
        {"text": "Poor packaging, item arrived damaged.", "expected": 0}
    ]
    
    # Load deployed model for testing
    model_path = deployed_model["model_path"]
    
    try:
        from transformers import BertForSequenceClassification, BertTokenizer
        import torch.nn.functional as F
        
        model = BertForSequenceClassification.from_pretrained(model_path)
        tokenizer = BertTokenizer.from_pretrained(model_path)
        model.eval()
        
        test_results = []
        correct_predictions = 0
        
        for i, test_case in enumerate(test_cases):
            text = test_case["text"]
            expected = test_case["expected"]
            
            # Tokenize and predict
            inputs = tokenizer(
                text, 
                return_tensors="pt", 
                padding=True, 
                truncation=True, 
                max_length=128
            )
            
            with torch.no_grad():
                outputs = model(**inputs)
                probabilities = F.softmax(outputs.logits, dim=-1)
                prediction = torch.argmax(outputs.logits, dim=-1).item()
                confidence = probabilities[0][prediction].item()
            
            is_correct = prediction == expected
            if is_correct:
                correct_predictions += 1
            
            test_result = {
                "test_id": i + 1,
                "text": text,
                "prediction": prediction,
                "expected": expected,
                "confidence": confidence,
                "correct": is_correct
            }
            
            test_results.append(test_result)
            context.log.info(f"Test {i+1}: {'✓' if is_correct else '✗'} (confidence: {confidence:.3f})")
        
        # Calculate test metrics
        test_accuracy = correct_predictions / len(test_cases)
        avg_confidence = sum(r["confidence"] for r in test_results) / len(test_results)
        
        # Save test results
        results_dir = Path("results/inference_tests")
        results_dir.mkdir(parents=True, exist_ok=True)
        
        results_path = results_dir / "inference_test_results.json"
        test_summary = {
            "test_accuracy": test_accuracy,
            "avg_confidence": avg_confidence,
            "total_tests": len(test_cases),
            "correct_predictions": correct_predictions,
            "test_results": test_results,
            "test_timestamp": pd.Timestamp.now().isoformat()
        }
        
        with open(results_path, 'w') as f:
            json.dump(test_summary, f, indent=2)
        
        context.log.info(f"Inference tests completed: {correct_predictions}/{len(test_cases)} correct")
        context.log.info(f"Test accuracy: {test_accuracy:.2%}")
        context.log.info(f"Results saved to: {results_path}")
        
        return MaterializeResult(
            metadata={
                "test_accuracy": MetadataValue.float(test_accuracy),
                "avg_confidence": MetadataValue.float(avg_confidence),
                "total_tests": MetadataValue.int(len(test_cases)),
                "correct_predictions": MetadataValue.int(correct_predictions),
                "results_path": MetadataValue.path(str(results_path))
            },
            asset_materialization_data=test_summary
        )
        
    except Exception as e:
        context.log.error(f"Inference tests failed: {str(e)}")
        raise
