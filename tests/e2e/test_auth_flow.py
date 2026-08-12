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

@pytest.mark.asyncio
async def test_refresh_token_flow(client: AsyncClient, register_user_without_email: tuple) -> None:
    username, password = register_user_without_email
    login_response = await client.post('/v1/auth/login', json = {'username': username, 'password': password})
    assert login_response.status_code == 200
    login_data = login_response.json()

    refresh_response = await client.post('/v1/auth/refresh', json = {'refresh_token': login_data['refresh_token']})
    assert refresh_response.status_code == 200

    refresh_data = refresh_response.json()
    assert refresh_data['access_token'] is not None and refresh_data['access_token'] != ''
    assert refresh_data['refresh_token'] is not None and refresh_data['refresh_token'] != ''

@pytest.mark.asyncio
async def test_refresh_token_but_with_old_refresh_token(client: AsyncClient, register_user_without_email: tuple) -> None:
    username, password = register_user_without_email
    login_response = await client.post('/v1/auth/login', json = {'username': username, 'password': password})
    assert login_response.status_code == 200
    login_data = login_response.json()

    refresh_token = login_data['refresh_token']
    refresh_response = await client.post('/v1/auth/refresh', json = {'refresh_token': refresh_token})
    assert refresh_response.status_code == 200

    refresh_response_with_old_refresh_token = await client.post('/v1/auth/refresh', json = {'refresh_token': refresh_token})
    assert refresh_response_with_old_refresh_token.status_code == 403

@pytest.mark.asyncio
async def test_logout_flow(client: AsyncClient, register_user_without_email: tuple) -> None:
    username, password = register_user_without_email
    login_response = await client.post('/v1/auth/login', json = {'username': username, 'password': password})
    assert login_response.status_code == 200
    login_data = login_response.json()

    refresh_token = login_data['refresh_token']
    access_token = login_data['access_token']

    headers = {'Authorization': f'Bearer {access_token}'}
    logout_response = await client.post('/v1/auth/logout', headers = headers)
    assert logout_response.status_code == 204

    refresh_response = await client.post('/v1/auth/refresh', json = {'refresh_token': refresh_token})
    assert refresh_response.status_code == 400

