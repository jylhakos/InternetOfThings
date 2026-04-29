import React, { useState, useRef } from 'react';
import { Upload, File, AlertCircle, CheckCircle, X } from 'lucide-react';
import { documentAPI } from '../services/api';

const DocumentUpload = () => {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef();

  const [metadata, setMetadata] = useState({
    title: '',
    category: '',
    tags: ''
  });

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = async (file) => {
    setError(null);
    setUploadResult(null);
    setUploading(true);
    setUploadProgress(0);

    try {
      // Validate file
      const maxSize = 50 * 1024 * 1024; // 50MB
      if (file.size > maxSize) {
        throw new Error('File size must be less than 50MB');
      }

      const allowedTypes = ['application/pdf', 'text/plain', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/markdown'];
      if (!allowedTypes.includes(file.type) && !file.name.endsWith('.md')) {
        throw new Error('Unsupported file type. Please use PDF, TXT, DOCX, or Markdown files.');
      }

      // Prepare metadata
      const fileMetadata = {
        title: metadata.title || file.name,
        category: metadata.category || 'general',
        tags: metadata.tags ? metadata.tags.split(',').map(tag => tag.trim()) : []
      };

      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      // Upload file
      const result = await documentAPI.upload(file, fileMetadata);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      setUploadResult(result);
      
      // Reset form
      setMetadata({ title: '', category: '', tags: '' });
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }

    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setUploading(false);
    }
  };

  const clearResult = () => {
    setUploadResult(null);
    setError(null);
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Upload Document</h2>
        
        {/* Metadata Form */}
        <div className="mb-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Title (optional)
            </label>
            <input
              type="text"
              value={metadata.title}
              onChange={(e) => setMetadata({...metadata, title: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Document title"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Category (optional)
            </label>
            <select
              value={metadata.category}
              onChange={(e) => setMetadata({...metadata, category: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select category</option>
              <option value="technical">Technical</option>
              <option value="business">Business</option>
              <option value="research">Research</option>
              <option value="documentation">Documentation</option>
              <option value="other">Other</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tags (optional, comma-separated)
            </label>
            <input
              type="text"
              value={metadata.tags}
              onChange={(e) => setMetadata({...metadata, tags: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="AI, machine learning, RAG"
            />
          </div>
        </div>

        {/* Upload Area */}
        <div
          className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors duration-200 ${
            dragActive
              ? 'border-blue-400 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          } ${uploading ? 'pointer-events-none opacity-50' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            ref={fileInputRef}
            type="file"
            onChange={handleChange}
            accept=".pdf,.txt,.docx,.md"
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            disabled={uploading}
          />
          
          <div className="space-y-4">
            <Upload className="mx-auto h-12 w-12 text-gray-400" />
            <div>
              <p className="text-lg text-gray-600">
                Drag and drop your document here, or{' '}
                <span className="text-blue-600 font-medium">click to browse</span>
              </p>
              <p className="text-sm text-gray-500 mt-2">
                Supports PDF, TXT, DOCX, and Markdown files (max 50MB)
              </p>
            </div>
          </div>
        </div>

        {/* Upload Progress */}
        {uploading && (
          <div className="mt-4">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>Uploading and processing...</span>
              <span>{uploadProgress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          </div>
        )}

        {/* Success Result */}
        {uploadResult && (
          <div className="mt-4 bg-green-50 border border-green-200 rounded-md p-4">
            <div className="flex">
              <CheckCircle className="h-5 w-5 text-green-400" />
              <div className="ml-3 flex-1">
                <h3 className="text-sm font-medium text-green-800">
                  Document uploaded successfully!
                </h3>
                <div className="mt-2 text-sm text-green-700">
                  <p><strong>File:</strong> {uploadResult.document.filename}</p>
                  <p><strong>Chunks created:</strong> {uploadResult.document.chunk_count}</p>
                  <p><strong>Size:</strong> {(uploadResult.document.file_size / 1024).toFixed(1)} KB</p>
                </div>
              </div>
              <button
                onClick={clearResult}
                className="ml-4 text-green-400 hover:text-green-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="mt-4 bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <AlertCircle className="h-5 w-5 text-red-400" />
              <div className="ml-3 flex-1">
                <h3 className="text-sm font-medium text-red-800">Upload failed</h3>
                <p className="mt-2 text-sm text-red-700">{error}</p>
              </div>
              <button
                onClick={() => setError(null)}
                className="ml-4 text-red-400 hover:text-red-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentUpload;
