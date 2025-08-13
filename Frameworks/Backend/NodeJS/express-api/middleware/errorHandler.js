const errorHandler = (err, req, res, next) => {
  console.error('Error Stack:', err.stack);
  
  // Default error
  let error = {
    status: 500,
    message: 'Server Error'
  };
  
  // Mongoose bad ObjectId
  if (err.name === 'CastError') {
    error = {
      status: 400,
      message: 'Invalid ID format'
    };
  }
  
  // Mongoose duplicate key
  if (err.code === 11000) {
    error = {
      status: 400,
      message: 'Duplicate field value entered'
    };
  }
  
  // Mongoose validation error
  if (err.name === 'ValidationError') {
    const message = Object.values(err.errors).map(val => val.message).join(', ');
    error = {
      status: 400,
      message
    };
  }
  
  // JWT errors
  if (err.name === 'JsonWebTokenError') {
    error = {
      status: 401,
      message: 'Invalid token'
    };
  }
  
  if (err.name === 'TokenExpiredError') {
    error = {
      status: 401,
      message: 'Token expired'
    };
  }
  
  // Send error response
  res.status(error.status).json({
    error: error.message,
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
};

module.exports = errorHandler;
