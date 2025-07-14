import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { AuthService } from '../services/AuthService';
import { logger } from '../utils/logger';

declare global {
  namespace Express {
    interface Request {
      user?: {
        id: string;
        username: string;
        role: string;
      };
      requestId?: string;
    }
  }
}

const authService = new AuthService();

export const authenticateToken = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const authHeader = req.headers.authorization;
    const apiKey = req.headers['x-api-key'] as string;

    let token: string | null = null;

    // Check for Bearer token
    if (authHeader && authHeader.startsWith('Bearer ')) {
      token = authHeader.substring(7);
    }
    // Check for API key
    else if (apiKey) {
      const user = await authService.validateApiKey(apiKey);
      if (user) {
        req.user = {
          id: user.id,
          username: user.username,
          role: user.role,
        };
        return next();
      }
    }

    if (!token) {
      return res.status(401).json({
        error: {
          message: 'Access token is required',
          type: 'authentication_error',
        }
      });
    }

    // Validate JWT token
    const user = await authService.validateToken(token);
    
    if (!user) {
      return res.status(401).json({
        error: {
          message: 'Invalid or expired token',
          type: 'authentication_error',
        }
      });
    }

    // Add user info to request
    req.user = {
      id: user.id,
      username: user.username,
      role: user.role,
    };

    next();
  } catch (error) {
    logger.error('Authentication error:', error);
    res.status(401).json({
      error: {
        message: 'Authentication failed',
        type: 'authentication_error',
      }
    });
  }
};

export const requireRole = (roles: string[]) => {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({
        error: {
          message: 'Authentication required',
          type: 'authentication_error',
        }
      });
    }

    if (!roles.includes(req.user.role)) {
      return res.status(403).json({
        error: {
          message: 'Insufficient permissions',
          type: 'authorization_error',
        }
      });
    }

    next();
  };
};
