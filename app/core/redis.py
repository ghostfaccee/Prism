import redis.asyncio as redis
from app.core import settings

_redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses = True,
    socket_connect_timeout = 5,
    socket_timeout = 5
)


async def get_redis() -> redis.Redis: # dependency for getting a redis client
    return _redis_client
