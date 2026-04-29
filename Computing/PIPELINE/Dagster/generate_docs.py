#!/usr/bin/env python3
"""
Generate architecture diagrams for the Dagster BERT Pipeline
"""

def create_pipeline_diagram():
    """Create a simple ASCII art diagram of the pipeline"""
    
    diagram = """
# Dagster BERT Pipeline Architecture

## Local Development Flow
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

## AWS Production Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                           AWS Cloud                             │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │     VPC     │  │   Internet  │  │   Route53   │            │
│  │             │  │   Gateway   │  │     DNS     │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                Application Load Balancer                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│         ┌─────────────────┼─────────────────┐                  │
│         │                 │                 │                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ECS Cluster  │  │ECS Cluster  │  │   Lambda    │            │
│  │  Dagster    │  │ BERT API    │  │ Functions   │            │
│  │ Webserver   │  │   Server    │  │             │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│         │                 │                 │                  │
│         └─────────────────┼─────────────────┘                  │
│                           │                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │     RDS     │  │     S3      │  │  Secrets    │            │
│  │ PostgreSQL  │  │   Bucket    │  │  Manager    │            │
│  │             │  │             │  │             │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ CloudWatch  │  │     ECR     │  │    IAM      │            │
│  │   Logs      │  │ Container   │  │   Roles     │            │
│  │             │  │  Registry   │  │             │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
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

## Data Flow
```
Raw Data → Data Preparation → Model Training → Model Evaluation → Deployment → Inference

├── Input: Text samples
├── Processing: Tokenization, splitting
├── Training: BERT fine-tuning
├── Validation: Accuracy, F1-score
├── Deployment: Model serving
└── Output: Classification results
```

## Dagster vs Airflow Decision Matrix
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

## Deployment Options
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
"""
    
    return diagram

def create_cost_analysis():
    """Create cost analysis for AWS deployment"""
    
    cost_analysis = """
# AWS Cost Analysis for Dagster BERT Pipeline

## Monthly Cost Estimates (us-east-1)

### Minimal Setup (Development)
```
┌─────────────────────┬──────────────┬──────────────┐
│      Service        │     Size     │ Monthly Cost │
├─────────────────────┼──────────────┼──────────────┤
│ ECS Fargate         │ 0.5 vCPU     │    $15-25    │
│ RDS PostgreSQL      │ db.t3.micro  │    $13-20    │
│ S3 Storage          │ 10 GB        │    $1-2      │
│ CloudWatch Logs     │ 1 GB         │    $0.50     │
│ Data Transfer       │ 1 GB         │    $0.10     │
│ Load Balancer       │ Basic ALB    │    $18-22    │
├─────────────────────┼──────────────┼──────────────┤
│ Total               │              │  $47-69/mo   │
└─────────────────────┴──────────────┴──────────────┘
```

### Production Setup
```
┌─────────────────────┬──────────────┬──────────────┐
│      Service        │     Size     │ Monthly Cost │
├─────────────────────┼──────────────┼──────────────┤
│ ECS Fargate         │ 2 vCPU       │    $60-90    │
│ RDS PostgreSQL      │ db.t3.small  │    $25-35    │
│ S3 Storage          │ 100 GB       │    $3-5      │
│ CloudWatch Logs     │ 10 GB        │    $5        │
│ Data Transfer       │ 10 GB        │    $1        │
│ Load Balancer       │ ALB + SSL    │    $22-25    │
│ Lambda Functions    │ 1M requests  │    $1-3      │
│ Secrets Manager     │ 5 secrets    │    $2-3      │
├─────────────────────┼──────────────┼──────────────┤
│ Total               │              │ $119-166/mo  │
└─────────────────────┴──────────────┴──────────────┘
```

### Enterprise Setup
```
┌─────────────────────┬──────────────┬──────────────┐
│      Service        │     Size     │ Monthly Cost │
├─────────────────────┼──────────────┼──────────────┤
│ ECS Fargate         │ 4 vCPU Multi │   $200-300   │
│ RDS PostgreSQL      │ db.r5.large  │   $150-200   │
│ S3 Storage          │ 1 TB         │    $25-30    │
│ CloudWatch/X-Ray    │ Full logging │    $20-40    │
│ Data Transfer       │ 100 GB       │    $9-12     │
│ Load Balancer       │ ALB + WAF    │    $50-70    │
│ Lambda Functions    │ 10M requests │    $10-20    │
│ Backup & Disaster   │ Multi-AZ     │    $50-100   │
├─────────────────────┼──────────────┼──────────────┤
│ Total               │              │ $514-772/mo  │
└─────────────────────┴──────────────┴──────────────┘
```

## Cost Optimization Strategies

1. **Use Spot Instances**: 50-70% cost reduction for training workloads
2. **S3 Intelligent Tiering**: Automatic cost optimization for storage
3. **Reserved Instances**: 30-60% discount for predictable workloads
4. **Lambda for Inference**: Pay-per-request pricing for low-volume inference
5. **Scheduled Scaling**: Scale down non-production environments during off-hours
"""
    
    return cost_analysis

def main():
    """Generate and save architecture documentation"""
    
    # Create architecture diagram
    arch_diagram = create_pipeline_diagram()
    with open('ARCHITECTURE.md', 'w') as f:
        f.write(arch_diagram)
    
    # Create cost analysis
    cost_analysis = create_cost_analysis()
    with open('COST.md', 'w') as f:
        f.write(cost_analysis)
    
    print("✓ Architecture documentation created:")
    print("  - ARCHITECTURE.md: Pipeline architecture diagrams")
    print("  - COST.md: AWS cost estimates and optimization")

if __name__ == "__main__":
    main()
