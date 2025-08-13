import { Link, useLocation } from 'react-router-dom'
import { Home, Package, Users, Info, Menu, X } from 'lucide-react'
import { useState } from 'react'

const Layout = ({ children }) => {
  const location = useLocation()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  const navigation = [
    { name: 'Home', href: '/', icon: Home },
    { name: 'Products', href: '/products', icon: Package },
    { name: 'Users', href: '/users', icon: Users },
    { name: 'About', href: '/about', icon: Info },
  ]

  const isActive = (path) => location.pathname === path

  return (
    <div className="layout">
      <header className="header">
        <div className="container">
          <div className="header-content">
            <Link to="/" className="logo">
              <div className="logo-icon">⚡</div>
              <span>Vite + React</span>
            </Link>

            {/* Desktop Navigation */}
            <nav className="desktop-nav">
              {navigation.map((item) => {
                const Icon = item.icon
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`nav-link ${isActive(item.href) ? 'active' : ''}`}
                  >
                    <Icon size={18} />
                    {item.name}
                  </Link>
                )
              })}
            </nav>

            {/* Mobile Menu Button */}
            <button
              className="mobile-menu-btn"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              aria-label="Toggle menu"
            >
              {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>

          {/* Mobile Navigation */}
          {isMobileMenuOpen && (
            <nav className="mobile-nav">
              {navigation.map((item) => {
                const Icon = item.icon
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`mobile-nav-link ${isActive(item.href) ? 'active' : ''}`}
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    <Icon size={18} />
                    {item.name}
                  </Link>
                )
              })}
            </nav>
          )}
        </div>
      </header>

      <main className="main-content">
        <div className="container">
          {children}
        </div>
      </main>

      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <p>&copy; 2024 Vite + React Demo. Fast development with modern tooling.</p>
            <div className="footer-links">
              <a href="https://vitejs.dev" target="_blank" rel="noopener noreferrer">
                Vite
              </a>
              <a href="https://reactjs.org" target="_blank" rel="noopener noreferrer">
                React
              </a>
              <a href="https://github.com" target="_blank" rel="noopener noreferrer">
                GitHub
              </a>
            </div>
          </div>
        </div>
      </footer>

      <style jsx>{`
        .layout {
          min-height: 100vh;
          display: flex;
          flex-direction: column;
        }

        .header {
          background: var(--background);
          border-bottom: 1px solid var(--border);
          position: sticky;
          top: 0;
          z-index: var(--z-sticky);
          backdrop-filter: blur(10px);
          background: rgba(255, 255, 255, 0.95);
        }

        .header-content {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: var(--space-4) 0;
        }

        .logo {
          display: flex;
          align-items: center;
          gap: var(--space-3);
          font-size: var(--font-size-xl);
          font-weight: 700;
          color: var(--text-primary);
          text-decoration: none;
        }

        .logo:hover {
          color: var(--primary);
          text-decoration: none;
        }

        .logo-icon {
          font-size: var(--font-size-2xl);
          background: linear-gradient(135deg, var(--primary), var(--primary-hover));
          background-clip: text;
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }

        .desktop-nav {
          display: flex;
          align-items: center;
          gap: var(--space-8);
        }

        .nav-link {
          display: flex;
          align-items: center;
          gap: var(--space-2);
          padding: var(--space-2) var(--space-4);
          border-radius: var(--radius);
          color: var(--text-secondary);
          text-decoration: none;
          font-weight: 500;
          transition: var(--transition);
        }

        .nav-link:hover {
          color: var(--primary);
          background: var(--background-alt);
          text-decoration: none;
        }

        .nav-link.active {
          color: var(--primary);
          background: var(--background-alt);
        }

        .mobile-menu-btn {
          display: none;
          background: none;
          border: none;
          color: var(--text-primary);
          cursor: pointer;
          padding: var(--space-2);
          border-radius: var(--radius);
          transition: var(--transition);
        }

        .mobile-menu-btn:hover {
          background: var(--background-alt);
        }

        .mobile-nav {
          display: none;
          flex-direction: column;
          gap: var(--space-2);
          padding: var(--space-4) 0;
          border-top: 1px solid var(--border);
        }

        .mobile-nav-link {
          display: flex;
          align-items: center;
          gap: var(--space-3);
          padding: var(--space-3) var(--space-4);
          color: var(--text-secondary);
          text-decoration: none;
          font-weight: 500;
          border-radius: var(--radius);
          transition: var(--transition);
        }

        .mobile-nav-link:hover {
          color: var(--primary);
          background: var(--background-alt);
          text-decoration: none;
        }

        .mobile-nav-link.active {
          color: var(--primary);
          background: var(--background-alt);
        }

        .main-content {
          flex: 1;
          padding: var(--space-8) 0;
        }

        .footer {
          background: var(--background-alt);
          border-top: 1px solid var(--border);
          padding: var(--space-6) 0;
        }

        .footer-content {
          display: flex;
          justify-content: space-between;
          align-items: center;
          color: var(--text-secondary);
          font-size: var(--font-size-sm);
        }

        .footer-links {
          display: flex;
          gap: var(--space-4);
        }

        .footer-links a {
          color: var(--text-secondary);
          text-decoration: none;
          transition: var(--transition);
        }

        .footer-links a:hover {
          color: var(--primary);
          text-decoration: none;
        }

        /* Mobile Styles */
        @media (max-width: 768px) {
          .desktop-nav {
            display: none;
          }

          .mobile-menu-btn {
            display: block;
          }

          .mobile-nav {
            display: flex;
          }

          .footer-content {
            flex-direction: column;
            gap: var(--space-4);
            text-align: center;
          }
        }
      `}</style>
    </div>
  )
}

export default Layout
