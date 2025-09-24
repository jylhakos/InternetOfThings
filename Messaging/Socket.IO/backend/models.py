from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class WeatherData(BaseModel):
    temperature: float
    humidity: int
    wind_speed: float
    wind_direction: int
    description: str
    condition: str
    pressure: float
    visibility: float
    timestamp: datetime
    location: str = "Amsterdam Airport Schiphol"

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: User