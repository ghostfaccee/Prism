from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.models import GitHubIntegration
from uuid import UUID

class GitHubIntegrationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_user_id(self, user_id: UUID) -> Optional[GitHubIntegration]:
        github = await self.db.execute(select(GitHubIntegration).where(GitHubIntegration.user_id == user_id))
        return github.scalar_one_or_none()

    async def create(self, integration: GitHubIntegration) -> GitHubIntegration:
        self.db.add(integration)
        await self.db.commit()
        await self.db.refresh(integration)
        return integration

    async def update_access_token(self, user_id: UUID, access_token: str) -> Optional[GitHubIntegration]:
        integration = await self.get_by_user_id(user_id)
        if not integration:
            return None
        integration.access_token = access_token
        await self.db.commit()
        await self.db.refresh(integration)
        return integration

    async def update_github_username(self, user_id: UUID, new_username: str) -> Optional[GitHubIntegration]:
        integration = await self.get_by_user_id(user_id)
        if not integration:
            return None
        integration.github_username = new_username
        await self.db.commit()
        await self.db.refresh(integration)
        return integration

    async def delete_by_user_id(self, user_id: UUID) -> bool:
        integration = await self.get_by_user_id(user_id)
        if integration:
            await self.db.delete(integration)
            await self.db.commit()
            return True
        return False

