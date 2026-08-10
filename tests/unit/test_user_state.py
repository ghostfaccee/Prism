import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from app.models import User
from app.exceptions import user as user_exc
from app.exceptions import state as state_exc
from app.services import UserService
from app.infrastructure import GitHubStateService, StateCheckResult

@pytest.mark.asyncio
async def test_setup_new_state(test_user: User, user_service: UserService) -> None:
    state = 'teststate'
    with patch.object(GitHubStateService, 'set_state', new = AsyncMock(return_value = True)):
        res = await user_service.setup_new_state(test_user.user_id, state)
    assert res is True

@pytest.mark.asyncio
async def test_setup_new_state_but_user_does_not_exists(user_service: UserService) -> None:
    with pytest.raises(user_exc.UserDoesNotExists):
        await user_service.setup_new_state(uuid4(), 'teststate')

@pytest.mark.asyncio
async def test_setup_new_srate_but_redis_error(test_user: User, user_service: UserService) -> None:
    state = 'teststate'
    with patch.object(GitHubStateService, 'set_state', new = AsyncMock(return_value = False)):
        with pytest.raises(state_exc.SetupStateError):
            await user_service.setup_new_state(test_user.user_id, state)

@pytest.mark.asyncio
async def test_check_state(test_user: User, user_service: UserService) -> None:
    state = 'teststate'
    with patch.object(GitHubStateService, 'check_state', new = AsyncMock(return_value = StateCheckResult.SUCCESS)):
        await user_service.check_state(test_user.user_id, state)

@pytest.mark.asyncio
async def test_check_state_but_user_does_not_exists(user_service: UserService) -> None:
    with pytest.raises(user_exc.UserDoesNotExists):
        await user_service.check_state(uuid4(), 'teststate')


@pytest.mark.asyncio
async def test_check_state_but_state_not_found(test_user: User, user_service: UserService) -> None:
    state = 'teststate'
    with patch.object(GitHubStateService, 'check_state', new = AsyncMock(return_value = StateCheckResult.NOT_FOUND)):
        with pytest.raises(state_exc.StateExpiredError):
            await user_service.check_state(test_user.user_id, state)

@pytest.mark.asyncio
async def test_check_state_but_csrf_attack(test_user: User, user_service: UserService) -> None:
    state = 'teststate'
    with patch.object(GitHubStateService, 'check_state', new = AsyncMock(return_value = StateCheckResult.MISMATCH)):
        with pytest.raises(state_exc.InvalidStateError):
            await user_service.check_state(test_user.user_id, state)