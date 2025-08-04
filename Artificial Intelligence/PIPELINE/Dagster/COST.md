
# AWS Cost Analysis for Dagster BERT Pipeline

## Monthly Cost estimates (us-east-1)

### Minimal setup (Development)
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

### Production setup
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

### Enterprise setup
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

## Cost optimization strategies

1. **Use Spot Instances**: 50-70% cost reduction for training workloads
2. **S3 Intelligent Tiering**: Automatic cost optimization for storage
3. **Reserved Instances**: 30-60% discount for predictable workloads
4. **Lambda for Inference**: Pay-per-request pricing for low-volume inference
5. **Scheduled Scaling**: Scale down non-production environments during off-hours
