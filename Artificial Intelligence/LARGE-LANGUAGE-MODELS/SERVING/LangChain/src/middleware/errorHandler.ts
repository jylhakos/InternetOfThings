import { Request, Response, NextFunction } from 'express';
import { logger } from '../utils/logger';

export const errorHandler = (
  error: any,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  logger.error('Unhandled error:', {
    error: error.message,
    stack: error.stack,
    path: req.path,
    method: req.method,
    requestId: req.requestId,
  });

  // Default error
  let status = 500;
  let message = 'Internal server error';
  let type = 'internal_error';

  // Handle specific error types
  if (error.name === 'ValidationError') {
    status = 400;
    message = 'Validation error';
    type = 'validation_error';
  } else if (error.name === 'UnauthorizedError') {
    status = 401;
    message = 'Unauthorized';
    type = 'authentication_error';
  } else if (error.name === 'ForbiddenError') {
    status = 403;
    message = 'Forbidden';
    type = 'authorization_error';
  } else if (error.name === 'NotFoundError') {
    status = 404;
    message = 'Not found';
    type = 'not_found_error';
  } else if (error.message) {
    message = error.message;
  }

  res.status(status).json({
    error: {
      message,
      type,
      ...(process.env.NODE_ENV === 'development' && { stack: error.stack }),
    }
  });
};
