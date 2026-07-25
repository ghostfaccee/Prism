import pytest
from httpx import AsyncClient
from unittest.mock import patch
from app.utils import verify_password
from app.models import User
from app.services.tests import UserTestsService

@pytest.mark.asyncio
async def test_full_user_update(client: AsyncClient, full_auth: str) -> None:
    headers = {"Authorization": f"Bearer {full_auth}"}
    with patch('app.services.user.send_verification_email.delay'):
        user_response = await client.patch('/v1/me', headers = headers, json = {'username' : 'newuser', 'email' : 'newemail@mail.com'})
    assert user_response.status_code == 200
    updated_data = user_response.json()
    assert updated_data['username'] == 'newuser'
    assert updated_data['email'] == 'newemail@mail.com'

@pytest.mark.asyncio
async def test_full_user_update_without_email(client: AsyncClient, full_auth: str) -> None:
    headers = {"Authorization": f"Bearer {full_auth}"}
    user_response = await client.patch('/v1/me', headers = headers, json = {'username' : 'newuser'})
    assert user_response.status_code == 200
    updated_data = user_response.json()
    assert updated_data['username'] == 'newuser'
    assert updated_data['email'] == 'testuser@mail.com'

@pytest.mark.asyncio
async def test_full_user_update_without_username(client: AsyncClient, full_auth: str) -> None:
    headers = {"Authorization": f"Bearer {full_auth}"}
    with patch('app.services.user.send_verification_email.delay'):
        user_reponse = await client.patch('/v1/me', headers = headers, json = {'email' : 'newemail@mail.com'})
    assert user_reponse.status_code == 200
    updated_data = user_reponse.json()
    assert updated_data['username'] == 'testuser'
    assert updated_data['email'] == 'newemail@mail.com'

@pytest.mark.asyncio
async def test_full_user_update_without_all(client: AsyncClient, full_auth: str) -> None:
    headers = {"Authorization": f"Bearer {full_auth}"}
    user_response = await client.patch('/v1/me', headers = headers, json = {})
    assert user_response.status_code == 200
    updated_data = user_response.json()
    assert updated_data['username'] == 'testuser'
    assert updated_data['email'] == 'testuser@mail.com'

@pytest.mark.asyncio
async def test_user_without_email_update(client: AsyncClient, auth_without_email: str) -> None:
    headers = {"Authorization": f"Bearer {auth_without_email}"}
    with patch('app.services.user.send_verification_email.delay'):
        user_response = await client.patch('/v1/me', headers = headers, json = {'username' : 'newuser', 'email' : 'newemail@mail.com'})
    assert user_response.status_code == 200
    updated_data = user_response.json()
    assert updated_data['username'] == 'newuser'
    assert updated_data['email'] == 'newemail@mail.com'

@pytest.mark.asyncio
async def test_user_without_email_update_without_email(client: AsyncClient, auth_without_email: str) -> None:
    headers = {"Authorization": f"Bearer {auth_without_email}"}
    user_response = await client.patch('/v1/me', headers = headers, json = {'username' : 'newuser'})
    assert user_response.status_code == 200
    updated_data = user_response.json()
    assert updated_data['username'] == 'newuser'
    assert updated_data['email'] == None

@pytest.mark.asyncio
async def test_user_without_email_update_without_username(client: AsyncClient, auth_without_email: str) -> None:
    headers = {"Authorization": f"Bearer {auth_without_email}"}
    with patch('app.services.user.send_verification_email.delay'):
        user_response = await client.patch('/v1/me', headers = headers, json = {'email': 'newemail@mail.com'})
    assert user_response.status_code == 200
    updated_data = user_response.json()
    assert updated_data['username'] == 'testuser'
    assert updated_data['email'] == 'newemail@mail.com'

@pytest.mark.asyncio
async def test_user_without_email_update_without_all(client: AsyncClient, auth_without_email: str) -> None:
    headers = {"Authorization": f"Bearer {auth_without_email}"}
    user_response = await client.patch('/v1/me', headers = headers, json = {})
    assert user_response.status_code == 200
    updated_data = user_response.json()
    assert updated_data['username'] == 'testuser'
    assert updated_data['email'] == None

@pytest.mark.asyncio
async def test_full_user_update_password(client: AsyncClient, full_auth: str, user_tests_service: UserTestsService) -> None:
    headers = {"Authorization": f"Bearer {full_auth}"}
    user_response = await client.patch('/v1/me/password', headers = headers, json = {'old_pass' : 'testpass123', 'new_pass' : 'newpass123'})
    assert user_response.status_code == 200
    assert verify_password('newpass123', await user_tests_service.get_hashed_password_by_username(user_response.json()['username']))

@pytest.mark.asyncio
async def test_user_without_email_update_password(client: AsyncClient, auth_without_email: str, user_tests_service: UserTestsService) -> None:
    headers = {"Authorization": f"Bearer {auth_without_email}"}
    user_response = await client.patch('/v1/me/password', headers = headers, json = {'old_pass' : 'testpass123', 'new_pass' : 'newpass123'})
    assert user_response.status_code == 200
    assert verify_password('newpass123', await user_tests_service.get_hashed_password_by_username(user_response.json()['username']))

@pytest.mark.asyncio
async def test_get_full_user_by_jwt(client: AsyncClient, full_auth: str) -> None:
    headers = {'Authorization' : f'Bearer {full_auth}'}
    user_response = await client.get('/v1/me', headers = headers)
    assert user_response.status_code == 200
    user_data = user_response.json()
    assert user_data['username'] == 'testuser'
    assert user_data['email'] == 'testuser@mail.com'

@pytest.mark.asyncio
async def test_get_user_without_email_by_jwt(client: AsyncClient, auth_without_email: str) -> None:
    headers = {'Authorization' : f'Bearer {auth_without_email}'}
    user_response = await client.get('/v1/me', headers = headers)
    assert user_response.status_code == 200
    user_data = user_response.json()
    assert user_data['username'] == 'testuser'
    assert user_data['email'] == None

@pytest.mark.asyncio
async def test_get_another_user_by_username_with_user_without_email(client: AsyncClient, test_user2_for_test_user: User, auth_without_email: str) -> None:
    headers = {'Authorization' : f'Bearer {auth_without_email}'}
    user_response = await client.get(f'/v1/user/username/{test_user2_for_test_user.username}', headers = headers)
    assert user_response.status_code == 200
    user_data = user_response.json()
    assert user_data['username'] == 'testuser2'
    assert user_data['email'] == 'testuser2@mail.com'

@pytest.mark.asyncio
async def test_get_another_user_by_username_with_full_user(client: AsyncClient, test_user2_for_test_user: User, full_auth: str) -> None:
    headers = {'Authorization' : f'Bearer {full_auth}'}
    user_response = await client.get(f'/v1/user/username/{test_user2_for_test_user.username}', headers = headers)
    assert user_response.status_code == 200
    user_data = user_response.json()
    assert user_data['username'] == 'testuser2'
    assert user_data['email'] == 'testuser2@mail.com'

@pytest.mark.asyncio
async def test_get_another_user_by_uuid_with_user_without_email(client: AsyncClient, test_user2_for_test_user: User, auth_without_email: str) -> None:
    headers = {'Authorization' : f'Bearer {auth_without_email}'}
    user_response = await client.get(f'/v1/user/uuid/{test_user2_for_test_user.user_id}', headers = headers)
    assert user_response.status_code == 200
    user_data = user_response.json()
    assert user_data['username'] == 'testuser2'
    assert user_data['email'] == 'testuser2@mail.com'

@pytest.mark.asyncio
async def test_get_another_user_by_uuid_with_full_user(client: AsyncClient, test_user2_for_test_user: User, full_auth: str) -> None:
    headers = {'Authorization' : f'Bearer {full_auth}'}
    user_response = await client.get(f'/v1/user/uuid/{test_user2_for_test_user.user_id}', headers = headers)
    assert user_response.status_code == 200
    user_data = user_response.json()
    assert user_data['username'] == 'testuser2'
    assert user_data['email'] == 'testuser2@mail.com'

@pytest.mark.asyncio
async def test_delete_full_user(client: AsyncClient, full_auth: str) -> None:
    headers = {'Authorization' : f'Bearer {full_auth}'}
    user_response = await client.delete('/v1/me', headers = headers)
    assert user_response.status_code == 204

@pytest.mark.asyncio
async def test_delete_user_without_email(client: AsyncClient, auth_without_email: str) -> None:
    headers = {'Authorization' : f'Bearer {auth_without_email}'}
    user_response = await client.delete('/v1/me', headers = headers)
    assert user_response.status_code == 204
