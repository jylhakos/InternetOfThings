# Node.js and Express.js application serving a React app on a Docker container

## Example: Configure Dockerfiles for Node.js and React app

Node.js stack: 

Express.js with latest security practices

React integration: 

React app with modern hooks

NoSQL database with connection pooling

MongoDB database initialization script: 

```

    // MongoDB initialization script
    db = db.getSiblingDB('nodeapp');

    // Create collections
    db.createCollection('users');
    db.createCollection('tasks');

    // Create indexes
    db.users.createIndex({ "email": 1 }, { unique: true });
    db.tasks.createIndex({ "userId": 1 });
    db.tasks.createIndex({ "createdAt": -1 });

    // Insert sample data (optional)
    db.users.insertOne({
        name: "Test User",
        email: "test@example.com",
        password: "$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewwrzqNlxN5.i0r6", // password: testpass
        createdAt: new Date()
    });

    print("MongoDB initialized successfully for Node.js application");

```
Authentication: 

JWT-based auth with bcrypt password hashing

Security: 

Helmet, CORS, rate limiting, input validation

Docker: 

Multi-stage builds, health checks, non-root users

To set up and deploy a Node.js and Express.js application with a React app in a Docker container on Linux, follow these steps.

Project structure

Organize your project with separate folders for the client (React) and server (Node.js/Express.js).

Dockerfile for Node.js/Express.js 

```

    FROM node:18-alpine
    WORKDIR /app
    COPY package.json package-lock.json ./
    RUN npm install --production
    COPY . .
    # Express server port
    EXPOSE 5000
    CMD ["node", "server.js"]

```

Dockerfile for React app

```

    # Stage 1: Build the React app
    FROM node:18-alpine AS builder
    WORKDIR /app
    COPY package.json ./
    RUN npm install
    COPY . .
    RUN npm run build

    # Stage 2: Serve the React app with Nginx
    FROM nginx:alpine
    COPY --from=builder /app/build /usr/share/nginx/html
    # Nginx port
    EXPOSE 80
    CMD ["nginx", "-g", "daemon off;"]

```

The docker-compose.yml file

```

    version: '3.8'
    services:
      frontend:
        build:
          context: ./client
          dockerfile: Dockerfile.client
        ports:
          - "3000:3000"
        depends_on:
          - backend

      backend:
        build:
          context: ./server
          dockerfile: Dockerfile.server
        ports:
          - "5000:5000" # Map host port to container port
        environment:
          NODE_ENV: production
          # Add any environment variables for your backend

```

Nginx configuration for React

```

    server {
        listen 3000;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;

        # Gzip compression
        gzip on;
        gzip_vary on;
        gzip_min_length 1024;
        gzip_proxied expired no-cache no-store private must-revalidate auth;
        gzip_types
            text/plain
            text/css
            text/xml
            text/javascript
            application/javascript
            application/xml+rss
            application/json;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;
        add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

        # Handle React Router
        location / {
            try_files $uri $uri/ /index.html;
            
            # Cache static assets
            location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
                expires 1y;
                add_header Cache-Control "public, immutable";
            }
        }

        # API proxy (optional)
        location /api {
            proxy_pass http://backend:5000/api;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
        }

        # Error pages
        error_page 404 /index.html;
    }

```

The environment variables

```

    # MongoDB Configuration
    MONGODB_URI=mongodb://root:password123@mongo:27017/nodeapp?authSource=admin
    MONGO_INITDB_ROOT_USERNAME=root
    MONGO_INITDB_ROOT_PASSWORD=password123
    MONGO_INITDB_DATABASE=nodeapp

    # Node.js/Express configuration
    NODE_ENV=production
    PORT=5000
    JWT_SECRET=your-super-secret-jwt-key-change-in-production-environment
    FRONTEND_URL=http://localhost:3000

    # React configuration
    REACT_APP_API_URL=http://localhost:5000

```
Navigate to the root of your my-app directory in your Linux terminal and run the docker-compose up command.

```

    $ docker-compose up --build -d

```
Your React app will be accessible on port 3000 of your browser, and the Express.js server will be accessible internally within the Docker network on port 5000 (and mapped to port 5000 on the host).
