from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import UserRepository
from app.models import User
from app.exceptions import user as user_exc

class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = UserRepository(db)
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise user_exc.UserDoesNotExists()
        return user
    