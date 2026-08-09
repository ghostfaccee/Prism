from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_URL: str

    TEST_POSTGRES_URL: str

    REDIS_URL: str
    DEFAULT_TTL: int

    DEBUG: bool

    SLOW_REQUEST_THRESHOLD: float

    SECRET_JWT_KEY: str
    ALGORITHM: str
    JWT_TOKEN_EXPIRE_MINUTES: int

    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    VERIFICATION_LINK: str


    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str
    GITHUB_REDIRECT_URI: str

    model_config = ConfigDict(env_file = '.env', case_sensitive = True, extra = 'ignore')

settings = Settings()
