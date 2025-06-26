import React, { useState } from 'react';
import axios from 'axios';

const FileUpload = () => {
    const [selectedFiles, setSelectedFiles] = useState([]);
    const [uploading, setUploading] = useState(false);
    const [uploadedFiles, setUploadedFiles] = useState([]);
    const [uploadProgress, setUploadProgress] = useState(0);

    const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001/api';

    const handleFileSelect = (event) => {
        const files = Array.from(event.target.files);
        setSelectedFiles(files);
    };

    const uploadSingleFile = async (file) => {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
                onUploadProgress: (progressEvent) => {
                    const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                    setUploadProgress(progress);
                },
            });

            return response.data;
        } catch (error) {
            console.error('Upload error:', error);
            throw error;
        }
    };

    const uploadMultipleFiles = async () => {
        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append('files', file);
        });

        try {
            const response = await axios.post(`${API_BASE_URL}/upload-multiple`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
                onUploadProgress: (progressEvent) => {
                    const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                    setUploadProgress(progress);
                },
            });

            return response.data;
        } catch (error) {
            console.error('Multiple upload error:', error);
            throw error;
        }
    };

    const handleUpload = async () => {
        if (selectedFiles.length === 0) return;

        setUploading(true);
        setUploadProgress(0);

        try {
            let result;
            
            if (selectedFiles.length === 1) {
                result = await uploadSingleFile(selectedFiles[0]);
                setUploadedFiles(prev => [...prev, result]);
            } else {
                result = await uploadMultipleFiles();
                setUploadedFiles(prev => [...prev, ...result.files]);
            }

            setSelectedFiles([]);
            setUploadProgress(100);
            
            // Reset progress after success
            setTimeout(() => setUploadProgress(0), 2000);

        } catch (error) {
            console.error('Upload failed:', error);
            alert('Upload failed: ' + (error.response?.data?.error || error.message));
        } finally {
            setUploading(false);
        }
    };

    const deleteFile = async (fileName) => {
        try {
            await axios.delete(`${API_BASE_URL}/delete/${fileName}`);
            setUploadedFiles(prev => prev.filter(file => file.fileName !== fileName));
        } catch (error) {
            console.error('Delete error:', error);
            alert('Delete failed: ' + (error.response?.data?.error || error.message));
        }
    };

    const getPresignedUrl = async (fileName) => {
        try {
            const response = await axios.get(`${API_BASE_URL}/presigned-url/${fileName}`);
            window.open(response.data.signedUrl, '_blank');
        } catch (error) {
            console.error('Presigned URL error:', error);
            alert('Failed to get secure URL: ' + (error.response?.data?.error || error.message));
        }
    };

    return (
        <div className="file-upload-container">
            <h2>File Upload to AWS S3 via CloudFront</h2>
            
            <div className="upload-section">
                <input
                    type="file"
                    multiple
                    onChange={handleFileSelect}
                    accept=".jpg,.jpeg,.png,.gif,.pdf,.doc,.docx"
                />
                
                {selectedFiles.length > 0 && (
                    <div className="selected-files">
                        <h3>Selected Files:</h3>
                        <ul>
                            {selectedFiles.map((file, index) => (
                                <li key={index}>
                                    {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

                <button 
                    onClick={handleUpload}
                    disabled={uploading || selectedFiles.length === 0}
                    className="upload-button"
                >
                    {uploading ? 'Uploading...' : 'Upload Files'}
                </button>

                {uploading && (
                    <div className="progress-bar">
                        <div 
                            className="progress-fill" 
                            style={{ width: `${uploadProgress}%` }}
                        ></div>
                        <span className="progress-text">{uploadProgress}%</span>
                    </div>
                )}
            </div>

            <div className="uploaded-files-section">
                <h3>Uploaded Files</h3>
                {uploadedFiles.length === 0 ? (
                    <p>No files uploaded yet.</p>
                ) : (
                    <div className="uploaded-files-grid">
                        {uploadedFiles.map((file, index) => (
                            <div key={index} className="file-card">
                                <div className="file-info">
                                    <h4>{file.originalName || file.fileName}</h4>
                                    <p>Size: {(file.size / 1024 / 1024).toFixed(2)} MB</p>
                                    <p>Type: {file.mimeType}</p>
                                    <p>Uploaded: {new Date(file.uploadedAt).toLocaleString()}</p>
                                </div>
                                
                                <div className="file-actions">
                                    <a 
                                        href={file.cloudFrontUrl} 
                                        target="_blank" 
                                        rel="noopener noreferrer"
                                        className="view-button"
                                    >
                                        View (CloudFront)
                                    </a>
                                    
                                    <button 
                                        onClick={() => getPresignedUrl(file.fileName)}
                                        className="secure-view-button"
                                    >
                                        Secure View
                                    </button>
                                    
                                    <button 
                                        onClick={() => deleteFile(file.fileName)}
                                        className="delete-button"
                                    >
                                        Delete
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default FileUpload;