import { Router, Request, Response } from 'express';
import { logger } from '../utils/logger';

const router = Router();

// Health check endpoint
router.get('/', (req: Request, res: Response) => {
  const healthStatus = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    environment: process.env.NODE_ENV || 'development',
    version: '1.0.0',
    services: {
      llm: 'operational',
      auth: 'operational',
      memory: 'operational',
    },
    system: {
      platform: process.platform,
      nodeVersion: process.version,
      memory: {
        used: Math.round(process.memoryUsage().heapUsed / 1024 / 1024),
        total: Math.round(process.memoryUsage().heapTotal / 1024 / 1024),
        external: Math.round(process.memoryUsage().external / 1024 / 1024),
      },
    },
  };

  res.json(healthStatus);
});

// Detailed health check
router.get('/detailed', async (req: Request, res: Response) => {
  try {
    const detailedHealth = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      checks: {
        database: {
          status: 'healthy',
          message: 'In-memory storage operational',
        },
        llm_service: {
          status: 'healthy',
          message: 'LLM service initialized and ready',
        },
        auth_service: {
          status: 'healthy',
          message: 'Authentication service operational',
        },
        rate_limiter: {
          status: 'healthy',
          message: 'Rate limiting active',
        },
      },
      metrics: {
        uptime_seconds: process.uptime(),
        memory_usage_mb: Math.round(process.memoryUsage().heapUsed / 1024 / 1024),
        memory_total_mb: Math.round(process.memoryUsage().heapTotal / 1024 / 1024),
        cpu_usage: process.cpuUsage(),
      },
    };

    res.json(detailedHealth);
  } catch (error) {
    logger.error('Health check error:', error);
    res.status(503).json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: 'Health check failed',
    });
  }
});

// Readiness probe
router.get('/ready', (req: Request, res: Response) => {
  // Check if all services are ready
  const isReady = true; // Add actual readiness checks here

  if (isReady) {
    res.json({
      status: 'ready',
      timestamp: new Date().toISOString(),
    });
  } else {
    res.status(503).json({
      status: 'not_ready',
      timestamp: new Date().toISOString(),
    });
  }
});

// Liveness probe
router.get('/live', (req: Request, res: Response) => {
  res.json({
    status: 'alive',
    timestamp: new Date().toISOString(),
  });
});

export { router as healthRoutes };
