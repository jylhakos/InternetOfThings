import { Request, Response, NextFunction } from 'express';
import axios from 'axios';
import { createErrorResponse, logger } from '@microservices/shared';

export interface AuthenticatedRequest extends Request {
  user?: {
    id: number;
    email: string;
  };
}

export const authenticateToken = async (
  req: AuthenticatedRequest,
  res: Response,
  next: NextFunction
) => {
  try {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json(
        createErrorResponse('Authentication failed', 'No token provided')
      );
    }

    // Verify token with auth service
    const authServiceUrl = process.env.AUTH_SERVICE_URL || 'http://localhost:3001';
    const response = await axios.get(`${authServiceUrl}/auth/verify`, {
      headers: {
        Authorization: authHeader
      }
    });

    if (response.data.success && response.data.data.isValid) {
      req.user = response.data.data.user;
      next();
    } else {
      return res.status(401).json(
        createErrorResponse('Authentication failed', 'Invalid token')
      );
    }
  } catch (error) {
    logger.error('Authentication middleware error:', error);
    return res.status(401).json(
      createErrorResponse('Authentication failed', 'Token verification failed')
    );
  }
};
