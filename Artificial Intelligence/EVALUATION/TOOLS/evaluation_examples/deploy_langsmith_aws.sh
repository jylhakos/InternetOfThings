#!/bin/bash
# AWS LangSmith Integration Script
# Deploy BERT evaluation with LangSmith observability

# 1. Create Lambda function for LangSmith integration
aws lambda create-function \
    --function-name bert-langsmith-evaluator \
    --runtime python3.9 \
    --role arn:aws:iam::your-account:role/lambda-execution-role \
    --handler langsmith_lambda.lambda_handler \
    --zip-file fileb://langsmith-deployment-package.zip \
    --timeout 300 \
    --memory-size 1024 \
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
    "# Install dependencies\n",
    "!pip install langsmith torch transformers"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "import os\n",
    "from langsmith import Client\n",
    "from langsmith.evaluation import evaluate\n",
    "\n",
    "# Set API key\n",
    "os.environ['LANGCHAIN_API_KEY'] = 'your-key-here'\n",
    "\n",
    "# Run evaluation\n",
    "client = Client()\n",
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
