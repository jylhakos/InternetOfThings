// Node.js Express Server for Vite + React App
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import dotenv from 'dotenv';
import { v4 as uuidv4 } from 'uuid';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(helmet());
app.use(cors({
  origin: process.env.CLIENT_URL || 'http://localhost:5173',
  credentials: true
}));
app.use(morgan('combined'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Mock IoT Device Data
let devices = [
  {
    id: '1',
    name: 'Temperature Sensor 1',
    type: 'temperature',
    status: 'online',
    value: 23.5,
    unit: '°C',
    location: 'Living Room',
    lastUpdate: new Date().toISOString(),
    battery: 85
  },
  {
    id: '2',
    name: 'Humidity Sensor',
    type: 'humidity',
    status: 'online',
    value: 65.2,
    unit: '%',
    location: 'Kitchen',
    lastUpdate: new Date().toISOString(),
    battery: 92
  },
  {
    id: '3',
    name: 'Motion Detector',
    type: 'motion',
    status: 'offline',
    value: 0,
    unit: 'detected',
    location: 'Entrance',
    lastUpdate: new Date(Date.now() - 300000).toISOString(), // 5 minutes ago
    battery: 15
  }
];

// API Routes
app.get('/api/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    version: '1.0.0'
  });
});

// Get all devices
app.get('/api/devices', (req, res) => {
  try {
    // Simulate some device updates
    devices = devices.map(device => ({
      ...device,
      value: device.type === 'temperature' 
        ? parseFloat((Math.random() * 30 + 15).toFixed(1))
        : device.type === 'humidity'
        ? parseFloat((Math.random() * 40 + 40).toFixed(1))
        : Math.floor(Math.random() * 2),
      lastUpdate: device.status === 'online' ? new Date().toISOString() : device.lastUpdate
    }));

    const stats = {
      total: devices.length,
      online: devices.filter(d => d.status === 'online').length,
      offline: devices.filter(d => d.status === 'offline').length,
      lowBattery: devices.filter(d => d.battery < 20).length
    };

    res.json({
      devices,
      stats,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Error fetching devices:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get single device
app.get('/api/devices/:id', (req, res) => {
  try {
    const device = devices.find(d => d.id === req.params.id);
    
    if (!device) {
      return res.status(404).json({ error: 'Device not found' });
    }

    res.json(device);
  } catch (error) {
    console.error('Error fetching device:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Update device
app.put('/api/devices/:id', (req, res) => {
  try {
    const deviceIndex = devices.findIndex(d => d.id === req.params.id);
    
    if (deviceIndex === -1) {
      return res.status(404).json({ error: 'Device not found' });
    }

    devices[deviceIndex] = {
      ...devices[deviceIndex],
      ...req.body,
      lastUpdate: new Date().toISOString()
    };

    res.json(devices[deviceIndex]);
  } catch (error) {
    console.error('Error updating device:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create new device
app.post('/api/devices', (req, res) => {
  try {
    const newDevice = {
      id: uuidv4(),
      ...req.body,
      lastUpdate: new Date().toISOString()
    };

    devices.push(newDevice);
    res.status(201).json(newDevice);
  } catch (error) {
    console.error('Error creating device:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Delete device
app.delete('/api/devices/:id', (req, res) => {
  try {
    const deviceIndex = devices.findIndex(d => d.id === req.params.id);
    
    if (deviceIndex === -1) {
      return res.status(404).json({ error: 'Device not found' });
    }

    const deletedDevice = devices.splice(deviceIndex, 1)[0];
    res.json(deletedDevice);
  } catch (error) {
    console.error('Error deleting device:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Vite + React API Server running on http://localhost:${PORT}`);
  console.log(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`📡 CORS enabled for: ${process.env.CLIENT_URL || 'http://localhost:5173'}`);
});
