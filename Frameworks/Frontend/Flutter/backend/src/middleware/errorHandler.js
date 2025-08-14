/**
 * Global error handling middleware
 * This should be the last middleware in the stack
 */
const errorHandler = (err, req, res, next) => {
  console.error('Error occurred:', {
    error: err.message,
    stack: err.stack,
    url: req.url,
    method: req.method,
    ip: req.ip,
    userAgent: req.get('User-Agent'),
    timestamp: new Date().toISOString()
  });

  // Default error
  let error = { ...err };
  error.message = err.message;

  // Mongoose bad ObjectId
  if (err.name === 'CastError') {
    const message = 'Resource not found';
    error = {
      message,
      statusCode: 404
    };
  }

  // Mongoose duplicate key error
  if (err.code === 11000) {
    const field = Object.keys(err.keyValue)[0];
    const value = err.keyValue[field];
    const message = `${field.charAt(0).toUpperCase() + field.slice(1)} '${value}' already exists`;
    error = {
      message,
      statusCode: 400
    };
  }

  // Mongoose validation error
  if (err.name === 'ValidationError') {
    const message = Object.values(err.errors).map(val => val.message).join(', ');
    error = {
      message,
      statusCode: 400
    };
  }

  // JWT errors
  if (err.name === 'JsonWebTokenError') {
    const message = 'Invalid token';
    error = {
      message,
      statusCode: 401
    };
  }

  if (err.name === 'TokenExpiredError') {
    const message = 'Token expired';
    error = {
      message,
      statusCode: 401
    };
  }

  // Rate limiting errors
  if (err.message && err.message.includes('Too many requests')) {
    error = {
      message: 'Too many requests, please try again later',
      statusCode: 429
    };
  }

  // File upload errors
  if (err.code === 'LIMIT_FILE_SIZE') {
    error = {
      message: 'File too large',
      statusCode: 413
    };
  }

  if (err.code === 'LIMIT_FILE_COUNT') {
    error = {
      message: 'Too many files',
      statusCode: 413
    };
  }

  if (err.code === 'LIMIT_UNEXPECTED_FILE') {
    error = {
      message: 'Unexpected file field',
      statusCode: 400
    };
  }

  // AWS SDK errors
  if (err.code && err.code.startsWith('AWS')) {
    error = {
      message: 'Cloud service error',
      statusCode: 502
    };
  }

  // Database connection errors
  if (err.name === 'MongoNetworkError' || err.name === 'MongoTimeoutError') {
    error = {
      message: 'Database connection error',
      statusCode: 503
    };
  }

  // Set default status code
  const statusCode = error.statusCode || 500;
  const message = error.message || 'Internal server error';

  // Prepare error response
  const errorResponse = {
    success: false,
    message,
    error: message
  };

  // Add additional error details in development
  if (process.env.NODE_ENV === 'development') {
    errorResponse.stack = err.stack;
    errorResponse.details = {
      name: err.name,
      code: err.code,
      statusCode: err.statusCode
    };
  }

  // Add error ID for tracking
  const errorId = generateErrorId();
  errorResponse.errorId = errorId;

  // Log error with ID for debugging
  console.error(`Error ID: ${errorId}`, {
    message: error.message,
    statusCode,
    originalError: err.name,
    url: req.url,
    method: req.method
  });

  // Send error response
  res.status(statusCode).json(errorResponse);
};

/**
 * Generate unique error ID for tracking
 */
function generateErrorId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

/**
 * Async error wrapper
 * Use this to wrap async route handlers to automatically catch errors
 */
const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

/**
 * 404 handler
 * Use this for routes that don't exist
 */
const notFound = (req, res, next) => {
  const error = new Error(`Not found - ${req.originalUrl}`);
  error.statusCode = 404;
  next(error);
};

/**
 * Custom error class for application-specific errors
 */
class AppError extends Error {
  constructor(message, statusCode) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = true;

    Error.captureStackTrace(this, this.constructor);
  }
}

/**
 * Validation error handler
 * Use this to handle express-validator errors
 */
const handleValidationErrors = (req, res, next) => {
  const { validationResult } = require('express-validator');
  const errors = validationResult(req);

  if (!errors.isEmpty()) {
    const errorMessages = errors.array().map(error => ({
      field: error.param,
      message: error.msg,
      value: error.value
    }));

    return res.status(400).json({
      success: false,
      message: 'Validation failed',
      error: 'Please check your input data',
      details: errorMessages
    });
  }

  next();
};

module.exports = {
  errorHandler,
  asyncHandler,
  notFound,
  AppError,
  handleValidationErrors
};
