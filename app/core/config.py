from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_URL: str = 'postgres url'

    TEST_POSTGRES_URL: str = Field(...)

    REDIS_URL: str = Field(...)
    DEFAULT_TTL: int = 300

    DEBUG: bool = True

    SLOW_REQUEST_THRESHOLD: float = 3.5

    SECRET_JWT_KEY: str = 'secretkey'
    SECRET_REFRESH_KEY: str = 'secretrefreshkey'
    ALGORITHM: str = 'HS256'
    JWT_TOKEN_EXPIRE_MINUTES: int = 10
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    SMTP_HOST: str = 'host'
    SMTP_PORT: int = 123
    SMTP_USER: str = 'user'
    SMTP_PASSWORD: str = 'pass'
    VERIFICATION_LINK: str = 'http://127.0.0.1:8000/v1/verify'


    GITHUB_CLIENT_ID: str = 'clientid'
    GITHUB_CLIENT_SECRET: str = 'clientsecret'
    GITHUB_REDIRECT_URI: str = 'http://localhost:8001/v1/github/callback'

    model_config = ConfigDict(env_file = '.env', case_sensitive = True, extra = 'ignore')

settings = Settings()
