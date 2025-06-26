import { s3, S3_BUCKET_NAME, CLOUDFRONT_DOMAIN } from '../config/aws';
import { v4 as uuidv4 } from 'uuid';

export interface UploadResult {
  key: string;
  url: string;
  cloudFrontUrl: string;
}

export class S3Service {
  async uploadFile(
    file: Express.Multer.File,
    folder: string = 'uploads'
  ): Promise<UploadResult> {
    const fileExtension = file.originalname.split('.').pop();
    const key = `${folder}/${uuidv4()}.${fileExtension}`;

    const params = {
      Bucket: S3_BUCKET_NAME,
      Key: key,
      Body: file.buffer,
      ContentType: file.mimetype,
      ACL: 'public-read' as const,
      CacheControl: 'max-age=31536000', // 1 year cache
    };

    try {
      const result = await s3.upload(params).promise();
      
      return {
        key,
        url: result.Location,
        cloudFrontUrl: `https://${CLOUDFRONT_DOMAIN}/${key}`
      };
    } catch (error) {
      throw new Error(`Failed to upload file: ${error}`);
    }
  }

  async deleteFile(key: string): Promise<void> {
    const params = {
      Bucket: S3_BUCKET_NAME,
      Key: key,
    };

    try {
      await s3.deleteObject(params).promise();
    } catch (error) {
      throw new Error(`Failed to delete file: ${error}`);
    }
  }

  async getSignedUrl(key: string, expires: number = 3600): Promise<string> {
    const params = {
      Bucket: S3_BUCKET_NAME,
      Key: key,
      Expires: expires,
    };

    return s3.getSignedUrl('getObject', params);
  }
}