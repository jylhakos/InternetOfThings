import { Router, Request, Response } from 'express';
import { upload } from '../middleware/upload';
import { S3Service } from '../services/s3Service';

const router = Router();
const s3Service = new S3Service();

// Single file upload
router.post('/single', upload.single('file'), async (req: Request, res: Response) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file provided' });
    }

    const result = await s3Service.uploadFile(req.file);
    
    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({ 
      error: 'Failed to upload file',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Multiple files upload
router.post('/multiple', upload.array('files', 5), async (req: Request, res: Response) => {
  try {
    const files = req.files as Express.Multer.File[];
    
    if (!files || files.length === 0) {
      return res.status(400).json({ error: 'No files provided' });
    }

    const uploadPromises = files.map(file => s3Service.uploadFile(file));
    const results = await Promise.all(uploadPromises);
    
    res.json({
      success: true,
      data: results
    });
  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({ 
      error: 'Failed to upload files',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Delete file
router.delete('/:key(*)', async (req: Request, res: Response) => {
  try {
    const key = req.params.key;
    await s3Service.deleteFile(key);
    
    res.json({
      success: true,
      message: 'File deleted successfully'
    });
  } catch (error) {
    console.error('Delete error:', error);
    res.status(500).json({ 
      error: 'Failed to delete file',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

export default router;