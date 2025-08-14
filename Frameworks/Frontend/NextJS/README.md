# Web Application by Next.js + Express.js + Prisma ORM

A web application uses Next.js (React frontend) with Express.js (backend API) and Prisma ORM for PostgreSQL database interactions. This setup provides both server-side rendering (SSR) capabilities and a robust backend API infrastructure.

## Table of Contents

1. [Tech Stack](#tech-stack)
2. [Project](#project)
3. [Debugging in VS Code](#debugging-in-vs-code)
4. [Next.js vs Express.js](#nextjs-vs-expressjs)
5. [Getting Started](#getting-started)
6. [VS Code Configuration](#vs-code-configuration)
7. [Database Setup](#database-setup)
8. [Resources](#resources)

## Tech Stack

- **Frontend**: Next.js 15 with React (Server-Side Rendering)
- **Backend**: Express.js (Node.js framework)
- **Database**: PostgreSQL
- **ORM**: Prisma
- **Runtime**: Node.js 20.19.0
- **Bundler**: Webpack 5
- **Module System**: ESM (ECMAScript Modules)
- **Styling**: Tailwind CSS
- **Language**: TypeScript

## Project

## Project Structure

```
├── app/                   # Next.js App Router
├── components/           # Reusable React components
├── lib/                  # Utility functions and configurations
├── prisma/              # Database schema and migrations
├── public/              # Static assets
├── .vscode/             # VS Code configuration
│   └── launch.json      # Debug configurations
├── .env                 # Environment variables
├── .gitignore          # Git ignore rules
├── package.json        # Dependencies and scripts
└── next.config.mjs     # Next.js configuration
```

### Next.js
Next.js is a React framework for building server-rendered or statically exported React applications. It provides:
- **File-system based routing**: Automatic routing based on file structure
- **API routes**: Server-side logic and backend capabilities
- **Server-side rendering (SSR)**: Improved performance and SEO
- **Static site generation (SSG)**: Pre-rendered pages at build time
- **Image optimization**: Automatic image optimization and lazy loading

### Express.js
Express.js is a minimalist web application framework for Node.js, designed for:
- **Backend APIs**: Robust API development and management
- **Server-side logic**: Complex business logic handling
- **Database interactions**: Advanced database operations and connections
- **Middleware support**: Custom request processing and authentication
- **General-purpose backend**: Framework-agnostic backend development

### Can Next.js and Express.js be used together?

  Next.js and Express.js integration is chosen when you need:
- An existing Express.js backend to integrate with a new Next.js frontend
- More complex server-side logic and custom middleware
- Advanced database interactions that are better managed with a dedicated Express.js server
- Custom server requirements not hosted on Vercel's platform
- Full control over the server infrastructure

## Debugging in VS Code

Debugging Next.js applications in VS Code on Linux with Node.js involves configuring VS Code's debugger to attach to or launch your Next.js development server.

### 1. Configure launch.json

1. Open your Next.js project in VS Code
2. Go to the Run and Debug view (`Ctrl+Shift+D`)
3. Click on "create a launch.json file" (if one doesn't exist) and select "Node.js"
4. Add or modify the configurations for server-side and client-side debugging

### 2. VS Code Launch Configuration

Create `.vscode/launch.json` in your project root:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Next.js: debug server-side",
      "type": "node-terminal",
      "request": "launch",
      "command": "npm run dev"
    },
    {
      "name": "Next.js: debug client-side",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:3000"
    },
    {
      "name": "Next.js: debug client-side (Firefox)",
      "type": "firefox",
      "request": "launch",
      "url": "http://localhost:3000",
      "reAttach": true,
      "pathMappings": [
        {
          "url": "webpack://_N_E",
          "path": "${workspaceFolder}"
        }
      ]
    },
    {
      "name": "Next.js: debug full stack",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/node_modules/next/dist/bin/next",
      "runtimeArgs": ["--inspect"],
      "skipFiles": ["<node_internals>/**"],
      "serverReadyAction": {
        "action": "debugWithEdge",
        "killOnServerStop": true,
        "pattern": "- Local:.+(https?://.+)",
        "uriFormat": "%s",
        "webRoot": "${workspaceFolder}"
      }
    },
    {
      "name": "Express.js: debug server",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/server.js",
      "env": {
        "NODE_ENV": "development"
      },
      "runtimeArgs": ["--inspect"],
      "skipFiles": ["<node_internals>/**"]
    }
  ]
}
```

### 3. Debugging

- **Auto Attach**: Automatically attach debugger to Node.js processes
- **JavaScript Debug Terminal**: Run Node.js processes with debugging enabled
- **Breakpoints**: Set conditional breakpoints, logpoints, and hit count breakpoints
- **Source Maps**: Debug TypeScript and transpiled code with full source map support
- **Remote Debugging**: Debug applications running on remote servers or containers

### 4. Browser DevTools

#### Server-side debugging:
```bash
NODE_OPTIONS='--inspect' next dev
```

#### For Windows users:
```bash
npm install -D cross-env
```

Update package.json:
```json
{
  "scripts": {
    "dev": "cross-env NODE_OPTIONS='--inspect' next dev"
  }
}
```

## Next.js vs Express.js

| Aspect | Next.js | Express.js |
|--------|---------|------------|
| **Focus** | Frontend/React framework with SSR | Backend/API framework |
| **Routing** | File-system based | Manual route definition |
| **Rendering** | SSR, SSG, Client-side | Server-side only |
| **API Routes** | Built-in API routes | Full API framework |
| **Database** | Through API routes | Direct database connections |
| **Middleware** | Limited built-in | Extensive middleware ecosystem |
| **Deployment** | Vercel-optimized | Any Node.js host |

## Getting Started

### Prerequisites

- Node.js 20.19.0 or higher
- PostgreSQL database
- Prisma Postgres connection strings:
  - Prisma Postgres + Accelerate connection string
  - Prisma Postgres direct TCP connection string

### 1. Clone and Install

```bash
git clone [your-repo-url]
cd your-project-directory
npm install
# or
yarn install
# or
pnpm install
```

### 2. Environment Variables

Create `.env` file:

```env
# Prisma Postgres connection string (used for migrations)
DATABASE_URL="__YOUR_PRISMA_POSTGRES_CONNECTION_STRING__"

# Postgres connection string (used for queries by Prisma Client)
DIRECT_URL="__YOUR_PRISMA_POSTGRES_DIRECT_CONNECTION_STRING__"

NEXT_PUBLIC_URL="http://localhost:3000"
```

### 3. Database Setup

```bash
# Run migrations
pnpm prisma migrate dev --name init

# Seed the database
pnpm prisma db seed

# Generate Prisma Client
pnpm prisma generate
```

### 4. Start Development

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

## VS Code Configuration

### Essential Extensions

1. **ES7+ React/Redux/React-Native snippets**
2. **Prettier - Code formatter**
3. **ESLint**
4. **TypeScript Importer**
5. **Prisma** (for database schema)
6. **Firefox Debugger** (if using Firefox for debugging)

### Auto Attach Configuration

1. Open Command Palette (`Ctrl+Shift+P`)
2. Run "Debug: Toggle Auto Attach"
3. Select "smart" mode for automatic debugging

## Database Setup

This project uses Prisma ORM with PostgreSQL:

### Prisma Schema Features
- Type-safe database client
- Automatic migrations
- Database seeding
- Query optimization
- Connection pooling

### Example Model
```prisma
generator client {
  provider = "prisma-client"
  output = "../lib/generated/prisma"
  previewFeatures = ["driverAdapters", "queryCompiler"]
  runtime = "nodejs"
}

model Quote {
  id      Int       @id @default(autoincrement())
  text    String
  author  String
  kind    QuoteKind
  @@map("quotes")
}

enum QuoteKind {
  INSPIRATIONAL
  MOTIVATIONAL
  PHILOSOPHICAL
}
```

## DevOps

### Docker Setup for PostgreSQL

#### 1. PostgreSQL with Docker

Create a `docker-compose.yml` file for PostgreSQL:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: webapp_postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: webapp_user
      POSTGRES_PASSWORD: webapp_password
      POSTGRES_DB: webapp_database
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init:/docker-entrypoint-initdb.d
    networks:
      - webapp_network

  redis:
    image: redis:7-alpine
    container_name: webapp_redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - webapp_network

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local

networks:
  webapp_network:
    driver: bridge
```

#### 2. Start PostgreSQL

```bash
# Start PostgreSQL and Redis
docker-compose up -d

# Check container status
docker-compose ps

# View logs
docker-compose logs postgres

# Connect to PostgreSQL
docker exec -it webapp_postgres psql -U webapp_user -d webapp_database
```

#### 3. Environment Variables for Docker

Create `.env` file:

```env
# Database Configuration
DATABASE_URL="postgresql://webapp_user:webapp_password@localhost:5432/webapp_database"
DIRECT_URL="postgresql://webapp_user:webapp_password@localhost:5432/webapp_database"

# Redis Configuration
REDIS_URL="redis://localhost:6379"

# Application Configuration
NODE_ENV="development"
NEXT_PUBLIC_URL="http://localhost:3000"
API_URL="http://localhost:3000"

# Security
JWT_SECRET="your-jwt-secret-key"
NEXTAUTH_SECRET="your-nextauth-secret"
NEXTAUTH_URL="http://localhost:3000"
```

### Docker Setup for Node.js/Next.js Application

#### 1. Create Dockerfile

```dockerfile
# Base image
FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json yarn.lock* package-lock.json* pnpm-lock.yaml* ./
RUN \
  if [ -f yarn.lock ]; then yarn --frozen-lockfile; \
  elif [ -f package-lock.json ]; then npm ci; \
  elif [ -f pnpm-lock.yaml ]; then corepack enable pnpm && pnpm i --frozen-lockfile; \
  else echo "Lockfile not found." && exit 1; \
  fi

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Generate Prisma Client
RUN npx prisma generate

# Next.js collects completely anonymous telemetry data about general usage.
# Learn more here: https://nextjs.org/telemetry
# Uncomment the following line in case you want to disable telemetry during the build.
ENV NEXT_TELEMETRY_DISABLED 1

RUN \
  if [ -f yarn.lock ]; then yarn run build; \
  elif [ -f package-lock.json ]; then npm run build; \
  elif [ -f pnpm-lock.yaml ]; then corepack enable pnpm && pnpm run build; \
  else echo "Lockfile not found." && exit 1; \
  fi

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Automatically leverage output traces to reduce image size
# https://nextjs.org/docs/advanced-features/output-file-tracing
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

# server.js is created by next build from the standalone output
# https://nextjs.org/docs/pages/api-reference/next-config-js/output
CMD ["node", "server.js"]
```

#### 2. Create .dockerignore

```dockerignore
# Dependencies
node_modules
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Next.js
.next
out
build

# Production
dist

# Misc
.DS_Store
*.tgz

# Debug
*.log

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Vercel
.vercel

# TypeScript
*.tsbuildinfo

# Docker
Dockerfile
.dockerignore
docker-compose.yml

# Git
.git
.gitignore
README.md

# IDE
.vscode
.idea

# Testing
coverage
.nyc_output

# Prisma
prisma/migrations
```

#### 3. Docker Compose Setup

Create `docker-compose.full.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: webapp_postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: webapp_user
      POSTGRES_PASSWORD: webapp_password
      POSTGRES_DB: webapp_database
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - webapp_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U webapp_user -d webapp_database"]
      interval: 30s
      timeout: 10s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: webapp_redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - webapp_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5

  webapp:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: webapp_frontend
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://webapp_user:webapp_password@postgres:5432/webapp_database
      - DIRECT_URL=postgresql://webapp_user:webapp_password@postgres:5432/webapp_database
      - REDIS_URL=redis://redis:6379
      - NODE_ENV=production
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - webapp_network

  nginx:
    image: nginx:alpine
    container_name: webapp_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./docker/nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - webapp
    networks:
      - webapp_network

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local

networks:
  webapp_network:
    driver: bridge
```

### Deployment Scripts

#### 1. Development

Create `scripts/dev-setup.sh`:

```bash
#!/bin/bash

echo "Setting up development environment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo " Creating .env file..."
    cp .env.example .env
    echo "Please update the .env file with your configuration"
fi

# Start PostgreSQL and Redis
echo "🐘 Starting PostgreSQL and Redis..."
docker-compose up -d

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until docker exec webapp_postgres pg_isready -U webapp_user -d webapp_database; do
    sleep 2
done

# Install dependencies
echo "Installing dependencies..."
npm install

# Generate Prisma client
echo "Generating Prisma client..."
npx prisma generate

# Run migrations
echo "Running database migrations..."
npx prisma migrate dev

# Seed database
echo "🌱 Seeding database..."
npx prisma db seed

echo "Development environment setup complete."
echo "You can now run: npm run dev"
```

#### 2. Production

Create `scripts/deploy.sh`:

```bash
#!/bin/bash

echo "Deploying to production..."

# Build and push Docker image
echo "Building Docker image..."
docker build -t webapp:latest .

# Stop existing containers
echo "Stopping existing containers..."
docker-compose -f docker-compose.full.yml down

# Start production environment
echo "Starting production environment..."
docker-compose -f docker-compose.full.yml up -d

# Run migrations
echo "Running database migrations..."
docker exec webapp_frontend npx prisma migrate deploy

echo "Deployment complete."
echo "Application is running at http://localhost"
```

#### 3. Database Backup

Create `scripts/backup-db.sh`:

```bash
#!/bin/bash

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/webapp_backup_$TIMESTAMP.sql"

echo "Creating database backup..."

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Create backup
docker exec webapp_postgres pg_dump -U webapp_user -d webapp_database > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

echo "Database backup created: $BACKUP_FILE.gz"

# Clean up old backups (keep last 7 days)
find $BACKUP_DIR -name "webapp_backup_*.sql.gz" -mtime +7 -delete
```

### Production

#### 1. Environment Variables for Production

```env
# Production Database
DATABASE_URL="postgresql://user:password@prod-db-host:5432/webapp"
DIRECT_URL="postgresql://user:password@prod-db-host:5432/webapp"

# Redis
REDIS_URL="redis://prod-redis-host:6379"

# Security
JWT_SECRET="production-jwt-secret-very-long-and-secure"
NEXTAUTH_SECRET="production-nextauth-secret-very-long-and-secure"
NEXTAUTH_URL="https://yourdomain.com"

# Application
NODE_ENV="production"
NEXT_PUBLIC_URL="https://yourdomain.com"
API_URL="https://yourdomain.com"

# Analytics
GOOGLE_ANALYTICS_ID="GA-XXXXXXXXX"

# Email
SMTP_HOST="smtp.example.com"
SMTP_PORT="587"
SMTP_USER="noreply@yourdomain.com"
SMTP_PASSWORD="smtp-password"
```

#### 2. Nginx Configuration

Create `docker/nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream webapp {
        server webapp:3000;
    }

    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;

        location / {
            return 301 https://$server_name$request_uri;
        }
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://webapp;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
        }
    }
}
```

### Monitoring and Logging

#### 1. Health Check Endpoints

The application includes health check endpoints:
- `GET /api/health` - Basic health check
- `GET /api/health/db` - Database connectivity check
- `GET /api/health/detailed` - Comprehensive system status

#### 2. Docker Health Checks

```yaml
# In docker-compose.yml
webapp:
  # ... other configuration
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s
```

#### 3. Log Management

```bash
# View application logs
docker-compose logs -f webapp

# View database logs
docker-compose logs -f postgres

# View all logs
docker-compose logs -f
```

## Resources

### Documentation
- [Next.js Debugging Guide](https://nextjs.org/docs/app/guides/debugging)
- [Node.js debugging in VS Code](https://code.visualstudio.com/docs/nodejs/nodejs-debugging)
- [Express.js Examples](https://expressjs.com/en/starter/examples.html)
- [Prisma Documentation](https://www.prisma.io/docs)

### Example Repositories
- [Prisma Next.js Starter](https://github.com/prisma/prisma-examples/tree/latest/generator-prisma-client/nextjs-starter-webpack)
- [Express.js Examples](https://github.com/expressjs/express/tree/master/examples)

### Community Resources
- [Prisma Discord Community](https://pris.ly/discord)
- [Next.js Discord](https://nextjs.org/discord)
- [Express.js GitHub](https://github.com/expressjs/express)

## Development Commands

```bash
# Development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Database operations
npx prisma studio          # Database GUI
npx prisma migrate dev      # Run migrations
npx prisma generate         # Generate client
npx prisma db seed         # Seed database

# Code quality
npm run lint               # ESLint
npm run format            # Prettier

# Docker operations
docker-compose up -d       # Start PostgreSQL and Redis
docker-compose down        # Stop all services
docker-compose logs -f     # View logs

# DevOps scripts
chmod +x scripts/*.sh      # Make scripts executable
./scripts/dev-setup.sh     # Setup development environment
./scripts/deploy.sh        # Deploy to production
./scripts/backup-db.sh     # Backup database
```

## RESTful API Endpoints

### Frontend React UI with Server-Side Rendering

The React frontend uses server-side rendering (SSR) and consumes the following RESTful API endpoints:

### 1. Quotes API

```bash
# Get all quotes with filtering and pagination
GET /api/quotes?search=inspiration&category=motivational&limit=20&offset=0

# Get random quote
GET /api/quotes/random

# Get quote statistics
GET /api/quotes/stats

# Get quotes by kind
GET /api/quotes/kind/inspirational

# Get specific quote
GET /api/quotes/:id

# Create new quote (POST)
POST /api/quotes
Content-Type: application/json
{
  "text": "Your quote text here",
  "author": "Author Name",
  "category": "motivational",
  "kind": "inspirational",
  "tags": ["motivation", "success"]
}

# Update quote (PUT)
PUT /api/quotes/:id

# Delete quote (DELETE)
DELETE /api/quotes/:id
```

### 2. Blog Posts API

```bash
# Get all blog posts with filtering
GET /api/posts?search=nextjs&tag=tutorial&limit=12&offset=0

# Get featured posts
GET /api/posts/featured?limit=3

# Get popular posts
GET /api/posts/popular?limit=5

# Get specific post by slug
GET /api/posts/:slug

# Like/Unlike post
POST /api/posts/:id/like
DELETE /api/posts/:id/like

# Create new post (POST)
POST /api/posts
Content-Type: application/json
{
  "title": "Your Blog Post Title",
  "content": "Blog post content here...",
  "excerpt": "Short description",
  "tags": ["nextjs", "tutorial"],
  "featured": false,
  "published": true
}
```

### 3. Products API

```bash
# Get all products with filtering
GET /api/products?category=electronics&minPrice=50&maxPrice=200&inStock=true

# Get featured products
GET /api/products/featured?limit=4

# Get product categories
GET /api/products/categories

# Get specific product
GET /api/products/:id

# Get product reviews
GET /api/products/:id/reviews?limit=10&offset=0

# Update product stock
PATCH /api/products/:id/stock
Content-Type: application/json
{
  "quantity": 10,
  "operation": "add"
}

# Add product review
POST /api/products/:id/reviews
Content-Type: application/json
{
  "rating": 5,
  "title": "Great product!",
  "comment": "Really satisfied with this purchase",
  "reviewerName": "John Doe",
  "reviewerEmail": "john@example.com"
}
```

### 4. Users API

```bash
# Get all users
GET /api/users?limit=20&offset=0

# Get featured users
GET /api/users/featured?limit=6

# Get user profile
GET /api/users/:username

# Follow/Unfollow user
POST /api/users/:id/follow
DELETE /api/users/:id/follow

# Create user profile
POST /api/users
Content-Type: application/json
{
  "username": "johndoe",
  "email": "john@example.com",
  "name": "John Doe",
  "bio": "Software developer",
  "avatar": "https://example.com/avatar.jpg"
}
```

### 5. Analytics API

```bash
# Get analytics overview
GET /api/analytics/overview?period=7d

# Get traffic analytics
GET /api/analytics/traffic?period=7d&groupBy=day

# Get page analytics
GET /api/analytics/pages?period=7d&limit=10

# Get real-time analytics
GET /api/analytics/realtime

# Get custom events
GET /api/analytics/events?eventName=button_click&period=7d

# Track custom event
POST /api/analytics/events
Content-Type: application/json
{
  "name": "button_click",
  "category": "engagement",
  "label": "hero_cta",
  "page": "/",
  "value": 1
}

# Get conversion analytics
GET /api/analytics/conversions?period=7d&funnelType=general

# Get goal completion analytics
GET /api/analytics/goals?period=7d
```

### Frontend Integration

```javascript
// React component example using the API
import { useState, useEffect } from 'react';
import { quotesApi, productsApi } from '@/lib/api';

export default function HomePage() {
  const [data, setData] = useState({
    randomQuote: null,
    featuredProducts: []
  });

  useEffect(() => {
    async function loadData() {
      try {
        const [quoteRes, productsRes] = await Promise.all([
          quotesApi.getRandom(),
          productsApi.getFeatured({ limit: 4 })
        ]);
        
        setData({
          randomQuote: quoteRes.data,
          featuredProducts: productsRes.data
        });
      } catch (error) {
        console.error('Failed to load data:', error);
      }
    }
    
    loadData();
  }, []);

  return (
    <div>
      {data.randomQuote && (
        <blockquote>"{data.randomQuote.text}" - {data.randomQuote.author}</blockquote>
      )}
      
      <div className="products-grid">
        {data.featuredProducts.map(product => (
          <div key={product.id} className="product-card">
            <h3>{product.name}</h3>
            <p>${product.price}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### API Response Format

All API endpoints follow a consistent response format:

```javascript
// Success Response
{
  "success": true,
  "data": { /* response data */ },
  "message": "Operation completed successfully", // Optional
  "pagination": { // For paginated endpoints
    "total": 100,
    "limit": 20,
    "offset": 0,
    "hasMore": true
  }
}

// Error Response
{
  "success": false,
  "error": "Error message description",
  "details": { /* additional error details */ } // Optional
}
```

### References

[How to use Prisma in Docker](https://www.prisma.io/docs/guides/docker)

[How to deploy your Next.js application](https://nextjs.org/docs/pages/getting-started/deploying)

[How to Build a Fullstack App with Next.js, Prisma, and Postgres](https://vercel.com/guides/nextjs-prisma-postgres)

[Why Express and Prisma?](https://www.prisma.io/express)

[Express web framework](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Server-side/Express_Nodejs)

[Express](https://github.com/expressjs/express)