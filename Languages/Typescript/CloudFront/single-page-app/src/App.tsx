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