# Deploying a Go application to ECS (Elastic Container Service) using Fargate

ECS is a container orchestration service that manages the deployment, scaling, and management of Docker containers on AWS. 

Fargate is a compute engine for ECS that allows you to run containers without managing the underlying EC2 instances or clusters. 

Fargate's serverless, meaning AWS handles the infrastructure, so you only pay for the resources your containers consume.

## Example: Go application to run on Docker container deployed on AWS 

1. Write your Go application

Go

[main.go](https://github.com/jylhakos/InternetOfThings/blob/main/Languages/Golang/ECS/main.go)

Handlers

[handlers.go](https://github.com/jylhakos/InternetOfThings/blob/main/Languages/Golang/ECS/handlers.go)

Models

[models.go](https://github.com/jylhakos/InternetOfThings/blob/main/Languages/Golang/ECS/models.go)

2. Create a Dockerfile and Dockerize

This file will define how your Go application is built into a Docker image. 

Dockerfile will specify the base image (e.g., golang:latest), copy your application code, install dependencies, build the application, and expose the port your API listens on. 

```

    # Use an official Go runtime as a parent image
    FROM golang:latest
    
    # Set the working directory in the container
    WORKDIR /app
    
    # Copy the source code into the container
    COPY . .
    
    # Download all the dependencies.
    RUN go mod download
    
    # Build the Go application
    RUN go build -o main .
    
    # Expose port 8080 to the outside world
    EXPOSE 8080
    
    # Command to run the executable
    CMD ["/app/main"]

```
Build the Docker image:

Use the docker build command to build your Docker image locally. For example: docker build -t my-go-app .

Push the Docker image to a container registry:

You'll need to push your Docker image to a container registry like Amazon Elastic Container Registry (ECR) or Docker Hub.

2. Set up your AWS infrastructure

Create a Virtual Private Cloud (VPC):

Define a VPC with public and private subnets, internet gateways, and route tables to isolate your application and database.

Set up Route 53:

Configure a hosted zone and record sets to map your domain name to your application's endpoint.

Create an RDS PostgreSQL instance:

Provision a PostgreSQL database instance within your VPC, ensuring it's not publicly accessible.

Set up IAM roles:

Define IAM roles for ECS tasks and ECS execution to grant permissions for accessing other AWS resources, like RDS and ECR. 

Create an ECS cluster:

Create an ECS cluster, which will be the environment where your application runs.

Create a Fargate profile:

Define a Fargate profile to specify the VPC and subnets where your Fargate tasks will run, ensuring they are within your VPC. 

3. Configure ECS and deploy with Fargate

Create a task definition:

This definition specifies the Docker image to use, the resources (CPU and memory) required, the port mappings, and the IAM role for the task.

Define a service:

Create an ECS service, which manages the desired number of tasks and ensures they are running correctly. You can use Fargate as the launch type for your service.

Configure service discovery (optional):

You can use AWS Cloud Map or Application Load Balancer for service discovery, allowing other services to easily find your Go application.

Deploy your Go application:

Deploy your ECS service. ECS and Fargate will handle the deployment, scaling, and management of your Go application within your VPC. 

## Deploying a Go application to AWS with Terraform, RDS, VPC, Route53, ECS, and Fargate

Deploying a Go application to AWS using Terraform, RDS, VPC, Route53, ECS, and Fargate involves the following steps:

1. Go, AWS and Terraform project setup

Go Application: 

Write a Go application

Dockerize the Go Application: 

Create a Dockerfile that packages your Go application and its dependencies into a Docker image. 

You can use multi-stage builds to optimize the image size for production.

Version Control: 

Store your Go application code and Terraform configurations in a version control system like Git.

AWS CLI: 

Install and configure the AWS Command Line Interface (CLI) on your Linux machine to interact with AWS services.

Terraform: 

Install Terraform on your Linux machine.

2. AWS Infrastructure with Terraform

AWS Provider Configuration: 

Configure the AWS provider in your Terraform files to authenticate with your AWS account.

VPC (Virtual Private Cloud): Define a VPC in your Terraform code to create an isolated network for your application. 

Include public and private subnets within different Availability Zones for high availability.

RDS (Relational Database Service):

Create an RDS instance within the private subnet of your VPC to host your database.

Configure a subnet group for your RDS instance within the VPC.

Define security groups to control access to the RDS instance, allowing access only from your application's security group.

ECS (Elastic Container Service) Cluster:

Create an ECS cluster to manage your containerized Go application.

Define an ECS task definition, specifying the Docker image for your Go application, required resources (CPU, memory), and network mode (use awsvpc for Fargate).

Fargate: 

Use Fargate as the compute engine for your ECS tasks. This eliminates the need to provision and manage EC2 instances.

ECR (Elastic Container Registry):

Create an ECR repository to store your Go application's Docker image.

Build and push the Docker image to the ECR repository.

Route53:

Configure Route53 to manage your domain name.

Create a hosted zone for your domain.

Use Service Discovery to automatically create DNS records for your ECS service.

Load Balancer (Optional):

Provision an Application Load Balancer (ALB) in your public subnets to distribute incoming traffic to your ECS tasks.

Configure listeners and target groups to route traffic to the appropriate containers.

3. Deployment with Terraform

Initialize Terraform: 

Run terraform init in your project directory to set up the Terraform environment and download necessary plugins.

Review plan: 

Execute terraform plan to see the proposed infrastructure changes before applying them.

Apply configuration: 

Apply the Terraform configuration with terraform apply --auto-approve to create and configure the AWS resources.


## Deploying a Flutter and Dart application to AWS

Deploying a Flutter web application to AWS with S3 involves preparing the application for web deployment, configuring an S3 bucket for hosting, and uploading the built application files.

1. Prepare Your Flutter Web application

Enable Web support: 

Ensure your Flutter project has web support enabled. 

If not, add it using the command: 

```

	$ flutter create . 

```

(in your project directory).

Build for production: 

Generate a production-ready build of your Flutter web app using the command: 

```

	$ flutter build web --release

```

This command creates a build/web folder containing the optimized web files.

Optional: 

Integrate AWS SDK (if your app needs to interact with S3):

Add the aws_sdk_flutter or flutter_aws_s3_client package to your pubspec.yaml file.

Run flutter pub get to install the dependencies.

Configure and initialize the AWS SDK within your Flutter application, including setting your access key, secret key, and region.

Use the SDK's methods to upload or retrieve files from your S3 bucket as needed.

2. Configure Your AWS S3 bucket

Create an S3 bucket:

Log in to the AWS Management Console and navigate to the S3 service.

Click "Create bucket" and provide a unique name and select a region.

Enable Static Website Hosting:

Go to the Properties tab of your bucket and enable Static website hosting.

Specify index.html as the index document.

Configure Bucket Policy for public access:

By default, S3 buckets are private. 

To make your web app accessible, you need to configure a bucket policy that grants public read access to your objects.

In the bucket's Permissions tab, edit the Bucket policy and add a policy like the one shown in the search results to allow public access to s3:GetObject actions on your bucket's objects.

3. Deploy the Flutter Web application

Upload Build Files: 

Upload the contents of the build/web folder (from the Flutter build step) to your S3 bucket. You can use the AWS CLI, the AWS Management Console, or other tools for this purpose.

Access the Deployed App: 

Once the files are uploaded, you can access your Flutter web application using the S3 website endpoint provided in the bucket's Static website hosting properties. 

4. Optional

Use CloudFront for content delivery: 

For improved performance and security, consider distributing your web app using Amazon CloudFront.


