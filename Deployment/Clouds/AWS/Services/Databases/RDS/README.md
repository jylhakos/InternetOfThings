# Amazon RDS (Relational Database Service)

Amazon RDS (Relational Database Service) uses a database as a managed database service, simplifying the setup, operation, and scaling of databases in the cloud.

Amazon RDS takes care of the underlying infrastructure, operating system, file systems, networking, and other low-level management tasks for your database. 

You can deploy a database instances using the AWS Management Console or AWS CLI. 

Amazon RDS integrates with other AWS services like Amazon Bedrock and Amazon SageMaker for machine learning (ML) applications. 

What is Amazon Relational Database Service (Amazon RDS)?

Amazon Relational Database Service (Amazon RDS) is a web service that makes it easier to set up, operate, and scale a relational database in the AWS Cloud.

## Example: RESTful API application uses PostgreSQL deployed on AWS with EC2, RDS and IAM

To deploy a RESTful API application on AWS using EC2, RDS, and IAM with PostgreSQL, you'll need to configure your infrastructure, set up IAM roles and policies for secure access, and deploy your application code.

Here's a breakdown of the key steps:

1. Infrastructure setup

EC2 Instance:

Launch an EC2 instance (e.g., using an Ubuntu AMI) to host your API application. 

Configure security groups to allow inbound traffic on the necessary ports (e.g., 80 for your API, 22 for SSH) and outbound traffic to reach your RDS instance (5432 for PostgreSQL).

RDS PostgreSQL instance:

Create an RDS PostgreSQL instance. 

During setup, note the endpoint, username, and password. 

You'll need these for your application configuration.

IAM Roles and Policies:

Define IAM roles and policies to grant your EC2 instance the necessary permissions to interact with other AWS services, including RDS. 

This involves creating a policy that allows access to the RDS instance and attaching it to the EC2 instance's role.

2. Application configuration

Database Connection:

Configure your API application (e.g., using Node.js and Sequelize) to connect to the RDS PostgreSQL instance using the provided credentials and endpoint.

IAM authentication (Optional but recommended):

For enhanced security, enable IAM database authentication for your RDS instance and configure your application to use IAM roles and tokens for database access, instead of storing static credentials.

Environment variables:

Use environment variables (e.g., using a .env file) to store sensitive information like database credentials and API keys.

3. Deployment

Deploy application code: 

Deploy your RESTful API application code to the EC2 instance.

Start application: 

Start your application server (e.g., using npm start for a Node.js application).

Detailed steps:

1. IAM database authentication:

Activate IAM database authentication on your RDS PostgreSQL instance.

Create a database user account within PostgreSQL.

Create an IAM policy that maps the database user to the IAM role associated with your EC2 instance.

Attach the IAM role to your EC2 instance.

Generate an AWS authentication token to authenticate with the database.

2. Security groups

Create a security group for your EC2 instance.

Allow inbound traffic on the necessary ports (e.g., 80 for your API, 22 for SSH).

Allow outbound traffic to the RDS instance on the PostgreSQL port (5432).

Allow outbound traffic on port 443 (HTTPS) for communication with the SSM VPC endpoint interfaces.

In both rules, add your VPC CIDR range as the destination.

3. Application code (Node.js)

Use Sequelize (or another ORM) to interact with PostgreSQL.

Install dependencies: 

```

	$ npm install express sequelize pg pg-hstore dotenv

```

Configure Sequelize with your database details in a config.js file, including environment variables for host, port, username, password, and database name.

Define your API routes in a routes/index.js file.

Set up your Express application in app.js and connect to the database.

Use a .env file to store environment variables, including database credentials and API keys.

4. Deployment

You can deploy your application using various methods, such as using a deployment script, Docker, or other CI/CD tools.

If using Docker, you can create a Dockerfile to package your application and then deploy it to an EC2 instance using Docker Compose or other container orchestration tools.


## Amazon SageMaker and PostgreSQL

Amazon SageMaker uses PostgreSQL as a data source and for storing metadata. 

Specifically, it leverages Amazon RDS for PostgreSQL for its relational database needs, enabling users to manage and query data that is used in their machine learning workflows. 

SageMaker can connect to and interact with PostgreSQL databases to access training data, store model artifacts, and manage other relevant information. 

References

Why Amazon RDS?

https://aws.amazon.com/rds/

Amazon RDS for PostgreSQL

https://aws.amazon.com/rds/postgresql/

Creating and connecting to a PostgreSQL DB instance

https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_GettingStarted.CreatingConnecting.PostgreSQL.html

