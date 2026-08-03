import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services import GitHubService
from app.schemas import GitHubTokenResponse, GitHubUserInfo
from app.models import User
from app.exceptions import github as github_exc

STATUS_TO_EXCEPTION = {
    304: github_exc.GitHubNotModified304Error,
    400: github_exc.GitHubBadRequest400Error,
    401: github_exc.GitHubNotAuthentificated401Error,
    403: github_exc.GitHubForbidden403Error,
    404: github_exc.GitHubResourceNotFound404Error,
    409: github_exc.GitHubConflict409Error,
    422: github_exc.GitHubValidation422Error,
    500: github_exc.GitHubInternal500Error,
    503: github_exc.GitHubUnavailable503Error
}

@pytest.mark.asyncio
async def test_exchange_code_for_token(github_service: GitHubService) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'access_token' : 'token',
        'token_type' : 'bearer',
        'scope' : 'scope'
    }
    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    with patch('httpx.AsyncClient', return_value = mock_client):
        res = await github_service.exchange_code_for_token('code')
    assert isinstance(res, GitHubTokenResponse)
    assert res.access_token == 'token'
    assert res.token_type == 'bearer'
    assert res.scope == 'scope'

@pytest.mark.asyncio
async def test_exchange_code_for_token_but_without_access_token_and_error(github_service: GitHubService) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'message' : 'this is some unknown error that returns a 200 status code but does not return a token'
    }
    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    with patch('httpx.AsyncClient', return_value = mock_client):
        with pytest.raises(github_exc.GitHubError):
            await github_service.exchange_code_for_token('code')

@pytest.mark.asyncio
@pytest.mark.parametrize('status_code, excepted_exception', [(status_code, exc) for status_code, exc in STATUS_TO_EXCEPTION.items()])
async def test_exchange_code_for_token_but_http_errors(github_service: GitHubService, status_code: int, excepted_exception: Exception) -> None:
    mock_response = MagicMock()
    mock_response.json.return_value = {'message': 'error'}
    mock_response.status_code = status_code

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    with patch('httpx.AsyncClient', return_value = mock_client):
        with pytest.raises(excepted_exception):
            await github_service.exchange_code_for_token('code')

@pytest.mark.asyncio
async def test_exchange_code_for_token_but_unknown_http_error(github_service: GitHubService) -> None:
    mock_response = MagicMock()
    mock_response.json.return_value = {'message': 'unknown error'}
    mock_response.status_code = 1234

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    with patch('httpx.AsyncClient', return_value = mock_client):
        with pytest.raises(github_exc.GitHubUnknownAPIError):
            await github_service.exchange_code_for_token('code')

@pytest.mark.asyncio
async def test_create_user_token(test_user: User, github_service: GitHubService) -> None:
    integration = await github_service.create_user_token(test_user.user_id, 'token')
    assert integration.user_id == test_user.user_id
    assert integration.access_token == 'token'

@pytest.mark.asyncio
async def test_create_user_token_but_integration_is_exists(test_user: User, github_service: GitHubService) -> None:
    await github_service.create_user_token(test_user.user_id, 'token')
    with pytest.raises(github_exc.GitHubIntegrationExistsError):
        await github_service.create_user_token(test_user.user_id, 'token2')

@pytest.mark.asyncio
async def test_update_user_token(test_user: User, github_service: GitHubService) -> None:
    await github_service.create_user_token(test_user.user_id, 'token1')
    updated_integration = await github_service.update_user_token(test_user.user_id, 'newtoken2')
    assert updated_integration.access_token == 'newtoken2'

@pytest.mark.asyncio
async def test_update_user_token_but_integration_does_not_exists(test_user: User, github_service: GitHubService) -> None:
    with pytest.raises(github_exc.GitHubIntegrationDoesNotExistsError):
        await github_service.update_user_token(test_user.user_id, '123')

@pytest.mark.asyncio
async def test_update_github_username(test_user: User, github_service: GitHubService) -> None:
    await github_service.create_user_token(test_user.user_id, 'token')
    integration = await github_service._update_github_username(test_user.user_id, 'newgithubusername')
    assert integration.github_username == 'newgithubusername'

@pytest.mark.asyncio
async def test_update_github_username_but_integration_does_not_exists(test_user: User, github_service: GitHubService) -> None:
    with pytest.raises(github_exc.GitHubIntegrationDoesNotExistsError):
        await github_service._update_github_username(test_user.user_id, 'newgithubusername')

@pytest.mark.asyncio
async def test_delete_integration(test_user: User, github_service: GitHubService) -> None:
    await github_service.create_user_token(test_user.user_id, '123')
    assert await github_service.delete(test_user.user_id) == None

@pytest.mark.asyncio
async def test_delete_integration_but_integration_does_not_exists(test_user: User, github_service: GitHubService) -> None:
    with pytest.raises(github_exc.GitHubIntegrationDoesNotExistsError):
        await github_service.delete(test_user.user_id)

@pytest.mark.asyncio
async def test_get_access_token_by_user_id(test_user: User, github_service: GitHubService) -> None:
    await github_service.create_user_token(test_user.user_id, '123')
    assert await github_service._get_access_token_by_user_id(test_user.user_id) == '123'

@pytest.mark.asyncio
async def test_get_access_token_by_user_id_but_integration_does_not_exists(test_user: User, github_service: GitHubService) -> None:
    with pytest.raises(github_exc.GitHubIntegrationDoesNotExistsError):
        await github_service._get_access_token_by_user_id(test_user.user_id)

@pytest.mark.asyncio
async def test_get_github_username(test_user: User, github_service: GitHubService) -> None:
    await github_service.create_user_token(test_user.user_id, 'token')

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'login': 'github_testuser'}

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    with patch('httpx.AsyncClient', return_value = mock_client):
        res = await github_service._get_github_username(test_user.user_id)
    assert res == 'github_testuser'

@pytest.mark.asyncio
async def test_get_github_username_but_integration_does_not_exists(test_user: User, github_service: GitHubService) -> None:
    with pytest.raises(github_exc.GitHubIntegrationDoesNotExistsError):
        await github_service._get_github_username(test_user.user_id)

@pytest.mark.asyncio
async def test_get_github_username_but_login_not_in_response(test_user: User, github_service: GitHubService) -> None:
    await github_service.create_user_token(test_user.user_id, '123')

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'message': 'this is some unknown error that returns a 200 status code, but returns a response without a login'}

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client

    with patch('httpx.AsyncClient', return_value = mock_client):
        with pytest.raises(github_exc.LoginNotInResponseError):
            await github_service._get_github_username(test_user.user_id)

@pytest.mark.asyncio
@pytest.mark.parametrize('status_code, excepted_exception', [(status_code, exc) for status_code, exc in STATUS_TO_EXCEPTION.items()])
async def test_get_github_username_but_http_errors(test_user: User, github_service: GitHubService, status_code: str, excepted_exception: Exception) -> None:
    await github_service.create_user_token(test_user.user_id, '123')

    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.json.return_value = {'message': 'error'}

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client

    with patch('httpx.AsyncClient', return_value = mock_client):
        with pytest.raises(excepted_exception):
            await github_service._get_github_username(test_user.user_id)

@pytest.mark.asyncio
async def test_get_ensure_github_username(test_user: User, github_service: GitHubService) -> None:
    await github_service.create_user_token(test_user.user_id, 'token')
    github_service._get_github_username = AsyncMock(return_value = 'githubtestuser')
    res = await github_service._get_ensure_current_github_username(test_user.user_id)
    assert res == 'githubtestuser'

@pytest.mark.asyncio
async def test_get_ensure_github_username_but_integration_does_not_exists(test_user: User, github_service: GitHubService) -> None:
    with pytest.raises(github_exc.GitHubIntegrationDoesNotExistsError):
        await github_service._get_ensure_current_github_username(test_user.user_id)

@pytest.mark.asyncio
async def test_get_user_info(test_user: User, github_service: GitHubService) -> None:
    await github_service.create_user_token(test_user.user_id, 'token')
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'login' : 'userlogin',
        'name' : 'user',
        'email' : 'testuser@mail.com',
        'avatar_url' : 'avatar_url',
        'bio' : 'frontend developer',
        'public_repos' : 12,
        'followers' : 22,
        'following' : 15
    }
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    with patch('httpx.AsyncClient', return_value = mock_client):
        res = await github_service.get_user_info(test_user.user_id)
    assert isinstance(res, GitHubUserInfo)
    assert res.login == 'userlogin'
    assert res.name == 'user'
    assert res.email == 'testuser@mail.com'


@pytest.mark.asyncio
@pytest.mark.parametrize('status_code, excepted_error', [(status_code, exc) for status_code, exc in STATUS_TO_EXCEPTION.items()])
async def test_get_user_info_but_http_errors(test_user: User, github_service: GitHubService, status_code: int, excepted_error: Exception) -> None:
    await github_service.create_user_token(test_user.user_id, 'token')
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.json.return_value = {'message': 'error'}

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client

    with patch('httpx.AsyncClient', return_value = mock_client):
        with pytest.raises(excepted_error):
            await github_service.get_user_info(test_user.user_id)

@pytest.mark.asyncio
async def test_get_user_events(test_user: User, github_service: GitHubService) -> None:
    await github_service.create_user_token(test_user.user_id, 'token')
    github_service._get_ensure_current_github_username = AsyncMock(return_value = 'githubusername')
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{'event1': 'update readme'}, {'event2': 'sterred repository with name \"BEST README TEMPLATE\"'}]

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client

    with patch('httpx.AsyncClient', return_value = mock_client):
        await github_service.get_user_events(test_user.user_id)

@pytest.mark.asyncio
@pytest.mark.parametrize('status_code, excepted_error', [(status_code, exc) for status_code, exc in STATUS_TO_EXCEPTION.items()])
async def test_get_user_events_but_http_errors(test_user: User, github_service: GitHubService, status_code: int, excepted_error: Exception) -> None:
    await github_service.create_user_token(test_user.user_id, 'token')
    github_service._get_ensure_current_github_username = AsyncMock(return_value = 'githubusername')
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.json.return_value = {'message': 'error'}

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client

    with patch('httpx.AsyncClient', return_value = mock_client):
        with pytest.raises(excepted_error):
            await github_service.get_user_events(test_user.user_id)

@pytest.mark.asyncio
async def test_get_user_repositories(test_user: User, github_service: GitHubService) -> None:
    await github_service.create_user_token(test_user.user_id, 'token')
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{'repo1': 'testuser/testuser'}, {'repo2': 'testuser/crud-app'}]

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client

    with patch('httpx.AsyncClient', return_value = mock_client):
        await github_service.get_user_repositories(test_user.user_id)

@pytest.mark.asyncio
@pytest.mark.parametrize('status_code, excepted_error', [(status_code, exc) for status_code, exc in STATUS_TO_EXCEPTION.items()])
async def test_get_user_repositories_but_http_errors(test_user: User, github_service: GitHubService, status_code: int, excepted_error: Exception) -> None:
    await github_service.create_user_token(test_user.user_id, 'token')
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.json.return_value = {'message': 'error'}

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client

    with patch('httpx.AsyncClient', return_value = mock_client):
        with pytest.raises(excepted_error):
            await github_service.get_user_repositories(test_user.user_id)

@pytest.mark.asyncio
async def test_get_github_commits(test_user: User, github_service: GitHubService) -> None:
    await github_service.create_user_token(test_user.user_id, 'token')
    github_service._get_ensure_current_github_username = AsyncMock(return_value = 'githubtestusername')
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{'commit1': 'githubtestusername/githubtestusername'}, {'commit2': 'githubtestusername/githubtestusername'}]

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client

    with patch('httpx.AsyncClient', return_value = mock_client):
        await github_service.get_github_commits(test_user.user_id, 'githubtestusername')

@pytest.mark.asyncio
@pytest.mark.parametrize('status_code, excepted_error', [(status_code, exc) for status_code, exc in STATUS_TO_EXCEPTION.items()])
async def test_get_github_commits_but_http_errors(test_user: User, github_service: GitHubService, status_code: int, excepted_error: Exception) -> None:
    await github_service.create_user_token(test_user.user_id, 'token')
    github_service._get_ensure_current_github_username = AsyncMock(return_value = 'githubtestusername')
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.json.return_value = {'message': 'error'}

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client

    with patch('httpx.AsyncClient', return_value = mock_client):
        with pytest.raises(excepted_error):
            await github_service.get_github_commits(test_user.user_id, 'repo')

@pytest.mark.asyncio
async def test_get_repository_pulls(test_user: User, github_service: GitHubService) -> None:
    await github_service.create_user_token(test_user.user_id, 'token')
    github_service._get_ensure_current_github_username = AsyncMock(return_value = 'githubtestusername')
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{'pull1': '12.03.2024'}, {'pull2': '13.02.2025'}]

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client

    with patch('httpx.AsyncClient', return_value = mock_client):
        await github_service.get_repository_pulls(test_user.user_id, 'repo')

@pytest.mark.asyncio
@pytest.mark.parametrize('status_code, excepted_error', [(status_code, exc) for status_code, exc in STATUS_TO_EXCEPTION.items()])
async def test_get_repository_pulls_but_http_errors(test_user: User, github_service: GitHubService, status_code: int, excepted_error: Exception) -> None:
    await github_service.create_user_token(test_user.user_id, 'token')
    github_service._get_ensure_current_github_username = AsyncMock(return_value = 'githubtestuser')
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.json.return_value = {'message': 'error'}

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client

    with patch('httpx.AsyncClient', return_value = mock_client):
        with pytest.raises(excepted_error):
            await github_service.get_repository_pulls(test_user.user_id, 'repo')

@pytest.mark.asyncio
async def test_get_repository_issues(test_user: User, github_service: GitHubService) -> None:
    await github_service.create_user_token(test_user.user_id, 'token')
    github_service._get_ensure_current_github_username = AsyncMock(return_value = 'githubtestuser')
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{'repo': 'issue1'}, {'repo': 'issue2'}]

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client

    with patch('httpx.AsyncClient', return_value = mock_client):
        await github_service.get_repository_issues(test_user.user_id, 'repo')

@pytest.mark.asyncio
@pytest.mark.parametrize('status_code, excepted_error', [(status_code, exc) for status_code, exc in STATUS_TO_EXCEPTION.items()])
async def test_get_repository_issues_but_http_errors(test_user: User, github_service: GitHubService, status_code: int, excepted_error: Exception) -> None:
    await github_service.create_user_token(test_user.user_id, 'token')
    github_service._get_ensure_current_github_username = AsyncMock(return_value = 'githubtestuser')
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.json.return_value = {'message': 'error'}

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client

    with patch('httpx.AsyncClient', return_value = mock_client):
        with pytest.raises(excepted_error):
            await github_service.get_repository_issues(test_user.user_id, 'repo')
