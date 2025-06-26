import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { uploadService } from '../services/uploadService';
import { UploadResult } from '../types/upload';

interface FileUploadProps {
  onUploadComplete?: (results: UploadResult[]) => void;
  multiple?: boolean;
  accept?: Record<string, string[]>;
  maxSize?: number;
}

const FileUpload: React.FC<FileUploadProps> = ({
  onUploadComplete,
  multiple = false,
  accept = {
    'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.webp'],
    'application/pdf': ['.pdf'],
    'text/plain': ['.txt'],
  },
  maxSize = 10 * 1024 * 1024, // 10MB
}) => {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [uploadedFiles, setUploadedFiles] = useState<UploadResult[]>([]);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    setUploading(true);
    setError(null);
    setProgress(0);

    try {
      let results: UploadResult[] = [];

      if (multiple) {
        results = await uploadService.uploadMultipleFiles(
          acceptedFiles,
          setProgress
        );
      } else {
        const result = await uploadService.uploadSingleFile(
          acceptedFiles[0],
          setProgress
        );
        results = [result];
      }

      setUploadedFiles(prev => [...prev, ...results]);
      onUploadComplete?.(results);
      setProgress(100);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  }, [multiple, onUploadComplete]);

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept,
    maxSize,
    multiple,
    disabled: uploading,
  });

  const handleDelete = async (key: string) => {
    try {
      await uploadService.deleteFile(key);
      setUploadedFiles(prev => prev.filter(file => file.key !== key));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Delete failed');
    }
  };

  return (
    <div className="file-upload">
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'active' : ''} ${uploading ? 'disabled' : ''}`}
        style={{
          border: '2px dashed #ccc',
          borderRadius: '8px',
          padding: '40px',
          textAlign: 'center',
          cursor: uploading ? 'not-allowed' : 'pointer',
          backgroundColor: isDragActive ? '#f0f8ff' : '#fafafa',
        }}
      >
        <input {...getInputProps()} />
        {uploading ? (
          <div>
            <p>Uploading... {progress}%</p>
            <div
              style={{
                width: '100%',
                height: '10px',
                backgroundColor: '#e0e0e0',
                borderRadius: '5px',
                overflow: 'hidden',
              }}
            >
              <div
                style={{
                  width: `${progress}%`,
                  height: '100%',
                  backgroundColor: '#4caf50',
                  transition: 'width 0.3s ease',
                }}
              />
            </div>
          </div>
        ) : (
          <div>
            {isDragActive ? (
              <p>Drop the files here...</p>
            ) : (
              <p>
                Drag & drop {multiple ? 'files' : 'a file'} here, or click to select
              </p>
            )}
          </div>
        )}
      </div>

      {fileRejections.length > 0 && (
        <div style={{ color: 'red', marginTop: '10px' }}>
          <p>Some files were rejected:</p>
          <ul>
            {fileRejections.map(({ file, errors }) => (
              <li key={file.name}>
                {file.name} - {errors.map(e => e.message).join(', ')}
              </li>
            ))}
          </ul>
        </div>
      )}

      {error && (
        <div style={{ color: 'red', marginTop: '10px' }}>
          <p>Error: {error}</p>
        </div>
      )}

      {uploadedFiles.length > 0 && (
        <div style={{ marginTop: '20px' }}>
          <h3>Uploaded Files:</h3>
          <ul>
            {uploadedFiles.map((file) => (
              <li key={file.key} style={{ marginBottom: '10px' }}>
                <div>
                  <strong>Key:</strong> {file.key}
                </div>
                <div>
                  <strong>S3 URL:</strong>{' '}
                  <a href={file.url} target="_blank" rel="noopener noreferrer">
                    {file.url}
                  </a>
                </div>
                <div>
                  <strong>CloudFront URL:</strong>{' '}
                  <a href={file.cloudFrontUrl} target="_blank" rel="noopener noreferrer">
                    {file.cloudFrontUrl}
                  </a>
                </div>
                <button
                  onClick={() => handleDelete(file.key)}
                  style={{
                    marginTop: '5px',
                    padding: '5px 10px',
                    backgroundColor: '#f44336',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                  }}
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default FileUpload;