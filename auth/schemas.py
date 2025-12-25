from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: Optional[bool] = True


class CreateUser(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    role_id: int

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginInput(BaseModel):
    email: EmailStr
    password: str

class BlacklistedTokenSubmit(BaseModel):
    token: str
    reason: Optional[str] = None