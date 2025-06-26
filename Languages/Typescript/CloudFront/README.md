# A React application by TypeScript that uses AWS CloudFront

 A React application by TypeScript that uses AWS CloudFront for static files with AWS S3, while having your Node.js Express backend upload those static files.

1. Create your TypeScript React application

In your React application, create components and functionality to allow users to select and upload files.

First, initialize a React project using create React app with the TypeScript template.

```

	$ npx create-react-app my-spa --template typescript

	$ cd my-spa

```
Implement client-side routing using a library like React Router DOM to manage different views within your SPA.

Use a library like Axios to send the file upload requests from your React frontend to your Node.js Express backend's upload endpoint.

Consider using state management libraries like Redux or React Context API for complex applications.

Direct URLs (for publicly accessible files).

If the files in your S3 bucket (served by CloudFront) are publicly accessible, you can use their CloudFront URLs directly in your application.

Create an <a> tag with the href attribute set to the file's CloudFront URL and the download attribute to suggest a filename.

Example

<a href="https://your-cloudfront-domain.cloudfront.net/path/to/your/file.pdf" download="my-file.pdf">Download File</a>

Using AWS Amplify Storage (for more complex scenarios or private files): 

If you need to handle authentication, authorization, or download private files, consider using AWS Amplify's Storage module.

Use the getUrl API to generate a presigned URL that provides temporary access to the file.

You can then use this presigned URL in an <a> tag or fetch the file programmatically.

Here's the basic project structure with AWS integration.

```

	// AWS Configuration
	export const AWS_CONFIG = {
	  cloudFrontDomain: process.env.REACT_APP_CLOUDFRONT_DOMAIN || '',
	  s3BucketName: process.env.REACT_APP_S3_BUCKET || '',
	  region: process.env.REACT_APP_AWS_REGION || 'us-east-1',
	};

	// CDN URL helper
	export const getCDNUrl = (path: string): string => {
	  const baseUrl = AWS_CONFIG.cloudFrontDomain;
	  return `https://${baseUrl}/${path.startsWith('/') ? path.slice(1) : path}`;
	};

```
Run npm run build in your React project to create a production build.

2. Set up AWS S3 and CloudFront

Create an S3 bucket: 

Log into your AWS Management Console and create an S3 bucket to store your static files.

Configure S3 for Static Website Hosting: 

Enable static website hosting in your S3 bucket's properties.

Create a CloudFront distribution: 

Create a CloudFront distribution that uses your S3 bucket as the origin.

Configure CloudFront for Security and Caching: 

Configure settings such as SSL/TLS certificates and caching behavior.

Set up OAC (Origin access control):

It's recommended to restrict direct access to your S3 bucket and allow CloudFront to access it through OAC. 

You can create an OAC in the CloudFront console and link it to your S3 origin in the distribution settings.

Update S3 bucket policy: 

Modify the bucket policy of your S3 bucket to allow read access from the CloudFront OAC. 

3. Create your Node.js and Express program

Set up Express: 

Initialize your Node.js project and set up an Express.js server.

Install AWS SDK for JavaScript: 

Install the AWS SDK for JavaScript to interact with AWS services, including S3.

```

	import AWS from 'aws-sdk';
	import dotenv from 'dotenv';

	dotenv.config();

	// Configure AWS SDK
	AWS.config.update({
	  accessKeyId: process.env.AWS_ACCESS_KEY_ID,
	  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
	  region: process.env.AWS_REGION || 'us-east-1'
	});

	export const s3 = new AWS.S3();

	export const S3_BUCKET_NAME = process.env.S3_BUCKET_NAME || '';
	export const CLOUDFRONT_DOMAIN = process.env.CLOUDFRONT_DOMAIN || '';

```

Implement File upload endpoint: 

Create an API endpoint (e.g., /upload) in your Express app to handle file uploads.

Use Multer and Multer-S3: 

Utilize multer for handling file uploads and multer-s3 to seamlessly upload the files to your S3 bucket.

Configure AWS credentials: 

Securely configure your AWS credentials (e.g., using environment variables) for the backend to access your S3 bucket.

Upload static files to S3: 

Upload the contents of your React app's build folder to your S3 bucket.

In your upload endpoint, use the AWS SDK and Multer to upload the received files to your S3 bucket. 

After deploying, you may need to invalidate the CloudFront distribution's cache to ensure that users are served the latest version of your application.
