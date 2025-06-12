# Storage

## S3 (Simple Storage Service)

An object storage service that provides scalable and durable storage for various types of data. You can store files, images, videos, and other data in S3 buckets, and access them from anywhere via the internet.

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

References

Deploy a React based single-page application to Amazon S3 and CloudFront

https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/deploy-a-react-based-single-page-application-to-amazon-s3-and-cloudfront.html


React single-page application (SPA) hosted on Amazon S3 and exposed through a CloudFront.

https://github.com/aws-samples/react-cors-spa

