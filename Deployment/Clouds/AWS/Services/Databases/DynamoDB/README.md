# DynamoDB

DynamoDB is a NoSQL database service.

To use DynamoDB on AWS, you first create a table, defining its primary key. 

Then, you can write, read, update, and query data within that table.

DynamoDB supports both key/value and document data models, allowing flexibility to structure your data.

1. Creating a DynamoDB table

Access DynamoDB: 

Navigate to the DynamoDB service in the AWS Management Console.

Create Table: Click on "Create table".

Table name: 

Choose a descriptive name for your table.

Primary Key: 

Define the primary key for your table. This is crucial for efficient data retrieval. It consists of a partition key (required) and optionally a sort key.

Table settings: 

Configure other settings like table class (standard or on-demand), read/write capacity modes (provisioned or on-demand), and any global secondary indexes.

Create: Click "Create table" to finalize the process.

2. Data Management

Writing Data: 

You can add data to your table using the AWS SDKs (available in various languages like Python, Java, etc.), the AWS CLI, or through the DynamoDB console.

Reading Data: 

Use GetItem, Query, or Scan operations to retrieve data from your table.

Updating Data: 

Use the UpdateItem operation to modify existing data.

Deleting Data: 

Use the DeleteItem operation to remove data. 

## Example: EC2, IAM and DynamoDB

To utilize DynamoDB, EC2, and IAM together when deploying an application to Amazon EC2, you should configure an IAM role with the necessary permissions for DynamoDB access and attach it to your EC2 instance. 

This allows your application, running on the EC2 instance, to interact with DynamoDB without storing explicit AWS credentials.

Here's a breakdown of the configuration process:

1. Create an IAM role

Access the IAM Console: 

Navigate to the IAM (Identity and Access Management) console in the AWS Management Console.

Create a New role: 

Choose "Roles" and then "Create role".

Select Trusted Entity: 

Choose "AWS service" as the trusted entity and select "EC2" as the use case.

Attach Policies: 

Attach the appropriate IAM policy to the role. This policy should grant the necessary permissions for DynamoDB access (e.g., AmazonDynamoDBFullAccess or a custom policy with more granular permissions).

Name and Create: 

Give the role a descriptive name and create it.

2. Attach the IAM role to the EC2 instance

Access the EC2 Console: 

Navigate to the EC2 (Elastic Compute Cloud) console in the AWS Management Console.

Select Instance: 

Choose the EC2 instance where your application is deployed.

Modify IAM role: 

Navigate to "Actions" > "Security" > "Modify IAM role".

Assign role: 

Select the newly created IAM role from the dropdown menu and update the instance.

3. Configure your application

Use AWS SDKs:

Your application should be built using the AWS SDKs for the language you are using (e.g., Python, Java, Node.js).

No need for explicit credentials:

The SDKs will automatically detect and use the IAM role's credentials when interacting with DynamoDB.

4. Testing and verification

Run the Application: 

Deploy and run your application on the EC2 instance.

Verify access: 

Ensure that the application can successfully perform the intended DynamoDB operations (read, write, etc.).

Test with no IAM role (Optional):

You can also test the application without the IAM role by detaching it from the instance and confirming that it fails to access DynamoDB, demonstrating that the role is indeed necessary and providing the required permissions.

References

Getting started with DynamoDB

https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GettingStartedDynamoDB.html
