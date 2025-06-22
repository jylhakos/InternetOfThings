# Serverless on AWS

AWS offers serverless services across all three layers: compute, integration, and data storage.

## Lambda

Lambda is a serverless, event-driven compute service that lets you run code without managing servers. 

You write functions, upload them to Lambda, and they are executed in response to events like HTTP requests, file uploads, or other triggers. 

AWS handles the underlying infrastructure, scaling, and maintenance.

## Example: Serverless functions with Go and deployed to AWS Lambda by Serverless Framework

Serverless Framework uses AWS CloudFormation to manage resources.

To deploy a Go function to AWS Lambda using the Serverless Framework on a local Linux machine, you'll need to install the Serverless CLI, configure your AWS credentials, write a Serverless configuration file (serverless.yml), create your Go function, compile it, and then deploy using the Serverless Framework. 

Build Go Serverless REST APIs and Deploy to AWS using the Serverless Framework.

Here’s a detailed steps.

![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/Deployment/Clouds/AWS/Serverless/React_Native.png?raw=true)

1. Prerequisites

Install Go: 

Make sure you have Go installed on your Linux machine.

Install Serverless Framework: 

Use npm to install the Serverless CLI globally: 

```

    $ npm install -g serverless

```
Configure AWS Credentials: 

Ensure your AWS credentials (access key and secret key) are configured on your system.

You can set these as environment variables or through the AWS CLI.

2. Project setup

Create a project directory. 

```

    $ mkdir my-go-lambda && cd my-go-lambda

```

Create a serverless.yml file in your project root to configure your service and function. 

An example configuration, which defines the service name, AWS provider details (runtime, region), packaging rules to include your compiled binary, and function definitions with handler and event triggers.

A basic example to define your Serverless application.

Create [a serverless.yml file](https://github.com/jylhakos/InternetOfThings/blob/main/Languages/Golang/Serverless/serverless.yml) in your project root to configure your service and function. 

```

    service: my-go-lambda
    frameworkVersion: ">=2.0.0"
    provider:
      name: aws
      runtime: go1.x
      region: us-east-1  # Replace with your desired region
      iamRoleStatements:
        - Effect: "Allow"
          Action:
            - "logs:CreateLogGroup"
            - "logs:CreateLogStream"
            - "logs:PutLogEvents"
          Resource: "arn:aws:logs:*:*:*"
    functions:
      hello:
        handler: handler # The name of your Go function (without .go)
        events:
          - http:
              path: /hello
              method: get

```

Go functions in Lambda use the "provided" runtime, requiring a compiled binary.

Create [a Go file](https://github.com/jylhakos/InternetOfThings/blob/main/Languages/Golang/Serverless/handler.go) (e.g., handler.go)

```

    package main

    import (
      "context"
      "fmt"
      "github.com/aws/aws-lambda-go/lambda"
      "github.com/aws/aws-lambda-go/events"
    )

    type Response struct {
      Message string `json:"message"`
    }

    func Handler(ctx context.Context, request events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
      message := fmt.Sprintf("Your request was processed with path: %s", request.Path)

      response := Response{
        Message: message,
      }

      return events.APIGatewayProxyResponse{
        Body:       fmt.Sprintf("%v", response),
        StatusCode: 200,
      }, nil
    }

    func main() {
      lambda.Start(Handler)
    }

```

3. Compile the Go function

Build the binary.
```

  $ GOOS=linux go build -o handler handler.go

```

The go build command compiles the Go code for the Linux platform and outputs the binary to handler. 

4. Package the function

Create a zip file.

```

   $ zip handler.zip handler

```

The zip command creates a zip archive named handler.zip containing the compiled binary.

Deploy with Serverless:

Execute the serverless deploy command in your terminal from the project root. 

The serverless deploy command packages your function, provisions AWS resources, and deploys your application. You can use the --verbose flag for more detailed output.

Navigate to your project directory.

```

    $ cd my-go-lambda
    
```

To deploy a Go application to AWS Lambda using the Serverless Framework on Linux, you'll utilize the serverless deploy command.

```

  $ serverless deploy

```

The serverless deploy command uses the serverless.yml file to deploy your application to AWS Lambda.

5. Test your deployed function

After deployment, the Serverless Framework provides the URL of your deployed endpoint. 

Test it using curl or a tool like Postman. 

Alternatively, use the Serverless Framework's invoke command: 

```

  $ serverless invoke -f health

```
## Example: Deployment of Serverless functions written in Go with AWS Cloud Development Kit (CDK) for AWS Lambda, RDS, S3 and IAM

Deploying Go serverless functions with AWS Cloud Development Kit (CDK) for AWS Lambda, RDS, S3, and IAM involves defining your infrastructure as code using Go within your CDK project.

1. Setting up your AWS CDK project

Initialize a AWS CDK project: 

Initialize a CDK project: 

Use the CDK CLI (cdk init --language go) to create a new CDK project in Go.

Use the cdk init command to create a new project in Go.

Install necessary CDK modules and dependencies: 

Include the AWS CDK modules for Lambda (awslambda), RDS (awscdk/awscdk.rds), S3 (awscdk/awss3), and IAM (awscdk/awsiam) in your Go project dependencies.

Add the necessary CDK Go packages for AWS Lambda, S3, and RDS to your project's go.mod file and run go build to install them. 

Structure your code: 

Organize your CDK application into stacks and constructs to represent logical units of your infrastructure.

Create a Go file for your stack:

This file will contain the code that defines your AWS resources using the CDK's Go constructs.

2. Defining your Infrastructure in AWS CDK

Lambda function:

Use the awslambda.NewFunction construct: 

This construct allows you to define your Lambda function.

Specify the runtime: 

Choose the appropriate Go runtime for your Lambda function.

Specify the code: 

You can point to your Go code using the awslambda.Code.FromAsset method, which will zip and upload your code during deployment.

Configure the function: 

Set memory, timeout, environment variables (e.g., for database connection details), and other settings as needed.

Grant permissions: 

Define the necessary IAM permissions for your Lambda function to interact with S3 and RDS. 

Create the Lambda function code: 

Write your Go code for the Lambda function handler, ensuring it's compiled as a .zip file for deployment.

Define the Lambda construct in CDK: 

Use the awslambda.NewFunction construct to specify the function name, runtime (Go), handler, and other configuration settings like memory, timeout, and environment variables.

Minimize the deployment artifact size: 

Optimize your Go code and dependencies to minimize the size of the deployment package, which can improve cold start times.

```

func (s *MyStack) NewGoLambda(scope constructs.Construct, id string) awslambda.Function {
    return awslambda.NewFunction(scope, jsii.String(id), &awslambda.FunctionProps{
        Runtime: awslambda.Runtime_GO_1_X(), // Or the appropriate Go runtime
        Handler: jsii.String("main"),      // Your Go function handler
        Code:    awslambda.Code_FromAsset(jsii.String("path/to/your/go/code"), nil),
    })
}

```

RDS Database:

Define the RDS construct in CDK: 

Use the awscdk.rds.DatabaseInstance or awscdk.rds.DatabaseCluster construct to create your RDS database instance, specifying the engine, size, and other configuration settings.

Use the awscdkrds.NewDatabaseInstance construct: 

Specify the database engine (e.g., PostgreSQL), instance size, storage, and other settings.

This construct creates an RDS database instance.

Configure security groups: 

Set up security groups to allow the Lambda function to connect to the RDS instance.

Manage database credentials securely: 

The AWS CDK can automatically create and store database credentials in AWS Secrets Manager, which is a recommended security best practice.\

Set up security groups to control access to the RDS instance and allow your Lambda function to connect to it.

Use the rds.GrantConnect (or similar) method to authorize your Lambda function to connect to the database.

Place the RDS instance in a VPC: 

For security, place the RDS instance in a private subnet within a VPC.

```

func (s *MyStack) NewRDSInstance(scope constructs.Construct, id string, vpc ec2.Vpc, securityGroup ec2.SecurityGroup) awscdkrds.DatabaseInstance {
    return awscdkrds.NewDatabaseInstance(scope, jsii.String(id), &awscdkrds.DatabaseInstanceProps{
        Engine: awscdkrds.DatabaseInstanceEngine_Postgres(&awscdkrds.PostgresEngineVersion{
            Version: jsii.String("13.4"), // Or your desired version
        }),
        Vpc:            vpc,
        VpcSubnets:     &ec2.SubnetSelection{SubnetType: ec2.SubnetType_PRIVATE_WITH_EGRESS},
        SecurityGroups: &[]ec2.ISecurityGroup{securityGroup},
    })
}

```
S3 Bucket:

Define the S3 bucket construct in CDK: 

Use the awscdk/awss3.Bucket construct to create your S3 bucket.

This construct creates an S3 bucket.

Configure bucket properties: 

Set access control, versioning, and other options as required.

Define access permissions: 

Grant the Lambda function the necessary permissions to interact with the S3 bucket (e.g., upload, download objects).

Grant Lambda access to the bucket: 

Use the bucket.GrantReadWrite (or similar) method to grant your Lambda function permission to interact with the S3 bucket.

```

func (s *MyStack) NewS3Bucket(scope constructs.Construct, id string) awss3.Bucket {
    return awss3.NewBucket(scope, jsii.String(id), &awss3.BucketProps{
        Versioned: jsii.Bool(true),
    })
}

```

IAM roles and policies:

Let CDK manage IAM roles and security groups: 

The AWS CDK construct library provides convenience methods like grant() to create minimally scoped IAM roles that grant specific permissions to resources. 

For instance, myBucket.grantRead(myLambda) grants read access to myBucket to myLambda.

Define required IAM policies: 

Define IAM policies that grant the Lambda function permissions to access RDS, S3, and other necessary AWS services.

3. Deployment

Build and synthesize your CDK application:

Run go build to compile your Go code and cdk synth to generate the AWS CloudFormation template.

Synthesize the CDK app: 

Run cdk synth to generate the CloudFormation template for your stack.

Deploy the CDK stack: 

Use the cdk deploy command to provision your defined AWS resources. 

Run cdk deploy to provision the AWS resources defined in your stack.


## Example: Serverless functions with Go for AWS, utilizing Lambda, RDS with PostgreSQL, CloudFront, S3 and IAM

Deploying a Go application from a local Linux machine to AWS using Serverless functions, AWS Lambda, RDS with PostgreSQL, CloudFront, S3, and IAM involves several steps.

1. Go application development

Structure your Go application: 

Organize your code into a project structure suitable for Lambda functions. 

A common approach involves having a main.go file that contains your Lambda handler function.

Implement Lambda Handler: 

Your Go code should have a handler function that processes incoming events from AWS services like API Gateway.

Compile for Linux: 

Since AWS Lambda runs on a Linux environment, compile your Go application for the Linux target architecture (e.g., GOOS=linux GOARCH=amd64).

2. Serverless Framework configuration

Install Serverless Framework: 

If you don't have it installed, follow the instructions to install the Serverless Framework on your Linux machine.

Create serverless.yml: 

This file defines your serverless application, including Lambda functions, events (e.g., API Gateway), and AWS resources.

```


service: my-go-lambda-service

provider:
  name: aws
  runtime: go1.x
  region: us-east-1 # Replace with your preferred region
  package:
    patterns:
      - '!./**'  # Exclude all files initially
      - ./bin/** # Include the compiled Go binary in the 'bin' directory

functions:
  hello:
    handler: bin/hello # Path to your compiled binary
    events:
      - http:
          path: /hello
          method: get
          cors: true

plugins:
  - serverless-go-plugin # Example plugin for Go deployment

```

provider: 

Defines the cloud provider (AWS in this case) and global settings for your service. 

Key settings include:

name: 

Must be set to aws.

runtime: 

Specifies the Go runtime for your Lambda functions. Common options include go1.x.

region: 

Sets the AWS region where the service will be deployed.

package: 

Defines packaging configurations, including which files/directories to include or exclude. 

For Go, this is often used to specify the compiled binary to be included in the function package.

iamRoleStatements: 

Defines IAM role permissions for your Lambda functions at the provider level, enabling them to interact with other AWS services. 

functions: 

Lists the individual Lambda functions within your service. 

Each function has its own configuration:

health (or your function name): The name of the function.

handler: 

Specifies the entry point for your Lambda function, usually the path to the compiled binary.

events: 

Defines the events that trigger the Lambda function, such as HTTP requests, SQS messages, etc.

http: 

Configures an HTTP endpoint for your function, specifying the path, method (GET, POST, etc.), and other API Gateway settings. 

The Serverless Framework translates the serverless.yml into an AWS CloudFormation stack for deployment.

Configure Go runtime: 

Specify provided.al2 or provided.al2023 as the runtime for your Go Lambda functions. 

You'll need to use the serverless-go-plugin to simplify the build and deployment process.

Define Lambda functions: 

Define your Go Lambda functions in serverless.yml, pointing the handler to the compiled binary (e.g., bootstrap).

Configure API Gateway: 

Define the API Gateway events that trigger your Lambda functions in serverless.yml.

Configure RDS integration:

Secrets Manager: 

Store your RDS PostgreSQL database credentials securely in AWS Secrets Manager.

Lambda function permissions: 

Grant your Lambda function permission to access the secret in Secrets Manager.

Environment variables: 

Configure environment variables in serverless.yml to pass the database host, database name, and secret name to your Lambda function.

Connect to RDS: 

Your Go code will need to retrieve the database credentials from Secrets Manager and establish a connection to your RDS PostgreSQL database.

Configure CloudFront and S3:

Define S3 Bucket: 

Configure an S3 bucket in your serverless.yml to store your static website content or other assets.

Configure CloudFront distribution: 

Set up a CloudFront distribution that uses your S3 bucket as an origin.

Configure IAM roles:

Default Lambda role: 

Serverless Framework typically creates a default IAM role for your Lambda functions. You can add specific permissions to this role in serverless.yml.

Grant Access to AWS Resources: 

Ensure your Lambda function's IAM role has permissions to interact with other AWS services like Secrets Manager, RDS, and S3.

3. Deployment

Build the Go application: 

Use the make command (if using a Makefile setup) or run the Go build command with the appropriate settings (e.g., GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -tags lambda.norpc -o bootstrap main.go) to create the executable binary.

Deploy with Serverless Framework: 

Use the serverless deploy command from your local Linux machine to deploy your serverless application to AWS.

Serverless Framework Actions: 

Serverless Framework uses AWS CloudFormation to create and manage your AWS resources.

Deployment process: 

Packaging your Go binary into a .zip file.

Creating or updating your Lambda function in AWS.

Setting up API Gateway to trigger your Lambda function.

Configuring the CloudFront distribution and S3 bucket.

Creating or updating IAM roles and policies.

4. Testing

Test Lambda function:

After deployment, you can test your Lambda function directly from the AWS Lambda console or by sending requests to your API Gateway endpoint.

Test RDS connection: 

Verify that your Lambda function can successfully connect to the RDS PostgreSQL database and execute queries.

Test CloudFront and S3:

Access your static content through the CloudFront distribution URL to ensure it's being served correctly. 

References

Building Lambda functions with Go

https://docs.aws.amazon.com/lambda/latest/dg/lambda-golang.html

Deploying Lambda functions with the AWS CDK

https://docs.aws.amazon.com/lambda/latest/dg/lambda-cdk-tutorial.html

Invoking an AWS Lambda function from an RDS for PostgreSQL DB instance

https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/PostgreSQL-Lambda.html

Deploy Go Lambda functions with .zip file archives

https://docs.aws.amazon.com/lambda/latest/dg/golang-package.html