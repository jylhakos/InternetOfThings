#!/usr/bin/env python3
"""
Ragas Example for BERT Model Evaluation
RAG (Retrieval-Augmented Generation) application evaluation toolkit
"""

import os
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Ragas imports
try:
    from ragas import evaluate
    from ragas.metrics import (
        answer_relevancy,
        faithfulness,
        context_precision,
        context_recall,
        answer_correctness,
        answer_similarity
    )
    from datasets import Dataset
    RAGAS_AVAILABLE = True
    print("✅ Ragas imported successfully")
except ImportError:
    RAGAS_AVAILABLE = False
    print("❌ Ragas not installed. Run: pip install ragas")

# Additional imports for demo data
import pandas as pd

@dataclass
class RAGTestCase:
    """RAG evaluation test case"""
    question: str
    answer: str
    contexts: List[str]
    ground_truth: str
    metadata: Optional[Dict[str, Any]] = None

class BERTRagasEvaluator:
    """Ragas integration for BERT RAG evaluation"""
    
    def __init__(self, model_name: str = "bert-base-uncased"):
        self.model_name = model_name
        
        # Initialize Ragas metrics
        if RAGAS_AVAILABLE:
            self.metrics = [
                answer_relevancy,      # How relevant is the answer to the question
                faithfulness,          # How faithful is the answer to the context
                context_precision,     # Precision of retrieved context
                context_recall,        # Recall of retrieved context  
                answer_correctness,    # Overall correctness of answer
                answer_similarity      # Semantic similarity to ground truth
            ]
        else:
            self.metrics = []
        
        print(f"📊 Configured {len(self.metrics)} Ragas metrics")
    
    def create_sample_rag_data(self) -> List[RAGTestCase]:
        """Create sample RAG test data for BERT evaluation"""
        
        test_cases = [
            RAGTestCase(
                question="What is BERT and how does it differ from traditional language models?",
                answer="BERT (Bidirectional Encoder Representations from Transformers) is a pre-trained language model that reads text bidirectionally. Unlike traditional models that process text left-to-right, BERT considers context from both directions, enabling better understanding of word meanings.",
                contexts=[
                    "BERT is a transformer-based machine learning technique for NLP pre-training developed by Google.",
                    "Traditional language models process text in one direction (left-to-right), but BERT processes bidirectionally.",
                    "BERT uses the transformer encoder architecture and is pre-trained on large text corpora."
                ],
                ground_truth="BERT is a bidirectional transformer model that processes text in both directions, unlike traditional unidirectional language models.",
                metadata={"category": "definition", "difficulty": "medium"}
            ),
            RAGTestCase(
                question="How does the attention mechanism work in transformers?",
                answer="The attention mechanism in transformers allows the model to focus on different parts of the input sequence when processing each element. It uses query, key, and value vectors to compute attention weights, enabling the model to capture long-range dependencies and relationships between words.",
                contexts=[
                    "Attention mechanism computes weighted representations of input sequences.",
                    "Query, key, and value vectors are used in the attention computation.",
                    "Self-attention allows models to relate different positions of a sequence to compute representations.",
                    "Multi-head attention runs several attention mechanisms in parallel."
                ],
                ground_truth="Attention mechanism uses query-key-value computations to allow models to focus on relevant parts of input sequences.",
                metadata={"category": "technical", "difficulty": "hard"}
            ),
            RAGTestCase(
                question="What are the main advantages of fine-tuning BERT?",
                answer="Fine-tuning BERT provides several advantages: 1) Leverages pre-trained knowledge from large text corpora, 2) Requires less task-specific training data, 3) Achieves better performance on downstream tasks, 4) Faster convergence compared to training from scratch.",
                contexts=[
                    "Fine-tuning adapts pre-trained models to specific downstream tasks.",
                    "Transfer learning with BERT requires less training data than training from scratch.",
                    "Pre-trained BERT models have learned rich language representations.",
                    "Fine-tuning typically achieves better performance than task-specific models."
                ],
                ground_truth="Fine-tuning BERT leverages pre-trained knowledge, requires less data, and achieves better performance on specific tasks.",
                metadata={"category": "application", "difficulty": "easy"}
            ),
            RAGTestCase(
                question="How do you evaluate the quality of a RAG system?",
                answer="RAG systems can be evaluated using metrics like answer relevancy (how well the answer addresses the question), faithfulness (whether the answer is grounded in the retrieved context), context precision and recall (quality of retrieved documents), and overall answer correctness.",
                contexts=[
                    "RAG evaluation involves assessing both retrieval and generation components.",
                    "Answer relevancy measures how well the answer addresses the input question.",
                    "Faithfulness evaluates whether the answer is supported by the retrieved context.",
                    "Context precision and recall measure the quality of document retrieval."
                ],
                ground_truth="RAG evaluation uses metrics for answer quality, context relevance, faithfulness, and retrieval effectiveness.",
                metadata={"category": "evaluation", "difficulty": "medium"}
            )
        ]
        
        return test_cases
    
    def prepare_ragas_dataset(self, test_cases: List[RAGTestCase]) -> Dataset:
        """Prepare dataset in Ragas format"""
        
        data = {
            "question": [case.question for case in test_cases],
            "answer": [case.answer for case in test_cases], 
            "contexts": [case.contexts for case in test_cases],
            "ground_truth": [case.ground_truth for case in test_cases]
        }
        
        # Add metadata if available
        if test_cases[0].metadata:
            for key in test_cases[0].metadata.keys():
                data[key] = [case.metadata.get(key, "") for case in test_cases]
        
        dataset = Dataset.from_dict(data)
        print(f"✅ Created Ragas dataset with {len(test_cases)} examples")
        
        return dataset
    
    def run_ragas_evaluation(self, test_cases: List[RAGTestCase]) -> Dict[str, Any]:
        """Run Ragas evaluation on test cases"""
        
        if not RAGAS_AVAILABLE:
            return self.create_demo_results()
        
        print("🔍 Running Ragas RAG Evaluation...")
        
        # Prepare dataset
        dataset = self.prepare_ragas_dataset(test_cases)
        
        try:
            # Run evaluation with all metrics
            print("📊 Computing Ragas metrics...")
            results = evaluate(dataset, metrics=self.metrics)
            
            return self.process_ragas_results(results, test_cases)
        
        except Exception as e:
            print(f"❌ Ragas evaluation failed: {e}")
            return self.create_demo_results()
    
    def process_ragas_results(self, results, test_cases: List[RAGTestCase]) -> Dict[str, Any]:
        """Process Ragas evaluation results"""
        
        processed = {
            "framework": "Ragas",
            "model": self.model_name,
            "timestamp": datetime.now().isoformat(),
            "metrics": {},
            "individual_scores": {},
            "summary": {}
        }
        
        # Extract metric scores
        if hasattr(results, 'scores'):
            for metric_name, scores in results.scores.items():
                processed["metrics"][metric_name] = {
                    "mean": float(scores.mean()) if hasattr(scores, 'mean') else float(scores),
                    "std": float(scores.std()) if hasattr(scores, 'std') else 0,
                    "min": float(scores.min()) if hasattr(scores, 'min') else float(scores),
                    "max": float(scores.max()) if hasattr(scores, 'max') else float(scores)
                }
        
        # Individual test case results
        for i, test_case in enumerate(test_cases):
            case_results = {}
            if hasattr(results, 'scores'):
                for metric_name, scores in results.scores.items():
                    if hasattr(scores, '__getitem__'):
                        case_results[metric_name] = float(scores[i])
                    else:
                        case_results[metric_name] = float(scores)
            
            processed["individual_scores"][f"case_{i}"] = {
                "question": test_case.question[:100] + "...",
                "metadata": test_case.metadata,
                "scores": case_results
            }
        
        # Overall summary
        if processed["metrics"]:
            all_mean_scores = [m["mean"] for m in processed["metrics"].values()]
            processed["summary"] = {
                "total_cases": len(test_cases),
                "metrics_count": len(processed["metrics"]),
                "overall_score": sum(all_mean_scores) / len(all_mean_scores),
                "best_metric": max(processed["metrics"].keys(), 
                                  key=lambda k: processed["metrics"][k]["mean"]),
                "worst_metric": min(processed["metrics"].keys(),
                                   key=lambda k: processed["metrics"][k]["mean"])
            }
        
        return processed
    
    def create_demo_results(self) -> Dict[str, Any]:
        """Create demo results when Ragas is not available"""
        
        print("🎬 Running in DEMO mode (simulated Ragas results)...")
        
        demo_results = {
            "framework": "Ragas (Demo)",
            "model": self.model_name,
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "answer_relevancy": {
                    "mean": 0.85,
                    "std": 0.08,
                    "min": 0.76,
                    "max": 0.92
                },
                "faithfulness": {
                    "mean": 0.82,
                    "std": 0.12,
                    "min": 0.68,
                    "max": 0.94
                },
                "context_precision": {
                    "mean": 0.78,
                    "std": 0.15,
                    "min": 0.58,
                    "max": 0.89
                },
                "context_recall": {
                    "mean": 0.74,
                    "std": 0.18,
                    "min": 0.52,
                    "max": 0.88
                },
                "answer_correctness": {
                    "mean": 0.80,
                    "std": 0.10,
                    "min": 0.67,
                    "max": 0.91
                },
                "answer_similarity": {
                    "mean": 0.83,
                    "std": 0.07,
                    "min": 0.75,
                    "max": 0.90
                }
            },
            "summary": {
                "total_cases": 4,
                "metrics_count": 6,
                "overall_score": 0.80,
                "best_metric": "answer_relevancy",
                "worst_metric": "context_recall"
            },
            "note": "Demo results - actual evaluation requires Ragas installation"
        }
        
        return demo_results
    
    def run_comprehensive_evaluation(self) -> Dict[str, Any]:
        """Run comprehensive Ragas evaluation"""
        
        print("🔍 Running Comprehensive Ragas RAG Evaluation")
        print("="*50)
        
        # Create test data
        test_cases = self.create_sample_rag_data()
        print(f"📋 Created {len(test_cases)} RAG test cases")
        
        # Run evaluation
        results = self.run_ragas_evaluation(test_cases)
        
        return results
    
    def export_results(self, results: Dict[str, Any], filename: str = "ragas_results.json"):
        """Export Ragas evaluation results"""
        
        output_path = f"evaluation_examples/{filename}"
        
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"📁 Results exported to: {output_path}")
        return output_path
    
    def generate_evaluation_report(self, results: Dict[str, Any]) -> str:
        """Generate human-readable evaluation report"""
        
        report = []
        report.append("📊 RAGAS RAG EVALUATION REPORT")
        report.append("=" * 50)
        report.append(f"Model: {results.get('model', 'N/A')}")
        report.append(f"Framework: {results.get('framework', 'N/A')}")
        report.append(f"Timestamp: {results.get('timestamp', 'N/A')}")
        
        # Metrics summary
        report.append("\n📈 METRICS SUMMARY")
        report.append("-" * 30)
        
        metrics = results.get("metrics", {})
        for metric_name, metric_data in metrics.items():
            mean_score = metric_data.get("mean", 0)
            std_score = metric_data.get("std", 0)
            report.append(f"{metric_name}: {mean_score:.3f} ± {std_score:.3f}")
        
        # Overall summary
        summary = results.get("summary", {})
        if summary:
            report.append(f"\n🎯 OVERALL ASSESSMENT")
            report.append("-" * 25)
            report.append(f"Overall Score: {summary.get('overall_score', 0):.3f}")
            report.append(f"Best Metric: {summary.get('best_metric', 'N/A')}")
            report.append(f"Areas for Improvement: {summary.get('worst_metric', 'N/A')}")
        
        # Recommendations
        report.append(f"\n💡 RECOMMENDATIONS")
        report.append("-" * 20)
        
        overall_score = summary.get('overall_score', 0)
        if overall_score >= 0.85:
            report.append("✅ Excellent RAG performance across all metrics")
        elif overall_score >= 0.75:
            report.append("✅ Good RAG performance with room for improvement")
        else:
            report.append("⚠️ RAG system needs significant improvements")
        
        report.append("- Focus on context retrieval quality")
        report.append("- Improve answer faithfulness to retrieved context")
        report.append("- Enhance answer relevancy to user questions")
        
        report_text = "\n".join(report)
        
        # Save report
        report_path = "evaluation_examples/ragas_evaluation_report.txt"
        with open(report_path, "w") as f:
            f.write(report_text)
        
        print(f"📄 Report saved to: {report_path}")
        
        return report_text

def run_ragas_example():
    """Run complete Ragas example"""
    print("🔍 Ragas BERT RAG Evaluation Example")
    print("="*50)
    
    if not RAGAS_AVAILABLE:
        print("❌ Ragas package not installed")
        print("📦 Install with: pip install ragas")
    
    # Initialize evaluator
    evaluator = BERTRagasEvaluator("bert-base-uncased")
    
    # Run comprehensive evaluation
    results = evaluator.run_comprehensive_evaluation()
    
    # Display results
    print(f"\n📈 RAGAS EVALUATION RESULTS")
    print("-" * 40)
    
    metrics = results.get("metrics", {})
    for metric_name, metric_data in metrics.items():
        if isinstance(metric_data, dict) and "mean" in metric_data:
            mean_score = metric_data["mean"]
            std_score = metric_data["std"]
            print(f"{metric_name}: {mean_score:.3f} ± {std_score:.3f}")
    
    # Summary
    summary = results.get("summary", {})
    if summary:
        print(f"\n🎯 Summary:")
        print(f"Overall Score: {summary.get('overall_score', 0):.3f}")
        print(f"Best Metric: {summary.get('best_metric', 'N/A')}")
        print(f"Needs Improvement: {summary.get('worst_metric', 'N/A')}")
    
    # Export results
    evaluator.export_results(results)
    
    # Generate report
    report = evaluator.generate_evaluation_report(results)
    print(f"\n{report}")
    
    print(f"\n🎯 Ragas Recommendations:")
    print("- Specialized for RAG system evaluation")
    print("- Comprehensive metrics for retrieval and generation")
    print("- Easy integration with existing RAG pipelines")
    print("- Supports both synthetic and human-annotated datasets")

def create_aws_deployment_script():
    """Create AWS deployment script for Ragas"""
    
    aws_script = '''#!/bin/bash
# AWS Ragas RAG Evaluation Deployment Script
# Deploy BERT RAG evaluation using Ragas on AWS

# 1. Create SageMaker training job for Ragas evaluation
aws sagemaker create-training-job \\
    --training-job-name bert-ragas-evaluation-$(date +%Y%m%d-%H%M%S) \\
    --algorithm-specification TrainingImage=763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-training:1.13.1-cpu-py39-ubuntu20.04-sagemaker,TrainingInputMode=File \\
    --role-arn arn:aws:iam::your-account:role/SageMakerExecutionRole \\
    --input-data-config ChannelName=training,DataSource='{S3DataSource={S3DataType=S3Prefix,S3Uri=s3://your-bucket/ragas-data/,S3DataDistributionType=FullyReplicated}}',ContentType=application/json,CompressionType=None,RecordWrapperType=None \\
    --output-data-config S3OutputPath=s3://your-bucket/ragas-results/ \\
    --resource-config InstanceType=ml.m5.xlarge,InstanceCount=1,VolumeSizeInGB=30 \\
    --stopping-condition MaxRuntimeInSeconds=3600

# 2. Create Lambda function for Ragas evaluation
cat > ragas_lambda.py << 'EOF'
import json
import boto3
from ragas import evaluate
from ragas.metrics import answer_relevancy, faithfulness
from datasets import Dataset

def lambda_handler(event, context):
    """AWS Lambda handler for Ragas evaluation"""
    
    # Load test data from event or S3
    test_data = event.get('test_data', [])
    
    if not test_data:
        # Load from S3
        s3 = boto3.client('s3')
        bucket = event.get('s3_bucket', 'your-bucket')
        key = event.get('s3_key', 'ragas-test-data.json')
        
        response = s3.get_object(Bucket=bucket, Key=key)
        test_data = json.loads(response['Body'].read())
    
    # Prepare dataset
    dataset = Dataset.from_dict(test_data)
    
    # Run Ragas evaluation
    results = evaluate(
        dataset,
        metrics=[answer_relevancy, faithfulness]
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'evaluation_results': results.to_dict(),
            'metrics_count': len(results.scores),
            'status': 'completed'
        })
    }
EOF

# 3. Create containerized Ragas evaluation
cat > Dockerfile.ragas << 'EOF'
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
RUN pip install ragas datasets pandas

# Copy evaluation scripts
COPY evaluation_examples/ /app/evaluation_examples/

# Set entrypoint
ENTRYPOINT ["python", "/app/evaluation_examples/ragas_example.py"]
EOF

# 4. Build and push to ECR
aws ecr create-repository --repository-name bert-ragas-evaluator
$(aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com)
docker build -t bert-ragas-evaluator -f Dockerfile.ragas .
docker tag bert-ragas-evaluator:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/bert-ragas-evaluator:latest
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/bert-ragas-evaluator:latest

# 5. Create ECS task definition for batch processing
aws ecs register-task-definition \\
    --family bert-ragas-evaluation \\
    --network-mode awsvpc \\
    --requires-compatibilities FARGATE \\
    --cpu 1024 \\
    --memory 2048 \\
    --execution-role-arn arn:aws:iam::YOUR_ACCOUNT:role/ecsTaskExecutionRole \\
    --container-definitions '[{
        "name": "ragas-evaluator",
        "image": "YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/bert-ragas-evaluator:latest",
        "essential": true,
        "logConfiguration": {
            "logDriver": "awslogs",
            "options": {
                "awslogs-group": "/ecs/bert-ragas-evaluation",
                "awslogs-region": "us-east-1",
                "awslogs-stream-prefix": "ecs"
            }
        }
    }]'

echo "✅ Ragas AWS deployment setup completed"
echo "🏃 Run evaluation: aws ecs run-task --cluster your-cluster --task-definition bert-ragas-evaluation"
'''
    
    with open("evaluation_examples/deploy_ragas_aws.sh", "w") as f:
        f.write(aws_script)
    
    print("📁 AWS deployment script created: evaluation_examples/deploy_ragas_aws.sh")

if __name__ == "__main__":
    # Run local example
    run_ragas_example()
    
    # Create AWS deployment script
    create_aws_deployment_script()
    
    print(f"\n✅ Ragas example completed!")
    print("🌟 Next steps:")
    print("1. Install: pip install ragas datasets")
    print("2. Local: python evaluation_examples/ragas_example.py")
    print("3. AWS: bash evaluation_examples/deploy_ragas_aws.sh")
    print("4. Documentation: https://docs.ragas.io/en/stable/")
