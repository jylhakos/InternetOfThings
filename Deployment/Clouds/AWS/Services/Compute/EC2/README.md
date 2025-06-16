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

## Example: Go backend providing RESTful APIs and CRUD operations with PostgreSQL and React frontend with Axios both deployed to AWS utilizing AWS EC2, RDS, S3, CloudFront and API Gateway

Create a Go backend with PostgreSQL CRUD, a React frontend with Axios, and deploy both to AWS (EC2, RDS, S3, CloudFront, API Gateway).

1. Create Go backend for CRUD operations with RESTful API

Initialize Go project:

```

    $ go mod init myapi

```
Add Go dependencies:

```

    $ go get github.com/gorilla/mux github.com/lib/pq github.com/joho/godotenv

```

Implement [CRUD handler functions](https://github.com/jylhakos/InternetOfThings/blob/main/Languages/Golang/CRUD/) using Gorilla Mux and pq.


SQL table:

```

    CREATE TABLE items (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        value TEXT NOT NULL
    );

```
2. Create React frontend with Axios

Create React app:

```

    $ npx create-react-app myfrontend

    $ cd myfrontend

    $ npm install axios

```


Axios usage:

```

import axios from "axios";
const baseURL = "https://your-api-gateway-id.execute-api.region.amazonaws.com/prod"; // use API Gateway URL

export const getItems = () => axios.get(`${baseURL}/items`);
export const createItem = (item) => axios.post(`${baseURL}/items`, item);
export const updateItem = (id, item) => axios.put(`${baseURL}/items/${id}`, item);
export const deleteItem = (id) => axios.delete(`${baseURL}/items/${id}`);

```

Use these functions in your React components (e.g., in useEffect or on form submit).

3. Deploy Go Backend to AWS EC2

Provision EC2 (Ubuntu) and open necessary ports (typically 8080, but restrict to API Gateway security group).

Install Go: 

```

    $ sudo apt update && sudo apt install golang

```

Clone Git repository and build Go application:

```

$ git clone <repo>

$ cd <repo>

$ go build -o myapi


```
Set DATABASE_URL to RDS endpoint in environment variables.

Run your Go application:

```

    $ ./myapi

```

4. AWS RDS for PostgreSQL

Create RDS instance via AWS Console (PostgreSQL).

Set security group to allow EC2 access (by EC2’s security group).

Get endpoint and use it in your Go app’s DATABASE_URL.


5. AWS S3 & CloudFront for React frontend

Build React app:

```

    $ npm run build

```

Create S3 bucket (enable static website hosting)

Upload build/ contents to S3.

Set bucket policy for public read (or use CloudFront for better security).

Create CloudFront distribution with S3 bucket as the origin.

Use CloudFront DNS as your frontend URL.

6. Secure REST API with AWS API Gateway

Create API Gateway REST API (or HTTP API) in AWS Console.

Set up resources and methods matching your Go API endpoints.

Set integration to your EC2 instance (via VPC Link, or use a public endpoint).

Optionally, enable custom domain and HTTPS.

Set up security (e.g., API Key, Cognito, IAM, or JWT authorizer).

Restrict EC2 to accept traffic only from API Gateway security group for security.

7. Access Control & Security

API Gateway: 

Use an authorizer (API Key, JWT, Cognito User Pools).

CORS: 

Enable CORS on API Gateway for your frontend domain.

HTTPS: 

CloudFront and API Gateway both provide HTTPS endpoints.

## Example: Node.js backend and React app on AWS EC2

To deploy a Node.js backend and React app from a local Linux computer to AWS EC2 involves several steps.

1. Set up an EC2 instance

Launch an EC2 instance using the AWS Management Console.

Choose an Amazon Machine Image (AMI) like Amazon Linux 2.

Configure instance details, storage, and security groups.

Allow inbound traffic on ports 80 (HTTP) and 22 (SSH).

Create a new key pair or use existing one for SSH access.

2. Connect to the EC2 Instance

Use SSH to connect to your EC2 instance using the public IP address and the private key file.

```

    $ ssh -i "your-key-pair.pem" ec2-user@<public-ip-address>

```
    
3. Install Node.js and npm

Update the package list.

```

	$ sudo apt update -y

```

Use apt command to install Node.js and npm.

```

    $ sudo apt install -y nodejs npm

```

Verify node installation.

```

    $ node -v

```

Verify npm installation.

```

    $ npm -v

```

4. Install Git

Install git.

```

$ sudo apt install -y git

```

5. Prepare your Node.js and React applications

Backend:

Ensure your Node.js backend is ready with necessary dependencies listed in package.json file.

Frontend:

Ensure your React app is built using npm run build or yarn build.

6. Transfer your applications to EC2

Clone your the source code from the Git repository:

```

$ git clone <your-repository-url>

```
Or, copy your project files using scp command:

```

	$ scp -i "your-key-pair.pem" -r /path/to/your/project ec2-user@<public-ip-address>:/home/ec2-user

```

7. Install dependencies

Navigate to the project directory.

```

    $ cd /home/ec2-user/<your-project-name>

```


Install backend dependencies.

```

	$ npm install

```
Navigate to the React app directory.

```

	$ cd /home/ec2-user/<your-project-name>/client

```

Install frontend dependencies.

```

	$ npm install

```

8. Configure Web server (Nginx)

Install nginx server

```

    $ sudo apt install -y nginx

```

Create a Nginx configuration file for your React app:


```

	$ sudo nano /etc/nginx/sites-available/your-app

```

Add Nginx configuration.

```

        server {
            listen 80;
            server_name <your-public-ip-address>;

            root /home/ec2-user/<your-project-name>/client/build;

            index index.html;

            location / {
                try_files $uri $uri/ /index.html;
            }

           location /api {
                proxy_pass http://localhost:5000;
                proxy_http_version 1.1;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection 'upgrade';
                proxy_set_header Host $host;
                proxy_cache_bypass $http_upgrade;
           }
        }

```

Create a symbolic link to enable the site:

```

	$ sudo ln -s /etc/nginx/sites-available/your-app /etc/nginx/sites-enabled

```

Remove default Nginx configuration.

```

	$ sudo rm /etc/nginx/sites-enabled/default

```

Test Nginx.

```

	$ sudo nginx -t

```

Restart Nginx.

```

	$ sudo systemctl restart nginx

```
 
9. Run your backend application

Start your Node.js backend.

```

	$ cd /home/ec2-user/<your-project-name>/server

	$ node index.js

```

10. Use PM2 for process management

Install PM2.

```

	$ sudo npm install -g pm2

```
Start backend with PM2.

```

	$ cd /home/ec2-user/<your-project-name>/server
    
	$ pm2 start index.js

```

Start frontend with PM2.

```

	$ cd /home/ec2-user/<your-project-name>/client

	$ pm2 serve build 3000 --name react_app

```

Save PM2 process.

```

$ pm2 save

```

11. Access your application by a web browser

Open a web browser and navigate to your EC2 instance's public IP address.

Notes:

AWS SDK: 

The AWS SDK for Node.js can be used within your backend for interacting with other AWS services.

Environment variables: 

Use environment variables to manage sensitive data.

Security: 

Configure security groups and use HTTPS for production environments.

Elastic IP: 

Assign an Elastic IP to your EC2 instance for a static IP address.

Load balancing: 

Consider using an Application Load Balancer for scaling and high availability.

Continuous deployment:

Automate deployments using tools like GitHub Actions or AWS CodePipeline.

References

Get started with CloudFront

https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/GettingStarted.html

Private integrations for RESTful APIs in API Gateway

https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-private-integration.html



