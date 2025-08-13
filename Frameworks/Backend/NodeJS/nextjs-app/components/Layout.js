import React from 'react';

const Layout = ({ children }) => {
  return (
    <div className="layout">
      <header className="header">
        <nav className="nav">
          <div className="nav-container">
            <h1 className="nav-title">Next.js Demo App</h1>
            <ul className="nav-links">
              <li><a href="/" className="nav-link">Home</a></li>
              <li><a href="/products" className="nav-link">Products</a></li>
              <li><a href="/about" className="nav-link">About</a></li>
            </ul>
          </div>
        </nav>
      </header>

      <main className="main-content">
        {children}
      </main>

      <footer className="footer">
        <p>&copy; 2024 Next.js Demo App. Built with Next.js and React.</p>
      </footer>

      <style jsx>{`
        .layout {
          min-height: 100vh;
          display: flex;
          flex-direction: column;
        }

        .header {
          background: #0070f3;
          color: white;
          padding: 1rem 0;
        }

        .nav-container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 0 1rem;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .nav-title {
          font-size: 1.5rem;
          font-weight: bold;
          margin: 0;
        }

        .nav-links {
          list-style: none;
          display: flex;
          gap: 2rem;
          margin: 0;
          padding: 0;
        }

        .nav-link {
          color: white;
          text-decoration: none;
          font-weight: 500;
          transition: opacity 0.2s;
        }

        .nav-link:hover {
          opacity: 0.8;
        }

        .main-content {
          flex: 1;
          max-width: 1200px;
          margin: 0 auto;
          padding: 2rem 1rem;
          width: 100%;
        }

        .footer {
          background: #f8f9fa;
          border-top: 1px solid #e9ecef;
          padding: 1rem;
          text-align: center;
          color: #6c757d;
        }

        .footer p {
          margin: 0;
        }

        @media (max-width: 768px) {
          .nav-container {
            flex-direction: column;
            gap: 1rem;
          }

          .nav-links {
            gap: 1rem;
          }

          .main-content {
            padding: 1rem;
          }
        }
      `}</style>
    </div>
  );
};

export default Layout;
