# An application on Docker container deployed to AWS

ECS (Elastic Container Service):

ECS is a container orchestration service that manages the deployment, scaling, and management of Docker containers on AWS. 

Fargate:

Fargate is a compute engine for ECS that allows you to run containers without managing the underlying EC2 instances or clusters. 

Fargate's serverless, meaning AWS handles the infrastructure, so you only pay for the resources your containers consume.

## Amazon ECS with Fargate

For deploying a Go program with Docker on AWS, using Amazon ECS with Fargate is recommended as Fargate offers a serverless compute engine, simplifying infrastructure management, especially when used with Terraform for automation.

Why ECS with Fargate is a good choice for Go programs?

Simplified Infrastructure Management:

Fargate abstracts away the complexities of managing EC2 instances, allowing you to focus on your application code.

Serverless Compute:

Fargate's serverless nature means you only pay for the resources your containers consume, making it cost-effective for many workloads.

Integration with ECS:

Fargate is designed to work seamlessly with ECS, providing a robust container orchestration platform.

Terraform integration:

You can easily define and provision your ECS with Fargate infrastructure using Terraform, ensuring consistent and repeatable deployments. 

## Example: Go handler function for AWS ECS and Fargate with Terraform

This steps details how to create a Go handler on AWS ECS and Fargate, with the Infrastructure as Code (VPC, Route53, S3, RDS, IAM roles) orchestrated by Terraform.

1. Create your Go handler

Prerequisites commands:

Install AWS CLI (if not already installed):

```

	$ curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
	$ unzip awscliv2.zip
	$ sudo ./aws/install

```

Configure AWS credentials:

```

	$ aws configure

```

Project structure: 

Create a project directory and a basic Go handler. 

```

	$ go mod init go-fargate-server

```

The content of go.mod file:

```

	module go-fargate-server

	go 1.24.4

```

For example "Hello World" or HTTP handler is a good starting point.

The content of main.go file:

```

	package main

	import (
	    "fmt"
	    "net/http"
	)

	func handler(w http.ResponseWriter, r *http.Request) {
	    fmt.Fprintf(w, "Hello from Go on Fargate!")
	}

	func main() {
	    http.HandleFunc("/", handler)
	    fmt.Println("Server listening on port 8080.")
	    // Change the port if needed
	    http.ListenAndServe(":8080", nil) 
	}

```

2. Docker commands to create Docker image

Containerize your Go application: 

Create a Dockerfile to containerize your Go application.

The content of Dockerfile file:


```

	FROM golang:1.21-alpine AS builder

	# Set the working directory inside the container
	WORKDIR /app

	# Copy go.mod and go.sum files
	COPY go.mod go.sum ./

	# Download dependencies
	RUN go mod download

	# Copy the source code
	COPY . .

	# Build the Go application
	RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

	# Use a minimal image for the final stage
	FROM alpine:latest

	# Install ca-certificates for HTTPS requests
	RUN apk --no-cache add ca-certificates

	# Set the working directory
	WORKDIR /root/

	# Copy the binary from the builder stage
	COPY --from=builder /app/main .

	# Expose port 8080
	EXPOSE 8080

	# Run the application
	CMD ["./main"]

```

Build and push: 

Build the Docker image and push it to Amazon Elastic Container Registry (ECR). 

You'll need to create an ECR repository first.

Create ECR repository:

```

	# Set your AWS region and repository name
	$ export AWS_REGION=us-east-1
	$ export ECR_REPO_NAME=my-go-app

	# Create ECR repository
	$ aws ecr create-repository --repository-name $ECR_REPO_NAME --region $AWS_REGION

```

Replace us-east-1 with your preferred AWS region.

Replace my-go-app with your desired repository name.

Ensure you have the necessary AWS permissions for ECR operations.

Get ECR Login Token:

```

	# Get the login token and authenticate Docker to ECR
	$ aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com

```

Build the Docker image:

```

	$ docker build -t $ECR_REPO_NAME .

```

Set a tag for the Docker image:

```

	# Get your AWS account ID
	$ export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

	# Tag the image for ECR
	$ docker tag $ECR_REPO_NAME:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest

```

Test the Docker image locally before pushing to ECR:

```

	$ docker run -p 8080:8080 $ECR_REPO_NAME:latest

```

Push the Docker image to ECR:

```

	# Push the image to ECR
	$ docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest

```

List ECR repositories:

```

	$ aws ecr describe-repositories --region $AWS_REGION

```
List images in ECR repository:

```

	$ aws ecr list-images --repository-name $ECR_REPO_NAME --region $AWS_REGION

```

Delete ECR repository:

```

	$ aws ecr delete-repository --repository-name $ECR_REPO_NAME --region $AWS_REGION --force

```

3. Configure Terraform for AWS infrastructure

Project structure: 

Organize your Terraform files within a dedicated directory.

Provider Configuration (provider.tf): 

Specify the AWS provider and region.

Variables (variables.tf and terraform.tfvars): 

Define variables for customization (e.g., environment, VPC CIDR).

VPC and Networking (network.tf): 

Define the VPC, subnets, and associated resources.

Security Groups (security.tf): 

Define security groups to control traffic to your Fargate task.

ECS Cluster and Service (ecs.tf): 

Define the ECS cluster, task definition (referencing your ECR image), and ECS service (using Fargate launch type).

Application Load Balancer (alb.tf): Define an Application Load Balancer (ALB) and associated target group to route traffic to your service.

Route53 (route53.tf): 

If required, define Route53 records to map a domain name to your ALB.

S3 (s3.tf): 

Define S3 buckets for storing Terraform state or application data.

RDS (rds.tf): 

Define an RDS database instance if your application requires a database.

IAM Roles (iam.tf): 

Define IAM roles for the ECS task execution and task role. Refer to AWS documentation for recommended roles.

Terraform backend: 

Configure a backend (e.g., S3) to store your Terraform state, especially for collaboration.

Initialize and apply: 

Run terraform init to download necessary providers and modules. Then, run terraform apply to provision the infrastructure. 

Grant executable permissions to the bash script for deploying the Docker image to ECR using Terraform.

```
	$ chmod +x deploy.sh

```

![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/JWT/JWT.png?raw=true)
 