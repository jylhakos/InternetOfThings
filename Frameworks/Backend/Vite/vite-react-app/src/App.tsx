import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { DeviceCard } from './components/DeviceCard';
import { deviceService } from './services/api';
import { Device, DeviceStats } from './types';
import './App.css';

function App() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [stats, setStats] = useState<DeviceStats>({ total: 0, online: 0, offline: 0, lowBattery: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDevices = async () => {
    try {
      setLoading(true);
      const response = await deviceService.getAllDevices();
      setDevices(response.devices);
      setStats(response.stats);
      setError(null);
    } catch (err) {
      setError('Failed to fetch devices. Make sure the server is running on port 3001.');
      console.error('Error fetching devices:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDevices();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchDevices, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleUpdateDevice = async (updatedDevice: Device) => {
    try {
      const result = await deviceService.updateDevice(updatedDevice.id, {
        status: updatedDevice.status
      });
      
      setDevices(prev => prev.map(device => 
        device.id === result.id ? result : device
      ));
      
      // Update stats
      await fetchDevices();
    } catch (err) {
      console.error('Error updating device:', err);
    }
  };

  const handleDeleteDevice = async (id: string) => {
    try {
      await deviceService.deleteDevice(id);
      setDevices(prev => prev.filter(device => device.id !== id));
      await fetchDevices(); // Refresh stats
    } catch (err) {
      console.error('Error deleting device:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading devices...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center bg-white p-8 rounded-lg shadow-md">
          <div className="text-red-600 text-6xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Connection Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button 
            onClick={fetchDevices}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        {/* Header */}
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <h1 className="text-2xl font-bold text-gray-900">
                  🏠 IoT Dashboard
                </h1>
                <span className="ml-3 px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                  Vite + React
                </span>
              </div>
              
              <nav className="flex space-x-4">
                <Link 
                  to="/" 
                  className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Dashboard
                </Link>
                <Link 
                  to="/about" 
                  className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
                >
                  About
                </Link>
              </nav>
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={
              <div>
                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                          <span className="text-white font-bold text-sm">📱</span>
                        </div>
                      </div>
                      <div className="ml-4">
                        <p className="text-sm font-medium text-gray-600">Total Devices</p>
                        <p className="text-2xl font-semibold text-gray-900">{stats.total}</p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                          <span className="text-white font-bold text-sm">✓</span>
                        </div>
                      </div>
                      <div className="ml-4">
                        <p className="text-sm font-medium text-gray-600">Online</p>
                        <p className="text-2xl font-semibold text-gray-900">{stats.online}</p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-red-500 rounded-md flex items-center justify-center">
                          <span className="text-white font-bold text-sm">✗</span>
                        </div>
                      </div>
                      <div className="ml-4">
                        <p className="text-sm font-medium text-gray-600">Offline</p>
                        <p className="text-2xl font-semibold text-gray-900">{stats.offline}</p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
                          <span className="text-white font-bold text-sm">🔋</span>
                        </div>
                      </div>
                      <div className="ml-4">
                        <p className="text-sm font-medium text-gray-600">Low Battery</p>
                        <p className="text-2xl font-semibold text-gray-900">{stats.lowBattery}</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Devices Grid */}
                <div className="mb-6">
                  <div className="flex justify-between items-center">
                    <h2 className="text-lg font-medium text-gray-900">Connected Devices</h2>
                    <button 
                      onClick={fetchDevices}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                    >
                      🔄 Refresh
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {devices.map(device => (
                    <DeviceCard 
                      key={device.id} 
                      device={device} 
                      onUpdate={handleUpdateDevice}
                      onDelete={handleDeleteDevice}
                    />
                  ))}
                </div>

                {devices.length === 0 && (
                  <div className="text-center py-12">
                    <div className="text-gray-400 text-6xl mb-4">📱</div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No devices found</h3>
                    <p className="text-gray-600">Check your server connection and try again.</p>
                  </div>
                )}
              </div>
            } />
            
            <Route path="/about" element={
              <div className="bg-white rounded-lg shadow-md p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">About This Application</h2>
                <div className="space-y-4 text-gray-600">
                  <p>
                    This is a demonstration IoT Device Management Dashboard built with:
                  </p>
                  <ul className="list-disc list-inside space-y-2 ml-4">
                    <li><strong>Frontend:</strong> Vite + React + TypeScript</li>
                    <li><strong>Backend:</strong> Node.js + Express</li>
                    <li><strong>Styling:</strong> Tailwind CSS</li>
                    <li><strong>Debugging:</strong> VS Code with Vite debugging</li>
                  </ul>
                  <p>
                    The application demonstrates client-side rendering with separate API server,
                    perfect for SPA applications that need fast development and flexible deployment.
                  </p>
                </div>
              </div>
            } />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
