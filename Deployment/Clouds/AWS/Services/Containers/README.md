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

Terraform Integration:

You can easily define and provision your ECS with Fargate infrastructure using Terraform, ensuring consistent and repeatable deployments. 


![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/JWT/JWT.png?raw=true)
 