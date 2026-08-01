import pytest
from httpx import HTTPStatusError
from unittest.mock import AsyncMock, MagicMock, patch
from app.services import GitHubService
from app.schemas import GitHubTokenResponse, GitHubUserInfo
from app.models import User
from app.exceptions import github as github_exc

@pytest.mark.asyncio
async def test_exchange_code_for_token() -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'access_token' : 'token',
        'token_type' : 'bearer',
        'scope' : 'scope'
    }
    mock_response.raise_for_status = MagicMock(return_value = None)

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    with patch('httpx.AsyncClient', return_value = mock_client):
        service = GitHubService(AsyncMock())
        res = await service.exchange_code_for_token('testcode')
    assert isinstance(res, GitHubTokenResponse)
    assert res.access_token == 'token'
    assert res.token_type == 'bearer'
    assert res.scope == 'scope'

@pytest.mark.asyncio
async def test_exchange_code_for_token_but_without_access_token() -> None:
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'error' : 'error123',
        'error_description' : 'idk what this error is'
    }
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock(return_value = None)
    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    with patch('httpx.AsyncClient', return_value = mock_client):
        service = GitHubService(AsyncMock())
        with pytest.raises(github_exc.GitHubError):
            await service.exchange_code_for_token('token')

@pytest.mark.asyncio
async def test_exchange_code_for_token_but_http_error() -> None:
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'error' : 'error123',
        'error_description' : 'error with code 400'
    }
    mock_response.status_code = 400
    mock_response.raise_for_status.side_effect = HTTPStatusError('ERROR', request = MagicMock(), response = MagicMock())
    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    with patch('httpx.AsyncClient', return_value = mock_client):
        service = GitHubService(AsyncMock())
        with pytest.raises(HTTPStatusError):
            await service.exchange_code_for_token('token')

@pytest.mark.asyncio
async def test_create_user_token(test_user: User, github_service: GitHubService) -> None:
    integration = await github_service.create_user_token(test_user.user_id, '123')
    assert integration.user_id == test_user.user_id
    assert integration.access_token == '123'

@pytest.mark.asyncio
async def test_create_user_token_but_integration_already_exists(test_user: User, github_service: GitHubService) -> None:
    await github_service.create_user_token(test_user.user_id, '123')
    with pytest.raises(github_exc.GitHubIntegrationExistsError):
        await github_service.create_user_token(test_user.user_id, '123')

@pytest.mark.asyncio
async def test_exists_integration_by_user_id_if_integration_exists(test_user: User, github_service: GitHubService) -> None:
    await github_service.create_user_token(test_user.user_id, '123')
    assert await github_service.exists_integration_by_user_id(test_user.user_id) == True

@pytest.mark.asyncio
async def test_exists_integration_by_user_id_if_integration_does_not_exists(test_user: User, github_service: GitHubService) -> None:
    assert await github_service.exists_integration_by_user_id(test_user.user_id) == False

@pytest.mark.asyncio
async def test_update_user_token(test_user: User, github_service: GitHubService) -> None:
    await github_service.create_user_token(test_user.user_id, '123')
    integration = await github_service.update_user_token(test_user.user_id, '1234')
    assert integration.access_token == '1234'

@pytest.mark.asyncio
async def test_update_user_token_but_integration_does_not_exists(test_user: User, github_service: GitHubService) -> None:
    with pytest.raises(github_exc.GitHubIntegrationDoesNotExistsError):
        await github_service.update_user_token(test_user.user_id, '1234')

@pytest.mark.asyncio
async def test_delete_user_token(test_user: User, github_service: GitHubService) -> None:
    await github_service.create_user_token(test_user.user_id, '123')
    assert await github_service.delete(test_user.user_id) == None

@pytest.mark.asyncio
async def test_delete_user_token_but_integration_does_not_exists(test_user: User, github_service: GitHubService) -> None:
    with pytest.raises(github_exc.GitHubIntegrationDoesNotExistsError):
        await github_service.delete(test_user.user_id)

@pytest.mark.asyncio
async def test_get_acceess_token_by_user_id(test_user: User, github_service: GitHubService) -> None:
    await github_service.create_user_token(test_user.user_id, '123')
    assert await github_service._get_access_token_by_user_id(test_user.user_id) == '123'

@pytest.mark.asyncio
async def test_get_access_token_by_user_id_but_github_integration_does_not_exists(test_user: User, github_service: GitHubService) -> None:
    with pytest.raises(github_exc.GitHubIntegrationDoesNotExistsError):
        await github_service._get_access_token_by_user_id(test_user.user_id)

@pytest.mark.asyncio
async def test_get_user_info(test_user: User, github_service: GitHubService) -> None:
    await github_service.create_user_token(test_user.user_id, '123')
    mock_response = MagicMock()
    mock_response.status_code == 200
    mock_response.json.return_value = {
        'id' : 12345,
        'login' : 'testuser',
        'name' : 'user',
        'email' : 'testuser@mail.com',
        'avatar_url' : 'http://12345/123',
        'public_repos' : 12,
        'bio' : 'frontend developer',
        'followers' : 123,
        'following' : 15
    }
    mock_response.raise_for_status.return_value = None

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client

    with patch('httpx.AsyncClient', return_value = mock_client):
        res = await github_service.get_user_info(test_user.user_id)
    assert isinstance(res, GitHubUserInfo)
    assert res.login == 'testuser'
    assert res.bio == 'frontend developer'
    assert res.name == 'user'
    assert res.email == 'testuser@mail.com'

@pytest.mark.asyncio
async def test_get_user_info_but_status_code_is_401(test_user: User, github_service: GitHubService) -> None:
    await github_service.create_user_token(test_user.user_id, '123')

    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.raise_for_status.return_value = None

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client

    with patch('httpx.AsyncClient', return_value = mock_client):
        with pytest.raises(github_exc.InvalidOrExpiredGitHubTokenError):
            await github_service.get_user_info(test_user.user_id)

@pytest.mark.asyncio
async def test_get_user_info_but_another_status_code(test_user: User, github_service: GitHubService) -> None:
    await github_service.create_user_token(test_user.user_id, '123')

    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.raise_for_status.side_effect = HTTPStatusError('ERROR', request = MagicMock(), response = MagicMock())

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client

    with patch('httpx.AsyncClient', return_value = mock_client):
        with pytest.raises(HTTPStatusError):
            await github_service.get_user_info(test_user.user_id)
