# Compute

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
