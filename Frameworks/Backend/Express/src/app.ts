import express, { Request, Response, NextFunction } from 'express';
import { createDebug } from './utils/debug';

const debug = createDebug('app:server');
const app = express();
const port = process.env.PORT || 3000;

// Custom error class
export class AppError extends Error {
    public statusCode: number;
    public status: string;
    public isOperational: boolean;

    constructor(message: string, statusCode: number) {
        super(message);
        this.statusCode = statusCode;
        this.status = `${statusCode}`.startsWith('4') ? 'fail' : 'error';
        this.isOperational = true;

        Error.captureStackTrace(this, this.constructor);
    }
}

// Interfaces
interface User {
    id: number;
    name: string;
    email?: string;
    createdAt: string;
}

interface CreateUserRequest {
    name: string;
    email?: string;
}

interface DebugInfo {
    method: string;
    url: string;
    params: any;
    query: any;
    headers: Record<string, string>;
}

// Debug middleware
const debugMiddleware = (req: Request, res: Response, next: NextFunction): void => {
    const start = Date.now();
    
    const debugInfo: DebugInfo = {
        method: req.method,
        url: req.url,
        params: req.params,
        query: req.query,
        headers: {
            'user-agent': req.headers['user-agent'] || '',
            'content-type': req.headers['content-type'] || ''
        }
    };
    
    debug('Request started: %O', debugInfo);
    
    const originalJson = res.json;
    res.json = function(data: any) {
        const duration = Date.now() - start;
        debug(`Request completed: ${req.method} ${req.url} - ${res.statusCode} - ${duration}ms`);
        return originalJson.call(this, data);
    };
    
    next();
};

// Performance monitoring
const performanceMiddleware = (req: Request, res: Response, next: NextFunction): void => {
    const start = process.hrtime.bigint();
    
    res.on('finish', () => {
        const end = process.hrtime.bigint();
        const duration = Number(end - start) / 1000000; // Convert to milliseconds
        
        if (duration > 100) {
            console.warn(`⚠️  Slow request: ${req.method} ${req.url} took ${duration.toFixed(2)}ms`);
        }
    });
    
    next();
};

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(debugMiddleware);
app.use(performanceMiddleware);

// Routes
app.get('/', (req: Request, res: Response) => {
    debug('Home route accessed');
    
    const response = {
        message: 'TypeScript Express.js Debugging Demo!',
        timestamp: new Date().toISOString(),
        environment: process.env.NODE_ENV || 'development',
        nodeVersion: process.version,
        platform: process.platform
    };
    
    res.json(response);
});

app.get('/users', (req: Request, res: Response) => {
    debug('Users list route accessed');
    
    const users: User[] = [
        {
            id: 1,
            name: 'John Doe',
            email: 'john@example.com',
            createdAt: new Date().toISOString()
        },
        {
            id: 2,
            name: 'Jane Smith',
            email: 'jane@example.com',
            createdAt: new Date().toISOString()
        },
        {
            id: 3,
            name: 'Bob Johnson',
            email: 'bob@example.com',
            createdAt: new Date().toISOString()
        }
    ];
    
    // Simulate async operation
    setTimeout(() => {
        res.json(users);
    }, Math.random() * 100);
});

app.get('/users/:id', (req: Request, res: Response, next: NextFunction) => {
    const userId = parseInt(req.params.id, 10);
    debug(`User detail route accessed for ID: ${userId}`);
    
    try {
        // Type guard for user ID validation
        if (!Number.isInteger(userId) || userId <= 0) {
            throw new AppError('Invalid user ID provided', 400);
        }
        
        const user: User = {
            id: userId,
            name: `User ${userId}`,
            email: `user${userId}@example.com`,
            createdAt: new Date().toISOString()
        };
        
        // Set breakpoint here to inspect the user object
        debug('User data prepared: %O', user);
        res.json(user);
        
    } catch (error) {
        next(error);
    }
});

app.post('/users', (req: Request, res: Response, next: NextFunction) => {
    debug('Create user route accessed');
    
    try {
        const userData: CreateUserRequest = req.body;
        
        // Validation
        if (!userData.name?.trim()) {
            throw new AppError('Name is required and cannot be empty', 400);
        }
        
        if (userData.name.length < 2) {
            throw new AppError('Name must be at least 2 characters long', 400);
        }
        
        // Create new user
        const newUser: User = {
            id: Date.now(),
            name: userData.name.trim(),
            email: userData.email || `${userData.name.toLowerCase().replace(/\s+/g, '.')}@example.com`,
            createdAt: new Date().toISOString()
        };
        
        debug('New user created: %O', newUser);
        res.status(201).json(newUser);
        
    } catch (error) {
        next(error);
    }
});

// Debug route for testing errors
app.get('/error/:type', (req: Request, res: Response, next: NextFunction) => {
    const errorType = req.params.type;
    debug(`Error test route accessed with type: ${errorType}`);
    
    switch (errorType) {
        case 'validation':
            next(new AppError('This is a validation error', 400));
            break;
        case 'auth':
            next(new AppError('Unauthorized access', 401));
            break;
        case 'notfound':
            next(new AppError('Resource not found', 404));
            break;
        case 'server':
            next(new AppError('Internal server error', 500));
            break;
        default:
            next(new AppError('Unknown error type', 400));
    }
});

// Memory and performance monitoring
app.get('/debug/memory', (req: Request, res: Response) => {
    const memUsage = process.memoryUsage();
    const formatBytes = (bytes: number): string => 
        `${Math.round(bytes / 1024 / 1024 * 100) / 100} MB`;
    
    const cpuUsage = process.cpuUsage();
    
    const debugInfo = {
        memory: {
            rss: formatBytes(memUsage.rss),
            heapTotal: formatBytes(memUsage.heapTotal),
            heapUsed: formatBytes(memUsage.heapUsed),
            external: formatBytes(memUsage.external)
        },
        cpu: {
            user: `${cpuUsage.user} microseconds`,
            system: `${cpuUsage.system} microseconds`
        },
        uptime: `${Math.round(process.uptime())} seconds`,
        version: process.version,
        platform: process.platform,
        arch: process.arch,
        pid: process.pid
    };
    
    res.json(debugInfo);
});

// Global error handling middleware
app.use((error: Error, req: Request, res: Response, next: NextFunction) => {
    let appError = error as AppError;
    
    // Convert generic errors to AppError
    if (!(error instanceof AppError)) {
        appError = new AppError(error.message || 'Something went wrong!', 500);
    }
    
    debug('Error caught: %O', {
        message: appError.message,
        statusCode: appError.statusCode,
        stack: appError.stack,
        url: req.url,
        method: req.method,
        body: req.body
    });
    
    const errorResponse: any = {
        status: appError.status,
        message: appError.message
    };
    
    // Include stack trace in development
    if (process.env.NODE_ENV === 'development') {
        errorResponse.stack = appError.stack;
        errorResponse.error = appError;
    }
    
    res.status(appError.statusCode).json(errorResponse);
});

// 404 handler
app.use('*', (req: Request, res: Response) => {
    res.status(404).json({
        error: 'Not Found',
        message: `Route ${req.originalUrl} not found`,
        availableRoutes: [
            'GET /',
            'GET /users',
            'GET /users/:id',
            'POST /users',
            'GET /error/:type',
            'GET /debug/memory'
        ]
    });
});

// Start server
const server = app.listen(port, () => {
    debug(`TypeScript Express server starting on port ${port}`);
    console.log(`🚀 TypeScript Express server running at http://localhost:${port}`);
    console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
    console.log(`Node.js: ${process.version}`);
    console.log('Available routes:');
    console.log('  GET  /');
    console.log('  GET  /users');
    console.log('  GET  /users/:id');
    console.log('  POST /users');
    console.log('  GET  /error/:type (validation|auth|notfound|server)');
    console.log('  GET  /debug/memory');
});

// Graceful shutdown
const shutdown = (signal: string) => {
    console.log(`${signal} received, shutting down gracefully`);
    server.close(() => {
        debug('Server closed');
        process.exit(0);
    });
};

process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));

export default app;
