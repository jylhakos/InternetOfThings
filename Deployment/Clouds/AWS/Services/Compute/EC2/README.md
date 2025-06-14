# Elastic Compute Cloud (EC2)

## An example to deploy Go web application with RESTful APIs on Amazon AWS, utilizing EC2, S3, RDS for PostgreSQL, and IAM

Key steps for deploying a Golang (Go) web application with RESTful APIs on Amazon AWS, incorporating EC2, S3, RDS for PostgreSQL, and IAM for enhanced security.

1. Infrastructure setup

VPC, Subnets, and Gateways: 

Create a Virtual Private Cloud (VPC) to provide a private network for your AWS resources. 

Within the VPC, establish public and private subnets, configure an Internet Gateway (IGW) for internet access, and set up route tables to manage traffic flow between subnets and the IGW.

Configure security groups: 

Define security groups to control inbound and outbound traffic to your EC2 instances and RDS database. 

Create a security group for your web server (EC2) that allows incoming HTTP/HTTPS traffic.

SSH access (port 22) for connecting from your local machine.

HTTP/HTTPS traffic (ports 80/443) for your application.

Outbound connections to the RDS database port.

EC2 Instance: 

Launch an EC2 instance within the VPC. 

Sign in to the AWS Management Console and launch a new EC2 instance, choosing a suitable AMI (e.g., Amazon Linux 2).

EC2 instance will host your Golang web application. 

Install Golang on the EC2 instance.

RDS for PostgreSQL: 

Create an RDS instance for PostgreSQL to store your application's data.

S3 Bucket: 

Create an S3 bucket to store static assets of your web application. 

You can also configure it for static web hosting.

2. Web application deployment and configuration

Code preparation: 

Ensure your Golang application is ready for deployment. 

This includes building the executable.

To upload your Go application's executable from your local Linux computer to an EC2 instance on AWS, you can utilize the scp (secure copy) command.

Use SSH to connect to your EC2 instance from your local Linux machine, using the key pair you downloaded during instance creation.

Database schema: 

Connect to the RDS database using a secure method like a bastion host and create the necessary database schema for your application.

Upload and launch: 

Install the Go runtime on the EC2 instance.

Transfer your compiled Go application binary or source code to the EC2 instance. 

Upload your Go application's executable to the EC2 instance. 

Set up the environment variables for your application, including database credentials (if not using Secrets Manager).

You may need to configure a process manager (e.g., systemd, supervisord) to ensure the application starts automatically.

Configure the server to launch your application, using process managers like systemd.

Ensure your application compiles and runs correctly on your local Linux machine.

Cross-Compile your Go application for Linux:

Since you're transferring from a Linux machine to a Linux EC2 instance, you need to ensure your executable is built for the correct Linux architecture and operating system, which is common if you are not running the same distribution locally.

Open your terminal and use the go build command with environment variables set for the target OS and architecture.

```

$ env GOOS=linux GOARCH=amd64 go build -o your_app_executable_name package-import-path

```
Replace your_app_executable_name with the desired name for your executable.

Replace package-import-path with the import path of your main Go package.

Identify your EC2 instance's public DNS or IP and username:

Log in to your AWS Management Console.

Navigate to the EC2 Dashboard.

Select your running instance.

Find the Public DNS (IPv4) or Public IPv4 address.

Note the default username for your instance (e.g., ec2-user for Amazon Linux, ubuntu for Ubuntu AMIs). 

Use scp to upload the executable:

Open a new terminal on your local Linux computer.

Use the scp command in the following format:

```

$ scp -i /path/to/your/private-key.pem /path/to/your_app_executable_name username@your-ec2-public-dns-or-ip:/path/to/destination/directory/

```

Replace /path/to/your/private-key.pem with the actual path to your private key file.

Replace /path/to/your_app_executable_name with the path to your compiled Go executable.

Replace username with the EC2 instance's username.

Replace your-ec2-public-dns-or-ip with the public DNS or IP address of your instance.

Replace /path/to/destination/directory/ with the desired path on your EC2 instance where you want to upload the file.

For example, if the executable is in your home directory and your EC2 instance is at ec2-54-166-128-20.compute-1.amazonaws.com with the user ubuntu, and you want to upload it to the /home/ubuntu/data/ directory, the command would look like this:

```

$ scp -i ~/.ssh/mykey.pem ~/my_app_executable_name ubuntu@ec2-54-166-128-20.compute-1.amazonaws.com:/home/ubuntu/data/

```

Ensure the EC2 instance's security group allows inbound SSH traffic (port 22) from your IP address or a trusted source.

Ensure the target directory on your EC2 instance has appropriate write permissions for the user you're connecting as.

Consider using AWS Systems Manager Session Manager or EC2 Instance Connect Endpoint for more secure and flexible ways to connect to your instances, especially for instances in private subnets or without public IPs.

Connect to RDS: 

Update your application's database connection settings to connect to the RDS PostgreSQL instance.

Configure database connections (RDS):

You can use IAM to authenticate to your RDS instance from your Go application, which is a secure method recommended by AWS.

Create an IAM role for your EC2 instance with permissions to connect to your RDS database instance.

Utilize AWS SDK for Go V2: Use the AWS SDK for Go V2 to generate authentication tokens for connecting to your database, particularly for Aurora MySQL or PostgreSQL.

Avoid hardcoding database credentials in your code. 

Consider using environment variables or AWS Secrets Manager for production environments.

Configure static file serving (Optional): 

If your application serves static files, configure S3 to host them and update your application to reference the S3 URLs.

Load balancing: 

If you anticipate high traffic, consider using an Application Load Balancer (ALB) to distribute incoming requests across multiple EC2 instances running your application.

3. Securing your application (IAM)

IAM role for EC2: 

Create an IAM role that allows your EC2 instance to interact with AWS services, such as RDS and S3. 

Attach this role to your EC2 instance.

Ensure your application uses the AWS SDK for Go V2 to interact with S3. 

The EC2 instance will need permissions to access your S3 buckets.

Permissions for S3 and RDS: 

Configure the IAM role with specific policies to grant necessary permissions to your EC2 instance for accessing S3 buckets (e.g., read, write) and RDS database (e.g., connect, query).

IAM authentication for RDS: 

For enhanced security, consider using IAM database authentication for your RDS instance. 

This eliminates the need to manage database credentials within your application code and provides a more secure connection method.

S3 bucket policy: 

Configure your S3 bucket policy to grant the EC2 instance's IAM role the necessary permissions for accessing your S3 buckets (e.g., reading/writing objects). 

RDS security group: 

Ensure the security group for your RDS instance allows inbound connections from the EC2 instance's security group on the correct database port.

4. Deploy and run the application

Run the application: 

Execute the Go executable on the EC2 instance.

Example: /path/on/ec2/instance/my_app

Alternative deployment methods:

Elastic Beanstalk: 

Consider using AWS Elastic Beanstalk, which simplifies deploying, managing, and scaling Go web applications.

Containers (Docker and ECS): 

For more scalable deployments, consider containerizing your Go application with Docker and deploying it to Amazon Elastic Container Service (ECS).

5. Cost management on AWS

Monitor your AWS resource usage and optimize configurations to control costs.



