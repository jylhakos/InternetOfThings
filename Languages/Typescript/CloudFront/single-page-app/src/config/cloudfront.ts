interface CloudFrontConfig {
  distributionUrl: string;
  region: string;
}

const getCloudFrontConfig = (): CloudFrontConfig => {
  const env = process.env.NODE_ENV || 'development';
  
  switch (env) {
    case 'production':
      return {
        distributionUrl: process.env.REACT_APP_CLOUDFRONT_PROD_URL || '',
        region: process.env.REACT_APP_AWS_REGION || 'us-east-1'
      };
    case 'staging':
      return {
        distributionUrl: process.env.REACT_APP_CLOUDFRONT_STAGING_URL || '',
        region: process.env.REACT_APP_AWS_REGION || 'us-east-1'
      };
    default:
      return {
        distributionUrl: process.env.REACT_APP_CLOUDFRONT_DEV_URL || 'http://localhost:3001',
        region: 'us-east-1'
      };
  }
};

export default getCloudFrontConfig();