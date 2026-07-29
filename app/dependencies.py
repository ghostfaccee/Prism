from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core import get_db
from app.exceptions import user as user_exc
from app.services import AuthService, UserService, VerificationService, GitHubService
from app.utils import decode_jwt_token

async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)

async def get_verification_service(db: AsyncSession = Depends(get_db)) -> VerificationService:
    return VerificationService(db)

async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)

async def get_github_service(db: AsyncSession = Depends(get_db)) -> GitHubService:
    return GitHubService(db)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = '/v1/login')
async def get_current_user(token: str = Depends(oauth2_scheme), service: UserService = Depends(get_user_service)):
    payload = decode_jwt_token(token)
    if not payload:
        raise user_exc.CouldNotValidateCredentialsError()
    user_id = payload.get('sub')
    if not user_id:
        raise user_exc.CouldNotValidateCredentialsError()
    return await service.get_by_id(user_id)

