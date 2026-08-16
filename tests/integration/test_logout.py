import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_logout_with_invalid_access_token(client: AsyncClient) -> None:
    headers = {'Authorization': f'Bearer invalidaccesstoken'}
    logout_response = await client.post('/v1/auth/logout', headers = headers)
    assert logout_response.status_code == 401
