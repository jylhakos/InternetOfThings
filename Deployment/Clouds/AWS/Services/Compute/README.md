# Compute

## Elastic Compute Cloud (EC2)

EC2 provides virtual machines that act like servers, allowing you to run your applications, websites and offers an on-demand model, where you can launch instances whenever you need them.

### An example to use EC2 and API Gateway

To secure and configure a RESTful API running on EC2 using the AWS API Gateway console, you'll need to create a REST API, define resources and methods, set up an integration with your EC2 instance, and configure security mechanisms like API keys or IAM roles.

Here's a breakdown of the process:

1. Create a REST API

Navigate to the API Gateway console in the AWS Management Console.

Choose "Create API" and select "REST API".

Choose "New API" and enter an API name.

Select "Regional" for the API endpoint type.

Choose "Create API".

2. Define resources and methods

In the API Gateway console, select your API.

Under "Resources", choose "Create Resource".

Define a resource path (e.g., /users).

Under the resource, choose "Create Method".

Select the appropriate HTTP method (e.g., GET, POST).

Choose "Integration type" as "HTTP" (if using a public IP) or "VPC Link" (if using a private IP via a load balancer).

If using "HTTP", provide the endpoint URL of your EC2 instance (including the public IP and port, e.g., http://<public-ip>:8080).

If using "VPC Link", configure the VPC Link and endpoint URL (e.g., http://<private-ip>:8080).

3. Secure the API

API keys:

Go to the "API Keys" section in the API Gateway console.

Create an API key.

Enable API key usage on the desired methods within your API.

Associate the API key with a usage plan to control access and usage.

IAM roles:

Create IAM roles with policies that grant permission to access your API resources.

Associate the IAM role with the API Gateway API or specific methods.

Clients can then use AWS credentials to authenticate and access the API.

Alternative security solutions:

Use Cognito user pools for user authentication and authorization.

Configure resource policies to control access to the API.

Utilize VPC endpoint policies for private APIs.

Use HTTPS for secure communication between API Gateway and your EC2 instances.

4. Deploy the API

In the API Gateway console, select your API.

Choose "Actions" and select "Deploy API".

Choose a deployment stage (e.g., prod, dev) or create a new one.

Choose "Deploy".

5. Test the API

Go to the "Stages" section of your API in the API Gateway console.

Find the invoke URL for your deployed API.

Use this URL to test your API with tools like curl or Postman.

## Lambda

Lambda is serverless, event-driven compute service that allows you to run code without provisioning or managing servers. 

You can execute code in response to events like S3 uploads or API Gateway requests. 

You write functions, upload them to Lambda, and they are executed in response to events like HTTP requests, file uploads, or other triggers. 

AWS handles the underlying infrastructure, scaling, and maintenance.

While the programming model defines how Lambda interacts with your code, Execution environment is where Lambda actually runs your function.

Lambda runs your code with language specific runtimes (like Node.js or Python) in execution environments that package your runtime, layers, and extensions.

Lambda function is a block of code that runs in response to events.

Lambda function handler is the method in your function code that processes events.

When should you utilize Lambda for executing code on AWS?

- Web applications

- Stream processing

- Mobile backends

Key Features and Benefits

Serverless: 

You don't need to provision or manage servers. 

Event-Driven: 

Functions are triggered by events, making them ideal for handling dynamic workloads. 

Pay-as-you-go: 

You only pay for the compute time your functions use.

Automatic Scaling: 

Lambda scales up or down automatically based on demand.

Amazon RDS Proxy:

You can connect a Lambda function to an Amazon Relational Database Service (Amazon RDS) database directly and through an Amazon RDS Proxy.

Amazon RDS database:

Connecting to an Amazon RDS database in a Lambda function

Connecting to an Amazon RDS database in a Lambda function using JavaScript.

Permissions:

You can use AWS Identity and Access Management (IAM) to manage permissions in AWS Lambda.

You define the permissions that your Lambda function needs in a special IAM role called an execution role.

Processing event notifications from Amazon RDS

You can use Lambda to process event notifications from an Amazon RDS database. 

Amazon RDS sends notifications to an Amazon Simple Notification Service (Amazon SNS) topic, which you can configure to invoke a Lambda function. 

![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/Deployment/Clouds/AWS/Services/Compute/lambda_rds.png?raw=true)

References

Using AWS Lambda with Amazon RDS

https://docs.aws.amazon.com/lambda/latest/dg/services-rds.html

Lambda and Amazon RDS tutorial

https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-lambda-tutorial.html

How Lambda works

https://docs.aws.amazon.com/lambda/latest/dg/concepts-basics.html
