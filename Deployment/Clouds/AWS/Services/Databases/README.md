# Databases


## RDS (Relational Database Service):

A managed relational database service that supports popular database engines like MySQL, PostgreSQL, and MariaDB. It simplifies database management by handling tasks like backups, patching, and high availability.

### Integrate with RDS

Prerequisites: 

Ensure you have an RDS instance configured and accessible.

Create IAM Role: 

Create an IAM role with permissions to access your RDS database, potentially using policies like AmazonRDSDataFullAccess.

Create RDS Proxy (Optional but Recommended): Use an RDS Proxy for better connection management and security.

Connect to RDS: 

Connect to the database using the necessary credentials and connection parameters.

Create RDS Proxy (Optional): 

Use an RDS Proxy for better connection management and security.

Connect to RDS: 

Connect to the database using the necessary credentials and connection parameters.

Interact with Database: 

Perform database operations (e.g., querying or inserting data) from your Lambda function.

