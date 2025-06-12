# Security

## IAM

AWS Identity and Access Management (IAM), a service for managing users, groups, roles, and policies to define who has access to what AWS resources.

IAM users:

Represent individuals or applications needing to interact with AWS services.

IAM roles:

Define permissions for AWS services to interact with other AWS services.

IAM policies:

Determine what permissions a user or role has, allowing or denying access to specific AWS resources.

Secrets: 

Store database credentials and API keys securely in AWS Secrets Manager or Parameter Store.

IAM authentication: 

Favor IAM authentication for RDS connections instead of storing credentials directly in your code.

### An example to configure IAM roles and policies for Serverless

To secure your Node.js web application deployed with Lambda, RDS, CloudFront, and S3 on AWS, you'll need to configure IAM roles and policies for each service. 

1. IAM Roles and Policies

Lambda:

Create an IAM role for your Lambda function.

Attach policies like AmazonS3FullAccess if your Lambda needs to interact with S3, and AmazonRDSFullAccess if it interacts with RDS.

You can also create custom policies for specific actions (e.g., AmazonRDSDescribeDBInstances) to limit permissions.

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