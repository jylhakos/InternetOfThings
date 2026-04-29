#!/bin/bash
# AWS G-Eval Deployment Script
# Deploy BERT evaluation with GPT-4 as judge to AWS

# 1. Create Lambda function for G-Eval
aws lambda create-function \
    --function-name bert-geval-evaluator \
    --runtime python3.9 \
    --role arn:aws:iam::your-account:role/lambda-execution-role \
    --handler geval_lambda.lambda_handler \
    --zip-file fileb://geval-deployment-package.zip \
    --timeout 300 \
    --memory-size 1024 \
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
