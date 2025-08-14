# Vite Setup for JavaScript and TypeScript - Migration to Next.js

The tutorial helps to setup Vite for JavaScript and TypeScript development with VS Code on Linux/Debian systems which involves the following steps, including debugging configurations and DevOps build processes.

**Last Updated**: August 2025
**Vite Version**: 6.x
**Supported Node.js**: 18.x, 20.x, 22.x

## Table of Contents

- [Prerequisites](#prerequisites)
- [Project Setup](#project-setup)
- [Development Server](#development-server)
- [VS Code Configuration](#vs-code-configuration)
- [Debugging](#debugging)
- [DevOps Build Configuration](#devops-build-configuration)
- [Available Scripts](#available-scripts)
- [Migration to Next.js](#migration-to-nextjs)
- [References](#references)

## Prerequisites

### System Requirements

Ensure you have the following installed on your Linux/Debian system:

```bash
# Install Node.js and npm
sudo apt update
sudo apt install nodejs npm

# Verify installation
node -v
npm -v

# Optional: Install yarn or pnpm
npm install -g yarn
# or
npm install -g pnpm
```

### Recommended Versions
- Node.js: 18.x or higher
- npm: 8.x or higher

## Project Setup

### 1. Create a New Vite Project

```bash
# Using npm
npm create vite@latest my-vite-project

# Using yarn
yarn create vite my-vite-project

# Using pnpm
pnpm create vite my-vite-project
```

### 2. Project Configuration Options

When prompted, select:
- **Project name**: Enter your project name
- **Frameworks**:
  - Vanilla (Plain JavaScript/TypeScript)
  - React
  - Vue
  - Svelte
  - Preact
  - Lit
  - Qwik
  - Solid
- **Variant**: Choose JavaScript or TypeScript

### 3. Install Dependencies

```bash
cd my-vite-project
npm install
```

## Development Server

### Start Development Server

```bash
# Start dev server
npm run dev

# Start dev server with specific options
npm run dev -- --host 0.0.0.0 --port 3000 --open

# Start with debug mode
npm run dev -- --debug

# Start with profiling
npm run dev -- --profile
```

Vite will start a development server, accessible at http://localhost:5173 (or a similar port).

### Development Server Comparison: Vite vs Next.js

For comprehensive information about Next.js development server setup and migration guidance, see the [MIGRATION.md](./MIGRATION.md) file.

#### Why These Frameworks Shouldn't Work Together

**Vite + React.js** and **Next.js + React.js** represent fundamentally different architectures that cannot be mixed:

1. **Entry Points**: 
   - Vite uses `main.tsx` for client-side mounting
   - Next.js uses `page.tsx` for server-side rendering

2. **Rendering Strategies**:
   - Vite: Pure client-side rendering (CSR)
   - Next.js: Server-side rendering (SSR) + Static Site Generation (SSG)

3. **Development Servers**:
   - Vite: Fast development server on port 5173 with HMR
   - Next.js: Integrated full-stack server on port 3000 with Fast Refresh

4. **VS Code Debugging**:
   - Vite: Requires Chrome debugging configuration
   - Next.js: Uses integrated SSR debugging with different breakpoint handling

**Warning**: Attempting to use Vite as a bundler for Next.js will result in conflicts because Next.js has its own built-in bundler and development server optimized for SSR.

### Vite CLI Options

Based on the [official Vite CLI documentation](https://vite.dev/guide/cli), key development server options include:

| Option | Description |
|--------|-------------|
| `--host [host]` | Specify hostname (string) |
| `--port <port>` | Specify port (number) |
| `--open [path]` | Open browser on startup (boolean \| string) |
| `--cors` | Enable CORS (boolean) |
| `--strictPort` | Exit if specified port is already in use (boolean) |
| `--force` | Force the optimizer to ignore cache and re-bundle (boolean) |
| `-c, --config <file>` | Use specified config file (string) |
| `--base <path>` | Public base path (default: /) (string) |
| `-l, --logLevel <level>` | info \| warn \| error \| silent (string) |
| `--profile` | Start built-in Node.js inspector (boolean) |
| `-d, --debug [feat]` | Show debug logs (string \| boolean) |
| `-f, --filter <filter>` | Filter debug logs (string) |
| `-m, --mode <mode>` | Set env mode (string) |

## VS Code Configuration

### 1. Open Project in VS Code

```bash
code my-vite-project
```

### 2. Extensions

Install the following VS Code extensions:

- **TypeScript and JavaScript Language Features** (built-in)
- **ESLint** (`dbaeumer.vscode-eslint`)
- **Prettier - Code formatter** (`esbenp.prettier-vscode`)
- **Vite** (`antfu.vite`)
- **Auto Rename Tag** (`formulahendry.auto-rename-tag`)
- **Bracket Pair Colorizer** (`coenraads.bracket-pair-colorizer`)

### 3. TypeScript Configuration

For TypeScript projects, ensure your `tsconfig.json` includes:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "node",
    "strict": true,
    "jsx": "preserve",
    "sourceMap": true,
    "esModuleInterop": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"]
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

## Debugging

### 1. Browser Developer Tools

Vite automatically generates source maps in development mode, enabling debugging of original source code:

1. **Open Browser DevTools**: Press `F12` or `Ctrl+Shift+I`
2. **Navigate to Sources**: Go to the "Sources" tab
3. **Locate Files**: Find your files under the `webpack://` or `vite://` hierarchy
4. **Set Breakpoints**: Click on line numbers to set breakpoints
5. **Inspect Variables**: Use the debugger to inspect variables and call stack

### 2. VS Code Debugging Configuration

Create `.vscode/launch.json` for integrated debugging:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Launch Chrome against localhost",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:5173",
      "webRoot": "${workspaceFolder}/src",
      "sourceMaps": true,
      "trace": "verbose",
      "preLaunchTask": "npm: dev"
    },
    {
      "name": "Attach to Chrome",
      "type": "chrome",
      "request": "attach",
      "port": 9222,
      "webRoot": "${workspaceFolder}/src"
    }
  ]
}
```

### 3. Debug Tasks Configuration

Create `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "type": "npm",
      "script": "dev",
      "group": "build",
      "label": "npm: dev",
      "detail": "vite",
      "isBackground": true,
      "problemMatcher": {
        "owner": "vite",
        "pattern": {
          "regexp": "^(.*)$",
          "file": 1
        },
        "background": {
          "activeOnStart": true,
          "beginsPattern": "Local:",
          "endsPattern": "ready in"
        }
      }
    }
  ]
}
```

### 4. Debugging Tools

#### Vite Debug Logs
```bash
# Enable Vite internal debug logs
DEBUG=vite:* npm run dev

# Filter debug logs
npm run dev -- --debug --filter="hmr"
```

#### Performance Profiling
```bash
# Start with profiling enabled
npm run dev -- --profile

# This starts the built-in Node.js inspector
# Open chrome://inspect in Chrome to analyze performance
```

#### Debugging Vite Configuration
```bash
# Debug vite.config.js/ts
DEBUG=vite:config npm run dev
```

## DevOps Build Configuration

### 1. Production Build

```bash
# Build for production
npm run build

# Build with source maps
npm run build -- --sourcemap

# Build with specific target
npm run build -- --target es2015

# Build with debug information
npm run build -- --debug

# Build with profiling
npm run build -- --profile
```

### 2. Build Options

Key build options from the Vite CLI:

| Option | Description |
|--------|-------------|
| `--target <target>` | Transpile target (default: "modules") |
| `--outDir <dir>` | Output directory (default: dist) |
| `--assetsDir <dir>` | Directory under outDir to place assets |
| `--sourcemap [output]` | Output source maps ("inline" \| "hidden") |
| `--minify [minifier]` | Enable minification ("terser" \| "esbuild") |
| `--manifest [name]` | Emit build manifest json |
| `--emptyOutDir` | Force empty outDir when outside of root |
| `-w, --watch` | Rebuilds when modules change on disk |

### 3. Preview Production Build

```bash
# Preview the production build locally
npm run preview

# Preview with specific options
npm run preview -- --host 0.0.0.0 --port 4173 --open
```

### 4. CI/CD Pipeline Example

Example GitHub Actions workflow (`.github/workflows/build.yml`):

```yaml
name: Build and Test

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [18.x, 20.x]

    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v4
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run type checking
      run: npm run type-check
    
    - name: Run linting
      run: npm run lint
    
    - name: Run tests
      run: npm run test
    
    - name: Build application
      run: npm run build
    
    - name: Upload build artifacts
      uses: actions/upload-artifact@v4
      with:
        name: dist-${{ matrix.node-version }}
        path: dist/
```

### 5. Docker Configuration

Example `Dockerfile`:

```dockerfile
# Build stage
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Available Scripts

Add these scripts to your `package.json`:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "type-check": "tsc --noEmit",
    "lint": "eslint . --ext .js,.jsx,.ts,.tsx",
    "lint:fix": "eslint . --ext .js,.jsx,.ts,.tsx --fix",
    "format": "prettier --write \"src/**/*.{js,jsx,ts,tsx,json,css,md}\"",
    "clean": "rm -rf dist",
    "analyze": "npm run build && npx vite-bundle-analyzer dist"
  }
}
```

## Project Structure

```
my-vite-project/
├── .vscode/
│   ├── launch.json
│   ├── tasks.json
│   └── settings.json
├── src/
│   ├── assets/
│   ├── components/
│   ├── styles/
│   ├── main.ts (or main.js)
│   └── index.html
├── public/
├── dist/ (generated)
├── node_modules/ (generated)
├── .gitignore
├── package.json
├── tsconfig.json (for TypeScript)
├── vite.config.ts (or .js)
└── README.md
```

## Environment Variables

Create environment files:

- `.env` - Default environment variables
- `.env.local` - Local environment variables (ignored by git)
- `.env.development` - Development environment variables
- `.env.production` - Production environment variables

Example `.env`:
```
VITE_APP_TITLE=My Vite App
VITE_API_URL=http://localhost:3000/api
```

Access in code:
```javascript
const apiUrl = import.meta.env.VITE_API_URL;
```

## Hot Module Replacement (HMR)

Vite provides fast HMR out of the box. For custom HMR handling:

```javascript
if (import.meta.hot) {
  import.meta.hot.accept('./module.js', (newModule) => {
    // Handle the updated module
  });
  
  import.meta.hot.dispose((data) => {
    // Cleanup before module replacement
  });
}
```

## Troubleshooting

### Issues

1. **Port already in use**: Use `--strictPort` or change the port with `--port`
2. **Module not found**: Check import paths and ensure proper file extensions
3. **TypeScript errors**: Verify `tsconfig.json` configuration
4. **HMR not working**: Try clearing the cache with `--force`
5. **Build errors**: Check for unused imports and type errors

### Debug Commands

```bash
# Clear Vite cache
rm -rf node_modules/.vite

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Check for outdated packages
npm outdated

# Update packages
npm update
```

## Migration to Next.js

### Why Migrate from Vite to Next.js?

Next.js is a full-stack React framework that extends React's capabilities by offering features like server-side rendering (SSR), static site generation (SSG), API routes, and optimized image handling. Here are key reasons to consider migration:

#### **Performance**
- **Faster Initial Page Loading**: Eliminates the slow initial loading time common in client-side only applications (SPAs)
- **Automatic Code Splitting**: Built into the router, eliminating manual code splitting and network waterfalls
- **Server-Side Rendering**: Improves SEO and initial page load performance
- **Static Site Generation**: Pre-renders pages at build time for optimal performance

#### **Developer Experience**
- **Built-in Optimizations**: Automatic image, font, and third-party script optimization
- **File-System Based Routing**: Convention-based routing system
- **API Routes**: Full-stack capabilities with serverless functions
- **Middleware Support**: Run code on the server before request completion

#### **Features**
- **Data Fetching Strategies**: Choose between build-time, request-time, or client-side fetching
- **React Server Components**: Latest React features with server-side execution
- **Streaming with Suspense**: Intentional loading states without network waterfalls

### Migration Steps

Based on the [official Next.js migration guide](https://nextjs.org/docs/app/guides/migrating/from-vite), follow these steps:

#### **Step 1: Install Next.js Dependency**

```bash
npm install next@latest
```

#### **Step 2: Create Next.js Configuration**

Create `next.config.mjs` at your project root:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export', // Outputs a Single-Page Application (SPA)
  distDir: './dist', // Changes the build output directory to ./dist/
  trailingSlash: true,
  images: {
    unoptimized: true // Required for static export
  }
}

export default nextConfig
```

#### **Step 3: Update TypeScript Configuration**

If using TypeScript, update your `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "esModuleInterop": true,
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",
    "strict": true,
    "allowJs": true,
    "forceConsistentCasingInFileNames": true,
    "incremental": true,
    "plugins": [{ "name": "next" }]
  },
  "include": ["./src", "./dist/types/**/*.ts", "./next-env.d.ts"],
  "exclude": ["./node_modules"]
}
```

#### **Step 4: Create Root Layout**

Create `app/layout.tsx`:

```tsx
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'My App',
  description: 'My App migrated from Vite',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <div id="root">{children}</div>
      </body>
    </html>
  )
}
```

#### **Step 5: Create Entry Point**

Create `app/[[...slug]]/page.tsx` for catch-all routing:

```tsx
import '../../index.css'
import { ClientOnly } from './client'

export function generateStaticParams() {
  return [{ slug: [''] }]
}

export default function Page() {
  return <ClientOnly />
}
```

Create `app/[[...slug]]/client.tsx`:

```tsx
'use client'
import React from 'react'
import dynamic from 'next/dynamic'

const App = dynamic(() => import('../../App'), { ssr: false })

export function ClientOnly() {
  return <App />
}
```

#### **Step 6: Update Environment Variables**

Change environment variable prefixes:
- `VITE_` → `NEXT_PUBLIC_`
- `import.meta.env.MODE` → `process.env.NODE_ENV`
- `import.meta.env.PROD` → `process.env.NODE_ENV === 'production'`
- `import.meta.env.DEV` → `process.env.NODE_ENV !== 'production'`

#### **Step 7: Update Package.json Scripts**

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "export": "next build && next export"
  }
}
```

#### **Step 8: Update .gitignore**

Add Next.js specific entries:

```gitignore
# Next.js
.next/
next-env.d.ts
out/
```

### Next.js Debugging Setup

#### **1. VS Code Debug Configuration**

Create `.vscode/launch.json` for Next.js debugging:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Next.js: debug server-side",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/node_modules/.bin/next",
      "args": ["dev"],
      "console": "integratedTerminal",
      "skipFiles": ["<node_internals>/**"],
      "env": {
        "NODE_OPTIONS": "--inspect"
      }
    },
    {
      "name": "Next.js: debug client-side",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:3000",
      "webRoot": "${workspaceFolder}",
      "sourceMaps": true
    },
    {
      "name": "Next.js: debug full stack",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/node_modules/.bin/next",
      "args": ["dev"],
      "console": "integratedTerminal",
      "serverReadyAction": {
        "pattern": "ready - started server on .+, url: (https?://.+)",
        "uriFormat": "%s",
        "action": "debugWithChrome"
      }
    }
  ]
}
```

### Next.js (Optional)

We've created a full Next.js application in the `nextjs-app/` directory that demonstrates:

- **Server-Side Rendering (SSR)** with React components
- **TypeScript** configuration for type safety
- **API Routes** for backend functionality
- **Tailwind CSS** for modern styling
- **Docker** setup for development and production
- **IoT Device Dashboard** as a practical example

#### Quick Start with the Next.js Application

```bash
# Navigate to the Next.js application
cd nextjs-app

# Install all dependencies
npm install

# Start development server
npm run dev

# Or use Docker for isolated development
docker-compose up --build

# Application will be available at:
# http://localhost:3000 (Next.js app)
# http://localhost:80 (nginx proxy via Docker)
```

#### Application Features

| Feature | Description | File Location |
|---------|-------------|---------------|
| **Homepage with SSR** | Server-rendered IoT dashboard | `src/app/page.tsx` |
| **API Routes** | RESTful endpoints for devices | `src/app/api/devices/` |
| **React Components** | Reusable UI components | `src/components/` |
| **TypeScript Types** | Type-safe development | `src/lib/types.ts` |
| **Responsive Design** | Mobile-first with Tailwind | `src/app/globals.css` |
| **Docker Setup** | Dev and production containers | `docker-compose.yml` |

#### DevOps

The Next.js application includes comprehensive deployment configurations:

- **Multi-stage Docker builds** for optimized production images
- **Docker Compose** setup with nginx, Redis, and PostgreSQL
- **Health checks** and monitoring endpoints
- **Environment variable** management
- **Complete deployment guide** in `DEPLOYMENT.md`

#### For Production Deployment

See the detailed setup instructions in `nextjs-app/DEPLOYMENT.md` covering:

- **Linux/Debian system setup** and prerequisites
- **Docker deployment** strategies (development and production)
- **VS Code debugging** configuration for Next.js
- **DevOps best practices** including nginx, PM2, and systemd
- **Monitoring and logging** setup
- **CI/CD pipeline** examples
- **Troubleshooting guide** for common issues

## � Project Structure Overview

This repository contains **two separate and complete projects** demonstrating different React-based architectures:

```
📁 Vite/
├── 📁 vite-react-app/           # Vite + React + Express.js
│   ├── 📁 src/                  # React frontend (port 5173)
│   ├── 📁 server/               # Express.js API (port 3001)  
│   ├── vite.config.ts           # Vite configuration
│   ├── package.json             # Frontend dependencies
│   └── README.md                # Vite project documentation
│
├── 📁 nextjs-app/               # Next.js + React + Integrated API
│   ├── 📁 src/app/              # Next.js App Router + API routes
│   ├── 📁 src/components/       # React components  
│   ├── next.config.js           # Next.js configuration
│   ├── package.json             # Full-stack dependencies
│   ├── DEPLOYMENT.md            # Next.js deployment guide
│   └── docker-compose.yml       # Docker configuration
│
├── 📄 COMPARISON.md             # Detailed comparison guide
├── 📄 README.md                 # This file
└── 📁 .vscode/                  # VS Code debugging for both projects
    └── launch.json              # Debug configurations
```

## Quick Start

### Option 1: Vite + React + Express.js (Client-Side Rendering)

```bash
cd vite-react-app
npm install
npm run dev:full     # Starts both Vite (5173) and Express (3001)
```

**Access Points:**
- Frontend: http://localhost:5173
- API: http://localhost:3001

### Option 2: Next.js + React + Integrated API (Server-Side Rendering)

```bash
cd nextjs-app
npm install
npm run dev          # Starts Next.js server (3000)
```

**Access Points:**
- Application: http://localhost:3000
- API: http://localhost:3000/api

## Differences

| Feature | Vite + React | Next.js + React |
|---------|--------------|------------------|
| **Rendering** | Client-side only | Server-side + Client-side |
| **Development** | ⚡ Instant startup | 🔄 Fast startup |
| **Architecture** | Separated frontend/backend | Integrated full-stack |
| **SEO** | ❌ Limited | ✅ Excellent |
| **Debugging** | Chrome + Node.js separately | Next.js integrated debugger |
| **Deployment** | Static + API server | Full-stack application |
| **Best For** | SPAs, Admin dashboards | Public websites, E-commerce |

**For comparison, see [COMPARISON.md](COMPARISON.md)**

## 🚫 Why Vite and Next.js Should NOT Work Together

### Fundamental Architecture Differences

**Vite** and **Next.js** are fundamentally different tools that solve different problems and should **not** be combined in the same project. Here's why they are incompatible:

#### **1. Build System Conflicts**
- **Vite**: Uses esbuild and Rollup for bundling, optimized for fast development
- **Next.js**: Uses its own build system with Webpack, Turbopack, and SWC
- **Conflict**: They have different module resolution, hot module replacement, and bundling strategies

#### **2. Development Server Architecture**
- **Vite**: Pure client-side development server with proxy to separate API
- **Next.js**: Integrated full-stack server with SSR, API routes, and middleware
- **Conflict**: Cannot run both development servers simultaneously on same project

#### **3. Debugging and Tooling Differences**

| Aspect | Vite + React | Next.js + React |
|--------|--------------|------------------|
| **Dev Server** | `vite dev` (port 5173) | `next dev` (port 3000) |
| **Build Command** | `vite build` | `next build` |
| **VS Code Debugging** | Chrome debugger + Node.js for API | Next.js specific debugger |
| **Hot Reload** | Vite HMR | Next.js Fast Refresh |
| **Source Maps** | Vite source maps | Next.js source maps |
| **Environment Variables** | `VITE_*` prefix | `NEXT_PUBLIC_*` prefix |

#### **4. Project Structure Incompatibility**
```
Vite Project:           Next.js Project:
├── src/                ├── src/app/          # App Router
├── public/             ├── pages/            # Pages Router  
├── index.html          ├── public/
├── vite.config.ts      ├── next.config.js
└── server/ (separate)  └── (integrated API)
```

### Separate Projects Solution

We've created **two distinct projects** to demonstrate the proper approach:

#### **Project 1: Vite + React + Node.js** (`vite-react-app/`)
- **Architecture**: Client-side rendering with separate Express.js API server
- **Debugging**: Chrome DevTools for React, Node.js debugger for API
- **Development**: Two servers running simultaneously (Vite + Express)
- **Best For**: SPAs, static sites, fast prototyping, separate frontend/backend teams

```bash
cd vite-react-app
npm install
npm run dev:full  # Starts both Vite (5173) and Express (3001)
```

#### **Project 2: Next.js + React + Node.js** (`nextjs-app/`)
- **Architecture**: Server-side rendering with integrated API routes
- **Debugging**: Next.js specific debugging with SSR support
- **Development**: Single integrated server
- **Best For**: SEO-critical apps, full-stack applications, complex routing

```bash
cd nextjs-app
npm install
npm run dev  # Starts Next.js server (3000)
```

### 🔧 VS Code Debugging Differences

#### **Vite Project Debugging**
```json
{
  "name": "Vite: Debug Client",
  "type": "chrome",
  "request": "launch",
  "url": "http://localhost:5173",
  "webRoot": "${workspaceFolder}/vite-react-app/src"
}
```

#### **Next.js Project Debugging**
```json
{
  "name": "Next.js: Debug Server-Side",
  "type": "node",
  "request": "launch",
  "program": "node_modules/.bin/next",
  "args": ["dev"]
}
```

### When to Choose Each

| Use Case | Choose Vite + React | Choose Next.js + React |
|----------|-------------------|----------------------|
| **SPA/Static Site** | ✅ Perfect fit | ❌ Overkill |
| **SEO Critical** | ❌ Limited SEO | ✅ Excellent SEO |
| **Fast Development** | ✅ Instant HMR | ⚠️ Good, but slower |
| **API Integration** | ✅ Flexible backends | ✅ Built-in API routes |
| **Team Structure** | ✅ Separate FE/BE teams | ⚠️ Full-stack teams |
| **Deployment** | ✅ CDN/Static hosting | ✅ Serverless/Server |
| **Complex Routing** | ⚠️ Manual setup | ✅ File-based routing |
| **Real-time Features** | ✅ WebSockets/separate | ⚠️ More complex setup |

### Migration Strategy

If you need to migrate from Vite to Next.js (not combine them):

1. **Create new Next.js project** (don't modify existing Vite project)
2. **Port React components** to Next.js file structure
3. **Convert API calls** to Next.js API routes or keep external API
4. **Update environment variables** (`VITE_*` → `NEXT_PUBLIC_*`)
5. **Reconfigure debugging** for Next.js toolchain
6. **Test thoroughly** as rendering behavior changes significantly

### ⚠️ Common Mistakes to Avoid

❌ **Don't do this:**
- Installing Vite in a Next.js project
- Using `vite.config.js` with Next.js
- Mixing Vite and Next.js build commands
- Using Vite HMR with Next.js components

✅ **Do this instead:**
- Choose one architecture based on your needs
- Use appropriate debugging tools for each
- Follow framework-specific best practices
- Keep projects completely separate

## 🔄 Migration from Vite to Next.js
        "action": "debugWithChrome"
      }
    }
  ]
}
```

#### **2. Next.js Development Tools**

Enable debugging features in `next.config.mjs`:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable source maps in development
  productionBrowserSourceMaps: process.env.NODE_ENV === 'development',
  
  // Enable React DevTools
  reactStrictMode: true,
  
  // Enable detailed error messages
  devIndicators: {
    buildActivity: true,
    buildActivityPosition: 'bottom-right',
  },
  
  // Enable browser debug info in terminal
  browserDebugInfoInTerminal: true,
  
  // Enable logging
  logging: {
    fetches: {
      fullUrl: true,
    }
  }
}

export default nextConfig
```

#### **3. Server-Side Debugging**

Debug server-side code and API routes:

```bash
# Start Next.js with Node.js debugger
NODE_OPTIONS='--inspect' npm run dev

# Debug with specific port
NODE_OPTIONS='--inspect=0.0.0.0:9229' npm run dev
```

#### **4. Client-Side Debugging**

For client-side debugging:

```tsx
// Use browser debugging in development
if (process.env.NODE_ENV === 'development') {
  console.log('Debug info:', data);
  debugger; // Browser will pause here
}

// React DevTools integration
import { useEffect } from 'react'

function MyComponent() {
  useEffect(() => {
    // This will show in React DevTools
    console.log('Component mounted');
  }, []);
  
  return <div>My Component</div>
}
```

#### **5. Performance Debugging**

Enable performance debugging:

```bash
# Build with bundle analyzer
npm install --save-dev @next/bundle-analyzer

# Enable in next.config.mjs
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
})

module.exports = withBundleAnalyzer(nextConfig)

# Run analysis
ANALYZE=true npm run build
```

#### **6. Network and API Debugging**

Debug API routes and data fetching:

```tsx
// pages/api/debug.ts
export default function handler(req, res) {
  console.log('API Request:', {
    method: req.method,
    headers: req.headers,
    body: req.body
  });
  
  res.status(200).json({ debug: 'API working' });
}

// Client-side fetch debugging
const fetchWithDebug = async (url: string, options?: RequestInit) => {
  console.log('Fetching:', url, options);
  const response = await fetch(url, options);
  console.log('Response:', response.status, response.headers);
  return response;
};
```

### Comparison: Vite vs Next.js

| Feature | Vite | Next.js |
|---------|------|---------|
| **Build Speed** | ⚡ Extremely Fast | 🚀 Fast |
| **Bundle Size** | 📦 Small | 📦 Optimized |
| **SEO** | ❌ Client-side only | ✅ Server-side rendering |
| **Routing** | 🔧 Manual setup | ✅ File-system based |
| **API Routes** | ❌ Not built-in | ✅ Built-in |
| **Image Optimization** | 🔧 Manual | ✅ Automatic |
| **TypeScript** | ✅ Excellent | ✅ Excellent |
| **Hot Reload** | ⚡ Lightning fast | 🚀 Fast |
| **Deployment** | 🔧 Manual setup | ✅ Optimized |
| **Learning Curve** | 📚 Simple | 📚 Moderate |

Choose **Vite** for:
- Simple SPAs or prototypes
- Library development
- Maximum build speed
- Minimal configuration

Choose **Next.js** for:
- Production web applications
- SEO-critical applications
- Full-stack development
- E-commerce or content sites

## References

- [Official Vite Documentation](https://vite.dev/)
- [Vite CLI Guide](https://vite.dev/guide/cli)
- [Vite Configuration Reference](https://vite.dev/config/)
- [VS Code Debugging Guide](https://code.visualstudio.com/docs/editor/debugging)
- [Node.js Debugging Guide](https://nodejs.org/en/docs/guides/debugging-started/)
- [Chrome DevTools Documentation](https://developer.chrome.com/docs/devtools/)
- [TypeScript Configuration](https://www.typescriptlang.org/tsconfig)
- [How to migrate from Vite to Next.js](https://nextjs.org/docs/app/guides/migrating/from-vite)
- [Next.js Documentation](https://nextjs.org/docs)
- [Next.js Debugging Guide](https://nextjs.org/docs/app/guides/debugging)
- [Next.js App Router](https://nextjs.org/docs/app)
- [React Server Components](https://nextjs.org/docs/app/getting-started/server-and-client-components)
- [How to migrate from Vite to Next.js](https://nextjs.org/docs/app/guides/migrating/from-vite)

```

---
