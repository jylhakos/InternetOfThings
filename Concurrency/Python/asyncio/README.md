# Web application with FastAPI

FastAPI is built on Starlette and Uvicorn designed to leverage Python's asyncio library for asynchronous programming. enabling it to handle a large number of concurrent requests.

## The asynchronous operations

The asynchronous database transactions in Python enables non-blocking database interactions.

The asyncpg and databases are two distinct libraries in Python used for asynchronous database operations

The asyncpg is an asynchronous PostgreSQL client library for Python's asyncio framework.

The databases is an asynchronous database library that provides a unified interface for various databases, including PostgreSQL.

The databases allows you to write queries using the SQLAlchemy Core expression language.

## Example in Python

The project

```

	my_fastapi_app/
	├── app/
	│   ├── __init__.py
	│   ├── main.py
	│   ├── database.py
	│   ├── models.py
	│   ├── schemas.py
	│   ├── crud.py
	│   └── routers/
	│       ├── __init__.py
	│       └── users.py
	├── requirements.txt
	├── .env
	└── docker-compose.yml

```

API (RESTful)

```

	GET /api/v1/users/ - Get all users (paginated)
	GET /api/v1/users/{id} - Get user by ID
	POST /api/v1/users/ - Create new user
	GET /api/v1/users/async/ - Async version for high concurrency
	GET /docs - Interactive API documentation

```
The web application (FastAPI)

```

	from fastapi import FastAPI, HTTPException
	from fastapi.middleware.cors import CORSMiddleware
	from fastapi.responses import JSONResponse
	import uvicorn
	import asyncio
	from contextlib import asynccontextmanager

	from app.database import database, engine, Base
	from app.routers import users

	# Create database tables
	Base.metadata.create_all(bind=engine)

	# Lifespan context manager for startup/shutdown events
	@asynccontextmanager
	async def lifespan(app: FastAPI):
	    # Startup
	    await database.connect()
	    print("Database connected")
	    yield
	    # Shutdown
	    await database.disconnect()
	    print("Database disconnected")

	# Initialize FastAPI app with lifespan
	app = FastAPI(
	    title="FastAPI PostgreSQL Demo",
	    description="A FastAPI application with PostgreSQL and async support",
	    version="1.0.0",
	    lifespan=lifespan
	)

	# CORS middleware for browser requests
	app.add_middleware(
	    CORSMiddleware,
	    allow_origins=["*"],  # In production, specify exact origins
	    allow_credentials=True,
	    allow_methods=["*"],
	    allow_headers=["*"],
	)

	# Include routers
	app.include_router(users.router, prefix="/api/v1")

	# Root endpoint
	@app.get("/")
	async def root():
	    return {
	        "message": "FastAPI with PostgreSQL",
	        "version": "1.0.0",
	        "docs": "/docs",
	        "redoc": "/redoc"
	    }

	# Global exception handler
	@app.exception_handler(Exception)
	async def global_exception_handler(request, exc):
	    return JSONResponse(
	        status_code=500,
	        content={
	            "success": False,
	            "message": "Internal server error",
	            "detail": str(exc)
	        }
	    )

	# Run the application
	if __name__ == "__main__":
	    uvicorn.run(
	        "app.main:app",
	        host="0.0.0.0",
	        port=8000,
	        reload=True,  # For development only
	        workers=1,    # For development; increase for production
	        loop="asyncio"
	    )

```
References

Concurrency and async / await¶

https://fastapi.tiangolo.com/async/