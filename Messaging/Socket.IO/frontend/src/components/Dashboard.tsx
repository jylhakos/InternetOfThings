import React, { useState, useEffect } from 'react';
import type { WeatherData } from '../types';
import { useAuth } from '../AuthContext';
import { socketService } from '../services/socket';
import { weatherAPI } from '../services/api';
import './Dashboard.css';

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  useEffect(() => {
    // Connect to Socket.IO
    socketService.connect();

    // Listen for weather updates
    socketService.onWeatherUpdate((data: WeatherData) => {
      setWeatherData(data);
      setLastUpdated(new Date());
      setLoading(false);
      setError('');
    });

    // Listen for weather errors
    socketService.onWeatherError((errorData) => {
      setError(errorData.error);
      setLoading(false);
    });

    // Load initial weather data
    loadWeatherData();

    return () => {
      socketService.disconnect();
    };
  }, []);

  const loadWeatherData = async () => {
    try {
      setLoading(true);
      const data = await weatherAPI.getCurrentWeather();
      setWeatherData(data);
      setLastUpdated(new Date());
      setError('');
    } catch {
      setError('Failed to load weather data');
    } finally {
      setLoading(false);
    }
  };

  const refreshWeather = () => {
    socketService.requestWeather();
    setLoading(true);
  };

  const getWeatherIcon = (condition: string) => {
    switch (condition.toLowerCase()) {
      case 'clear':
        return '☀️';
      case 'clouds':
        return '☁️';
      case 'rain':
        return '🌧️';
      case 'snow':
        return '❄️';
      case 'mist':
      case 'fog':
        return '🌫️';
      case 'thunderstorm':
        return '⛈️';
      default:
        return '🌤️';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>Weather Dashboard</h1>
          <div className="user-info">
            <span>Welcome, {user?.first_name}!</span>
            <button onClick={logout} className="logout-btn">
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="dashboard-main">
        <div className="user-card">
          <h2>User Information</h2>
          <div className="user-details">
            <p><strong>Name:</strong> {user?.first_name} {user?.last_name}</p>
            <p><strong>Email:</strong> {user?.email}</p>
            <p><strong>Phone:</strong> {user?.phone}</p>
          </div>
        </div>

        <div className="weather-section">
          <div className="weather-header">
            <h2>
              <span className="weather-icon">🌤️</span>
              Schiphol Airport Weather
            </h2>
            <button 
              onClick={refreshWeather} 
              className="refresh-btn"
              disabled={loading}
            >
              {loading ? '🔄' : '🔄'} Refresh
            </button>
          </div>

          {error && (
            <div className="error-card">
              <p>⚠️ {error}</p>
              <button onClick={loadWeatherData}>Try Again</button>
            </div>
          )}

          {weatherData && (
            <div className="weather-grid">
              <div className="weather-card main-weather">
                <div className="weather-main">
                  <div className="weather-icon-large">
                    {getWeatherIcon(weatherData.condition)}
                  </div>
                  <div className="weather-temp">
                    <span className="temp-value">{weatherData.temperature}°C</span>
                    <span className="weather-desc">{weatherData.description}</span>
                  </div>
                </div>
                <div className="weather-location">📍 {weatherData.location}</div>
              </div>

              <div className="weather-card">
                <h3>💨 Wind</h3>
                <p className="metric-value">{weatherData.wind_speed} m/s</p>
                <p className="metric-label">Direction: {weatherData.wind_direction}°</p>
              </div>

              <div className="weather-card">
                <h3>💧 Humidity</h3>
                <p className="metric-value">{weatherData.humidity}%</p>
              </div>

              <div className="weather-card">
                <h3>🔗 Pressure</h3>
                <p className="metric-value">{weatherData.pressure} hPa</p>
              </div>

              <div className="weather-card">
                <h3>👁️ Visibility</h3>
                <p className="metric-value">{weatherData.visibility} km</p>
              </div>

              <div className="weather-card timestamp-card">
                <h3>🕒 Last Updated</h3>
                <p className="timestamp">
                  {lastUpdated ? lastUpdated.toLocaleString() : formatTimestamp(weatherData.timestamp)}
                </p>
                <p className="live-indicator">
                  {socketService.isConnected() ? '🟢 Live' : '🔴 Offline'}
                </p>
              </div>
            </div>
          )}

          {loading && !weatherData && (
            <div className="loading-card">
              <div className="loading-spinner"></div>
              <p>Loading weather data...</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default Dashboard;