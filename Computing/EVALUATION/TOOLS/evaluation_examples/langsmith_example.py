#!/usr/bin/env python3
"""
LangSmith Example for BERT Model Evaluation
Production LLM observability and evaluation platform
"""

import os
import json
import time
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

# LangSmith SDK
try:
    from langsmith import Client
    from langsmith.evaluation import evaluate, LangSmithEvaluator
    from langsmith.schemas import Run, Example
    LANGSMITH_AVAILABLE = True
    print("✅ LangSmith SDK imported successfully")
except ImportError:
    LANGSMITH_AVAILABLE = False
    print("❌ LangSmith not installed. Run: pip install langsmith")

@dataclass
class EvaluationExample:
    """Example for LangSmith evaluation"""
    inputs: Dict[str, str]
    expected_outputs: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None

class BERTLangSmithEvaluator:
    """LangSmith integration for BERT Q&A evaluation"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('LANGCHAIN_API_KEY')
        if not self.api_key:
            print("⚠️ Warning: No LangSmith API key provided")
            print("Set LANGCHAIN_API_KEY environment variable")
        
        if LANGSMITH_AVAILABLE and self.api_key:
            self.client = Client(api_key=self.api_key)
        else:
            self.client = None
        
        self.project_name = "bert-qa-evaluation"
        self.dataset_name = "bert-qa-test-dataset"
    
    def create_bert_qa_function(self):
        """Create BERT Q&A function for evaluation"""
        
        def bert_qa_pipeline(inputs: Dict[str, str]) -> Dict[str, str]:
            """
            BERT Question Answering Pipeline
            This would be replaced with your actual BERT model inference
            """
            question = inputs.get("question", "")
            context = inputs.get("context", "")
            
            # Simulate BERT inference (replace with actual model)
            import hashlib
            seed = int(hashlib.md5(question.encode()).hexdigest()[:8], 16)
            
            # Simulated BERT responses based on question patterns
            if "what is" in question.lower():
                if "bert" in question.lower():
                    answer = "BERT is a bidirectional transformer model for natural language processing tasks."
                else:
                    answer = "This is a fundamental concept in machine learning and AI."
            elif "how" in question.lower():
                if "attention" in question.lower():
                    answer = "Attention mechanism allows models to focus on relevant parts of input sequences."
                else:
                    answer = "This process involves multiple steps and computational techniques."
            else:
                answer = "The answer depends on the specific context and requirements of the question."
            
            # Add some variance based on question content
            confidence = 0.85 + (seed % 100) / 1000
            
            return {
                "answer": answer,
                "confidence": round(confidence, 3),
                "model": "bert-base-uncased",
                "processing_time_ms": 45 + (seed % 50)
            }
        
        return bert_qa_pipeline
    
    def create_evaluation_dataset(self) -> List[EvaluationExample]:
        """Create dataset for BERT Q&A evaluation"""
        
        examples = [
            EvaluationExample(
                inputs={
                    "question": "What is BERT and how does it work?",
                    "context": "BERT is a transformer-based language model developed by Google."
                },
                expected_outputs={
                    "answer": "BERT is a bidirectional transformer model for NLP tasks.",
                    "expected_confidence": 0.9
                },
                metadata={"category": "definition", "difficulty": "easy"}
            ),
            EvaluationExample(
                inputs={
                    "question": "How does the attention mechanism work in transformers?",
                    "context": "Attention mechanism is core to transformer architecture."
                },
                expected_outputs={
                    "answer": "Attention allows models to focus on relevant input parts.",
                    "expected_confidence": 0.85
                },
                metadata={"category": "technical", "difficulty": "medium"}
            ),
            EvaluationExample(
                inputs={
                    "question": "What are the advantages of fine-tuning BERT?",
                    "context": "Fine-tuning adapts pre-trained models to specific tasks."
                },
                expected_outputs={
                    "answer": "Fine-tuning leverages pre-trained knowledge for specific tasks.",
                    "expected_confidence": 0.88
                },
                metadata={"category": "application", "difficulty": "medium"}
            ),
            EvaluationExample(
                inputs={
                    "question": "How is BERT different from GPT models?",
                    "context": "BERT and GPT are both transformer-based but have different architectures."
                },
                expected_outputs={
                    "answer": "BERT is bidirectional while GPT is autoregressive.",
                    "expected_confidence": 0.82
                },
                metadata={"category": "comparison", "difficulty": "hard"}
            )
        ]
        
        return examples
    
    def create_custom_evaluators(self) -> List[Callable]:
        """Create custom evaluators for BERT Q&A"""
        
        def answer_relevance_evaluator(run: Run, example: Example) -> Dict[str, Any]:
            """Evaluate answer relevance to question"""
            
            question = example.inputs.get("question", "")
            answer = run.outputs.get("answer", "") if run.outputs else ""
            
            # Simple keyword-based relevance (replace with semantic similarity)
            question_words = set(question.lower().split())
            answer_words = set(answer.lower().split())
            
            overlap = len(question_words.intersection(answer_words))
            relevance_score = overlap / max(len(question_words), 1)
            
            return {
                "key": "answer_relevance",
                "score": min(relevance_score * 2, 1.0),  # Scale to 0-1
                "reason": f"Keyword overlap: {overlap}/{len(question_words)} words"
            }
        
        def confidence_calibration_evaluator(run: Run, example: Example) -> Dict[str, Any]:
            """Evaluate confidence calibration"""
            
            predicted_confidence = run.outputs.get("confidence", 0) if run.outputs else 0
            expected_confidence = example.expected_outputs.get("expected_confidence", 0.5) if example.expected_outputs else 0.5
            
            calibration_error = abs(predicted_confidence - expected_confidence)
            calibration_score = max(0, 1 - calibration_error)
            
            return {
                "key": "confidence_calibration", 
                "score": calibration_score,
                "reason": f"Confidence error: {calibration_error:.3f}"
            }
        
        def response_completeness_evaluator(run: Run, example: Example) -> Dict[str, Any]:
            """Evaluate response completeness"""
            
            answer = run.outputs.get("answer", "") if run.outputs else ""
            expected = example.expected_outputs.get("answer", "") if example.expected_outputs else ""
            
            # Simple length-based completeness metric
            length_ratio = len(answer) / max(len(expected), 1)
            completeness_score = min(length_ratio, 1.0) if length_ratio <= 1.5 else max(0, 2 - length_ratio)
            
            return {
                "key": "response_completeness",
                "score": completeness_score,
                "reason": f"Length ratio: {length_ratio:.2f}"
            }
        
        return [
            answer_relevance_evaluator,
            confidence_calibration_evaluator,
            response_completeness_evaluator
        ]
    
    def upload_dataset_to_langsmith(self, examples: List[EvaluationExample]) -> str:
        """Upload dataset to LangSmith"""
        
        if not self.client:
            print("❌ LangSmith client not available")
            return None
        
        try:
            # Create dataset
            dataset = self.client.create_dataset(
                dataset_name=self.dataset_name,
                description="BERT Q&A evaluation dataset"
            )
            
            # Upload examples
            self.client.create_examples(
                inputs=[ex.inputs for ex in examples],
                outputs=[ex.expected_outputs for ex in examples],
                metadata=[ex.metadata for ex in examples],
                dataset_id=dataset.id
            )
            
            print(f"✅ Dataset uploaded with {len(examples)} examples")
            return dataset.id
        
        except Exception as e:
            print(f"❌ Failed to upload dataset: {e}")
            return None
    
    def run_langsmith_evaluation(self) -> Dict[str, Any]:
        """Run evaluation using LangSmith"""
        
        if not LANGSMITH_AVAILABLE:
            return self.create_demo_results()
        
        if not self.client:
            print("❌ LangSmith client not configured")
            return self.create_demo_results()
        
        print("🔍 Running LangSmith Evaluation...")
        
        # Create BERT Q&A function
        bert_qa_function = self.create_bert_qa_function()
        
        # Create dataset
        examples = self.create_evaluation_dataset()
        dataset_id = self.upload_dataset_to_langsmith(examples)
        
        if not dataset_id:
            return self.create_demo_results()
        
        # Create evaluators
        evaluators = self.create_custom_evaluators()
        
        try:
            # Run evaluation
            results = evaluate(
                bert_qa_function,
                data=self.dataset_name,
                evaluators=evaluators,
                project_name=self.project_name,
                metadata={"model": "bert-base-uncased", "version": "1.0"}
            )
            
            return self.process_langsmith_results(results)
        
        except Exception as e:
            print(f"❌ Evaluation failed: {e}")
            return self.create_demo_results()
    
    def process_langsmith_results(self, results) -> Dict[str, Any]:
        """Process LangSmith evaluation results"""
        
        processed = {
            "framework": "LangSmith",
            "project": self.project_name,
            "dataset": self.dataset_name,
            "timestamp": datetime.now().isoformat(),
            "metrics": {},
            "individual_results": []
        }
        
        # Extract metrics (this would depend on actual LangSmith results structure)
        if hasattr(results, 'aggregate_metrics'):
            processed["metrics"] = results.aggregate_metrics
        
        if hasattr(results, 'results'):
            processed["individual_results"] = results.results
        
        return processed
    
    def create_demo_results(self) -> Dict[str, Any]:
        """Create demo results when LangSmith is not available"""
        
        print("🎬 Running in DEMO mode (simulated LangSmith results)...")
        
        demo_results = {
            "framework": "LangSmith (Demo)",
            "project": self.project_name,
            "dataset": self.dataset_name,
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "answer_relevance": {
                    "mean": 0.82,
                    "std": 0.12,
                    "min": 0.65,
                    "max": 0.95
                },
                "confidence_calibration": {
                    "mean": 0.78,
                    "std": 0.15,
                    "min": 0.58,
                    "max": 0.92
                },
                "response_completeness": {
                    "mean": 0.85,
                    "std": 0.08,
                    "min": 0.72,
                    "max": 0.94
                }
            },
            "evaluation_summary": {
                "total_examples": 4,
                "successful_runs": 4,
                "average_processing_time_ms": 47.5,
                "overall_score": 0.82
            },
            "note": "Demo results - actual evaluation requires LangSmith API key"
        }
        
        return demo_results
    
    def export_results(self, results: Dict[str, Any], filename: str = "langsmith_results.json"):
        """Export evaluation results"""
        
        output_path = f"evaluation_examples/{filename}"
        
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"📁 Results exported to: {output_path}")
        return output_path

def run_langsmith_example():
    """Run complete LangSmith example"""
    print("🔍 LangSmith BERT Q&A Evaluation Example")
    print("="*50)
    
    # Check API key
    api_key = os.getenv('LANGCHAIN_API_KEY')
    if not api_key:
        print("❌ LangSmith API key not found")
        print("📝 Set environment variable: export LANGCHAIN_API_KEY='your-key-here'")
        print("🔑 Get API key from: https://www.langchain.com/langsmith")
    
    if not LANGSMITH_AVAILABLE:
        print("❌ LangSmith package not installed")
        print("📦 Install with: pip install langsmith")
    
    # Initialize evaluator
    evaluator = BERTLangSmithEvaluator(api_key)
    
    # Run evaluation
    results = evaluator.run_langsmith_evaluation()
    
    # Display results
    print(f"\n📈 LANGSMITH EVALUATION RESULTS")
    print("-" * 40)
    
    metrics = results.get("metrics", {})
    for metric_name, metric_data in metrics.items():
        if isinstance(metric_data, dict) and "mean" in metric_data:
            mean_score = metric_data["mean"]
            std_score = metric_data["std"]
            print(f"{metric_name}: {mean_score:.3f} ± {std_score:.3f}")
        else:
            print(f"{metric_name}: {metric_data}")
    
    # Summary statistics
    summary = results.get("evaluation_summary", {})
    if summary:
        print(f"\n📊 Evaluation Summary:")
        print(f"Total Examples: {summary.get('total_examples', 'N/A')}")
        print(f"Successful Runs: {summary.get('successful_runs', 'N/A')}")
        print(f"Average Processing Time: {summary.get('average_processing_time_ms', 'N/A')} ms")
        print(f"Overall Score: {summary.get('overall_score', 'N/A'):.3f}")
    
    # Export results
    evaluator.export_results(results)
    
    print(f"\n🎯 LangSmith Recommendations:")
    print("- Real-time monitoring and debugging")
    print("- Custom evaluator configuration")
    print("- Dataset management and versioning")
    print("- Production observability platform")

def create_aws_deployment_script():
    """Create AWS deployment script for LangSmith"""
    
    aws_script = '''#!/bin/bash
# AWS LangSmith Integration Script
# Deploy BERT evaluation with LangSmith observability

# 1. Create Lambda function for LangSmith integration
aws lambda create-function \\
    --function-name bert-langsmith-evaluator \\
    --runtime python3.9 \\
    --role arn:aws:iam::your-account:role/lambda-execution-role \\
    --handler langsmith_lambda.lambda_handler \\
    --zip-file fileb://langsmith-deployment-package.zip \\
    --timeout 300 \\
    --memory-size 1024 \\
    --environment Variables='{LANGCHAIN_API_KEY=your-langsmith-key}'

# 2. Create Lambda handler
cat > langsmith_lambda.py << 'EOF'
import json
import os
from langsmith import Client
from langsmith.evaluation import evaluate

def lambda_handler(event, context):
    """AWS Lambda handler for LangSmith evaluation"""
    
    client = Client(api_key=os.environ['LANGCHAIN_API_KEY'])
    
    # BERT Q&A function
    def bert_qa(inputs):
        question = inputs.get('question', '')
        # Your BERT inference logic here
        return {'answer': f'Answer to: {question}', 'confidence': 0.85}
    
    # Run evaluation
    results = evaluate(
        bert_qa,
        data=event.get('dataset_name', 'bert-qa-test'),
        evaluators=event.get('evaluators', []),
        project_name=event.get('project_name', 'bert-aws-evaluation')
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'evaluation_results': str(results),
            'project_name': event.get('project_name'),
            'status': 'completed'
        })
    }
EOF

# 3. Create SageMaker notebook for LangSmith integration
cat > langsmith-sagemaker-notebook.ipynb << 'EOF'
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# BERT Evaluation with LangSmith on AWS SageMaker"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# Install dependencies\\n",
    "!pip install langsmith torch transformers"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "import os\\n",
    "from langsmith import Client\\n",
    "from langsmith.evaluation import evaluate\\n",
    "\\n",
    "# Set API key\\n",
    "os.environ['LANGCHAIN_API_KEY'] = 'your-key-here'\\n",
    "\\n",
    "# Run evaluation\\n",
    "client = Client()\\n",
    "# Your evaluation code here"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
EOF

# 4. Package and deploy
pip install langsmith -t .
zip -r langsmith-deployment-package.zip .

echo "✅ LangSmith AWS deployment setup completed"
echo "🌐 Test Lambda: aws lambda invoke --function-name bert-langsmith-evaluator"
'''
    
    with open("evaluation_examples/deploy_langsmith_aws.sh", "w") as f:
        f.write(aws_script)
    
    print("📁 AWS deployment script created: evaluation_examples/deploy_langsmith_aws.sh")

if __name__ == "__main__":
    # Run local example
    run_langsmith_example()
    
    # Create AWS deployment script
    create_aws_deployment_script()
    
    print(f"\n✅ LangSmith example completed!")
    print("🌟 Next steps:")
    print("1. Get LangSmith API key: https://www.langchain.com/langsmith")
    print("2. Local: export LANGCHAIN_API_KEY='key' && python evaluation_examples/langsmith_example.py")
    print("3. AWS: bash evaluation_examples/deploy_langsmith_aws.sh")
    print("4. Documentation: https://docs.smith.langchain.com/evaluation")
