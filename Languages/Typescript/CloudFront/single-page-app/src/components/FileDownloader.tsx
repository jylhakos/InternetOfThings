import React, { useState } from 'react';
import axios from 'axios';

interface FileDownloaderProps {
  cloudFrontUrl: string;
  fileName: string;
  displayName?: string;
}

const FileDownloader: React.FC<FileDownloaderProps> = ({
  cloudFrontUrl,
  fileName,
  displayName
}) => {
  const [downloading, setDownloading] = useState(false);
  const [progress, setProgress] = useState(0);

  const downloadFile = async () => {
    try {
      setDownloading(true);
      setProgress(0);

      const response = await axios({
        method: 'GET',
        url: `${cloudFrontUrl}/${fileName}`,
        responseType: 'blob',
        onDownloadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            setProgress(percentCompleted);
          }
        },
      });

      // Create blob URL and trigger download
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = displayName || fileName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
      alert('Download failed. Please try again.');
    } finally {
      setDownloading(false);
      setProgress(0);
    }
  };

  return (
    <div className="file-downloader">
      <button
        onClick={downloadFile}
        disabled={downloading}
        className="download-btn"
      >
        {downloading ? `Downloading... ${progress}%` : `Download ${displayName || fileName}`}
      </button>
      {downloading && (
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}
    </div>
  );
};

export default FileDownloader;