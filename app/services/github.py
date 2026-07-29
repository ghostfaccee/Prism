import httpx
from app.exceptions import github as github_exc
from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import GitHubIntegrationRepository
from app.models import GitHubIntegration
from app.core import settings
from app.schemas import GitHubTokenResponse, GitHubUserInfo

# TODO: write tests

class GitHubService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = GitHubIntegrationRepository(db)

    # === OAuth ===
    # Documentation: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps

    async def exchange_code_for_token(self, code: str) -> GitHubTokenResponse: 
        '''Exchanges a temporary code for a permanent token, which is required to obtain a permanent token.'''
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://github.com/login/oauth/access_token', # exchanging a code for a token
                headers = {'Accept': 'application/json'}, # the response is in the form of json
                params = {
                    'client_id': settings.GITHUB_CLIENT_ID, # required
                    'client_secret': settings.GITHUB_CLIENT_SECRET, # required
                    'code': code, # required
                    'redirect_uri': settings.GITHUB_REDIRECT_URI # recommended
                }
            )
        response.raise_for_status()
        data = response.json()
        if 'access_token' not in data:
            raise github_exc.GitHubError(data)
        return GitHubTokenResponse(**data)

    async def create_user_token(self, user_id: UUID, token: str) -> Optional[GitHubIntegration]:
        '''Saves the token for the user'''
        integration = await self.repo.get_by_user_id(user_id)
        if integration:
            raise github_exc.GitHubIntegrationExistsError()
        integration = GitHubIntegration(
            user_id = user_id,
            access_token = token
        )
        return await self.repo.create(integration)

    async def exists_integration_by_user_id(self, user_id: UUID) -> bool:
        integration = await self.repo.get_by_user_id(user_id)
        if integration:
            return True
        return False

    async def update_user_token(self, user_id: UUID, token: str) -> Optional[GitHubIntegration]:
        '''Updates the token for the user'''
        integration = await self.repo.get_by_user_id(user_id)
        if not integration:
            raise github_exc.GitHubIntegrationDoesNotExistsError()
        return await self.repo.update_access_token(user_id, token)

    async def delete(self, user_id: UUID) -> None:
        '''Delete the github integration for the user'''
        if not await self.repo.delete_by_user_id(user_id):
            raise github_exc.GitHubIntegrationDoesNotExistsError()
        return None

    # === GitHub API ===
    # Documentation: https://docs.github.com/en/rest/about-the-rest-api/about-the-rest-api?apiVersion=2026-03-10

    async def _get_access_token_by_user_id(self, user_id: UUID) -> str:
        '''Obtaining a token based on the user's ID is necessary for the service's API functions'''
        integration = await self.repo.get_by_user_id(user_id)
        if not integration:
            raise github_exc.GitHubIntegrationDoesNotExistsError()
        return integration.access_token

    async def get_user_info(self, user_id: UUID) -> GitHubUserInfo:
        '''Gets information about a github user'''
        access_token = await self._get_access_token_by_user_id(user_id)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                'https://api.github.com/user',
                headers = {'Authorization': f'Bearer {access_token}'}
            )
        if response.status_code == 401:
            raise github_exc.InvalidOrExpiredGitHubTokenError()

        response.raise_for_status()
        data = response.json()
        return GitHubUserInfo(**data)

    # TODO: add ways to get other statistics