variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "db_password" {
  description = "Password for the RDS instance"
  type        = string
  sensitive   = true
}