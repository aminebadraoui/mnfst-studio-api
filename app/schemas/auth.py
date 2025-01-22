from typing import Optional
from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool = True
    is_superuser: bool = False

class UserRegister(UserBase):
    password: str

class UserCreate(UserRegister):
    pass

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: int

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    password_hash: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str 