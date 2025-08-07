#!/usr/bin/env python3
"""
Enhanced LLM Benchmarking Suite with Zero-shot, Few-shot, and Fine-tuned Testing
Compares BERT, DistilBERT, and ALBERT across different testing paradigms
"""

import time
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import torch
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    AutoModelForQuestionAnswering, pipeline, Trainer, TrainingArguments
)
from datasets import load_dataset, Dataset
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

class EnhancedLLMBenchmarkSuite:
    def __init__(self):
        self.models = {
            'BERT': 'bert-base-uncased',
            'DistilBERT': 'distilbert-base-uncased',
            'ALBERT': 'albert-base-v2'
        }
        self.results = {}
        
    def load_models_for_task(self, task_type: str):
        """Load models for specific task"""
        loaded_models = {}
        tokenizers = {}
        
        for name, model_name in self.models.items():
            print(f"Loading {name} for {task_type}...")
            
            try:
                tokenizers[name] = AutoTokenizer.from_pretrained(model_name)
                
                if task_type == 'classification':
                    loaded_models[name] = AutoModelForSequenceClassification.from_pretrained(model_name)
                elif task_type == 'qa':
                    loaded_models[name] = AutoModelForQuestionAnswering.from_pretrained(model_name)
                elif task_type == 'generation':
                    loaded_models[name] = pipeline("text-generation", model=model_name, max_length=100)
                    
                print(f"✓ {name} loaded successfully")
                    
            except Exception as e:
                print(f"✗ Error loading {name}: {e}")
                continue
                
        return loaded_models, tokenizers

    def zero_shot_text_classification(self, dataset_name: str = 'imdb', num_samples: int = 50):
        """Zero-shot text classification - no examples provided"""
        print(f"\n=== ZERO-SHOT TEXT CLASSIFICATION ===")
        print(f"Dataset: {dataset_name}, Samples: {num_samples}")
        
        try:
            dataset = load_dataset(dataset_name, split=f'test[:{num_samples}]')
            models, tokenizers = self.load_models_for_task('classification')
            
            if not models:
                return {}
                
            results = {}
            
            for model_name, model in models.items():
                print(f"\nTesting {model_name} (Zero-shot)...")
                
                predictions = []
                true_labels = []
                inference_times = []
                
                for idx, example in enumerate(dataset):
                    if idx % 10 == 0:
                        print(f"  Processing {idx}/{len(dataset)}")
                        
                    text = example['text']
                    label = example['label']
                    
                    inputs = tokenizers[model_name](
                        text, return_tensors="pt", max_length=512, 
                        truncation=True, padding=True
                    )
                    
                    start_time = time.time()
                    with torch.no_grad():
                        outputs = model(**inputs)
                        prediction = torch.argmax(outputs.logits, dim=-1).item()
                    end_time = time.time()
                    
                    predictions.append(prediction)
                    true_labels.append(label)
                    inference_times.append(end_time - start_time)
                
                # Calculate metrics
                accuracy = accuracy_score(true_labels, predictions)
                f1 = f1_score(true_labels, predictions, average='weighted')
                avg_time = np.mean(inference_times)
                
                results[model_name] = {
                    'approach': 'zero-shot',
                    'accuracy': accuracy,
                    'f1_score': f1,
                    'avg_inference_time': avg_time,
                    'total_samples': len(dataset)
                }
                
                print(f"  ✓ {model_name}: {accuracy:.3f} accuracy, {avg_time:.3f}s avg time")
            
            return results
            
        except Exception as e:
            print(f"Error in zero-shot classification: {e}")
            return {}

    def few_shot_text_classification(self, dataset_name: str = 'imdb', num_samples: int = 50, num_examples: int = 3):
        """Few-shot text classification with examples in prompts"""
        print(f"\n=== FEW-SHOT TEXT CLASSIFICATION ===")
        print(f"Dataset: {dataset_name}, Samples: {num_samples}, Examples: {num_examples}")
        
        try:
            # Load full dataset to get examples
            full_dataset = load_dataset(dataset_name)
            train_data = full_dataset['train'].shuffle(seed=42)
            test_data = full_dataset['test'].shuffle(seed=42).select(range(num_samples))
            
            # Get examples for few-shot prompts
            pos_examples = [ex for ex in train_data if ex['label'] == 1][:num_examples//2 + 1]
            neg_examples = [ex for ex in train_data if ex['label'] == 0][:num_examples//2]
            examples = pos_examples + neg_examples
            
            results = {}
            
            # Use generation pipeline for few-shot
            for model_name in self.models.keys():
                print(f"\nTesting {model_name} (Few-shot)...")
                
                try:
                    generator = pipeline(
                        "text-generation", 
                        model=self.models[model_name],
                        tokenizer=self.models[model_name],
                        device=0 if torch.cuda.is_available() else -1
                    )
                except:
                    print(f"  Skipping {model_name} - generation pipeline not available")
                    continue
                
                predictions = []
                true_labels = []
                inference_times = []
                
                # Build few-shot prompt template
                prompt_template = "Classify the sentiment of movie reviews as 'positive' or 'negative'.\n\nExamples:\n"
                for ex in examples:
                    sentiment = "positive" if ex['label'] == 1 else "negative"
                    text_snippet = ex['text'][:150] + "..." if len(ex['text']) > 150 else ex['text']
                    prompt_template += f"Review: {text_snippet}\nSentiment: {sentiment}\n\n"
                
                for idx, example in enumerate(test_data):
                    if idx % 5 == 0:
                        print(f"  Processing {idx}/{len(test_data)}")
                    
                    text = example['text'][:200]  # Limit text length
                    true_label = example['label']
                    
                    prompt = prompt_template + f"Review: {text}\nSentiment:"
                    
                    start_time = time.time()
                    try:
                        response = generator(
                            prompt, 
                            max_new_tokens=5,
                            num_return_sequences=1,
                            do_sample=False,
                            pad_token_id=generator.tokenizer.eos_token_id
                        )
                        generated_text = response[0]['generated_text']
                        
                        # Extract prediction from generated text
                        answer = generated_text.split("Sentiment:")[-1].strip().lower()
                        if 'positive' in answer[:20]:
                            prediction = 1
                        elif 'negative' in answer[:20]:
                            prediction = 0
                        else:
                            prediction = 0  # Default to negative
                            
                    except Exception as e:
                        print(f"    Generation error: {e}")
                        prediction = 0  # Default
                    
                    end_time = time.time()
                    
                    predictions.append(prediction)
                    true_labels.append(true_label)
                    inference_times.append(end_time - start_time)
                
                # Calculate metrics
                accuracy = accuracy_score(true_labels, predictions)
                f1 = f1_score(true_labels, predictions, average='weighted')
                avg_time = np.mean(inference_times)
                
                results[model_name] = {
                    'approach': 'few-shot',
                    'accuracy': accuracy,
                    'f1_score': f1,
                    'avg_inference_time': avg_time,
                    'num_examples': num_examples,
                    'total_samples': len(test_data)
                }
                
                print(f"  ✓ {model_name}: {accuracy:.3f} accuracy, {avg_time:.3f}s avg time")
            
            return results
            
        except Exception as e:
            print(f"Error in few-shot classification: {e}")
            return {}

    def fine_tuned_text_classification(self, dataset_name: str = 'imdb', num_train: int = 1000, num_test: int = 200, epochs: int = 2):
        """Fine-tuned text classification with task-specific training"""
        print(f"\n=== FINE-TUNED TEXT CLASSIFICATION ===")
        print(f"Dataset: {dataset_name}, Train: {num_train}, Test: {num_test}, Epochs: {epochs}")
        
        try:
            # Load dataset
            dataset = load_dataset(dataset_name)
            train_data = dataset['train'].shuffle(seed=42).select(range(num_train))
            test_data = dataset['test'].shuffle(seed=42).select(range(num_test))
            
            results = {}
            
            for model_name, model_path in self.models.items():
                print(f"\nFine-tuning {model_name}...")
                
                # Load fresh model and tokenizer
                tokenizer = AutoTokenizer.from_pretrained(model_path)
                model = AutoModelForSequenceClassification.from_pretrained(
                    model_path, num_labels=2
                )
                
                # Add padding token if necessary
                if tokenizer.pad_token is None:
                    tokenizer.pad_token = tokenizer.eos_token
                    model.config.pad_token_id = tokenizer.pad_token_id
                
                # Tokenize datasets
                def tokenize_function(examples):
                    return tokenizer(
                        examples['text'], 
                        truncation=True, 
                        padding=True, 
                        max_length=256  # Reduced for memory
                    )
                
                train_tokenized = train_data.map(tokenize_function, batched=True)
                test_tokenized = test_data.map(tokenize_function, batched=True)
                
                # Set format for PyTorch
                train_tokenized.set_format(type='torch', columns=['input_ids', 'attention_mask', 'label'])
                test_tokenized.set_format(type='torch', columns=['input_ids', 'attention_mask', 'label'])
                
                # Training arguments
                training_args = TrainingArguments(
                    output_dir=f'./fine_tuned/{model_name.lower()}',
                    num_train_epochs=epochs,
                    per_device_train_batch_size=8,  # Reduced batch size
                    per_device_eval_batch_size=16,
                    warmup_steps=100,
                    weight_decay=0.01,
                    logging_steps=50,
                    evaluation_strategy="epoch",
                    save_strategy="no",  # Don't save to reduce disk usage
                    load_best_model_at_end=False,
                    dataloader_pin_memory=False,
                )
                
                # Trainer
                trainer = Trainer(
                    model=model,
                    args=training_args,
                    train_dataset=train_tokenized,
                    eval_dataset=test_tokenized,
                )
                
                # Fine-tune
                print(f"  Training {model_name}...")
                start_time = time.time()
                trainer.train()
                training_time = time.time() - start_time
                
                # Evaluate
                print(f"  Evaluating {model_name}...")
                start_time = time.time()
                predictions = trainer.predict(test_tokenized)
                inference_time = time.time() - start_time
                
                predicted_labels = np.argmax(predictions.predictions, axis=1)
                true_labels = test_data['label']
                
                # Calculate metrics
                accuracy = accuracy_score(true_labels, predicted_labels)
                f1 = f1_score(true_labels, predicted_labels, average='weighted')
                avg_inference_time = inference_time / len(test_data)
                
                results[model_name] = {
                    'approach': 'fine-tuned',
                    'accuracy': accuracy,
                    'f1_score': f1,
                    'training_time': training_time,
                    'avg_inference_time': avg_inference_time,
                    'epochs': epochs,
                    'train_samples': len(train_data),
                    'test_samples': len(test_data)
                }
                
                print(f"  ✓ {model_name}: {accuracy:.3f} accuracy, {training_time:.1f}s training")
                
                # Clean up to save memory
                del model, trainer, tokenizer
                torch.cuda.empty_cache() if torch.cuda.is_available() else None
            
            return results
            
        except Exception as e:
            print(f"Error in fine-tuned classification: {e}")
            return {}

    def run_comprehensive_benchmark(self, quick_mode: bool = True):
        """Run all three testing approaches"""
        print("🚀 COMPREHENSIVE LLM BENCHMARKING SUITE")
        print("=" * 60)
        
        # Adjust sample sizes based on mode
        if quick_mode:
            samples = {'num_samples': 30, 'num_train': 500, 'num_test': 50, 'epochs': 1}
            print("Running in QUICK MODE (reduced samples for faster execution)")
        else:
            samples = {'num_samples': 100, 'num_train': 2000, 'num_test': 200, 'epochs': 3}
            print("Running in FULL MODE")
        
        print(f"Samples: {samples}")
        
        # Run benchmarks
        self.results = {}
        
        # Zero-shot
        print(f"\n{'='*20} ZERO-SHOT TESTING {'='*20}")
        zero_shot = self.zero_shot_text_classification(num_samples=samples['num_samples'])
        if zero_shot:
            self.results['zero_shot'] = zero_shot
        
        # Few-shot
        print(f"\n{'='*20} FEW-SHOT TESTING {'='*20}")
        few_shot = self.few_shot_text_classification(num_samples=samples['num_samples'])
        if few_shot:
            self.results['few_shot'] = few_shot
        
        # Fine-tuned (only in full mode due to computational requirements)
        if not quick_mode:
            print(f"\n{'='*20} FINE-TUNED TESTING {'='*20}")
            fine_tuned = self.fine_tuned_text_classification(
                num_train=samples['num_train'], 
                num_test=samples['num_test'], 
                epochs=samples['epochs']
            )
            if fine_tuned:
                self.results['fine_tuned'] = fine_tuned
        else:
            print(f"\n{'='*20} FINE-TUNED TESTING {'='*20}")
            print("⚠️  Fine-tuning skipped in quick mode (enable full mode for fine-tuning)")
        
        return self.results

    def generate_comprehensive_report(self, save_file: str = 'comprehensive_benchmark_results.json'):
        """Generate detailed report comparing all approaches"""
        if not self.results:
            print("No results to report. Run benchmarks first.")
            return
        
        print(f"\n{'='*80}")
        print("COMPREHENSIVE BENCHMARKING REPORT")
        print(f"{'='*80}")
        
        # Create comparison DataFrame
        comparison_data = []
        
        for approach_name, approach_results in self.results.items():
            for model_name, metrics in approach_results.items():
                row = {
                    'Testing_Approach': approach_name.replace('_', '-').title(),
                    'Model': model_name,
                    'Accuracy': f"{metrics['accuracy']:.3f}",
                    'F1_Score': f"{metrics['f1_score']:.3f}",
                    'Avg_Inference_Time_ms': f"{metrics['avg_inference_time']*1000:.1f}",
                }
                
                # Add approach-specific metrics
                if 'num_examples' in metrics:
                    row['Examples_Used'] = metrics['num_examples']
                if 'epochs' in metrics:
                    row['Training_Epochs'] = metrics['epochs']
                if 'training_time' in metrics:
                    row['Training_Time_s'] = f"{metrics['training_time']:.1f}"
                
                comparison_data.append(row)
        
        df = pd.DataFrame(comparison_data)
        
        # Display results
        print("\nPERFORMance COMPARISON TABLE:")
        print("-" * 80)
        print(df.to_string(index=False))
        
        # Performance insights
        print(f"\n{'PERFORMANCE INSIGHTS':^80}")
        print("-" * 80)
        
        if 'zero_shot' in self.results and 'few_shot' in self.results:
            print("📊 Zero-shot vs Few-shot Performance:")
            for model in self.models.keys():
                if model in self.results['zero_shot'] and model in self.results['few_shot']:
                    zero_acc = self.results['zero_shot'][model]['accuracy']
                    few_acc = self.results['few_shot'][model]['accuracy']
                    improvement = (few_acc - zero_acc) * 100
                    print(f"   {model}: {improvement:+.1f}% improvement with few-shot")
        
        if 'fine_tuned' in self.results:
            print("\n🔥 Fine-tuning Performance:")
            for model, metrics in self.results['fine_tuned'].items():
                print(f"   {model}: {metrics['accuracy']:.1%} accuracy after {metrics['epochs']} epochs")
        
        # Resource efficiency
        print(f"\n⚡ Resource Efficiency Ranking (by inference speed):")
        if any(self.results.values()):
            speed_data = []
            for approach, models in self.results.items():
                for model, metrics in models.items():
                    speed_data.append({
                        'model': model,
                        'approach': approach,
                        'speed_ms': metrics['avg_inference_time'] * 1000
                    })
            
            speed_df = pd.DataFrame(speed_data).sort_values('speed_ms')
            for i, row in speed_df.head(5).iterrows():
                print(f"   {row['model']} ({row['approach']}): {row['speed_ms']:.1f}ms")
        
        # Save results
        Path("results").mkdir(exist_ok=True)
        
        with open(f"results/{save_file}", 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        df.to_csv(f"results/comprehensive_benchmark_summary.csv", index=False)
        
        print(f"\n✅ Detailed results saved to: results/{save_file}")
        print(f"✅ Summary table saved to: results/comprehensive_benchmark_summary.csv")
        
        return df

    def create_performance_plots(self):
        """Create visualization plots comparing approaches"""
        if not self.results:
            print("No results available for plotting")
            return
        
        Path("results").mkdir(exist_ok=True)
        
        # Prepare data for plotting
        plot_data = []
        for approach, models in self.results.items():
            for model, metrics in models.items():
                plot_data.append({
                    'Approach': approach.replace('_', '-').title(),
                    'Model': model,
                    'Accuracy': metrics['accuracy'],
                    'F1_Score': metrics['f1_score'],
                    'Inference_Time_ms': metrics['avg_inference_time'] * 1000
                })
        
        if not plot_data:
            print("No data available for plotting")
            return
        
        df_plot = pd.DataFrame(plot_data)
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('LLM Benchmarking Results: Testing Approaches Comparison', fontsize=16)
        
        # Accuracy comparison
        pivot_acc = df_plot.pivot(index='Model', columns='Approach', values='Accuracy')
        pivot_acc.plot(kind='bar', ax=axes[0, 0], color=['#1f77b4', '#ff7f0e', '#2ca02c'])
        axes[0, 0].set_title('Accuracy by Testing Approach')
        axes[0, 0].set_ylabel('Accuracy')
        axes[0, 0].legend(title='Testing Approach')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # F1 Score comparison
        pivot_f1 = df_plot.pivot(index='Model', columns='Approach', values='F1_Score')
        pivot_f1.plot(kind='bar', ax=axes[0, 1], color=['#1f77b4', '#ff7f0e', '#2ca02c'])
        axes[0, 1].set_title('F1 Score by Testing Approach')
        axes[0, 1].set_ylabel('F1 Score')
        axes[0, 1].legend(title='Testing Approach')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Inference time comparison
        pivot_time = df_plot.pivot(index='Model', columns='Approach', values='Inference_Time_ms')
        pivot_time.plot(kind='bar', ax=axes[1, 0], color=['#1f77b4', '#ff7f0e', '#2ca02c'])
        axes[1, 0].set_title('Inference Time by Testing Approach')
        axes[1, 0].set_ylabel('Time (ms)')
        axes[1, 0].legend(title='Testing Approach')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Performance vs Speed scatter
        axes[1, 1].scatter(df_plot['Inference_Time_ms'], df_plot['Accuracy'], 
                          c=pd.Categorical(df_plot['Approach']).codes, 
                          s=100, alpha=0.7, cmap='viridis')
        axes[1, 1].set_xlabel('Inference Time (ms)')
        axes[1, 1].set_ylabel('Accuracy')
        axes[1, 1].set_title('Accuracy vs Inference Time')
        
        # Add model labels to scatter plot
        for _, row in df_plot.iterrows():
            axes[1, 1].annotate(f"{row['Model'][:4]}", 
                              (row['Inference_Time_ms'], row['Accuracy']),
                              xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        plt.tight_layout()
        plt.savefig('results/comprehensive_benchmark_plots.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("📈 Performance plots saved to: results/comprehensive_benchmark_plots.png")

def main():
    """Run the comprehensive benchmark suite"""
    print("🔬 Enhanced LLM Benchmarking Suite")
    print("Testing Zero-shot, Few-shot, and Fine-tuned approaches")
    print("=" * 70)
    
    # Initialize benchmark suite
    benchmark = EnhancedLLMBenchmarkSuite()
    
    # Ask user for mode selection
    print("\nSelect benchmark mode:")
    print("1. Quick Mode (faster, reduced samples)")
    print("2. Full Mode (comprehensive, longer runtime)")
    
    choice = input("Enter choice (1/2) [default: 1]: ").strip()
    quick_mode = choice != '2'
    
    try:
        # Run benchmarks
        results = benchmark.run_comprehensive_benchmark(quick_mode=quick_mode)
        
        if results:
            # Generate report
            report = benchmark.generate_comprehensive_report()
            
            # Create visualizations
            benchmark.create_performance_plots()
            
            print(f"\n🎉 Comprehensive benchmarking completed successfully!")
            print(f"   Check the 'results/' directory for detailed outputs")
        else:
            print("❌ No results generated. Check for errors above.")
            
    except Exception as e:
        print(f"❌ Error during benchmarking: {e}")
        print("   This might be due to memory constraints or model loading issues.")
        print("   Try running in quick mode or with fewer samples.")

if __name__ == "__main__":
    main()
