import pytest
from unittest.mock import patch
from httpx import AsyncClient
from app.services.tests import UserTestsService
from app.core import settings

@pytest.mark.asyncio
async def test_full_auth_flow(client: AsyncClient, full_auth: str, user_tests_service: UserTestsService) -> None:
    headers = {"Authorization": f"Bearer {full_auth}"}
    me_response = await client.get('/v1/me', headers = headers)
    assert me_response.status_code == 200, 'the user\'s data was not received'
    user_data = me_response.json()
    token = await user_tests_service.get_verification_token_by_username(user_data['username'])

    verify_response = await client.get(f'{settings.VERIFICATION_LINK}/{token}', headers = headers)
    assert verify_response.status_code == 200, 'Couldn\'t verify the user'

    with patch('app.services.user.send_verification_email.delay'):
        update_response = await client.patch('/v1/me', headers = headers, json = {'username' : 'newusername', 'email' : 'newemail@mail.com'})
    assert update_response.status_code == 200, 'Couldn\'t update the user'

    update_password_response = await client.patch('/v1/me/password', headers = headers, json = {'old_pass' : 'testpass123', 'new_pass' : 'newtestpass123'})
    assert update_password_response.status_code == 200, 'Couldn\'t update the user password'

@pytest.mark.asyncio
async def test_auth_without_email_flow(client: AsyncClient, auth_without_email: str, user_tests_service: UserTestsService) -> None:
    headers = {"Authorization": f"Bearer {auth_without_email}"}
    me_response = await client.get('/v1/me', headers = headers)
    assert me_response.status_code == 200, 'The user\'s data was not received'
    with patch('app.services.user.send_verification_email.delay'):
        me_update_response = await client.patch('/v1/me', headers = headers, json = {'email' : 'testuser@mail.com'})
    user_data = me_update_response.json()
    token = await user_tests_service.get_verification_token_by_username(user_data['username'])

    verify_response = await client.get(f'{settings.VERIFICATION_LINK}/{token}', headers = headers)
    assert verify_response.status_code == 200, 'Couldn\'t verify the user'

    with patch('app.services.user.send_verification_email.delay'):
        update_response = await client.patch('/v1/me', headers = headers, json = {'username' : 'newusername', 'email' : 'newemail@mail.com'})
    assert update_response.status_code == 200, 'Couldn\'t update the user'

    update_password_response = await client.patch('/v1/me/password', headers = headers, json = {'old_pass' : 'testpass123', 'new_pass' : 'newtestpass123'})
    assert update_password_response.status_code == 200, 'Couldn\'t update the user password'

