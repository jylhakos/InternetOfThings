from sqlalchemy.orm import Session
from sqlalchemy import text
from app import models, schemas
from typing import List, Optional
from databases import Database

# Synchronous CRUD operations
class UserCRUD:
    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.email == email).first()

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
        return db.query(models.User).offset(skip).limit(limit).all()

    @staticmethod
    def create_user(db: Session, user: schemas.UserCreate) -> models.User:
        db_user = models.User(**user.model_dump())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
        db_user = db.query(models.User).filter(models.User.id == user_id).first()
        if db_user:
            update_data = user_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_user, field, value)
            db.commit()
            db.refresh(db_user)
        return db_user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        db_user = db.query(models.User).filter(models.User.id == user_id).first()
        if db_user:
            db.delete(db_user)
            db.commit()
            return True
        return False

# Asynchronous CRUD operations for high concurrency
class AsyncUserCRUD:
    @staticmethod
    async def get_users_async(database: Database, skip: int = 0, limit: int = 100):
        query = """
        SELECT id, email, username, full_name, is_active, created_at, updated_at 
        FROM users 
        ORDER BY id 
        OFFSET :skip LIMIT :limit
        """
        return await database.fetch_all(query=query, values={"skip": skip, "limit": limit})

    @staticmethod
    async def get_user_by_id_async(database: Database, user_id: int):
        query = """
        SELECT id, email, username, full_name, is_active, created_at, updated_at 
        FROM users 
        WHERE id = :user_id
        """
        return await database.fetch_one(query=query, values={"user_id": user_id})

    @staticmethod
    async def create_user_async(database: Database, user: schemas.UserCreate):
        query = """
        INSERT INTO users (email, username, full_name, is_active) 
        VALUES (:email, :username, :full_name, :is_active) 
        RETURNING id, email, username, full_name, is_active, created_at, updated_at
        """
        return await database.fetch_one(query=query, values=user.model_dump())