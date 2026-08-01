import httpx
from app.exceptions import github as github_exc
from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import GitHubIntegrationRepository
from app.models import GitHubIntegration
from app.core import settings
from app.schemas import GitHubTokenResponse, GitHubUserInfo
from app.utils import handle_github_status_code
# TODO: Due to the error handling update, update the tests
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
        handle_github_status_code(response)
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

    async def _update_github_username(self, user_id: UUID, new_username: str) -> Optional[GitHubIntegration]:
        '''Updates the username from GitHub'''
        # TODO: unit tests
        integration = await self.repo.get_by_user_id(user_id)
        if not integration:
            raise github_exc.GitHubIntegrationDoesNotExistsError()
        return await self.repo.update_github_username(user_id, new_username)

    async def delete(self, user_id: UUID) -> None:
        '''Delete the github integration for the user'''
        if not await self.repo.delete_by_user_id(user_id):
            raise github_exc.GitHubIntegrationDoesNotExistsError()
        return None

    # === GitHub API ===
    # Documentation: https://docs.github.com/en/rest/about-the-rest-api/about-the-rest-api?apiVersion=2026-03-10

    async def _get_access_token_by_user_id(self, user_id: UUID) -> Optional[str]:
        '''Obtaining a token based on the user's ID is necessary for the service's API functions'''
        integration = await self.repo.get_by_user_id(user_id)
        if not integration:
            raise github_exc.GitHubIntegrationDoesNotExistsError()
        return integration.access_token

    async def _get_github_username(self, user_id: UUID) -> Optional[str]:
        '''Required to get a username on GitHub'''
        # TODO: unit tests
        integration = await self.repo.get_by_user_id(user_id)
        if not integration:
            raise github_exc.GitHubIntegrationDoesNotExistsError()
        async with httpx.AsyncClient() as client:
            response = await client.get(
                'https://api.github.com/user',
                headers = {'Authorization': f'Bearer {integration.access_token}'}
            )
        handle_github_status_code(response)
        data = response.json()
        if 'login' not in data:
            raise github_exc.LoginNotInResponseError()
        return data['login']

    async def _get_ensure_current_github_username(self, user_id: UUID) -> Optional[str]:
        '''Returns the user's GitHub username and updates it in the database if it has changed.'''
        # TODO: unit tests
        integration = await self.repo.get_by_user_id(user_id)
        if not integration:
            raise github_exc.GitHubIntegrationDoesNotExistsError()
        current_username = await self._get_github_username(user_id)
        if integration.github_username != current_username or integration.github_username is None:
            updated_integration = await self._update_github_username(user_id, current_username)
            return updated_integration.github_username
        else:
            return integration.github_username

    async def get_user_info(self, user_id: UUID) -> GitHubUserInfo:
        '''Gets information about a github user'''
        access_token = await self._get_access_token_by_user_id(user_id)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                'https://api.github.com/user',
                headers = {'Authorization': f'Bearer {access_token}'}
            )
        handle_github_status_code(response)
        data = response.json()
        return GitHubUserInfo(**data)

    async def get_user_events(self, user_id: UUID) -> list:
        '''Receives user events'''
        access_token = await self._get_access_token_by_user_id(user_id)
        username = await self._get_ensure_current_github_username(user_id)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'https://api.github.com/users/{username}/events',
                headers = {'Authorization': f'Bearer {access_token}'},
                params = {'per_page': 5}
            )
        handle_github_status_code(response)
        return response.json()

    async def get_user_repositories(self, user_id: UUID) -> list:
        access_token = await self._get_access_token_by_user_id(user_id)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                'https://api.github.com/user/repos',
                headers = {'Authorization': f'Bearer {access_token}'},
                params = {'per_page': 5}
            )
        handle_github_status_code(response)
        return response.json()

    async def get_github_commits(self, user_id: int, repo_name: str) -> list:
        owner = await self._get_ensure_current_github_username(user_id)
        access_token = await self._get_access_token_by_user_id(user_id)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'https://api.github.com/repos/{owner}/{repo_name}/commits',
                headers = {'Authorization': f'Bearer {access_token}'},
                params = {'per_page': 5}
            )
        handle_github_status_code(response)
        return response.json()

    async def get_repository_pulls(self, user_id: UUID, repo_name: str) -> list:
        owner = await self._get_ensure_current_github_username(user_id)
        access_token = await self._get_access_token_by_user_id(user_id)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'https://api.github.com/repos/{owner}/{repo_name}/pulls',
                headers = {'Authorization': f'Bearer {access_token}'},
                params = {'state': 'all', 'sort': 'updated', 'direction': 'desc', 'per_page': 5}
            )
        handle_github_status_code(response)
        return response.json()

    async def get_repository_issues(self, user_id: UUID, repo_name: str) -> list:
        owner = await self._get_ensure_current_github_username(user_id)
        access_token = await self._get_access_token_by_user_id(user_id)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'https://api.github.com/repos/{owner}/{repo_name}/issues',
                headers = {'Authorization': f'Bearer {access_token}'},
                params = {'state': 'all', 'sort': 'updated', 'direction': 'desc', 'per_page': 5}
            )
        handle_github_status_code(response)
        return response.json()
    