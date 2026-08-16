from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.core import settings

engine = create_async_engine(url = settings.POSTGRES_URL, echo = settings.DEBUG)

AsyncSessionLocal = async_sessionmaker(engine, class_ = AsyncSession, expire_on_commit = True)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
