import traceback
from slowapi.errors import RateLimitExceeded
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.api import router
from app.middlewares import LoggingMiddleware
from app.middlewares import RateLimit
from app.core import engine, Base, logger, RedisClient

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await (await RedisClient.get_client()).ping()
    logger.info('Prism started')
    yield
    await (await RedisClient.get_client()).close()

app = FastAPI(lifespan = lifespan)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        f'Unhandled error on {request.method} {request.url.path}\n'
        f'{traceback.format_exc()}'
    )
    return JSONResponse(
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
        content = {'detail' : 'Internal server error'}
    )

app.state.limiter = RateLimit.get_limiter()
app.add_exception_handler(RateLimitExceeded, RateLimit.rate_limit_exceed_handler)

app.add_middleware(LoggingMiddleware)
app.include_router(router)