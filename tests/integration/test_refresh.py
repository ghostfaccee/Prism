import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_refresh_with_invalid_token(client: AsyncClient) -> None:
    refresh_response = await client.post('/v1/auth/refresh', json = {'refresh_token': 'invalidrefreshtoken'})
    assert refresh_response.status_code == 404

@pytest.mark.asyncio
async def test_refresh_without_token(client: AsyncClient) -> None:
    refresh_response = await client.post('/v1/auth/refresh', json = {'refresh_token': ''})
    assert refresh_response.status_code == 404

