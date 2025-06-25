# Content Delivery


## CloudFront

A content delivery network (CDN) that helps you distribute your static and dynamic web content to users with low latency and high data transfer speeds. 

CloudFront caches content in edge locations around the world, so users can access it faster, regardless of their location.

### Static Website Hosting

Configure Static Website Hosting (Optional): 

You can enable static website hosting on your S3 bucket, but it's recommended to use a REST API endpoint and restrict access with OAC/OAI when using CloudFront for enhanced security.

Create a CloudFront distribution: 

Create a CloudFront distribution, selecting your S3 bucket as the origin domain.

Configure Origin Access Control (OAC) or Origin Access Identity (OAI): 

Restrict direct access to your S3 bucket, allowing only CloudFront to retrieve content.

### The configuration of Content Delivery Network (CDN) for your web application

CloudFront acts as a content delivery network (CDN) that caches your web application's static files at edge locations closer to your users, reducing latency and improving page load times.

Follow below steps to configure your web application with Javascript to distribute content via AWS CloudFront.

1. Prepare your content in an S3 bucket

Create an S3 bucket: 

This bucket will serve as the origin for your CloudFront distribution, storing your static web content like HTML, CSS, JavaScript files, and images. 

You can create one via the AWS S3 console, making sure to follow naming conventions.

Upload your web application files:

Place your Javascript web application files into the S3 bucket.

2. Configure a CloudFront distribution

Create a distribution: 

Go to the CloudFront console in the AWS Management Console and initiate the creation of a new distribution.

Choose "Create Distribution" and the Web distribution type.

Choose "Website" for "Origin Settings" if your bucket has static website hosting enabled.

Under "Origin Domain Name", select your S3 bucket.

Specify your S3 bucket as the origin: 

Select your S3 bucket from the list as the origin for the distribution.

Configure cache behavior: 

Define how CloudFront should cache your content. 

For static content like Javascript files, you can set a long time-to-live (TTL) to maximize caching and improve performance. 

For dynamic content, you might consider shorter TTLs or "no cache" settings.

Configure other settings like viewer protocol policy (HTTPS only or redirect HTTP to HTTPS).

Set up security: 

Ensure you enable HTTPS for secure content delivery between viewers and CloudFront. 

You can also consider setting up Origin Access Control (OAC) to restrict direct access to your S3 bucket, ensuring users can only access content through CloudFront. 

Origin Access Identity (OAI):

To restrict direct access to your S3 bucket, use an Origin Access Identity (OAI) with your CloudFront distribution which ensures that only CloudFront can access the S3 bucket's content.

This is now the recommended approach for restricting access to S3 origins.

Configure distribution settings:

Set other desired options, such as logging, geo-restriction if needed, and access control.

Deploy the distribution: 

CloudFront will take some time to deploy the distribution across its edge locations globally.

Record the domain name: 

Once deployed, note down the CloudFront domain name assigned to your distribution.

3. Configure your web application

Follow the steps below to update your web application to distribute the CloudFront domain name to browsers.

Identify the S3 URLs:

In your web application, locate all instances where you are currently using the S3 bucket URL to access content (e.g., images, scripts, etc.).

HTTPS:

Ensure that your CloudFront distribution is configured to use HTTPS for secure connections.

Replace with CloudFront URLs:

Replace these S3 URLs with the corresponding URLs from your CloudFront distribution (either the default distribution domain or your custom domain).

Use the CloudFront domain name: 

Update your web application's configuration or code to use the CloudFront domain name instead of the direct S3 bucket URL to access content. 

This allows users to access your content via the distributed, cached version.

Consider using environment variables:

For easier management and flexibility, you can store the CloudFront domain name in an environment variable and use it in your application code.

For example your S3 bucket URL is my-bucket.s3.amazonaws.com/images/logo.png and your CloudFront distribution domain is d1234567890abcdef.cloudfront.net. 

S3 bucket URL in your code

```

	const imageUrl = 'http://my-bucket.s3.amazonaws.com/images/logo.png';

```

You would change the S3 bucket URL to CloudFront distribution domain in your code.

```

	const imageUrl = 'http://d1234567890abcdef.cloudfront.net/images/logo.png';

```

References

Get started with a CloudFront standard distribution

https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/GettingStarted.SimpleDistribution.html

