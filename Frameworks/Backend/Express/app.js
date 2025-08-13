const express = require('express');
const debug = require('debug')('app:server');
const app = express();
const port = process.env.PORT || 3000;

// Debug middleware for request logging
const debugMiddleware = (req, res, next) => {
    const start = Date.now();
    
    // Log request details
    debug(`${req.method} ${req.url} - Started`);
    console.log('Request received:', {
        method: req.method,
        url: req.url,
        params: req.params,
        query: req.query,
        headers: {
            'user-agent': req.headers['user-agent'],
            'content-type': req.headers['content-type']
        }
    });
    
    // Override res.json to log responses
    const originalJson = res.json;
    res.json = function(data) {
        const duration = Date.now() - start;
        debug(`${req.method} ${req.url} - ${res.statusCode} - ${duration}ms`);
        console.log(`Response sent: ${res.statusCode} - ${duration}ms`);
        return originalJson.call(this, data);
    };
    
    next();
};

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(debugMiddleware);

// Performance monitoring middleware
app.use((req, res, next) => {
    const start = process.hrtime();
    
    res.on('finish', () => {
        const [seconds, nanoseconds] = process.hrtime(start);
        const duration = seconds * 1000 + nanoseconds / 1000000;
        
        if (duration > 100) {
            console.warn(`⚠️  Slow request detected: ${req.method} ${req.url} took ${duration.toFixed(2)}ms`);
        }
    });
    
    next();
});

// Routes
app.get('/', (req, res) => {
    debug('Home route accessed');
    res.json({ 
        message: 'Express.js Debugging Demo!',
        timestamp: new Date().toISOString(),
        environment: process.env.NODE_ENV || 'development'
    });
});

app.get('/users', (req, res) => {
    debug('Users list route accessed');
    const users = [
        { id: 1, name: 'John Doe', email: 'john@example.com' },
        { id: 2, name: 'Jane Smith', email: 'jane@example.com' },
        { id: 3, name: 'Bob Johnson', email: 'bob@example.com' }
    ];
    
    // Simulate processing time
    setTimeout(() => {
        res.json(users);
    }, Math.random() * 200);
});

app.get('/users/:id', (req, res) => {
    const userId = parseInt(req.params.id);
    debug(`User detail route accessed for ID: ${userId}`);
    
    console.log('Processing user ID:', userId);
    
    // Validate user ID
    if (isNaN(userId) || userId <= 0) {
        return res.status(400).json({ 
            error: 'Invalid user ID',
            provided: req.params.id,
            expected: 'positive integer'
        });
    }
    
    try {
        const user = {
            id: userId,
            name: `User ${userId}`,
            email: `user${userId}@example.com`,
            createdAt: new Date().toISOString()
        };
        
        console.log('User data prepared:', user);
        
        // Set breakpoint here to inspect the user object
        res.json(user);
    } catch (error) {
        console.error('Error processing user:', error);
        res.status(500).json({ 
            error: 'Internal server error',
            message: error.message 
        });
    }
});

app.post('/users', (req, res) => {
    debug('Create user route accessed');
    const userData = req.body;
    
    console.log('Received user data:', userData);
    
    // Validate required fields
    if (!userData.name) {
        return res.status(400).json({
            error: 'Validation failed',
            message: 'Name is required'
        });
    }
    
    try {
        // Simulate user creation
        const newUser = {
            id: Date.now(),
            name: userData.name,
            email: userData.email || `${userData.name.toLowerCase().replace(' ', '.')}@example.com`,
            createdAt: new Date().toISOString(),
            ...userData
        };
        
        console.log('New user created:', newUser);
        res.status(201).json(newUser);
    } catch (error) {
        console.error('Error creating user:', error);
        res.status(500).json({ 
            error: 'Failed to create user',
            message: error.message 
        });
    }
});

// Route to test error handling
app.get('/error', (req, res, next) => {
    debug('Error test route accessed');
    const error = new Error('This is a test error');
    error.statusCode = 500;
    next(error);
});

// Route to test memory usage
app.get('/memory', (req, res) => {
    const memUsage = process.memoryUsage();
    const formatBytes = (bytes) => Math.round(bytes / 1024 / 1024 * 100) / 100;
    
    res.json({
        memory: {
            rss: `${formatBytes(memUsage.rss)} MB`,
            heapTotal: `${formatBytes(memUsage.heapTotal)} MB`,
            heapUsed: `${formatBytes(memUsage.heapUsed)} MB`,
            external: `${formatBytes(memUsage.external)} MB`
        },
        uptime: `${Math.round(process.uptime())} seconds`
    });
});

// Custom error class
class AppError extends Error {
    constructor(message, statusCode) {
        super(message);
        this.statusCode = statusCode;
        this.status = `${statusCode}`.startsWith('4') ? 'fail' : 'error';
        this.isOperational = true;

        Error.captureStackTrace(this, this.constructor);
    }
}

// Global error handling middleware
app.use((err, req, res, next) => {
    err.statusCode = err.statusCode || 500;
    err.status = err.status || 'error';
    
    console.error('Error caught:', {
        message: err.message,
        statusCode: err.statusCode,
        stack: err.stack,
        url: req.url,
        method: req.method
    });

    if (process.env.NODE_ENV === 'development') {
        res.status(err.statusCode).json({
            status: err.status,
            error: err,
            message: err.message,
            stack: err.stack
        });
    } else {
        res.status(err.statusCode).json({
            status: err.status,
            message: err.isOperational ? err.message : 'Something went wrong!'
        });
    }
});

// 404 handler
app.use('*', (req, res) => {
    res.status(404).json({
        error: 'Not Found',
        message: `Route ${req.originalUrl} not found`,
        availableRoutes: [
            'GET /',
            'GET /users',
            'GET /users/:id',
            'POST /users',
            'GET /error',
            'GET /memory'
        ]
    });
});

// Start server
const server = app.listen(port, () => {
    debug(`Server starting on port ${port}`);
    console.log(`🚀 Express server running at http://localhost:${port}`);
    console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
    console.log('Available routes:');
    console.log('  GET  /');
    console.log('  GET  /users');
    console.log('  GET  /users/:id');
    console.log('  POST /users');
    console.log('  GET  /error (test error handling)');
    console.log('  GET  /memory (memory usage)');
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('SIGTERM received, shutting down gracefully');
    server.close(() => {
        console.log('Process terminated');
    });
});

process.on('SIGINT', () => {
    console.log('SIGINT received, shutting down gracefully');
    server.close(() => {
        console.log('Process terminated');
    });
});

module.exports = app;
