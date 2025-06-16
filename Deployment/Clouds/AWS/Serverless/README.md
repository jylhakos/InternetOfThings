# Serverless on AWS

AWS offers serverless services across all three layers: compute, integration, and data storage.

## Use cases

- Web Applications

Build APIs and backends using Lambda functions triggered by API Gateway or other events.

- Data Processing

Process data streams, handle file uploads, and perform batch processing.

- Machine Learning

Preprocess data, serve models for prediction, and perform other ML tasks.

- Backends for other AWS services

Integrate Lambda with services like S3, DynamoDB, and Kinesis.

## Lambda

Lambda is a serverless, event-driven compute service that lets you run code without managing servers. 

You write functions, upload them to Lambda, and they are executed in response to events like HTTP requests, file uploads, or other triggers. 

AWS handles the underlying infrastructure, scaling, and maintenance.

### Example: Serverless functions with Node.js for AWS, utilizing Lambda, RDS, CloudFront and S3 services

By following these steps, you can create Serverless functions with Node.js for AWS, utilizing Lambda, RDS, CloudFront, and S3 services.

1. Set up your AWS account

If you don't have one, create an AWS account.

2. Create a Node.js Lambda function

In the AWS Management Console, navigate to the Lambda service.

Click "Create function".

Choose "Author from scratch".

Provide a function name and choose Node.js as the runtime.

Click "Create function".

Write your Lambda function code: 

This code will contain the logic to interact with other AWS services (RDS, S3).

Install necessary dependencies: 

For example, to interact with RDS, install the necessary database client module (like mysql2 for MySQL) using npm and include it in your Lambda deployment package.

Deploy your Lambda function: 

Lambda is serverless compute service that allows you to run code without managing servers. 

You pay only for the compute time consumed. 

Write your Node.js code that will execute in response to events or requests.

Upload your code as a .zip file or paste it directly in the Lambda console.

You can upload your code as a zip file or link to a code repository.

Configure Runtime:

Choose a Node.js runtime environment for your function.

Create an IAM role with the necessary permissions for your Lambda function to interact with other AWS services like S3 and RDS.

Lambda Function Handling: 

In your Node.js code, process the S3 event data, such as bucket name and object key.

Interact with S3 Objects: 

Use the AWS SDK for JavaScript to perform actions like getting object content from S3.

3. Set up RDS

RDS is relational database service that supports various database engines like MySQL, PostgreSQL, Oracle, and SQL Server.

Create an RDS Instance: 

Navigate to the RDS service in the AWS console and create a new database instance (e.g., MySQL, PostgreSQL).

Configure VPC and Security Group: 

Ensure your Lambda function is configured within the same VPC as your RDS instance, ideally in a private subnet. 

Configure security group rules to allow your Lambda function to connect to the RDS instance on the appropriate database port (e.g., 3306 for MySQL).

Create IAM Role: 

Create an IAM role with permissions to access your RDS database, potentially using policies like AmazonRDSDataFullAccess.

Create Database Credentials in Secrets Manager: 

For secure database access, store your RDS credentials in AWS Secrets Manager.

Create and attach an RDS Proxy (Optional): 

Use an RDS Proxy to manage database connections and improve the scalability and resilience of your serverless application. 

Configure the proxy to use the Secrets Manager secret for database authentication.

Configure Lambda to connect to the RDS Proxy: 

Update your Lambda function configuration to connect to the RDS proxy endpoint instead of the RDS instance endpoint directly.

Perform database operations (e.g., querying or inserting data) from your Lambda function.

4. Set up S3

S3 is an object storage service that provides scalable and durable storage for a wide variety of data types.

You can store files, images, videos, and other data in S3 buckets, and access them from anywhere via the internet.

Create an S3 Bucket: 

Navigate to the S3 service in the AWS console and create a new bucket to store your application's static content (like HTML files, images, etc.).

Configure S3 for Static Website Hosting (Optional): 

If you're hosting a static website, enable static website hosting on the S3 bucket.

Upload your content to the S3 bucket: Upload your application's static files to the bucket.

5. Set up CloudFront

CloudFront is a content delivery network (CDN) service that helps deliver content quickly and efficiently to users worldwide.

It caches content in edge locations around the world, so users can access it faster, regardless of their location.

Create a CloudFront Distribution: 

Navigate to the CloudFront service in the AWS console and create a new distribution.

Configure the S3 Bucket as the Origin: 

Select your S3 bucket as the origin for the CloudFront distribution.

Configure Origin Access Control (OAC): 

Use OAC to restrict direct access to your S3 bucket and ensure users access content only through the CloudFront distribution.

Configure Distribution Settings: 

Set caching behaviors, viewer protocol policies (e.g., redirect HTTP to HTTPS), and other relevant settings.

Update the S3 Bucket Policy: 

Update the S3 bucket policy to allow the CloudFront OAC to read objects from the bucket.

6. Integrate the services

Trigger Lambda from S3 events: Configure the S3 bucket to trigger your Lambda function when specific events occur (e.g., when a new file is uploaded).

Connect Lambda to RDS: 

In your Lambda function code, use the appropriate database client to connect to the RDS Proxy endpoint and perform database operations.

Use CloudFront for content delivery: Access your static content through the CloudFront distribution domain name.

7. Deploy and test

Deploy your Lambda function: 

Ensure your Lambda function is deployed with the necessary dependencies and configuration.

Upload a test object to your S3 bucket (for S3 triggers): 

This will invoke your Lambda function to process the object.

Test your application: 

Access your application through the CloudFront distribution domain name and verify that the Lambda function is able to interact with RDS and S3 as expected.

Considerations:

Serverless Frameworks:

Consider using frameworks like the AWS Cloud Development Kit (CDK) to simplify the process of defining, deploying, and managing your serverless application as infrastructure as code.

IAM roles and permissions: 

Pay careful attention to IAM roles and permissions to ensure that your Lambda function has the necessary permissions to access other AWS services like S3 and RDS.

VPC and Networking: 

Configure your Lambda function and RDS instance within the same VPC and ensure appropriate security group rules to allow communication between them.

Error handling and logging:

Implement robust error handling in your Lambda function and configure logging to CloudWatch Logs to monitor your application's performance and troubleshoot issues.

Security:

Follow AWS practices for security, including using IAM roles, Secrets Manager, and OAC.

Amazon Cognito provides authentication, authorization, and user management for web and mobile apps.

## Example: Serverlss Go application run on AWS Lambda deployed by Serverless Framework 

Serverless Framework uses AWS CloudFormation to manage resources.

The serverless-go-plugin can simplify Go compilation and deployment.

To create a serverless Go application for AWS Lambda using the Serverless Framework, you'll need to set up your project, write your function code, configure the serverless.yml file, and deploy it. 

This involves installing the Serverless Framework, initializing a Go project, defining your Lambda function with its handler and triggers in the serverless.yml, and then using the serverless deploy command to deploy your application to AWS.

Here's a more detailed breakdown:

1. Prerequisites

Install Serverless Framework: npm install -g serverless. 

Install Go: Make sure you have Go installed and configured. 

Configure AWS Credentials: Ensure your AWS CLI is configured with appropriate credentials for deployment. 

2. Project setup

Create a project directory: mkdir my-go-lambda && cd my-go-lambda. 

Initialize a Go module: 

```

    $ go mod init your-module-name

```

Install the aws-lambda-go package: 

```

    $ go get github.com/aws/aws-lambda-go/lambda


```

Install necessary dependencies: 

```

    $ go mod tidy

```

3. Write your Go code

Go functions in Lambda use the "provided" runtime, requiring a compiled binary.

Create your Go code (e.g., in a main.go file) that implements an AWS Lambda handler function.

Example handler for Serverless: 

```

    package main

    import (
        "context"
        "fmt"
        "github.com/aws/aws-lambda-go/lambda"
    )

    type Request struct {
        Name string `json:"name"`
    }

    type Response struct {
        Message string `json:"message"`
    }

    func handler(ctx context.Context, name Request) (Response, error) {
        message := fmt.Sprintf("Hello, %s!", name.Name)
        return Response{Message: message}, nil
    }

    func main() {
        lambda.Start(handler)
    }

```
Create a main.go file: 

The [main.go file](https://github.com/jylhakos/InternetOfThings/blob/main/Deployment/Clouds/AWS/Serverless/main.go) contains your Lambda function handler.

This example takes a JSON input with a name field and returns a JSON response with a greeting message. 

Compile your Go code for the Linux environment:

```

    $ env GOARCH=amd64 GOOS=linux go build -ldflags="-s -w" -o bin/health main.go

```

This command specifies the architecture (GOARCH=amd64), targets Linux (GOOS=linux), reduces the binary size (-ldflags="-s -w"), and sets the output path (-o bin/health) for your compiled binary.

4. Configure the serverless.yml file

Finally, you can configure triggers for your Lambda function within the AWS console or by defining them in the serverless.yml file. 

This [serverless.yml file](https://github.com/jylhakos/InternetOfThings/blob/main/Deployment/Clouds/AWS/Serverless/serverless.yml) defines your service, provider, functions, and events.

Create a serverless.yml file in your project root to configure your service and function. 

Example serverless.yml: 

```

    service: my-go-lambda

    provider:
      name: aws
      runtime: go1.x  # Or use provided.al2 for newer runtimes
      region: us-east-1 # Choose your desired AWS region
      architecture: arm64 # Optional: Use ARM architecture for cost and performance improvements
      environment:
        ENVIRONMENT: dev # Example environment variable
      iamRoleStatements:
        - Effect: "Allow"
          Action:
            - "logs:CreateLogGroup"
            - "logs:CreateLogStream"
            - "logs:PutLogEvents"
          Resource: "arn:aws:logs:*:*:*"
        - Effect: "Allow"
          Action:
            - "s3:GetObject"
            - "s3:PutObject"
            - "s3:DeleteObject"
          Resource:
            - "arn:aws:s3:::your-bucket-name/*" # Replace with your bucket name
      memorySize: 128 # Adjust memory as needed
      timeout: 30 # Adjust timeout as needed

    functions:
      hello:
        handler: handler # Matches the name of the function in your go code
        events:
          - http:
              path: /hello
              method: get
        package:
           individually: true
           artifact: bin/function # Path to the compiled binary
        environment:
           TABLE_NAME: my-table # Example environment variable

    package:
      individually: true
      exclude:
        - ./**
      include:
        - ./bin/**

```
provider: 

Specifies the cloud provider (AWS), runtime, region, and other configurations.

functions: 

Defines your Lambda functions, including their handlers, events (e.g., HTTP), and packages. 

package: 

Configures how your code is packaged for deployment. 

5. Deploy your serverless function

You'll need to install the Serverless CLI, configure your AWS credentials.

Run the Serverless deploy command in your terminal: 

```

$ serverless deploy

```
The Serverless Framework translates all syntax in serverless.yml to a single AWS CloudFormation template. 

The Serverless Framework will handle the infrastructure setup and deploy your Go function to AWS Lambda.

After deployment, the Serverless Framework provides the URL of your deployed endpoint.

## An Example to deploy Serverless mobile app

Amazon Cognito authenticates app users and authorizes them to access the app.

Amazon DynamoDB is a NoSQL database service that provides fast, predictable, and scalable performance.

To create and fetch data, AWS AppSync uses a GraphQL API to interact with the frontend app and a backend DynamoDB table.

![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/Deployment/Clouds/AWS/Serverless/React_Native.png?raw=true)

The diagram shows an example architecture for running a React Native mobile app’s backend in the AWS cloud.

The code for the sample application that’s used in this pattern is available in the GitHub aws-amplify-react-native-ios-todo-app repository.

References

Serverless services on AWS

https://aws.amazon.com/serverless/

Serverless

https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/serverless-pattern-list.html

Build and Test a Serverless Application with AWS Lambda

https://docs.aws.amazon.com/toolkit-for-visual-studio/latest/user-guide/lambda-build-test-severless-app.html

Build a serverless mobile app by using AWS Amplify

https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/build-a-serverless-react-native-mobile-app-by-using-aws-amplify.html

Build a Serverless Mobile (React Native) App using AWS Amplify

https://github.com/aws-samples/aws-amplify-react-native-ios-todo-app



