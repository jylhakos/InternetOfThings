# Vite + React + Node.js Project

This project demonstrates a **client-side rendered (CSR)** IoT device management application using Vite as the build tool, React for the UI, and a separate Node.js Express server for the API.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT-SIDE ARCHITECTURE                 │
├─────────────────────────────────────────────────────────────┤
│  Browser (http://localhost:5173)                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              React SPA                              │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │ DeviceCard  │  │    Stats    │  │   Router    │  │   │
│  │  │ Component   │  │  Component  │  │   (React    │  │   │
│  │  │             │  │             │  │   Router)   │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │ HTTP Requests (Axios)            │
│                          ▼                                  │
│  API Server (http://localhost:3001)                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Express.js Server                      │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │ GET /api/   │  │ POST /api/  │  │ PUT /api/   │  │   │
│  │  │ devices     │  │ devices     │  │ devices/:id │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## ✨ Key Features

- **⚡ Fast Development**: Vite's instant hot module replacement (HMR)
- **🔄 Separate Concerns**: Frontend and backend are completely decoupled
- **🎨 Modern UI**: React with TypeScript and Tailwind CSS
- **📱 Responsive Design**: Mobile-first approach
- **🔌 RESTful API**: Express.js server with full CRUD operations
- **🐛 VS Code Debugging**: Separate debugging for client and server

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation and Setup

```bash
# Install frontend dependencies
npm install

# Install backend dependencies (Express server)
cd server && npm install express cors helmet morgan dotenv uuid

# Start development servers (both frontend and backend)
npm run dev:full

# Or start them separately:
# Terminal 1: Frontend (Vite)
npm run dev

# Terminal 2: Backend (Express)
npm run server
```

### Access Points
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:3001
- **API Health Check**: http://localhost:3001/api/health

## 🔧 VS Code Debugging Setup

### 1. Frontend Debugging (React)
Use Chrome DevTools integration:

```json
{
  "name": "Vite: Debug Client",
  "type": "chrome",
  "request": "launch",
  "url": "http://localhost:5173",
  "webRoot": "${workspaceFolder}/src",
  "sourceMaps": true
}
```

### 2. Backend Debugging (Node.js)
Debug the Express server:

```json
{
  "name": "Vite: Debug Server (Node.js)",
  "type": "node",
  "request": "launch",
  "program": "${workspaceFolder}/server/index.js",
  "env": {
    "NODE_ENV": "development",
    "PORT": "3001"
  }
}
```

### 3. Full-Stack Debugging
Debug both simultaneously:

```json
{
  "name": "Vite: Debug Full Stack",
  "type": "node",
  "request": "launch",
  "program": "${workspaceFolder}/server/index.js",
  "serverReadyAction": {
    "action": "debugWithChrome"
  }
}
```

## 📁 Project Structure

```
vite-react-app/
├── src/
│   ├── components/
│   │   └── DeviceCard.tsx          # Reusable device component
│   ├── services/
│   │   └── api.ts                  # Axios-based API client
│   ├── types/
│   │   └── index.ts                # TypeScript interfaces
│   ├── App.tsx                     # Main React application
│   ├── main.tsx                    # React app entry point
│   ├── index.css                   # Global styles
│   └── App.css                     # Component styles
├── server/
│   └── index.js                    # Express.js API server
├── public/                         # Static assets
├── index.html                      # HTML template
├── vite.config.ts                  # Vite configuration
├── tsconfig.json                   # TypeScript configuration
└── package.json                    # Dependencies and scripts
```

## 🛠️ Development Workflow

### 1. Adding New Features
```bash
# Start development servers
npm run dev:full

# Make changes to React components in src/
# Make changes to API endpoints in server/index.js
# Both will auto-reload thanks to Vite HMR and nodemon
```

### 2. API Development
The Express server provides RESTful endpoints:

- `GET /api/devices` - Get all devices with stats
- `GET /api/devices/:id` - Get single device
- `POST /api/devices` - Create new device
- `PUT /api/devices/:id` - Update device
- `DELETE /api/devices/:id` - Delete device
- `GET /api/health` - Server health check

### 3. Frontend Development
React components use the API service:

```typescript
import { deviceService } from '@services/api';

// Fetch devices
const response = await deviceService.getAllDevices();
setDevices(response.devices);
```

## 🎨 Styling and UI

- **Tailwind CSS**: Utility-first CSS framework
- **Responsive Design**: Mobile-first approach
- **Component-based**: Modular React components
- **TypeScript**: Full type safety

## 🐛 Debugging Features

### Frontend Debugging
- **React DevTools**: Browser extension for React debugging
- **Vite DevTools**: Built-in Vite debugging features
- **Source Maps**: Full source map support for TypeScript
- **Hot Reload**: Instant updates without page refresh

### Backend Debugging
- **Node.js Inspector**: VS Code integrated debugging
- **Console Logging**: Structured logging with Morgan
- **Error Handling**: Comprehensive error middleware
- **Auto Restart**: Nodemon for automatic server restarts

## 🚀 Production Build

```bash
# Build frontend for production
npm run build

# Preview production build
npm run preview

# Production server (separate process)
NODE_ENV=production node server/index.js
```

## 📦 Deployment Options

### Frontend Deployment
- **Static Hosting**: Netlify, Vercel, GitHub Pages
- **CDN**: CloudFront, CloudFlare
- **Container**: Docker with nginx

### Backend Deployment
- **Node.js Hosting**: Railway, Render, DigitalOcean
- **Containerization**: Docker + Kubernetes
- **Serverless**: AWS Lambda (with adaptation)

## ⚡ Performance Features

- **Fast Cold Starts**: Vite's esbuild preprocessing
- **Tree Shaking**: Dead code elimination
- **Code Splitting**: Automatic route-based splitting
- **Asset Optimization**: Image and font optimization
- **Caching**: HTTP caching headers

## 🔍 Why Choose Vite + React?

### ✅ Advantages
- **Extremely fast development** with instant HMR
- **Flexible backend** - can use any API server
- **Simple deployment** - frontend and backend separate
- **Team scalability** - frontend/backend teams can work independently
- **Technology flexibility** - easy to swap out backend technologies

### ⚠️ Considerations
- **SEO limitations** - client-side rendering only
- **Initial load time** - JavaScript must load before app renders
- **API coordination** - need to manage API contracts between teams
- **Separate deployment** - two deployment processes to manage

## 📚 Learning Resources

- [Vite Documentation](https://vitejs.dev/)
- [React Documentation](https://react.dev/)
- [Express.js Guide](https://expressjs.com/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)

---

This Vite + React project demonstrates the **client-side rendering approach** with a separate API server, perfect for teams that want maximum flexibility and the fastest possible development experience.
