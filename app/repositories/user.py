from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from sqlalchemy import select
from app.models import User
from typing import Optional
from uuid import UUID

class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
    
    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def update(self, user_id: UUID, data: dict) -> Optional[User]:
        user = await self.get_by_id(user_id)
        if not user:
            return None
        for key, value in data.items():
            setattr(user, key, value)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def delete(self, user_id: UUID) -> bool:
        user = await self.get_by_id(user_id)
        if user:
            await self.db.delete(user)
            await self.db.commit()
            return True
        return False

    async def get_by_username(self, username: str) -> Optional[User]:
        user = await self.db.execute(select(User).where(User.username == username))
        return user.scalar_one_or_none()
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        user = await self.db.execute(select(User).where(User.user_id == user_id))
        return user.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        user = await self.db.execute(select(User).where(User.email == email))
        return user.scalar_one_or_none()
    
    async def get_by_verification_token(self, token: str) -> Optional[User]:
        user = await self.db.execute(select(User).where(User.verification_token == token))
        return user.scalar_one_or_none()

    async def activate_user(self, user_id: UUID) -> Optional[User]:
        user = await self.get_by_id(user_id)
        if not user:
            return None
        user.is_active = True
        user.verification_token = None
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def setup_new_state(self, user_id: UUID, state: str, expire: datetime) -> bool:
        user = await self.get_by_id(user_id)
        if not user:
            return False
        user.github_oauth_state = state
        user.github_oauth_state_expires = expire
        await self.db.commit()
        await self.db.refresh(user)
        return True

    async def reset_state(self, user_id: UUID) -> bool:
        user = await self.get_by_id(user_id)
        if not user:
            return False
        user.github_oauth_state = None
        user.github_oauth_state_expires = None
        await self.db.commit()
        await self.db.refresh(user)
        return True
    