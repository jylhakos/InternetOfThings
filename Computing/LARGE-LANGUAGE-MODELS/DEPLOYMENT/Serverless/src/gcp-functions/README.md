# Google Cloud Functions LLM Inference

This example demonstrates how to deploy LLM inference orchestration using Google Cloud Functions.

## Important Notes

Cloud Functions (Gen 2) has similar limitations:
- Maximum execution time: 60 minutes (Gen 2)
- Maximum memory: 32 GB (Gen 2)
- Cold start latency
- No direct GPU support

**Best Use Cases**:
- Orchestration and routing to Vertex AI
- Preprocessing and postprocessing
- Integration layer
- Lightweight model inference

## Architecture

```
HTTP(S) → Cloud Functions → Vertex AI (Gemini/PaLM) / Custom Endpoint
```

## Prerequisites

- Google Cloud Project with billing enabled
- gcloud CLI installed
- Python 3.11+
- Virtual environment activated

## Setup

1. **Install Google Cloud CLI**:
   ```bash
   # On Linux
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL
   
   # Initialize
   gcloud init
   ```

2. **Enable required APIs**:
   ```bash
   gcloud services enable cloudfunctions.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable artifactregistry.googleapis.com
   gcloud services enable aiplatform.googleapis.com
   ```

3. **Set up authentication**:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

4. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Local Testing

```bash
# Install Functions Framework
pip install functions-framework

# Set environment variables
export GCP_PROJECT="your-project-id"
export VERTEX_AI_LOCATION="us-central1"
export USE_VERTEX_AI="true"

# Run function locally
functions-framework --target=inference --debug

# Test in another terminal
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is artificial intelligence?",
    "max_tokens": 150,
    "temperature": 0.7,
    "model": "gemini-pro"
  }'
```

## Deployment

### Deploy Cloud Function (Gen 2)

```bash
# Set variables
PROJECT_ID="your-project-id"
REGION="us-central1"
FUNCTION_NAME="llm-inference"

# Deploy inference function
gcloud functions deploy $FUNCTION_NAME \
  --gen2 \
  --runtime=python311 \
  --region=$REGION \
  --source=. \
  --entry-point=inference \
  --trigger-http \
  --allow-unauthenticated \
  --memory=2Gi \
  --timeout=300s \
  --set-env-vars=GCP_PROJECT=$PROJECT_ID,VERTEX_AI_LOCATION=$REGION,USE_VERTEX_AI=true

# Deploy health check function
gcloud functions deploy ${FUNCTION_NAME}-health \
  --gen2 \
  --runtime=python311 \
  --region=$REGION \
  --source=. \
  --entry-point=health \
  --trigger-http \
  --allow-unauthenticated

# Deploy batch inference function
gcloud functions deploy ${FUNCTION_NAME}-batch \
  --gen2 \
  --runtime=python311 \
  --region=$REGION \
  --source=. \
  --entry-point=batch_inference \
  --trigger-http \
  --allow-unauthenticated \
  --memory=4Gi \
  --timeout=540s \
  --set-env-vars=GCP_PROJECT=$PROJECT_ID,VERTEX_AI_LOCATION=$REGION,USE_VERTEX_AI=true
```

### Get Function URL

```bash
# Get function URL
FUNCTION_URL=$(gcloud functions describe $FUNCTION_NAME \
  --gen2 \
  --region=$REGION \
  --format='value(serviceConfig.uri)')

echo "Function URL: $FUNCTION_URL"
```

### Test Deployed Function

```bash
curl -X POST $FUNCTION_URL \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing in simple terms",
    "max_tokens": 200,
    "temperature": 0.7,
    "model": "gemini-pro"
  }'
```

## Configuration Options

### Environment Variables

Set environment variables during deployment:

```bash
gcloud functions deploy $FUNCTION_NAME \
  --gen2 \
  --set-env-vars=\
GCP_PROJECT=$PROJECT_ID,\
VERTEX_AI_LOCATION=$REGION,\
USE_VERTEX_AI=true,\
VERTEX_AI_ENDPOINT=""
```

### Available Models on Vertex AI

- `gemini-pro` - Gemini Pro (multimodal)
- `gemini-pro-vision` - Gemini Pro with vision
- `text-bison` - PaLM 2 for text
- `chat-bison` - PaLM 2 for chat
- Custom deployed models

## Deploy with Custom Configuration

### High Memory Configuration

```bash
gcloud functions deploy $FUNCTION_NAME \
  --gen2 \
  --runtime=python311 \
  --region=$REGION \
  --source=. \
  --entry-point=inference \
  --trigger-http \
  --allow-unauthenticated \
  --memory=16Gi \
  --cpu=4 \
  --timeout=3600s
```

### With Service Account

```bash
# Create service account
gcloud iam service-accounts create llm-function-sa \
  --display-name="LLM Function Service Account"

# Grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:llm-function-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# Deploy with service account
gcloud functions deploy $FUNCTION_NAME \
  --gen2 \
  --runtime=python311 \
  --region=$REGION \
  --source=. \
  --entry-point=inference \
  --trigger-http \
  --allow-unauthenticated \
  --service-account=llm-function-sa@$PROJECT_ID.iam.gserviceaccount.com
```

## Monitoring and Logging

### View Logs

```bash
# Stream logs
gcloud functions logs read $FUNCTION_NAME \
  --gen2 \
  --region=$REGION \
  --limit=50

# Follow logs in real-time
gcloud functions logs tail $FUNCTION_NAME \
  --gen2 \
  --region=$REGION
```

### Metrics in Cloud Console

Navigate to Cloud Functions → Select Function → View metrics:
- Invocation count
- Execution time
- Memory usage
- Error rate

### Set Up Alerting

```bash
# Create alert policy (example using gcloud)
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High Error Rate" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=0.05
```

## Advanced: Cloud Run for Better Performance

For better performance and control, consider Cloud Run:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD exec functions-framework --target=inference --port=8080
```

Deploy to Cloud Run:

```bash
# Build container
gcloud builds submit --tag gcr.io/$PROJECT_ID/llm-inference

# Deploy to Cloud Run
gcloud run deploy llm-inference \
  --image gcr.io/$PROJECT_ID/llm-inference \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 3600 \
  --set-env-vars=GCP_PROJECT=$PROJECT_ID,VERTEX_AI_LOCATION=$REGION
```

## Cost Optimization

- Use Gen 2 for better price/performance
- Set appropriate memory allocation
- Use Cloud Run for consistent workloads
- Use Vertex AI batch prediction for large-scale inference
- Enable automatic scaling with min instances = 0

## Security Best Practices

1. **Use Service Accounts**: Don't use default compute service account
2. **Enable Authentication**: Remove `--allow-unauthenticated` for production
3. **Use Secret Manager**: Store API keys in Secret Manager
4. **Set Up VPC**: Use VPC connectors for private resources
5. **Enable Cloud Armor**: Protect against DDoS attacks

## Clean Up

```bash
# Delete function
gcloud functions delete $FUNCTION_NAME \
  --gen2 \
  --region=$REGION \
  --quiet

# Delete service account
gcloud iam service-accounts delete \
  llm-function-sa@$PROJECT_ID.iam.gserviceaccount.com \
  --quiet
```

## Troubleshooting

### Common Issues

1. **Permission Denied**:
   ```bash
   # Grant aiplatform.user role
   gcloud projects add-iam-policy-binding $PROJECT_ID \
     --member="serviceAccount:YOUR_SA@$PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/aiplatform.user"
   ```

2. **Timeout Errors**:
   - Increase timeout: `--timeout=540s`
   - Use async invocation patterns
   - Consider Cloud Run for long-running tasks

3. **Memory Issues**:
   - Increase memory allocation: `--memory=8Gi`
   - Optimize model loading
   - Use model caching

## References

- [Cloud Functions Documentation](https://cloud.google.com/functions/docs)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Functions Framework Python](https://github.com/GoogleCloudPlatform/functions-framework-python)
