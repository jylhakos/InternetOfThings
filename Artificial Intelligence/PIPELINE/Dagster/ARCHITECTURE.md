
# Dagster BERT Pipelines

## Local development flow
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Prep     │───▶│   BERT Training  │───▶│   Evaluation    │
│                 │    │                  │    │                 │
│ training_dataset│    │trained_bert_model│    │model_evaluation │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Inference Tests │◀───│   Deployment     │◀───│                 │
│                 │    │                  │    │                 │
│ inference_tests │    │ deployed_model   │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## AWS production architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                           AWS Cloud                             │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │     VPC     │  │   Internet  │  │   Route53   │              │
│  │             │  │   Gateway   │  │     DNS     │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                Application Load Balancer                │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           │                                     │
│         ┌─────────────────┼─────────────────┐                   │
│         │                 │                 │                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ECS Cluster  │  │ECS Cluster  │  │   Lambda    │              │
│  │  Dagster    │  │ BERT API    │  │ Functions   │              │
│  │ Webserver   │  │   Server    │  │             │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│         │                 │                 │                   │
│         └─────────────────┼─────────────────┘                   │
│                           │                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │     RDS     │  │     S3      │  │  Secrets    │              │
│  │ PostgreSQL  │  │   Bucket    │  │  Manager    │              │
│  │             │  │             │  │             │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ CloudWatch  │  │     ECR     │  │    IAM      │              │
│  │   Logs      │  │ Container   │  │   Roles     │              │
│  │             │  │  Registry   │  │             │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

## Component Interaction
```
Dagster Webserver (Port 3000)
    │
    ├── Asset Management
    ├── Job Scheduling
    ├── Run Coordination
    └── UI Interface
    
Dagster Daemon
    │
    ├── Schedule Processing
    ├── Sensor Management
    └── Run Queue Management

BERT API Server (Port 8000)
    │
    ├── Model Inference
    ├── Health Checks
    └── API Documentation

PostgreSQL (Port 5432)
    │
    ├── Run Metadata
    ├── Asset Lineage
    └── Event Logs

S3 Storage
    │
    ├── Model Artifacts
    ├── Training Data
    └── Compute Logs
```

## Data flow
```
Raw Data → Data Preparation → Model Training → Model Evaluation → Deployment → Inference

├── Input: Text samples
├── Processing: Tokenization, splitting
├── Training: BERT fine-tuning
├── Validation: Accuracy, F1-score
├── Deployment: Model serving
└── Output: Classification results
```

## Dagster vs Airflow decision matrix
```
┌─────────────────┬─────────────────┬─────────────────┐
│    Feature      │    Dagster      │    Airflow      │
├─────────────────┼─────────────────┼─────────────────┤
│ Architecture    │ Asset-centric   │ Task-centric    │
│ Data Lineage    │ Built-in        │ Manual setup    │
│ Type Safety     │ Strong typing   │ Dynamic         │
│ UI/UX           │ Modern          │ Traditional     │
│ Testing         │ Built-in        │ Manual          │
│ ML/AI Support   │ Excellent       │ Good            │
│ Community       │ Growing         │ Large           │
│ Learning Curve  │ Moderate        │ Steep           │
│ AWS Integration │ First-class     │ Via providers   │
│ Development     │ Hot reloading   │ Manual restart  │
└─────────────────┴─────────────────┴─────────────────┘
```

## Deployment options
```
Local Development:
┌─────────────────┐
│ Docker Compose  │ ── Dagster + PostgreSQL + MinIO + API
│     Stack       │
└─────────────────┘

AWS ECS Deployment:
┌─────────────────┐
│  ECS Fargate    │ ── Dagster Webserver + Daemon + API
│   Containers    │
└─────────────────┘

AWS Lambda Functions:
┌─────────────────┐
│ Serverless      │ ── Model inference + data processing
│  Functions      │
└─────────────────┘

Kubernetes (Optional):
┌─────────────────┐
│    EKS/K8s      │ ── Scalable container orchestration
│    Cluster      │
└─────────────────┘
```
