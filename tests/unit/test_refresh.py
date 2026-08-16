import pytest
from app.models import User
from app.services import AuthService
from app.schemas import UserLogin, TokenResponse
from app.exceptions import user as user_exc
from app.exceptions import internal as internal_exc
from app.exceptions import token as token_exc
from app.infrastructure import TokenService, TokenServiceReturnValues
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_login_return_values(test_user: User, auth_service: AuthService) -> None:
    token_response = await auth_service.login(UserLogin(username = test_user.username, password = 'testpass123'))
    assert token_response.refresh_token is not None or token_response.refresh_token != ''
    assert token_response.access_token is not None or token_response.access_token != ''
    assert token_response.token_type == 'bearer'
    assert token_response.access_token_expires_in_minutes is not None and token_response.access_token_expires_in_minutes != 0
    assert token_response.refresh_token_expires_in_days is not None and token_response.refresh_token_expires_in_days != 0

@pytest.mark.asyncio
async def test_refresh(test_user: User, auth_service: AuthService) -> None:
    login_response = await auth_service.login(UserLogin(username = test_user.username, password = 'testpass123'))
    token_response = await auth_service.refresh(login_response.refresh_token)
    assert isinstance(token_response, TokenResponse)
    assert token_response.refresh_token is not None and token_response.refresh_token != ''
    assert token_response.access_token is not None and token_response.access_token != ''

@pytest.mark.asyncio
async def test_refresh_but_invalid_refresh_token(auth_service: AuthService) -> None:
    with pytest.raises(user_exc.InvalidOrExpiredTokenError):
        await auth_service.refresh('invalidrefreshtoken')

@pytest.mark.asyncio
async def test_refresh_but_token_in_blacklist(refresh_token: str, auth_service: AuthService) -> None:
    with patch.object(TokenService, 'in_blacklist', AsyncMock(return_value = TokenServiceReturnValues.SUCCESS)):
        with pytest.raises(user_exc.BlacklistTokenError):
            await auth_service.refresh(refresh_token)

@pytest.mark.asyncio
async def test_refresh_but_get_refresh_token_with_internal_redis_error(refresh_token: str, auth_service: AuthService) -> None:
    with patch.object(TokenService, 'get_refresh_token', AsyncMock(return_value = None)):
        with pytest.raises(internal_exc.InternalRedisError):
            await auth_service.refresh(refresh_token)

@pytest.mark.asyncio
async def test_refresh_but_get_refresh_token_with_not_found(refresh_token: str, auth_service: AuthService) -> None:
    with patch.object(TokenService, 'get_refresh_token', AsyncMock(return_value = '0')):
        with pytest.raises(token_exc.TokenNotFoundError):
            await auth_service.refresh(refresh_token)

@pytest.mark.asyncio
async def test_refresh_but_get_refresh_token_and_refresh_token_is_different(refresh_token: str, auth_service: AuthService) -> None:
    with patch.object(TokenService, 'get_refresh_token', AsyncMock(return_value = 'anothertoken')):
        with pytest.raises(user_exc.InvalidOrExpiredTokenError):
            await auth_service.refresh(refresh_token)

@pytest.mark.asyncio
async def test_refresh_but_add_to_blacklist_with_error(refresh_token: str, auth_service: AuthService) -> None:
    with patch.object(TokenService, 'add_to_blacklist', AsyncMock(return_value = False)):
        with pytest.raises(internal_exc.InternalRedisError):
            await auth_service.refresh(refresh_token)

@pytest.mark.asyncio
async def test_refresh_but_store_refresh_token_with_error(refresh_token: str, auth_service: AuthService) -> None:
    with patch.object(TokenService, 'store_refresh_token', AsyncMock(return_value = False)):
        with pytest.raises(internal_exc.InternalRedisError):
            await auth_service.refresh(refresh_token)

@pytest.mark.asyncio
async def test_logout_but_redis_error(test_user: User, auth_service: AuthService) -> None:
    with patch.object(TokenService, 'delete_refresh_token', AsyncMock(return_value = TokenServiceReturnValues.ERROR)):
        with pytest.raises(internal_exc.InternalRedisError):
            await auth_service.logout(test_user.user_id)

@pytest.mark.asyncio
async def test_logout_but_not_found(test_user: User, auth_service: AuthService) -> None:
    with patch.object(TokenService, 'delete_refresh_token', AsyncMock(return_value = TokenServiceReturnValues.NOT_FOUND)):
        with pytest.raises(token_exc.TokenNotFoundError):
            await auth_service.logout(test_user.user_id)

@pytest.mark.asyncio
async def test_logout(test_user: User, auth_service: AuthService) -> None:
    with patch.object(TokenService, 'delete_refresh_token', AsyncMock(return_value = TokenServiceReturnValues.SUCCESS)):
        await auth_service.logout(test_user.user_id)
