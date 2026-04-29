#!/usr/bin/env python3
"""
DeepEval Example for BERT Model Evaluation
Comprehensive LLM testing framework for question-answering systems
"""

import os
import json
import sys
from typing import List, Dict, Any
from dataclasses import dataclass

# Try to import DeepEval (install with: pip install deepeval)
try:
    from deepeval import evaluate
    from deepeval.metrics import (
        AnswerRelevancyMetric,
        FaithfulnessMetric, 
        ContextualPrecisionMetric,
        ContextualRecallMetric,
        HallucinationMetric,
        BiasMetric
    )
    from deepeval.test_case import LLMTestCase
    DEEPEVAL_AVAILABLE = True
    print("✅ DeepEval imported successfully")
except ImportError:
    DEEPEVAL_AVAILABLE = False
    print("❌ DeepEval not installed. Run: pip install deepeval")

@dataclass
class QATestCase:
    """Question-Answer test case structure"""
    question: str
    expected_answer: str
    actual_answer: str
    context: str = ""
    retrieval_context: List[str] = None

class BERTDeepEvalTester:
    """DeepEval integration for BERT Q&A evaluation"""
    
    def __init__(self, model_name: str = "BERT-QA"):
        self.model_name = model_name
        self.test_cases = []
        
        # Initialize metrics
        self.metrics = {
            'answer_relevancy': AnswerRelevancyMetric(threshold=0.7),
            'faithfulness': FaithfulnessMetric(threshold=0.7),
            'contextual_precision': ContextualPrecisionMetric(threshold=0.7),
            'contextual_recall': ContextualRecallMetric(threshold=0.7),
            'hallucination': HallucinationMetric(threshold=0.3),
            'bias': BiasMetric(threshold=0.3)
        }
    
    def add_test_case(self, qa_case: QATestCase):
        """Add a test case for evaluation"""
        test_case = LLMTestCase(
            input=qa_case.question,
            actual_output=qa_case.actual_answer,
            expected_output=qa_case.expected_answer,
            context=qa_case.retrieval_context or [qa_case.context]
        )
        self.test_cases.append(test_case)
    
    def create_sample_qa_data(self):
        """Create sample Q&A test data for BERT evaluation"""
        sample_cases = [
            QATestCase(
                question="What is BERT?",
                expected_answer="BERT is a bidirectional transformer model for natural language processing.",
                actual_answer="BERT (Bidirectional Encoder Representations from Transformers) is a language model developed by Google for NLP tasks.",
                context="BERT is a transformer-based machine learning technique for natural language processing pre-training developed by Google."
            ),
            QATestCase(
                question="How does attention mechanism work in transformers?",
                expected_answer="Attention mechanism allows the model to focus on different parts of the input sequence when processing each element.",
                actual_answer="The attention mechanism in transformers uses query, key, and value vectors to compute weighted representations of input sequences.",
                context="The attention mechanism is a key component of transformer models that enables them to process sequences effectively."
            ),
            QATestCase(
                question="What are the benefits of fine-tuning BERT?",
                expected_answer="Fine-tuning BERT adapts the pre-trained model to specific downstream tasks with better performance.",
                actual_answer="Fine-tuning BERT allows adaptation to specific tasks while leveraging pre-trained knowledge, improving performance on domain-specific data.",
                context="Fine-tuning is a transfer learning technique where a pre-trained model is adapted to new tasks."
            )
        ]
        
        for case in sample_cases:
            self.add_test_case(case)
        
        print(f"✅ Created {len(sample_cases)} sample test cases")
    
    def run_evaluation(self) -> Dict[str, Any]:
        """Run DeepEval evaluation on test cases"""
        if not DEEPEVAL_AVAILABLE:
            return {"error": "DeepEval not available"}
        
        if not self.test_cases:
            self.create_sample_qa_data()
        
        print(f"\n🧪 Running DeepEval evaluation on {len(self.test_cases)} test cases...")
        
        results = {}
        
        for metric_name, metric in self.metrics.items():
            print(f"\n📊 Evaluating {metric_name}...")
            
            try:
                # Run evaluation for each test case
                metric_results = []
                for i, test_case in enumerate(self.test_cases):
                    metric.measure(test_case)
                    metric_results.append({
                        'test_case': i,
                        'score': metric.score,
                        'success': metric.success,
                        'reason': metric.reason
                    })
                
                # Calculate aggregate results
                scores = [r['score'] for r in metric_results if r['score'] is not None]
                avg_score = sum(scores) / len(scores) if scores else 0
                success_rate = sum(r['success'] for r in metric_results) / len(metric_results)
                
                results[metric_name] = {
                    'average_score': avg_score,
                    'success_rate': success_rate,
                    'individual_results': metric_results
                }
                
                print(f"   Average Score: {avg_score:.3f}")
                print(f"   Success Rate: {success_rate:.1%}")
                
            except Exception as e:
                print(f"   ❌ Error evaluating {metric_name}: {e}")
                results[metric_name] = {'error': str(e)}
        
        return results
    
    def export_results(self, results: Dict[str, Any], filename: str = "deepeval_results.json"):
        """Export evaluation results to JSON file"""
        output_path = f"evaluation_examples/{filename}"
        
        export_data = {
            'model_name': self.model_name,
            'evaluation_framework': 'DeepEval',
            'timestamp': str(pd.Timestamp.now()),
            'test_cases_count': len(self.test_cases),
            'metrics_evaluated': list(self.metrics.keys()),
            'results': results
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"📁 Results exported to: {output_path}")
        return output_path

def run_deepeval_example():
    """Run complete DeepEval example"""
    print("🚀 DeepEval BERT Q&A Evaluation Example")
    print("="*50)
    
    if not DEEPEVAL_AVAILABLE:
        print("❌ DeepEval not installed.")
        print("📦 Install with: pip install deepeval")
        print("🔗 GitHub: https://github.com/confident-ai/deepeval")
        return
    
    # Initialize evaluator
    evaluator = BERTDeepEvalTester("BERT-QA-Demo")
    
    # Run evaluation
    results = evaluator.run_evaluation()
    
    # Display summary
    print(f"\n📈 EVALUATION SUMMARY")
    print("-" * 30)
    
    for metric_name, metric_results in results.items():
        if 'error' in metric_results:
            print(f"{metric_name}: ❌ Error - {metric_results['error']}")
        else:
            avg_score = metric_results['average_score']
            success_rate = metric_results['success_rate']
            print(f"{metric_name}: Score={avg_score:.3f}, Success={success_rate:.1%}")
    
    # Export results
    try:
        import pandas as pd
        evaluator.export_results(results)
    except ImportError:
        print("⚠️ pandas not available for export")
    
    print(f"\n🎯 DeepEval Recommendations:")
    print("- Use answer_relevancy for Q&A quality")
    print("- Use faithfulness for factual accuracy")
    print("- Use hallucination metric for reliability")
    print("- Monitor bias for fairness assessment")

# AWS Deployment Configuration
def create_aws_deployment_script():
    """Create AWS deployment script for DeepEval"""
    
    aws_script = '''#!/bin/bash
# AWS DeepEval Deployment Script
# Deploy BERT evaluation to Amazon EC2

# 1. Create EC2 instance
aws ec2 run-instances \\
    --image-id ami-0abcdef1234567890 \\
    --count 1 \\
    --instance-type t3.large \\
    --key-name your-key-pair \\
    --security-group-ids sg-12345678 \\
    --subnet-id subnet-12345678 \\
    --user-data file://deepeval-userdata.sh \\
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=BERT-DeepEval-Evaluator}]'

# 2. User data script (deepeval-userdata.sh)
cat > deepeval-userdata.sh << 'EOF'
#!/bin/bash
yum update -y
yum install -y python3 python3-pip git

# Install dependencies
pip3 install deepeval torch transformers

# Clone repository
git clone https://github.com/your-repo/bert-evaluation.git
cd bert-evaluation

# Run evaluation
python3 evaluation_examples/deepeval_example.py

# Upload results to S3
aws s3 cp deepeval_results.json s3://your-bucket/evaluation-results/
EOF

# 3. Create CloudFormation template for automated deployment
cat > deepeval-cloudformation.yaml << 'EOF'
AWSTemplateFormatVersion: '2010-09-09'
Description: 'BERT DeepEval Evaluation Infrastructure'

Resources:
  BERTEvaluationInstance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-0abcdef1234567890
      InstanceType: t3.large
      IamInstanceProfile: !Ref InstanceProfile
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          pip3 install deepeval torch transformers
          python3 /path/to/deepeval_example.py
          aws s3 cp results.json s3://your-results-bucket/
      Tags:
        - Key: Name
          Value: BERT-DeepEval-Evaluator

  InstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      Roles: [!Ref EC2Role]

  EC2Role:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: assume-role
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/AmazonS3FullAccess

  ResultsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: bert-deepeval-results
EOF

echo "📁 AWS deployment scripts created"
echo "🚀 Deploy with: aws cloudformation create-stack --stack-name bert-deepeval --template-body file://deepeval-cloudformation.yaml"
'''
    
    with open("evaluation_examples/deploy_deepeval_aws.sh", "w") as f:
        f.write(aws_script)
    
    print("📁 AWS deployment script created: evaluation_examples/deploy_deepeval_aws.sh")

if __name__ == "__main__":
    # Run local example
    run_deepeval_example()
    
    # Create AWS deployment script
    create_aws_deployment_script()
    
    print(f"\n✅ DeepEval example completed!")
    print("🌟 Next steps:")
    print("1. Local: python evaluation_examples/deepeval_example.py")
    print("2. AWS: bash evaluation_examples/deploy_deepeval_aws.sh")
    print("3. Documentation: https://deepeval.com/docs/metrics-llm-evals")
