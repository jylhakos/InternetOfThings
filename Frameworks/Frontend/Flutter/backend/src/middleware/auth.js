const jwt = require('jsonwebtoken');
const { promisify } = require('util');

// JWT Secret - In production, this should be a strong secret key
const JWT_SECRET = process.env.JWT_SECRET || 'your-super-secret-jwt-key-change-this-in-production';
const JWT_EXPIRE = process.env.JWT_EXPIRE || '24h';
const JWT_REFRESH_SECRET = process.env.JWT_REFRESH_SECRET || 'your-super-secret-refresh-key';
const JWT_REFRESH_EXPIRE = process.env.JWT_REFRESH_EXPIRE || '7d';

/**
 * Middleware to authenticate JWT tokens
 */
const authenticateToken = async (req, res, next) => {
  try {
    const authHeader = req.headers.authorization;
    const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

    if (!token) {
      return res.status(401).json({
        success: false,
        message: 'Access token required',
        error: 'No token provided'
      });
    }

    // Verify token
    const decoded = await promisify(jwt.verify)(token, JWT_SECRET);
    
    // Add user info to request
    req.user = {
      id: decoded.id,
      email: decoded.email,
      role: decoded.role,
      cognitoId: decoded.cognitoId
    };

    next();
  } catch (error) {
    if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({
        success: false,
        message: 'Invalid token',
        error: 'Token verification failed'
      });
    }
    
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({
        success: false,
        message: 'Token expired',
        error: 'Please refresh your token'
      });
    }

    return res.status(500).json({
      success: false,
      message: 'Token verification error',
      error: error.message
    });
  }
};

/**
 * Middleware to authenticate admin role
 */
const requireAdmin = (req, res, next) => {
  if (req.user && req.user.role === 'admin') {
    next();
  } else {
    return res.status(403).json({
      success: false,
      message: 'Admin access required',
      error: 'Insufficient permissions'
    });
  }
};

/**
 * Middleware to check if user owns the resource or is admin
 */
const requireOwnershipOrAdmin = (resourceIdField = 'id') => {
  return (req, res, next) => {
    const resourceId = req.params[resourceIdField];
    const userId = req.user.id;
    const isAdmin = req.user.role === 'admin';

    if (isAdmin || resourceId === userId) {
      next();
    } else {
      return res.status(403).json({
        success: false,
        message: 'Access denied',
        error: 'You can only access your own resources'
      });
    }
  };
};

/**
 * Generate access token
 */
const generateAccessToken = (user) => {
  const payload = {
    id: user._id || user.id,
    email: user.email,
    role: user.role || 'user',
    cognitoId: user.cognitoId
  };

  return jwt.sign(payload, JWT_SECRET, { 
    expiresIn: JWT_EXPIRE,
    issuer: 'flutter-spa-api',
    audience: 'flutter-spa-client'
  });
};

/**
 * Generate refresh token
 */
const generateRefreshToken = (user) => {
  const payload = {
    id: user._id || user.id,
    email: user.email,
    tokenType: 'refresh'
  };

  return jwt.sign(payload, JWT_REFRESH_SECRET, { 
    expiresIn: JWT_REFRESH_EXPIRE,
    issuer: 'flutter-spa-api',
    audience: 'flutter-spa-client'
  });
};

/**
 * Verify refresh token
 */
const verifyRefreshToken = async (token) => {
  try {
    const decoded = await promisify(jwt.verify)(token, JWT_REFRESH_SECRET);
    return decoded;
  } catch (error) {
    throw new Error('Invalid refresh token');
  }
};

/**
 * Generate both access and refresh tokens
 */
const generateTokens = (user) => {
  return {
    accessToken: generateAccessToken(user),
    refreshToken: generateRefreshToken(user),
    expiresIn: JWT_EXPIRE,
    tokenType: 'Bearer'
  };
};

/**
 * Optional authentication middleware
 * Adds user info if token is present and valid, but doesn't reject requests without tokens
 */
const optionalAuth = async (req, res, next) => {
  try {
    const authHeader = req.headers.authorization;
    const token = authHeader && authHeader.split(' ')[1];

    if (token) {
      const decoded = await promisify(jwt.verify)(token, JWT_SECRET);
      req.user = {
        id: decoded.id,
        email: decoded.email,
        role: decoded.role,
        cognitoId: decoded.cognitoId
      };
    }

    next();
  } catch (error) {
    // If token is invalid, continue without user info
    next();
  }
};

/**
 * Rate limiting middleware for sensitive operations
 */
const sensitiveOperationLimit = (maxAttempts = 5, windowMs = 15 * 60 * 1000) => {
  const attempts = new Map();

  return (req, res, next) => {
    const key = req.ip + ':' + (req.user ? req.user.id : 'anonymous');
    const now = Date.now();
    
    // Clean up old entries
    if (attempts.has(key)) {
      const userAttempts = attempts.get(key);
      userAttempts.times = userAttempts.times.filter(time => now - time < windowMs);
      
      if (userAttempts.times.length === 0) {
        attempts.delete(key);
      }
    }

    // Check current attempts
    const userAttempts = attempts.get(key) || { times: [] };
    
    if (userAttempts.times.length >= maxAttempts) {
      return res.status(429).json({
        success: false,
        message: 'Too many attempts',
        error: 'Please try again later',
        retryAfter: Math.ceil((userAttempts.times[0] + windowMs - now) / 1000)
      });
    }

    // Record this attempt
    userAttempts.times.push(now);
    attempts.set(key, userAttempts);

    next();
  };
};

module.exports = {
  authenticateToken,
  requireAdmin,
  requireOwnershipOrAdmin,
  optionalAuth,
  generateAccessToken,
  generateRefreshToken,
  generateTokens,
  verifyRefreshToken,
  sensitiveOperationLimit
};
