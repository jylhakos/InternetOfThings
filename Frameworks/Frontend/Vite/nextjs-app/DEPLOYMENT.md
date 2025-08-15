# Development Guide: Next.js with Vite and React

This project demonstrates how to set up and deploy a Next.js application with TypeScript and React components for IoT device management.

## 🚀 Quick Start

### Option 1: Docker Development (Recommended)

```bash
# Clone or navigate to the project
cd nextjs-app

# Start development environment
docker-compose up --build

# Access the application
# - Next.js app: http://localhost:3000
# - nginx proxy: http://localhost:80
```

### Option 2: Local Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Access the application
# http://localhost:3000
```

## 📋 Prerequisites

### System Requirements
- **Node.js**: Version 18.x or higher
- **npm**: Version 8.x or higher (or yarn/pnpm)
- **Docker**: Version 20.x or higher (optional)
- **Docker Compose**: Version 2.x or higher (optional)

### Linux/Debian Setup
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Docker (optional)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## 🛠️ Development Setup

### 1. Project Structure
```
nextjs-app/
├── src/
│   ├── app/
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Homepage
│   │   ├── globals.css         # Global styles
│   │   └── api/
│   │       └── devices/        # API routes
│   └── components/
│       ├── DeviceCard.tsx      # Device component
│       └── ServerStatus.tsx    # Status component
├── docker-compose.yml          # Multi-service setup
├── Dockerfile                  # Production build
├── Dockerfile.dev              # Development build
├── next.config.js             # Next.js configuration
├── tailwind.config.js         # Tailwind CSS
└── package.json               # Dependencies
```

### 2. Environment Configuration

Create `.env.local` file:
```bash
# Application
NEXT_PUBLIC_APP_URL=http://localhost:3000
NODE_ENV=development

# Database (optional)
DATABASE_URL=postgresql://user:password@localhost:5432/iot_db

# Redis (optional)
REDIS_URL=redis://localhost:6379
```

### 3. VS Code Development Setup

Install recommended extensions:
```bash
# Install VS Code extensions
code --install-extension bradlc.vscode-tailwindcss
code --install-extension esbenp.prettier-vscode
code --install-extension ms-vscode.vscode-typescript-next
code --install-extension formulahendry.auto-rename-tag
```

VS Code debug configuration (`.vscode/launch.json`):
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
    }
  ]
}
```

## 🐳 Docker Deployment

### Development Environment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f nextjs-app

# Rebuild after changes
docker-compose up --build

# Stop services
docker-compose down
```

### Production Deployment

```bash
# Build production image
docker build -t nextjs-iot-app .

# Run production container
docker run -d \
  --name nextjs-app \
  -p 3000:3000 \
  -e NODE_ENV=production \
  nextjs-iot-app

# With environment file
docker run -d \
  --name nextjs-app \
  -p 3000:3000 \
  --env-file .env.production \
  nextjs-iot-app
```

### Multi-Service Production Setup

```bash
# Production docker-compose
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale the application
docker-compose up --scale nextjs-app=3 -d
```

## 🔧 DevOps Configuration

### 1. Linux Systemd Service

Create service file `/etc/systemd/system/nextjs-app.service`:
```ini
[Unit]
Description=Next.js IoT Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/nextjs-app
ExecStart=/usr/bin/node server.js
Restart=on-failure
RestartSec=10
Environment=NODE_ENV=production
Environment=PORT=3000

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable nextjs-app
sudo systemctl start nextjs-app
sudo systemctl status nextjs-app
```

### 2. Nginx Reverse Proxy

Create `/etc/nginx/sites-available/nextjs-app`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
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
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/nextjs-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. Process Management with PM2

```bash
# Install PM2
npm install -g pm2

# Create ecosystem file
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'nextjs-app',
    script: 'server.js',
    instances: 'max',
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    }
  }]
}
EOF

# Start application
pm2 start ecosystem.config.js
pm2 startup
pm2 save
```

## 📊 Monitoring and Logging

### 1. Application Monitoring

```bash
# Docker stats
docker stats

# Container logs
docker logs -f nextjs-app

# System resources
htop
iotop
```

### 2. Health Checks

Create health check endpoint in `src/app/api/health/route.ts`:
```typescript
export async function GET() {
  return Response.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  })
}
```

### 3. Log Configuration

Add to `next.config.js`:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  logging: {
    fetches: {
      fullUrl: true,
    },
  },
  experimental: {
    logging: {
      level: 'verbose',
    },
  },
}
```

## 🚀 Deployment Strategies

### 1. Blue-Green Deployment

```bash
#!/bin/bash
# blue-green-deploy.sh

# Build new version
docker build -t nextjs-app:green .

# Stop old version
docker stop nextjs-app-blue

# Start new version
docker run -d \
  --name nextjs-app-green \
  -p 3000:3000 \
  nextjs-app:green

# Health check
if curl -f http://localhost:3000/api/health; then
  echo "Green deployment successful"
  docker rm nextjs-app-blue
  docker tag nextjs-app:green nextjs-app:blue
else
  echo "Green deployment failed, rolling back"
  docker stop nextjs-app-green
  docker start nextjs-app-blue
fi
```

### 2. Rolling Updates with Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.prod.yml nextjs-stack

# Update service
docker service update --image nextjs-app:latest nextjs-stack_nextjs-app
```

### 3. Kubernetes Deployment

Create `k8s-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nextjs-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nextjs-app
  template:
    metadata:
      labels:
        app: nextjs-app
    spec:
      containers:
      - name: nextjs-app
        image: nextjs-app:latest
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: "production"
---
apiVersion: v1
kind: Service
metadata:
  name: nextjs-service
spec:
  selector:
    app: nextjs-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 3000
  type: LoadBalancer
```

## 🔍 Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   sudo lsof -i :3000
   sudo kill -9 <PID>
   ```

2. **Permission errors**:
   ```bash
   sudo chown -R $USER:$USER .
   chmod +x scripts/*.sh
   ```

3. **Memory issues**:
   ```bash
   # Increase Node.js memory limit
   export NODE_OPTIONS="--max-old-space-size=4096"
   ```

4. **Docker build failures**:
   ```bash
   # Clean Docker cache
   docker system prune -a
   
   # Rebuild without cache
   docker build --no-cache -t nextjs-app .
   ```

### Performance Optimization

1. **Enable compression**:
   ```javascript
   // next.config.js
   const nextConfig = {
     compress: true,
     poweredByHeader: false,
   }
   ```

2. **Optimize images**:
   ```bash
   npm install sharp
   ```

3. **Bundle analysis**:
   ```bash
   npm install @next/bundle-analyzer
   ANALYZE=true npm run build
   ```

## 📚 Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)
- [Docker Documentation](https://docs.docker.com)
- [Tailwind CSS](https://tailwindcss.com/docs)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `npm test`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
