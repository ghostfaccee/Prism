import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core import Base, get_db, settings
from app.repositories import UserRepository
from app.services import UserService, AuthService, VerificationService
from app.services.tests import UserTestsService
from app.models import User
from app.utils import hash_password

# ...

from app.main import app

TEST_DATABASE_URL = settings.TEST_POSTGRES_URL
engine = create_async_engine(TEST_DATABASE_URL, echo = False)
TestingSessionLocal = async_sessionmaker(engine, class_ = AsyncSession, expire_on_commit = True)

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

from sqlalchemy.pool import NullPool

@pytest.fixture(scope="session")
async def pg_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool
    )
    yield engine
    await engine.dispose()

@pytest.fixture(autouse = True)
async def setup_db() -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session(pg_engine):
    async with pg_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSession(pg_engine, expire_on_commit=False) as session:
        yield session
    
    async with pg_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app = app)
    async with AsyncClient(transport = transport, base_url = 'http://test') as client:
        yield client


@pytest.fixture
async def full_auth(client: AsyncClient) -> str:
    username = f'testuser'
    password = 'testpass123'
    email = f'{username}@mail.com'

    with patch('app.services.auth.send_verification_email.delay'):
        register_response = await client.post('/v1/auth/register', json = {'username' : username, 'password' : password, 'email' : email})
    assert register_response.status_code == 201, 'Failed to register testuser'

    login_response = await client.post('/v1/auth/login', json = {'username' : username, 'password' : password})
    assert login_response.status_code == 200, 'Failed to login testuser'

    login_data = login_response.json()
    assert 'access_token' in login_data, 'No access_token in login_data'
    assert 'token_type' in login_data, 'No token_type in login_data'

    return login_data['access_token']

@pytest.fixture
async def auth_without_email(client: AsyncClient) -> str:
    username = f'testuser'
    password = 'testpass123'
    
    register_response = await client.post('/v1/auth/register', json = {'username' : username, 'password' : password})
    assert register_response.status_code == 201, 'Failed to register testuser'
    
    login_response = await client.post('/v1/auth/login', json = {'username' : username, 'password' : password})
    assert login_response.status_code == 200, 'Failed to login testuser'
    
    login_data = login_response.json()
    assert 'access_token' in login_data, 'No access_token in login_data'
    assert 'token_type' in login_data, 'No token_type in login_data'
    
    return login_data['access_token']

@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    repo = UserRepository(db_session)
    user = User(
        username = 'testuser',
        email = 'testuser@mail.com',
        hashed_password = hash_password('testpass123')
    )
    return await repo.create(user)

@pytest.fixture
async def test_user2_for_test_user(db_session: AsyncSession) -> User:
    repo = UserRepository(db_session)
    user = User(
        username = 'testuser2',
        email = 'testuser2@mail.com',
        hashed_password = hash_password('testpass123')
    )
    return await repo.create(user)

@pytest.fixture
async def user_service(db_session: AsyncSession) -> UserService:
    return UserService(db_session)

@pytest.fixture
async def auth_service(db_session: AsyncSession) -> AuthService:
    return AuthService(db_session)

@pytest.fixture
async def verification_service(db_session: AsyncSession) -> VerificationService:
    return VerificationService(db_session)

@pytest.fixture
async def user_tests_service(db_session: AsyncSession) -> UserTestsService:
    return UserTestsService(db_session)
