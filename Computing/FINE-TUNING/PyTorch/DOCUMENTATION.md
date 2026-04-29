# BERT Text classification Documentation

## Overview

This FastAPI-based REST API provides text classification services using a fine-tuned BERT model. It offers both single text and batch processing capabilities with optional confidence scores.

## Start

### Local development
```bash
# 1. Install dependencies
pip install -r requirements-api.txt

# 2. Start the server
python api.py
# or
uvicorn api:app --reload

# 3. Access the API
curl http://localhost:8000/health
```

### Docker deployment
```bash
# Build and test
./docker_deploy.sh test

# Or use docker-compose
docker-compose up -d
```

## API Endpoints

### Base URL
- Local: `http://localhost:8000`
- Docker: `http://localhost:8000` (or configured port)

### Authentication
Currently, no authentication is required (suitable for internal/development use).

## Endpoint reference

### 1. Health Check
**GET** `/health`

Check API and model status.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2025-07-20T15:30:00",
  "version": "1.0.0"
}
```

### 2. Model information
**GET** `/model/info`

Get detailed model information.

**Response:**
```json
{
  "model_name": "bert-base-uncased",
  "model_path": "./fine_tuned_bert",
  "device": "cpu",
  "tokenizer_vocab_size": 30522,
  "max_sequence_length": 512
}
```

### 3. Text Classification
**POST** `/classify`

Classify a single text input.

**Request Body:**
```json
{
  "text": "I absolutely love this product!",
  "return_confidence": true
}
```

**Response:**
```json
{
  "text": "I absolutely love this product!",
  "prediction": 1,
  "label": "positive",
  "confidence": 0.9876,
  "processing_time_ms": 45.23
}
```

**Parameters:**
- `text` (string, required): Text to classify (1-512 characters)
- `return_confidence` (boolean, optional): Include confidence score

### 4. Text Classification (Batch)
**POST** `/classify/batch`

Classify multiple texts in a single request.

**Request Body:**
```json
{
  "texts": [
    "Great product!",
    "Terrible service.",
    "Average experience."
  ],
  "return_confidence": true
}
```

**Response:**
```json
{
  "results": [
    {
      "text": "Great product!",
      "prediction": 1,
      "label": "positive", 
      "confidence": 0.9234,
      "processing_time_ms": 42.1
    },
    {
      "text": "Terrible service.",
      "prediction": 0,
      "label": "negative",
      "confidence": 0.8765,
      "processing_time_ms": 38.7
    },
    {
      "text": "Average experience.",
      "prediction": 1,
      "label": "positive",
      "confidence": 0.6123,
      "processing_time_ms": 41.2
    }
  ],
  "total_texts": 3,
  "total_processing_time_ms": 122.0
}
```

**Parameters:**
- `texts` (array of strings, required): 1-100 texts to classify
- `return_confidence` (boolean, optional): Include confidence scores

### 5. Demo Classification
**GET** `/classify/demo`

Get sample classifications for testing purposes.

**Response:**
```json
{
  "demo_results": [
    {
      "text": "I absolutely love this product! It's amazing!",
      "prediction": 1,
      "label": "positive",
      "confidence": 0.9876,
      "processing_time_ms": 45.23
    }
    // ... more demo results
  ],
  "note": "These are demo classifications using predefined texts"
}
```

## Error responses

### HTTP status codes
- `200` - Success
- `400` - Bad Request (invalid input)
- `422` - Validation Error (malformed request)
- `500` - Internal Server Error
- `503` - Service Unavailable (model not loaded)

### Error response format
```json
{
  "detail": "Error description",
  "status_code": 400
}
```

### Errors
1. **Empty text**: Text field cannot be empty
2. **Text too long**: Maximum 512 characters per text
3. **Too many texts**: Maximum 100 texts per batch request
4. **Model not loaded**: Service starting up or model failed to load

## Testing

### cURL

#### Health Check
```bash
curl -X GET http://localhost:8000/health
```

#### Classification (Single)
```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "I really enjoyed this movie!", "return_confidence": true}'
```

#### Classification (Batch)
```bash
curl -X POST http://localhost:8000/classify/batch \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["Excellent service!", "Poor quality.", "It was okay."],
    "return_confidence": true
  }'
```

### Python client
```python
import requests
import json

# API base URL
base_url = "http://localhost:8000"

# Single text classification
response = requests.post(f"{base_url}/classify", 
    json={
        "text": "This product is amazing!",
        "return_confidence": True
    }
)
result = response.json()
print(f"Prediction: {result['label']}, Confidence: {result['confidence']}")

# Batch classification
texts = ["Great!", "Terrible.", "Average."]
response = requests.post(f"{base_url}/classify/batch",
    json={
        "texts": texts,
        "return_confidence": True
    }
)
results = response.json()
for result in results['results']:
    print(f"'{result['text']}' -> {result['label']} ({result['confidence']:.3f})")
```

### JavaScript/Node.js example
```javascript
const axios = require('axios');

const baseUrl = 'http://localhost:8000';

// Single text classification
async function classifyText(text) {
    try {
        const response = await axios.post(`${baseUrl}/classify`, {
            text: text,
            return_confidence: true
        });
        
        console.log(`"${text}" -> ${response.data.label} (${response.data.confidence})`);
        return response.data;
    } catch (error) {
        console.error('Classification failed:', error.response.data);
    }
}

// Batch classification
async function classifyBatch(texts) {
    try {
        const response = await axios.post(`${baseUrl}/classify/batch`, {
            texts: texts,
            return_confidence: true
        });
        
        response.data.results.forEach(result => {
            console.log(`"${result.text}" -> ${result.label} (${result.confidence})`);
        });
        
        return response.data;
    } catch (error) {
        console.error('Batch classification failed:', error.response.data);
    }
}

// Usage
classifyText("I love this product!");
classifyBatch(["Great service!", "Poor quality.", "Average experience."]);
```

## Performance

### Response times
- Single text: ~40-60ms (CPU), ~20-30ms (GPU)
- Batch processing: ~30-50ms per text
- Model loading: ~5-10 seconds on startup

### Resource usage
- Memory: ~2-4GB (depends on model size)
- CPU: 1-4 cores recommended
- GPU: Optional, but significantly faster

### Optimization
1. **Batch processing**: Use batch endpoint for multiple texts
2. **Keep connections alive**: Reuse HTTP connections
3. **Text length**: Shorter texts process faster
4. **Model quantization**: Use quantized models for faster inference

## Monitoring and logging

### Log levels
- `INFO`: General operational messages
- `ERROR`: Error conditions
- `DEBUG`: Detailed diagnostic information

### Metrics
- Request processing time
- Model inference time
- Request volume
- Error rates

### Health monitoring
Regular health checks are available at `/health` endpoint for:
- Load balancer health checks
- Container orchestration systems
- Monitoring tools

## Security

### Current Implementation
- No authentication (development/internal use)
- CORS enabled for all origins
- No rate limiting

### Production
1. **Authentication**: Add JWT or API key authentication
2. **Rate Limiting**: Implement request rate limiting
3. **Input Validation**: Enhanced input sanitization
4. **HTTPS**: Use TLS encryption
5. **CORS**: Restrict origins in production
6. **Logging**: Avoid logging sensitive data

###  Security enhancements
```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

# Rate limiting
@app.post("/classify")
@limiter(times=100, seconds=60)  # 100 requests per minute
async def classify_text(request: TextRequest):
    # ... implementation
```

## Deployment

### Development
```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
# With multiple workers
uvicorn api:app --workers 4 --host 0.0.0.0 --port 8000

# With Gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api:app --bind 0.0.0.0:8000
```

### Docker production
```bash
# Using docker-compose with nginx
docker-compose --profile production up -d
```

## Troubleshooting

### Issues

#### API not starting
```bash
# Check logs
docker logs <container_name>

# Common causes:
# - Port already in use
# - Model files missing
# - Insufficient memory
```

#### Model loading errors
```bash
# Verify model files exist
ls -la fine_tuned_bert/

# Check model compatibility
python -c "from transformers import BertForSequenceClassification; 
           model = BertForSequenceClassification.from_pretrained('./fine_tuned_bert')"
```

#### Performance issues
```bash
# Monitor resource usage
docker stats <container_name>

# Check for memory leaks
# Restart container if memory usage keeps growing
docker restart <container_name>
```
