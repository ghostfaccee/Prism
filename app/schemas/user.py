from pydantic import BaseModel, Field, EmailStr
from uuid import UUID
from typing import Optional

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length = 3, max_length = 20)
    email: Optional[EmailStr] = None

class UpdatePassword(BaseModel):
    old_pass: str
    new_pass: str = Field(..., min_length = 5)

class UserResponse(BaseModel):
    user_id: UUID
    username: str
    email: Optional[str]
    is_active: bool