#!/usr/bin/env python3
"""
Complete Dataset Management Demo
Demonstrates all dataset management, exploration, and training capabilities
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )

def demo_dataset_configuration():
    """Demo 1: Dataset Configuration Management"""
    print("="*80)
    print("🔧 DEMO 1: DATASET CONFIGURATION MANAGEMENT")
    print("="*80)
    
    from src.dataset_manager import BERTDatasetConfig
    
    # Initialize configuration
    config = BERTDatasetConfig("config/dataset_config.json")
    
    # List available datasets
    print("\n📋 Available Datasets:")
    for dataset_name in config.list_available_datasets():
        dataset_config = config.get_dataset_config(dataset_name)
        print(f"  • {dataset_name}: {dataset_config.get('name', 'Unknown')}")
        print(f"    Type: {dataset_config.get('type', 'N/A')}")
        print(f"    Classes: {dataset_config.get('classes', 'N/A')}")
        if 'max_samples' in dataset_config:
            max_samples = dataset_config['max_samples']
            print(f"    Max samples: {max_samples if max_samples > 0 else 'Unlimited'}")
        print()
    
    print("✅ Configuration management demo complete!")

def demo_dataset_loading():
    """Demo 2: Dataset Loading and Basic Processing"""
    print("\n" + "="*80)
    print("📊 DEMO 2: DATASET LOADING AND PROCESSING")
    print("="*80)
    
    from src.dataset_manager import DatasetManager
    
    # Initialize dataset manager
    manager = DatasetManager("config/dataset_config.json")
    
    # Load custom dataset
    print("\n📥 Loading custom dataset...")
    df, dataset_config = manager.load_dataset("custom", limit_samples=20)
    
    print(f"✅ Dataset loaded:")
    print(f"   Samples: {len(df)}")
    print(f"   Columns: {df.columns.tolist()}")
    print(f"   Text column: {dataset_config['text_column']}")
    print(f"   Label column: {dataset_config['label_column']}")
    
    # Show sample data
    print(f"\n📄 Sample data:")
    for i, row in df.head(3).iterrows():
        text = row[dataset_config['text_column']]
        label = row[dataset_config['label_column']]
        print(f"   {i+1}. Text: '{text[:50]}...' | Label: {label}")
    
    # Check label distribution
    label_counts = df[dataset_config['label_column']].value_counts()
    print(f"\n📊 Label distribution:")
    for label, count in label_counts.items():
        print(f"   {label}: {count} samples")
    
    print("\n✅ Dataset loading demo complete!")
    return df, dataset_config

def demo_data_exploration(df, dataset_config):
    """Demo 3: Comprehensive Data Exploration"""
    print("\n" + "="*80)
    print("🔍 DEMO 3: COMPREHENSIVE DATA EXPLORATION")
    print("="*80)
    
    from src.data_wrangling import DataExplorer
    
    # Initialize explorer
    explorer = DataExplorer(df, dataset_config['text_column'], dataset_config['label_column'])
    
    # Run different types of analysis
    print("\n📈 Running basic statistics analysis...")
    basic_stats = explorer.basic_statistics()
    
    print("\n🔍 Running text quality analysis...")
    quality_stats = explorer.text_quality_analysis()
    
    print("\n📚 Running vocabulary analysis...")
    vocab_stats = explorer.vocabulary_analysis(top_n=10)
    
    print("\n🏷️  Running label distribution analysis...")
    label_stats = explorer.label_distribution_analysis()
    
    print("\n🚨 Detecting data quality issues...")
    issues = explorer.detect_data_issues()
    
    print("\n💡 Generating recommendations...")
    recommendations = explorer.generate_recommendations()
    
    print(f"\n📋 Summary of Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")
    
    print("\n✅ Data exploration demo complete!")
    return basic_stats, quality_stats, vocab_stats

def demo_data_cleaning(df, dataset_config):
    """Demo 4: Data Cleaning and Preprocessing"""
    print("\n" + "="*80)
    print("🧹 DEMO 4: DATA CLEANING AND PREPROCESSING")
    print("="*80)
    
    from src.data_wrangling import DataCleaner
    
    # Create a copy with some problematic data for demonstration
    demo_df = df.copy()
    
    # Add some issues for demonstration
    print("\n🔧 Adding some data quality issues for demonstration...")
    
    # Add empty text
    demo_df.loc[len(demo_df)] = ['', 1]
    
    # Add duplicate
    if len(demo_df) > 0:
        demo_df.loc[len(demo_df)] = demo_df.iloc[0].copy()
    
    # Add text with HTML and URLs
    demo_df.loc[len(demo_df)] = ['Check out <b>this</b> amazing product at http://example.com!', 1]
    
    print(f"📊 Dataset with issues: {len(demo_df)} samples")
    
    # Initialize cleaner
    cleaner = DataCleaner(demo_df, dataset_config['text_column'], dataset_config['label_column'])
    
    # Apply cleaning steps
    print("\n🧹 Applying data cleaning steps...")
    
    original_size = len(demo_df)
    
    # Remove missing data
    demo_df = cleaner.remove_missing_data()
    print(f"   After removing missing data: {len(demo_df)} samples")
    
    # Clean text
    demo_df = cleaner.clean_text(
        remove_html=True,
        remove_urls=True,
        remove_emails=True,
        normalize_whitespace=True
    )
    print(f"   After text cleaning: {len(demo_df)} samples")
    
    # Remove duplicates
    demo_df = cleaner.remove_duplicates()
    print(f"   After removing duplicates: {len(demo_df)} samples")
    
    # Filter by length
    demo_df = cleaner.filter_by_length(min_length=5, max_length=1000)
    print(f"   After length filtering: {len(demo_df)} samples")
    
    # Check class balance
    label_counts = demo_df[dataset_config['label_column']].value_counts()
    imbalance_ratio = label_counts.max() / label_counts.min() if len(label_counts) > 1 else 1.0
    
    print(f"\n📊 Class balance analysis:")
    print(f"   Imbalance ratio: {imbalance_ratio:.2f}")
    
    if imbalance_ratio > 2.0:
        print("   Applying class balancing...")
        demo_df = cleaner.balance_classes(method='undersample')
        print(f"   After balancing: {len(demo_df)} samples")
    
    # Get cleaning summary
    cleaning_summary = cleaner.get_cleaning_summary()
    
    print(f"\n📋 Cleaning Summary:")
    for operation in cleaning_summary:
        print(f"   • {operation}")
    
    print(f"\n📈 Results:")
    print(f"   Original: {original_size} samples")
    print(f"   Final: {len(demo_df)} samples")
    print(f"   Reduction: {((original_size - len(demo_df)) / original_size) * 100:.1f}%")
    
    print("\n✅ Data cleaning demo complete!")
    return demo_df

def demo_dataset_splitting(df, dataset_config):
    """Demo 5: Dataset Splitting and DataLoader Creation"""
    print("\n" + "="*80)
    print("📊 DEMO 5: DATASET SPLITTING AND DATALOADER CREATION")
    print("="*80)
    
    from src.dataset_manager import DatasetManager
    from transformers import BertTokenizer
    
    # Initialize managers
    manager = DatasetManager("config/dataset_config.json")
    
    # Prepare train/validation/test splits
    print("\n🔄 Creating train/validation/test splits...")
    train_df, val_df, test_df = manager.prepare_train_val_test(df, dataset_config)
    
    print(f"📊 Data splits:")
    print(f"   Training: {len(train_df)} samples ({len(train_df)/len(df)*100:.1f}%)")
    print(f"   Validation: {len(val_df)} samples ({len(val_df)/len(df)*100:.1f}%)")
    print(f"   Test: {len(test_df)} samples ({len(test_df)/len(df)*100:.1f}%)")
    
    # Initialize tokenizer
    print("\n🔤 Initializing BERT tokenizer...")
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    
    # Create dataloaders
    print("\n📦 Creating PyTorch DataLoaders...")
    train_dataloader, val_dataloader, test_dataloader = manager.create_dataloaders(
        train_df, val_df, test_df, dataset_config, tokenizer, batch_size=4
    )
    
    print(f"📊 DataLoaders created:")
    print(f"   Training: {len(train_dataloader)} batches")
    print(f"   Validation: {len(val_dataloader)} batches")
    print(f"   Test: {len(test_dataloader)} batches")
    
    # Show sample batch
    print(f"\n📄 Sample batch from training data:")
    for batch in train_dataloader:
        print(f"   Input IDs shape: {batch['input_ids'].shape}")
        print(f"   Attention mask shape: {batch['attention_mask'].shape}")
        print(f"   Labels shape: {batch['labels'].shape}")
        print(f"   Sample tokens: {batch['input_ids'][0][:10].tolist()}...")
        break
    
    print("\n✅ Dataset splitting demo complete!")
    return train_df, val_df, test_df

def demo_enhanced_training():
    """Demo 6: Enhanced BERT Training"""
    print("\n" + "="*80)
    print("🤖 DEMO 6: ENHANCED BERT TRAINING (QUICK DEMO)")
    print("="*80)
    
    print("🎯 This demo shows training setup without full training...")
    
    from src.enhanced_bert_training import ConfigurableBERTTrainer
    
    # Initialize trainer
    print("\n🔧 Initializing enhanced BERT trainer...")
    trainer = ConfigurableBERTTrainer("config/dataset_config.json", "custom")
    
    # Load dataset (limit to small sample for demo)
    print("\n📥 Loading dataset for training...")
    df = trainer.load_and_explore_dataset(
        limit_samples=10,  # Very small for demo
        explore=False,     # Skip exploration for speed
        clean=True
    )
    
    print(f"   Loaded {len(df)} samples for training demo")
    
    # Prepare data
    print("\n📊 Preparing data for training...")
    train_df, val_df, test_df = trainer.prepare_data_for_training(df)
    
    # Initialize model
    print("\n🤖 Initializing BERT model...")
    model = trainer.initialize_model()
    
    print(f"📊 Training setup complete:")
    print(f"   Model: BERT-base-uncased")
    print(f"   Device: {trainer.device}")
    print(f"   Batch size: {trainer.batch_size}")
    print(f"   Epochs: {trainer.num_epochs}")
    print(f"   Training batches: {len(trainer.train_dataloader)}")
    
    print("\n💡 To run full training:")
    print("   python src/enhanced_bert_training.py --dataset custom --limit_samples 100")
    
    print("\n✅ Enhanced training demo complete!")

def demo_airflow_integration():
    """Demo 7: Apache Airflow Integration"""
    print("\n" + "="*80)
    print("🌊 DEMO 7: APACHE AIRFLOW INTEGRATION")
    print("="*80)
    
    print("📋 Available Airflow DAGs:")
    print("   • enhanced_bert_fine_tuning_dag.py - Complete ML pipeline")
    print("   • bert_fine_tuning_dag.py - Basic fine-tuning pipeline")
    
    print("\n🔧 DAG Configuration Example:")
    dag_config = {
        "dataset_name": "custom",
        "config_file": "config/dataset_config.json", 
        "limit_samples": 1000,
        "auto_balance": True,
        "min_accuracy": 0.75,
        "model_output_dir": "models/airflow_bert_model"
    }
    
    for key, value in dag_config.items():
        print(f"   {key}: {value}")
    
    print("\n📊 Pipeline Tasks:")
    tasks = [
        "validate_dataset_config - Validate dataset configuration",
        "load_and_explore_data - Load and explore dataset", 
        "clean_and_preprocess_data - Clean and preprocess data",
        "prepare_train_test_splits - Create data splits",
        "train_bert_model - Train BERT model",
        "validate_trained_model - Validate trained model",
        "generate_pipeline_report - Generate execution report"
    ]
    
    for i, task in enumerate(tasks, 1):
        print(f"   {i}. {task}")
    
    print("\n🚀 To run Airflow pipeline:")
    print("   1. Start Airflow: docker-compose up -d")
    print("   2. Access UI: http://localhost:8080")
    print("   3. Enable DAG: enhanced_bert_fine_tuning_pipeline")
    print("   4. Trigger with configuration above")
    
    print("\n✅ Airflow integration demo complete!")

def main():
    """Run complete dataset management demonstration"""
    setup_logging()
    
    print("🚀 BERT DATASET MANAGEMENT AND TRAINING DEMONSTRATION")
    print("This demo showcases all dataset management capabilities")
    print("="*80)
    
    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    
    try:
        # Run all demos
        demo_dataset_configuration()
        
        df, dataset_config = demo_dataset_loading()
        
        basic_stats, quality_stats, vocab_stats = demo_data_exploration(df, dataset_config)
        
        cleaned_df = demo_data_cleaning(df, dataset_config)
        
        train_df, val_df, test_df = demo_dataset_splitting(cleaned_df, dataset_config)
        
        demo_enhanced_training()
        
        demo_airflow_integration()
        
        print("\n" + "="*80)
        print("🎉 ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*80)
        
        print("\n💡 Next Steps:")
        print("1. Customize dataset configuration in config/dataset_config.json")
        print("2. Add your own datasets in data/ directory")
        print("3. Run full training: python src/enhanced_bert_training.py")
        print("4. Setup Airflow for production: docker-compose up -d")
        print("5. Monitor training progress in Airflow UI")
        
        print("\n📚 Key Files Created/Used:")
        print("   • config/dataset_config.json - Dataset configuration")
        print("   • data/custom_dataset.csv - Sample custom dataset")
        print("   • src/dataset_manager.py - Dataset management")
        print("   • src/data_wrangling.py - Data exploration and cleaning")
        print("   • src/enhanced_bert_training.py - Enhanced training")
        print("   • dags/enhanced_bert_fine_tuning_dag.py - Airflow DAG")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("Please check your installation and dependencies")
        raise

if __name__ == "__main__":
    main()
