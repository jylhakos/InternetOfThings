# Debugging Express.js & Node.js

## Debugging Express.js and Node.js in Linux/Debian with VS Code

### Table of Contents
1. [Prerequisites](#prerequisites)
2. [VS Code Debugging](#vs-code-debugging)
3. [Node.js Inspector and Chrome DevTools](#nodejs-inspector-and-chrome-devtools)
4. [Debugging Tools and Techniques](#debugging-tools)
5. [Testing Frameworks](#testing-frameworks)
6. [TypeScript Debugging](#typescript-debugging)
7. [Docker Containerized Debugging](#docker-containerized-debugging)
8. [GitHub Copilot for Debugging](#github-copilot-for-debugging)
9. [References](#references)

**Quick Reference**: See [DEBUG.md](./DEBUG.md) for a list of debugging commands.

---

## Prerequisites

### 1. System Requirements (Linux/Debian)

**Install Node.js and npm:**
```bash
# Using Node Version Manager (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install --lts
nvm use --lts

# Or using package manager
sudo apt update
sudo apt install nodejs npm

# Verify installation
node --version
npm --version
```

**Install Visual Studio Code:**
```bash
# Download and install VS Code
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
sudo apt update
sudo apt install code

# Launch VS Code
code
```

**Essential VS Code Extensions:**
```bash
# Install via command line
code --install-extension ms-vscode.vscode-node-debug2
code --install-extension ms-vscode.js-debug
code --install-extension github.copilot
code --install-extension github.copilot-chat
code --install-extension bradlc.vscode-tailwindcss
code --install-extension rangav.vscode-thunder-client
code --install-extension ms-vscode.vscode-typescript-next
```

---

## VS Code Debugging

### 1. Basic Express.js Project Setup

**Create a new Express.js project:**
```bash
mkdir express-debug-demo
cd express-debug-demo
npm init -y
npm install express
npm install --save-dev nodemon
```

**Create basic Express application (app.js):**
```javascript
const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.get('/', (req, res) => {
    res.json({ message: 'Hello World!' });
});

app.get('/users/:id', (req, res) => {
    const userId = req.params.id;
    const user = { id: userId, name: `User ${userId}` };
    res.json(user);
});

app.post('/users', (req, res) => {
    const userData = req.body;
    // Simulate user creation
    const newUser = { id: Date.now(), ...userData };
    res.status(201).json(newUser);
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).send('Something broke!');
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});

module.exports = app;
```

### 2. VS Code Launch Configuration

**Create .vscode/launch.json:**
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Launch Express App",
            "type": "node",
            "request": "launch",
            "program": "${workspaceFolder}/app.js",
            "console": "integratedTerminal",
            "restart": true,
            "runtimeExecutable": "node",
            "skipFiles": [
                "<node_internals>/**"
            ],
            "env": {
                "NODE_ENV": "development",
                "DEBUG": "express:*"
            }
        },
        {
            "name": "Launch with Nodemon",
            "type": "node",
            "request": "launch",
            "program": "${workspaceFolder}/node_modules/.bin/nodemon",
            "args": ["app.js"],
            "console": "integratedTerminal",
            "restart": true,
            "protocol": "inspector",
            "env": {
                "NODE_ENV": "development"
            }
        },
        {
            "name": "Attach to Process",
            "type": "node",
            "request": "attach",
            "port": 9229,
            "restart": true,
            "localRoot": "${workspaceFolder}",
            "remoteRoot": null,
            "skipFiles": [
                "<node_internals>/**"
            ]
        }
    ]
}
```

**Create .vscode/tasks.json:**
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Start Express Server",
            "type": "shell",
            "command": "npm",
            "args": ["start"],
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            },
            "problemMatcher": []
        },
        {
            "label": "Debug Express Server",
            "type": "shell",
            "command": "node",
            "args": ["--inspect", "app.js"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        }
    ]
}
```

---

## Node.js Inspector and Chrome DevTools

### 1. Using Node.js Inspector

**Start your application with debugging enabled:**
```bash
# Basic inspector (default port 9229)
node --inspect app.js

# Custom port
node --inspect=5858 app.js

# Break on first line
node --inspect-brk app.js

# With specific host binding
node --inspect=0.0.0.0:9229 app.js
```

**Connect Chrome DevTools:**
1. Open Chrome browser
2. Navigate to `chrome://inspect`
3. Click "Open dedicated DevTools for Node"
4. Set breakpoints and inspect variables

### 2. Debug Environment Variables

**Create .env file:**
```env
NODE_ENV=development
PORT=3000
DEBUG=express:*,app:*
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
```

**Load environment variables:**
```javascript
require('dotenv').config();

const debug = require('debug')('app:server');

debug('Server starting with environment:', process.env.NODE_ENV);
```

---

## Debugging Tools and Techniques {#debugging-tools}

### 1. Console-based Debugging

**Strategic console.log placement:**
```javascript
app.get('/users/:id', (req, res) => {
    console.log('Request received:', {
        method: req.method,
        url: req.url,
        params: req.params,
        headers: req.headers
    });
    
    const userId = req.params.id;
    console.log('Processing user ID:', userId);
    
    try {
        const user = { id: userId, name: `User ${userId}` };
        console.log('User data prepared:', user);
        res.json(user);
    } catch (error) {
        console.error('Error processing user:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});
```

### 2. Debug Module Usage

**Install and configure debug module:**
```bash
npm install debug
```

**Usage in application:**
```javascript
const debug = require('debug');
const serverDebug = debug('app:server');
const dbDebug = debug('app:database');
const routeDebug = debug('app:routes');

serverDebug('Server starting on port %s', port);

app.get('/users', (req, res) => {
    routeDebug('GET /users called');
    dbDebug('Fetching users from database');
    // ... route logic
});
```

**Enable debug output:**
```bash
# Enable all app debugging
DEBUG=app:* node app.js

# Enable specific modules
DEBUG=app:server,app:routes node app.js

# Enable Express internal debugging
DEBUG=express:* node app.js
```

### 3. Advanced Debugging Techniques

**Memory and performance monitoring:**
```javascript
// Monitor memory usage
setInterval(() => {
    const memUsage = process.memoryUsage();
    console.log('Memory usage:', {
        rss: Math.round(memUsage.rss / 1024 / 1024) + ' MB',
        heapTotal: Math.round(memUsage.heapTotal / 1024 / 1024) + ' MB',
        heapUsed: Math.round(memUsage.heapUsed / 1024 / 1024) + ' MB'
    });
}, 30000);

// Performance timing
app.use((req, res, next) => {
    const start = Date.now();
    res.on('finish', () => {
        const duration = Date.now() - start;
        console.log(`${req.method} ${req.url} - ${res.statusCode} - ${duration}ms`);
    });
    next();
});
```

---

## Testing Frameworks

### 1. Setup Testing Environment

**Install testing dependencies:**
```bash
npm install --save-dev mocha chai supertest jest
npm install --save-dev @types/mocha @types/chai @types/supertest  # For TypeScript
```

### 2. Mocha + Chai + Supertest Example

**Create test/app.test.js:**
```javascript
const request = require('supertest');
const { expect } = require('chai');
const app = require('../app');

describe('Express App Tests', () => {
    describe('GET /', () => {
        it('should return hello world message', async () => {
            const response = await request(app)
                .get('/')
                .expect(200);
            
            expect(response.body).to.have.property('message');
            expect(response.body.message).to.equal('Hello World!');
        });
    });

    describe('GET /users/:id', () => {
        it('should return user data', async () => {
            const userId = '123';
            const response = await request(app)
                .get(`/users/${userId}`)
                .expect(200);
            
            expect(response.body).to.have.property('id', userId);
            expect(response.body).to.have.property('name', `User ${userId}`);
        });
    });

    describe('POST /users', () => {
        it('should create a new user', async () => {
            const userData = { name: 'John Doe', email: 'john@example.com' };
            
            const response = await request(app)
                .post('/users')
                .send(userData)
                .expect(201);
            
            expect(response.body).to.have.property('id');
            expect(response.body.name).to.equal(userData.name);
            expect(response.body.email).to.equal(userData.email);
        });
    });
});
```

### 3. Jest Configuration

**Create jest.config.js:**
```javascript
module.exports = {
    testEnvironment: 'node',
    collectCoverage: true,
    coverageDirectory: 'coverage',
    coverageReporters: ['text', 'lcov', 'html'],
    testMatch: [
        '**/__tests__/**/*.js',
        '**/?(*.)+(spec|test).js'
    ],
    verbose: true
};
```

### 4. Package.json Scripts

**Add test scripts to package.json:**
```json
{
    "scripts": {
        "start": "node app.js",
        "dev": "nodemon app.js",
        "test": "mocha test/**/*.test.js",
        "test:watch": "mocha test/**/*.test.js --watch",
        "test:coverage": "nyc mocha test/**/*.test.js",
        "jest": "jest",
        "jest:watch": "jest --watch",
        "debug": "node --inspect app.js"
    }
}
```

---

## TypeScript Debugging

### 1. TypeScript Project Setup

**Install TypeScript dependencies:**
```bash
npm install --save-dev typescript ts-node @types/node @types/express
npm install --save-dev tsconfig-paths  # For path mapping
```

**Create tsconfig.json:**
```json
{
    "compilerOptions": {
        "target": "ES2020",
        "module": "commonjs",
        "outDir": "./dist",
        "rootDir": "./src",
        "strict": true,
        "esModuleInterop": true,
        "skipLibCheck": true,
        "forceConsistentCasingInFileNames": true,
        "sourceMap": true,
        "declaration": true,
        "declarationMap": true,
        "resolveJsonModule": true,
        "baseUrl": "./",
        "paths": {
            "@/*": ["src/*"],
            "@controllers/*": ["src/controllers/*"],
            "@middleware/*": ["src/middleware/*"],
            "@routes/*": ["src/routes/*"]
        }
    },
    "include": ["src/**/*"],
    "exclude": ["node_modules", "dist", "test"]
}
```

### 2. TypeScript Express Application

**Create src/app.ts:**
```typescript
import express, { Request, Response, NextFunction } from 'express';
import { AppError } from './middleware/errorHandler';

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Interfaces
interface User {
    id: string;
    name: string;
    email?: string;
}

// Routes
app.get('/', (req: Request, res: Response) => {
    res.json({ message: 'TypeScript Express App!' });
});

app.get('/users/:id', (req: Request, res: Response, next: NextFunction) => {
    try {
        const userId: string = req.params.id;
        const user: User = {
            id: userId,
            name: `User ${userId}`,
            email: `user${userId}@example.com`
        };
        res.json(user);
    } catch (error) {
        next(new AppError('User not found', 404));
    }
});

// Error handling
app.use((err: AppError, req: Request, res: Response, next: NextFunction) => {
    console.error(err.stack);
    res.status(err.statusCode || 500).json({
        error: err.message || 'Internal Server Error'
    });
});

app.listen(port, () => {
    console.log(`TypeScript Express server running at http://localhost:${port}`);
});

export default app;
```

### 3. TypeScript Debugging Configuration

**Update .vscode/launch.json for TypeScript:**
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug TypeScript App",
            "type": "node",
            "request": "launch",
            "program": "${workspaceFolder}/src/app.ts",
            "runtimeArgs": ["-r", "ts-node/register", "-r", "tsconfig-paths/register"],
            "console": "integratedTerminal",
            "restart": true,
            "env": {
                "NODE_ENV": "development"
            },
            "skipFiles": [
                "<node_internals>/**"
            ],
            "sourceMaps": true,
            "outFiles": ["${workspaceFolder}/dist/**/*.js"]
        },
        {
            "name": "Debug Compiled JS",
            "type": "node",
            "request": "launch",
            "program": "${workspaceFolder}/dist/app.js",
            "preLaunchTask": "tsc: build - tsconfig.json",
            "outFiles": ["${workspaceFolder}/dist/**/*.js"],
            "console": "integratedTerminal"
        }
    ]
}
```

---

## Docker Containerized Debugging

### 1. Dockerfile for Development

**Create Dockerfile.dev:**
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=development

# Copy source code
COPY . .

# Expose debug port
EXPOSE 3000 9229

# Run with debugging enabled
CMD ["node", "--inspect=0.0.0.0:9229", "app.js"]
```

### 2. Docker Compose for Development

**Create docker-compose.dev.yml:**
```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
      - "9229:9229"  # Debug port
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
      - DEBUG=express:*,app:*
    command: ["nodemon", "--inspect=0.0.0.0:9229", "app.js"]
    
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 3. Debug Container from VS Code

**Add to .vscode/launch.json:**
```json
{
    "name": "Attach to Docker",
    "type": "node",
    "request": "attach",
    "port": 9229,
    "address": "localhost",
    "localRoot": "${workspaceFolder}",
    "remoteRoot": "/app",
    "skipFiles": [
        "<node_internals>/**"
    ]
}
```

---

## GitHub Copilot for Debugging

### 1. Setup GitHub Copilot

**Install Copilot extensions:**
```bash
code --install-extension github.copilot
code --install-extension github.copilot-chat
```

### 2. Using Copilot for Debugging

**Copilot Chat Commands for Debugging:**
- `@workspace /fix` - Fix code issues in workspace
- `@workspace /explain` - Explain complex code sections
- `@workspace /tests` - Generate test cases
- `/optimize` - Optimize performance

**Example Copilot-generated debug middleware:**
```javascript
// Generated with: "Create error logging middleware"
const debugMiddleware = (req, res, next) => {
    const start = Date.now();
    
    // Log request
    console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
    
    // Override res.json to log responses
    const originalJson = res.json;
    res.json = function(data) {
        const duration = Date.now() - start;
        console.log(`[${new Date().toISOString()}] Response ${res.statusCode} - ${duration}ms`);
        return originalJson.call(this, data);
    };
    
    next();
};
```

---

### 1. Environment-specific Debugging

**Development vs Production:**
```javascript
const isDev = process.env.NODE_ENV === 'development';

if (isDev) {
    // Development-only debugging
    app.use(require('morgan')('dev'));
    app.use((req, res, next) => {
        console.log('Request body:', req.body);
        next();
    });
}

// Production-safe logging
const logger = require('winston');
logger.info('Server started', { port, environment: process.env.NODE_ENV });
```

### 2. Error Handling Strategy

**Centralized error handling:**
```javascript
class AppError extends Error {
    constructor(message, statusCode) {
        super(message);
        this.statusCode = statusCode;
        this.status = `${statusCode}`.startsWith('4') ? 'fail' : 'error';
        this.isOperational = true;

        Error.captureStackTrace(this, this.constructor);
    }
}

const globalErrorHandler = (err, req, res, next) => {
    err.statusCode = err.statusCode || 500;
    err.status = err.status || 'error';

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
};
```

### 3. Performance Monitoring

**Basic performance tracking:**
```javascript
const performanceMonitor = (req, res, next) => {
    const start = process.hrtime();
    
    res.on('finish', () => {
        const [seconds, nanoseconds] = process.hrtime(start);
        const duration = seconds * 1000 + nanoseconds / 1000000;
        
        console.log(`${req.method} ${req.url} - ${res.statusCode} - ${duration.toFixed(2)}ms`);
        
        if (duration > 1000) {
            console.warn(`Slow request detected: ${req.url} took ${duration.toFixed(2)}ms`);
        }
    });
    
    next();
};
```

## What's Vite Relationship with Express.js/Node.js?

### Vite
**Vite** is a frontend build tool that provides:
- Fast cold server start
- Lightning-fast Hot Module Replacement (HMR)
- Rich features out-of-the-box
- Optimized builds

### Vite's Role in Development

**Frontend Development Tool:**
```javascript
// Vite is primarily for frontend, but can work with Express
// Example: Frontend (Vite) + Backend (Express) setup

// vite.config.js (Frontend)
import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:3000',  // Your Express server
        changeOrigin: true
      }
    }
  }
})
```

### Integration Pattern: Vite Frontend + Express Backend

**Full-stack development setup:**
```bash
# Project structure
my-app/
├── frontend/          # Vite React/Vue app
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── backend/           # Express API
│   ├── app.js
│   ├── routes/
│   └── package.json
└── package.json       # Root package.json
```

**Root package.json with concurrent development:**
```json
{
  "scripts": {
    "dev": "concurrently \"npm run dev:backend\" \"npm run dev:frontend\"",
    "dev:backend": "cd backend && npm run dev",
    "dev:frontend": "cd frontend && npm run dev",
    "build": "cd frontend && npm run build",
    "start": "cd backend && npm start"
  },
  "devDependencies": {
    "concurrently": "^7.6.0"
  }
}
```


## References

### Documentation
- [Express.js Official Documentation](https://expressjs.com/)
- [Express.js Starter Guide](https://expressjs.com/en/starter/installing.html)
- [Mozilla Express/Node.js Introduction](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Server-side/Express_Nodejs/Introduction)
- [VS Code TypeScript Debugging](https://code.visualstudio.com/docs/typescript/typescript-debugging)
- [Prisma Docker Guide](https://www.prisma.io/docs/guides/docker)
- [DEBUG.md](./DEBUG.md) - Quick reference for debugging commands and techniques

### Debugging Tools
- **VS Code Extensions:**
  - Node.js Debugger (built-in)
  - Thunder Client (API testing)
  - REST Client
  - Error Lens
- **CLI Tools:**
  - `lsof -i tcp:3000` - Check port usage
  - `htop` - Monitor system resources
  - `journalctl -u service-name` - Check service logs

### Testing Tools
- **Unit Testing:** Mocha, Jest, Jasmine
- **API Testing:** Supertest, Postman, Thunder Client
- **Load Testing:** Artillery, k6
- **Mocking:** Sinon, nock

### Open Source Debugging Tools
- **Debug Module:** `npm install debug`
- **Winston Logger:** `npm install winston`
- **Morgan HTTP Logger:** `npm install morgan`
- **Clinic.js:** Performance profiling
- **0x:** Flame graph profiler

---

