import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.tests import UserTestsService
from app.core import settings

@pytest.mark.asyncio
async def test_full_auth_flow(client: AsyncClient, full_auth: str, db_session: AsyncSession) -> None:
    # we receive the user token required for verification
    headers = {"Authorization": f"Bearer {full_auth}"}
    me_response = await client.get('/v1/me', headers = headers)
    assert me_response.status_code == 200
    user_data = me_response.json()
    token = await UserTestsService(db_session).get_verification_token_by_username(user_data['username'])

    # follow the link for verification
    verify_response = await client.get(f'{settings.VERIFICATION_LINK}/{token}', headers = headers)
    assert verify_response.status_code == 200, 'Couldn\'t verify the user'

    