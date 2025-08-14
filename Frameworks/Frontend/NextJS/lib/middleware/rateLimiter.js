// Simple rate limiter implementation
const rateLimiterMap = new Map();

export const rateLimiter = (req, res, next) => {
  const key = req.ip || req.connection.remoteAddress;
  const now = Date.now();
  const windowMs = 15 * 60 * 1000; // 15 minutes
  const maxRequests = 100; // requests per window

  if (!rateLimiterMap.has(key)) {
    rateLimiterMap.set(key, {
      requests: 1,
      startTime: now
    });
    return next();
  }

  const record = rateLimiterMap.get(key);
  
  // Reset window if expired
  if (now - record.startTime > windowMs) {
    record.requests = 1;
    record.startTime = now;
    return next();
  }

  // Check if limit exceeded
  if (record.requests >= maxRequests) {
    return res.status(429).json({
      success: false,
      error: 'Too Many Requests',
      message: 'Rate limit exceeded. Please try again later.',
      retryAfter: Math.ceil((windowMs - (now - record.startTime)) / 1000)
    });
  }

  record.requests++;
  next();
};

// Cleanup old entries periodically
setInterval(() => {
  const now = Date.now();
  const windowMs = 15 * 60 * 1000;
  
  for (const [key, record] of rateLimiterMap.entries()) {
    if (now - record.startTime > windowMs) {
      rateLimiterMap.delete(key);
    }
  }
}, 5 * 60 * 1000); // Clean every 5 minutes
