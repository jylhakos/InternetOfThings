# Amazon ECS (Elastic Container Service)

Amazon Elastic Container Service (Amazon ECS) is a container orchestration service that helps you deploy, manage, and scale containerized applications.

## Example: Terraform, Docker and ECS

How to use Terraform with Golang application deployed with Docker on AWS with ECS?

You can use Terraform and AWS ECS together to deploy a web application utilizing various AWS services like RDS, ELB, VPC, and S3.

ECS for container orchestration:

ECS will manage your containerized web application, running it on either Fargate (serverless) or EC2 instances.

ELB for load balancing:

An Application Load Balancer (ALB) or Network Load Balancer (NLB) can be provisioned via Terraform to distribute traffic to your ECS tasks, ensuring scalability and high availability.

VPC for network isolation: 

A defined VPC with public and private subnets will provide a secure and isolated network environment for your application.

S3 for storage:

You can use S3 to store your Terraform state files, provide storage for the web application, or other static assets. 

RDS for your database: 

Terraform can provision and configure your RDS database instance to store your web application's data.

Here's steps for deploying a Go application on AWS ECS with Docker and Terraform.

1. Prerequisites

AWS Account: 

You need an active AWS account.

Terraform: 

Install Terraform CLI on your local machine.

AWS CLI: 

Install and configure the AWS CLI with necessary credentials.

Docker: 

Install Docker on your local machine.

Go: 

Create a Go application and a Dockerfile to containerize it.

Build your backend application: 

Create your Golang project, focusing on core logic, API endpoints, and database interactions.

Connect to RDS: 

Integrate your application with an AWS RDS database, handling database connections and queries within your Go code. 

Create a Dockerfile: 

Write a Dockerfile to define the environment for your Golang application, including the base image, dependencies, and build commands.

Dockerize the Go application:

Create a Dockerfile in your Go project directory:

```

FROM golang:1.22-alpine
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go build -o main .
EXPOSE 8080
CMD ["./main"]

```

Build the Docker image: 

Use the docker build command to build the Docker image based on your Dockerfile.

```

$ docker build -t your-app-image .

```

Tag the image: 

Tag the image appropriately, including the ECR repository URI for easy identification. 

2. Setting up the environment

IAM User:

Create an IAM user with programmatic access and necessary permissions for Terraform to manage resources. 

Assign admin group to the user for simplicity.

Docker Image:

Build your Docker image using docker build -t <your-image-name> . and push it to a repository like ECR.

Building and pushing Docker image to ECR:

Build the Docker image: 

Follow the steps to build your Docker image.

Authenticate with ECR: 

Authenticate your Docker client with your ECR repository.

Push the image to ECR: 

Use the docker push command to push your Docker image to the ECR repository. 

3. Terraform configuration

Set up Terraform: 

Ensure you have Terraform installed and configured to interact with your AWS account.

Define AWS resources with Terraform: 

Create a directory for your Terraform files (e.g., terraform-aws-go-app) to define and manage AWS resources and within it, create a file called main.tf.

Here's an example Terraform configuration:

```

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "your-aws-region" # e.g., "us-east-1"
}

resource "aws_instance" "app_server" {
  ami           = "ami-xxxxxxxxxxxxx"  # Replace with your desired AMI ID
  instance_type = "t2.micro" # Or any instance type
  key_name      = "your-key-pair" # Name of your EC2 key pair
  tags = {
    Name = "go-app-server"
  }
  user_data = <<-EOF
              #!/bin/bash
              sudo apt update
              sudo apt install -y docker.io
              sudo systemctl start docker
              sudo docker run -d -p 8080:8080 your-app-image
              EOF
}


```

Provider: 

Configure the AWS provider in your Terraform files.

VPC: 

Set up your VPC, subnets, and security groups.

ECS Cluster: 

Create an ECS cluster to manage your containerized applications.

Task Definition: 

Define the task definition with your Docker image, CPU, memory, and port mappings.

Service: 

Create an ECS service to run the tasks.

Load Balancer: 

Optionally, set up a load balancer to distribute traffic.

Route Tables: 

Set up route tables to control network traffic within your VPC.


4. Terraform Workflow

Initialization: 

Run terraform init to initialize your Terraform project.

Navigate to your Terraform directory in the terminal and run:

```

$ terraform init

```
This downloads the necessary AWS provider plugins.

Planning: 

Run terraform plan to preview the changes.

Application: 

Run terraform apply to create to create an execution plan for the infrastructure on AWS.

```

$ terraform plan

$ terraform apply

```

Once Terraform finishes, it will output the public IP address of the EC2 instance.

Access your application in the browser using http://<your-ec2-public-ip>:8080.

References

What is Amazon Elastic Container Service?

https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html

![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/JWT/JWT.png?raw=true)
