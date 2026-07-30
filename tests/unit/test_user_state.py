import pytest
from uuid import uuid4
from app.models import User
from app.exceptions import user as user_exc
from app.exceptions import state as state_exc
from app.services import UserService
from datetime import datetime, timezone, timedelta

@pytest.mark.asyncio
async def test_setup_new_state(test_user: User, user_service: UserService) -> None:
    state = 'teststate'
    expire = datetime.now(timezone.utc).replace(tzinfo = None) + timedelta(minutes = 10)
    result = await user_service.setup_new_state(test_user.user_id, state, expire)
    assert result == True

@pytest.mark.asyncio
async def test_setup_new_state_but_user_does_not_exists(user_service: UserService) -> None:
    with pytest.raises(user_exc.UserDoesNotExists):
        await user_service.setup_new_state(uuid4(), 'teststate', datetime.now(timezone.utc).replace(tzinfo = None) + timedelta(minutes = 10))

@pytest.mark.asyncio
async def test_check_state(test_user_with_state: User, user_service: UserService) -> None:
    assert await user_service.check_state(test_user_with_state.user_id, 'teststate') == True

@pytest.mark.asyncio
async def test_check_state_but_user_does_not_exists(user_service: UserService) -> None:
    with pytest.raises(user_exc.UserDoesNotExists):
        await user_service.check_state(uuid4(), 'teststate') 

@pytest.mark.asyncio
async def test_check_state_but_state_is_none(test_user_with_state: User, user_service: UserService) -> None:
    with pytest.raises(state_exc.InvalidStateError):
        await user_service.check_state(test_user_with_state.user_id, None)

@pytest.mark.asyncio
async def test_check_state_but_csrf_attack(test_user_with_state: User, user_service: UserService) -> None:
    with pytest.raises(state_exc.InvalidStateError):
        await user_service.check_state(test_user_with_state.user_id, 'anotherstate')

@pytest.mark.asyncio
async def test_check_state_but_state_expired(test_user: User, user_service: UserService) -> None:
    assert await user_service.setup_new_state(test_user.user_id, 'teststate', datetime.now(timezone.utc).replace(tzinfo = None))
    with pytest.raises(state_exc.StateExpiredError):
        await user_service.check_state(test_user.user_id, 'teststate')
