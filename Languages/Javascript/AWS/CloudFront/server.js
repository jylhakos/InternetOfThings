const express = require('express');
const cors = require('cors');
const multer = require('multer');
const { S3Client, PutObjectCommand, GetObjectCommand, DeleteObjectCommand } = require('@aws-sdk/client-s3');
const { getSignedUrl } = require('@aws-sdk/s3-request-presigner');
const path = require('path');
const fs = require('fs');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// AWS S3 configuration
const s3Client = new S3Client({
    region: process.env.AWS_REGION,
    credentials: {
        accessKeyId: process.env.AWS_ACCESS_KEY_ID,
        secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
    },
});

const BUCKET_NAME = process.env.S3_BUCKET_NAME;
const CLOUDFRONT_DOMAIN = process.env.CLOUDFRONT_DOMAIN; // e.g., 'https://d123456789.cloudfront.net'

// Multer configuration for file uploads
const storage = multer.memoryStorage();
const upload = multer({
    storage: storage,
    limits: {
        fileSize: 10 * 1024 * 1024, // 10MB limit
    },
    fileFilter: (req, file, cb) => {
        // Allow only specific file types
        const allowedTypes = /jpeg|jpg|png|gif|pdf|doc|docx/;
        const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
        const mimetype = allowedTypes.test(file.mimetype);

        if (mimetype && extname) {
            return cb(null, true);
        } else {
            cb(new Error('Invalid file type'));
        }
    }
});

// Helper function to generate unique filename
const generateFileName = (originalName) => {
    const timestamp = Date.now();
    const randomString = Math.random().toString(36).substring(2, 15);
    const extension = path.extname(originalName);
    return `uploads/${timestamp}-${randomString}${extension}`;
};

// Routes

// Health check
app.get('/api/health', (req, res) => {
    res.json({ status: 'OK', message: 'Server is running' });
});

// Upload single file to S3
app.post('/api/upload', upload.single('file'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'No file uploaded' });
        }

        const fileName = generateFileName(req.file.originalname);
        
        const uploadParams = {
            Bucket: BUCKET_NAME,
            Key: fileName,
            Body: req.file.buffer,
            ContentType: req.file.mimetype,
            // Optional: Set cache control for CloudFront
            CacheControl: 'max-age=31536000', // 1 year
        };

        const command = new PutObjectCommand(uploadParams);
        await s3Client.send(command);

        // Generate CloudFront URL
        const cloudFrontUrl = `${CLOUDFRONT_DOMAIN}/${fileName}`;
        
        res.json({
            message: 'File uploaded successfully',
            fileName: fileName,
            originalName: req.file.originalname,
            size: req.file.size,
            mimeType: req.file.mimetype,
            s3Url: `https://${BUCKET_NAME}.s3.${process.env.AWS_REGION}.amazonaws.com/${fileName}`,
            cloudFrontUrl: cloudFrontUrl,
            uploadedAt: new Date().toISOString()
        });

    } catch (error) {
        console.error('Upload error:', error);
        res.status(500).json({ error: 'Failed to upload file', details: error.message });
    }
});

// Upload multiple files to S3
app.post('/api/upload-multiple', upload.array('files', 10), async (req, res) => {
    try {
        if (!req.files || req.files.length === 0) {
            return res.status(400).json({ error: 'No files uploaded' });
        }

        const uploadPromises = req.files.map(async (file) => {
            const fileName = generateFileName(file.originalname);
            
            const uploadParams = {
                Bucket: BUCKET_NAME,
                Key: fileName,
                Body: file.buffer,
                ContentType: file.mimetype,
                CacheControl: 'max-age=31536000',
            };

            const command = new PutObjectCommand(uploadParams);
            await s3Client.send(command);

            return {
                fileName: fileName,
                originalName: file.originalname,
                size: file.size,
                mimeType: file.mimetype,
                cloudFrontUrl: `${CLOUDFRONT_DOMAIN}/${fileName}`,
                uploadedAt: new Date().toISOString()
            };
        });

        const results = await Promise.all(uploadPromises);

        res.json({
            message: 'Files uploaded successfully',
            files: results
        });

    } catch (error) {
        console.error('Multiple upload error:', error);
        res.status(500).json({ error: 'Failed to upload files', details: error.message });
    }
});

// Generate presigned URL for secure file access
app.get('/api/presigned-url/:fileName', async (req, res) => {
    try {
        const { fileName } = req.params;
        const expiresIn = req.query.expires || 3600; // Default 1 hour

        const command = new GetObjectCommand({
            Bucket: BUCKET_NAME,
            Key: fileName,
        });

        const signedUrl = await getSignedUrl(s3Client, command, { expiresIn: parseInt(expiresIn) });

        res.json({
            signedUrl: signedUrl,
            expiresIn: expiresIn,
            expiresAt: new Date(Date.now() + parseInt(expiresIn) * 1000).toISOString()
        });

    } catch (error) {
        console.error('Presigned URL error:', error);
        res.status(500).json({ error: 'Failed to generate presigned URL', details: error.message });
    }
});

// Delete a file from S3
app.delete('/api/delete/:fileName', async (req, res) => {
    try {
        const { fileName } = req.params;

        const deleteParams = {
            Bucket: BUCKET_NAME,
            Key: fileName,
        };

        const command = new DeleteObjectCommand(deleteParams);
        await s3Client.send(command);

        res.json({
            message: 'File deleted successfully',
            fileName: fileName,
            deletedAt: new Date().toISOString()
        });

    } catch (error) {
        console.error('Delete error:', error);
        res.status(500).json({ error: 'Failed to delete file', details: error.message });
    }
});

// Serve static files (for non-S3 files)
app.use('/static', express.static(path.join(__dirname, 'public')));

// Error handling middleware
app.use((error, req, res, next) => {
    if (error instanceof multer.MulterError) {
        if (error.code === 'LIMIT_FILE_SIZE') {
            return res.status(400).json({ error: 'File too large' });
        }
    }
    
    console.error('Server error:', error);
    res.status(500).json({ error: 'Internal server error' });
});

// 404 handler
app.use('*', (req, res) => {
    res.status(404).json({ error: 'Route not found' });
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
    console.log(`Health check: http://localhost:${PORT}/api/health`);
});

module.exports = app;