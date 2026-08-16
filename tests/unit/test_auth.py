import pytest
from unittest.mock import patch
from app.schemas import UserRegister, UserLogin
from app.services import AuthService, VerificationService
from app.services.tests import UserTestsService
from app.models import User
from app.exceptions import user as user_exc
from app.utils import verify_password

@pytest.mark.asyncio
async def test_register_with_email(auth_service: AuthService) -> None:
    with patch('app.services.auth.send_verification_email.delay'):
        registered_user = await auth_service.register(UserRegister(username = 'username', email = 'username@mail.com', password = '123456'))
    assert registered_user.username == 'username'
    assert registered_user.email == 'username@mail.com'
    assert verify_password('123456', registered_user.hashed_password)
    assert registered_user.is_active == False
    assert registered_user.verification_token is not None

@pytest.mark.asyncio
async def test_register_without_email(auth_service: AuthService) -> None:
    registered_user = await auth_service.register(UserRegister(username = 'username', password = '123456'))
    assert registered_user.username == 'username'
    assert registered_user.email is None
    assert verify_password('123456', registered_user.hashed_password)
    assert registered_user.is_active == False
    assert registered_user.verification_token is None

@pytest.mark.asyncio
async def test_register_if_username_is_already_taken(test_user: User, auth_service: AuthService) -> None:
    with pytest.raises(user_exc.UsernameExistsError):
        await auth_service.register(UserRegister(username = test_user.username, password = '123456'))

@pytest.mark.asyncio
async def test_register_if_email_is_already_taken(test_user: User, auth_service: AuthService) -> None:
    with pytest.raises(user_exc.EmailExistsError):
        await auth_service.register(UserRegister(username = 'username', password = '123456', email = test_user.email))

@pytest.mark.asyncio
async def test_login(test_user: User, auth_service: AuthService) -> None:
    token_response = await auth_service.login(UserLogin(username = test_user.username, password = 'testpass123'))
    assert token_response.access_token is not None
    assert token_response.token_type is not None

@pytest.mark.asyncio
async def test_login_but_username_id_not_exists(auth_service: AuthService) -> None:
    with pytest.raises(user_exc.UsernameDoesNotExistsError):
        await auth_service.login(UserLogin(username = 'the_one_whose_name_cannot_be_mentioned', password = '123456'))

@pytest.mark.asyncio
async def test_login_but_invalid_password(test_user: User, auth_service: AuthService) -> None:
    with pytest.raises(user_exc.InvalidPassword):
        await auth_service.login(UserLogin(username = test_user.username, password = 'the_password_of_the_one_whose_name_cannot_be_mentioned'))

@pytest.mark.asyncio
async def test_verification(test_user: User, verification_service: VerificationService, user_tests_service: UserTestsService) -> None:
    updated_user = await verification_service.verify_email(await user_tests_service.get_verification_token_by_username(test_user.username))
    assert updated_user.is_active == True

@pytest.mark.asyncio
async def test_verification_but_token_is_invalid(verification_service: VerificationService):
    with pytest.raises(user_exc.InvalidOrExpiredTokenError):
        await verification_service.verify_email('the_token_belongs_to_someone_whose_name_cannot_be_revealed')

@pytest.mark.asyncio
async def test_verification_but_user_is_active(test_user: User, verification_service: VerificationService, user_tests_service: UserTestsService) -> None:
    await verification_service.verify_email(await user_tests_service.get_verification_token_by_username(test_user.username))
    with pytest.raises(user_exc.EmailAlreadyVerifiedError):
        await verification_service.verify_email(await user_tests_service.get_verification_token_by_username(test_user.username))
