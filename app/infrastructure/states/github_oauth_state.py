from uuid import UUID
from typing import Optional
from app.core import logger, RedisClient
from enum import Enum

class StateCheckResult(Enum):
    SUCCESS = 1
    MISMATCH = 0
    NOT_FOUND = -1

class GitHubStateService:
    PREFIX = 'oauth:state'
    TTL = 600 # 10 minutes

    @classmethod
    def _make_key(cls, user_id: UUID) -> str:
        return f'{cls.PREFIX}:{user_id}'

    @classmethod
    async def set_state(cls, user_id: UUID, state: str) -> bool:
        try:
            key = cls._make_key(user_id)
            redis = await RedisClient.get_client()
            await redis.set(key, state, ex = cls.TTL)
            return True
        except Exception as e:
            logger.error(f'State set error: {e}')
            return False

    @classmethod
    async def get_state(cls, user_id: UUID) -> Optional[str]:
        try:
            redis = await RedisClient.get_client()
            key = cls._make_key(user_id)
            data = await redis.get(key)
            if data is None: 
                return None
            return data
        except Exception as e:
            logger.error(f'State get error: {e}')
            return None

    @classmethod
    async def delete_state(cls, user_id: UUID) -> bool:
        try:
            redis = await RedisClient.get_client()
            key = cls._make_key(user_id)
            result = await redis.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f'State delete error: {e}')
            return False

    @classmethod
    async def check_state(cls, user_id: UUID, current_state: str) -> int:
        '''
        checks for the presence of state, verifies it, and deletes it
        
        return value:
            * -1 - state not found | errors
            * 0 - state mismatch (possible csrf attack)
            * 1 - success
        '''
        saved_state = await cls.get_state(user_id)
        if saved_state is None:
            return StateCheckResult.NOT_FOUND
        if saved_state != current_state:
            await cls.delete_state(user_id)
            return StateCheckResult.MISMATCH
        await cls.delete_state(user_id)
        return StateCheckResult.SUCCESS