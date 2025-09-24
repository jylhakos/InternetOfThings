# Development Guide

## Quick Start

1. **Initial Setup** (one-time):
   ```bash
   chmod +x setup.sh start.sh stop.sh
   ./setup.sh
   ```

2. **Configure Environment**:
   ```bash
   # Edit backend/.env with your settings
   nano backend/.env
   ```

3. **Start Application**:
   ```bash
   ./start.sh
   ```

4. **Access Application**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

5. **Stop Application**:
   ```bash
   ./stop.sh
   ```

## Development Workflow

### Backend Development
```bash
# Activate virtual environment
source venv/bin/activate

# Install new packages
pip install package_name
pip freeze > backend/requirements.txt

# Run backend only
cd backend
python main.py

# Run tests
python -m pytest

# Format code
black . && flake8 .
```

### Frontend Development
```bash
# Install new packages
cd frontend
npm install package_name

# Run frontend only
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Lint code
npm run lint
```

### Database Operations
```bash
# Connect to PostgreSQL
psql -h localhost -U username -d weatherdb

# Create database (if not exists)
sudo -u postgres createdb weatherdb

# Drop and recreate (development only)
sudo -u postgres dropdb weatherdb
sudo -u postgres createdb weatherdb
```

## API Testing

### Authentication
```bash
# Register user
curl -X POST "http://localhost:8000/api/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890"
  }'

# Login
curl -X POST "http://localhost:8000/api/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword"
  }'

# Get user info (with token)
curl -X GET "http://localhost:8000/api/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Weather Data
```bash
# Get weather data
curl -X GET "http://localhost:8000/api/weather"

# Health check
curl -X GET "http://localhost:8000/health"
```

## Docker Development

### Build and run with Docker
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Remove volumes (reset data)
docker-compose down -v
```

### Individual service commands
```bash
# Backend only
docker-compose up -d db redis
docker-compose run --rm backend

# Frontend only (after backend is running)
docker-compose up frontend
```

## Debugging

### Backend Issues
```bash
# Check backend logs
tail -f logs/backend.log

# Check if backend is running
curl http://localhost:8000/health

# Check database connection
python -c "
from backend.database import engine
import asyncio
async def test():
    async with engine.begin() as conn:
        result = await conn.execute('SELECT 1')
        print('DB OK:', result.scalar())
asyncio.run(test())
"
```

### Frontend Issues
```bash
# Check frontend logs
tail -f logs/frontend.log

# Check if frontend is accessible
curl http://localhost:5173

# Clear cache and reinstall
rm -rf frontend/node_modules
rm frontend/package-lock.json
cd frontend && npm install
```

### Socket.IO Issues
```bash
# Test Socket.IO connection
node -e "
const io = require('socket.io-client');
const socket = io('http://localhost:8000');
socket.on('connect', () => console.log('Connected'));
socket.on('weather_update', (data) => console.log('Weather:', data));
setTimeout(() => socket.disconnect(), 5000);
"
```

## Common Issues

### Port Already in Use
```bash
# Find and kill process on port 8000
lsof -ti :8000 | xargs kill -9

# Find and kill process on port 5173
lsof -ti :5173 | xargs kill -9
```

### Database Connection Error
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql

# Create database and user
sudo -u postgres psql -c "CREATE DATABASE weatherdb;"
sudo -u postgres psql -c "CREATE USER username WITH PASSWORD 'password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE weatherdb TO username;"
```

### Python Import Errors
```bash
# Reinstall requirements
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
```

### Node.js Issues
```bash
# Clear npm cache
npm cache clean --force

# Update Node.js (using nvm)
nvm install --lts
nvm use --lts
```

## Performance Monitoring

### System Resources
```bash
# Monitor CPU and memory
htop

# Monitor disk usage
df -h

# Monitor network connections
netstat -tulpn | grep :8000
```

### Application Metrics
```bash
# Backend performance
curl http://localhost:8000/health

# Database connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"
```

## Security Checklist

- [ ] Change JWT_SECRET_KEY in production
- [ ] Use strong database passwords
- [ ] Enable HTTPS in production
- [ ] Configure proper CORS origins
- [ ] Use environment variables for secrets
- [ ] Enable database SSL in production
- [ ] Set up proper firewall rules
- [ ] Use non-root users in Docker

## Production Deployment

1. **Environment Setup**:
   ```bash
   cp .env.production.example .env
   # Edit .env with production values
   ```

2. **SSL/HTTPS Setup**:
   ```bash
   # Use Let's Encrypt or your SSL certificates
   # Update nginx.conf for HTTPS
   ```

3. **Deploy with Docker**:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

4. **Monitor Services**:
   ```bash
   docker-compose logs -f
   ```