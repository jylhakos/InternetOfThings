#!/usr/bin/env python3
"""
Large language models (LLMs) Benchmarking  Script
Compares BERT, DistilBERT, and ALBERT on various tasks
"""

import time
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
import torch
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    AutoModelForQuestionAnswering, pipeline
)
from datasets import load_dataset
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import matplotlib.pyplot as plt
import seaborn as sns

class LLMBenchmarkSuite:
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
    
    def benchmark_question_answering(self, dataset_name: str = 'squad', num_samples: int = 50):
        """Benchmark Q&A performance"""
        print(f"\n--- Question Answering Benchmark ({num_samples} samples) ---")
        
        try:
            # Load dataset
            print(f"Loading {dataset_name} dataset...")
            dataset = load_dataset(dataset_name, split=f'validation[:{num_samples}]')
            print(f"✓ Dataset loaded: {len(dataset)} samples")
            
            models, tokenizers = self.load_models_for_task('qa')
            
            if not models:
                print("No models loaded successfully for QA task")
                return {}
                
            results = {}
            
            for model_name, model in models.items():
                print(f"\nTesting {model_name}...")
                
                correct_answers = 0
                total_time = 0
                exact_matches = 0
                
                for idx, example in enumerate(dataset):
                    if idx % 10 == 0:
                        print(f"Processing sample {idx}/{len(dataset)}")
                        
                    context = example['context']
                    question = example['question']
                    true_answer = example['answers']['text'][0] if example['answers']['text'] else ""
                    
                    # Tokenize input
                    inputs = tokenizers[model_name](
                        question, context,
                        return_tensors="pt",
                        max_length=512,
                        truncation=True,
                        padding=True
                    )
                    
                    start_time = time.time()
                    
                    with torch.no_grad():
                        outputs = model(**inputs)
                        answer_start = torch.argmax(outputs.start_logits)
                        answer_end = torch.argmax(outputs.end_logits) + 1
                        
                        # Extract answer
                        answer_tokens = inputs['input_ids'][0][answer_start:answer_end]
                        predicted_answer = tokenizers[model_name].decode(answer_tokens, skip_special_tokens=True)
                    
                    end_time = time.time()
                    total_time += (end_time - start_time)
                    
                    # Check exact match
                    if predicted_answer.strip().lower() == true_answer.strip().lower():
                        exact_matches += 1
                
                results[model_name] = {
                    'exact_match': exact_matches / len(dataset),
                    'avg_inference_time': total_time / len(dataset),
                    'total_samples': len(dataset),
                    'exact_matches': exact_matches
                }
                
                print(f"✓ {model_name} completed: {exact_matches}/{len(dataset)} exact matches")
            
            self.results['question_answering'] = results
            return results
            
        except Exception as e:
            print(f"Error in QA benchmark: {e}")
            return {}
    
    def benchmark_mathematical_reasoning(self, num_problems: int = 20):
        """Benchmark mathematical reasoning"""
        print(f"\n--- Mathematical Reasoning Benchmark ({num_problems} problems) ---")
        
        # Simple math problems
        math_problems = [
            {"question": "What is 15 + 7?", "answer": "22"},
            {"question": "What is 25 - 9?", "answer": "16"},
            {"question": "What is 8 × 3?", "answer": "24"},
            {"question": "What is 36 ÷ 6?", "answer": "6"},
            {"question": "If John has 12 apples and gives away 5, how many does he have left?", "answer": "7"},
            {"question": "What is 100 + 50?", "answer": "150"},
            {"question": "What is 200 - 75?", "answer": "125"},
            {"question": "What is 9 × 4?", "answer": "36"},
            {"question": "What is 48 ÷ 8?", "answer": "6"},
            {"question": "If there are 24 hours in a day, how many hours are in 2 days?", "answer": "48"}
        ]
        
        # Extend problems if needed
        while len(math_problems) < num_problems:
            math_problems.extend(math_problems)
        
        math_problems = math_problems[:num_problems]
        
        models, _ = self.load_models_for_task('generation')
        
        if not models:
            print("No models loaded successfully for mathematical reasoning")
            return {}
            
        results = {}
        
        for model_name, model in models.items():
            print(f"\nTesting {model_name} on math problems...")
            
            correct = 0
            total_time = 0
            
            for idx, problem in enumerate(math_problems):
                if idx % 5 == 0:
                    print(f"Processing problem {idx}/{len(math_problems)}")
                    
                prompt = f"Question: {problem['question']}\nAnswer:"
                
                start_time = time.time()
                try:
                    response = model(prompt, max_length=50, num_return_sequences=1, do_sample=False)
                    generated_text = response[0]['generated_text'] if isinstance(response, list) else response['generated_text']
                except Exception as e:
                    print(f"Error generating response: {e}")
                    generated_text = ""
                    
                end_time = time.time()
                total_time += (end_time - start_time)
                
                # Extract answer (simple approach)
                import re
                if "Answer:" in generated_text:
                    answer_part = generated_text.split("Answer:")[-1].strip()
                else:
                    answer_part = generated_text.split(problem['question'])[-1].strip()
                
                numbers = re.findall(r'\d+', answer_part)
                predicted_answer = numbers[0] if numbers else ""
                
                if predicted_answer == problem['answer']:
                    correct += 1
            
            results[model_name] = {
                'accuracy': correct / len(math_problems),
                'avg_inference_time': total_time / len(math_problems),
                'correct_answers': correct,
                'total_problems': len(math_problems)
            }
            
            print(f"✓ {model_name} completed: {correct}/{len(math_problems)} correct answers")
        
        self.results['mathematical_reasoning'] = results
        return results
    
    def benchmark_text_classification(self, dataset_name: str = 'imdb', num_samples: int = 100):
        """Benchmark text classification"""
        print(f"\n--- Text Classification Benchmark ({num_samples} samples) ---")
        
        try:
            # Load dataset
            print(f"Loading {dataset_name} dataset...")
            dataset = load_dataset(dataset_name, split=f'test[:{num_samples}]')
            print(f"✓ Dataset loaded: {len(dataset)} samples")
            
            models, tokenizers = self.load_models_for_task('classification')
            
            if not models:
                print("No models loaded successfully for classification task")
                return {}
                
            results = {}
            
            for model_name, model in models.items():
                print(f"\nTesting {model_name}...")
                
                predictions = []
                true_labels = []
                total_time = 0
                
                for idx, example in enumerate(dataset):
                    if idx % 20 == 0:
                        print(f"Processing sample {idx}/{len(dataset)}")
                        
                    text = example['text']
                    label = example['label']
                    
                    inputs = tokenizers[model_name](
                        text,
                        return_tensors="pt",
                        max_length=512,
                        truncation=True,
                        padding=True
                    )
                    
                    start_time = time.time()
                    
                    with torch.no_grad():
                        outputs = model(**inputs)
                        prediction = torch.argmax(outputs.logits, dim=-1).item()
                    
                    end_time = time.time()
                    total_time += (end_time - start_time)
                    
                    predictions.append(prediction)
                    true_labels.append(label)
                
                # Calculate metrics
                accuracy = accuracy_score(true_labels, predictions)
                f1 = f1_score(true_labels, predictions, average='weighted')
                precision = precision_score(true_labels, predictions, average='weighted')
                recall = recall_score(true_labels, predictions, average='weighted')
                
                results[model_name] = {
                    'accuracy': accuracy,
                    'f1_score': f1,
                    'precision': precision,
                    'recall': recall,
                    'avg_inference_time': total_time / len(dataset)
                }
                
                print(f"✓ {model_name} completed: {accuracy:.3f} accuracy")
            
            self.results['text_classification'] = results
            return results
            
        except Exception as e:
            print(f"Error in text classification benchmark: {e}")
            return {}
    
    def create_visualizations(self):
        """Create benchmark visualization plots"""
        print("\n--- Creating Visualizations ---")
        
        if not self.results:
            print("No results to visualize")
            return
            
        # Create results directory
        Path("results").mkdir(exist_ok=True)
        
        # Plot 1: Accuracy comparison across tasks
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('LLM Benchmark Results Comparison', fontsize=16)
        
        # Accuracy comparison
        if 'text_classification' in self.results:
            models = list(self.results['text_classification'].keys())
            accuracies = [self.results['text_classification'][m]['accuracy'] for m in models]
            
            axes[0, 0].bar(models, accuracies, color=['blue', 'green', 'red'])
            axes[0, 0].set_title('Text Classification Accuracy')
            axes[0, 0].set_ylabel('Accuracy')
            axes[0, 0].set_ylim(0, 1)
            
        # Inference time comparison
        if 'text_classification' in self.results:
            inf_times = [self.results['text_classification'][m]['avg_inference_time'] * 1000 for m in models]
            
            axes[0, 1].bar(models, inf_times, color=['blue', 'green', 'red'])
            axes[0, 1].set_title('Average Inference Time (ms)')
            axes[0, 1].set_ylabel('Time (ms)')
            
        # Mathematical reasoning accuracy
        if 'mathematical_reasoning' in self.results:
            models_math = list(self.results['mathematical_reasoning'].keys())
            math_acc = [self.results['mathematical_reasoning'][m]['accuracy'] for m in models_math]
            
            axes[1, 0].bar(models_math, math_acc, color=['blue', 'green', 'red'])
            axes[1, 0].set_title('Mathematical Reasoning Accuracy')
            axes[1, 0].set_ylabel('Accuracy')
            axes[1, 0].set_ylim(0, 1)
            
        # QA exact match
        if 'question_answering' in self.results:
            models_qa = list(self.results['question_answering'].keys())
            qa_acc = [self.results['question_answering'][m]['exact_match'] for m in models_qa]
            
            axes[1, 1].bar(models_qa, qa_acc, color=['blue', 'green', 'red'])
            axes[1, 1].set_title('Question Answering Exact Match')
            axes[1, 1].set_ylabel('Exact Match Rate')
            axes[1, 1].set_ylim(0, 1)
        
        plt.tight_layout()
        plt.savefig('results/benchmark_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("✓ Visualization saved to results/benchmark_comparison.png")
    
    def generate_report(self, output_file: str = 'results/benchmark_results.json'):
        """Generate comprehensive benchmark report"""
        print(f"\n--- Generating Benchmark Report ---")
        
        # Create results directory
        Path("results").mkdir(exist_ok=True)
        
        # Save results to JSON
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        # Generate summary table
        summary_data = []
        
        for task, task_results in self.results.items():
            for model, metrics in task_results.items():
                row = {'Task': task, 'Model': model}
                row.update(metrics)
                summary_data.append(row)
        
        if summary_data:
            df = pd.DataFrame(summary_data)
            
            # Save to CSV
            csv_file = 'results/benchmark_summary.csv'
            df.to_csv(csv_file, index=False)
            
            # Print summary
            print("\n=== BENCHMARK SUMMARY ===")
            print(df.to_string(index=False))
            
            print(f"\n✓ Results saved to: {output_file}")
            print(f"✓ Summary saved to: {csv_file}")
            
            return df
        else:
            print("No results to generate report")
            return None

def main():
    """Run complete benchmark suite"""
    print("🚀 LLM Benchmarking Suite")
    print("=" * 50)
    
    benchmark = LLMBenchmarkSuite()
    
    try:
        # Run benchmarks with smaller sample sizes for quick testing
        print("Starting benchmark runs...")
        
        # Text classification
        benchmark.benchmark_text_classification(num_samples=50)
        
        # Mathematical reasoning  
        benchmark.benchmark_mathematical_reasoning(num_problems=10)
        
        # Question answering (commented out by default due to potential memory issues)
        # benchmark.benchmark_question_answering(num_samples=20)
        
        # Generate report and visualizations
        report = benchmark.generate_report()
        benchmark.create_visualizations()
        
        print(f"\n🎉 Benchmarking completed successfully!")
        print(f"Check the 'results/' directory for detailed output.")
        
    except Exception as e:
        print(f"\n❌ Error during benchmarking: {e}")
        print("This might be due to memory constraints or model loading issues.")
        print("Try reducing the number of samples or running individual benchmarks.")

if __name__ == "__main__":
    main()
