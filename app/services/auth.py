from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.repositories import UserRepository
from app.utils import hash_password, verify_password, create_access_token, create_refresh_token, generate_verification_token, decode_refresh_token
from app.infrastructure import TokenService, TokenServiceReturnValues
from app.core import settings
from app.tasks.email import send_verification_email
from app.exceptions import user as user_exc
from app.exceptions import internal as internal_exc
from app.exceptions import token as token_exc
from app.schemas import *
from app.models import User

class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = UserRepository(db)
    
    async def register(self, data: UserRegister) -> User:
        existing = await self.repo.get_by_username(data.username)
        if existing:
            raise user_exc.UsernameExistsError(data.username)
        token = None
        if data.email:
            existing = await self.repo.get_by_email(data.email)
            if existing:
                raise user_exc.EmailExistsError(data.email)
            else:
                token = generate_verification_token()
                send_verification_email.delay(data.email, token)
        
        hashed_pwd = hash_password(data.password)
        user = User(
            username = data.username,
            email = data.email,
            hashed_password = hashed_pwd,
            is_active = False,
            verification_token = token
        )
        return await self.repo.create(user)

    async def login(self, data: UserLogin) -> TokenResponse:
        exists = await self.repo.get_by_username(data.username)
        if not exists:
            raise user_exc.UsernameDoesNotExistsError(data.username)
        if not verify_password(data.password, exists.hashed_password):
            raise user_exc.InvalidPassword()
        access_token = create_access_token({'sub': str(exists.user_id)})
        refresh_token = create_refresh_token({'sub': str(exists.user_id)})
        ttl = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
        if not await TokenService.store_refresh_token(exists.user_id, refresh_token, ttl):
            raise internal_exc.InternalRedisError()
        return TokenResponse(access_token = access_token, refresh_token = refresh_token)

    async def refresh(self, refresh_token: str) -> TokenResponse:
        payload = decode_refresh_token(refresh_token)
        if not payload:
            raise user_exc.InvalidOrExpiredTokenError()
        user_id = payload.get('sub')
        if not user_id:
            raise user_exc.InvalidOrExpiredTokenError()
        if await TokenService.in_blacklist(refresh_token) == TokenServiceReturnValues.SUCCESS:
            # If the token is already blacklisted - attack.
            await TokenService.delete_refresh_token(user_id)
            raise user_exc.BlacklistTokenError()
        stored = await TokenService.get_refresh_token(UUID(user_id))
        if stored is None:
            raise internal_exc.InternalRedisError()
        if stored == '0':
            raise token_exc.TokenNotFoundError()
        if stored != refresh_token:
            # If the tokens are different, that’s also an attack.
            await TokenService.delete_refresh_token(user_id)
            raise user_exc.InvalidOrExpiredTokenError()
        new_access_token = create_access_token({'sub': str(user_id)})
        new_refresh_token = create_refresh_token({'sub': str(user_id)})
        ttl_for_blacklist = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
        if not await TokenService.add_to_blacklist(refresh_token, ttl_for_blacklist):
            raise internal_exc.InternalRedisError()
        ttl_for_refresh_token = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
        if not await TokenService.store_refresh_token(user_id, new_refresh_token, ttl_for_refresh_token):
            raise internal_exc.InternalRedisError()
        return TokenResponse(
            access_token = new_access_token,
            refresh_token = new_refresh_token
        )

    async def logout(self, user_id: UUID) -> None:
        res = await TokenService.delete_refresh_token(user_id)
        if res == TokenServiceReturnValues.ERROR:
            raise internal_exc.InternalRedisError()
        if res == TokenServiceReturnValues.NOT_FOUND:
            raise token_exc.TokenNotFoundError()
        return None

class VerificationService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = UserRepository(db)
    
    async def verify_email(self, token: str) -> VerificationResponse:
        user = await self.repo.get_by_verification_token(token)

        if not user:
            raise user_exc.InvalidOrExpiredTokenError()
        
        if user.is_active:
            raise user_exc.EmailAlreadyVerifiedError()

        return await self.repo.activate_user(user.user_id)

