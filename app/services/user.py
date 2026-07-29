from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import UserRepository
from app.models import User
from app.schemas import UserUpdate, UpdatePassword
from app.tasks.email import send_verification_email
from app.utils import generate_verification_token, verify_password, hash_password
from app.exceptions import user as user_exc
from app.exceptions import state as state_exc
from datetime import datetime, timezone

class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = UserRepository(db)
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise user_exc.UserDoesNotExists()
        return user
    
    async def get_by_username(self, username: str) -> Optional[User]:
        user = await self.repo.get_by_username(username)
        if not user:
            raise user_exc.UsernameDoesNotExistsError(username)
        return user
    
    async def update_user(self, user_id: UUID, data: UserUpdate) -> User:
        user = await self.repo.get_by_id(user_id)
        updated_data = {}
        if not user:
            raise user_exc.UserDoesNotExists()
        if data.username is not None and data.username.strip() != "" and data.username != user.username:
            existing = await self.repo.get_by_username(data.username)
            if existing:
                raise user_exc.UsernameExistsError(data.username)
            updated_data['username'] = data.username
        if data.email is not None and data.email != user.email:
            existing = await self.repo.get_by_email(data.email)
            if existing:
                raise user_exc.EmailExistsError(data.email)
            token = generate_verification_token()
            updated_data["email"] = data.email
            updated_data["verification_token"] = token
            updated_data["is_active"] = False
            send_verification_email.delay(data.email, token)
        if updated_data:
            return await self.repo.update(user_id, updated_data)
        return user
    
    async def update_password(self, user_id: UUID, data: UpdatePassword) -> User:
        user = await self.repo.get_by_id(user_id)
        updated_data = {}
        if not user:
            raise user_exc.UserDoesNotExists()
        if not verify_password(data.old_pass, user.hashed_password):
            raise user_exc.InvalidPassword()
        updated_data['hashed_password'] = hash_password(data.new_pass)
        return await self.repo.update(user_id, updated_data)

    async def delete(self, user_id: UUID) -> None:
        if not await self.repo.delete(user_id):
            raise user_exc.UserDoesNotExists()
        return None

    async def setup_new_state(self, user_id: UUID, state: str, expire: datetime) -> Optional[bool]: # TODO: write tests
        success = await self.repo.setup_new_state(user_id, state, expire)
        if not success:
            raise user_exc.UserDoesNotExists()
        return success

    async def check_state(self, current_user: User, state: str) -> Optional[bool]:
        if not current_user.github_oauth_state or current_user.github_oauth_state != state:
            raise state_exc.InvalidStateError()
        if current_user.github_oauth_state_expires < datetime.now(timezone.utc).replace(tzinfo=None):
            raise state_exc.StateExpiredError()
        return await self.repo.reset_state(current_user.user_id)