#!/usr/bin/env python3
"""
G-Eval Example for BERT Model Evaluation
LLM-as-a-Judge framework using GPT-4 for human-like evaluation
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# OpenAI client for G-Eval
try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
    print("✅ OpenAI client imported successfully")
except ImportError:
    OPENAI_AVAILABLE = False
    print("❌ OpenAI not installed. Run: pip install openai")

@dataclass
class GEvalCriteria:
    """G-Eval evaluation criteria"""
    name: str
    description: str
    evaluation_steps: List[str]
    score_range: tuple = (1, 5)

class BERTGEvalTester:
    """G-Eval integration for BERT Q&A evaluation"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            print("⚠️ Warning: No OpenAI API key provided")
            print("Set OPENAI_API_KEY environment variable")
        
        if OPENAI_AVAILABLE and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None
        
        # Define G-Eval criteria
        self.criteria = {
            'relevance': GEvalCriteria(
                name="Answer Relevance",
                description="How well does the answer address the question?",
                evaluation_steps=[
                    "Read the question carefully",
                    "Examine the provided answer",
                    "Assess how directly the answer addresses the question",
                    "Consider completeness and specificity",
                    "Rate from 1 (completely irrelevant) to 5 (highly relevant)"
                ]
            ),
            'accuracy': GEvalCriteria(
                name="Factual Accuracy", 
                description="How factually correct is the answer?",
                evaluation_steps=[
                    "Verify key facts in the answer",
                    "Check for any factual errors or misconceptions",
                    "Assess the technical correctness",
                    "Consider the reliability of information",
                    "Rate from 1 (many errors) to 5 (completely accurate)"
                ]
            ),
            'clarity': GEvalCriteria(
                name="Response Clarity",
                description="How clear and understandable is the answer?",
                evaluation_steps=[
                    "Evaluate language clarity and simplicity",
                    "Check for logical flow and structure",
                    "Assess readability and comprehension",
                    "Consider use of technical terms",
                    "Rate from 1 (very unclear) to 5 (crystal clear)"
                ]
            ),
            'completeness': GEvalCriteria(
                name="Answer Completeness",
                description="How complete and comprehensive is the answer?",
                evaluation_steps=[
                    "Identify key aspects the question asks about",
                    "Check if all important points are covered",
                    "Assess depth of explanation",
                    "Consider if examples or context are needed",
                    "Rate from 1 (incomplete) to 5 (comprehensive)"
                ]
            )
        }
    
    def create_evaluation_prompt(self, question: str, answer: str, criteria: GEvalCriteria) -> str:
        """Create G-Eval prompt for GPT-4 evaluation"""
        
        steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(criteria.evaluation_steps)])
        
        prompt = f"""
You are an expert evaluator for question-answering systems. Your task is to evaluate the quality of an answer using chain-of-thought reasoning.

**Evaluation Criteria: {criteria.name}**
{criteria.description}

**Evaluation Steps:**
{steps_text}

**Question:** {question}

**Answer to Evaluate:** {answer}

**Instructions:**
1. Follow each evaluation step systematically
2. Provide your reasoning for each step
3. Give a final numerical score from {criteria.score_range[0]} to {criteria.score_range[1]}
4. Explain your final decision

**Response Format:**
```
Step-by-step Analysis:
[Your detailed analysis following each step]

Final Score: [X]/5
Reasoning: [Brief explanation of your final score]
```
"""
        return prompt
    
    def evaluate_with_gpt4(self, question: str, answer: str, criteria: GEvalCriteria) -> Dict[str, Any]:
        """Evaluate using GPT-4 as judge"""
        
        if not self.client:
            return {
                'error': 'OpenAI client not available',
                'score': None,
                'reasoning': 'API key or OpenAI package missing'
            }
        
        prompt = self.create_evaluation_prompt(question, answer, criteria)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert evaluator for AI systems. Provide thorough, unbiased evaluations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistent evaluation
                max_tokens=1000
            )
            
            evaluation_text = response.choices[0].message.content
            
            # Extract score from response
            score = self.extract_score_from_response(evaluation_text)
            
            return {
                'criteria': criteria.name,
                'score': score,
                'max_score': criteria.score_range[1],
                'evaluation_text': evaluation_text,
                'reasoning': self.extract_reasoning(evaluation_text)
            }
            
        except Exception as e:
            return {
                'error': f'GPT-4 evaluation failed: {str(e)}',
                'score': None,
                'reasoning': f'Error: {str(e)}'
            }
    
    def extract_score_from_response(self, response_text: str) -> Optional[int]:
        """Extract numerical score from GPT-4 response"""
        import re
        
        # Look for patterns like "Final Score: 4/5" or "Score: 4"
        patterns = [
            r'Final Score:\s*(\d+)(?:/\d+)?',
            r'Score:\s*(\d+)(?:/\d+)?',
            r'Rating:\s*(\d+)(?:/\d+)?',
            r'(\d+)(?:/5|\s*/\s*5)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    
    def extract_reasoning(self, response_text: str) -> str:
        """Extract reasoning from GPT-4 response"""
        lines = response_text.split('\n')
        reasoning_lines = []
        
        for line in lines:
            if 'reasoning:' in line.lower():
                reasoning_lines.append(line.split(':', 1)[-1].strip())
            elif 'final score:' in line.lower():
                break
        
        return ' '.join(reasoning_lines) if reasoning_lines else response_text[:200] + "..."
    
    def run_comprehensive_evaluation(self, qa_pairs: List[Dict[str, str]]) -> Dict[str, Any]:
        """Run G-Eval on multiple Q&A pairs"""
        
        print(f"🧠 Running G-Eval on {len(qa_pairs)} Q&A pairs...")
        print("📊 Using GPT-4 as judge with chain-of-thought reasoning")
        
        results = {
            'overall_results': {},
            'individual_evaluations': []
        }
        
        for criteria_name, criteria in self.criteria.items():
            print(f"\n📋 Evaluating {criteria.name}...")
            
            criteria_scores = []
            criteria_evaluations = []
            
            for i, qa_pair in enumerate(qa_pairs):
                print(f"   Processing Q&A pair {i+1}/{len(qa_pairs)}...")
                
                evaluation = self.evaluate_with_gpt4(
                    qa_pair['question'],
                    qa_pair['answer'], 
                    criteria
                )
                
                if evaluation['score'] is not None:
                    criteria_scores.append(evaluation['score'])
                
                criteria_evaluations.append({
                    'qa_index': i,
                    'question': qa_pair['question'][:100] + "...",
                    'evaluation': evaluation
                })
            
            # Calculate aggregate metrics
            if criteria_scores:
                avg_score = sum(criteria_scores) / len(criteria_scores)
                max_possible = criteria.score_range[1]
                normalized_score = avg_score / max_possible
                
                results['overall_results'][criteria_name] = {
                    'average_score': avg_score,
                    'max_possible': max_possible,
                    'normalized_score': normalized_score,
                    'total_evaluations': len(criteria_scores)
                }
                
                print(f"   Average Score: {avg_score:.2f}/{max_possible} ({normalized_score:.1%})")
            else:
                results['overall_results'][criteria_name] = {
                    'error': 'No successful evaluations'
                }
            
            results['individual_evaluations'].extend(criteria_evaluations)
        
        return results
    
    def create_sample_qa_data(self) -> List[Dict[str, str]]:
        """Create sample Q&A data for BERT evaluation"""
        return [
            {
                'question': "What is BERT and how does it work?",
                'answer': "BERT (Bidirectional Encoder Representations from Transformers) is a pre-trained language model developed by Google. It uses transformer architecture with bidirectional training to understand context from both left and right of each word, making it excellent for various NLP tasks like question answering and text classification."
            },
            {
                'question': "How is BERT different from traditional language models?",
                'answer': "Unlike traditional left-to-right language models, BERT reads text bidirectionally, considering context from both directions. This allows it to better understand word meanings based on complete sentence context."
            },
            {
                'question': "What are the main applications of BERT?",
                'answer': "BERT is widely used for text classification, question answering, named entity recognition, sentiment analysis, and language understanding tasks. It serves as a foundation for many modern NLP applications."
            }
        ]

def run_geval_example():
    """Run complete G-Eval example"""
    print("🧠 G-Eval BERT Q&A Evaluation Example")
    print("="*50)
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OpenAI API key not found")
        print("📝 Set environment variable: export OPENAI_API_KEY='your-key-here'")
        print("🔑 Get API key from: https://platform.openai.com/api-keys")
        
        # Create demo mode
        print("\n🎬 Running in DEMO mode (simulated results)...")
        create_demo_results()
        return
    
    if not OPENAI_AVAILABLE:
        print("❌ OpenAI package not installed")
        print("📦 Install with: pip install openai")
        return
    
    # Initialize evaluator
    evaluator = BERTGEvalTester(api_key)
    
    # Create sample data
    qa_data = evaluator.create_sample_qa_data()
    
    # Run evaluation
    results = evaluator.run_comprehensive_evaluation(qa_data)
    
    # Display results
    print(f"\n📈 G-EVAL RESULTS SUMMARY")
    print("-" * 40)
    
    for criteria_name, criteria_results in results['overall_results'].items():
        if 'error' in criteria_results:
            print(f"{criteria_name}: ❌ {criteria_results['error']}")
        else:
            avg_score = criteria_results['average_score']
            max_score = criteria_results['max_possible']
            percentage = criteria_results['normalized_score']
            print(f"{criteria_name}: {avg_score:.2f}/{max_score} ({percentage:.1%})")
    
    # Export results
    export_path = "evaluation_examples/geval_results.json"
    with open(export_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n📁 Results exported to: {export_path}")
    
    print(f"\n🎯 G-Eval Recommendations:")
    print("- Uses GPT-4 for human-like evaluation")
    print("- Provides detailed reasoning for each score")
    print("- Best for creative and nuanced content")
    print("- Requires OpenAI API key and credits")

def create_demo_results():
    """Create demo results when API key is not available"""
    demo_results = {
        'overall_results': {
            'relevance': {
                'average_score': 4.2,
                'max_possible': 5,
                'normalized_score': 0.84,
                'total_evaluations': 3
            },
            'accuracy': {
                'average_score': 4.5,
                'max_possible': 5,
                'normalized_score': 0.90,
                'total_evaluations': 3
            },
            'clarity': {
                'average_score': 4.0,
                'max_possible': 5,
                'normalized_score': 0.80,
                'total_evaluations': 3
            },
            'completeness': {
                'average_score': 3.8,
                'max_possible': 5,
                'normalized_score': 0.76,
                'total_evaluations': 3
            }
        },
        'note': 'Demo results - actual evaluation requires OpenAI API key'
    }
    
    print(f"\n📈 G-EVAL DEMO RESULTS")
    print("-" * 30)
    
    for criteria, results in demo_results['overall_results'].items():
        avg_score = results['average_score']
        percentage = results['normalized_score']
        print(f"{criteria}: {avg_score:.1f}/5 ({percentage:.1%})")
    
    # Export demo results
    export_path = "evaluation_examples/geval_demo_results.json"
    with open(export_path, 'w') as f:
        json.dump(demo_results, f, indent=2)
    print(f"\n📁 Demo results exported to: {export_path}")

def create_aws_deployment_script():
    """Create AWS deployment script for G-Eval"""
    
    aws_script = '''#!/bin/bash
# AWS G-Eval Deployment Script
# Deploy BERT evaluation with GPT-4 as judge to AWS

# 1. Create Lambda function for G-Eval
aws lambda create-function \\
    --function-name bert-geval-evaluator \\
    --runtime python3.9 \\
    --role arn:aws:iam::your-account:role/lambda-execution-role \\
    --handler geval_lambda.lambda_handler \\
    --zip-file fileb://geval-deployment-package.zip \\
    --timeout 300 \\
    --memory-size 1024 \\
    --environment Variables='{OPENAI_API_KEY=your-openai-key}'

# 2. Create deployment package
cat > geval_lambda.py << 'EOF'
import json
import os
from openai import OpenAI

def lambda_handler(event, context):
    """AWS Lambda handler for G-Eval"""
    
    client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
    
    question = event.get('question', '')
    answer = event.get('answer', '')
    
    # G-Eval prompt
    prompt = f"""
    Evaluate the following Q&A pair for relevance, accuracy, clarity, and completeness.
    
    Question: {question}
    Answer: {answer}
    
    Provide scores from 1-5 for each criterion with brief reasoning.
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'evaluation': response.choices[0].message.content,
            'question': question,
            'answer': answer
        })
    }
EOF

# 3. Package and deploy
pip install openai -t .
zip -r geval-deployment-package.zip .

# 4. Create API Gateway
aws apigateway create-rest-api --name bert-geval-api

# 5. Set up CloudWatch for monitoring
aws logs create-log-group --log-group-name /aws/lambda/bert-geval-evaluator

echo "✅ G-Eval AWS deployment completed"
echo "🌐 Test API: aws lambda invoke --function-name bert-geval-evaluator"
'''
    
    with open("evaluation_examples/deploy_geval_aws.sh", "w") as f:
        f.write(aws_script)
    
    print("📁 AWS deployment script created: evaluation_examples/deploy_geval_aws.sh")

if __name__ == "__main__":
    # Run local example
    run_geval_example()
    
    # Create AWS deployment script
    create_aws_deployment_script()
    
    print(f"\n✅ G-Eval example completed!")
    print("🌟 Next steps:")
    print("1. Get OpenAI API key: https://platform.openai.com/api-keys")
    print("2. Local: export OPENAI_API_KEY='key' && python evaluation_examples/geval_example.py")
    print("3. AWS: bash evaluation_examples/deploy_geval_aws.sh")
    print("4. GitHub: https://github.com/nlpyang/geval")
