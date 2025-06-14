# Amazon Web Services (AWS)

What are the services in AWS?

Some of the key services categories in AWS include:

Compute: 
 
 EC2, Lambda, Elastic Beanstalk, and Lightsail that provide scalable computing capacity and serverless options to run applications.  
 
Storage: 
 
 S3, EFS, and Glacier that offer object, file and archive storage with high durability and availability.  
 
Databases: 
 
 RDS, DynamoDB, ElastiCache, Neptune, and Timestream for relational, NoSQL, in-memory, and time series data.  
 
Networking: 
 
 VPC, Direct Connect, and Route 53 that provide networking capabilities and connectivity options for resources.  
 
Analytics: 

 EMR, Athena, Kinesis, and QuickSight that enable big data analytics and insights from data.  
 
Security: 
 
 IAM, GuardDuty, Inspector, Macie that provide identity management, threat detection, security assessments, and data security.  
 
Management Tools: 
 
CloudWatch, CloudTrail, Config, OpsWorks, and Service Catalog that enable governance, auditing, automation and management of AWS resources.

## Create an AWS account

How to sign up for an AWS account?

If you do not have an AWS account, complete the following steps to create one.

1. To sign up for an AWS account

Open [signup](https://portal.aws.amazon.com/billing/signup) page.

2. Follow the online instructions.

Part of the sign-up procedure involves receiving a phone call and entering a verification code on the phone keypad.

When you sign up for an AWS account, an AWS account root user is created. 

The root user has access to all AWS services and resources in the account. 

AWS sends you a confirmation email after the sign-up process is complete. 

Start building on AWS

Creating [an account](https://aws.amazon.com/resources/create-account/) is the starting point to provide access to AWS.

3. Secure your AWS account root user

After you sign up for an AWS account, secure your AWS account root user, enable AWS IAM Identity Center, and create an administrative user so that you don't use the root user for everyday tasks.

4. Trying Free Tier services

Instances, containers, and serverless computing for free of charge on AWS.

Navigate to the  [AWS Free Tier](http://aws.amazon.com/free/) page.

## Managing and deploying applications in the AWS cloud environment.

Deploying and managing applications on AWS can be accomplished through various services such as Elastic Beanstalk, CodeDeploy, and App Runner. 

Elastic Beanstalk provides a managed platform for deploying and managing Go applications, while CodeDeploy offers automated deployments, and App Runner is a container-based service for deploying applications without managing infrastructure.

1. Using AWS Elastic Beanstalk:

AWS Elastic Beanstalk automates the process of deploying and managing applications, allowing you to focus on your code rather than infrastructure.

Prerequisites: Create an AWS account and set up your Go development environment.

Deployment: You can deploy Go applications to Elastic Beanstalk using the EB CLI or the AWS Management Console.

Management: Elastic Beanstalk provides tools to manage your application, including monitoring, logging, and scaling.

2. Using AWS CodeDeploy:

Deployment: CodeDeploy automates deployments to Amazon EC2 instances, on-premises instances, and other AWS services.

Management: CodeDeploy offers features like blue/green deployments, canary deployments, and rollback capabilities.

Integration: CodeDeploy can be integrated with CI/CD systems like GitHub Actions.

3. Using AWS App Runner:

Deployment: App Runner simplifies deployment by handling infrastructure management for containerized applications.

Management: App Runner provides features like automatic scaling, monitoring, and integration with other AWS services.

Go Runtime: App Runner supports Go applications, and you can configure build and run commands.

4. Additional considerations:

AWS SDK for Go:

To deploy an application using the AWS SDK, you need to configure your SDK with credentials and region, establish a session or client for AWS services, and then use the SDK's API calls to interact with AWS resources.

You can deploy your application using different AWS services like EC2, CodeDeploy, Lambda, or Elastic Beanstalk.

Utilize the AWS SDK for Go to interact with AWS services from within your Go applications.

Docker:

Packaging your Go application in a Docker container can simplify deployment and management on AWS.

Infrastructure as Code (IaC):

IaC tools allow you to automate the deployment process, ensuring consistency and repeatability.

Tools like CloudFormation and AWS CDK can be used to provision and manage your AWS infrastructure.

### Learn to deploy and manage AWS applications using Infrastructure as Code tools like CloudFormation.

To deploy and manage applications on AWS using Infrastructure as Code (IaC), you can leverage AWS CloudFormation and AWS CDK. 

CloudFormation enables you to define and manage AWS infrastructure using declarative JSON or YAML templates, while CDK provides a framework for describing infrastructure using familiar programming languages.

1. Using AWS CloudFormation:

Define Infrastructure:

Write a CloudFormation template that describes the AWS resources (e.g., EC2 instances, S3 buckets, databases) needed for your application.

Deploy Infrastructure:

Upload the template to CloudFormation and initiate the deployment process.

CloudFormation will create and configure the resources as specified in the template.

Manage Changes:

Modify the template and re-deploy to update or add resources. CloudFormation automatically manages the changes, ensuring the desired infrastructure state.

2. Using AWS CDK:

Install and Initialize:

Install the CDK and create a new project.

Define Resources:

Write code (e.g., Go, Python or TypeScript) to define the AWS resources required by your application.

Synthesize Template:

Run the cdk synth command to generate a CloudFormation template from your CDK code.

Deploy Infrastructure:

Run the cdk deploy command to deploy the generated template and provision the infrastructure.

Manage Changes:

Edit the code, synthesize a new template, and redeploy to make changes to the infrastructure. 

### Example: Deploying to Elastic Beanstalk

1. Create a Go application: Write your Go application and package it for deployment.

2. Install the EB CLI: Install the Elastic Beanstalk Command Line Interface.

3. Configure the EB CLI: Configure the EB CLI with your AWS credentials.

4. Deploy your application: Use the eb deploy command to deploy your application to an Elastic Beanstalk environment.

![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/JWT/JWT.png?raw=true)

### Example: Deploying Golang (Go) backend application with Docker container on AWS

Terraform as your IaC tool: 

You'll write Terraform code to define your infrastructure, including the VPC, subnets, RDS database, ELB, and ECS cluster, tasks, and services.

ECS for container orchestration: 

ECS will manage your containerized web application, running it on either Fargate (serverless) or EC2 instances.

Choose between ECS Fargate (serverless) or ECS with EC2 instances. 

Fargate simplifies management as AWS handles the underlying infrastructure.

RDS for your database: 

Terraform can provision and configure your RDS database instance to store your web application's data.

ELB for load balancing: 

An Application Load Balancer (ALB) or Network Load Balancer (NLB) can be provisioned via Terraform to distribute traffic to your ECS tasks, ensuring scalability and high availability.

VPC for network isolation: 

A VPC with public and private subnets will provide a secure and isolated network environment for your application.

S3 for Storage: 

You can use S3 to store your Terraform state files, provide storage for the web application, or other static assets. 

CloudFront: 

A content delivery network (CDN) that helps you distribute your static and dynamic web content to users.

IAM (Identity and Access Management): 

Create IAM roles and policies to grant necessary permissions to your ECS tasks to access other AWS services like ECR, RDS, and S3. 

Deploying a Golang backend application on AWS with ECS, Fargate, RDS, ELB, VPC, S3, CloudFront, Route53, and Terraform requires following essential steps. 

1. Developing the Golang Application

Build your backend application: 

Create your Golang project, focusing on core logic, API endpoints, and database interactions.

Connect to RDS: 

Integrate your application with an AWS RDS database, handling database connections and queries within your Go code.

2. Containerizing the Application with Docker

Create a Dockerfile: 

Write a Dockerfile to define the environment for your Golang application, including the base image, dependencies, and build commands.

Build the Docker image: 

Use the docker build command to build the Docker image based on your Dockerfile.

Tag the image: 

Tag the image appropriately, including the ECR repository URI for easy identification.

3. Deploying to AWS with Terraform

Set up Terraform: 

Ensure you have Terraform installed and configured to interact with your AWS account.

Define AWS resources with Terraform: 

Create Terraform configuration files (e.g., .tf files) to define and manage the following AWS resources:

VPC: 

Define your Virtual Private Cloud (VPC) for network isolation.

Subnets: 

Create subnets within your VPC to segregate resources.

Internet Gateway: 

Configure an Internet Gateway to allow external access to resources within your VPC.

Route Tables: 

Set up route tables to control network traffic within your VPC.

Security Groups: 

Define security groups to control inbound and outbound traffic for your resources.

ECR Repository: 

Create an Amazon Elastic Container Registry (ECR) repository to store your Docker images.

ECS Cluster: 

Create an ECS cluster to manage your containerized applications.

Task Definition: 

Define an ECS Task Definition to specify the container image, resource requirements (CPU and memory), and other configuration for your application.

ECS Service: 

Create an ECS Service to run and manage your application tasks, ensuring the desired number of tasks are running.

Application Load Balancer (ALB): 

Configure an ALB to distribute incoming traffic across your application tasks.

Route53: 

Set up Route53 to manage your domain name and point it to your ALB.

CloudFront: 

Integrate CloudFront for content delivery and caching, improving performance and reducing latency.

RDS Database: 

Provision an RDS database instance for your application's data storage.

S3 Bucket: 

Create an S3 bucket to store static assets or other application data.

Apply Terraform configuration: 

Run terraform init, terraform plan, and terraform apply to provision the AWS infrastructure defined in your Terraform files.

4. Building and pushing Docker image to ECR:

Build the Docker image: 

Follow the steps in section 2 to build your Docker image.

Authenticate with ECR: 

Authenticate your Docker client with your ECR repository.

Push the image to ECR: 

Use the docker push command to push your Docker image to the ECR repository.

5. Deploying and managing the application:

Update the ECS Service: 

Update your ECS Service to use the new task definition with the updated Docker image.

Monitor and scale: 

Utilize CloudWatch for monitoring your application and configure auto-scaling policies to handle changes in traffic load.

Considerations

IAM Roles: 

Configure appropriate IAM roles for your EC2 instances and ECS tasks to grant necessary permissions to interact with other AWS services.

Security Groups: 

Define security groups to control inbound and outbound traffic to your application, ensuring only necessary ports are open.

HTTPS: 

Implement HTTPS for secure communication by using an ALB with an ACM certificate.

CI/CD pipeline: 

Setting up a CI/CD pipeline using services like GitHub Actions or AWS CodePipeline to automate the build, testing, and deployment process.

Logging and Monitoring: 

Integrate CloudWatch for logging and monitoring your application's performance and health.

References

Sign up for AWS

https://signin.aws.amazon.com/signup?request_type=register


