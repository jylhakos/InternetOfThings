const { S3Client } = require('@aws-sdk/client-s3');
const { CloudFrontClient } = require('@aws-sdk/client-cloudfront');

// S3 client configuration
const createS3Client = () => {
    return new S3Client({
        region: process.env.AWS_REGION,
        credentials: {
            accessKeyId: process.env.AWS_ACCESS_KEY_ID,
            secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
        },
    });
};

// CloudFront client configuration
const createCloudFrontClient = () => {
    return new CloudFrontClient({
        region: process.env.AWS_REGION,
        credentials: {
            accessKeyId: process.env.AWS_ACCESS_KEY_ID,
            secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
        },
    });
};

// S3 Bucket CORS configuration (apply this to your S3 bucket)
const corsConfiguration = {
    CORSRules: [
        {
            AllowedHeaders: ["*"],
            AllowedMethods: ["GET", "PUT", "POST", "DELETE", "HEAD"],
            AllowedOrigins: ["*"], // In production, specify your domain
            ExposeHeaders: ["ETag", "x-amz-meta-custom-header"],
            MaxAgeSeconds: 3000
        }
    ]
};

// S3 bucket policy for CloudFront access
const bucketPolicyForCloudFront = {
    Version: "2012-10-17",
    Statement: [
        {
            Sid: "AllowCloudFrontServicePrincipalReadOnly",
            Effect: "Allow",
            Principal: {
                Service: "cloudfront.amazonaws.com"
            },
            Action: "s3:GetObject",
            Resource: `arn:aws:s3:::${process.env.S3_BUCKET_NAME}/*`,
            Condition: {
                StringEquals: {
                    "AWS:SourceArn": `arn:aws:cloudfront::${process.env.AWS_ACCOUNT_ID}:distribution/${process.env.CLOUDFRONT_DISTRIBUTION_ID}`
                }
            }
        }
    ]
};

module.exports = {
    createS3Client,
    createCloudFrontClient,
    corsConfiguration,
    bucketPolicyForCloudFront
};