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
    title="React Backend API",
    description="RESTful API backend for React frontend",
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

# API Routes
@app.get("/")
async def root():
    return {"message": "Python Backend API for React Frontend", "timestamp": datetime.utcnow()}

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