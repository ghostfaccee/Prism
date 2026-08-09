from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import Optional
from fastapi import Request
from app.core.config import settings
from app.exceptions import rate_limit as rate_limit_exc

class RateLimit:
    _enabled_redis = True
    _limiter: Optional[Limiter] = None

    @classmethod
    def disable_redis(cls):
        cls._enabled_redis = False

    @classmethod
    def get_limiter(cls):
        if not cls._limiter:
            if not cls._enabled_redis:
                cls._limiter = Limiter(
                    key_func = get_remote_address,
                    enabled = False # Disabling limits for tests
                )
            else:
                cls._limiter = Limiter(
                    key_func = get_remote_address,
                    storage_uri = settings.REDIS_URL,
                    default_limits = ['20/minute']
                )
        return cls._limiter

    @staticmethod
    def rate_limit_exceed_handler(request: Request, exc: RateLimitExceeded):
        raise rate_limit_exc.RateLimitExceedError()
