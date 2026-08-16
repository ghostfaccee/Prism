from uuid import UUID
from app.core import RedisClient, logger
from typing import Optional
from enum import Enum

class TokenServiceReturnValues(Enum):
    ERROR = -1
    NOT_FOUND = 0
    SUCCESS = 1

class TokenService:
    REFRESH_PREFIX = 'refresh_token'
    BLACKLIST_PREFIX = 'blacklist'

    @classmethod
    def _refresh_key(cls, user_id: UUID) -> str:
        return f'{cls.REFRESH_PREFIX}:{user_id}'

    @classmethod
    def _blacklist_key(cls, token: str) -> str:
        return f'{cls.BLACKLIST_PREFIX}:{token}'

    @classmethod
    async def store_refresh_token(cls, user_id: UUID, refresh_token: str, ttl: int) -> bool:
        '''
        saves the refresh token to redis

        return value: 
            * True - success
            * False - error
        '''
        try:
            redis = await RedisClient.get_client()
            key = cls._refresh_key(user_id)
            await redis.set(key, refresh_token, ex = ttl)
            return True
        except Exception as e:
            logger.error(f'Failed to store refresh token: {e}')
            return False

    @classmethod
    async def get_refresh_token(cls, user_id: UUID) -> Optional[str]:
        '''
        get a refresh token from redis

        return value:
            * None - error
            * 0 - not found
            * <token> - success 
        '''
        try:
            redis = await RedisClient.get_client()
            key = cls._refresh_key(user_id)
            token = await redis.get(key)
            if token is None:
                return '0'
            return token
        except Exception as e:
            logger.error(f'Failed to get refresh token: {e}')
            return None

    @classmethod
    async def delete_refresh_token(cls, user_id: UUID) -> int:
        '''
        removes the refresh token from redis

        return value:
            * -1 - error
            * 0 - not found
            * 1 - success
        '''
        try:
            redis = await RedisClient.get_client()
            key = cls._refresh_key(user_id)
            res = await redis.delete(key)
            if res == 0:
                return TokenServiceReturnValues.NOT_FOUND
            return TokenServiceReturnValues.SUCCESS
        except Exception as e:
            logger.error(f'Failed to delete refresh_token: {e}')
            return TokenServiceReturnValues.ERROR

    @classmethod
    async def add_to_blacklist(cls, token: str, ttl: int) -> bool:
        '''
        adds the token to the blacklist

        return value:
            * True - success
            * False - error
        '''
        try:
            redis = await RedisClient.get_client()
            key = cls._blacklist_key(token)
            await redis.set(key, '1', ex = ttl)
            return True
        except Exception as e:
            logger.error(f'Failed to add token to clacklist: {e}')
            return False

    @classmethod
    async def in_blacklist(cls, token: str) -> int:
        '''
        checks whether the token is in the blacklist

        return value:
            * -1 - error
            * 0 - not found
            * 1 - success
        '''
        try:
            redis = await RedisClient.get_client()
            key = cls._blacklist_key(token)
            res = await redis.get(key)
            if res is None:
                return TokenServiceReturnValues.NOT_FOUND
            return TokenServiceReturnValues.SUCCESS
        except Exception as e:
            logger.error(f'Failed to check in blacklist: {e}')
            return TokenServiceReturnValues.ERROR
