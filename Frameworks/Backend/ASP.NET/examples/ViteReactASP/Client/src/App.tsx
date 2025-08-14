import React, { useState, useEffect } from 'react';
import './App.css';

// Types for weather forecast
interface WeatherForecast {
  date: string;
  temperatureC: number;
  temperatureF: number;
  summary: string;
}

interface ApiResponse<T> {
  data?: T;
  error?: string;
  loading: boolean;
}

// Custom hook for API calls
function useApi<T>(url: string): ApiResponse<T> {
  const [data, setData] = useState<T | undefined>();
  const [error, setError] = useState<string | undefined>();
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(undefined);
        
        console.log('🌐 Fetching data from:', url);
        
        const response = await fetch(url);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status} - ${response.statusText}`);
        }
        
        const result = await response.json();
        console.log('✅ Data received:', result);
        setData(result);
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
        console.error('❌ API Error:', errorMessage);
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [url]);

  return { data, error, loading };
}

// Weather component
const WeatherForecast: React.FC = () => {
  const { data: forecasts, error, loading } = useApi<WeatherForecast[]>('/api/weatherforecast');
  const [refreshKey, setRefreshKey] = useState<number>(0);

  // Force refresh by changing the key
  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
    window.location.reload(); // Simple refresh for demo
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading weather data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <h2>⚠️ Error Loading Data</h2>
        <p>Error: {error}</p>
        <button onClick={handleRefresh} className="retry-btn">
          🔄 Retry
        </button>
        <div className="error-details">
          <details>
            <summary>Troubleshooting Tips</summary>
            <ul>
              <li>Ensure the ASP.NET Core backend is running on https://localhost:7042</li>
              <li>Check if CORS is properly configured</li>
              <li>Verify the API endpoint is accessible</li>
              <li>Check the browser's network tab for more details</li>
            </ul>
          </details>
        </div>
      </div>
    );
  }

  return (
    <div className="weather-section">
      <div className="section-header">
        <h2>🌤️ Weather Forecast</h2>
        <p>Data fetched from ASP.NET Core backend via Vite proxy</p>
        <button onClick={handleRefresh} className="refresh-btn">
          🔄 Refresh Data
        </button>
      </div>

      {forecasts && forecasts.length > 0 ? (
        <div className="weather-grid">
          {forecasts.map((forecast, index) => (
            <div key={index} className="weather-card">
              <div className="weather-date">
                {new Date(forecast.date).toLocaleDateString('en-US', {
                  weekday: 'short',
                  month: 'short',
                  day: 'numeric'
                })}
              </div>
              <div className="weather-temp">
                <span className="temp-c">{forecast.temperatureC}°C</span>
                <span className="temp-f">({forecast.temperatureF}°F)</span>
              </div>
              <div className="weather-summary">
                {forecast.summary}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="no-data">
          <p>No weather data available</p>
        </div>
      )}
    </div>
  );
};

// API Status component
const ApiStatus: React.FC = () => {
  const { data: health, error, loading } = useApi<{ status: string; timestamp: string; environment: string }>('/health');

  return (
    <div className="api-status">
      <h3>🔧 API Status</h3>
      {loading && <span className="status-loading">Checking...</span>}
      {error && <span className="status-error">❌ Error: {error}</span>}
      {health && (
        <div className="status-success">
          ✅ Status: {health.status} | Environment: {health.environment}
          <br />
          <small>Last checked: {new Date(health.timestamp).toLocaleTimeString()}</small>
        </div>
      )}
    </div>
  );
};

// Main App component
const App: React.FC = () => {
  const [currentTime, setCurrentTime] = useState<string>('');

  useEffect(() => {
    // Update current time every second
    const timer = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-content">
          <h1>⚛️ React + ASP.NET Core with Vite</h1>
          <p className="subtitle">
            Modern full-stack development with hot module replacement
          </p>
          <div className="build-info">
            <span>Build: {__APP_VERSION__}</span>
            <span>Time: {currentTime}</span>
          </div>
        </div>
      </header>

      <main className="main-content">
        <section className="intro-section">
          <h2>🚀 Features Demonstrated</h2>
          <div className="features-grid">
            <div className="feature-card">
              <h3>⚡ Vite Development</h3>
              <p>Lightning-fast HMR and optimized builds</p>
            </div>
            <div className="feature-card">
              <h3>🔄 API Proxy</h3>
              <p>Seamless communication with ASP.NET Core</p>
            </div>
            <div className="feature-card">
              <h3>🎨 TypeScript</h3>
              <p>Type-safe development with React</p>
            </div>
            <div className="feature-card">
              <h3>📦 Production Ready</h3>
              <p>Optimized builds for deployment</p>
            </div>
          </div>
        </section>

        <WeatherForecast />
        
        <section className="tech-stack">
          <h2>🛠️ Technology Stack</h2>
          <div className="stack-list">
            <div className="stack-item">
              <strong>Frontend:</strong> React 18, TypeScript, Vite 5
            </div>
            <div className="stack-item">
              <strong>Backend:</strong> ASP.NET Core 8, Web API
            </div>
            <div className="stack-item">
              <strong>Development:</strong> Hot Module Replacement, Proxy Configuration
            </div>
            <div className="stack-item">
              <strong>Build:</strong> Optimized bundles, Code splitting
            </div>
          </div>
        </section>

        <ApiStatus />
      </main>

      <footer className="App-footer">
        <p>
          Built with ❤️ using Vite + React + ASP.NET Core
        </p>
        <div className="footer-links">
          <a href="/swagger" target="_blank" rel="noopener noreferrer">
            📚 API Documentation
          </a>
          <a href="https://vitejs.dev" target="_blank" rel="noopener noreferrer">
            ⚡ Vite Documentation
          </a>
          <a href="https://docs.microsoft.com/aspnet/core" target="_blank" rel="noopener noreferrer">
            🏗️ ASP.NET Core Docs
          </a>
        </div>
      </footer>
    </div>
  );
};

// Global declarations for build-time constants
declare const __APP_VERSION__: string;

export default App;
