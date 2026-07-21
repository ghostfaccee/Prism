from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import UserRepository
from app.utils import hash_password, verify_password, create_jwt_token, generate_verification_token
from app.tasks.email import send_verification_email
from app.exceptions import user as user_exc
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

    async def login(self, data: UserLogin) -> TokenResponse: # TODO: Add email verification if the email is confirmed.
        exists = await self.repo.get_by_username(data.username)
        if not exists:
            raise user_exc.UsernameDoesNotExistsError(data.username)
        if not verify_password(data.password, exists.hashed_password):
            raise user_exc.InvalidPassword()
        token = create_jwt_token({'sub': str(exists.user_id)})
        return TokenResponse(access_token = token)

    async def update_user(self, user_id: UUID, data: UserUpdate) -> User:
        updated = await self.repo.update(user_id, data)
        return updated
    
    async def delete(self, user_id: UUID) -> None:
        if not await self.repo.delete(user_id):
            raise user_exc.UserDoesNotExists()
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

