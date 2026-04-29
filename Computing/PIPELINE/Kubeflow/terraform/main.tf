terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.20"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "kubeflow-cluster"
}

variable "node_instance_type" {
  description = "EC2 instance type for EKS nodes"
  type        = string
  default     = "m5.large"
}

variable "desired_capacity" {
  description = "Desired number of nodes"
  type        = number
  default     = 2
}

variable "max_capacity" {
  description = "Maximum number of nodes"
  type        = number
  default     = 4
}

variable "min_capacity" {
  description = "Minimum number of nodes"
  type        = number
  default     = 1
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# VPC for EKS
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"
  
  name = "${var.cluster_name}-vpc"
  cidr = "10.0.0.0/16"
  
  azs             = slice(data.aws_availability_zones.available.names, 0, 3)
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  
  enable_nat_gateway = true
  enable_vpn_gateway = false
  enable_dns_hostnames = true
  enable_dns_support = true
  
  # Tags required for EKS
  public_subnet_tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
    "kubernetes.io/role/elb"                    = "1"
  }
  
  private_subnet_tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
    "kubernetes.io/role/internal-elb"           = "1"
  }
  
  tags = {
    Terraform = "true"
    Environment = "dev"
    Project = "bert-kubeflow"
  }
}

# EKS Cluster
module "eks" {
  source = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"
  
  cluster_name    = var.cluster_name
  cluster_version = "1.27"
  
  vpc_id                         = module.vpc.vpc_id
  subnet_ids                     = module.vpc.private_subnets
  cluster_endpoint_public_access = true
  
  # EKS Managed Node Group(s)
  eks_managed_node_group_defaults = {
    instance_types = [var.node_instance_type]
    
    attach_cluster_primary_security_group = true
    
    # Disabling and using externally provided security groups
    create_security_group = false
  }
  
  eks_managed_node_groups = {
    main = {
      name = "main-node-group"
      
      instance_types = [var.node_instance_type]
      
      min_size     = var.min_capacity
      max_size     = var.max_capacity
      desired_size = var.desired_capacity
      
      pre_bootstrap_user_data = <<-EOT
        #!/bin/bash
        /etc/eks/bootstrap.sh ${var.cluster_name}
      EOT
      
      vpc_security_group_ids = [aws_security_group.node_group_one.id]
      
      tags = {
        Environment = "dev"
        Application = "kubeflow"
        NodeGroup   = "main"
      }
    }
  }
  
  # OIDC Provider
  cluster_identity_providers = {
    sts = {
      client_id = "sts.amazonaws.com"
    }
  }
  
  tags = {
    Environment = "dev"
    Project     = "bert-kubeflow"
  }
}

# Security group for EKS nodes
resource "aws_security_group" "node_group_one" {
  name_prefix = "${var.cluster_name}-node-group-"
  vpc_id      = module.vpc.vpc_id
  
  ingress {
    from_port = 22
    to_port   = 22
    protocol  = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr_block]
  }
  
  tags = {
    Name = "${var.cluster_name}-node-group-sg"
  }
}

# ECR Repository for Docker images
resource "aws_ecr_repository" "bert_pipeline" {
  name                 = "bert-pipeline"
  image_tag_mutability = "MUTABLE"
  
  image_scanning_configuration {
    scan_on_push = true
  }
  
  tags = {
    Environment = "dev"
    Project     = "bert-kubeflow"
  }
}

# S3 bucket for model artifacts
resource "aws_s3_bucket" "model_artifacts" {
  bucket = "${var.cluster_name}-model-artifacts-${random_string.bucket_suffix.result}"
  
  tags = {
    Environment = "dev"
    Project     = "bert-kubeflow"
  }
}

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

resource "aws_s3_bucket_versioning" "model_artifacts_versioning" {
  bucket = aws_s3_bucket.model_artifacts.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "model_artifacts_encryption" {
  bucket = aws_s3_bucket.model_artifacts.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# IAM role for Kubeflow Pipelines
resource "aws_iam_role" "kubeflow_pipelines_role" {
  name = "${var.cluster_name}-kubeflow-pipelines-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      },
      {
        Action = "sts:AssumeRoleWithWebIdentity"
        Effect = "Allow"
        Principal = {
          Federated = module.eks.oidc_provider_arn
        }
        Condition = {
          StringEquals = {
            "${replace(module.eks.cluster_oidc_issuer_url, "https://", "")}:sub": "system:serviceaccount:kubeflow:kubeflow-pipelines-api"
            "${replace(module.eks.cluster_oidc_issuer_url, "https://", "")}:aud": "sts.amazonaws.com"
          }
        }
      }
    ]
  })
  
  tags = {
    Environment = "dev"
    Project     = "bert-kubeflow"
  }
}

# IAM policy for Kubeflow Pipelines
resource "aws_iam_policy" "kubeflow_pipelines_policy" {
  name = "${var.cluster_name}-kubeflow-pipelines-policy"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.model_artifacts.arn,
          "${aws_s3_bucket.model_artifacts.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:GetAuthorizationToken"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "sagemaker:CreateTrainingJob",
          "sagemaker:DescribeTrainingJob",
          "sagemaker:StopTrainingJob",
          "sagemaker:CreateModel",
          "sagemaker:CreateEndpointConfig",
          "sagemaker:CreateEndpoint",
          "sagemaker:DescribeEndpoint",
          "sagemaker:UpdateEndpoint",
          "sagemaker:DeleteEndpoint",
          "sagemaker:DeleteEndpointConfig",
          "sagemaker:DeleteModel"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "kubeflow_pipelines_policy_attachment" {
  role       = aws_iam_role.kubeflow_pipelines_role.name
  policy_arn = aws_iam_policy.kubeflow_pipelines_policy.arn
}

# Network Load Balancer for Kubeflow
resource "aws_lb" "kubeflow_nlb" {
  name               = "${var.cluster_name}-kubeflow-nlb"
  internal           = false
  load_balancer_type = "network"
  subnets            = module.vpc.public_subnets
  
  enable_deletion_protection = false
  
  tags = {
    Environment = "dev"
    Project     = "bert-kubeflow"
  }
}

# Target group for Kubeflow UI
resource "aws_lb_target_group" "kubeflow_ui" {
  name     = "${var.cluster_name}-kubeflow-ui"
  port     = 80
  protocol = "TCP"
  vpc_id   = module.vpc.vpc_id
  
  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }
  
  tags = {
    Environment = "dev"
    Project     = "bert-kubeflow"
  }
}

# Listener for NLB
resource "aws_lb_listener" "kubeflow_ui" {
  load_balancer_arn = aws_lb.kubeflow_nlb.arn
  port              = "80"
  protocol          = "TCP"
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.kubeflow_ui.arn
  }
}

# Output values
output "cluster_id" {
  description = "EKS cluster ID"
  value       = module.eks.cluster_id
}

output "cluster_arn" {
  description = "EKS cluster ARN"
  value       = module.eks.cluster_arn
}

output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks.cluster_endpoint
}

output "cluster_security_group_id" {
  description = "Security group ids attached to the cluster control plane"
  value       = module.eks.cluster_security_group_id
}

output "kubectl_config" {
  description = "kubectl config as generated by the module"
  value = yamlencode({
    apiVersion      = "v1"
    kind            = "Config"
    current-context = "terraform"
    clusters = [{
      name = module.eks.cluster_id
      cluster = {
        certificate-authority-data = module.eks.cluster_certificate_authority_data
        server                     = module.eks.cluster_endpoint
      }
    }]
    contexts = [{
      name = "terraform"
      context = {
        cluster = module.eks.cluster_id
        user    = "terraform"
      }
    }]
    users = [{
      name = "terraform"
      user = {
        token = data.aws_eks_cluster_auth.cluster.token
      }
    }]
  })
  sensitive = true
}

output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.bert_pipeline.repository_url
}

output "s3_bucket_name" {
  description = "S3 bucket for model artifacts"
  value       = aws_s3_bucket.model_artifacts.bucket
}

output "load_balancer_dns" {
  description = "Load balancer DNS name"
  value       = aws_lb.kubeflow_nlb.dns_name
}

# Data source for EKS cluster auth
data "aws_eks_cluster_auth" "cluster" {
  name = module.eks.cluster_id
}
