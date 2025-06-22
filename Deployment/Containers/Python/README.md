# Deploying the Dockerized Python application

Creating a Python backend for RESTful APIs

Choose a Python framework

Select a Python web framework suitable for building RESTful APIs.

Flask: 

A lightweight micro-framework, ideal for simple APIs.

FastAPI: 

A modern, fast, and asynchronous web framework built on Starlette and Pydantic, excellent for high-performance APIs.

Project setup

Create a virtual environment and activate it.

python -m venv venv 

Define Python dependencies and libraries in the requirements.txt file.

```

    fastapi==0.104.1
    uvicorn[standard]==0.24.0
    pydantic[email]==2.5.0
    python-jose[cryptography]==3.3.0
    passlib[bcrypt]==1.7.4
    python-multipart==0.0.6
    asyncpg==0.29.0
    python-dotenv==1.0.0

```
Python application uses FastAPI with async/await support

```

    from fastapi import FastAPI, HTTPException, Depends
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from pydantic import BaseModel, EmailStr
    from typing import List, Optional
    import uvicorn
    import os
    from datetime import datetime, timedelta
    import jwt
    from passlib.context import CryptContext
    import asyncpg
    import asyncio
    from contextlib import asynccontextmanager

    # Database connection pool
    db_pool = None

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup
        global db_pool
        db_pool = await asyncpg.create_pool(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "password"),
            database=os.getenv("DB_NAME", "apidb"),
            min_size=1,
            max_size=20
        )
        yield
        # Shutdown
        await db_pool.close()

    # FastAPI app with lifespan
    app = FastAPI(
        title="RESTful APIs",
        description="RESTful APIs for React frontend",
        version="1.0.0",
        lifespan=lifespan
    )

    # CORS middleware for React frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:3001", "*"],  # React dev server
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Security
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM = "HS256"

    # Pydantic models
    class UserCreate(BaseModel):
        name: str
        email: EmailStr
        password: str

    class UserResponse(BaseModel):
        id: int
        name: str
        email: str
        created_at: datetime

    class UserLogin(BaseModel):
        email: EmailStr
        password: str

    class Token(BaseModel):
        access_token: str
        token_type: str

    class TodoCreate(BaseModel):
        title: str
        description: Optional[str] = None

    class TodoResponse(BaseModel):
        id: int
        title: str
        description: Optional[str]
        completed: bool
        created_at: datetime
        user_id: int

    # Database functions
    async def get_db():
        async with db_pool.acquire() as connection:
            yield connection

    # Authentication functions
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
        except jwt.PyJWTError:
            raise credentials_exception
        
        async with db_pool.acquire() as connection:
            user = await connection.fetchrow("SELECT * FROM users WHERE email = $1", email)
            if user is None:
                raise credentials_exception
        return user

    # API routes
    @app.get("/")
    async def root():
        return {"message": "Python Backend API for React frontend", "timestamp": datetime.utcnow()}

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "timestamp": datetime.utcnow()}

    # Authentication endpoints
    @app.post("/api/auth/register", response_model=UserResponse)
    async def register(user: UserCreate):
        hashed_password = pwd_context.hash(user.password)
        
        async with db_pool.acquire() as connection:
            # Check if user exists
            existing_user = await connection.fetchrow("SELECT email FROM users WHERE email = $1", user.email)
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already registered")
            
            # Create user
            query = """
                INSERT INTO users (name, email, password_hash, created_at) 
                VALUES ($1, $2, $3, $4) 
                RETURNING id, name, email, created_at
            """
            new_user = await connection.fetchrow(
                query, user.name, user.email, hashed_password, datetime.utcnow()
            )
            
        return UserResponse(**dict(new_user))

    @app.post("/api/auth/login", response_model=Token)
    async def login(user_credentials: UserLogin):
        async with db_pool.acquire() as connection:
            user = await connection.fetchrow(
                "SELECT * FROM users WHERE email = $1", user_credentials.email
            )
            
        if not user or not pwd_context.verify(user_credentials.password, user['password_hash']):
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user['email']}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

    # User endpoints
    @app.get("/api/users/me", response_model=UserResponse)
    async def read_users_me(current_user = Depends(get_current_user)):
        return UserResponse(**dict(current_user))

    # Todo endpoints
    @app.get("/api/todos", response_model=List[TodoResponse])
    async def get_todos(current_user = Depends(get_current_user)):
        async with db_pool.acquire() as connection:
            todos = await connection.fetch(
                "SELECT * FROM todos WHERE user_id = $1 ORDER BY created_at DESC", 
                current_user['id']
            )
        return [TodoResponse(**dict(todo)) for todo in todos]

    @app.post("/api/todos", response_model=TodoResponse)
    async def create_todo(todo: TodoCreate, current_user = Depends(get_current_user)):
        async with db_pool.acquire() as connection:
            query = """
                INSERT INTO todos (title, description, completed, created_at, user_id) 
                VALUES ($1, $2, $3, $4, $5) 
                RETURNING *
            """
            new_todo = await connection.fetchrow(
                query, todo.title, todo.description, False, datetime.utcnow(), current_user['id']
            )
        return TodoResponse(**dict(new_todo))

    @app.put("/api/todos/{todo_id}", response_model=TodoResponse)
    async def update_todo(todo_id: int, completed: bool, current_user = Depends(get_current_user)):
        async with db_pool.acquire() as connection:
            updated_todo = await connection.fetchrow(
                "UPDATE todos SET completed = $1 WHERE id = $2 AND user_id = $3 RETURNING *",
                completed, todo_id, current_user['id']
            )
            
        if not updated_todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        
        return TodoResponse(**dict(updated_todo))

    @app.delete("/api/todos/{todo_id}")
    async def delete_todo(todo_id: int, current_user = Depends(get_current_user)):
        async with db_pool.acquire() as connection:
            result = await connection.execute(
                "DELETE FROM todos WHERE id = $1 AND user_id = $2",
                todo_id, current_user['id']
            )
        
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Todo not found")
        
        return {"message": "Todo deleted successfully"}

    if __name__ == "__main__":
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=int(os.getenv("PORT", 8000)),
            reload=True
        )

```
Structure your project with clear separation of concerns (e.g., models, views/resources, serializers).

API endpoints

Define API endpoints (routes) and associate them with functions or class-based views that handle requests.

Implement CRUD operations (Create, Read, Update, Delete) for your resources.

Use appropriate HTTP methods (GET, POST, PUT, DELETE) for each operation.

Handle data serialization/deserialization (e.g., converting Python objects to JSON and vice versa).

Database configuration

Choose a database (e.g., PostgreSQL, MySQL, MongoDB).

Use an ORM (Object-Relational Mapper) like SQLAlchemy or Django's ORM to interact with the database.

Define schema and models representing your data structures.

```
    -- Create users table
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Create todos table
    CREATE TABLE IF NOT EXISTS todos (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        completed BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
    );

    -- Create indexes
    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
    CREATE INDEX IF NOT EXISTS idx_todos_user_id ON todos(user_id);
    CREATE INDEX IF NOT EXISTS idx_todos_created_at ON todos(created_at);

    -- Insert sample data
    INSERT INTO users (name, email, password_hash) VALUES 
        ('John Doe', 'john@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewwrzqNlxN5.i0r6'),
        ('Jane Smith', 'jane@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewwrzqNlxN5.i0r6')
    ON CONFLICT (email) DO NOTHING;

```
Authentication and authorization

Implement a security for your API, such as token-based authentication (e.g., JWT) or session-based authentication.

JWT-based authentication with bcrypt password hashing.

Control access to resources based on user roles or permissions.

CORS configured for React frontend integration.

Create a Dockerfile for Python application

```
    # Example for Flask/FastAPI with Gunicorn

    # Use a lightweight Python base image
    FROM python:3.9-slim-buster

    # Set the working directory inside the container
    WORKDIR /app

    # Copy requirements.txt and install dependencies
    COPY requirements.txt .

    RUN pip install --no-cache-dir -r requirements.txt

    # Copy the rest of your application code
    COPY . .

    # Expose the port your application will run on
    EXPOSE 8000 # (e.g., Flask's default is 5000)

    # Command to run your application
    CMD ["gunicorn", "--bind", "0.0.0.0:8000", "your_app_name:app"] 

```
Create a Dockerfile for React app

```

    # Build stage
    FROM node:18-alpine AS builder

    WORKDIR /app

    # Copy package files
    COPY package*.json ./

    # Install dependencies
    RUN npm ci --only=production

    # Copy source code
    COPY . .

    # Build the application
    RUN npm run build

    # Production stage
    FROM nginx:alpine

    # Copy built app to nginx
    COPY --from=builder /app/build /usr/share/nginx/html

    # Copy nginx configuration
    COPY nginx.conf /etc/nginx/conf.d/default.conf

    # Expose port
    EXPOSE 3000

    # Start nginx
    CMD ["nginx", "-g", "daemon off;"]

```
The docker-compose.yml file

```

    version: '3.8'

    services:
      # PostgreSQL Database
      postgres:
        image: postgres:15-alpine
        container_name: postgres_db
        restart: unless-stopped
        environment:
          POSTGRES_DB: apidb
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: password
        ports:
          - "5432:5432"
        volumes:
          - postgres_data:/var/lib/postgresql/data
          - ./init.sql:/docker-entrypoint-initdb.d/init.sql
        networks:
          - app-network
        healthcheck:
          test: ["CMD-SHELL", "pg_isready -U postgres"]
          interval: 30s
          timeout: 10s
          retries: 5

      # Python Backend API
      backend:
        build:
          context: .
          dockerfile: Dockerfile
        container_name: python_backend
        restart: unless-stopped
        ports:
          - "8000:8000"
        environment:
          - DB_HOST=postgres
          - DB_PORT=5432
          - DB_USER=postgres
          - DB_PASSWORD=password
          - DB_NAME=apidb
          - SECRET_KEY=your-super-secret-key-here-change-in-production
          - PORT=8000
        depends_on:
          postgres:
            condition: service_healthy
        networks:
          - app-network
        volumes:
          - ./app:/app
        healthcheck:
          test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
          interval: 30s
          timeout: 10s
          retries: 3

      # React Frontend (optional - can be deployed separately)
      frontend:
        build:
          context: ./frontend
          dockerfile: Dockerfile
        container_name: react_frontend
        restart: unless-stopped
        ports:
          - "3000:3000"
        environment:
          - REACT_APP_API_URL=http://localhost:8000
        depends_on:
          - backend
        networks:
          - app-network

    volumes:
      postgres_data:

    networks:
      app-network:
        driver: bridge

```

Nginx configuration file for React

```

    server {
        listen 3000;
        server_name localhost;

        location / {
            root /usr/share/nginx/html;
            index index.html index.htm;
            try_files $uri $uri/ /index.html;
        }

        # API proxy (optional if backend is on different domain)
        location /api {
            proxy_pass http://backend:8000/api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Enable gzip compression
        gzip on;
        gzip_vary on;
        gzip_min_length 1024;
        gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;
    }

```
The environment variables in .env file

```

    # Database
    DB_HOST=postgres
    DB_PORT=5432
    DB_USER=postgres
    DB_PASSWORD=your-secure-password
    DB_NAME=apidb

    # Backend
    SECRET_KEY=your-super-secret-key-change-in-production
    PORT=8000

    # Frontend
    REACT_APP_API_URL=http://localhost:8000

```
The bash script for Docker deployment

```

    #!/bin/bash

    echo "🚀 Deploying Python RESTful APIs + React app with Docker..."

    # Create necessary directories
    mkdir -p app frontend

    # Clean up existing Docker containers
    echo "🧹 Cleaning up existing containers..."
    docker-compose down -v

    # Build and start services
    echo "🏗️ Building and starting services..."
    docker-compose up --build -d

    # Wait for services to be ready
    echo "⏳ Waiting for services to start..."
    sleep 30

    # Check service status
    echo "🔍 Checking service status..."
    docker-compose ps

    # Test the RESTful API
    echo "🧪 Testing..."
    curl -X GET http://localhost:8000/health
    curl -X GET http://localhost:8000/

    echo "✅ Docker deployment completed."
    echo "🔗 RESTful APIs: http://localhost:8000"
    echo "🔗 React app: http://localhost:3000"
    echo "🔗 API documentation: http://localhost:8000/docs"

```