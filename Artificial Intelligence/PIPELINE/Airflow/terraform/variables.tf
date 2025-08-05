# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "bert-fine-tuning"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "key_pair_name" {
  description = "EC2 Key Pair name for SSH access"
  type        = string
  default     = "your-key-pair"
}

# Outputs
output "mwaa_webserver_url" {
  description = "MWAA Webserver URL"
  value       = aws_mwaa_environment.bert_airflow.webserver_url
}

output "sagemaker_endpoint_name" {
  description = "SageMaker Endpoint Name"
  value       = aws_sagemaker_endpoint.bert_endpoint.name
}

output "api_gateway_invoke_url" {
  description = "API Gateway Invoke URL"
  value       = aws_api_gateway_deployment.bert_api_deployment.invoke_url
}

output "ollama_alb_dns_name" {
  description = "Ollama Application Load Balancer DNS Name"
  value       = aws_lb.ollama_alb.dns_name
}

output "s3_bucket_name" {
  description = "S3 Bucket for MWAA"
  value       = aws_s3_bucket.mwaa_bucket.bucket
}
