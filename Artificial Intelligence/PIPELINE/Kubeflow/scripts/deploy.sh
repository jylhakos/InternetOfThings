#!/bin/bash

# Build and Deploy BERT Model with Kubeflow pipeline
# This script handles Docker image building and pushing to ECR

set -e

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Default values
AWS_REGION=${AWS_REGION:-us-west-2}
AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID:-}
ECR_REPOSITORY=${ECR_REPOSITORY:-bert-pipeline}
CLUSTER_NAME=${EKS_CLUSTER_NAME:-kubeflow-cluster}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check AWS credentials and get account ID
check_aws_credentials() {
    log_info "Checking AWS credentials..."
    
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured"
        log_info "Please run: aws configure"
        exit 1
    fi
    
    if [ -z "$AWS_ACCOUNT_ID" ]; then
        AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
        log_info "AWS Account ID: $AWS_ACCOUNT_ID"
    fi
}

# Login to ECR
ecr_login() {
    log_info "Logging into ECR..."
    aws ecr get-login-password --region "$AWS_REGION" | \
        docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
    log_success "ECR login successful"
}

# Build Docker images
build_images() {
    log_info "Building Docker images..."
    
    # Build training image
    log_info "Building training image..."
    docker build -t bert-training -f Dockerfile.training .
    docker tag bert-training:latest "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:training"
    log_success "Training image built"
    
    # Build serving image
    log_info "Building serving image..."
    docker build -t bert-serving .
    docker tag bert-serving:latest "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:serving"
    log_success "Serving image built"
    
    # Build pipeline component images
    log_info "Building pipeline component images..."
    
    # Data preprocessing component
    cat > Dockerfile.preprocessing << 'EOF'
FROM python:3.9-slim

WORKDIR /app

RUN pip install pandas scikit-learn transformers torch

COPY pipeline/components/data_preprocessing.py .

CMD ["python", "data_preprocessing.py"]
EOF
    
    docker build -t bert-preprocessing -f Dockerfile.preprocessing .
    docker tag bert-preprocessing:latest "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:preprocessing"
    
    # Model evaluation component
    cat > Dockerfile.evaluation << 'EOF'
FROM python:3.9-slim

WORKDIR /app

RUN pip install torch transformers scikit-learn

COPY pipeline/components/model_evaluation.py .

CMD ["python", "model_evaluation.py"]
EOF
    
    docker build -t bert-evaluation -f Dockerfile.evaluation .
    docker tag bert-evaluation:latest "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:evaluation"
    
    log_success "All images built successfully"
}

# Push images to ECR
push_images() {
    log_info "Pushing images to ECR..."
    
    # Push training image
    docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:training"
    log_success "Training image pushed"
    
    # Push serving image
    docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:serving"
    log_success "Serving image pushed"
    
    # Push component images
    docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:preprocessing"
    log_success "Preprocessing image pushed"
    
    docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:evaluation"
    log_success "Evaluation image pushed"
    
    log_success "All images pushed to ECR"
}

# Create Kubernetes manifests
create_k8s_manifests() {
    log_info "Creating Kubernetes manifests..."
    
    mkdir -p k8s
    
    # Persistent Volume Claim for model storage
    cat > k8s/model-pvc.yaml << EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: bert-model-pvc
  namespace: kubeflow
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: gp2
EOF
    
    # Secret for ECR access
    cat > k8s/ecr-secret.yaml << EOF
apiVersion: v1
kind: Secret
metadata:
  name: ecr-secret
  namespace: kubeflow
type: kubernetes.io/dockerconfigjson
data:
  .dockerconfigjson: $(echo -n '{"auths":{"'$AWS_ACCOUNT_ID'.dkr.ecr.'$AWS_REGION'.amazonaws.com":{"auth":"'$(echo -n "AWS:$(aws ecr get-login-password --region $AWS_REGION)" | base64 -w 0)'"}}}' | base64 -w 0)
EOF
    
    # Model serving deployment
    cat > k8s/bert-serving-deployment.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bert-serving
  namespace: kubeflow
  labels:
    app: bert-serving
spec:
  replicas: 2
  selector:
    matchLabels:
      app: bert-serving
  template:
    metadata:
      labels:
        app: bert-serving
    spec:
      imagePullSecrets:
      - name: ecr-secret
      containers:
      - name: bert-serving
        image: $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:serving
        ports:
        - containerPort: 8000
        env:
        - name: MODEL_PATH
          value: "/app/model"
        - name: API_HOST
          value: "0.0.0.0"
        - name: API_PORT
          value: "8000"
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 1000m
            memory: 2Gi
        volumeMounts:
        - name: model-storage
          mountPath: /app/model
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: model-storage
        persistentVolumeClaim:
          claimName: bert-model-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: bert-serving-service
  namespace: kubeflow
  labels:
    app: bert-serving
spec:
  selector:
    app: bert-serving
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
    name: http
  type: LoadBalancer
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: bert-serving-ingress
  namespace: kubeflow
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: bert-api.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: bert-serving-service
            port:
              number: 80
EOF
    
    # HorizontalPodAutoscaler
    cat > k8s/bert-serving-hpa.yaml << EOF
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: bert-serving-hpa
  namespace: kubeflow
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: bert-serving
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
EOF
    
    log_success "Kubernetes manifests created in k8s/ directory"
}

# Deploy to Kubernetes
deploy_to_k8s() {
    log_info "Deploying to Kubernetes..."
    
    # Ensure we're connected to the right cluster
    if [ -n "$CLUSTER_NAME" ]; then
        aws eks update-kubeconfig --region "$AWS_REGION" --name "$CLUSTER_NAME"
    fi
    
    # Create namespace if it doesn't exist
    kubectl create namespace kubeflow --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply manifests
    kubectl apply -f k8s/
    
    # Wait for deployment
    log_info "Waiting for deployment to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/bert-serving -n kubeflow
    
    # Get service information
    log_info "Getting service information..."
    kubectl get svc bert-serving-service -n kubeflow
    
    log_success "Deployment completed successfully"
}

# Compile and upload pipeline
upload_pipeline() {
    log_info "Compiling and uploading Kubeflow pipeline..."
    
    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        source venv/bin/activate
    elif [ -d "bert-kubeflow-env" ]; then
        source bert-kubeflow-env/bin/activate
    fi
    
    # Compile pipeline
    python pipeline/bert_pipeline.py
    
    # Upload to Kubeflow (if accessible)
    if command -v kfp &> /dev/null; then
        log_info "Uploading pipeline to Kubeflow..."
        
        # Try to get Kubeflow endpoint
        local kubeflow_endpoint
        if kubectl get svc -n istio-system istio-ingressgateway &> /dev/null; then
            kubeflow_endpoint=$(kubectl get svc -n istio-system istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
            if [ -n "$kubeflow_endpoint" ]; then
                log_info "Kubeflow endpoint: $kubeflow_endpoint"
                # kfp pipeline upload-pipeline --file bert_pipeline.yaml --name bert-training-pipeline --endpoint $kubeflow_endpoint
            fi
        fi
        
        log_warning "Please upload bert_pipeline.yaml manually to Kubeflow UI"
    else
        log_warning "kfp CLI not available. Please upload bert_pipeline.yaml manually to Kubeflow UI"
    fi
    
    log_success "Pipeline compilation completed"
}

# Create monitoring manifests
create_monitoring() {
    log_info "Creating monitoring manifests..."
    
    mkdir -p monitoring
    
    # ServiceMonitor for Prometheus
    cat > monitoring/bert-service-monitor.yaml << EOF
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: bert-serving-monitor
  namespace: kubeflow
  labels:
    app: bert-serving
spec:
  selector:
    matchLabels:
      app: bert-serving
  endpoints:
  - port: http
    path: /metrics
    interval: 30s
EOF
    
    # Grafana dashboard ConfigMap
    cat > monitoring/bert-dashboard.yaml << EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: bert-dashboard
  namespace: monitoring
  labels:
    grafana_dashboard: "1"
data:
  bert-dashboard.json: |
    {
      "dashboard": {
        "id": null,
        "title": "BERT Model Serving",
        "tags": ["bert", "ml"],
        "style": "dark",
        "timezone": "browser",
        "panels": [
          {
            "title": "Request Rate",
            "type": "graph",
            "targets": [
              {
                "expr": "rate(http_requests_total{job=\"bert-serving\"}[5m])",
                "legendFormat": "{{method}} {{status}}"
              }
            ]
          },
          {
            "title": "Response Time",
            "type": "graph",
            "targets": [
              {
                "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job=\"bert-serving\"}[5m]))",
                "legendFormat": "95th percentile"
              }
            ]
          }
        ],
        "time": {
          "from": "now-1h",
          "to": "now"
        },
        "refresh": "5s"
      }
    }
EOF
    
    log_success "Monitoring manifests created"
}

# Test deployment
test_deployment() {
    log_info "Testing deployment..."
    
    # Get service endpoint
    local service_endpoint
    service_endpoint=$(kubectl get svc bert-serving-service -n kubeflow -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
    
    if [ -z "$service_endpoint" ]; then
        log_warning "LoadBalancer endpoint not available yet. Using port-forward for testing..."
        kubectl port-forward svc/bert-serving-service 8000:80 -n kubeflow &
        local port_forward_pid=$!
        sleep 5
        service_endpoint="localhost:8000"
    fi
    
    # Test health endpoint
    log_info "Testing health endpoint..."
    if curl -f "http://$service_endpoint/health" &> /dev/null; then
        log_success "Health check passed"
    else
        log_error "Health check failed"
    fi
    
    # Test prediction endpoint
    log_info "Testing prediction endpoint..."
    local test_response
    test_response=$(curl -s -X POST "http://$service_endpoint/predict" \
        -H "Content-Type: application/json" \
        -d '{"text": "This is a test message", "return_confidence": true}')
    
    if [ $? -eq 0 ]; then
        log_success "Prediction test passed"
        echo "Response: $test_response"
    else
        log_error "Prediction test failed"
    fi
    
    # Clean up port-forward if used
    if [ -n "$port_forward_pid" ]; then
        kill $port_forward_pid 2>/dev/null || true
    fi
}

# Main deployment function
main() {
    log_info "Starting BERT model deployment..."
    
    # Check prerequisites
    check_aws_credentials
    
    # Login to ECR
    ecr_login
    
    # Build and push images
    build_images
    push_images
    
    # Create Kubernetes manifests
    create_k8s_manifests
    
    # Deploy to Kubernetes
    deploy_to_k8s
    
    # Create monitoring
    create_monitoring
    
    # Compile and upload pipeline
    upload_pipeline
    
    # Test deployment
    test_deployment
    
    log_success "Deployment completed successfully!"
    
    echo ""
    echo "📊 DEPLOYMENT SUMMARY:"
    echo "  ✅ Docker images built and pushed to ECR"
    echo "  ✅ Kubernetes manifests created"
    echo "  ✅ Model serving deployed to EKS"
    echo "  ✅ Kubeflow pipeline compiled"
    echo "  ✅ Monitoring setup created"
    echo ""
    echo "🔗 ACCESS POINTS:"
    echo "  Kubeflow UI: kubectl port-forward -n istio-system svc/istio-ingressgateway 8080:80"
    echo "  BERT API: kubectl port-forward -n kubeflow svc/bert-serving-service 8000:80"
    echo "  Grafana: kubectl port-forward -n monitoring svc/grafana 3000:80"
    echo ""
    echo "📝 NEXT STEPS:"
    echo "  1. Access Kubeflow UI and upload bert_pipeline.yaml"
    echo "  2. Run the pipeline with your training data"
    echo "  3. Monitor training progress in Kubeflow UI"
    echo "  4. Test the deployed model API"
    echo ""
}

# Script options
case "${1:-}" in
    "build")
        check_aws_credentials
        ecr_login
        build_images
        ;;
    "push")
        check_aws_credentials
        ecr_login
        push_images
        ;;
    "deploy")
        check_aws_credentials
        create_k8s_manifests
        deploy_to_k8s
        ;;
    "pipeline")
        upload_pipeline
        ;;
    "test")
        test_deployment
        ;;
    "monitoring")
        create_monitoring
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [build|push|deploy|pipeline|test|monitoring|help]"
        echo ""
        echo "Options:"
        echo "  build      Build Docker images only"
        echo "  push       Push Docker images to ECR only"
        echo "  deploy     Deploy to Kubernetes only"
        echo "  pipeline   Compile and upload pipeline only"
        echo "  test       Test deployment only"
        echo "  monitoring Create monitoring setup only"
        echo "  help       Show this help message"
        echo ""
        echo "Run without arguments for full deployment"
        ;;
    *)
        main
        ;;
esac
