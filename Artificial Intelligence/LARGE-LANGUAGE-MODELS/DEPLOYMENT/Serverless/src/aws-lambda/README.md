# AWS Lambda LLM Inference

This example demonstrates how to deploy LLM inference orchestration using AWS Lambda.

## Important Notes

AWS Lambda has limitations that make it unsuitable for direct large model inference:
- Maximum execution time: 15 minutes
- Maximum memory: 10 GB
- Cold start latency
- No direct GPU support

**Best Use Cases**:
- Orchestration and routing requests to SageMaker/Bedrock
- Preprocessing and postprocessing
- Integration layer between services
- Small model inference with quantization

## Architecture

```
API Gateway → Lambda → Amazon Bedrock / SageMaker Endpoint
```

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured
- AWS SAM CLI installed
- Python 3.11+

## Setup

1. **Install AWS SAM CLI**:
   ```bash
   pip install aws-sam-cli
   ```

2. **Install dependencies locally** (for testing):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure AWS credentials**:
   ```bash
   aws configure
   ```

## Deployment

### Deploy with Amazon Bedrock

```bash
sam build
sam deploy --guided \
  --parameter-overrides UseBedrock=true
```

### Deploy with SageMaker Endpoint

First, create a SageMaker endpoint with your model, then:

```bash
sam build
sam deploy --guided \
  --parameter-overrides \
    UseBedrock=false \
    SageMakerEndpointName=your-endpoint-name
```

## Testing

### Test locally

```bash
# Start local API
sam local start-api

# Test in another terminal
curl -X POST http://localhost:3000/inference \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is the capital of France?",
    "max_tokens": 100,
    "temperature": 0.7
  }'
```

### Test deployed function

```bash
# Get API endpoint from SAM output
export API_ENDPOINT="your-api-gateway-url"

curl -X POST $API_ENDPOINT/inference \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing in simple terms",
    "max_tokens": 200,
    "temperature": 0.7
  }'
```

## Configuration

### Environment Variables

- `SAGEMAKER_ENDPOINT_NAME`: Name of your SageMaker endpoint
- `USE_BEDROCK`: Set to 'true' to use Amazon Bedrock

### IAM Permissions

The Lambda function requires:
- `sagemaker:InvokeEndpoint` - If using SageMaker
- `bedrock:InvokeModel` - If using Bedrock

## Monitoring

Monitor your Lambda function:

```bash
# View logs
sam logs -n LLMInferenceFunction --tail

# View metrics in CloudWatch
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=LLMInferenceFunction \
  --start-time 2024-03-01T00:00:00Z \
  --end-time 2024-03-24T23:59:59Z \
  --period 3600 \
  --statistics Sum
```

## Cost Optimization

- Use provisioned concurrency for consistent latency
- Optimize memory allocation
- Use Amazon Bedrock on-demand pricing
- Consider Reserved Capacity for SageMaker endpoints

## Clean Up

```bash
sam delete
```

## Alternative: Container-based Lambda

For larger models, use Lambda with container images:

```dockerfile
FROM public.ecr.aws/lambda/python:3.11

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy function code
COPY handler.py ${LAMBDA_TASK_ROOT}

CMD ["handler.lambda_handler"]
```

Deploy with up to 10GB memory and 10GB ephemeral storage.
