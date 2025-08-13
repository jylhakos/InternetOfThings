import React from 'react';
import Layout from '../components/Layout';

const About = () => {
  return (
    <Layout>
      <div className="about-page">
        <div className="hero-section">
          <h1>About This Next.js Demo</h1>
          <p className="hero-text">
            A comprehensive example showcasing modern Next.js development patterns and best practices.
          </p>
        </div>

        <div className="content-grid">
          <section className="feature-card">
            <h2>🚀 Server-Side Rendering (SSR)</h2>
            <p>
              Demonstrates how to use <code>getServerSideProps</code> for dynamic content that needs to be 
              rendered on each request. Perfect for personalized or frequently changing data.
            </p>
          </section>

          <section className="feature-card">
            <h2>⚡ Static Site Generation (SSG)</h2>
            <p>
              Shows <code>getStaticProps</code> implementation for pre-rendered pages at build time. 
              Ideal for content that doesn't change often and provides excellent performance.
            </p>
          </section>

          <section className="feature-card">
            <h2>🛠 API Routes</h2>
            <p>
              Built-in API functionality with <code>/api</code> routes. Includes examples of CRUD operations, 
              dynamic routing, and proper error handling without needing a separate backend.
            </p>
          </section>

          <section className="feature-card">
            <h2>🎨 CSS-in-JS Styling</h2>
            <p>
              Utilizes Next.js built-in styled-jsx for component-scoped CSS. Provides excellent 
              developer experience with no additional setup required.
            </p>
          </section>

          <section className="feature-card">
            <h2>📱 Responsive Design</h2>
            <p>
              Mobile-first approach with responsive layouts and components. Ensures great user 
              experience across all device sizes and screen resolutions.
            </p>
          </section>

          <section className="feature-card">
            <h2>🔍 Dynamic Routing</h2>
            <p>
              Demonstrates Next.js file-based routing system with dynamic routes using brackets 
              notation like <code>[id].js</code> for flexible URL structures.
            </p>
          </section>
        </div>

        <section className="tech-stack">
          <h2>Technology Stack</h2>
          <div className="tech-list">
            <div className="tech-item">
              <h3>Next.js</h3>
              <p>React framework with SSR, SSG, and API routes</p>
            </div>
            <div className="tech-item">
              <h3>React</h3>
              <p>Component-based UI library with hooks</p>
            </div>
            <div className="tech-item">
              <h3>Styled JSX</h3>
              <p>CSS-in-JS solution built into Next.js</p>
            </div>
            <div className="tech-item">
              <h3>JavaScript ES6+</h3>
              <p>Modern JavaScript features and syntax</p>
            </div>
          </div>
        </section>

        <section className="getting-started">
          <h2>Getting Started</h2>
          <div className="steps">
            <div className="step">
              <span className="step-number">1</span>
              <div className="step-content">
                <h3>Install Dependencies</h3>
                <code>npm install</code>
              </div>
            </div>
            <div className="step">
              <span className="step-number">2</span>
              <div className="step-content">
                <h3>Run Development Server</h3>
                <code>npm run dev</code>
              </div>
            </div>
            <div className="step">
              <span className="step-number">3</span>
              <div className="step-content">
                <h3>Open Browser</h3>
                <code>http://localhost:3000</code>
              </div>
            </div>
          </div>
        </section>
      </div>

      <style jsx>{`
        .about-page {
          max-width: 1000px;
          margin: 0 auto;
        }

        .hero-section {
          text-align: center;
          margin-bottom: 3rem;
          padding: 2rem 0;
        }

        .hero-section h1 {
          font-size: 2.5rem;
          margin-bottom: 1rem;
          color: #333;
          font-weight: 700;
        }

        .hero-text {
          font-size: 1.2rem;
          color: #6c757d;
          max-width: 600px;
          margin: 0 auto;
          line-height: 1.6;
        }

        .content-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 2rem;
          margin-bottom: 3rem;
        }

        .feature-card {
          background: white;
          padding: 2rem;
          border-radius: 12px;
          border: 1px solid #e9ecef;
          transition: all 0.3s ease;
        }

        .feature-card:hover {
          transform: translateY(-3px);
          box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }

        .feature-card h2 {
          margin: 0 0 1rem 0;
          color: #0070f3;
          font-size: 1.3rem;
        }

        .feature-card p {
          color: #6c757d;
          line-height: 1.6;
          margin: 0;
        }

        .feature-card code {
          background: #f8f9fa;
          padding: 2px 4px;
          border-radius: 4px;
          font-size: 0.9em;
          color: #e83e8c;
        }

        .tech-stack {
          background: #f8f9fa;
          padding: 2rem;
          border-radius: 12px;
          margin-bottom: 3rem;
        }

        .tech-stack h2 {
          text-align: center;
          margin-bottom: 2rem;
          color: #333;
        }

        .tech-list {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1.5rem;
        }

        .tech-item {
          background: white;
          padding: 1.5rem;
          border-radius: 8px;
          text-align: center;
        }

        .tech-item h3 {
          margin: 0 0 0.5rem 0;
          color: #0070f3;
          font-size: 1.1rem;
        }

        .tech-item p {
          margin: 0;
          color: #6c757d;
          font-size: 0.9rem;
        }

        .getting-started {
          background: white;
          padding: 2rem;
          border-radius: 12px;
          border: 1px solid #e9ecef;
        }

        .getting-started h2 {
          text-align: center;
          margin-bottom: 2rem;
          color: #333;
        }

        .steps {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .step {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .step-number {
          background: #0070f3;
          color: white;
          width: 40px;
          height: 40px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          flex-shrink: 0;
        }

        .step-content h3 {
          margin: 0 0 0.25rem 0;
          color: #333;
          font-size: 1.1rem;
        }

        .step-content code {
          background: #f8f9fa;
          padding: 0.5rem 1rem;
          border-radius: 6px;
          font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
          color: #0070f3;
          display: inline-block;
        }

        @media (max-width: 768px) {
          .hero-section h1 {
            font-size: 2rem;
          }

          .content-grid {
            grid-template-columns: 1fr;
            gap: 1.5rem;
          }

          .feature-card {
            padding: 1.5rem;
          }

          .tech-stack {
            padding: 1.5rem;
          }

          .tech-list {
            grid-template-columns: 1fr;
          }

          .getting-started {
            padding: 1.5rem;
          }

          .step {
            flex-direction: column;
            text-align: center;
          }

          .step-content {
            text-align: center;
          }
        }
      `}</style>
    </Layout>
  );
};

export default About;
