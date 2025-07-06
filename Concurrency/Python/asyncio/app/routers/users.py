from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from databases import Database

from app.database import get_db, get_database
from app import schemas, crud
from app.schemas import APIResponse

router = APIRouter(prefix="/users", tags=["users"])

# Synchronous endpoints
@router.get("/", response_model=List[schemas.User])
async def read_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get users with pagination - synchronous version"""
    users = crud.UserCRUD.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=schemas.User)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID - synchronous version"""
    db_user = crud.UserCRUD.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create new user - synchronous version"""
    db_user = crud.UserCRUD.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.UserCRUD.create_user(db=db, user=user)

# Asynchronous endpoints for better concurrency
@router.get("/async/", response_model=List[dict])
async def read_users_async(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    database: Database = Depends(get_database)
):
    """Get users with pagination - asynchronous version for high concurrency"""
    users = await crud.AsyncUserCRUD.get_users_async(database, skip=skip, limit=limit)
    return [dict(user) for user in users]

@router.get("/async/{user_id}", response_model=dict)
async def read_user_async(user_id: int, database: Database = Depends(get_database)):
    """Get user by ID - asynchronous version for high concurrency"""
    user = await crud.AsyncUserCRUD.get_user_by_id_async(database, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return dict(user)

@router.post("/async/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_user_async(user: schemas.UserCreate, database: Database = Depends(get_database)):
    """Create new user - asynchronous version for high concurrency"""
    created_user = await crud.AsyncUserCRUD.create_user_async(database, user=user)
    return dict(created_user)

# Health check endpoint
@router.get("/health/check", response_model=APIResponse)
async def health_check():
    """Health check endpoint"""
    return APIResponse(
        success=True,
        message="Users service is healthy",
        data={"status": "operational"}
    )