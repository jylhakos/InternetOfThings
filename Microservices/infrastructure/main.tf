provider "aws" {
  region = var.aws_region
}

# ECS Cluster
resource "aws_ecs_cluster" "microservices_cluster" {
  name = "microservices-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# Application Load Balancer
resource "aws_lb" "api_gateway" {
  name               = "microservices-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = false
}

# API Gateway (AWS API Gateway)
resource "aws_api_gateway_rest_api" "microservices_api" {
  name        = "microservices-api"
  description = "API Gateway for microservices"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# Lambda function for serverless deployment
resource "aws_lambda_function" "product_service" {
  filename         = "product-service.zip"
  function_name    = "product-service"
  role            = aws_iam_role.lambda_role.arn
  handler         = "main"
  runtime         = "go1.x"
  timeout         = 30

  environment {
    variables = {
      ETCD_ENDPOINTS = aws_instance.etcd.private_ip
    }
  }
}

# Service Discovery with AWS Cloud Map
resource "aws_service_discovery_private_dns_namespace" "microservices" {
  name        = "microservices.local"
  description = "Private DNS namespace for microservices"
  vpc         = aws_vpc.main.id
}

resource "aws_service_discovery_service" "product_service" {
  name = "product-service"

  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.microservices.id

    dns_records {
      ttl  = 10
      type = "A"
    }

    routing_policy = "MULTIVALUE"
  }

  health_check_grace_period_seconds = 30
}