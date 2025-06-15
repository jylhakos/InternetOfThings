# Storage

AWS offers a variety of storage services, each designed for different use cases.

The key offerings are Amazon S3 for object storage, Amazon EBS for block storage, and Amazon EFS for file storage.

S3 is ideal for storing and retrieving any amount of data, EBS provides block storage for EC2 instances, and EFS offers scalable file storage for multiple EC2 instances. 

## Amazon S3 (Simple Storage Service)

An object storage service that provides scalable and durable storage for various types of data.

S3 is suitable for storing and retrieving any amount of data from anywhere.

You can store files, images, videos, and other data in S3 buckets, and access them from anywhere via the internet.

### Integrate with S3

Trigger from S3 Events:

Configure your S3 bucket to trigger your Lambda function based on events like object creation or deletion.

Lambda Function Handling:

In your Node.js code, process the S3 event data, such as bucket name and object key.

Interact with S3 Objects:

Use the AWS SDK for JavaScript to perform actions like getting object content from S3.

### Serve Static Content with S3

Create an S3 Bucket: 

Set up an S3 bucket to store your static website files (HTML, CSS, JavaScript).

Configure Static Website Hosting (Optional): 

You can enable static website hosting on your S3 bucket, but it's recommended to use a REST API endpoint and restrict access with OAC/OAI when using CloudFront for enhanced security.

## An example single-page application deployed

![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/Deployment/Clouds/AWS/Services/Storage/S3_CloudFront.png?raw=true)

A single-page application (SPA) that is deployed by using AWS CloudFormation (Infrastructure as Code) with Amazon S3 storage.

This sample application code is available in the GitHub React single-page application (SPA) repository.

## Amazon EBS (Elastic Block Storage)

Provides block-level storage volumes for use with Amazon EC2 instances. 

EBS is a good choice for data that needs persistent storage with low latency.

## Amazon EFS (Elastic File System)

A fully managed file storage service for use with EC2 instances.

EFS offers scalable, shared file storage for applications that need to share data between multiple instances.

References

Choosing an AWS storage service

https://docs.aws.amazon.com/decision-guides/latest/storage-on-aws-how-to-choose/choosing-aws-storage-service.html

Deploy a React based single-page application to Amazon S3 and CloudFront

https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/deploy-a-react-based-single-page-application-to-amazon-s3-and-cloudfront.html


React single-page application (SPA) hosted on Amazon S3 and exposed through a CloudFront.

https://github.com/aws-samples/react-cors-spa

