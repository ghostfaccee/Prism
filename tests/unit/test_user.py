import pytest
from uuid import uuid4
from unittest.mock import patch
from app.models import User
from app.services import UserService
from app.schemas import UserUpdate, UpdatePassword
from app.exceptions import user as user_exc
from app.utils import verify_password

@pytest.mark.asyncio
async def test_get_user_by_id(test_user: User, user_service: UserService) -> None:
    user = await user_service.get_by_id(test_user.user_id)
    assert user.username == test_user.username

@pytest.mark.asyncio
async def test_get_user_by_id_error(user_service: UserService) -> None:
    with pytest.raises(user_exc.UserDoesNotExists):
        await user_service.get_by_id(uuid4())

@pytest.mark.asyncio
async def test_get_user_by_username(test_user: User, user_service: UserService) -> None:
    user = await user_service.get_by_username(test_user.username)
    assert user.username == test_user.username

@pytest.mark.asyncio
async def test_get_user_by_username_error(user_service: UserService) -> None:
    with pytest.raises(user_exc.UsernameDoesNotExistsError):
        await user_service.get_by_username('this_username_definitely_doesn\'t_have_an_owner')

@pytest.mark.asyncio
async def test_update_user(test_user: User, user_service: UserService) -> None:
    with patch('app.services.user.send_verification_email.delay'):
        updated_user = await user_service.update_user(test_user.user_id, UserUpdate(username = 'new_username', email = 'newemail@mail.com'))
    assert updated_user.username == 'new_username'
    assert updated_user.email == 'newemail@mail.com'

@pytest.mark.asyncio
async def test_update_user_without_email(test_user: User, user_service: UserService) -> None:
    updated_user = await user_service.update_user(test_user.user_id, UserUpdate(username = 'new_username'))
    assert updated_user.username == 'new_username'
    assert updated_user.email == 'testuser@mail.com'

@pytest.mark.asyncio
async def test_update_user_without_username(test_user: User, user_service: UserService) -> None:
    with patch('app.services.user.send_verification_email.delay'):
        updated_user = await user_service.update_user(test_user.user_id, UserUpdate(email = 'newemail@mail.com'))
    assert updated_user.email == 'newemail@mail.com'
    assert updated_user.username == 'testuser'

@pytest.mark.asyncio
async def test_update_user_without_all(test_user: User, user_service: UserService) -> None:
    updated_user = await user_service.update_user(test_user.user_id, UserUpdate())
    assert updated_user.username == 'testuser'
    assert updated_user.email == 'testuser@mail.com'

@pytest.mark.asyncio
async def test_update_user_but_user_id_does_not_exists_error(user_service: UserService) -> None:
    with pytest.raises(user_exc.UserDoesNotExists):
        await user_service.update_user(uuid4(), UserUpdate())

@pytest.mark.asyncio
async def test_update_user_but_username_already_taken(test_user: User, test_user2_for_test_user: User, user_service: UserService) -> None:
    with pytest.raises(user_exc.UsernameExistsError):
        await user_service.update_user(test_user.user_id, UserUpdate(username = test_user2_for_test_user.username))

@pytest.mark.asyncio
async def test_update_user_but_username_is_him(test_user: User, user_service: UserService) -> None:
    updated_user = await user_service.update_user(test_user.user_id, UserUpdate(username = test_user.username))
    assert updated_user.username == test_user.username

@pytest.mark.asyncio
async def test_update_user_but_username_is_string_with_spaces(test_user: User, user_service: UserService) -> None:
    updated_user = await user_service.update_user(test_user.user_id, UserUpdate(username = '     '))
    assert updated_user.username == test_user.username

@pytest.mark.asyncio
async def test_update_user_but_email_already_taken(test_user: User, test_user2_for_test_user: User, user_service: UserService) -> None:
    with pytest.raises(user_exc.EmailExistsError):
        await user_service.update_user(test_user.user_id, UserUpdate(email = test_user2_for_test_user.email))

@pytest.mark.asyncio
async def test_update_user_password(test_user: User, user_service: UserService) -> None:
    updated_user = await user_service.update_password(test_user.user_id, UpdatePassword(old_pass = 'testpass123', new_pass = 'newpass123'))
    assert verify_password('newpass123', updated_user.hashed_password)

@pytest.mark.asyncio
async def test_update_user_password_but_user_id_does_not_exists_error(user_service: UserService) -> None:
    with pytest.raises(user_exc.UserDoesNotExists):
        await user_service.update_password(uuid4(), UpdatePassword(old_pass = 'testpass123', new_pass = 'newpass1234'))

@pytest.mark.asyncio
async def test_update_user_password_but_old_password_is_invalid(test_user: User, user_service: UserService) -> None:
    with pytest.raises(user_exc.InvalidPassword):
        await user_service.update_password(test_user.user_id, UpdatePassword(old_pass = 'invalidpassword', new_pass = 'newpass'))

@pytest.mark.asyncio
async def test_delete_user(test_user: User, user_service: UserService) -> None:
    assert await user_service.delete(test_user.user_id) is None

@pytest.mark.asyncio
async def test_delete_user_but_user_does_not_exist(user_service: UserService) -> None:
    with pytest.raises(user_exc.UserDoesNotExists):
        await user_service.delete(uuid4())
