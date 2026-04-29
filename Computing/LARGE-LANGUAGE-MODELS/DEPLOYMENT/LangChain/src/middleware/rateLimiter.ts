import { Request, Response, NextFunction } from 'express';
import { RateLimiterMemory } from 'rate-limiter-flexible';
import { logger } from '../utils/logger';

// Create rate limiter instances
const authLimiter = new RateLimiterMemory({
  keyGeneration: (req: Request) => req.ip,
  points: 5, // Number of requests
  duration: 900, // Per 15 minutes
});

const apiLimiter = new RateLimiterMemory({
  keyGeneration: (req: Request) => req.ip,
  points: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS || '100'),
  duration: parseInt(process.env.RATE_LIMIT_WINDOW_MS || '900000') / 1000, // Convert to seconds
});

const chatLimiter = new RateLimiterMemory({
  keyGeneration: (req: Request) => {
    // Use user ID if authenticated, otherwise use IP
    return (req as any).user?.id || req.ip;
  },
  points: 50, // Number of chat requests
  duration: 3600, // Per hour
});

export const rateLimiter = async (req: Request, res: Response, next: NextFunction) => {
  try {
    // Choose limiter based on endpoint
    let limiter: RateLimiterMemory;
    
    if (req.path.startsWith('/api/auth')) {
      limiter = authLimiter;
    } else if (req.path.startsWith('/api/chat') || req.path.startsWith('/v1/chat')) {
      limiter = chatLimiter;
    } else {
      limiter = apiLimiter;
    }

    await limiter.consume(req.ip);
    next();
  } catch (rateLimiterRes) {
    const secs = Math.round(rateLimiterRes.msBeforeNext / 1000) || 1;
    
    logger.warn('Rate limit exceeded', {
      ip: req.ip,
      path: req.path,
      resetTime: secs,
    });

    res.set('Retry-After', String(secs));
    res.status(429).json({
      error: {
        message: 'Too many requests',
        type: 'rate_limit_exceeded',
        retry_after: secs,
      }
    });
  }
};
