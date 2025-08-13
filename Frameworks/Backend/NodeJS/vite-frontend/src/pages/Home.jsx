import { useState, useEffect } from 'react'
import { Zap, Code, Rocket, Globe, Settings, ArrowRight } from 'lucide-react'

const Home = () => {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    setIsVisible(true)
  }, [])

  const features = [
    {
      icon: Zap,
      title: 'Lightning Fast',
      description: 'Vite provides instant server start and lightning-fast HMR for the best development experience.',
      color: '#fbbf24'
    },
    {
      icon: Code,
      title: 'Modern Development',
      description: 'Built with React 18, modern JavaScript features, and TypeScript support out of the box.',
      color: '#3b82f6'
    },
    {
      icon: Rocket,
      title: 'Optimized Builds',
      description: 'Rollup-powered builds with tree-shaking, code splitting, and optimized production bundles.',
      color: '#10b981'
    },
    {
      icon: Globe,
      title: 'Universal Compatibility',
      description: 'Works everywhere with ES modules support and legacy fallbacks for older browsers.',
      color: '#8b5cf6'
    },
    {
      icon: Settings,
      title: 'Zero Config',
      description: 'Sensible defaults with minimal configuration needed. Just start coding immediately.',
      color: '#f97316'
    }
  ]

  const stats = [
    { value: '<100ms', label: 'Cold Start Time' },
    { value: '~50ms', label: 'Hot Reload Speed' },
    { value: '90%', label: 'Smaller Bundle Size' },
    { value: '100+', label: 'Supported Frameworks' }
  ]

  return (
    <div className={`home-page ${isVisible ? 'visible' : ''}`}>
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <div className="hero-badge">
            <Zap size={16} />
            Powered by Vite
          </div>
          <h1 className="hero-title">
            Next Generation Frontend Development
          </h1>
          <p className="hero-description">
            Experience the future of web development with Vite + React. 
            Lightning-fast development server, instant hot module replacement, 
            and optimized production builds.
          </p>
          <div className="hero-actions">
            <button className="btn btn-primary btn-lg">
              Get Started
              <ArrowRight size={20} />
            </button>
            <button className="btn btn-outline btn-lg">
              Learn More
            </button>
          </div>
        </div>
        <div className="hero-visual">
          <div className="floating-card">
            <div className="code-preview">
              <div className="code-header">
                <div className="code-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <span className="code-title">App.jsx</span>
              </div>
              <div className="code-content">
                <div className="code-line">
                  <span className="code-keyword">import</span> React <span className="code-keyword">from</span> <span className="code-string">'react'</span>
                </div>
                <div className="code-line">
                  <span className="code-keyword">function</span> <span className="code-function">App</span>() {'{'}
                </div>
                <div className="code-line code-indent">
                  <span className="code-keyword">return</span> <span className="code-tag">&lt;h1&gt;</span>Hello Vite!<span className="code-tag">&lt;/h1&gt;</span>
                </div>
                <div className="code-line">{'}'}</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="stats-section">
        <div className="stats-grid">
          {stats.map((stat, index) => (
            <div key={index} className="stat-card">
              <div className="stat-value">{stat.value}</div>
              <div className="stat-label">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="section-header">
          <h2>Why Choose Vite?</h2>
          <p>Modern tooling designed for speed and developer experience</p>
        </div>
        <div className="features-grid">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <div key={index} className="feature-card">
                <div className="feature-icon" style={{ backgroundColor: feature.color + '20', color: feature.color }}>
                  <Icon size={24} />
                </div>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </div>
            )
          })}
        </div>
      </section>

      {/* Call to Action */}
      <section className="cta-section">
        <div className="cta-content">
          <h2>Ready to Build Something Amazing?</h2>
          <p>Join thousands of developers who are already building with Vite + React</p>
          <div className="cta-actions">
            <button className="btn btn-primary btn-lg">Start Building</button>
            <button className="btn btn-secondary btn-lg">View Documentation</button>
          </div>
        </div>
      </section>

      <style jsx>{`
        .home-page {
          opacity: 0;
          transform: translateY(20px);
          transition: all 0.6s ease;
        }

        .home-page.visible {
          opacity: 1;
          transform: translateY(0);
        }

        .hero-section {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: var(--space-16);
          align-items: center;
          min-height: 60vh;
          margin-bottom: var(--space-16);
        }

        .hero-content {
          max-width: 500px;
        }

        .hero-badge {
          display: inline-flex;
          align-items: center;
          gap: var(--space-2);
          background: var(--background-alt);
          color: var(--primary);
          padding: var(--space-2) var(--space-4);
          border-radius: var(--radius-xl);
          font-size: var(--font-size-sm);
          font-weight: 500;
          margin-bottom: var(--space-6);
          border: 1px solid var(--primary);
        }

        .hero-title {
          font-size: clamp(2.5rem, 5vw, 3.5rem);
          font-weight: 800;
          line-height: 1.2;
          margin-bottom: var(--space-6);
          background: linear-gradient(135deg, var(--text-primary), var(--primary));
          background-clip: text;
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }

        .hero-description {
          font-size: var(--font-size-lg);
          line-height: 1.7;
          margin-bottom: var(--space-8);
          color: var(--text-secondary);
        }

        .hero-actions {
          display: flex;
          gap: var(--space-4);
          flex-wrap: wrap;
        }

        .hero-visual {
          display: flex;
          justify-content: center;
          align-items: center;
        }

        .floating-card {
          perspective: 1000px;
          animation: float 6s ease-in-out infinite;
        }

        @keyframes float {
          0%, 100% { transform: translateY(0px) rotateY(0deg); }
          50% { transform: translateY(-20px) rotateY(5deg); }
        }

        .code-preview {
          background: var(--background);
          border: 1px solid var(--border);
          border-radius: var(--radius-xl);
          box-shadow: var(--shadow-xl);
          overflow: hidden;
          width: 350px;
        }

        .code-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: var(--space-4);
          background: var(--background-alt);
          border-bottom: 1px solid var(--border);
        }

        .code-dots {
          display: flex;
          gap: var(--space-2);
        }

        .code-dots span {
          width: 12px;
          height: 12px;
          border-radius: 50%;
          background: var(--border);
        }

        .code-dots span:nth-child(1) { background: #ff5f56; }
        .code-dots span:nth-child(2) { background: #ffbd2e; }
        .code-dots span:nth-child(3) { background: #27ca3f; }

        .code-title {
          font-size: var(--font-size-sm);
          font-weight: 500;
          color: var(--text-secondary);
        }

        .code-content {
          padding: var(--space-6);
          font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
          font-size: var(--font-size-sm);
          line-height: 1.6;
        }

        .code-line {
          margin-bottom: var(--space-2);
        }

        .code-indent {
          padding-left: var(--space-4);
        }

        .code-keyword { color: #d73a49; }
        .code-string { color: #032f62; }
        .code-function { color: #6f42c1; }
        .code-tag { color: #22863a; }

        .stats-section {
          margin-bottom: var(--space-16);
        }

        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: var(--space-6);
        }

        .stat-card {
          text-align: center;
          padding: var(--space-6);
          background: var(--background);
          border: 1px solid var(--border);
          border-radius: var(--radius-xl);
          transition: var(--transition);
        }

        .stat-card:hover {
          transform: translateY(-2px);
          box-shadow: var(--shadow);
        }

        .stat-value {
          font-size: var(--font-size-3xl);
          font-weight: 800;
          color: var(--primary);
          margin-bottom: var(--space-2);
        }

        .stat-label {
          color: var(--text-secondary);
          font-weight: 500;
        }

        .features-section {
          margin-bottom: var(--space-16);
        }

        .section-header {
          text-align: center;
          margin-bottom: var(--space-12);
        }

        .section-header h2 {
          font-size: var(--font-size-3xl);
          margin-bottom: var(--space-4);
        }

        .section-header p {
          font-size: var(--font-size-lg);
          color: var(--text-secondary);
        }

        .features-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: var(--space-8);
        }

        .feature-card {
          padding: var(--space-8);
          background: var(--background);
          border: 1px solid var(--border);
          border-radius: var(--radius-xl);
          transition: var(--transition-slow);
          text-align: center;
        }

        .feature-card:hover {
          transform: translateY(-5px);
          box-shadow: var(--shadow-lg);
        }

        .feature-icon {
          width: 60px;
          height: 60px;
          border-radius: var(--radius-xl);
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto var(--space-4);
        }

        .feature-card h3 {
          font-size: var(--font-size-xl);
          margin-bottom: var(--space-3);
          color: var(--text-primary);
        }

        .feature-card p {
          color: var(--text-secondary);
          line-height: 1.7;
          margin: 0;
        }

        .cta-section {
          background: linear-gradient(135deg, var(--primary), var(--primary-hover));
          color: white;
          padding: var(--space-16);
          border-radius: var(--radius-2xl);
          text-align: center;
          margin: var(--space-16) 0;
        }

        .cta-content h2 {
          font-size: var(--font-size-3xl);
          margin-bottom: var(--space-4);
          color: white;
        }

        .cta-content p {
          font-size: var(--font-size-lg);
          margin-bottom: var(--space-8);
          color: rgba(255, 255, 255, 0.9);
        }

        .cta-actions {
          display: flex;
          gap: var(--space-4);
          justify-content: center;
          flex-wrap: wrap;
        }

        /* Mobile Responsiveness */
        @media (max-width: 768px) {
          .hero-section {
            grid-template-columns: 1fr;
            gap: var(--space-8);
            text-align: center;
          }

          .hero-visual {
            order: -1;
          }

          .code-preview {
            width: 100%;
            max-width: 300px;
          }

          .stats-grid {
            grid-template-columns: repeat(2, 1fr);
            gap: var(--space-4);
          }

          .features-grid {
            grid-template-columns: 1fr;
            gap: var(--space-6);
          }

          .hero-actions {
            justify-content: center;
          }

          .cta-actions {
            flex-direction: column;
            align-items: center;
          }
        }

        @media (max-width: 480px) {
          .stats-grid {
            grid-template-columns: 1fr;
          }

          .hero-actions .btn {
            width: 100%;
            justify-content: center;
          }
        }
      `}</style>
    </div>
  )
}

export default Home
