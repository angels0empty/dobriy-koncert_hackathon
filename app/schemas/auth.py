from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Literal
from datetime import datetime
from uuid import UUID


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: Literal["student", "teacher"] = "student"

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
