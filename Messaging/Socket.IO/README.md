# Data Streaming

A full-stack real-time data streaming application built with **FastAPI**, **React**, **Socket.IO**, and **PostgreSQL**. The application provides real-time weather data for Schiphol Airport with user authentication and live updates.

##  Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   React SPA     │◄──►│  FastAPI +      │◄──►│   PostgreSQL    │
│   (Frontend)    │    │  Socket.IO      │    │   Database      │
│                 │    │  (Backend)      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       
         │                       │                       
         ▼                       ▼                       
┌─────────────────┐    ┌─────────────────┐              
│                 │    │                 │              
│   Socket.IO     │    │  Weather APIs   │              
│   Real-time     │    │  (OpenWeather,  │              
│   Communication │    │   Open-Meteo)   │              
└─────────────────┘    └─────────────────┘              
```

## Features

- **User Authentication**: JWT-based authentication with secure password hashing
- **Real-time Weather Updates**: Live weather data streaming via Socket.IO
- **User Dashboard**: Personalized dashboard showing user info and weather data
- **Responsive Design**: Mobile-friendly interface
- **Weather Data**: Real-time weather information for Schiphol Airport (EHAM)
- **Auto-refresh**: Hourly automatic weather updates
- **Manual Refresh**: On-demand weather data refresh button

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Python web framework
- **Socket.IO**: Real-time bidirectional communication
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Relational database
- **JWT**: JSON Web Tokens for authentication
- **bcrypt**: Password hashing
- **httpx**: Async HTTP client for API calls

### Frontend
- **React 19**: React with TypeScript
- **Vite**: Fast build tool and dev server
- **Socket.IO Client**: Real-time communication
- **Axios**: HTTP client for API calls
- **React Router**: Client-side routing
- **CSS3**: Styling with animations

## 📁 Project Structure

```
├── backend/
│   ├── main.py              # FastAPI application with Socket.IO
│   ├── auth.py              # Authentication utilities
│   ├── database.py          # Database models and connections
│   ├── weather_service.py   # Weather API integration
│   ├── models.py            # Pydantic models
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Environment variables
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Login.tsx           # Login/Register component
│   │   │   ├── Dashboard.tsx       # Main dashboard
│   │   │   ├── Auth.css           # Authentication styles
│   │   │   └── Dashboard.css      # Dashboard styles
│   │   ├── services/
│   │   │   ├── api.ts             # HTTP API calls
│   │   │   └── socket.ts          # Socket.IO service
│   │   ├── AuthContext.tsx        # Authentication context
│   │   ├── types.ts              # TypeScript interfaces
│   │   ├── App.tsx               # Main App component
│   │   └── main.tsx              # React entry point
│   ├── package.json         # Node.js dependencies
│   └── vite.config.ts       # Vite configuration
├── venv/                    # Python virtual environment
├── .gitignore              # Git ignore rules
├── README.md               # Project documentation
└── docker-compose.yml      # Docker composition (production)
```

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL 12+
- Git

### Backend Setup

1. **Navigate to the project directory:**
   ```bash
   cd /path/to/project
   ```

2. **Activate the Python virtual environment:**
   ```bash
   source venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configurations
   ```

5. **Configure PostgreSQL:**
   ```bash
   # Create database
   createdb weatherdb
   
   # Update DATABASE_URL in .env:
   DATABASE_URL=postgresql+asyncpg://username:password@localhost/weatherdb
   ```

6. **Start the backend server:**
   ```bash
   python main.py
   ```

   The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:5173`

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Database Configuration
DATABASE_URL=postgresql+asyncpg://username:password@localhost/weatherdb

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production-please
ALGORITHM=HS256

# Weather API Configuration
OPENWEATHER_API_KEY=your-openweather-api-key-here

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS Origins
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# PostgreSQL Database Configuration
POSTGRES_USER=username
POSTGRES_PASSWORD=password
POSTGRES_DB=weatherdb
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### Weather API

1. **OpenWeatherMap API** (Recommended):
   - Sign up at [openweathermap.org](https://openweathermap.org/api)
   - Get your free API key
   - Add to `.env` file as `OPENWEATHER_API_KEY`

2. **Open-Meteo API** (Free, no key required):
   - Used as fallback when OpenWeatherMap is unavailable
   - Automatic integration in the backend

## 🌐 API Endpoints

### Authentication
- `POST /api/register` - User registration
- `POST /api/login` - User login
- `GET /api/me` - Get current user info

### Weather
- `GET /api/weather` - Get current weather data
- `GET /health` - Health check endpoint

### Socket.IO Events
- `connect` - Client connection
- `disconnect` - Client disconnection
- `weather_update` - Weather data broadcast
- `request_weather` - Manual weather request
- `weather_error` - Weather fetch error

## Data Flow Architecture

### 🔄 **Complete Data Streaming Flow**

**IMPORTANT**: All weather data flows through the FastAPI backend, which acts as the server and security layer.

```
┌─────────────────────────────────────────────────────────────────┐
│                         DATA FLOW                               │
└─────────────────────────────────────────────────────────────────┘

🌐 Frontend (React + Socket.IO Client)
    │
    │ 1. HTTP POST /api/login
    ▼
🛡️ FastAPI Backend (Authentication)
    │
    │ 2. JWT Token Response
    ▼
🌐 Frontend (Authenticated)
    │
    │ 3. Socket.IO Connection
    ▼
 FastAPI Backend (Socket.IO Server)
    │
    │ 4. Weather Data Fetch
    ▼
🌤️ Weather APIs (OpenWeatherMap/Open-Meteo)
    │
    │ 5. Weather Response
    ▼
 FastAPI Backend (Process & Store)
    │
    │ 6. Real-time Broadcast
    ▼
🌐 Frontend (Live Updates)
```

### **Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React SPA     │    │   FastAPI +     │    │   PostgreSQL    │
│   (Port 5173)   │    │   Socket.IO     │    │   Database      │
│                 │    │   (Port 8000)   │    │   (Port 5432)   │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │Socket.IO    │◄┼────┼►│Socket.IO    │ │    │ │   Users     │ │
│ │Client       │ │    │ │Server       │ │    │ │   Table     │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │                 │
│ │Axios HTTP   │◄┼────┼►│FastAPI      │ │    │                 │
│ │Client       │ │    │ │REST API     │ │    │                 │
│ └─────────────┘ │    │ └─────────────┘ │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │                 │
│ │Auth Context │ │    │ │JWT Auth     │ │    │                 │
│ │JWT Storage  │ │    │ │Middleware   │ │    │                 │
│ └─────────────┘ │    │ └─────────────┘ │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                │ HTTP Requests
                                ▼
                       ┌─────────────────┐
                       │  Weather APIs   │
                       │                 │
                       │ ┌─────────────┐ │
                       │ │OpenWeather  │ │
                       │ │API          │ │
                       │ └─────────────┘ │
                       │ ┌─────────────┐ │
                       │ │Open-Meteo   │ │
                       │ │API (Fallback│ │
                       │ └─────────────┘ │
                       └─────────────────┘
```

### 🔄 **Data Streaming Process**

#### **Phase 1: Authentication Flow**
```
1. User enters credentials in React login form
    Frontend ──[HTTP POST /api/login]──► 🛡️ Backend

2. Backend validates credentials against PostgreSQL
   🛡️ Backend ──[SQL Query]──► Database

3. Backend generates JWT token and sends response
   🛡️ Backend ──[JWT Token + User Data]──►  Frontend

4. Frontend stores token in localStorage
    Frontend: localStorage.setItem('auth_token', token)
```

#### **Phase 2: Socket.IO Connection Establishment**
```
5. Frontend establishes Socket.IO connection with JWT
    Frontend ──[Socket.IO Connect]──►  Backend

6. Backend validates connection and adds to active connections
    Backend: active_connections[socket_id] = user_info

7. Backend immediately sends current weather data
    Backend ──[weather_update event]──►  Frontend
```

#### **Phase 3: Weather Data Streaming**
```
8. Backend fetches weather data from external APIs
    Backend ──[HTTP GET]──► 🌤️ Weather APIs

9. Backend processes and formats weather data
    Backend: format_weather_data(raw_api_response)

10. Backend broadcasts to all connected clients
     Backend ──[Socket.IO Broadcast]──►  All Clients

11. Frontend receives and displays real-time updates
     Frontend: onWeatherUpdate(data) → Update UI
```
**No client-side API keys for weather services**

###  **Streaming Data Flow Explained**

 **Backend acts as the single source of truth**
 **All weather requests go through FastAPI backend**
 **Backend manages all external API calls**
 **Socket.IO streams processed data from backend to clients**
 **Backend handles rate limiting and API key management**

### 🔐 **Security**

1. **API Key Protection**: Weather API keys are stored securely on backend
2. **Rate Limiting**: Backend controls API call frequency
3. **Data Validation**: Backend validates and sanitizes all data
4. **Authentication**: All requests require valid JWT tokens
5. **CORS Protection**: Frontend can only connect to authorized backend

### **Communication Protocols**

#### **HTTP/REST API (Axios)**
```javascript
// Frontend → Backend authentication
const response = await axios.post('/api/login', credentials);

// Frontend → Backend weather request
const weather = await axios.get('/api/weather', {
  headers: { Authorization: `Bearer ${token}` }
});
```

#### **WebSocket/Socket.IO**
```javascript
// Frontend establishes persistent connection
const socket = io('http://localhost:8000');

// Frontend listens for real-time updates
socket.on('weather_update', (data) => {
  setWeatherData(data);
});

// Frontend can request immediate updates
socket.emit('request_weather');
```

#### **Backend Weather API Integration**
```python
# Backend fetches from external weather APIs
async with httpx.AsyncClient() as client:
    response = await client.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={"lat": 52.31, "lon": 4.76, "appid": API_KEY}
    )
    
# Backend broadcasts to all connected clients
await sio.emit('weather_update', processed_data)
```

### **Streaming Patterns**

#### **Automatic Hourly Updates**
```python
# Backend runs background task
async def weather_streaming_task():
    while True:
        await asyncio.sleep(3600)  # Wait 1 hour
        weather_data = await weather_service.get_schiphol_weather()
        await sio.emit('weather_update', weather_data)  # Broadcast to all
```

#### **Manual Refresh Requests**
```javascript
// Frontend requests immediate update
const refreshWeather = () => {
  socket.emit('request_weather');  // Request to backend
};

// Backend handles request and sends data
@sio.event
async def request_weather(sid):
    weather_data = await weather_service.get_schiphol_weather()
    await sio.emit('weather_update', weather_data, room=sid)
```

### 🔄 **Data Transformation Pipeline**

```
🌤️ Raw Weather API Response
    │
    ▼ (Backend Processing)
🔧 Data Validation & Formatting
    │
    ▼ (Backend Processing)
 Structured Weather Object
    │
    ▼ (Socket.IO)
 Real-time Broadcast
    │
    ▼ (Frontend)
 UI State Update & Display
```

This architecture ensures **security**, **performance**, and **reliability** by centralizing all external API communication through the trusted backend server.

## 🐳 Docker Deployment

### Production Dockerfile (Backend)

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:socket_app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: weatherdb
      POSTGRES_USER: username
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://username:password@db/weatherdb
      - JWT_SECRET_KEY=your-production-secret-key
      - OPENWEATHER_API_KEY=your-api-key
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### Deployment Commands

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Note**: For production use, ensuresecurity measures, monitoring, and scaling considerations.

##  Development

### Running Tests

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Backend linting
cd backend
black . && flake8 .

# Frontend linting
cd frontend
npm run lint
```

## 🔒 Security

- **Password Hashing**: bcrypt with salt rounds
- **JWT Tokens**: Secure token-based authentication
- **CORS Protection**: Configured origins
- **SQL Injection Prevention**: SQLAlchemy ORM
- **Environment Variables**: Sensitive data protection

## 🌍 Weather Data Sources

### Primary: OpenWeatherMap
- **Location**: Schiphol Airport (52.31°N, 4.76°E)
- **Updates**: Real-time data
- **Metrics**: Temperature, humidity, pressure, wind, visibility

### Fallback: Open-Meteo
- **Free Service**: No API key required
- **KNMI Integration**: Dutch weather service
- **Reliability**: High uptime and accuracy

##  Mobile App

- **Responsive Design**: Works on all screen sizes
- **Touch-friendly**: Optimized for mobile interaction
- **Progressive Enhancement**: Graceful degradation

##  Troubleshooting

### Common Issues

1. **Database Connection Error**:
   ```bash
   # Check PostgreSQL service
   sudo systemctl status postgresql
   # Verify database exists
   psql -l
   ```

2. **Socket.IO Connection Failed**:
   - Verify backend is running on port 8000
   - Check CORS configuration in backend
   - Ensure no firewall blocking WebSocket connections

3. **Weather API Error**:
   - Verify API key in `.env` file
   - Check API quota limits
   - Review network connectivity

4. **Frontend Build Issues**:
   ```bash
   # Clear node modules and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

##  Performance Optimizations

- **Connection Pooling**: SQLAlchemy async engine
- **Caching**: Weather data caching (1-hour intervals)
- **Compression**: Gzip compression for API responses
- **Lazy Loading**: Component-based code splitting
- **WebSocket Optimization**: Efficient event handling

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **OpenWeatherMap**: Weather data provider
- **Open-Meteo**: Free weather API service
- **FastAPI**: Python web framework
- **Socket.IO**: Real-time communication library
- **React**: Frontend library

---
