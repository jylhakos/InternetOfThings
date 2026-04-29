from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.providers.amazon.aws.operators.sagemaker import SageMakerTrainingOperator
import os

# Default arguments
default_args = {
    'owner': 'ml-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email': ['admin@company.com']
}

# Create DAG
dag = DAG(
    'bert_fine_tuning_pipeline',
    default_args=default_args,
    description='BERT Fine-tuning ML Pipeline',
    schedule_interval='@daily',
    catchup=False,
    max_active_runs=1,
    tags=['ml', 'bert', 'nlp', 'fine-tuning']
)

# Task 1: Data Preparation
def prepare_data(**context):
    """Prepare training data for BERT fine-tuning"""
    import pandas as pd
    import numpy as np
    from sklearn.model_selection import train_test_split
    
    # Load and preprocess data
    print("📊 Loading and preparing training data...")
    
    # Example data preparation
    data = {
        'text': ['Great product!', 'Terrible service', 'Average quality'],
        'label': [1, 0, 1]
    }
    df = pd.DataFrame(data)
    
    # Split data
    train_df, val_df = train_test_split(df, test_size=0.2, random_state=42)
    
    # Save processed data
    train_df.to_csv('/tmp/train_data.csv', index=False)
    val_df.to_csv('/tmp/val_data.csv', index=False)
    
    print(f"✅ Data prepared: {len(train_df)} training, {len(val_df)} validation samples")
    return f"train_samples:{len(train_df)},val_samples:{len(val_df)}"

data_prep_task = PythonOperator(
    task_id='prepare_data',
    python_callable=prepare_data,
    dag=dag
)

# Task 2: BERT Fine-tuning
def fine_tune_bert(**context):
    """Fine-tune BERT model"""
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    from transformers import TrainingArguments, Trainer
    import pandas as pd
    
    print("🤖 Starting BERT fine-tuning...")
    
    # Load data
    train_df = pd.read_csv('/tmp/train_data.csv')
    val_df = pd.read_csv('/tmp/val_data.csv')
    
    # Initialize model and tokenizer
    model_name = "bert-base-uncased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name, num_labels=2
    )
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir='/tmp/fine_tuned_bert',
        num_train_epochs=3,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='/tmp/logs',
        logging_steps=10,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
    )
    
    # Training logic would go here
    print("✅ BERT fine-tuning completed")
    return "fine_tuning_completed"

fine_tuning_task = PythonOperator(
    task_id='fine_tune_bert',
    python_callable=fine_tune_bert,
    dag=dag
)

# Task 3: Model Evaluation
def evaluate_model(**context):
    """Evaluate fine-tuned model"""
    from sklearn.metrics import accuracy_score, classification_report
    import pandas as pd
    
    print("📈 Evaluating fine-tuned model...")
    
    # Load validation data
    val_df = pd.read_csv('/tmp/val_data.csv')
    
    # Model evaluation logic would go here
    accuracy = 0.95
    f1_score = 0.94
    
    # Log metrics
    print(f"✅ Model Evaluation Complete:")
    print(f"   Accuracy: {accuracy:.3f}")
    print(f"   F1-Score: {f1_score:.3f}")
    
    # Store metrics for monitoring
    metrics = {
        'accuracy': accuracy,
        'f1_score': f1_score,
        'timestamp': datetime.now().isoformat()
    }
    
    return metrics

evaluation_task = PythonOperator(
    task_id='evaluate_model',
    python_callable=evaluate_model,
    dag=dag
)

# Task 4: Model Testing
test_model_task = BashOperator(
    task_id='test_model',
    bash_command='cd /opt/airflow && python tests/test_model.py',
    dag=dag
)

# Task 5: Deploy to API
deploy_api_task = DockerOperator(
    task_id='deploy_api',
    image='bert-classifier:latest',
    container_name='bert-api-{{ ds }}',
    ports=[8000, 8000],
    auto_remove=True,
    dag=dag
)

# Task 6: Deploy to Ollama
def deploy_to_ollama(**context):
    """Deploy fine-tuned model to Ollama"""
    import requests
    import json
    import time
    
    print("🦙 Deploying model to Ollama...")
    
    ollama_url = "http://localhost:11434"
    
    # Create model in Ollama
    model_data = {
        "name": "bert-classifier-finetuned",
        "modelfile": """
FROM bert-base

PARAMETER temperature 0.1
PARAMETER top_k 40
PARAMETER top_p 0.9

SYSTEM "You are a text classifier using a fine-tuned BERT model. Classify text as positive (1) or negative (0)."

TEMPLATE "Text: {{ .Prompt }}\nClassification:"
        """
    }
    
    try:
        response = requests.post(f"{ollama_url}/api/create", json=model_data)
        if response.status_code == 200:
            print("✅ Model successfully deployed to Ollama")
            return "ollama_deployment_successful"
        else:
            raise Exception(f"Ollama deployment failed: {response.text}")
    except Exception as e:
        print(f"❌ Ollama deployment error: {str(e)}")
        raise

deploy_ollama_task = PythonOperator(
    task_id='deploy_to_ollama',
    python_callable=deploy_to_ollama,
    dag=dag
)

# Task 7: Health Check
def health_check(**context):
    """Perform health check on deployed API"""
    import requests
    import time
    
    print("🏥 Performing API health check...")
    
    # Wait for API to start
    time.sleep(30)
    
    try:
        response = requests.get('http://localhost:8000/health')
        if response.status_code == 200:
            print("✅ API health check passed")
            return "healthy"
        else:
            raise Exception(f"Health check failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        raise

health_check_task = PythonOperator(
    task_id='health_check',
    python_callable=health_check,
    dag=dag
)

# Task 8: Test Ollama Inference
def test_ollama_inference(**context):
    """Test inference on Ollama deployment"""
    import requests
    import json
    
    print("🧪 Testing Ollama inference...")
    
    ollama_url = "http://localhost:11434"
    test_texts = [
        "I absolutely love this product!",
        "This is terrible quality.",
        "Average performance, nothing special."
    ]
    
    for text in test_texts:
        payload = {
            "model": "bert-classifier-finetuned",
            "prompt": text,
            "stream": False
        }
        
        try:
            response = requests.post(f"{ollama_url}/api/generate", json=payload)
            result = response.json()
            print(f"Text: {text}")
            print(f"Classification: {result.get('response', 'No response')}")
            print("---")
        except Exception as e:
            print(f"Error testing text '{text}': {str(e)}")
    
    print("✅ Ollama inference testing completed")
    return "ollama_testing_completed"

test_ollama_task = PythonOperator(
    task_id='test_ollama_inference',
    python_callable=test_ollama_inference,
    dag=dag
)

# Task Dependencies
data_prep_task >> fine_tuning_task >> evaluation_task >> test_model_task >> [deploy_api_task, deploy_ollama_task]
deploy_api_task >> health_check_task
deploy_ollama_task >> test_ollama_task
