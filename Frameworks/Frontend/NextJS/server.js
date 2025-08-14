import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import compression from 'compression';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { createServer } from 'http';

// Import API routes
import apiRoutes from './lib/api/index.js';
import { errorHandler, notFoundHandler } from './lib/middleware/errorHandler.js';
import { rateLimiter } from './lib/middleware/rateLimiter.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const port = process.env.PORT || 3000;
const isDevelopment = process.env.NODE_ENV === 'development';

// Security middleware
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
      fontSrc: ["'self'", "https://fonts.gstatic.com"],
      imgSrc: ["'self'", "data:", "https:"],
      scriptSrc: ["'self'"],
    },
  },
}));

// CORS configuration
const corsOptions = {
  origin: isDevelopment 
    ? ['http://localhost:3001', 'http://localhost:3000']
    : process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
  credentials: true,
  optionsSuccessStatus: 200
};

app.use(cors(corsOptions));

// Compression middleware
app.use(compression());

// Logging middleware
app.use(morgan(isDevelopment ? 'dev' : 'combined'));

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Rate limiting
if (!isDevelopment) {
  app.use('/api/', rateLimiter);
}

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    environment: process.env.NODE_ENV,
    version: process.env.npm_package_version || '1.0.0'
  });
});

// API routes
app.use('/api', apiRoutes);

// Serve Next.js in production
if (!isDevelopment) {
  const nextBuild = join(__dirname, '.next');
  app.use(express.static(join(__dirname, 'public')));
  app.use(express.static(nextBuild));
  
  // Handle Next.js pages
  app.get('*', (req, res) => {
    res.sendFile(join(nextBuild, 'server/pages', req.path.endsWith('/') ? req.path + 'index.html' : req.path + '.html'));
  });
}

// Error handling
app.use(notFoundHandler);
app.use(errorHandler);

// Graceful shutdown
const server = createServer(app);

process.on('SIGTERM', () => {
  console.log('🔄 SIGTERM received, shutting down gracefully');
  server.close(() => {
    console.log('✅ Process terminated');
  });
});

process.on('SIGINT', () => {
  console.log('🔄 SIGINT received, shutting down gracefully');
  server.close(() => {
    console.log('✅ Process terminated');
  });
});

server.listen(port, () => {
  console.log(`🚀 Express server running on port ${port}`);
  console.log(`📊 Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`🔗 API Base URL: http://localhost:${port}/api`);
  
  if (isDevelopment) {
    console.log(`🎨 Next.js dev server should be running on http://localhost:3001`);
  }
});

export default app;
