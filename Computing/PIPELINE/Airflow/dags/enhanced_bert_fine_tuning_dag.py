#!/usr/bin/env python3
"""
Updated Apache Airflow DAG for BERT Fine-tuning with Dataset Management
Integrates with new dataset management and data wrangling capabilities
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
import sys
import os

# Add src directory to path
sys.path.append('/opt/airflow/dags/../src')

# Default DAG arguments
default_args = {
    'owner': 'data-science-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'catchup': False
}

# Create DAG
dag = DAG(
    'enhanced_bert_fine_tuning_pipeline',
    default_args=default_args,
    description='Enhanced BERT fine-tuning pipeline with dataset management',
    schedule_interval='@weekly',  # Run weekly
    max_active_runs=1,
    tags=['machine-learning', 'nlp', 'bert', 'fine-tuning', 'dataset-management']
)

# Task 1: Dataset Configuration and Validation
def validate_dataset_config(**context):
    """Validate dataset configuration and check availability"""
    from dataset_manager import DatasetManager
    import logging
    
    logging.info("🔍 Validating dataset configuration...")
    
    # Get dataset name from DAG configuration or use default
    dataset_name = context['dag_run'].conf.get('dataset_name', 'custom')
    config_file = context['dag_run'].conf.get('config_file', 'config/dataset_config.json')
    
    # Initialize dataset manager
    manager = DatasetManager(config_file)
    
    # Check if dataset exists in configuration
    available_datasets = manager.config.list_available_datasets()
    if dataset_name not in available_datasets:
        raise ValueError(f"Dataset '{dataset_name}' not found. Available: {available_datasets}")
    
    # Get dataset configuration
    dataset_config = manager.config.get_dataset_config(dataset_name)
    
    # Validate configuration
    required_fields = ['text_column', 'label_column', 'type']
    missing_fields = [field for field in required_fields if field not in dataset_config]
    if missing_fields:
        raise ValueError(f"Missing required fields in dataset config: {missing_fields}")
    
    # Check if custom dataset file exists (for custom datasets)
    if dataset_name == 'custom' and 'path' in dataset_config:
        if not os.path.exists(dataset_config['path']):
            raise FileNotFoundError(f"Custom dataset file not found: {dataset_config['path']}")
    
    logging.info(f"✅ Dataset '{dataset_name}' configuration validated")
    logging.info(f"   Type: {dataset_config['type']}")
    logging.info(f"   Text column: {dataset_config['text_column']}")
    logging.info(f"   Label column: {dataset_config['label_column']}")
    
    # Store configuration for downstream tasks
    context['task_instance'].xcom_push(key='dataset_name', value=dataset_name)
    context['task_instance'].xcom_push(key='config_file', value=config_file)
    context['task_instance'].xcom_push(key='dataset_config', value=dataset_config)
    
    return f"✅ Validated dataset: {dataset_name}"

validate_config_task = PythonOperator(
    task_id='validate_dataset_config',
    python_callable=validate_dataset_config,
    dag=dag
)

# Task 2: Data Loading and Exploration
def load_and_explore_data(**context):
    """Load dataset and perform comprehensive data exploration"""
    from dataset_manager import DatasetManager
    from data_wrangling import DataExplorer
    import logging
    import json
    
    logging.info("📊 Loading and exploring dataset...")
    
    # Get configuration from previous task
    dataset_name = context['task_instance'].xcom_pull(task_ids='validate_dataset_config', key='dataset_name')
    config_file = context['task_instance'].xcom_pull(task_ids='validate_dataset_config', key='config_file')
    
    # Get runtime parameters
    limit_samples = context['dag_run'].conf.get('limit_samples', None)
    if limit_samples:
        limit_samples = int(limit_samples)
    
    # Initialize managers
    manager = DatasetManager(config_file)
    
    # Load dataset
    df, dataset_config = manager.load_dataset(dataset_name, limit_samples)
    
    # Perform data exploration
    explorer = DataExplorer(df, dataset_config['text_column'], dataset_config['label_column'])
    exploration_results = explorer.full_analysis()
    
    # Store results for downstream tasks and monitoring
    context['task_instance'].xcom_push(key='dataset_size', value=len(df))
    context['task_instance'].xcom_push(key='exploration_results', value=exploration_results)
    
    # Log key statistics
    stats = exploration_results['basic_stats']
    logging.info(f"📈 Dataset loaded: {stats['total_samples']} samples")
    logging.info(f"🏷️  Classes: {stats['num_classes']}")
    logging.info(f"📝 Avg text length: {stats['text_length']['mean']:.1f} chars")
    
    # Check for data quality issues
    issues = exploration_results['data_issues']
    total_issues = sum([
        sum(issues['missing_data'].values()),
        sum(issues['duplicates'].values()),
        sum(issues['outliers'].values()),
        sum(issues['inconsistencies'].values())
    ])
    
    if total_issues > 0:
        logging.warning(f"⚠️  Found {total_issues} data quality issues - will be addressed in cleaning step")
    
    return f"✅ Explored dataset: {len(df)} samples, {stats['num_classes']} classes"

explore_data_task = PythonOperator(
    task_id='load_and_explore_data',
    python_callable=load_and_explore_data,
    dag=dag
)

# Task 3: Data Cleaning and Preprocessing
def clean_and_preprocess_data(**context):
    """Clean and preprocess the dataset"""
    from dataset_manager import DatasetManager
    from data_wrangling import DataCleaner
    import logging
    
    logging.info("🧹 Cleaning and preprocessing dataset...")
    
    # Get configuration
    dataset_name = context['task_instance'].xcom_pull(task_ids='validate_dataset_config', key='dataset_name')
    config_file = context['task_instance'].xcom_pull(task_ids='validate_dataset_config', key='config_file')
    
    # Get runtime parameters
    limit_samples = context['dag_run'].conf.get('limit_samples', None)
    if limit_samples:
        limit_samples = int(limit_samples)
    
    auto_balance = context['dag_run'].conf.get('auto_balance', 'true').lower() == 'true'
    
    # Initialize managers
    manager = DatasetManager(config_file)
    
    # Load dataset
    df, dataset_config = manager.load_dataset(dataset_name, limit_samples)
    original_size = len(df)
    
    # Initialize cleaner
    cleaner = DataCleaner(df, dataset_config['text_column'], dataset_config['label_column'])
    
    # Apply cleaning steps
    df = cleaner.remove_missing_data()
    df = cleaner.clean_text(
        remove_html=dataset_config.get('preprocessing', {}).get('remove_html', True),
        remove_urls=True,
        remove_emails=True,
        normalize_whitespace=True
    )
    df = cleaner.remove_duplicates()
    
    # Apply length filtering
    preprocessing = dataset_config.get('preprocessing', {})
    if 'min_length' in preprocessing or 'max_length' in preprocessing:
        min_len = preprocessing.get('min_length', 10)
        max_len = preprocessing.get('max_length', 5000)
        df = cleaner.filter_by_length(min_len, max_len)
    
    # Check class balance and apply balancing if needed
    label_counts = df[dataset_config['label_column']].value_counts()
    imbalance_ratio = label_counts.max() / label_counts.min()
    
    if auto_balance and imbalance_ratio > 3.0:
        logging.info(f"📊 Dataset imbalanced (ratio: {imbalance_ratio:.1f}) - applying undersampling")
        df = cleaner.balance_classes(method='undersample')
    
    # Get cleaning summary
    cleaning_summary = cleaner.get_cleaning_summary()
    
    # Log results
    final_size = len(df)
    logging.info(f"🧹 Cleaning completed:")
    logging.info(f"   Original: {original_size} samples")
    logging.info(f"   Final: {final_size} samples")
    logging.info(f"   Removed: {original_size - final_size} samples")
    
    for operation in cleaning_summary:
        logging.info(f"   • {operation}")
    
    # Store cleaned data and metadata
    context['task_instance'].xcom_push(key='cleaned_dataset_size', value=final_size)
    context['task_instance'].xcom_push(key='cleaning_summary', value=cleaning_summary)
    context['task_instance'].xcom_push(key='samples_removed', value=original_size - final_size)
    
    return f"✅ Cleaned dataset: {final_size} samples ({original_size - final_size} removed)"

clean_data_task = PythonOperator(
    task_id='clean_and_preprocess_data',
    python_callable=clean_and_preprocess_data,
    dag=dag
)

# Task 4: Data Preparation and Splitting
def prepare_train_test_splits(**context):
    """Prepare train, validation, and test splits"""
    from dataset_manager import DatasetManager
    from data_wrangling import DataCleaner
    import logging
    
    logging.info("📊 Preparing train/validation/test splits...")
    
    # Get configuration
    dataset_name = context['task_instance'].xcom_pull(task_ids='validate_dataset_config', key='dataset_name')
    config_file = context['task_instance'].xcom_pull(task_ids='validate_dataset_config', key='config_file')
    
    # Get runtime parameters
    limit_samples = context['dag_run'].conf.get('limit_samples', None)
    if limit_samples:
        limit_samples = int(limit_samples)
    
    auto_balance = context['dag_run'].conf.get('auto_balance', 'true').lower() == 'true'
    
    # Initialize managers
    manager = DatasetManager(config_file)
    
    # Load and clean dataset (repeat cleaning for consistency)
    df, dataset_config = manager.load_dataset(dataset_name, limit_samples)
    
    # Apply same cleaning as previous task
    cleaner = DataCleaner(df, dataset_config['text_column'], dataset_config['label_column'])
    df = cleaner.remove_missing_data()
    df = cleaner.clean_text(
        remove_html=dataset_config.get('preprocessing', {}).get('remove_html', True),
        remove_urls=True,
        remove_emails=True,
        normalize_whitespace=True
    )
    df = cleaner.remove_duplicates()
    
    preprocessing = dataset_config.get('preprocessing', {})
    if 'min_length' in preprocessing or 'max_length' in preprocessing:
        min_len = preprocessing.get('min_length', 10)
        max_len = preprocessing.get('max_length', 5000)
        df = cleaner.filter_by_length(min_len, max_len)
    
    # Apply balancing if configured
    label_counts = df[dataset_config['label_column']].value_counts()
    imbalance_ratio = label_counts.max() / label_counts.min()
    if auto_balance and imbalance_ratio > 3.0:
        df = cleaner.balance_classes(method='undersample')
    
    # Prepare train/validation/test splits
    train_df, val_df, test_df = manager.prepare_train_val_test(df, dataset_config)
    
    # Save processed data
    manager.save_processed_data(train_df, val_df, test_df, dataset_name)
    
    # Log split information
    logging.info(f"📊 Data splits prepared:")
    logging.info(f"   Train: {len(train_df)} samples")
    logging.info(f"   Validation: {len(val_df)} samples")  
    logging.info(f"   Test: {len(test_df)} samples")
    
    # Store split information
    context['task_instance'].xcom_push(key='train_size', value=len(train_df))
    context['task_instance'].xcom_push(key='val_size', value=len(val_df))
    context['task_instance'].xcom_push(key='test_size', value=len(test_df))
    
    return f"✅ Data splits: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}"

prepare_splits_task = PythonOperator(
    task_id='prepare_train_test_splits',
    python_callable=prepare_train_test_splits,
    dag=dag
)

# Task 5: BERT Model Training
def train_bert_model(**context):
    """Train BERT model using the enhanced training pipeline"""
    from enhanced_bert_training import ConfigurableBERTTrainer
    import logging
    import torch
    
    logging.info("🤖 Starting BERT model training...")
    
    # Get configuration
    dataset_name = context['task_instance'].xcom_pull(task_ids='validate_dataset_config', key='dataset_name')
    config_file = context['task_instance'].xcom_pull(task_ids='validate_dataset_config', key='config_file')
    
    # Get runtime parameters
    limit_samples = context['dag_run'].conf.get('limit_samples', None)
    if limit_samples:
        limit_samples = int(limit_samples)
    
    output_dir = context['dag_run'].conf.get('model_output_dir', 'models/bert_airflow_trained')
    
    # Initialize trainer
    trainer = ConfigurableBERTTrainer(config_file, dataset_name)
    
    # Load and prepare data (skip exploration and cleaning as already done)
    df = trainer.load_and_explore_dataset(
        limit_samples=limit_samples,
        explore=False,  # Skip exploration in training
        clean=True
    )
    
    # Prepare data for training
    train_df, val_df, test_df = trainer.prepare_data_for_training(df)
    
    # Initialize and train model
    trainer.initialize_model()
    trainer.train_model()
    
    # Test model
    test_accuracy, predictions, labels, report = trainer.test_model()
    
    # Save model
    model_path = trainer.save_model(output_dir)
    
    # Log training results
    logging.info(f"🎯 Training completed successfully!")
    logging.info(f"   Final test accuracy: {test_accuracy:.4f}")
    logging.info(f"   Model saved to: {model_path}")
    
    # Store training results
    context['task_instance'].xcom_push(key='test_accuracy', value=test_accuracy)
    context['task_instance'].xcom_push(key='model_path', value=str(model_path))
    context['task_instance'].xcom_push(key='training_history', value=trainer.training_history)
    
    return f"✅ Model trained - Test accuracy: {test_accuracy:.4f}, Saved to: {model_path}"

train_model_task = PythonOperator(
    task_id='train_bert_model',
    python_callable=train_bert_model,
    dag=dag
)

# Task 6: Model Validation and Testing
def validate_trained_model(**context):
    """Validate the trained model with additional tests"""
    import torch
    from transformers import BertForSequenceClassification, BertTokenizer
    import logging
    import json
    
    logging.info("🔍 Validating trained model...")
    
    # Get model path from training task
    model_path = context['task_instance'].xcom_pull(task_ids='train_bert_model', key='model_path')
    test_accuracy = context['task_instance'].xcom_pull(task_ids='train_bert_model', key='test_accuracy')
    
    # Load saved model for validation
    model = BertForSequenceClassification.from_pretrained(model_path)
    tokenizer = BertTokenizer.from_pretrained(model_path)
    
    # Load training configuration
    with open(f"{model_path}/training_config.json", 'r') as f:
        config = json.load(f)
    
    # Validate model architecture
    num_parameters = sum(p.numel() for p in model.parameters())
    logging.info(f"📊 Model validation:")
    logging.info(f"   Parameters: {num_parameters:,}")
    logging.info(f"   Test accuracy: {test_accuracy:.4f}")
    logging.info(f"   Training epochs: {len(config.get('training_history', []))}")
    
    # Test with sample predictions
    sample_texts = [
        "This product is amazing! I love it!",
        "Terrible quality, very disappointed.",
        "Average product, nothing special."
    ]
    
    logging.info("🧪 Testing sample predictions:")
    model.eval()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    
    for text in sample_texts:
        inputs = tokenizer(text, truncation=True, padding='max_length', max_length=512, return_tensors='pt')
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=-1)
            prediction = torch.argmax(logits, dim=-1).item()
            confidence = probabilities[0][prediction].item()
        
        logging.info(f"   Text: '{text[:50]}...'")
        logging.info(f"   Prediction: {prediction} (confidence: {confidence:.3f})")
    
    # Validation criteria
    min_accuracy = float(context['dag_run'].conf.get('min_accuracy', 0.7))
    
    if test_accuracy < min_accuracy:
        raise ValueError(f"Model accuracy {test_accuracy:.4f} below minimum threshold {min_accuracy}")
    
    logging.info(f"✅ Model validation passed! Accuracy: {test_accuracy:.4f} >= {min_accuracy}")
    
    # Store validation results
    context['task_instance'].xcom_push(key='validation_passed', value=True)
    context['task_instance'].xcom_push(key='model_parameters', value=num_parameters)
    
    return f"✅ Model validated - Accuracy: {test_accuracy:.4f}, Parameters: {num_parameters:,}"

validate_model_task = PythonOperator(
    task_id='validate_trained_model',
    python_callable=validate_trained_model,
    dag=dag
)

# Task 7: Pipeline Summary and Reporting
def generate_pipeline_report(**context):
    """Generate comprehensive pipeline execution report"""
    import logging
    from datetime import datetime
    
    logging.info("📝 Generating pipeline execution report...")
    
    # Collect all metrics from previous tasks
    dataset_name = context['task_instance'].xcom_pull(task_ids='validate_dataset_config', key='dataset_name')
    dataset_size = context['task_instance'].xcom_pull(task_ids='load_and_explore_data', key='dataset_size')
    cleaned_size = context['task_instance'].xcom_pull(task_ids='clean_and_preprocess_data', key='cleaned_dataset_size')
    samples_removed = context['task_instance'].xcom_pull(task_ids='clean_and_preprocess_data', key='samples_removed')
    
    train_size = context['task_instance'].xcom_pull(task_ids='prepare_train_test_splits', key='train_size')
    val_size = context['task_instance'].xcom_pull(task_ids='prepare_train_test_splits', key='val_size')
    test_size = context['task_instance'].xcom_pull(task_ids='prepare_train_test_splits', key='test_size')
    
    test_accuracy = context['task_instance'].xcom_pull(task_ids='train_bert_model', key='test_accuracy')
    model_path = context['task_instance'].xcom_pull(task_ids='train_bert_model', key='model_path')
    model_parameters = context['task_instance'].xcom_pull(task_ids='validate_trained_model', key='model_parameters')
    
    # Generate report
    report = f"""
    ================================================================================
    BERT FINE-TUNING PIPELINE EXECUTION REPORT
    ================================================================================
    
    📅 Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    🏷️  Dataset: {dataset_name}
    
    📊 DATA PROCESSING SUMMARY:
    • Original dataset size: {dataset_size:,} samples
    • After cleaning: {cleaned_size:,} samples
    • Samples removed: {samples_removed:,} ({(samples_removed/dataset_size)*100:.1f}%)
    
    📈 DATA SPLITS:
    • Training: {train_size:,} samples
    • Validation: {val_size:,} samples  
    • Test: {test_size:,} samples
    
    🤖 MODEL TRAINING RESULTS:
    • Test Accuracy: {test_accuracy:.4f}
    • Model Parameters: {model_parameters:,}
    • Model Location: {model_path}
    
    ✅ PIPELINE STATUS: COMPLETED SUCCESSFULLY
    
    📋 NEXT STEPS:
    1. Model is ready for deployment
    2. Use saved model at: {model_path}
    3. Review training history in training_config.json
    
    ================================================================================
    """
    
    logging.info(report)
    
    # Store final report
    context['task_instance'].xcom_push(key='pipeline_report', value=report)
    
    return "✅ Pipeline completed successfully!"

generate_report_task = PythonOperator(
    task_id='generate_pipeline_report',
    python_callable=generate_pipeline_report,
    dag=dag
)

# Define task dependencies
validate_config_task >> explore_data_task >> clean_data_task >> prepare_splits_task >> train_model_task >> validate_model_task >> generate_report_task

# Task documentation
dag.doc_md = """
# Enhanced BERT Fine-tuning Pipeline

This DAG provides a comprehensive BERT fine-tuning pipeline with advanced dataset management capabilities.

## Features:
- **Dataset Management**: Configurable dataset loading from multiple sources
- **Data Exploration**: Comprehensive data analysis and quality assessment
- **Data Cleaning**: Automated data preprocessing and cleaning
- **Class Balancing**: Automatic handling of imbalanced datasets
- **Model Training**: BERT fine-tuning with optimized configurations
- **Model Validation**: Comprehensive model testing and validation
- **Reporting**: Detailed execution reports

## Configuration:
Configure the pipeline by passing parameters in the DAG run configuration:

```json
{
    "dataset_name": "custom",
    "config_file": "config/dataset_config.json",
    "limit_samples": 1000,
    "auto_balance": true,
    "min_accuracy": 0.75,
    "model_output_dir": "models/my_bert_model"
}
```

## Dataset Types Supported:
- Custom CSV datasets
- IMDB movie reviews
- Amazon product reviews
- Financial news sentiment
- AG News classification

## Outputs:
- Fine-tuned BERT model
- Training configuration and history
- Data exploration results
- Pipeline execution report
"""
