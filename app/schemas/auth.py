from pydantic import BaseModel, EmailStr, Field
from app.core import settings
from typing import Optional

class UserRegister(BaseModel):
    username: str = Field(..., min_length = 3, max_length = 20)
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length = 5)

class UserLogin(BaseModel):
    username: str
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'
    access_token_expires_in_minutes: int = settings.JWT_TOKEN_EXPIRE_MINUTES
    refresh_token_expires_in_days: int = settings.REFRESH_TOKEN_EXPIRE_DAYS
