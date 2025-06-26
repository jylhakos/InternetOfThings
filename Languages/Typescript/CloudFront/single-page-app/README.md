# A single-page-app (SPA) with Typescript and React that uses AWS CloudFront

1. Create your single-page-app with React and Typescript

First, initialize a React project using create React app with the TypeScript template.

```

	$ npx create-react-app my-spa --template typescript

	$ cd my-spa

```

Install dependencies

```

	$ npm install axios

```

Create a React component to handle file downloads from CloudFront.

```

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

```
Create a React hook for fetching content from CloudFront.

```

	import { useState, useEffect } from 'react';
	import axios from 'axios';

	interface UseCloudFrontContentProps {
	  url: string;
	  autoFetch?: boolean;
	}

	interface ContentState<T> {
	  data: T | null;
	  loading: boolean;
	  error: string | null;
	}

	export const useCloudFrontContent = <T = any>({
	  url,
	  autoFetch = true
	}: UseCloudFrontContentProps) => {
	  const [state, setState] = useState<ContentState<T>>({
	    data: null,
	    loading: false,
	    error: null
	  });

	  const fetchContent = async () => {
	    setState(prev => ({ ...prev, loading: true, error: null }));
	    
	    try {
	      const response = await axios.get<T>(url, {
	        headers: {
	          'Cache-Control': 'no-cache',
	        }
	      });
	      setState({
	        data: response.data,
	        loading: false,
	        error: null
	      });
	    } catch (error) {
	      setState({
	        data: null,
	        loading: false,
	        error: error instanceof Error ? error.message : 'An error occurred'
	      });
	    }
	  };

	  useEffect(() => {
	    if (autoFetch && url) {
	      fetchContent();
	    }
	  }, [url, autoFetch]);

	  return {
	    ...state,
	    refetch: fetchContent
	  };
	};

```
Update your main App component to use CloudFront content.

```

	import React from 'react';
	import FileDownloader from './components/FileDownloader';
	import { useCloudFrontContent } from './hooks/useCloudFrontContent';
	import './App.css';

	// Configure your CloudFront distribution URL
	const CLOUDFRONT_URL = 'https://your-distribution-id.cloudfront.net';

	interface ContentItem {
	  id: string;
	  title: string;
	  filename: string;
	  description: string;
	}

	const App: React.FC = () => {
	  // Fetch content metadata from CloudFront
	  const { data: contentList, loading, error } = useCloudFrontContent<ContentItem[]>({
	    url: `${CLOUDFRONT_URL}/content-manifest.json`
	  });

	  if (loading) return <div className="loading">Loading content...</div>;
	  if (error) return <div className="error">Error: {error}</div>;

	  return (
	    <div className="App">
	      <header className="App-header">
	        <h1>My CloudFront SPA</h1>
	        <p>Download content and files from AWS CloudFront</p>
	      </header>

	      <main className="content-section">
	        <h2>Available Downloads</h2>
	        {contentList && contentList.length > 0 ? (
	          <div className="content-grid">
	            {contentList.map((item) => (
	              <div key={item.id} className="content-item">
	                <h3>{item.title}</h3>
	                <p>{item.description}</p>
	                <FileDownloader
	                  cloudFrontUrl={CLOUDFRONT_URL}
	                  fileName={item.filename}
	                  displayName={item.title}
	                />
	              </div>
	            ))}
	          </div>
	        ) : (
	          <p>No content available</p>
	        )}
	      </main>
	    </div>
	  );
	};

	export default App;

```
Create .env files

```

REACT_APP_CLOUDFRONT_PROD_URL=https://your-distribution-id.cloudfront.net
REACT_APP_AWS_REGION=us-east-1

```
Add some basic CSS styling.

Create an error handling service.

```

	export class DownloadError extends Error {
	  constructor(
	    message: string,
	    public statusCode?: number,
	    public originalError?: any
	  ) {
	    super(message);
	    this.name = 'DownloadError';
	  }
	}

	export const handleDownloadError = (error: any): DownloadError => {
	  if (error.response) {
	    // Server responded with error status
	    const statusCode = error.response.status;
	    switch (statusCode) {
	      case 403:
	        return new DownloadError('Access denied. Please check your permissions.', statusCode, error);
	      case 404:
	        return new DownloadError('File not found.', statusCode, error);
	      case 429:
	        return new DownloadError('Too many requests. Please try again later.', statusCode, error);
	      default:
	        return new DownloadError(`Server error: ${statusCode}`, statusCode, error);
	    }
	  } else if (error.request) {
	    // Network error
	    return new DownloadError('Network error. Please check your connection.', undefined, error);
	  } else {
	    // Other error
	    return new DownloadError('An unexpected error occurred.', undefined, error);
	  }
	};

```

Create environment files for different stages.

```


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

```

2. Set up AWS S3 and CloudFront

Create an S3 bucket: 

Log into your AWS Management Console and create an S3 bucket to store your static files.

Configure S3 for Static Website Hosting: 

Enable static website hosting in your S3 bucket's properties.

Create a CloudFront distribution: 

Create a CloudFront distribution that uses your S3 bucket as the origin.

Configure CloudFront for Security and Caching: 

Configure settings such as SSL/TLS certificates and caching behavior.

Set up OAC (Origin access control):

It's recommended to restrict direct access to your S3 bucket and allow CloudFront to access it through OAC. 

You can create an OAC in the CloudFront console and link it to your S3 origin in the distribution settings.

Update S3 bucket policy: 

Modify the bucket policy of your S3 bucket to allow read access from the CloudFront OAC.

CORS: 

Ensure your CloudFront distribution allows CORS headers
