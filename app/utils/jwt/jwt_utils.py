from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.config import settings
from typing import Optional

def create_jwt_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes = settings.JWT_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, settings.SECRET_JWT_KEY, settings.ALGORITHM)

def decode_jwt_token(token: str) -> Optional[str]:
    try:
        return jwt.decode(token, settings.SECRET_JWT_KEY, settings.ALGORITHM)
    except JWTError:
        return None

