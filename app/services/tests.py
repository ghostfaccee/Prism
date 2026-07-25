# This service is necessary to provide the data required for testing.
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import UserRepository

class UserTestsService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = UserRepository(db)

    async def get_verification_token_by_username(self, username: str) -> str:
        user = await self.repo.get_by_username(username)
        return user.verification_token

    async def get_hashed_password_by_username(self,  username: str) -> str:
        user = await self.repo.get_by_username(username)
        return user.hashed_password
    