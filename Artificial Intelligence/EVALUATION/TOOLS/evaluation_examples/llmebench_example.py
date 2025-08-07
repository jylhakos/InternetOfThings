#!/usr/bin/env python3
"""
LLMeBench Example for BERT Model Evaluation
Multi-lingual benchmarking framework for standardized LLM evaluation
"""

import os
import json
import requests
import subprocess
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class BenchmarkTask:
    """Benchmark task configuration"""
    task_name: str
    description: str
    language: str
    dataset_name: str
    metrics: List[str]

class BERTLLMeBenchTester:
    """LLMeBench integration for BERT evaluation"""
    
    def __init__(self, model_name: str = "bert-base-uncased"):
        self.model_name = model_name
        self.benchmark_results = {}
        
        # Available benchmark tasks
        self.available_tasks = {
            'sentiment': BenchmarkTask(
                task_name="sentiment_analysis",
                description="Sentiment classification task",
                language="en",
                dataset_name="imdb",
                metrics=["accuracy", "f1", "precision", "recall"]
            ),
            'qa': BenchmarkTask(
                task_name="question_answering",
                description="Question answering evaluation",
                language="en", 
                dataset_name="squad",
                metrics=["exact_match", "f1", "bertscore"]
            ),
            'classification': BenchmarkTask(
                task_name="text_classification",
                description="General text classification",
                language="en",
                dataset_name="ag_news",
                metrics=["accuracy", "macro_f1", "weighted_f1"]
            )
        }
    
    def check_llmebench_installation(self) -> bool:
        """Check if LLMeBench is installed and available"""
        try:
            # Try to import or run LLMeBench
            result = subprocess.run(['python', '-c', 'import llmebench'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ LLMeBench is available")
                return True
        except Exception as e:
            pass
        
        print("❌ LLMeBench not found")
        print("📦 Clone from: git clone https://github.com/qcri/LLMeBench.git")
        return False
    
    def install_llmebench(self):
        """Install LLMeBench framework"""
        print("📦 Installing LLMeBench...")
        
        install_script = '''
# Clone LLMeBench repository
git clone https://github.com/qcri/LLMeBench.git
cd LLMeBench

# Install dependencies
pip install -r requirements.txt

# Install LLMeBench package
pip install -e .

# Verify installation
python -c "import llmebench; print('LLMeBench installed successfully')"
'''
        
        with open("evaluation_examples/install_llmebench.sh", "w") as f:
            f.write(install_script)
        
        print("📁 Installation script created: evaluation_examples/install_llmebench.sh")
        print("🚀 Run: bash evaluation_examples/install_llmebench.sh")
    
    def create_benchmark_config(self, task: BenchmarkTask) -> Dict[str, Any]:
        """Create LLMeBench configuration for a task"""
        
        config = {
            "model": {
                "name": self.model_name,
                "type": "huggingface",
                "path": self.model_name,
                "tokenizer": self.model_name
            },
            "task": {
                "name": task.task_name,
                "type": "classification",
                "language": task.language,
                "dataset": {
                    "name": task.dataset_name,
                    "split": "test",
                    "max_samples": 1000
                }
            },
            "evaluation": {
                "metrics": task.metrics,
                "batch_size": 16,
                "max_length": 512
            },
            "output": {
                "save_predictions": True,
                "save_results": True,
                "output_dir": f"evaluation_examples/llmebench_results/{task.task_name}"
            }
        }
        
        return config
    
    def run_benchmark_task(self, task_name: str) -> Dict[str, Any]:
        """Run a specific benchmark task"""
        
        if task_name not in self.available_tasks:
            return {"error": f"Task {task_name} not available"}
        
        task = self.available_tasks[task_name]
        config = self.create_benchmark_config(task)
        
        print(f"🏆 Running LLMeBench task: {task.description}")
        print(f"📊 Metrics: {', '.join(task.metrics)}")
        
        # Save configuration
        config_path = f"evaluation_examples/llmebench_{task_name}_config.json"
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        
        # Simulate benchmark execution (replace with actual LLMeBench call)
        if self.check_llmebench_installation():
            try:
                # This would be the actual LLMeBench command
                cmd = f"python -m llmebench.run --config {config_path}"
                result = subprocess.run(cmd.split(), capture_output=True, text=True)
                
                if result.returncode == 0:
                    return self.parse_benchmark_results(task_name)
                else:
                    return {"error": f"Benchmark failed: {result.stderr}"}
            except Exception as e:
                return {"error": f"Execution error: {str(e)}"}
        else:
            # Create simulated results for demo
            return self.create_simulated_results(task)
    
    def create_simulated_results(self, task: BenchmarkTask) -> Dict[str, Any]:
        """Create simulated benchmark results for demo purposes"""
        
        import random
        random.seed(42)  # Reproducible results
        
        results = {
            "task": task.task_name,
            "model": self.model_name,
            "dataset": task.dataset_name,
            "language": task.language,
            "metrics": {}
        }
        
        # Generate realistic scores based on task type
        if task.task_name == "sentiment_analysis":
            results["metrics"] = {
                "accuracy": round(random.uniform(0.82, 0.89), 3),
                "f1": round(random.uniform(0.81, 0.88), 3),
                "precision": round(random.uniform(0.80, 0.87), 3),
                "recall": round(random.uniform(0.83, 0.90), 3)
            }
        elif task.task_name == "question_answering":
            results["metrics"] = {
                "exact_match": round(random.uniform(0.75, 0.82), 3),
                "f1": round(random.uniform(0.83, 0.89), 3),
                "bertscore": round(random.uniform(0.88, 0.93), 3)
            }
        else:  # text_classification
            results["metrics"] = {
                "accuracy": round(random.uniform(0.86, 0.92), 3),
                "macro_f1": round(random.uniform(0.84, 0.90), 3),
                "weighted_f1": round(random.uniform(0.85, 0.91), 3)
            }
        
        return results
    
    def parse_benchmark_results(self, task_name: str) -> Dict[str, Any]:
        """Parse results from LLMeBench output"""
        
        results_dir = f"evaluation_examples/llmebench_results/{task_name}"
        results_file = f"{results_dir}/results.json"
        
        try:
            if os.path.exists(results_file):
                with open(results_file, "r") as f:
                    return json.load(f)
            else:
                return {"error": "Results file not found"}
        except Exception as e:
            return {"error": f"Failed to parse results: {str(e)}"}
    
    def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run all available benchmark tasks"""
        
        print("🏆 Running Comprehensive LLMeBench Evaluation")
        print("="*50)
        
        all_results = {
            "model": self.model_name,
            "framework": "LLMeBench", 
            "tasks": {},
            "summary": {}
        }
        
        for task_name, task in self.available_tasks.items():
            print(f"\n📋 Running {task.description}...")
            
            results = self.run_benchmark_task(task_name)
            all_results["tasks"][task_name] = results
            
            if "metrics" in results:
                # Display results
                print(f"   Results for {task_name}:")
                for metric, score in results["metrics"].items():
                    print(f"   - {metric}: {score:.3f}")
        
        # Calculate summary statistics
        all_results["summary"] = self.calculate_summary_stats(all_results["tasks"])
        
        return all_results
    
    def calculate_summary_stats(self, task_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate summary statistics across all tasks"""
        
        all_scores = []
        task_count = 0
        
        for task_name, results in task_results.items():
            if "metrics" in results:
                task_count += 1
                for metric, score in results["metrics"].items():
                    if isinstance(score, (int, float)):
                        all_scores.append(score)
        
        if all_scores:
            return {
                "average_score": sum(all_scores) / len(all_scores),
                "min_score": min(all_scores),
                "max_score": max(all_scores),
                "tasks_completed": task_count,
                "total_metrics": len(all_scores)
            }
        else:
            return {"error": "No valid scores found"}
    
    def export_results(self, results: Dict[str, Any], filename: str = "llmebench_results.json"):
        """Export benchmark results"""
        
        output_path = f"evaluation_examples/{filename}"
        
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"📁 Results exported to: {output_path}")
        return output_path
    
    def create_leaderboard_entry(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Create leaderboard entry for model comparison"""
        
        entry = {
            "model_name": self.model_name,
            "timestamp": str(pd.Timestamp.now() if 'pd' in globals() else "2025-08-07"),
            "overall_score": results["summary"].get("average_score", 0),
            "task_scores": {}
        }
        
        for task_name, task_results in results["tasks"].items():
            if "metrics" in task_results:
                # Use the first metric as representative score
                first_metric = list(task_results["metrics"].keys())[0]
                entry["task_scores"][task_name] = task_results["metrics"][first_metric]
        
        return entry

def run_llmebench_example():
    """Run complete LLMeBench example"""
    print("🏆 LLMeBench BERT Evaluation Example")
    print("="*50)
    
    # Initialize evaluator
    evaluator = BERTLLMeBenchTester("bert-base-uncased")
    
    # Check installation
    if not evaluator.check_llmebench_installation():
        evaluator.install_llmebench()
        print("⚠️ Please install LLMeBench first, then rerun this script")
        return
    
    # Run comprehensive benchmark
    results = evaluator.run_comprehensive_benchmark()
    
    # Display summary
    print(f"\n📈 LLMEBENCH EVALUATION SUMMARY")
    print("-" * 40)
    
    summary = results.get("summary", {})
    if "error" not in summary:
        print(f"Average Score: {summary['average_score']:.3f}")
        print(f"Tasks Completed: {summary['tasks_completed']}")
        print(f"Total Metrics: {summary['total_metrics']}")
        print(f"Score Range: {summary['min_score']:.3f} - {summary['max_score']:.3f}")
    else:
        print(f"Summary Error: {summary['error']}")
    
    # Export results
    evaluator.export_results(results)
    
    # Create leaderboard entry
    leaderboard_entry = evaluator.create_leaderboard_entry(results)
    evaluator.export_results(leaderboard_entry, "llmebench_leaderboard_entry.json")
    
    print(f"\n🎯 LLMeBench Recommendations:")
    print("- Standardized benchmarking protocols")
    print("- Multi-lingual evaluation support") 
    print("- Fair model comparison framework")
    print("- Integration with research leaderboards")

def create_aws_deployment_script():
    """Create AWS deployment script for LLMeBench"""
    
    aws_script = '''#!/bin/bash
# AWS LLMeBench Deployment Script
# Deploy standardized BERT benchmarking to AWS Batch

# 1. Create ECR repository for custom image
aws ecr create-repository --repository-name bert-llmebench

# 2. Create Dockerfile for LLMeBench
cat > Dockerfile.llmebench << 'EOF'
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y git

# Clone and install LLMeBench
RUN git clone https://github.com/qcri/LLMeBench.git
WORKDIR /app/LLMeBench
RUN pip install -r requirements.txt
RUN pip install -e .

# Install additional dependencies
RUN pip install torch transformers

# Copy evaluation scripts
COPY evaluation_examples/ /app/evaluation_examples/

ENTRYPOINT ["python", "/app/evaluation_examples/llmebench_example.py"]
EOF

# 3. Build and push image
$(aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com)
docker build -t bert-llmebench -f Dockerfile.llmebench .
docker tag bert-llmebench:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/bert-llmebench:latest
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/bert-llmebench:latest

# 4. Create Batch job definition
aws batch register-job-definition \\
    --job-definition-name bert-llmebench-job \\
    --type container \\
    --container-properties '{
        "image": "YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/bert-llmebench:latest",
        "vcpus": 4,
        "memory": 8192,
        "jobRoleArn": "arn:aws:iam::YOUR_ACCOUNT:role/BatchJobRole"
    }'

# 5. Submit benchmark job
aws batch submit-job \\
    --job-name bert-benchmark-$(date +%Y%m%d-%H%M%S) \\
    --job-queue default-queue \\
    --job-definition bert-llmebench-job

echo "✅ LLMeBench AWS Batch job submitted"
echo "📊 Monitor: aws batch describe-jobs --jobs JOB_ID"
'''
    
    with open("evaluation_examples/deploy_llmebench_aws.sh", "w") as f:
        f.write(aws_script)
    
    print("📁 AWS deployment script created: evaluation_examples/deploy_llmebench_aws.sh")

if __name__ == "__main__":
    # Run local example
    run_llmebench_example()
    
    # Create AWS deployment script
    create_aws_deployment_script()
    
    print(f"\n✅ LLMeBench example completed!")
    print("🌟 Next steps:")
    print("1. Install: bash evaluation_examples/install_llmebench.sh")
    print("2. Local: python evaluation_examples/llmebench_example.py") 
    print("3. AWS: bash evaluation_examples/deploy_llmebench_aws.sh")
    print("4. GitHub: https://github.com/qcri/LLMeBench")
