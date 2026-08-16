import redis.asyncio as redis
from typing import Optional
from app.core.config import settings

class RedisClient:
    _client: Optional[redis.Redis] = None

    @classmethod
    async def get_client(cls) -> Optional[redis.Redis]:
        if cls._client is None:
            cls._client = redis.from_url(
                url = settings.REDIS_URL,
                decode_responses = True,
                max_connections = 10
            )
            await cls._client.ping()
        return cls._client

    @classmethod
    async def close(cls) -> None:
        if cls._client:
            await cls._client.close()
            cls._client = None
    