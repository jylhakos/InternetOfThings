const jwt = require('jsonwebtoken');
const axios = require('axios');

const authenticateToken = async (req, res, next) => {
  try {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

    if (!token) {
      return res.status(401).json({ error: 'Access token required' });
    }

    // Option 1: Verify token locally (faster)
    try {
      const decoded = jwt.verify(token, process.env.JWT_SECRET || 'fallback-secret');
      req.user = decoded;
      next();
    } catch (jwtError) {
      // Option 2: Verify with auth service (more secure)
      try {
        const authServiceUrl = process.env.AUTH_SERVICE_URL || 'http://localhost:3001';
        const response = await axios.post(`${authServiceUrl}/api/auth/verify`, { token });
        
        if (response.data.valid) {
          req.user = { userId: response.data.userId, email: response.data.email };
          next();
        } else {
          res.status(401).json({ error: 'Invalid token' });
        }
      } catch (authServiceError) {
        console.error('Auth service error:', authServiceError.message);
        res.status(401).json({ error: 'Token verification failed' });
      }
    }
  } catch (error) {
    console.error('Authentication error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
};

module.exports = { authenticateToken };
