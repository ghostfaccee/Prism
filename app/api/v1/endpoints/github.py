import secrets
from fastapi import APIRouter, Request, status, Depends
from app.dependencies import get_current_user, get_github_service, get_user_service
from app.services import GitHubService, UserService
from fastapi.responses import RedirectResponse
from app.models import User
from app.schemas import GitHubCallbackResponse, GitHubUserInfo
from app.core import settings
from datetime import datetime, timezone, timedelta


router = APIRouter()

@router.get('/github/login', status_code = status.HTTP_307_TEMPORARY_REDIRECT, summary = 'GitHub login', description = 'Redirects the user to the GitHub login page. Requires a jwt token.')
async def github_login(request: Request, current_user: User = Depends(get_current_user), user_service: UserService = Depends(get_user_service)) -> RedirectResponse:
    state = secrets.token_urlsafe(16)
    expire = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes = 10)
    await user_service.setup_new_state(current_user.user_id, state, expire)
    github_auth_url = (
        'https://github.com/login/oauth/authorize?'
        f'client_id={settings.GITHUB_CLIENT_ID}&'
        f'redirect_uri={settings.GITHUB_REDIRECT_URI}&'
        f'scope=read:user,user:email,repo&'
        f'state={state}'
    )
    return RedirectResponse(github_auth_url)

@router.get('/github/callback', response_model = GitHubCallbackResponse, status_code = status.HTTP_200_OK, summary = 'GitHub redirect', description = 'Accepts the code from GitHub, exchanges it for a token, and stores it in the database. Requires a jwt token.')
async def github_callback(request: Request, code: str, state: str, current_user: User = Depends(get_current_user), user_service: UserService = Depends(get_user_service), github_service: GitHubService = Depends(get_github_service)) -> GitHubCallbackResponse:
    await user_service.check_state(current_user, state)
    token_data = await github_service.exchange_code_for_token(code)
    if await github_service.exists_integration_by_user_id(current_user.user_id):
        await github_service.update_user_token(current_user.user_id, token_data.access_token)
    else:
        await github_service.create_user_token(current_user.user_id, token_data.access_token)
    return GitHubCallbackResponse(
        token_type = token_data.token_type,
        scope = token_data.scope
    )

@router.get('/github/me', response_model = GitHubUserInfo, status_code = status.HTTP_200_OK, summary = 'Get github user info', description = 'Gets information about the user\'s GitHub account, if they have linked it. Requires a jwt token.')
async def get_github_user_info(request: Request, current_user: User = Depends(get_current_user), service: GitHubService = Depends(get_github_service)) -> GitHubUserInfo:
    return await service.get_user_info(current_user.user_id)
