from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_URL: str

    REDIS_URL: str

    DEBUG: bool

    SLOW_REQUEST_THRESHOLD: float

    SECRET_JWT_KEY: str
    ALGORITHM: str
    JWT_TOKEN_EXPIRE_MINUTES: int

    model_config = ConfigDict(env_file = '.env', case_sensitive = True)

settings = Settings()
