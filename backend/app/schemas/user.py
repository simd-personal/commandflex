from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum
from backend.app.models.user import UserRole

class UserRole(str, Enum):
    dispatcher = "dispatcher"
    responder = "responder"

class UserCreate(BaseModel):
    username: str = Field(..., description="Username for login")
    password: str = Field(..., description="Password")
    role: UserRole = Field(..., description="User role")

class UserLogin(BaseModel):
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")

class UserResponse(BaseModel):
    id: int
    username: str
    role: UserRole

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: Optional[str] = None
    role: Optional[UserRole] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    username: Optional[str] = None 