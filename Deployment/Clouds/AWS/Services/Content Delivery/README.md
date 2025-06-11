# Content Delivery


## CloudFront

A content delivery network (CDN) that helps you distribute your static and dynamic web content to users with low latency and high data transfer speeds. It caches content in edge locations around the world, so users can access it faster, regardless of their location.

### Static Website Hosting

Configure Static Website Hosting (Optional): 

You can enable static website hosting on your S3 bucket, but it's recommended to use a REST API endpoint and restrict access with OAC/OAI when using CloudFront for enhanced security.

Create a CloudFront distribution: 

Create a CloudFront distribution, selecting your S3 bucket as the origin domain.

Configure Origin Access Control (OAC) or Origin Access Identity (OAI): 

Restrict direct access to your S3 bucket, allowing only CloudFront to retrieve content.
