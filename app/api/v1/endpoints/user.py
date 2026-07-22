from uuid import UUID
from fastapi import APIRouter, Request, status, Depends
from app import get_user_service, get_current_user
from app.schemas import UserUpdate, UpdatePassword, UserResponse
from app.services import UserService
from app.models import User

router = APIRouter()

@router.patch('/me', response_model = UserResponse, status_code = status.HTTP_200_OK, summary = 'Updates the user\'s data', description = 'Updates the username and email, the password is changed at the endpoint /v1/me/change_password. Requires a jwt token.')
async def update_user(request: Request, data: UserUpdate, current_user: User = Depends(get_current_user), service: UserService = Depends(get_user_service)):
    return await service.update_user(current_user.user_id, data)

@router.patch('/me/password', response_model = UserResponse, status_code = status.HTTP_200_OK, summary = 'Updates the user\'s password', description = 'Updates the password. Requires a jwt token.')
async def update_user_password(request: Request, data: UpdatePassword, current_user: User = Depends(get_current_user), service: UserService = Depends(get_user_service)):
    return await service.update_password(current_user.user_id, data)

@router.get('/me', response_model = UserResponse, status_code = status.HTTP_200_OK, summary = 'Get the current user', description = 'Returns a user who owns the provided jwt token. Requires a jwt token.')
async def get_current_user(request: Request, current_user: User = Depends(get_current_user), service: UserService = Depends(get_user_service)):
    return await service.get_by_id(current_user.user_id)


@router.get('/user/uuid/{user_uuid}', response_model = UserResponse, status_code = status.HTTP_200_OK, summary = 'Get user', description = 'Return a user information by user_id. Requires a jwt token')
async def get_user_by_uuid(request: Request, user_uuid: UUID, current_user: User = Depends(get_current_user), service: UserService = Depends(get_user_service)):
    return await service.get_by_id(user_uuid)

@router.get('/user/username/{username}', response_model = UserResponse, status_code = status.HTTP_200_OK, summary = 'Get user', description = 'Return a user information by username. Requires a jwt token.')
async def get_user_by_username(request: Request, username: str, current_user: User = Depends(get_current_user), service: UserService = Depends(get_user_service)):
    return await service.get_by_username(username)
