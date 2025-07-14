const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Security middleware
app.use(helmet());
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 1000 // limit each IP to 1000 requests per windowMs
});
app.use(limiter);

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));

// Service URLs
const AUTH_SERVICE_URL = process.env.AUTH_SERVICE_URL || 'http://localhost:3001';
const USER_SERVICE_URL = process.env.USER_SERVICE_URL || 'http://localhost:3002';

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ 
    status: 'healthy', 
    service: 'api-gateway',
    timestamp: new Date().toISOString()
  });
});

// Proxy configuration
const createProxy = (target, pathPrefix = '') => {
  return createProxyMiddleware({
    target,
    changeOrigin: true,
    pathRewrite: pathPrefix ? { [`^${pathPrefix}`]: '' } : undefined,
    onError: (err, req, res) => {
      console.error(`Proxy error for ${target}:`, err.message);
      res.status(502).json({ 
        error: 'Service unavailable', 
        message: 'The requested service is currently unavailable'
      });
    },
    onProxyReq: (proxyReq, req, res) => {
      console.log(`Proxying ${req.method} ${req.url} to ${target}`);
      // Forward original IP
      proxyReq.setHeader('X-Forwarded-For', req.ip);
    }
  });
};

// Route proxying
app.use('/api/auth', createProxy(AUTH_SERVICE_URL, '/api/auth'));
app.use('/api/users', createProxy(USER_SERVICE_URL, '/api/users'));

// API documentation endpoint
app.get('/api', (req, res) => {
  res.json({
    name: 'Microservices API Gateway',
    version: '1.0.0',
    endpoints: {
      auth: {
        baseUrl: '/api/auth',
        endpoints: [
          'POST /api/auth/signup',
          'POST /api/auth/signin',
          'POST /api/auth/verify'
        ]
      },
      users: {
        baseUrl: '/api/users',
        endpoints: [
          'GET /api/users/profile',
          'PUT /api/users/profile',
          'GET /api/users'
        ]
      }
    }
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({ 
    error: 'Route not found',
    path: req.originalUrl,
    method: req.method
  });
});

// Global error handler
app.use((err, req, res, next) => {
  console.error('API Gateway error:', err);
  res.status(500).json({ 
    error: 'Internal server error',
    message: process.env.NODE_ENV === 'production' ? 'Something went wrong' : err.message
  });
});

app.listen(PORT, () => {
  console.log(`API Gateway running on port ${PORT}`);
  console.log(`Auth Service: ${AUTH_SERVICE_URL}`);
  console.log(`User Service: ${USER_SERVICE_URL}`);
});

module.exports = app;
