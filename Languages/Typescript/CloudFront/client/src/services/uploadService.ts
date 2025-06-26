import axios, { AxiosProgressEvent } from 'axios';
import { UploadResult, ApiResponse } from '../types/upload';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

export class UploadService {
  async uploadSingleFile(
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<UploadResult> {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post<ApiResponse<UploadResult>>(
        `${API_BASE_URL}/upload/single`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent: AxiosProgressEvent) => {
            if (progressEvent.total && onProgress) {
              const percentage = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
              );
              onProgress(percentage);
            }
          },
        }
      );

      if (response.data.success && response.data.data) {
        return response.data.data;
      } else {
        throw new Error(response.data.error || 'Upload failed');
      }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(
          error.response?.data?.message || 
          error.response?.data?.error || 
          'Upload failed'
        );
      }
      throw error;
    }
  }

  async uploadMultipleFiles(
    files: File[],
    onProgress?: (progress: number) => void
  ): Promise<UploadResult[]> {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    try {
      const response = await axios.post<ApiResponse<UploadResult[]>>(
        `${API_BASE_URL}/upload/multiple`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent: AxiosProgressEvent) => {
            if (progressEvent.total && onProgress) {
              const percentage = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
              );
              onProgress(percentage);
            }
          },
        }
      );

      if (response.data.success && response.data.data) {
        return response.data.data;
      } else {
        throw new Error(response.data.error || 'Upload failed');
      }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(
          error.response?.data?.message || 
          error.response?.data?.error || 
          'Upload failed'
        );
      }
      throw error;
    }
  }

  async deleteFile(key: string): Promise<void> {
    try {
      const response = await axios.delete<ApiResponse<void>>(
        `${API_BASE_URL}/upload/${encodeURIComponent(key)}`
      );

      if (!response.data.success) {
        throw new Error(response.data.error || 'Delete failed');
      }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(
          error.response?.data?.message || 
          error.response?.data?.error || 
          'Delete failed'
        );
      }
      throw error;
    }
  }
}

export const uploadService = new UploadService();