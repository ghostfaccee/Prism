from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.config import settings
from typing import Optional

def create_access_token(data: dict, expires: int = settings.JWT_TOKEN_EXPIRE_MINUTES) -> str:
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes = expires)
    to_encode.update({'exp': expire, 'type': 'access'})
    return jwt.encode(to_encode, settings.SECRET_JWT_KEY, settings.ALGORITHM)

def decode_access_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.SECRET_JWT_KEY, settings.ALGORITHM)
        if payload.get('type') != 'access':
            return None
        return payload
    except JWTError:
        return None

def create_refresh_token(data: dict, expires: int = settings.REFRESH_TOKEN_EXPIRE_DAYS) -> str:
    to_encode = data.copy()
    expire = datetime.now() + timedelta(days = expires)
    to_encode.update({'exp': expire, 'type': 'refresh'})
    return jwt.encode(to_encode, settings.SECRET_REFRESH_KEY, settings.ALGORITHM)

def decode_refresh_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.SECRET_REFRESH_KEY, settings.ALGORITHM)
        if payload.get('type') != 'refresh':
            return None
        return payload
    except JWTError:
        return None
