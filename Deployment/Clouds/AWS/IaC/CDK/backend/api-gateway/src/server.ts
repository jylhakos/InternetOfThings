import dotenv from 'dotenv';
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import { createProxyMiddleware } from 'http-proxy-middleware';
import { logger } from '@microservices/shared';

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Security middleware
app.use(helmet());
app.use(cors({
  origin: process.env.CORS_ORIGIN || '*',
  credentials: true
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later.'
});
app.use(limiter);

// Body parsing middleware for direct routes
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Service URLs
const AUTH_SERVICE_URL = process.env.AUTH_SERVICE_URL || 'http://localhost:3001';
const USER_SERVICE_URL = process.env.USER_SERVICE_URL || 'http://localhost:3002';

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    service: 'api-gateway',
    timestamp: new Date().toISOString(),
    services: {
      auth: AUTH_SERVICE_URL,
      user: USER_SERVICE_URL
    }
  });
});

// Service discovery endpoint
app.get('/services', (req, res) => {
  res.json({
    success: true,
    data: {
      auth: {
        url: AUTH_SERVICE_URL,
        paths: ['/auth/signup', '/auth/signin', '/auth/verify']
      },
      user: {
        url: USER_SERVICE_URL,
        paths: ['/users/profile', '/users/:id', '/users']
      }
    }
  });
});

// Proxy middleware for Auth Service
app.use('/auth', createProxyMiddleware({
  target: AUTH_SERVICE_URL,
  changeOrigin: true,
  pathRewrite: {
    '^/auth': '/auth'
  },
  onError: (err, req, res) => {
    logger.error('Auth service proxy error:', err);
    if (res instanceof express.Response) {
      res.status(503).json({
        success: false,
        error: 'Auth service unavailable'
      });
    }
  },
  onProxyReq: (proxyReq, req, res) => {
    logger.info(`Proxying ${req.method} ${req.url} to auth service`);
  }
}));

// Proxy middleware for User Service
app.use('/users', createProxyMiddleware({
  target: USER_SERVICE_URL,
  changeOrigin: true,
  pathRewrite: {
    '^/users': '/users'
  },
  onError: (err, req, res) => {
    logger.error('User service proxy error:', err);
    if (res instanceof express.Response) {
      res.status(503).json({
        success: false,
        error: 'User service unavailable'
      });
    }
  },
  onProxyReq: (proxyReq, req, res) => {
    logger.info(`Proxying ${req.method} ${req.url} to user service`);
  }
}));

// Global error handling middleware
app.use((error: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  logger.error('API Gateway error:', error);
  
  const statusCode = error.statusCode || 500;
  const message = error.isOperational ? error.message : 'Internal server error';
  
  res.status(statusCode).json({
    success: false,
    error: message,
    ...(process.env.NODE_ENV === 'development' && { stack: error.stack })
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    success: false,
    error: 'Route not found',
    availableRoutes: [
      'GET /health',
      'GET /services',
      'POST /auth/signup',
      'POST /auth/signin',
      'GET /auth/verify',
      'GET /users/profile',
      'PUT /users/profile',
      'GET /users/:id',
      'GET /users'
    ]
  });
});

// Start server
app.listen(PORT, () => {
  logger.info(`API Gateway running on port ${PORT}`);
  logger.info(`Environment: ${process.env.NODE_ENV || 'development'}`);
  logger.info(`Auth Service: ${AUTH_SERVICE_URL}`);
  logger.info(`User Service: ${USER_SERVICE_URL}`);
});

export default app;
