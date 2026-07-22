from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from typing import Optional

class UserRegister(BaseModel):
    username: str = Field(..., min_length = 3, max_length = 20)
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length = 5)

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
