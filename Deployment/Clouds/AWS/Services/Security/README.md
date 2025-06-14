# Security

To secure REST APIs connecting to back-end services on AWS, various strategies can be implemented, mainly by leveraging Amazon API Gateway alongside other AWS services.

API Gateway serves as the entry point for your APIs, enabling you to manage access, regulate traffic, and implement security measures.

Below is an overview of typical methods to secure your APIs.

## API keys

API keys act as a form of authentication, allowing API Gateway to identify and authorize requests from different clients.

API keys work well for internal services or APIs where client authentication security is not a top priority.

API keys are not recommended as the main authentication method for public APIs by AWS due to significant security concerns.

In production environments, it's advisable to use more secure authentication methods like IAM roles.

Concept: 

API keys provide a way to identify and authenticate API clients.

Implementation: 

You can create API keys within API Gateway and associate them with usage plans that define usage limits and throttling.

When a client makes a request, they must include the API key in the header. API Gateway then validates the key against the configured usage plan.

How to implement API keys in API Gateway?

Console:

You can configure API keys through the AWS API Gateway console.

To set up API keys, navigate to API Keys in the main navigation pane.

Resources:

Navigate to your REST API, choose the desired method, and configure it to require an API key.

Choose Create API key, give it a name and description, and either auto-generate a key or create your own.

Usage plans:

Create usage plans to define the rate limits and quotas for API usage associated with specific API keys.

Deployment:

After configuring API keys and usage plans, deploy or redeploy your API for the changes to take effect.

## IAM users, roles, policies and secrets

AWS Identity and Access Management (IAM), a service for managing users, groups, roles, and policies to define who has access to what AWS resources.

IAM users:

If you need to grant specific users access, create IAM users and assign them to groups or directly attach policies to them.

Represent individuals or applications needing to interact with AWS services.

IAM roles:

Create IAM roles with policies that grant the necessary permissions to access your API resources.

These roles can be associated with your web application's backend (e.g., Lambda functions, EC2 instances).

Define permissions for AWS services to interact with other AWS services.

```

    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "execute-api:Invoke",
                "Resource": "arn:aws:execute-api:REGION:ACCOUNT_ID:API_ID/STAGE/ANY/",
                "Condition": {
                    "IpAddress": {
                        "aws:SourceIp": [
                            "10.0.0.0/16"
                        ]
                    }
                }
            }
        ]
    }

```
For EC2 instances:

If your web application is running on EC2, create an IAM role that trusts EC2 and grants it permissions to access the API.

IAM policies:

Define IAM policies that specify the actions (e.g., execute-api:Invoke for API Gateway) and resources (your API endpoints) that the role or user is allowed to access.

Determine what permissions a user or role has, allowing or denying access to specific AWS resources.

Secrets: 

Store database credentials and API keys securely in AWS Secrets Manager or Parameter Store.

IAM authentication: 

Favor IAM authentication for RDS connections instead of storing credentials directly in your code.

IAM authorization for API Gateway:

API Gateway can be configured to use IAM for authentication and authorization. 

When a client requests access to your API, the API Gateway checks their credentials against IAM policies.

Using IAM with API Gateway:

To enable IAM authentication for an API method in API Gateway, you need to select IAM as the authorization type in the Method Request settings.

To secure your RESTful services in API Gateway using IAM, you need to configure the API to use IAM authorization, create IAM roles and policies.

To utilize the AWS API Gateway console, you first navigate to the AWS Management Console and select API Gateway. 

Using the AWS API Gateway console, you can create HTTP or REST APIs, manage deployments, establish API keys and usage plans, and configure integrations with AWS services like Lambda.

1. Go to the AWS Management Console.

2. In the AWS services search bar, type API Gateway and select it.

In the API Gateway console, select the API you want to secure.

3. Navigate to the method (e.g., GET, POST) you want to protect.

4. In the Method Request section, under Authorization, choose edit and select AWS_IAM as the authorization type.

HTTP APIs: Choose Create API and then Build under the HTTP API section.

REST APIs: Choose Create API and select the appropriate option (e.g., New API).

Choose an integration: Select an integration type (e.g., Lambda, HTTP endpoint) for your API.

### An example to secure RESTful API running on EC2

To secure and configure a RESTful API running on EC2 using the AWS API Gateway console, you'll need to create a RESTful API, define resources and methods, set up an integration with your EC2 instance, and configure security mechanisms like API keys or IAM roles.

Consider using CloudFormation for infrastructure as code (IaC) to manage and automate your API setup.

1. Create a RESTful API

Navigate to the API Gateway console in the AWS Management console.

Choose Create API and select REST API.

Choose New API and enter an API name.

Select Regional for the API endpoint type.

Choose Create API. 

2. Define resources and methods

In the API Gateway console, select your API.

Under Resources, choose Create Resource.

Define a resource path (e.g., /users).

Under the resource, choose Create Method.

Select the appropriate HTTP method (e.g., GET, POST). 

Choose Integration type as HTTP (if using a public IP) or VPC Link (if using a private IP via a load balancer). 

If using HTTP, provide the endpoint URL of your EC2 instance (including the public IP and port, e.g., http://<public-ip>:8080).

If using VPC Link, configure the VPC Link and endpoint URL (e.g., http://<private-ip>:8080).

Use HTTPS for secure communication between API Gateway and your EC2 instances.

Implement WAF (Web Application Firewall) to protect your API from common web exploits.

3. Secure the API

API keys:

Go to the API Keys section in the API Gateway console.

Create an API key.

Enable API key usage on the desired methods within your API.

Associate the API key with a usage plan to control access and usage. 

IAM roles:

Create IAM roles with policies that grant permission to access your API resources.

Associate the IAM role with the API Gateway API or specific methods.

Clients can then use AWS credentials to authenticate and access the API.

Alternative security measures:

Use Cognito user pools for user authentication and authorization.

Configure resource policies to control access to the API.

Utilize VPC endpoint policies for private APIs. 

4. Deploy the API

In the API Gateway console, select your API.

Choose Actions and select Deploy API.

Choose a deployment stage (e.g., prod, dev) or create a new one.

Choose Deploy. 

5. Test the API

Go to the Stages section of your API in the API Gateway console. 

Find the invoke URL for your deployed API.

Use this URL to test your API with tools like curl or Postman.

### An example to configure IAM roles and policies for Serverless

To secure your Node.js web application deployed with Lambda, RDS, CloudFront, and S3 on AWS, you'll need to configure IAM roles and policies for each service. 

Configure your Web application for backend services (e.g., Lambda).

1. IAM roles and policies

Lambda:

If your web application uses Lambda functions as its backend, you'll need to configure those functions with the IAM role that has permissions to invoke your API.

Create an IAM role for your Lambda function.

Attach policies like AmazonS3FullAccess if your Lambda needs to interact with S3, and AmazonRDSFullAccess if it interacts with RDS.

You can also create custom policies for specific actions (e.g., AmazonRDSDescribeDBInstances) to limit permissions.

If you need more advanced authorization logic (e.g., checking user roles, scopes, or other attributes), you can create Lambda authorizers.

RDS:

Configure IAM authentication for your RDS instance (if you haven't already).

Create an IAM role that grants your Lambda function permissions to connect to the RDS instance (e.g., rds-db:connect, rds-db:auth).

Ensure that your Lambda function uses this role to connect to RDS.

CloudFront:

CloudFront itself uses an IAM role to interact with S3 (the origin).

If you're using Lambda@Edge, your Lambda function will also require an IAM role to execute code at the edge.

Attach the appropriate policies for S3 and, if applicable, CloudFront events (e.g., CloudFrontFullAccess, AmazonS3ObjectOwnership).

S3:

S3 bucket policies determine who can access the bucket's objects.

You'll likely grant access to CloudFront's IAM role and potentially your Lambda function (for uploading/downloading objects). 

2. Setting up IAM roles and policies

```

# Create a Lambda role (An example)
aws iam create-role --role-name LambdaRole --assume-role-policy-document file://lambda_assume_role.json

# lambda_assume_role.json: { "Version": "2012-10-17", "Statement": { "Effect": "Allow", "Principal": { "Service": "lambda.amazonaws.com" }, "Action": "sts:AssumeRole" } }

# Attach policies to the Lambda role
aws iam attach-role-policy --role-name LambdaRole --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

# or, attach a custom policy file:
# aws iam attach-role-policy --role-name LambdaRole --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccess
# --policy-name CustomPolicy --policy-document file://custom_policy.json
# custom_policy.json: { "Version": "2012-10-17", "Statement": { "Effect": "Allow", "Action": ["s3:*"], "Resource": "arn:aws:s3:::your-bucket/*" } }

# Example RDS Role
# aws iam create-role --role-name RdsRole --assume-role-policy-document file://rds_assume_role.json
# rds_assume_role.json: { "Version": "2012-10-17", "Statement": { "Effect": "Allow", "Principal": { "Service": "ec2.amazonaws.com" }, "Action": "sts:AssumeRole" } }

# Attach RDS permissions to the role (example using RDS-DB role)
aws iam attach-role-policy --role-name RdsRole --policy-arn arn:aws:iam::aws:policy/AmazonRDSDatabaseRole

```

### An example to configure IAM for Docker container deployment

1. Create a Role:

You'll create an IAM role, typically for your Elastic Container Service (ECS) or Elastic Container Registry (ECR) tasks.

Relationship: 

Configure the role to trust AWS services like ECS or ECR, allowing them to assume the role and access your resources.

2. Attach policies:

Attach policies to the IAM role that grant the necessary permissions:

Amazon EC2 Container Service for EC2 Role: This policy allows ECS tasks running on EC2 to access other AWS services.

Other Policies: 

Depending on your specific needs, you might also need policies for accessing ECR, S3, or other resources.

3. Docker Container Configuration:

Pass the Role ARN: 

Within your Dockerfile or container startup, you can pass the ARN (Amazon Resource Name) of the IAM role to the container.

Environment Variables: 

Set environment variables within the container to store the role ARN.

AWS SDK: 

If your Node.js application uses the AWS SDK, configure it to use the credentials from the assumed IAM role.

### An example to deploy a Node.js application:

Let's say you're deploying a Node.js application to ECS, and you need the container to pull images from ECR and interact with other AWS services:

1. Create IAM Role:

Create an IAM role named ecr-ecs-role and attach the AmazonEC2ContainerServiceforEC2Role and other necessary policies (e.g., AmazonEC2ContainerRegistryReadOnly, AmazonS3ReadOnlyAccess).

2. Configure ECS Task Definition:

In your ECS task definition, configure the IAM role to be used by the container.

3. Docker Configuration:

Set environment variables in your Dockerfile or container configuration to pass the ecr-ecs-role ARN.

4. Node.js Application:

Within your Node.js application, use the AWS SDK to authenticate using the environment variables containing the role ARN.

References

Deploy Node.js Lambda functions with container images

https://docs.aws.amazon.com/lambda/latest/dg/nodejs-image.html

Deploy a Docker application to Elastic Beanstalk

https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/docker-quickstart.html