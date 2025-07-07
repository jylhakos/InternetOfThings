# AWS Infrastructure for LLM Chat Service using Terraform

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
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
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "m5.xlarge"
}

variable "key_pair_name" {
  description = "EC2 Key Pair name"
  type        = string
  default     = "llm-chat-key"
}

variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to access the application"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# VPC
resource "aws_vpc" "llm_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "llm-chat-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "llm_igw" {
  vpc_id = aws_vpc.llm_vpc.id

  tags = {
    Name = "llm-chat-igw"
  }
}

# Public Subnet
resource "aws_subnet" "llm_public_subnet" {
  count                   = 2
  vpc_id                  = aws_vpc.llm_vpc.id
  cidr_block              = "10.0.${count.index + 1}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "llm-chat-public-subnet-${count.index + 1}"
  }
}

# Route Table
resource "aws_route_table" "llm_public_rt" {
  vpc_id = aws_vpc.llm_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.llm_igw.id
  }

  tags = {
    Name = "llm-chat-public-rt"
  }
}

# Route Table Association
resource "aws_route_table_association" "llm_public_rta" {
  count          = 2
  subnet_id      = aws_subnet.llm_public_subnet[count.index].id
  route_table_id = aws_route_table.llm_public_rt.id
}

# Security Group
resource "aws_security_group" "llm_sg" {
  name_prefix = "llm-chat-sg"
  vpc_id      = aws_vpc.llm_vpc.id

  # SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  # HTTP (Spring Boot)
  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  # Ollama
  ingress {
    from_port   = 11434
    to_port     = 11434
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  # HTTPS
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  # HTTP
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "llm-chat-security-group"
  }
}

# IAM Role for EC2 Instance
resource "aws_iam_role" "llm_ec2_role" {
  name = "llm-chat-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for CloudWatch Logs
resource "aws_iam_role_policy" "llm_cloudwatch_policy" {
  name = "llm-chat-cloudwatch-policy"
  role = aws_iam_role.llm_ec2_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Instance Profile
resource "aws_iam_instance_profile" "llm_profile" {
  name = "llm-chat-instance-profile"
  role = aws_iam_role.llm_ec2_role.name
}

# User Data Script
locals {
  user_data = base64encode(templatefile("${path.module}/user-data.tpl", {
    aws_region = var.aws_region
  }))
}

# EC2 Instance
resource "aws_instance" "llm_instance" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = var.instance_type
  key_name              = var.key_pair_name
  vpc_security_group_ids = [aws_security_group.llm_sg.id]
  subnet_id             = aws_subnet.llm_public_subnet[0].id
  iam_instance_profile  = aws_iam_instance_profile.llm_profile.name
  user_data             = local.user_data

  root_block_device {
    volume_size = 50
    volume_type = "gp3"
    encrypted   = true
  }

  tags = {
    Name = "llm-chat-service"
  }
}

# Application Load Balancer
resource "aws_lb" "llm_alb" {
  name               = "llm-chat-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.llm_sg.id]
  subnets            = aws_subnet.llm_public_subnet[*].id

  enable_deletion_protection = false

  tags = {
    Name = "llm-chat-alb"
  }
}

# Target Group
resource "aws_lb_target_group" "llm_tg" {
  name     = "llm-chat-tg"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = aws_vpc.llm_vpc.id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/actuator/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = {
    Name = "llm-chat-target-group"
  }
}

# Target Group Attachment
resource "aws_lb_target_group_attachment" "llm_tg_attachment" {
  target_group_arn = aws_lb_target_group.llm_tg.arn
  target_id        = aws_instance.llm_instance.id
  port             = 8080
}

# ALB Listener
resource "aws_lb_listener" "llm_listener" {
  load_balancer_arn = aws_lb.llm_alb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.llm_tg.arn
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "llm_logs" {
  name              = "/aws/ec2/llm-chat-service"
  retention_in_days = 7

  tags = {
    Name = "llm-chat-logs"
  }
}

# Outputs
output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.llm_instance.public_ip
}

output "load_balancer_dns" {
  description = "DNS name of the load balancer"
  value       = aws_lb.llm_alb.dns_name
}

output "application_url" {
  description = "URL to access the application"
  value       = "http://${aws_lb.llm_alb.dns_name}"
}

output "ssh_command" {
  description = "SSH command to connect to the instance"
  value       = "ssh -i ${var.key_pair_name}.pem ec2-user@${aws_instance.llm_instance.public_ip}"
}
