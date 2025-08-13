const jwt = require('jsonwebtoken');

const auth = (req, res, next) => {
  try {
    // Get token from header
    const token = req.header('Authorization')?.replace('Bearer ', '');
    
    if (!token) {
      return res.status(401).json({ 
        error: 'Access denied. No token provided.' 
      });
    }

    // Verify token
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'fallback_secret');
    
    // Add user info to request
    req.user = decoded;
    
    next();
  } catch (error) {
    res.status(401).json({ 
      error: 'Invalid token.' 
    });
  }
};

module.exports = auth;
