# AI/ML Pipeline

This repository contains machine learning pipelines built with different orchestration tools: **Apache Airflow**, **Dagster**, **Kubeflow**, and **MLflow**. Each implementation demonstrates best practices for building, deploying, and managing ML workflows on both local environments and Amazon AWS cloud infrastructure.

## 📁 Directory Structure

```
PIPELINE/
├── README.md                 # This file - overview of all pipeline implementations
├── Airflow/                  # Apache Airflow ML pipeline implementation
│   ├── dags/                 # Airflow DAG definitions
│   │   ├── bert_fine_tuning_dag.py
│   │   └── enhanced_bert_fine_tuning_dag.py
│   ├── src/                  # Source code for ML tasks
│   │   ├── bert_fine_tuning.py
│   │   ├── data_wrangling.py
│   │   └── enhanced_bert_training.py
│   ├── config/               # Configuration files
│   ├── data/                 # Training datasets
│   ├── docker-compose.yml    # Local Airflow deployment
│   ├── terraform/            # AWS MWAA infrastructure
│   └── api.py               # FastAPI deployment endpoint
├── Dagster/                  # Dagster ML pipeline implementation
│   ├── dagster_project/      # Main Dagster project
│   ├── src/                  # Pipeline assets and resources
│   ├── aws_config/           # AWS deployment configurations
│   ├── dagster.yaml         # Dagster workspace configuration
│   ├── docker-compose.yml    # Local Dagster deployment
│   └── ARCHITECTURE.md       # Detailed architecture documentation
├── Kubeflow/                 # Kubeflow ML pipeline implementation
│   ├── pipeline/             # Kubeflow pipeline definitions
│   ├── src/                  # ML components and models
│   ├── cloudformation/       # AWS EKS infrastructure
│   ├── terraform/            # Terraform deployment scripts
│   ├── docker-compose.yml    # Local development environment
│   └── Makefile             # Build and deployment automation
└── MLflow/                   # MLflow ML pipeline implementation
    ├── Dataset/              # Fish weight prediction dataset
    ├── notebooks/            # Jupyter notebooks for exploration
    ├── scikit-learn/         # Scikit-learn model implementations
    ├── MLproject            # MLflow project configuration
    ├── conda.yaml           # Conda environment specification
    ├── train.py             # Model training script
    ├── evaluate.py          # Model evaluation script
    └── serve_api.py         # Model serving API
```

## 🔧 Pipeline Implementations

### 🌪️ Apache Airflow
**Focus**: Workflow orchestration and scheduling for BERT model fine-tuning

- **Use Case**: BERT fine-tuning pipeline with automated scheduling, monitoring, and AWS SageMaker integration
- **Key Features**: 
  - DAG-based workflow orchestration
  - Integration with AWS MWAA (Managed Workflows for Apache Airflow)
  - Docker containerization support
  - Comprehensive error handling and retries
  - Model deployment to SageMaker endpoints
- **Best For**: Complex, time-based scheduling requirements and enterprise-grade workflow management
- **AWS Integration**: MWAA, SageMaker, S3, IAM, CloudWatch

### ⚡ Dagster
**Focus**: Asset-centric ML pipeline with strong data lineage and observability

- **Use Case**: BERT training pipeline with emphasis on data assets and lineage tracking
- **Key Features**:
  - Asset-based pipeline definition
  - Built-in data quality checks
  - Rich UI for pipeline monitoring
  - Integration with AWS services
  - Comprehensive testing framework
- **Best For**: Data-centric workflows requiring strong observability and data lineage
- **AWS Integration**: ECS, S3, SageMaker, EMR, Lambda

### ☸️ Kubeflow
**Focus**: Kubernetes-native ML pipelines with scalable model training and deployment

- **Use Case**: BERT ML pipeline with Kubernetes orchestration for scalability
- **Key Features**:
  - Kubernetes-native pipeline components
  - Distributed training capabilities
  - Model serving with KFServing
  - Integration with cloud ML services
  - Container-based execution
- **Best For**: Cloud-native ML workflows requiring high scalability and Kubernetes expertise
- **AWS Integration**: EKS, SageMaker, S3, ECR, Load Balancers

### 🐟 MLflow
**Focus**: End-to-end ML lifecycle management with experiment tracking and model registry

- **Use Case**: Fish weight prediction with comprehensive experiment tracking and model management
- **Key Features**:
  - Experiment tracking and metrics logging
  - Model registry and versioning
  - Multiple algorithm comparison (Linear, Ridge, Lasso, Random Forest)
  - REST API for model serving
  - Integration with various ML frameworks
- **Best For**: Research-oriented workflows requiring extensive experiment tracking and model comparison
- **AWS Integration**: SageMaker, S3, EC2, Model Registry

## Machine Learning (ML) Pipeline Architectures on Amazon AWS

### Apache Airflow on Amazon AWS
- **Orchestration**: AWS MWAA (Managed Workflows for Apache Airflow)
- **Training**: Amazon SageMaker training jobs
- **Storage**: S3 for data and model artifacts
- **Deployment**: SageMaker endpoints with API Gateway
- **Monitoring**: CloudWatch logs and metrics

### Dagster on Amazon AWS
- **Orchestration**: ECS Fargate for Dagster daemon and web server
- **Training**: SageMaker or EMR for distributed processing
- **Storage**: S3 for data lakes and model storage
- **Deployment**: Lambda functions for serverless inference
- **Monitoring**: CloudWatch and Dagster's built-in observability

### Kubeflow on Amazon AWS
- **Orchestration**: Amazon EKS (Elastic Kubernetes Service)
- **Training**: Distributed training across EKS nodes
- **Storage**: EFS for shared storage, S3 for data lakes
- **Deployment**: KFServing on EKS with Application Load Balancer
- **Monitoring**: Kubernetes metrics and CloudWatch Container Insights

### MLflow on Amazon AWS
- **Orchestration**: SageMaker Pipelines with MLflow tracking
- **Training**: SageMaker training jobs with MLflow logging
- **Storage**: S3 for artifacts, RDS for MLflow metadata
- **Deployment**: SageMaker endpoints registered in MLflow Model Registry
- **Monitoring**: MLflow UI with CloudWatch integration

## Choosing the right Pipeline

| Tool | Best For | Learning Curve | AWS Integration | Community |
|------|----------|---------------|-----------------|-----------|
| **Airflow** | Complex scheduling, enterprise workflows | Medium | Excellent (MWAA) | Large |
| **Dagster** | Data-centric pipelines, observability | Medium | Good | Growing |
| **Kubeflow** | Kubernetes-native, scalable ML | High | Good (EKS) | Active |
| **MLflow** | Experiment tracking, model lifecycle | Low | Excellent | Large |


Choose the pipeline that best fits your use case and explore the respective folder for detailed setup instructions.

##  Comparison: ML Pipeline Tools on Amazon AWS

### Apache Airflow + AWS
- **Orchestration**: AWS MWAA provides fully managed Apache Airflow
- **Strengths**: Mature ecosystem, extensive AWS integration, enterprise-ready
- **Use Cases**: Complex workflows, time-based scheduling, enterprise ML pipelines
- **AWS Services**: MWAA, SageMaker, S3, Lambda, EMR, Redshift

### Dagster + AWS 
- **Orchestration**: Asset-centric pipeline orchestration with strong data lineage
- **Strengths**: Modern data pipeline design, built-in testing, excellent observability
- **Use Cases**: Data-centric ML workflows, feature engineering, data quality monitoring
- **AWS Services**: ECS, SageMaker, S3, EMR, Lambda, Redshift

### Kubeflow + AWS
- **Orchestration**: Kubernetes-native ML pipelines on Amazon EKS
- **Strengths**: Cloud-native, highly scalable, container-based execution
- **Use Cases**: Large-scale distributed training, microservices architecture, multi-cloud deployments
- **AWS Services**: EKS, SageMaker, S3, ECR, EFS, Application Load Balancer

### MLflow + AWS
- **Orchestration**: Experiment tracking and model lifecycle management
- **Strengths**: Simple setup, excellent for experimentation, model registry integration
- **Use Cases**: Research workflows, model comparison, experiment tracking, A/B testing
- **AWS Services**: SageMaker (managed MLflow), S3, EC2, RDS, Model Registry

### Ray + AWS
- **Orchestration**: Distributed computing framework for scaling Python and AI workloads
- **Strengths**: High-performance distributed computing, unified API for data/ML/serving
- **Use Cases**: Large-scale data processing, distributed ML training, hyperparameter tuning
- **AWS Services**: EC2, EMR, SageMaker, S3, Ray on SageMaker Hyperpod

## Integration

### Multi-Tool Approaches
- **Ray + MLflow**: Use Ray for distributed training with MLflow for experiment tracking
- **Airflow + MLflow**: Orchestrate MLflow experiments using Airflow DAGs  
- **Kubeflow + MLflow**: Deploy MLflow tracking server on Kubernetes for experiment management
- **Dagster + Ray**: Use Dagster for data pipeline orchestration with Ray for compute-intensive tasks

### Amazon AWS specific patterns
- **SageMaker Integration**: All tools can integrate with SageMaker for managed training and deployment
- **S3 Data Lakes**: Centralized data storage accessible by all pipeline tools
- **IAM Security**: Unified access control across all AWS services
- **CloudWatch Monitoring**: Consistent logging and monitoring across all implementations

## Decision Matrix

| Requirement | Airflow | Dagster | Kubeflow | MLflow | Ray |
|-------------|---------|---------|----------|--------|-----|
| **Ease of Setup** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Scalability** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **AWS Integration** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Data Lineage** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Experiment Tracking** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Production Ready** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Learning Curve** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Community Support** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

## References

### Documentation
- [Apache Airflow](https://airflow.apache.org/) - Official Airflow documentation
- [Dagster](https://dagster.io/) - Official Dagster documentation  
- [Kubeflow](https://kubeflow.org/) - Official Kubeflow documentation
- [MLflow](https://mlflow.org/) - Official MLflow documentation
- [Ray](https://ray.io/) - Official Ray documentation

### Amazon AWS Services
- [Amazon SageMaker](https://aws.amazon.com/sagemaker/) - Fully managed ML service
- [AWS MWAA](https://aws.amazon.com/managed-workflows-for-apache-airflow/) - Managed Airflow
- [Amazon EKS](https://aws.amazon.com/eks/) - Managed Kubernetes service
- [AWS Lambda](https://aws.amazon.com/lambda/) - Serverless compute service

### Blog Posts & Tutorials
- [Scaling AI and Machine Learning Workloads with Ray on AWS](https://aws.amazon.com/blogs/opensource/scaling-ai-and-machine-learning-workloads-with-ray-on-aws/)
- [LLM experimentation at scale using Amazon SageMaker Pipelines and MLflow](https://aws.amazon.com/blogs/machine-learning/llm-experimentation-at-scale-using-amazon-sagemaker-pipelines-and-mlflow/)
- [Building ML Pipelines with Kubeflow on Amazon EKS](https://aws.amazon.com/blogs/opensource/kubeflow-amazon-eks/)
- [Orchestrating Analytics Jobs on Amazon EMR with Apache Airflow](https://aws.amazon.com/blogs/big-data/orchestrating-analytics-jobs-on-amazon-emr-with-apache-airflow/)
