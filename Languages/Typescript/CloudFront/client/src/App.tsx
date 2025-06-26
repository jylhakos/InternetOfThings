import React from 'react';
import FileUpload from './components/FileUpload';
import { UploadResult } from './types/upload';

function App() {
  const handleUploadComplete = (results: UploadResult[]) => {
    console.log('Upload completed:', results);
    // You can handle the uploaded files for example, save to state, show notifications, etc.
  };

  return (
    <div className="App" style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <header>
        <h1>React S3 file upload with CloudFront</h1>
        <p>React uploads files to AWS S3 and serves them via CloudFront CDN</p>
      </header>

      <main>
        <section style={{ marginBottom: '40px' }}>
          <h2>Single file upload</h2>
          <FileUpload
            onUploadComplete={handleUploadComplete}
            multiple={false}
          />
        </section>

        <section>
          <h2>Multiple files upload</h2>
          <FileUpload
            onUploadComplete={handleUploadComplete}
            multiple={true}
          />
        </section>
      </main>
    </div>
  );
}

export default App;