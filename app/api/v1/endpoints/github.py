import secrets
from uuid import UUID
from fastapi import APIRouter, Request, status, Depends
from app.dependencies import get_current_user_id, get_github_service, get_user_service, get_github_feed_service, get_current_user_id
from app.services import GitHubService, UserService, GitHubFeedService
from fastapi.responses import RedirectResponse
from app.schemas import GitHubCallbackResponse, GitHubUserInfo, GitHubFeedResponse
from app.core import settings
from app.middlewares import RateLimit
from app.infrastructure import CacheService

router = APIRouter()
limiter = RateLimit.get_limiter()

@router.get('/github/login', status_code = status.HTTP_307_TEMPORARY_REDIRECT, summary = 'GitHub login', description = 'Redirects the user to the GitHub login page. Requires a jwt token.')
@limiter.limit('5/minute')
async def github_login(request: Request, current_user_id: UUID = Depends(get_current_user_id), user_service: UserService = Depends(get_user_service)) -> RedirectResponse:
    state = secrets.token_urlsafe(16)
    await user_service.setup_new_state(current_user_id, state)
    github_auth_url = (
        'https://github.com/login/oauth/authorize?'
        f'client_id={settings.GITHUB_CLIENT_ID}&'
        f'redirect_uri={settings.GITHUB_REDIRECT_URI}&'
        f'scope=read:user,user:email,repo&'
        f'state={state}'
    )
    return RedirectResponse(github_auth_url)

@router.get('/github/callback', response_model = GitHubCallbackResponse, status_code = status.HTTP_200_OK, summary = 'GitHub redirect', description = 'Accepts the code from GitHub, exchanges it for a token, and stores it in the database. Requires a jwt token.')
@limiter.limit('5/minute')
async def github_callback(request: Request, code: str, state: str, current_user_id: UUID = Depends(get_current_user_id), user_service: UserService = Depends(get_user_service), github_service: GitHubService = Depends(get_github_service)) -> GitHubCallbackResponse:
    await user_service.check_state(current_user_id.user_id, state)
    token_data = await github_service.exchange_code_for_token(code)
    if await github_service.exists_integration_by_user_id(current_user_id):
        await github_service.update_user_token(current_user_id, token_data.access_token)
    else:
        await github_service.create_user_token(current_user_id, token_data.access_token)
    return GitHubCallbackResponse(
        token_type = token_data.token_type,
        scope = token_data.scope
    )

@router.get('/github/me', response_model = GitHubUserInfo, status_code = status.HTTP_200_OK, summary = 'Get github user info', description = 'Gets information about the user\'s GitHub account, if they have linked it. Requires a jwt token.')
@limiter.limit('5/minute')
@CacheService.cached(ttl = 180, namespace = 'github', user_id_field = 'current_user_id')
async def get_github_user_info(request: Request, current_user_id: UUID = Depends(get_current_user_id), service: GitHubService = Depends(get_github_service)) -> GitHubUserInfo:
    return await service.get_user_info(current_user_id)

@router.get('/github/events', status_code = status.HTTP_200_OK, summary = 'Get github events', description = 'Returns a list of events on GitHub. Requires a jwt token.')
@limiter.limit('5/minute')
@CacheService.cached(ttl = 180, namespace = 'github', user_id_field = 'current_user_id')
async def get_github_user_events(request: Request, current_user_id: UUID = Depends(get_current_user_id), service: GitHubService = Depends(get_github_service)) -> list:
    return await service.get_user_events(current_user_id)

@router.get('/github/repositories', status_code = status.HTTP_200_OK, summary = 'Get github repositories', description = 'Returns a list of repositories on GitHub. Requires a jwt token.')
@limiter.limit('5/minute')
@CacheService.cached(ttl = 180, namespace = 'github', user_id_field = 'current_user_id')
async def get_github_user_repositories(request: Request, current_user_id: UUID = Depends(get_current_user_id), service: GitHubService = Depends(get_github_service)) -> list:
    return await service.get_user_repositories(current_user_id)

@router.get('/github/{repo}/commits', status_code = status.HTTP_200_OK, summary = 'Get github commits', description = 'Returns a list of commits. Requires a jwt token.')
@limiter.limit('5/minute')
@CacheService.cached(ttl = 180, namespace = 'github', user_id_field = 'current_user_id', extra_fields = ['repo'])
async def get_github_repo_commits(request: Request, repo: str, current_user_id: UUID = Depends(get_current_user_id), service: GitHubService = Depends(get_github_service)) -> list:
    return await service.get_github_commits(current_user_id, repo)

@router.get('/github/{repo}/pulls', status_code = status.HTTP_200_OK, summary = 'Get github pulls', description = 'Returns a list of pulls. Requires a jwt token.')
@limiter.limit('5/minute')
@CacheService.cached(ttl = 180, namespace = 'github', user_id_field = 'current_user_id', extra_fields = ['repo'])
async def get_github_repo_pulls(request: Request, repo: str, current_user_id: UUID = Depends(get_current_user_id), service: GitHubService = Depends(get_github_service)) -> list:
    return await service.get_repository_pulls(current_user_id, repo)

@router.get('/github/{repo}/issues', status_code = status.HTTP_200_OK, summary = 'Get github issues', description = 'Return a list of issues. Requires a jwt token.')
@limiter.limit('5/minute')
@CacheService.cached(ttl = 180, namespace = 'github', user_id_field = 'current_user_id', extra_fields = ['repo'])
async def get_github_repo_issues(request: Request, repo: str, current_user_id: UUID = Depends(get_current_user_id), service: GitHubService = Depends(get_github_service)) -> list:
    return await service.get_repository_issues(current_user_id, repo)

@router.get('/github/feed', response_model = GitHubFeedResponse, status_code = status.HTTP_200_OK, summary = 'GitHub feed', description = 'Returns the GitHub feed. Requires a jwt token.')
@limiter.limit('5/minute')
@CacheService.cached(ttl = 180, namespace = 'github', user_id_field = 'current_user_id')
async def get_github_feed(request: Request, current_user_id: UUID = Depends(get_current_user_id), service: GitHubFeedService = Depends(get_github_feed_service)) -> GitHubFeedResponse:
    return await service.get_user_feed(current_user_id)
